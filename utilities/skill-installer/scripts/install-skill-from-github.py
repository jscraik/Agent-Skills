#!/usr/bin/env python3
"""Install a skill from a GitHub repo path into a category folder under ~/dev/agent-skills by default."""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
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
# Full 40-character hex SHA (git commit SHA).
SHA_RE = re.compile(r"^[0-9a-f]{40}$", re.IGNORECASE)
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
TOKEN_STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "that",
    "this",
    "from",
    "into",
    "when",
    "then",
    "than",
    "your",
    "you",
    "are",
    "use",
    "using",
    "used",
    "also",
    "must",
    "should",
    "will",
    "can",
    "not",
    "all",
    "any",
    "each",
    "after",
    "before",
    "into",
    "over",
    "under",
    "mode",
    "path",
    "paths",
    "script",
    "scripts",
    "skill",
    "skills",
}


def _local_security_config_path() -> Path:
    override = os.environ.get("CODEX_SKILL_SECURITY_CONFIG")
    if override:
        return Path(override).expanduser()
    return Path("~/.codex/skill-security/allow-block.json").expanduser()


@dataclass
class Args:
    url: str | None = None
    repo: str | None = None
    skill: str | None = None
    path: list[str] | None = None
    ref: str = DEFAULT_REF
    dest: str | None = None
    name: str | None = None
    method: str = "auto"
    on_warning: str = "prompt"
    force_unsafe: bool = False
    dry_run: bool = False
    deconflict: bool = False
    deconflict_threshold: float = 0.2
    deconflict_block_threshold: float = 0.45
    deconflict_engine: str = "auto"
    deconflict_cache_path: str | None = None
    deconflict_artifact_path: str | None = None
    merge_proposal: bool = False
    merge_proposal_dir: str | None = None
    run_deconflict_benchmark: bool = False
    benchmark_file: str | None = None


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


@dataclass
class DeconflictMatch:
    path: str
    score: float
    token_score: float
    command_score: float
    harness_score: float
    intent_score: float
    same_job: bool
    confidence: str
    block_recommended: bool
    shared_terms: tuple[str, ...]
    improvement_hints: tuple[str, ...]
    proposal_path: str | None = None


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


def _validate_ref_is_pinned(ref: str, require_pinned: bool) -> list[RiskFinding]:
    """Return a RiskFinding when ref is a mutable branch/tag rather than a full SHA.

    When *require_pinned* is True this raises InstallError immediately so CI
    pipelines can hard-fail without needing --on-warning=stop.
    """
    if SHA_RE.match(ref):
        return []
    message = (
        f"Ref '{ref}' is a mutable branch or tag, not a pinned commit SHA. "
        "A branch HEAD can change between resolution and install, meaning a "
        "different version of the skill could be fetched than the one reviewed. "
        "Use --ref <40-char-sha> to pin to an exact commit. "
        "Pass --require-pinned-ref to hard-fail on mutable refs in CI."
    )
    if require_pinned:
        raise InstallError(message)
    return [RiskFinding(source="ref", message=message, severity="medium")]


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


def _tokenize_overlap(text: str) -> set[str]:
    tokens = {
        token
        for token in re.findall(r"[a-z0-9][a-z0-9_-]{2,}", text.lower())
        if token not in TOKEN_STOPWORDS and not token.isdigit()
    }
    return tokens


def _extract_command_tokens(text: str) -> set[str]:
    commands: set[str] = set()
    for snippet in re.findall(r"`([^`]+)`", text):
        normalized = " ".join(snippet.strip().lower().split())
        if not normalized:
            continue
        if len(normalized) > 120:
            continue
        first = normalized.split()[0]
        if len(first) > 40:
            continue
        if not re.fullmatch(r"[a-z0-9._/@-]+", first):
            continue
        if any(marker in normalized for marker in ("--", "/", "python", "npm", "just ", "bash ", "zsh ")):
            commands.add(normalized)
    return commands


def _section_weight(heading: str | None) -> float:
    if not heading:
        return 1.0
    normalized = heading.lower()
    if any(key in normalized for key in ("scope", "trigger", "use when", "guiding question")):
        return 1.6
    if any(key in normalized for key in ("procedure", "workflow", "deliverable", "behavior", "option")):
        return 1.35
    if any(key in normalized for key in ("validation", "safety", "constraint")):
        return 1.2
    if any(key in normalized for key in ("anti-pattern", "non-goal")):
        return 0.8
    return 1.0


def _is_exclusion_section(heading: str | None) -> bool:
    if not heading:
        return False
    normalized = heading.lower()
    return any(key in normalized for key in ("anti-pattern", "non-goal", "not to", "out of scope"))


def _add_weighted_tokens(target: dict[str, float], text: str, weight: float) -> None:
    for token in _tokenize_overlap(text):
        target[token] = target.get(token, 0.0) + weight


def _extract_intent_profile(text: str) -> tuple[dict[str, float], set[str], set[str]]:
    weighted: dict[str, float] = {}
    focus_tokens: set[str] = set()
    exclusion_tokens: set[str] = set()

    desc_match = re.search(r"^description:\s*(.+)$", text, flags=re.MULTILINE)
    if desc_match:
        desc = desc_match.group(1)
        _add_weighted_tokens(weighted, desc, 1.7)
        focus_tokens.update(_tokenize_overlap(desc))

    heading: str | None = None
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        heading_match = re.match(r"^##+\s+(.+)$", line)
        if heading_match:
            heading = heading_match.group(1).strip().lower()
            continue

        content = line[2:].strip() if line.startswith("- ") else line
        if not content:
            continue

        weight = _section_weight(heading)
        _add_weighted_tokens(weighted, content, weight)

        content_tokens = _tokenize_overlap(content)
        if weight >= 1.3 or re.search(r"\b(use when|trigger|when the user asks|install|update|merge|validate|review)\b", content.lower()):
            focus_tokens.update(content_tokens)

        if _is_exclusion_section(heading) or re.search(r"\b(do not|don't|not for|out of scope|avoid)\b", content.lower()):
            exclusion_tokens.update(content_tokens)

    if not weighted:
        fallback = text[:1200]
        _add_weighted_tokens(weighted, fallback, 1.0)
        focus_tokens.update(_tokenize_overlap(fallback))

    return weighted, focus_tokens, exclusion_tokens


