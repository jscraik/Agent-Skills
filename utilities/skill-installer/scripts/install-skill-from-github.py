#!/usr/bin/env python3
"""Install a skill from a GitHub repo path into a category folder under ~/dev/agent-skills by default."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import fnmatch
import json
import os
import re
import shutil
import subprocess as sp
import sys
import tempfile
import urllib.error
import urllib.parse
import zipfile
from pathlib import Path

from github_utils import github_request
DEFAULT_REF = "main"
CATEGORY_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
TEXT_EXTENSIONS = {
    ".md",
    ".txt",
    ".yaml",
    ".yml",
    ".json",
    ".rules",
    ".toml",
    ".ini",
    ".cfg",
    ".py",
    ".sh",
    ".bash",
    ".zsh",
    ".js",
    ".ts",
}
DEFAULT_RISK_PATTERNS = [
    {
        "label": "Prompt override language",
        "regex": r"\b(ignore|disregard|forget)\b.*\b(previous|prior|system|developer)\b",
        "severity": "high",
    },
    {
        "label": "Role-shifting language",
        "regex": r"\byou are now\b|\bpretend to be\b|\bact as\b",
        "severity": "medium",
    },
    {
        "label": "High-risk control language",
        "regex": r"\b(bypass|jailbreak|override|exfiltrate)\b",
        "severity": "high",
    },
    {
        "label": "Command-like instructions",
        "regex": r"\b(curl|wget|powershell|invoke-webrequest|nc|netcat|rm\s+-rf|chmod\s+777)\b",
        "severity": "medium",
    },
]


def _local_security_config_path() -> Path:
    override = os.environ.get("CODEX_SKILL_SECURITY_CONFIG")
    if override:
        return Path(override).expanduser()
    return Path("~/.codex/skill-security/allow-block.json").expanduser()


@dataclass
class Args:
    url: str | None = None
    repo: str | None = None
    path: list[str] | None = None
    ref: str = DEFAULT_REF
    dest: str | None = None
    name: str | None = None
    method: str = "auto"
    on_warning: str = "prompt"
    force_unsafe: bool = False


@dataclass
class Source:
    owner: str
    repo: str
    ref: str
    paths: list[str]
    repo_url: str | None = None


@dataclass(frozen=True)
class RiskFinding:
    source: str
    message: str
    severity: str


class InstallError(Exception):
    pass


def _skills_root() -> str:
    env_home = os.environ.get("AGENT_SKILLS_HOME")
    if env_home:
        return os.path.expanduser(env_home)
    codex_home = os.environ.get("CODEX_HOME")
    if codex_home:
        return os.path.join(os.path.expanduser(codex_home), "skills")
    return os.path.expanduser("~/dev/agent-skills")


def _tmp_root() -> str:
    base = os.path.join(tempfile.gettempdir(), "codex")
    os.makedirs(base, exist_ok=True)
    return base


def _request(url: str) -> bytes:
    return github_request(url, "codex-skill-install")


def _parse_github_url(url: str, default_ref: str) -> tuple[str, str, str, str | None]:
    parsed = urllib.parse.urlparse(url)
    if parsed.netloc != "github.com":
        raise InstallError("Only GitHub URLs are supported for download mode.")
    parts = [p for p in parsed.path.split("/") if p]
    if len(parts) < 2:
        raise InstallError("Invalid GitHub URL.")
    owner, repo = parts[0], parts[1]
    ref = default_ref
    subpath = ""
    if len(parts) > 2:
        if parts[2] in ("tree", "blob"):
            if len(parts) < 4:
                raise InstallError("GitHub URL missing ref or path.")
            ref = parts[3]
            subpath = "/".join(parts[4:])
        else:
            subpath = "/".join(parts[2:])
    return owner, repo, ref, subpath or None


def _download_repo_zip(owner: str, repo: str, ref: str, dest_dir: str) -> str:
    zip_url = f"https://codeload.github.com/{owner}/{repo}/zip/{ref}"
    zip_path = os.path.join(dest_dir, "repo.zip")
    try:
        payload = _request(zip_url)
    except urllib.error.HTTPError as exc:
        raise InstallError(f"Download failed: HTTP {exc.code}") from exc
    with open(zip_path, "wb") as file_handle:
        file_handle.write(payload)
    with zipfile.ZipFile(zip_path, "r") as zip_file:
        _safe_extract_zip(zip_file, dest_dir)
        top_levels = {name.split("/")[0] for name in zip_file.namelist() if name}
    if not top_levels:
        raise InstallError("Downloaded archive was empty.")
    if len(top_levels) != 1:
        raise InstallError("Unexpected archive layout.")
    return os.path.join(dest_dir, next(iter(top_levels)))


def _run_git(args: list[str]) -> None:
    result = sp.run(args, stdout=sp.PIPE, stderr=sp.PIPE, text=True)
    if result.returncode != 0:
        raise InstallError(result.stderr.strip() or "Git command failed.")


def _safe_extract_zip(zip_file: zipfile.ZipFile, dest_dir: str) -> None:
    dest_root = os.path.realpath(dest_dir)
    for info in zip_file.infolist():
        extracted_path = os.path.realpath(os.path.join(dest_dir, info.filename))
        if extracted_path == dest_root or extracted_path.startswith(dest_root + os.sep):
            continue
        raise InstallError("Archive contains files outside the destination.")
    zip_file.extractall(dest_dir)


def _validate_relative_path(path: str) -> None:
    if os.path.isabs(path) or os.path.normpath(path).startswith(".."):
        raise InstallError("Skill path must be a relative path inside the repo.")


def _validate_skill_name(name: str) -> None:
    altsep = os.path.altsep
    if not name or os.path.sep in name or (altsep and altsep in name):
        raise InstallError("Skill name must be a single path segment.")
    if name in (".", ".."):
        raise InstallError("Invalid skill name.")


def _validate_category_name(category: str) -> None:
    if not CATEGORY_RE.fullmatch(category):
        raise InstallError("Category must be lowercase kebab-case (letters, numbers, hyphens).")


def _normalize_severity(severity: str) -> str:
    text = str(severity).strip().lower()
    if text not in {"low", "medium", "high"}:
        return "medium"
    return text


def _git_sparse_checkout(repo_url: str, ref: str, paths: list[str], dest_dir: str) -> str:
    repo_dir = os.path.join(dest_dir, "repo")
    clone_cmd = [
        "git",
        "clone",
        "--filter=blob:none",
        "--depth",
        "1",
        "--sparse",
        "--single-branch",
        "--branch",
        ref,
        repo_url,
        repo_dir,
    ]
    try:
        _run_git(clone_cmd)
    except InstallError:
        _run_git(
            [
                "git",
                "clone",
                "--filter=blob:none",
                "--depth",
                "1",
                "--sparse",
                "--single-branch",
                repo_url,
                repo_dir,
            ]
        )
    _run_git(["git", "-C", repo_dir, "sparse-checkout", "set", *paths])
    _run_git(["git", "-C", repo_dir, "checkout", ref])
    return repo_dir


def _validate_skill(path: str) -> None:
    if not os.path.isdir(path):
        raise InstallError(f"Skill path not found: {path}")
    skill_md = os.path.join(path, "SKILL.md")
    if not os.path.isfile(skill_md):
        raise InstallError("SKILL.md not found in selected skill directory.")


def _read_text(path: str) -> str:
    try:
        return Path(path).read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return Path(path).read_text(encoding="utf-8", errors="replace")


def _is_text_file(path: str) -> bool:
    ext = os.path.splitext(path)[1].lower()
    if os.path.basename(path) == "SKILL.md" or ext in TEXT_EXTENSIONS:
        return True
    try:
        chunk = Path(path).read_bytes()[:4096]
    except OSError:
        return False
    if b"\x00" in chunk:
        return False
    try:
        chunk.decode("utf-8")
        return True
    except UnicodeDecodeError:
        return False


def _load_skillignore(root: str) -> list[str]:
    ignore_path = os.path.join(root, ".skillignore")
    if not os.path.isfile(ignore_path):
        return []
    patterns: list[str] = []
    for raw in Path(ignore_path).read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        patterns.append(line)
    return patterns


def _load_risk_patterns() -> tuple[list[tuple[str, re.Pattern[str], str]], list[str]]:
    config_path = Path(__file__).resolve().parents[1] / "references" / "prompt-injection-patterns.json"
    warnings: list[str] = []
    patterns: list[tuple[str, re.Pattern[str], str]] = []
    allowed_severity = {"low", "medium", "high"}

    if config_path.exists():
        try:
            raw = json.loads(config_path.read_text(encoding="utf-8"))
            if not isinstance(raw, list):
                raise ValueError("pattern config must be a list")
            for entry in raw:
                if not isinstance(entry, dict):
                    raise ValueError("pattern entries must be objects")
                label = str(
                    entry.get("label")
                    or entry.get("code")
                    or entry.get("message")
                    or ""
                ).strip()
                regex = str(entry.get("regex", "")).strip()
                severity = str(entry.get("severity", "medium")).strip().lower()
                if not label or not regex:
                    raise ValueError("pattern entries must include label/code/message and regex")
                if severity not in allowed_severity:
                    warnings.append(f"config: invalid severity '{severity}' for {label}; defaulting to medium")
                    severity = "medium"
                patterns.append((label, re.compile(regex, re.IGNORECASE | re.DOTALL), severity))
        except Exception as exc:
            warnings.append(f"config: failed to load prompt patterns; using defaults ({exc})")
            patterns = []

    if not patterns:
        for entry in DEFAULT_RISK_PATTERNS:
            patterns.append((
                entry["label"],
                re.compile(entry["regex"], re.IGNORECASE | re.DOTALL),
                entry["severity"],
            ))

    return patterns, warnings


def _load_allow_block_patterns() -> tuple[list[re.Pattern[str]], list[tuple[re.Pattern[str], str, str]], list[str]]:
    warnings: list[str] = []
    allowlist: list[re.Pattern[str]] = []
    blocklist: list[tuple[re.Pattern[str], str, str]] = []
    config_path = _local_security_config_path()

    if not config_path.exists():
        return allowlist, blocklist, warnings

    try:
        raw = json.loads(config_path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ValueError("allow/block config must be an object")
        allow_raw = raw.get("allowlist", [])
        block_raw = raw.get("blocklist", [])
        if not isinstance(allow_raw, list) or not isinstance(block_raw, list):
            raise ValueError("allowlist and blocklist must be lists")

        for entry in allow_raw:
            if not isinstance(entry, dict):
                raise ValueError("allowlist entries must be objects")
            regex = str(entry.get("regex", "")).strip()
            if not regex:
                raise ValueError("allowlist entries must include regex")
            allowlist.append(re.compile(regex, re.IGNORECASE | re.DOTALL))

        for entry in block_raw:
            if not isinstance(entry, dict):
                raise ValueError("blocklist entries must be objects")
            regex = str(entry.get("regex", "")).strip()
            message = str(entry.get("message", "Blocklist match")).strip()
            severity = str(entry.get("severity", "high")).strip().lower()
            if not regex:
                raise ValueError("blocklist entries must include regex")
            if severity not in {"low", "medium", "high"}:
                warnings.append(f"config: invalid severity '{severity}' for blocklist; defaulting to medium")
                severity = "medium"
            blocklist.append((re.compile(regex, re.IGNORECASE | re.DOTALL), message, severity))
    except Exception as exc:
        warnings.append(f"config: failed to load allow/block config; ignoring ({exc})")
        allowlist = []
        blocklist = []

    return allowlist, blocklist, warnings


def _is_ignored(path: str, root: str, patterns: list[str]) -> bool:
    rel_path = os.path.relpath(path, root).replace("\\", "/")
    return any(fnmatch.fnmatch(rel_path, pattern) for pattern in patterns)


def _assert_within_root(path: str, root_real: str, *, kind: str) -> None:
    resolved = os.path.realpath(path)
    if resolved == root_real or resolved.startswith(root_real + os.sep):
        return
    raise InstallError(f"{kind} escapes skill root via symlink or traversal: {path}")


def _iter_scan_targets(root: str) -> list[tuple[str, bool]]:
    ignore_patterns = _load_skillignore(root)
    targets: list[tuple[str, bool]] = []
    root_real = os.path.realpath(root)
    if os.path.islink(root):
        raise InstallError(f"Skill root cannot be a symlink: {root}")
    _assert_within_root(root, root_real, kind="skill root")

    for dirpath, dirnames, filenames in os.walk(root):
        _assert_within_root(dirpath, root_real, kind="directory")
        if ".git" in Path(dirpath).parts:
            continue
        for dirname in list(dirnames):
            dir_full = os.path.join(dirpath, dirname)
            if os.path.islink(dir_full):
                raise InstallError(f"Symlinked directory is not allowed in skill package: {dir_full}")
            _assert_within_root(dir_full, root_real, kind="directory")
        for filename in filenames:
            path = os.path.join(dirpath, filename)
            if os.path.islink(path):
                raise InstallError(f"Symlinked file is not allowed in skill package: {path}")
            _assert_within_root(path, root_real, kind="file")
            if _is_ignored(path, root, ignore_patterns):
                continue
            targets.append((path, _is_text_file(path)))
    return targets


def _scan_skill_for_risks(skill_path: str) -> list[RiskFinding]:
    findings: list[RiskFinding] = []
    patterns, config_warnings = _load_risk_patterns()
    findings.extend(
        RiskFinding(source="config", message=warning, severity="medium")
        for warning in config_warnings
    )
    allowlist, blocklist, allow_block_warnings = _load_allow_block_patterns()
    findings.extend(
        RiskFinding(source="config", message=warning, severity="medium")
        for warning in allow_block_warnings
    )
    for file_path, is_text in _iter_scan_targets(skill_path):
        rel_path = os.path.relpath(file_path, skill_path)
        try:
            if os.path.getsize(file_path) > 1_000_000:
                findings.append(
                    RiskFinding(
                        source=rel_path,
                        message="skipped large file (>1MB) from risk scan",
                        severity="low",
                    )
                )
                continue
        except OSError:
            findings.append(
                RiskFinding(
                    source=rel_path,
                    message="unable to determine file size for risk scan",
                    severity="low",
                )
            )
            continue

        if not is_text:
            findings.append(
                RiskFinding(
                    source=rel_path,
                    message="non-text attachment (manual review required)",
                    severity="low",
                )
            )
            continue

        text = _read_text(file_path)
        for pattern, message, severity in blocklist:
            if pattern.search(text):
                findings.append(
                    RiskFinding(
                        source=rel_path,
                        message=f"blocklist match - {message}",
                        severity=_normalize_severity(severity),
                    )
                )
        if any(allow.search(rel_path) for allow in allowlist):
            continue
        for label, pattern, severity in patterns:
            if pattern.search(text):
                findings.append(
                    RiskFinding(
                        source=rel_path,
                        message=label,
                        severity=_normalize_severity(severity),
                    )
                )
    return findings


def _format_warnings(warnings: list[RiskFinding]) -> str:
    lines = ["Warning: Potential prompt-injection or risky command patterns detected:"]
    lines.extend([f"  - [{warning.severity.upper()}] {warning.source}: {warning.message}" for warning in warnings])
    return "\n".join(lines)


def _investigate_skill(skill_path: str, warnings: list[RiskFinding]) -> None:
    total_files = 0
    text_files = 0
    binary_files: list[tuple[str, int]] = []
    largest_files: list[tuple[str, int]] = []

    for file_path, is_text in _iter_scan_targets(skill_path):
        total_files += 1
        rel_path = os.path.relpath(file_path, skill_path)
        try:
            size = os.path.getsize(file_path)
        except OSError:
            size = -1
        if is_text:
            text_files += 1
        else:
            binary_files.append((rel_path, size))
        if size >= 0:
            largest_files.append((rel_path, size))

    largest_files.sort(key=lambda item: item[1], reverse=True)
    binary_files.sort(key=lambda item: item[1], reverse=True)

    print("\nInvestigation summary (read-only):", file=sys.stderr)
    print(f"- Skill path: {skill_path}", file=sys.stderr)
    print(f"- Total files: {total_files}", file=sys.stderr)
    print(f"- Text files: {text_files}", file=sys.stderr)
    print(f"- Binary attachments: {len(binary_files)}", file=sys.stderr)
    if warnings:
        print("- Warning matches:", file=sys.stderr)
        for warning in warnings:
            triage = _triage_warning(warning)
            print(
                f"  - [{warning.severity.upper()}] {warning.source}: {warning.message} [triage: {triage}]",
                file=sys.stderr,
            )
    if largest_files:
        print("- Largest files:", file=sys.stderr)
        for rel_path, size in largest_files[:10]:
            size_kb = "unknown" if size < 0 else f"{size / 1024:.1f} KB"
            print(f"  - {rel_path} ({size_kb})", file=sys.stderr)
    if binary_files:
        print("- Binary attachments (top 10):", file=sys.stderr)
        for rel_path, size in binary_files[:10]:
            size_kb = "unknown" if size < 0 else f"{size / 1024:.1f} KB"
            print(f"  - {rel_path} ({size_kb})", file=sys.stderr)
    print("\nSuggested next actions:", file=sys.stderr)
    print(f"- Open folder: {skill_path}", file=sys.stderr)
    print(f"- Open in Finder (macOS): open \"{skill_path}\"", file=sys.stderr)
    print("- Search for commands: rg -n \"curl|wget|rm -rf|powershell\" <skill_path>", file=sys.stderr)


def _triage_warning(warning: RiskFinding) -> str:
    if warning.source == "config":
        return "config"

    rel_path = warning.source
    path = Path(rel_path)
    ext = path.suffix.lower()
    parts = [part.lower() for part in path.parts]

    if "scripts" in parts or ext in {".py", ".sh", ".bash", ".zsh", ".js", ".ts"}:
        return "code-context"
    if "rules" in parts or "references" in parts or ext == ".md":
        return "docs-context"
    if ext:
        return "unknown"
    return "unknown"


def _should_continue_after_warning(
    warnings: list[RiskFinding],
    *,
    mode: str,
    skill_name: str,
    skill_path: str,
    force_unsafe: bool,
) -> bool:
    has_high = any(warning.severity == "high" for warning in warnings)
    if has_high and not force_unsafe:
        print(_format_warnings(warnings), file=sys.stderr)
        print(
            "Install blocked: high-severity findings detected. Re-run with --force-unsafe to override.",
            file=sys.stderr,
        )
        return False

    if mode == "continue":
        print(_format_warnings(warnings), file=sys.stderr)
        print("Warning: Review the skill files before installing. Continuing install.", file=sys.stderr)
        return True
    if mode == "stop":
        print(_format_warnings(warnings), file=sys.stderr)
        print("Install stopped due to warnings. Re-run with --on-warning continue to proceed.", file=sys.stderr)
        return False

    print(_format_warnings(warnings), file=sys.stderr)
    print("Choose an action:", file=sys.stderr)
    print("  [A] Investigate (read-only summary and stop)", file=sys.stderr)
    print("  [B] Continue install", file=sys.stderr)
    print("  [C] Stop install", file=sys.stderr)
    choice = input(f"Action for {skill_name} (A/B/C): ").strip().lower()
    if choice in {"a", "investigate"}:
        print("Investigate: review the skill files before installing.", file=sys.stderr)
        _investigate_skill(skill_path, warnings)
        return False
    if choice in {"b", "continue"}:
        print("Continuing install by user choice.", file=sys.stderr)
        return True
    print("Install stopped by user choice.", file=sys.stderr)
    return False


def _copy_skill(src: str, dest_dir: str) -> None:
    os.makedirs(os.path.dirname(dest_dir), exist_ok=True)
    if os.path.exists(dest_dir):
        raise InstallError(f"Destination already exists: {dest_dir}")
    _iter_scan_targets(src)
    shutil.copytree(src, dest_dir)


def _choose_python() -> str:
    preferred = Path.home() / ".venvs" / "pyyaml" / "bin" / "python"
    if preferred.exists():
        return str(preferred)
    return sys.executable


def _validator_scripts_root() -> Path:
    # .../utilities/skill-installer/scripts/install-skill-from-github.py
    # -> .../utilities/skill-creator/scripts
    scripts_root = Path(__file__).resolve().parents[2] / "skill-creator" / "scripts"
    if not scripts_root.exists():
        raise InstallError(f"Missing validator scripts directory: {scripts_root}")
    return scripts_root


def _run_required_validations(installed_skill_dir: str) -> None:
    py = _choose_python()
    scripts_root = _validator_scripts_root()
    skill_path = str(Path(installed_skill_dir).resolve())

    runner = "claude" if shutil.which("claude") else "codex" if shutil.which("codex") else None
    if runner is None:
        raise InstallError(
            "run_skill_evals.py is required for new skills, but no `claude` or `codex` CLI was found on PATH."
        )

    commands: list[list[str]] = [
        [py, str(scripts_root / "quick_validate.py"), skill_path],
        [py, str(scripts_root / "skill_gate.py"), skill_path],
        [py, str(scripts_root / "analyze_skill.py"), skill_path],
        [py, str(scripts_root / "openclaw_skill_guard.py"), skill_path, "--mode", "both"],
        [py, str(scripts_root / "run_skill_evals.py"), skill_path, "--runner", runner],
    ]

    if runner == "codex":
        # Trust checks can block evals in some local contexts; this flag is supported by the repo runner.
        commands[-1].extend(["--codex-arg=--skip-git-repo-check"])

    for cmd in commands:
        proc = sp.run(cmd, text=True, capture_output=True)
        if proc.returncode != 0:
            stdout = (proc.stdout or "").strip()
            stderr = (proc.stderr or "").strip()
            details = []
            if stdout:
                details.append(f"STDOUT:\n{stdout}")
            if stderr:
                details.append(f"STDERR:\n{stderr}")
            detail_block = ("\n\n" + "\n\n".join(details)) if details else ""
            raise InstallError(
                f"Validation failed: {' '.join(cmd)}{detail_block}"
            )


def _build_repo_url(owner: str, repo: str) -> str:
    return f"https://github.com/{owner}/{repo}.git"


def _build_repo_ssh(owner: str, repo: str) -> str:
    return f"git@github.com:{owner}/{repo}.git"


def _prepare_repo(source: Source, method: str, tmp_dir: str) -> str:
    if method in ("download", "auto"):
        try:
            return _download_repo_zip(source.owner, source.repo, source.ref, tmp_dir)
        except InstallError as exc:
            if method == "download":
                raise
            err_msg = str(exc)
            if "HTTP 401" in err_msg or "HTTP 403" in err_msg or "HTTP 404" in err_msg:
                pass
            else:
                raise
    if method in ("git", "auto"):
        repo_url = source.repo_url or _build_repo_url(source.owner, source.repo)
        try:
            return _git_sparse_checkout(repo_url, source.ref, source.paths, tmp_dir)
        except InstallError:
            repo_url = _build_repo_ssh(source.owner, source.repo)
            return _git_sparse_checkout(repo_url, source.ref, source.paths, tmp_dir)
    raise InstallError("Unsupported method.")


def _resolve_source(args: Args) -> Source:
    if args.url:
        owner, repo, ref, url_path = _parse_github_url(args.url, args.ref)
        if args.path is not None:
            paths = list(args.path)
        elif url_path:
            paths = [url_path]
        else:
            paths = []
        if not paths:
            raise InstallError("Missing --path for GitHub URL.")
        return Source(owner=owner, repo=repo, ref=ref, paths=paths)

    if not args.repo:
        raise InstallError("Provide --repo or --url.")
    if "://" in args.repo:
        return _resolve_source(
            Args(url=args.repo, repo=None, path=args.path, ref=args.ref)
        )

    repo_parts = [p for p in args.repo.split("/") if p]
    if len(repo_parts) != 2:
        raise InstallError("--repo must be in owner/repo format.")
    if not args.path:
        raise InstallError("Missing --path for --repo.")
    paths = list(args.path)
    return Source(
        owner=repo_parts[0],
        repo=repo_parts[1],
        ref=args.ref,
        paths=paths,
    )


def _parse_args(argv: list[str]) -> Args:
    parser = argparse.ArgumentParser(description="Install a skill from GitHub.")
    parser.add_argument("--repo", help="owner/repo")
    parser.add_argument("--url", help="https://github.com/owner/repo[/tree/ref/path]")
    parser.add_argument(
        "--path",
        nargs="+",
        help="Path(s) to skill(s) inside repo",
    )
    parser.add_argument("--ref", default=DEFAULT_REF)
    parser.add_argument("--dest", help="Destination skills directory")
    parser.add_argument(
        "--category",
        help="Category folder under the skills root (for example: utilities, product, frontend, interview, github).",
    )
    parser.add_argument(
        "--name", help="Destination skill name (defaults to basename of path)"
    )
    parser.add_argument(
        "--method",
        choices=["auto", "download", "git"],
        default="auto",
    )
    parser.add_argument(
        "--on-warning",
        choices=["prompt", "continue", "stop"],
        default="prompt",
        help="Behavior when warnings are detected (prompt, continue, stop).",
    )
    parser.add_argument(
        "--force-unsafe",
        action="store_true",
        help="Allow install to continue when high-severity risk findings are detected.",
    )
    return parser.parse_args(argv, namespace=Args())


def main(argv: list[str]) -> int:
    args = _parse_args(argv)
    try:
        source = _resolve_source(args)
        source.ref = source.ref or args.ref
        if not source.paths:
            raise InstallError("No skill paths provided.")
        for path in source.paths:
            _validate_relative_path(path)
        if args.dest:
            dest_root = args.dest
        else:
            if not args.category:
                raise InstallError("Missing --category (required when --dest is not set).")
            _validate_category_name(args.category)
            dest_root = os.path.join(_skills_root(), args.category)
        tmp_dir = tempfile.mkdtemp(prefix="skill-install-", dir=_tmp_root())
        try:
            repo_root = _prepare_repo(source, args.method, tmp_dir)
            installed = []
            for path in source.paths:
                skill_name = args.name if len(source.paths) == 1 else None
                skill_name = skill_name or os.path.basename(path.rstrip("/"))
                _validate_skill_name(skill_name)
                if not skill_name:
                    raise InstallError("Unable to derive skill name.")
                dest_dir = os.path.join(dest_root, skill_name)
                if os.path.exists(dest_dir):
                    raise InstallError(f"Destination already exists: {dest_dir}")
                skill_src = os.path.join(repo_root, path)
                _validate_skill(skill_src)
                warnings = _scan_skill_for_risks(skill_src)
                if warnings:
                    if not _should_continue_after_warning(
                        warnings,
                        mode=args.on_warning,
                        skill_name=skill_name,
                        skill_path=skill_src,
                        force_unsafe=args.force_unsafe,
                    ):
                        raise InstallError("Install stopped due to warnings.")
                _copy_skill(skill_src, dest_dir)
                try:
                    _run_required_validations(dest_dir)
                except InstallError:
                    shutil.rmtree(dest_dir, ignore_errors=True)
                    raise
                installed.append((skill_name, dest_dir))
        finally:
            if os.path.isdir(tmp_dir):
                shutil.rmtree(tmp_dir, ignore_errors=True)
        for skill_name, dest_dir in installed:
            print(f"Installed {skill_name} to {dest_dir}")
        return 0
    except InstallError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