def _skill_profile_cache_key(skill_dir: str) -> str:
    return os.path.realpath(skill_dir)


def _load_deconflict_cache(path: str | None) -> dict[str, dict[str, object]]:
    if not path:
        return {}
    cache_path = Path(path).expanduser()
    if not cache_path.exists():
        return {}
    try:
        payload = json.loads(cache_path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    if not isinstance(payload, dict):
        return {}
    entries = payload.get("entries")
    if not isinstance(entries, dict):
        return {}
    valid: dict[str, dict[str, object]] = {}
    for key, value in entries.items():
        if isinstance(key, str) and isinstance(value, dict):
            valid[key] = value
    return valid


def _save_deconflict_cache(path: str | None, cache: dict[str, dict[str, object]]) -> None:
    if not path:
        return
    cache_path = Path(path).expanduser()
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "1.0",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "entries": cache,
    }
    cache_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _skill_profile(
    skill_dir: str,
    profile_cache: dict[str, dict[str, object]],
) -> tuple[set[str], set[str], dict[str, float], set[str], set[str]]:
    skill_md = os.path.join(skill_dir, "SKILL.md")
    stat = os.stat(skill_md)
    key = _skill_profile_cache_key(skill_dir)
    cached = profile_cache.get(key)
    if (
        cached
        and isinstance(cached.get("mtime"), (int, float))
        and float(cached["mtime"]) == stat.st_mtime
    ):
        tokens = set(str(item) for item in cached.get("tokens", []))
        commands = set(str(item) for item in cached.get("commands", []))
        intent_raw = cached.get("intent_weights", {})
        intent_weights = {
            str(name): float(weight)
            for name, weight in intent_raw.items()
            if isinstance(name, str) and isinstance(weight, (int, float))
        } if isinstance(intent_raw, dict) else {}
        focus_tokens = set(str(item) for item in cached.get("focus_tokens", []))
        exclusion_tokens = set(str(item) for item in cached.get("exclusion_tokens", []))
        return tokens, commands, intent_weights, focus_tokens, exclusion_tokens

    text = _read_text(skill_md)
    tokens = _tokenize_overlap(text)
    commands = _extract_command_tokens(text)
    intent_weights, focus_tokens, exclusion_tokens = _extract_intent_profile(text)
    profile_cache[key] = {
        "mtime": stat.st_mtime,
        "tokens": sorted(tokens),
        "commands": sorted(commands),
        "intent_weights": intent_weights,
        "focus_tokens": sorted(focus_tokens),
        "exclusion_tokens": sorted(exclusion_tokens),
    }
    return tokens, commands, intent_weights, focus_tokens, exclusion_tokens


def _extract_markdown_headings(text: str) -> set[str]:
    headings: set[str] = set()
    for line in text.splitlines():
        match = re.match(r"^##+\s+(.+)$", line.strip())
        if not match:
            continue
        heading = re.sub(r"\s+", " ", match.group(1).strip().lower())
        headings.add(heading)
    return headings


def _generate_improvement_hints(source_skill_dir: str, existing_skill_dir: str) -> tuple[str, ...]:
    source_text = _read_text(os.path.join(source_skill_dir, "SKILL.md"))
    existing_text = _read_text(os.path.join(existing_skill_dir, "SKILL.md"))

    hints: list[str] = []

    source_commands = _extract_command_tokens(source_text)
    existing_commands = _extract_command_tokens(existing_text)
    new_commands = sorted(source_commands - existing_commands)
    if new_commands:
        preview = ", ".join(f"`{cmd}`" for cmd in new_commands[:2])
        hints.append(f"Candidate has install/validation commands not in current skill: {preview}.")

    source_headings = _extract_markdown_headings(source_text)
    existing_headings = _extract_markdown_headings(existing_text)
    interesting = ("validation", "safety", "feedback", "procedure", "deliverables", "deconflict")
    missing_sections = sorted(
        heading
        for heading in source_headings - existing_headings
        if any(keyword in heading for keyword in interesting)
    )
    if missing_sections:
        preview = ", ".join(missing_sections[:3])
        hints.append(f"Candidate includes extra workflow sections: {preview}.")

    if "decision-feedback-protocol:v2" in source_text and "decision-feedback-protocol:v2" not in existing_text:
        hints.append("Candidate includes decision-feedback protocol markers missing in current skill.")

    source_intent, _source_focus, _source_exclusions = _extract_intent_profile(source_text)
    existing_intent, _existing_focus, _existing_exclusions = _extract_intent_profile(existing_text)
    source_intent_terms = set(source_intent)
    existing_intent_terms = set(existing_intent)
    net_new_intent = sorted(source_intent_terms - existing_intent_terms)
    if net_new_intent:
        preview = ", ".join(net_new_intent[:6])
        hints.append(f"Candidate adds intent/trigger coverage terms: {preview}.")

    return tuple(hints[:3])


def _repo_root(path: str) -> str | None:
    proc = sp.run(
        ["git", "-C", path, "rev-parse", "--show-toplevel"],
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        return None
    root = (proc.stdout or "").strip()
    return root or None


def _build_harness_queries(skill_name: str, skill_text: str) -> list[str]:
    queries: list[str] = []
    queries.append(skill_name.replace("-", " "))

    desc_match = re.search(r"^description:\s*(.+)$", skill_text, flags=re.MULTILINE)
    if desc_match:
        desc = re.sub(r"[^a-z0-9 _-]+", " ", desc_match.group(1).lower())
        queries.append(desc.strip())

    words = re.findall(r"[a-z][a-z0-9_-]{2,}", skill_text.lower())
    word_counts = Counter(word for word in words if word not in TOKEN_STOPWORDS)
    if word_counts:
        top_terms = [term for term, _count in word_counts.most_common(12)]
        queries.append(" ".join(top_terms))

    seen: set[str] = set()
    deduped: list[str] = []
    for query in queries:
        normalized = " ".join(query.split())
        if not normalized:
            continue
        if normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(normalized[:180])
    return deduped[:3]


def _summarize_harness_warning(message: str) -> str:
    text = str(message).strip()
    if not text:
        return ""
    if "Failed to initialize semantic store" in text:
        return "harness semantic store unavailable (better-sqlite3 binding missing)"
    first_line = text.splitlines()[0].strip()
    return first_line[:180]


def _harness_command(query: str) -> list[str]:
    if shutil.which("harness"):
        return ["harness", "search", query]
    return ["pnpm", "dlx", "--allow-build=better-sqlite3", "@brainwav/coding-harness", "search", query]


def _run_harness_search(query: str, cwd: str) -> tuple[list[dict[str, object]], list[str]]:
    cmd = _harness_command(query)
    proc = sp.run(cmd, cwd=cwd, text=True, capture_output=True)
    payload_text = (proc.stdout or "").strip()
    try:
        payload = json.loads(payload_text)
    except json.JSONDecodeError:
        message = _summarize_harness_warning(proc.stderr or proc.stdout or "")
        if proc.returncode != 0:
            return [], [f"harness search failed for query '{query}': {message or 'unknown error'}"]
        return [], [f"harness search returned non-JSON output for query '{query}'"]

    warnings: list[str] = []
    raw_warnings = payload.get("warnings")
    if isinstance(raw_warnings, list):
        for item in raw_warnings:
            note = _summarize_harness_warning(str(item))
            if note:
                warnings.append(note)
    raw_results = payload.get("results")
    if not isinstance(raw_results, list):
        return [], warnings
    results = [item for item in raw_results if isinstance(item, dict)]
    return results, warnings


def _harness_similarity(
    *,
    skill_name: str,
    skill_src: str,
    existing_dirs: list[str],
    skills_root: str,
) -> tuple[dict[str, float], list[str]]:
    repo_root = _repo_root(skills_root)
    if not repo_root:
        return {}, ["harness: skipped (skills root is not in a git repository)"]
    if shutil.which("harness") is None and shutil.which("pnpm") is None:
        return {}, ["harness: skipped (neither harness nor pnpm found on PATH)"]

    skill_text = _read_text(os.path.join(skill_src, "SKILL.md"))
    queries = _build_harness_queries(skill_name, skill_text)
    if not queries:
        return {}, ["harness: skipped (unable to derive search queries)"]

    existing_rel: dict[str, str] = {}
    for existing in existing_dirs:
        try:
            rel = os.path.relpath(existing, repo_root).replace("\\", "/")
        except ValueError:
            continue
        existing_rel[existing] = rel

    if not existing_rel:
        return {}, ["harness: skipped (installed skills are outside repo root)"]

    raw_scores: dict[str, float] = {path: 0.0 for path in existing_rel}
    warnings: list[str] = []
    semantic_seen = False
    lexical_only_warned = False

    for query in queries:
        results, query_warnings = _run_harness_search(query, repo_root)
        warnings.extend(query_warnings)
        if any("semantic store unavailable" in warning.lower() for warning in query_warnings):
            lexical_only_warned = True
        best_for_query: dict[str, float] = {}
        for index, item in enumerate(results, start=1):
            raw_path = str(item.get("path", "")).strip().replace("\\", "/")
            if not raw_path:
                continue
            source = str(item.get("source", "")).strip().lower()
            if source == "semantic":
                semantic_seen = True
            rank_score = 1.0 / index
            if source == "semantic":
                rank_score *= 1.15
            rank_score = min(rank_score, 1.0)
            for existing_abs, rel in existing_rel.items():
                if raw_path == rel or raw_path.startswith(rel + "/"):
                    current = best_for_query.get(existing_abs, 0.0)
                    if rank_score > current:
                        best_for_query[existing_abs] = rank_score
        for existing_abs, score in best_for_query.items():
            raw_scores[existing_abs] += score

    denominator = max(len(queries), 1)
    normalized = {path: min(score / denominator, 1.0) for path, score in raw_scores.items()}
    if lexical_only_warned and not semantic_seen:
        warnings.append("harness: semantic engine unavailable; using lexical search signals only")
    deduped_warnings = sorted(set(warnings))
    return normalized, deduped_warnings


def _collect_installed_skill_dirs(skills_root: str) -> list[str]:
    root = Path(skills_root).expanduser()
    if not root.is_dir():
        return []
    root_real = root.resolve()
    results: list[str] = []
    for skill_md in root.rglob("SKILL.md"):
        if ".git" in skill_md.parts:
            continue
        try:
            if skill_md.parent.resolve() == root_real:
                continue
        except OSError:
            continue
        results.append(str(skill_md.parent))
    return sorted(set(results))


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 0.0
    union = a | b
    if not union:
        return 0.0
    return len(a & b) / len(union)


def _coverage(candidate: set[str], existing: set[str]) -> float:
    if not candidate:
        return 0.0
    return len(candidate & existing) / len(candidate)


def _weighted_jaccard(a: dict[str, float], b: dict[str, float]) -> float:
    if not a and not b:
        return 0.0
    keys = set(a) | set(b)
    if not keys:
        return 0.0
    numerator = sum(min(a.get(key, 0.0), b.get(key, 0.0)) for key in keys)
    denominator = sum(max(a.get(key, 0.0), b.get(key, 0.0)) for key in keys)
    if denominator <= 0:
        return 0.0
    return numerator / denominator


def _weighted_coverage(source: dict[str, float], target: dict[str, float]) -> float:
    if not source:
        return 0.0
    numerator = 0.0
    denominator = 0.0
    for key, weight in source.items():
        denominator += weight
        numerator += min(weight, target.get(key, 0.0))
    if denominator <= 0:
        return 0.0
    return numerator / denominator


def _negative_overlap_penalty(
    source_focus: set[str],
    source_exclusions: set[str],
    existing_focus: set[str],
    existing_exclusions: set[str],
) -> float:
    source_forbidden_hits = _coverage(source_exclusions, existing_focus)
    existing_forbidden_hits = _coverage(existing_exclusions, source_focus)
    return max(source_forbidden_hits, existing_forbidden_hits) * 0.25


def _confidence_label(
    *,
    score: float,
    same_job: bool,
    intent_score: float,
    advisory_threshold: float,
    block_threshold: float,
) -> str:
    if score >= block_threshold or (same_job and intent_score >= 0.6):
        return "high"
    if score >= max(advisory_threshold + 0.08, 0.25) or same_job:
        return "medium"
    return "low"


def _workspace_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _default_deconflict_artifact_path() -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return str(_workspace_root() / "artifacts" / "deconflict" / f"report-{timestamp}.json")


def _default_merge_proposal_dir() -> str:
    return str(_workspace_root() / "artifacts" / "deconflict" / "proposals")


def _slug(text: str) -> str:
    value = re.sub(r"[^a-z0-9-]+", "-", text.lower())
    value = value.strip("-")
    return value or "skill"


def _skill_name_forms(value: str) -> set[str]:
    base = _slug(os.path.basename(value.rstrip("/")))
    forms = {base, base.replace("-", "")}
    for prefix in ("skill-", "codex-", "agent-"):
        if base.startswith(prefix):
            trimmed = base[len(prefix):]
            if trimmed:
                forms.add(trimmed)
                forms.add(trimmed.replace("-", ""))
    for suffix in ("-skill", "-skills"):
        if base.endswith(suffix):
            trimmed = base[: -len(suffix)]
            if trimmed:
                forms.add(trimmed)
                forms.add(trimmed.replace("-", ""))
    return {item for item in forms if item}


def _names_imply_same_job(candidate_dir: str, existing_dir: str) -> bool:
    candidate_forms = _skill_name_forms(candidate_dir)
    existing_forms = _skill_name_forms(existing_dir)
    return bool(candidate_forms & existing_forms)


def _write_merge_proposal(
    *,
    skill_name: str,
    candidate_dir: str,
    match: DeconflictMatch,
    proposal_dir: str,
) -> str:
    proposal_path = Path(proposal_dir).expanduser()
    proposal_path.mkdir(parents=True, exist_ok=True)
    existing_name = os.path.basename(match.path.rstrip("/"))
    filename = f"{_slug(skill_name)}__into__{_slug(existing_name)}.md"
    target = proposal_path / filename

    lines = [
        f"# Merge proposal: `{skill_name}` -> `{existing_name}`",
        "",
        f"- Candidate: `{candidate_dir}`",
        f"- Existing: `{match.path}`",
        f"- Confidence: **{match.confidence}**",
        f"- Same-job: `{match.same_job}`",
        f"- Score: `{match.score:.2f}` (text `{match.token_score:.2f}`, command `{match.command_score:.2f}`, intent `{match.intent_score:.2f}`, harness `{match.harness_score:.2f}`)",
        "",
        "## Suggested merge checklist",
        "- [ ] Compare Scope/Triggers and keep the stricter trigger language.",
        "- [ ] Merge any missing validation and safety checks.",
        "- [ ] Preserve/extend decision-feedback protocol fields.",
        "- [ ] Re-run quick_validate, skill_gate, analyze_skill, and openclaw_skill_guard.",
    ]
    if match.improvement_hints:
        lines.append("")
        lines.append("## Candidate improvement ideas")
        for hint in match.improvement_hints:
            lines.append(f"- {hint}")

    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(target)


def _evaluate_deconflict_pair(
    *,
    candidate_dir: str,
    existing_dir: str,
    advisory_threshold: float,
    block_threshold: float,
    harness_score: float,
    use_harness: bool,
    harness_has_signal: bool,
    profile_cache: dict[str, dict[str, object]],
) -> DeconflictMatch:
    source_tokens, source_commands, source_intent, source_focus, source_exclusions = _skill_profile(
        candidate_dir,
        profile_cache,
    )
    (
        existing_tokens,
        existing_commands,
        existing_intent,
        existing_focus,
        existing_exclusions,
    ) = _skill_profile(existing_dir, profile_cache)

    token_score = _jaccard(source_tokens, existing_tokens)
    command_score = _coverage(source_commands, existing_commands)
    intent_jaccard = _weighted_jaccard(source_intent, existing_intent)
    intent_coverage = _weighted_coverage(source_intent, existing_intent)
    intent_score = max(intent_jaccard, intent_coverage)

    if use_harness and harness_has_signal:
        raw_score = (0.4 * token_score) + (0.15 * command_score) + (0.2 * harness_score) + (0.25 * intent_score)
    else:
        raw_score = (0.55 * token_score) + (0.2 * command_score) + (0.25 * intent_score)

    penalty = _negative_overlap_penalty(
        source_focus,
        source_exclusions,
        existing_focus,
        existing_exclusions,
    )
    score = max(raw_score - penalty, 0.0)
    focus_overlap = _jaccard(source_focus, existing_focus)
    name_same_job = _names_imply_same_job(candidate_dir, existing_dir)
    same_job = (
        (intent_coverage >= 0.62 and focus_overlap >= 0.25)
        or (intent_score >= 0.5 and focus_overlap >= 0.4)
        or (command_score >= 0.6 and focus_overlap >= 0.35)
    )
    if name_same_job:
        same_job = True
        intent_score = max(intent_score, 0.5)
        score = max(score, advisory_threshold + 0.02, 0.2)
    if penalty >= 0.1 and focus_overlap < 0.35:
        same_job = False

    confidence = _confidence_label(
        score=score,
        same_job=same_job,
        intent_score=intent_score,
        advisory_threshold=advisory_threshold,
        block_threshold=block_threshold,
    )
    if name_same_job and confidence == "low":
        confidence = "medium"
    block_recommended = score >= block_threshold or (
        same_job and confidence in {"high", "medium"} and intent_coverage >= 0.55
    ) or (name_same_job and score >= advisory_threshold)

    return DeconflictMatch(
        path=existing_dir,
        score=score,
        token_score=token_score,
        command_score=command_score,
        harness_score=harness_score,
        intent_score=intent_score,
        same_job=same_job,
        confidence=confidence,
        block_recommended=block_recommended,
        shared_terms=tuple(sorted(source_tokens & existing_tokens)[:10]),
        improvement_hints=tuple(),
    )


def _analyze_deconflicts(
    *,
    skill_name: str,
    skill_src: str,
    advisory_threshold: float,
    block_threshold: float,
    skills_root: str,
    engine: str,
    profile_cache: dict[str, dict[str, object]],
) -> tuple[list[DeconflictMatch], list[str]]:
    source_real = os.path.realpath(skill_src)
    existing_dirs = _collect_installed_skill_dirs(skills_root)
    harness_scores: dict[str, float] = {}
    notes: list[str] = []
    use_harness = engine in {"auto", "harness"}
    if use_harness:
        harness_scores, harness_warnings = _harness_similarity(
            skill_name=skill_name,
            skill_src=skill_src,
            existing_dirs=existing_dirs,
            skills_root=skills_root,
        )
        notes.extend(harness_warnings)
    harness_has_signal = any(score > 0 for score in harness_scores.values())
    if use_harness and not harness_has_signal:
        notes.append("harness: no overlap hits found; using lexical fallback weights")
    elif engine == "lexical":
        notes.append("harness: disabled (deconflict-engine=lexical)")

    matches: list[DeconflictMatch] = []

    for existing_dir in existing_dirs:
        existing_real = os.path.realpath(existing_dir)
        if existing_real == source_real:
            continue
        harness_score = harness_scores.get(existing_dir, 0.0)
        try:
            match = _evaluate_deconflict_pair(
                candidate_dir=skill_src,
                existing_dir=existing_dir,
                advisory_threshold=advisory_threshold,
                block_threshold=block_threshold,
                harness_score=harness_score,
                use_harness=use_harness,
                harness_has_signal=harness_has_signal,
                profile_cache=profile_cache,
            )
        except OSError:
            continue

        if match.score < advisory_threshold and not match.same_job:
            continue

        if match.same_job:
            match.improvement_hints = _generate_improvement_hints(skill_src, existing_dir)
        matches.append(match)

    return sorted(matches, key=lambda item: item.score, reverse=True), notes


def _format_deconflict_report(
    skill_name: str,
    advisory_threshold: float,
    block_threshold: float,
    matches: list[DeconflictMatch],
    notes: list[str],
) -> str:
    block_count = sum(1 for match in matches if match.block_recommended)
    lines = [
        (
            f"Deconflict advisory: '{skill_name}' matched installed skills by overlap >= {advisory_threshold:.0%} "
            "or same-job intent similarity."
        ),
        f"Policy thresholds: advisory={advisory_threshold:.0%}, block={block_threshold:.0%} | block candidates={block_count}",
        "Top overlap matches:",
    ]
    for match in matches[:5]:
        metric = (
            f"overall={match.score:.0%}, text={match.token_score:.0%}, "
            f"commands={match.command_score:.0%}, intent={match.intent_score:.0%}, harness={match.harness_score:.0%}"
        )
        same_job_tag = " [same-job]" if match.same_job else ""
        block_tag = " [block]" if match.block_recommended else ""
        lines.append(f"  - {match.path} ({metric}){same_job_tag}{block_tag} [confidence={match.confidence}]")
        if match.shared_terms:
            lines.append(f"    shared terms: {', '.join(match.shared_terms)}")
        if match.improvement_hints:
            for hint in match.improvement_hints:
                lines.append(f"    improvement idea: {hint}")
        if match.proposal_path:
            lines.append(f"    merge proposal: {match.proposal_path}")
    if notes:
        lines.append("Deconflict notes:")
        for note in notes[:5]:
            lines.append(f"  - {note}")
    lines.extend(
        [
            "Merge-plan (advisory, no filesystem changes):",
            "  1) Compare Scope/Triggers and Deliverables.",
            "  2) Preserve stricter validation and safety gates.",
            "  3) Fold missing capabilities into the existing skill.",
            "  4) Re-run quick_validate, skill_gate, analyze_skill, and openclaw_skill_guard.",
        ]
    )
    return "\n".join(lines)


def _deconflict_requires_confirmation(
    *,
    skill_name: str,
    advisory_threshold: float,
    block_threshold: float,
    matches: list[DeconflictMatch],
    notes: list[str],
    dry_run: bool,
    printed_notes: set[str] | None = None,
) -> bool:
    if not matches:
        for note in notes[:3]:
            if printed_notes is not None and note in printed_notes:
                continue
            if printed_notes is not None:
                printed_notes.add(note)
            print(f"Deconflict note: {note}", file=sys.stderr)
        return True

    has_block = any(match.block_recommended for match in matches)
    print(
        _format_deconflict_report(
            skill_name,
            advisory_threshold,
            block_threshold,
            matches,
            notes,
        ),
        file=sys.stderr,
    )
    if dry_run:
        if has_block:
            print("Dry-run note: real install would pause at block threshold without explicit confirmation.", file=sys.stderr)
        else:
            print("Dry-run note: real install would proceed unless user chooses merge-first.", file=sys.stderr)
        return True

    if not sys.stdin.isatty():
        if has_block:
            print(
                "Install paused: block-threshold match requires confirmation in an interactive run.",
                file=sys.stderr,
            )
            return False
        print("Non-interactive run: advisory-only matches detected; continuing install.", file=sys.stderr)
        return True

    print("Choose an action:", file=sys.stderr)
    print("  [M] Merge/improve existing skill first (stop install)", file=sys.stderr)
    if has_block:
        print("  [I] Install anyway (explicit override)", file=sys.stderr)
        print("  [S] Stop", file=sys.stderr)
        choice = input(f"Action for {skill_name} (M/I/S): ").strip().lower()
        if choice in {"i", "install"}:
            print("Continuing install by explicit user override.", file=sys.stderr)
            return True
        print("Install paused for merge-first workflow.", file=sys.stderr)
        return False

    print("  [C] Continue install", file=sys.stderr)
    print("  [S] Stop", file=sys.stderr)
    choice = input(f"Action for {skill_name} (M/C/S): ").strip().lower()
    if choice in {"", "c", "continue"}:
        print("Continuing install (advisory-only overlap).", file=sys.stderr)
        return True
    print("Install paused for deconflict review.", file=sys.stderr)
    return False


def _kg_node_id(path: str) -> str:
    normalized = os.path.realpath(path).replace("\\", "/")
    return f"skill:{normalized}"


def _default_deconflict_cache_path() -> str:
    return str(_workspace_root() / "artifacts" / "deconflict" / "profile-cache.json")


def _write_deconflict_artifact(
    *,
    path: str,
    source: Source,
    args: Args,
    run_mode: str,
    skill_entries: list[dict[str, object]],
) -> str:
    artifact_path = Path(path).expanduser()
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    nodes: dict[str, dict[str, object]] = {}
    edges: list[dict[str, object]] = []

    for entry in skill_entries:
        candidate_dir = str(entry.get("candidate_source_dir", ""))
        candidate_name = str(entry.get("skill_name", ""))
        if candidate_dir:
            node_id = _kg_node_id(candidate_dir)
            nodes[node_id] = {
                "id": node_id,
                "type": "candidate_skill",
                "name": candidate_name,
                "path": candidate_dir,
            }
        for match in entry.get("deconflict_matches", []):
            if not isinstance(match, dict):
                continue
            existing_path = str(match.get("path", ""))
            if not existing_path:
                continue
            existing_id = _kg_node_id(existing_path)
            nodes.setdefault(
                existing_id,
                {
                    "id": existing_id,
                    "type": "installed_skill",
                    "name": os.path.basename(existing_path.rstrip("/")),
                    "path": existing_path,
                },
            )
            if not candidate_dir:
                continue
            source_id = _kg_node_id(candidate_dir)
            edges.append(
                {
                    "source": source_id,
                    "target": existing_id,
                    "type": "same_job_candidate" if bool(match.get("same_job")) else "overlaps_with",
                    "weight": float(match.get("score", 0.0)),
                    "confidence": str(match.get("confidence", "low")),
                    "block_recommended": bool(match.get("block_recommended", False)),
                    "improvement_hints": list(match.get("improvement_hints", [])),
                }
            )

    payload = {
        "schema_version": "1.1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "knowledge_graph_profile": "utilities/skill-installer/references/task-profile.json",
        "mode": run_mode,
        "source": {
            "owner": source.owner,
            "repo": source.repo,
            "ref": source.ref,
            "paths": source.paths,
        },
        "thresholds": {
            "advisory": args.deconflict_threshold,
            "block": args.deconflict_block_threshold,
        },
        "engine": args.deconflict_engine,
        "skills": skill_entries,
        "knowledge_graph": {
            "nodes": list(nodes.values()),
            "edges": edges,
        },
    }
    artifact_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return str(artifact_path)


def _serialize_deconflict_match(match: DeconflictMatch) -> dict[str, object]:
    return {
        "path": match.path,
        "score": match.score,
        "token_score": match.token_score,
        "command_score": match.command_score,
        "intent_score": match.intent_score,
        "harness_score": match.harness_score,
        "same_job": match.same_job,
        "confidence": match.confidence,
        "block_recommended": match.block_recommended,
        "shared_terms": list(match.shared_terms),
        "improvement_hints": list(match.improvement_hints),
        "proposal_path": match.proposal_path,
    }


def _load_benchmark_dataset(path: str) -> list[dict[str, object]]:
    dataset_path = Path(path).expanduser()
    raw = json.loads(dataset_path.read_text(encoding="utf-8"))
    if isinstance(raw, dict):
        cases = raw.get("cases", [])
    else:
        cases = raw
    if not isinstance(cases, list):
        raise InstallError("Benchmark dataset must be a list of cases or an object with `cases`.")
    normalized: list[dict[str, object]] = []
    for case in cases:
        if isinstance(case, dict):
            normalized.append(case)
    return normalized


def _run_deconflict_benchmark(args: Args) -> int:
    benchmark_file = args.benchmark_file or str(
        Path(__file__).resolve().parents[1] / "references" / "deconflict-benchmarks.json"
    )
    cases = _load_benchmark_dataset(benchmark_file)
    workspace = _workspace_root()
    profile_cache: dict[str, dict[str, object]] = {}
    failures: list[dict[str, object]] = []
    passes = 0

    for case in cases:
        candidate_rel = str(case.get("candidate", "")).strip()
        existing_rel = str(case.get("existing", "")).strip()
        expect_same_job = bool(case.get("expect_same_job", False))
        min_score = float(case.get("expect_min_score", 0.0))
        max_score = float(case.get("expect_max_score", 1.0))
        case_id = str(case.get("id", f"{candidate_rel}->{existing_rel}"))

        candidate_dir = workspace / candidate_rel
        existing_dir = workspace / existing_rel
        if not (candidate_dir / "SKILL.md").exists() or not (existing_dir / "SKILL.md").exists():
            failures.append({"id": case_id, "reason": "missing SKILL.md for candidate or existing path"})
            continue

        use_harness = args.deconflict_engine in {"auto", "harness"}
        harness_score = 0.0
        harness_has_signal = False
        harness_notes: list[str] = []
        if use_harness:
            harness_scores, harness_notes = _harness_similarity(
                skill_name=candidate_dir.name,
                skill_src=str(candidate_dir),
                existing_dirs=[str(existing_dir)],
                skills_root=str(workspace),
            )
            harness_score = harness_scores.get(str(existing_dir), 0.0)
            harness_has_signal = harness_score > 0

        try:
            match = _evaluate_deconflict_pair(
                candidate_dir=str(candidate_dir),
                existing_dir=str(existing_dir),
                advisory_threshold=0.0,
                block_threshold=args.deconflict_block_threshold,
                harness_score=harness_score,
                use_harness=use_harness,
                harness_has_signal=harness_has_signal,
                profile_cache=profile_cache,
            )
        except OSError as exc:
            failures.append({"id": case_id, "reason": f"pair evaluation failed: {exc}"})
            continue

        if expect_same_job:
            if not match.same_job or match.score < min_score:
                failures.append(
                    {
                        "id": case_id,
                        "reason": "expected same-job match not found",
                        "score": match.score,
                        "same_job": match.same_job,
                        "harness_notes": harness_notes,
                    }
                )
                continue
        else:
            if match.same_job or match.score > max_score:
                failures.append(
                    {
                        "id": case_id,
                        "reason": "unexpected high-overlap/same-job match",
                        "score": match.score,
                        "same_job": match.same_job,
                        "harness_notes": harness_notes,
                    }
                )
                continue

        passes += 1

    summary = {
        "dataset": benchmark_file,
        "engine": args.deconflict_engine,
        "cases_total": len(cases),
        "cases_passed": passes,
        "cases_failed": len(failures),
        "failures": failures,
    }
    print(json.dumps(summary, indent=2))
    return 0 if not failures else 1


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


def _emit_force_unsafe_audit(
    *,
    skill_name: str,
    skill_path: str,
    warnings: list["RiskFinding"],
    mode: str,
) -> None:
    """Append a timestamped audit record when --force-unsafe overrides a high-severity block.

    Written to ~/.local/share/agent-skills/force-unsafe-audit.jsonl so that
    override usage is never invisible. Failures are non-fatal.
    """
    import fcntl
    import datetime

    audit_dir = Path.home() / ".local" / "share" / "agent-skills"
    audit_path = audit_dir / "force-unsafe-audit.jsonl"
    record = {
        "ts": datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "mode": mode,
        "skill_name": skill_name,
        "skill_path": skill_path,
        "findings": [
            {"severity": w.severity, "rule": getattr(w, "rule", ""), "message": str(w)[:200]}
            for w in warnings
            if w.severity == "high"
        ],
    }
    try:
        audit_dir.mkdir(parents=True, exist_ok=True)
        with audit_path.open("a", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            f.write(json.dumps(record, sort_keys=True) + "\n")
            f.flush()
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        print(f"[force-unsafe] override audited → {audit_path}", file=sys.stderr)
    except Exception as exc:  # pragma: no cover
        print(f"[force-unsafe] WARNING: audit log write failed ({exc}); continuing anyway.", file=sys.stderr)


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

    if has_high and force_unsafe:
        _emit_force_unsafe_audit(skill_name=skill_name, skill_path=skill_path, warnings=warnings, mode="install")
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


def _should_proceed_in_dry_run(
    warnings: list[RiskFinding],
    *,
    mode: str,
    force_unsafe: bool,
) -> bool:
    if not warnings:
        return True
    has_high = any(warning.severity == "high" for warning in warnings)
    if has_high and not force_unsafe:
        print(_format_warnings(warnings), file=sys.stderr)
        print(
            "Dry-run blocked: high-severity findings detected. Re-run with --force-unsafe to continue.",
            file=sys.stderr,
        )
        return False
    if has_high and force_unsafe:
        _emit_force_unsafe_audit(skill_name="<dry-run>", skill_path="", warnings=warnings, mode="dry-run")
    print(_format_warnings(warnings), file=sys.stderr)
    if mode == "stop":
        print("Dry-run stopped due to on-warning=stop.", file=sys.stderr)
        return False
    if mode == "prompt":
        print(
            "Dry-run continues after warning scan; no files will be changed.",
            file=sys.stderr,
        )
        return True
    print("Dry-run continuing despite warnings.", file=sys.stderr)
    return True


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
    if args.skill:
        if args.url or args.repo or args.path:
            raise InstallError("Use --skill without --url/--repo/--path.")
        _validate_skill_name(args.skill)
        return Source(
            owner="openai",
            repo="skills",
            ref=args.ref,
            paths=[f"skills/.curated/{args.skill}"],
        )

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


def _ratio(text: str) -> float:
    try:
        value = float(text)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be a float between 0 and 1") from exc
    if value < 0 or value > 1:
        raise argparse.ArgumentTypeError("must be between 0 and 1")
    return value


def _parse_args(argv: list[str]) -> Args:
    parser = argparse.ArgumentParser(description="Install a skill from GitHub.")
    parser.add_argument("--repo", help="owner/repo")
    parser.add_argument(
        "--skill",
        help="Curated skill name from openai/skills/.curated/<name>",
    )
    parser.add_argument("--url", help="https://github.com/owner/repo[/tree/ref/path]")
    parser.add_argument(
        "--path",
        nargs="+",
        help="Path(s) to skill(s) inside repo",
    )
    parser.add_argument(
        "--ref",
        default=DEFAULT_REF,
        help="Git ref (branch, tag, or full 40-char commit SHA). Prefer a full SHA for reproducibility.",
    )
    parser.add_argument(
        "--require-pinned-ref",
        action="store_true",
        help=(
            "Hard-fail if --ref is a mutable branch or tag instead of a full 40-character "
            "commit SHA. Recommended for CI/automation to ensure reproducible installs."
        ),
    )
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
        "--dry-run",
        action="store_true",
        help="Validate inputs and scan risks without copying files or running evaluations.",
    )
    parser.add_argument(
        "--deconflict",
        action="store_true",
        help="Advisory mode: scan installed skills for overlap and require confirmation before high-overlap installs.",
    )
    parser.add_argument(
        "--deconflict-threshold",
        type=_ratio,
        default=0.2,
        help="Advisory overlap threshold (0-1, default: 0.2).",
    )
    parser.add_argument(
        "--deconflict-block-threshold",
        type=_ratio,
        default=0.45,
        help="Blocking overlap threshold (0-1, default: 0.45).",
    )
    parser.add_argument(
        "--deconflict-engine",
        choices=["auto", "harness", "lexical"],
        default="auto",
        help="Deconflict scoring engine (default: auto; prefers coding-harness search).",
    )
    parser.add_argument(
        "--deconflict-cache-path",
        help="Path for reusable deconflict profile cache JSON.",
    )
    parser.add_argument(
        "--deconflict-artifact-path",
        help="Write structured deconflict artifact JSON (default: artifacts/deconflict/report-<timestamp>.json).",
    )
    parser.add_argument(
        "--merge-proposal",
        action="store_true",
        help="Generate merge proposal markdown files for same-job matches.",
    )
    parser.add_argument(
        "--merge-proposal-dir",
        help="Directory for merge proposal markdown files (default: artifacts/deconflict/proposals).",
    )
    parser.add_argument(
        "--run-deconflict-benchmark",
        action="store_true",
        help="Run deconflict benchmark dataset and exit.",
    )
    parser.add_argument(
        "--benchmark-file",
        help="Path to benchmark dataset JSON.",
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
        if args.run_deconflict_benchmark:
            return _run_deconflict_benchmark(args)

        source = _resolve_source(args)
        source.ref = source.ref or args.ref
        if not source.paths:
            raise InstallError("No skill paths provided.")
        for path in source.paths:
            _validate_relative_path(path)

        # Emit a medium-severity warning (or hard-fail with --require-pinned-ref)
        # when the resolved ref is a mutable branch/tag rather than a pinned SHA.
        ref_findings = _validate_ref_is_pinned(source.ref, getattr(args, "require_pinned_ref", False))
        if ref_findings and not args.dry_run:
            if not _should_continue_after_warning(
                ref_findings,
                mode=args.on_warning,
                skill_name="<ref-check>",
                skill_path="",
                force_unsafe=args.force_unsafe,
            ):
                raise InstallError("Install stopped due to unpinned ref warning.")

        if args.dest:
            dest_root = args.dest
        else:
            if not args.category:
                raise InstallError("Missing --category (required when --dest is not set).")
            _validate_category_name(args.category)
            dest_root = os.path.join(_skills_root(), args.category)

        profile_cache_path: str | None = None
        profile_cache: dict[str, dict[str, object]] = {}
        if args.deconflict:
            profile_cache_path = args.deconflict_cache_path or _default_deconflict_cache_path()
            profile_cache = _load_deconflict_cache(profile_cache_path)

        run_mode = "dry-run" if args.dry_run else "install"
        skill_entries: list[dict[str, object]] = []

        tmp_dir = tempfile.mkdtemp(prefix="skill-install-", dir=_tmp_root())
        try:
            repo_root = _prepare_repo(source, args.method, tmp_dir)
            installed = []
            printed_deconflict_notes: set[str] = set()
            for path in source.paths:
                skill_name = args.name if len(source.paths) == 1 else None
                skill_name = skill_name or os.path.basename(path.rstrip("/"))
                if skill_name in {"", "."}:
                    skill_name = source.repo
                _validate_skill_name(skill_name)
                if not skill_name:
                    raise InstallError("Unable to derive skill name.")
                dest_dir = os.path.join(dest_root, skill_name)
                if os.path.exists(dest_dir):
                    raise InstallError(f"Destination already exists: {dest_dir}")
                skill_src = os.path.join(repo_root, path)
                _validate_skill(skill_src)

                entry: dict[str, object] = {
                    "skill_name": skill_name,
                    "candidate_source_dir": os.path.realpath(skill_src),
                    "destination_dir": os.path.realpath(dest_dir),
                    "status": "planned",
                }

                if args.deconflict:
                    deconflicts, deconflict_notes = _analyze_deconflicts(
                        skill_name=skill_name,
                        skill_src=skill_src,
                        advisory_threshold=args.deconflict_threshold,
                        block_threshold=args.deconflict_block_threshold,
                        skills_root=_skills_root(),
                        engine=args.deconflict_engine,
                        profile_cache=profile_cache,
                    )

                    if args.merge_proposal:
                        proposal_dir = args.merge_proposal_dir or _default_merge_proposal_dir()
                        for match in deconflicts:
                            if not match.same_job:
                                continue
                            match.proposal_path = _write_merge_proposal(
                                skill_name=skill_name,
                                candidate_dir=skill_src,
                                match=match,
                                proposal_dir=proposal_dir,
                            )

                    entry["deconflict_matches"] = [
                        _serialize_deconflict_match(match) for match in deconflicts
                    ]
                    entry["deconflict_notes"] = list(deconflict_notes)

                    if not _deconflict_requires_confirmation(
                        skill_name=skill_name,
                        advisory_threshold=args.deconflict_threshold,
                        block_threshold=args.deconflict_block_threshold,
                        matches=deconflicts,
                        notes=deconflict_notes,
                        dry_run=args.dry_run,
                        printed_notes=printed_deconflict_notes,
                    ):
                        raise InstallError(f"Install paused by deconflict gate for {skill_name}.")

                warnings = _scan_skill_for_risks(skill_src)
                entry["risk_warnings"] = [
                    {
                        "source": warning.source,
                        "severity": warning.severity,
                        "message": warning.message,
                    }
                    for warning in warnings
                ]

                if args.dry_run:
                    if not _should_proceed_in_dry_run(
                        warnings,
                        mode=args.on_warning,
                        force_unsafe=args.force_unsafe,
                    ):
                        raise InstallError(f"Dry-run blocked for {skill_name}.")
                    print(f"DRY-RUN: would install {skill_name} to {dest_dir}")
                    installed.append((skill_name, dest_dir))
                    entry["status"] = "dry-run-pass"
                    skill_entries.append(entry)
                    continue

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
                entry["status"] = "installed"
                skill_entries.append(entry)
        finally:
            if os.path.isdir(tmp_dir):
                shutil.rmtree(tmp_dir, ignore_errors=True)

        if args.deconflict:
            artifact_path = args.deconflict_artifact_path or _default_deconflict_artifact_path()
            artifact_written = _write_deconflict_artifact(
                path=artifact_path,
                source=source,
                args=args,
                run_mode=run_mode,
                skill_entries=skill_entries,
            )
            print(f"Deconflict artifact: {artifact_written}", file=sys.stderr)
            _save_deconflict_cache(profile_cache_path, profile_cache)

        if args.dry_run:
            for skill_name, dest_dir in installed:
                print(f"DRY-RUN PASS: {skill_name} would install to {dest_dir}")
            return 0

        for skill_name, dest_dir in installed:
            print(f"Installed {skill_name} to {dest_dir}")
        return 0
    except InstallError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
