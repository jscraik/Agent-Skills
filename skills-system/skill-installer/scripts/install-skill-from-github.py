#!/usr/bin/env python3
"""Install one or more skills from GitHub into $CODEX_HOME/skills.

This installer enforces source provenance and transactional activation:
- pinned refs are required by default (`--ref` must be a 40-char commit SHA)
- imported skills are staged in quarantine before activation
- activation promotes staged skills atomically
- rollback journal records every step and restores state on failure
- provenance manifest is written for every successful install batch
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import zipfile

from github_utils import github_request

DEFAULT_REF = "main"
PINNED_REF_RE = re.compile(r"^[0-9a-fA-F]{40}$")
DEFAULT_TRUSTED_REPOS = {
    "openai/skills",
    "jamiecraik/agent-skills",
}


@dataclass
class Args:
    url: str | None = None
    repo: str | None = None
    path: list[str] | None = None
    ref: str = DEFAULT_REF
    dest: str | None = None
    name: str | None = None
    method: str = "auto"
    allow_unpinned_ref: bool = False
    provenance_dir: str | None = None
    journal_dir: str | None = None
    trusted_repo: list[str] | None = None
    allow_untrusted_source: bool = False
    validation_level: str = "strict"


@dataclass
class Source:
    owner: str
    repo: str
    ref: str
    paths: list[str]
    repo_url: str | None = None


@dataclass
class PreparedRepo:
    repo_root: str
    resolved_commit: str
    source_method: str


@dataclass
class StagedInstall:
    skill_name: str
    source_path: str
    staged_dir: str
    destination_dir: str
    tree_sha256: str
    file_count: int
    bytes_total: int
    validation: dict[str, object]


class InstallError(Exception):
    pass


class JournalWriter:
    """Append-only install journal for rollback and audit diagnostics."""

    def __init__(self, path: str):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(self.path, "a", encoding="utf-8"):
            pass

    def write(self, event: str, **details: object) -> None:
        row = {
            "timestamp": _utc_now_iso(),
            "event": event,
            "details": details,
        }
        with open(self.path, "a", encoding="utf-8") as file_handle:
            file_handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def _utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _codex_home() -> str:
    return os.environ.get("CODEX_HOME", os.path.expanduser("~/.codex"))


def _tmp_root() -> str:
    base = os.path.join(tempfile.gettempdir(), "codex")
    os.makedirs(base, exist_ok=True)
    return base


def _request(url: str) -> bytes:
    return github_request(url, "codex-skill-install")


def _is_pinned_ref(ref: str) -> bool:
    return bool(PINNED_REF_RE.fullmatch(ref.strip()))


def _resolve_commit_sha(owner: str, repo: str, ref: str) -> str:
    encoded_ref = urllib.parse.quote(ref, safe="")
    api_url = f"https://api.github.com/repos/{owner}/{repo}/commits/{encoded_ref}"
    try:
        payload = _request(api_url)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            raise InstallError(f"Ref not found for provenance resolution: {owner}/{repo}@{ref}") from exc
        raise InstallError(f"Provenance resolution failed: HTTP {exc.code}") from exc

    try:
        data = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise InstallError("Could not parse commit provenance response from GitHub API.") from exc

    sha = data.get("sha") if isinstance(data, dict) else None
    if not isinstance(sha, str) or not _is_pinned_ref(sha):
        raise InstallError("GitHub API did not return a valid commit SHA for provenance.")
    return sha.lower()


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


def _run_git(args: list[str]) -> str:
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise InstallError(result.stderr.strip() or "Git command failed.")
    return result.stdout.strip()


def _safe_extract_zip(zip_file: zipfile.ZipFile, dest_dir: str) -> None:
    dest_root = os.path.realpath(dest_dir)
    for info in zip_file.infolist():
        extracted_path = os.path.realpath(os.path.join(dest_dir, info.filename))
        if extracted_path == dest_root or extracted_path.startswith(dest_root + os.sep):
            continue
        raise InstallError("Archive contains files outside the destination.")
    zip_file.extractall(dest_dir)


def _validate_relative_path(path: str) -> None:
    normalized = os.path.normpath(path)
    if os.path.isabs(path) or normalized.startswith(".."):
        raise InstallError("Skill path must be a relative path inside the repo.")


def _validate_skill_name(name: str) -> None:
    altsep = os.path.altsep
    if not name or os.path.sep in name or (altsep and altsep in name):
        raise InstallError("Skill name must be a single path segment.")
    if name in (".", ".."):
        raise InstallError("Invalid skill name.")


def _git_sparse_checkout(repo_url: str, ref: str, paths: list[str], dest_dir: str) -> tuple[str, str]:
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
    resolved_commit = _run_git(["git", "-C", repo_dir, "rev-parse", "HEAD"])
    if not _is_pinned_ref(resolved_commit):
        raise InstallError("Could not resolve a valid pinned commit from git checkout.")
    return repo_dir, resolved_commit.lower()


def _validate_skill(path: str) -> None:
    if not os.path.isdir(path):
        raise InstallError(f"Skill path not found: {path}")

    skill_md = os.path.join(path, "SKILL.md")
    if not os.path.isfile(skill_md):
        raise InstallError("SKILL.md not found in selected skill directory.")

    refs_dir = os.path.join(path, "references")
    contract_path = os.path.join(refs_dir, "contract.yaml")
    evals_path = os.path.join(refs_dir, "evals.yaml")
    if not os.path.isfile(contract_path):
        raise InstallError("references/contract.yaml not found in selected skill directory.")
    if not os.path.isfile(evals_path):
        raise InstallError("references/evals.yaml not found in selected skill directory.")


def _normalize_repo_id(repo_text: str) -> str:
    parts = [p.strip() for p in repo_text.split("/") if p.strip()]
    if len(parts) != 2:
        raise InstallError(f"Trusted repo must be owner/repo: {repo_text}")
    return f"{parts[0].lower()}/{parts[1].lower()}"


def _trusted_repo_allowlist(raw_repos: list[str] | None) -> set[str]:
    allowlist = set(DEFAULT_TRUSTED_REPOS)
    env_raw = os.environ.get("CODEX_SKILL_TRUSTED_REPOS", "")
    if env_raw.strip():
        for item in env_raw.split(","):
            item = item.strip()
            if item:
                allowlist.add(_normalize_repo_id(item))

    for repo_text in raw_repos or []:
        allowlist.add(_normalize_repo_id(repo_text))
    return allowlist


def _repo_root_from_installer() -> Path:
    return Path(__file__).resolve().parents[3]


def _validator_paths(repo_root: Path) -> dict[str, Path]:
    return {
        "quick_validate": repo_root / "utilities" / "skill-builder" / "scripts" / "quick_validate.py",
        "skill_gate": repo_root / "utilities" / "skill-builder" / "scripts" / "skill_gate.py",
        "openclaw": repo_root / "utilities" / "skill-builder" / "scripts" / "openclaw_skill_guard.py",
    }


def _run_stage_validators(skill_dir: str, journal: JournalWriter, validation_level: str) -> dict[str, object]:
    result: dict[str, object] = {
        "validation_level": validation_level,
        "validators": [],
    }

    if validation_level == "compat":
        journal.write("stage_validation_skipped", skill_dir=skill_dir, validation_level=validation_level)
        return result

    repo_root = _repo_root_from_installer()
    validators = _validator_paths(repo_root)
    missing = [name for name, path in validators.items() if not path.exists()]
    if missing:
        raise InstallError(
            "Strict stage validation requires repo validator scripts. Missing: "
            + ", ".join(sorted(missing))
            + ". Re-run with --validation-level compat only if your environment intentionally lacks the validator bundle."
        )

    commands: list[tuple[str, list[str]]] = [
        (
            "quick_validate",
            [sys.executable, str(validators["quick_validate"]), skill_dir, "--mode", "compat"],
        ),
        (
            "skill_gate",
            [
                sys.executable,
                str(validators["skill_gate"]),
                skill_dir,
                "--require-fail-fast",
                "--require-security-evals",
                "--pi-high-fail",
            ],
        ),
        (
            "openclaw",
            [
                sys.executable,
                str(validators["openclaw"]),
                skill_dir,
                "--mode",
                "both",
                "--format",
                "json",
            ],
        ),
    ]

    for validator_name, command in commands:
        proc = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout = proc.stdout or ""
        stderr = proc.stderr or ""
        command_text = " ".join(command)
        validator_result = {
            "name": validator_name,
            "command": command_text,
            "exit_code": proc.returncode,
        }
        cast_list = result["validators"]
        assert isinstance(cast_list, list)
        cast_list.append(validator_result)
        journal.write(
            "stage_validator_result",
            skill_dir=skill_dir,
            validator=validator_name,
            command=command_text,
            exit_code=proc.returncode,
            stdout_tail=stdout[-800:],
            stderr_tail=stderr[-800:],
        )
        if proc.returncode != 0:
            raise InstallError(
                f"Staged validation failed ({validator_name}) for {skill_dir}. "
                "See rollback journal for command output tail."
            )

    return result


def _copy_skill(src: str, dest_dir: str) -> None:
    os.makedirs(os.path.dirname(dest_dir), exist_ok=True)
    if os.path.exists(dest_dir):
        raise InstallError(f"Destination already exists: {dest_dir}")
    shutil.copytree(src, dest_dir)


def _promote_skill(staged_dir: str, destination_dir: str) -> None:
    os.makedirs(os.path.dirname(destination_dir), exist_ok=True)
    if os.path.exists(destination_dir):
        raise InstallError(f"Destination already exists: {destination_dir}")
    os.replace(staged_dir, destination_dir)


def _rollback_promoted(promoted_dirs: list[str], journal: JournalWriter) -> list[str]:
    errors: list[str] = []
    for directory in reversed(promoted_dirs):
        try:
            if os.path.isdir(directory):
                shutil.rmtree(directory)
            journal.write("rollback_removed_destination", path=directory)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{directory}: {exc}")
            journal.write("rollback_remove_failed", path=directory, error=str(exc))
    return errors


def _build_repo_url(owner: str, repo: str) -> str:
    return f"https://github.com/{owner}/{repo}.git"


def _build_repo_ssh(owner: str, repo: str) -> str:
    return f"git@github.com:{owner}/{repo}.git"


def _prepare_repo(source: Source, method: str, tmp_dir: str) -> PreparedRepo:
    if method in ("download", "auto"):
        try:
            repo_root = _download_repo_zip(source.owner, source.repo, source.ref, tmp_dir)
            try:
                resolved_commit = _resolve_commit_sha(source.owner, source.repo, source.ref)
            except InstallError:
                if _is_pinned_ref(source.ref):
                    resolved_commit = source.ref.lower()
                else:
                    raise
            return PreparedRepo(repo_root=repo_root, resolved_commit=resolved_commit, source_method="download")
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
            repo_root, resolved_commit = _git_sparse_checkout(repo_url, source.ref, source.paths, tmp_dir)
        except InstallError:
            repo_url = _build_repo_ssh(source.owner, source.repo)
            repo_root, resolved_commit = _git_sparse_checkout(repo_url, source.ref, source.paths, tmp_dir)
        return PreparedRepo(repo_root=repo_root, resolved_commit=resolved_commit, source_method="git")

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
        return _resolve_source(Args(url=args.repo, repo=None, path=args.path, ref=args.ref))

    repo_parts = [p for p in args.repo.split("/") if p]
    if len(repo_parts) != 2:
        raise InstallError("--repo must be in owner/repo format.")
    if not args.path:
        raise InstallError("Missing --path for --repo.")

    return Source(
        owner=repo_parts[0],
        repo=repo_parts[1],
        ref=args.ref,
        paths=list(args.path),
    )


def _default_dest() -> str:
    return os.path.join(_codex_home(), "skills")


def _default_provenance_dir(dest_root: str) -> str:
    return os.path.join(dest_root, ".provenance", "skill-installer")


def _default_journal_dir(dest_root: str) -> str:
    return os.path.join(dest_root, ".install-journal", "skill-installer")


def _run_id() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _hash_tree(path: str) -> tuple[str, int, int]:
    hasher = hashlib.sha256()
    file_count = 0
    bytes_total = 0

    for root, dirs, files in os.walk(path):
        dirs.sort()
        files.sort()
        rel_root = os.path.relpath(root, path)
        for filename in files:
            full_path = os.path.join(root, filename)
            rel_path = filename if rel_root == "." else os.path.join(rel_root, filename)
            rel_norm = rel_path.replace(os.sep, "/")

            stat = os.stat(full_path)
            file_count += 1
            bytes_total += int(stat.st_size)

            hasher.update(rel_norm.encode("utf-8"))
            hasher.update(b"\0")
            hasher.update(str(stat.st_mode & 0o777).encode("utf-8"))
            hasher.update(b"\0")

            with open(full_path, "rb") as file_handle:
                for chunk in iter(lambda: file_handle.read(1024 * 64), b""):
                    hasher.update(chunk)

    return hasher.hexdigest(), file_count, bytes_total


def _write_json_atomic(path: str, payload: dict[str, object]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    temp_path = path + ".tmp"
    with open(temp_path, "w", encoding="utf-8") as file_handle:
        json.dump(payload, file_handle, indent=2, ensure_ascii=False)
        file_handle.write("\n")
    os.replace(temp_path, path)


def _parse_args(argv: list[str]) -> Args:
    parser = argparse.ArgumentParser(description="Install one or more skills from GitHub.")
    parser.add_argument("--repo", help="owner/repo")
    parser.add_argument("--url", help="https://github.com/owner/repo[/tree/ref/path]")
    parser.add_argument("--path", nargs="+", help="Path(s) to skill(s) inside repo")
    parser.add_argument(
        "--ref",
        default=DEFAULT_REF,
        help="Source ref to fetch. Must be a 40-char commit SHA unless --allow-unpinned-ref is set.",
    )
    parser.add_argument("--dest", help="Destination skills directory")
    parser.add_argument("--name", help="Destination skill name (defaults to basename of path)")
    parser.add_argument("--method", choices=["auto", "download", "git"], default="auto")
    parser.add_argument(
        "--allow-unpinned-ref",
        action="store_true",
        help="Allow non-SHA refs (branch/tag). Not recommended for production provenance.",
    )
    parser.add_argument(
        "--provenance-dir",
        help="Directory where provenance manifests are written (default: <dest>/.provenance/skill-installer).",
    )
    parser.add_argument(
        "--journal-dir",
        help="Directory where rollback journals are written (default: <dest>/.install-journal/skill-installer).",
    )
    parser.add_argument(
        "--trusted-repo",
        action="append",
        default=[],
        help=(
            "Additional trusted source in owner/repo format (repeatable). "
            "Default trust allowlist includes openai/skills and jamiecraik/agent-skills."
        ),
    )
    parser.add_argument(
        "--allow-untrusted-source",
        action="store_true",
        help=(
            "Allow source repos outside the trusted allowlist. "
            "Use only with explicit approval and audit intent."
        ),
    )
    parser.add_argument(
        "--validation-level",
        choices=["strict", "compat"],
        default="strict",
        help=(
            "Staged validation policy before promotion: "
            "strict runs quick_validate + skill_gate + openclaw in quarantine; "
            "compat keeps basic structural checks only."
        ),
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

        trusted_repos = _trusted_repo_allowlist(args.trusted_repo)
        requested_repo = _normalize_repo_id(f"{source.owner}/{source.repo}")
        source_trusted = requested_repo in trusted_repos
        if not source_trusted and not args.allow_untrusted_source:
            allowed = ", ".join(sorted(trusted_repos))
            raise InstallError(
                "Source repository is not in the trusted allowlist. "
                f"requested={requested_repo}; allowlist={allowed}. "
                "Pass --trusted-repo owner/repo to extend trust or --allow-untrusted-source with explicit approval."
            )

        ref_pinned = _is_pinned_ref(source.ref)
        if not ref_pinned and not args.allow_unpinned_ref:
            raise InstallError(
                "Ref pinning is required. Provide --ref <40-char commit SHA> (or URL with /tree/<sha>/...), "
                "or pass --allow-unpinned-ref explicitly."
            )

        dest_root = os.path.realpath(args.dest or _default_dest())
        os.makedirs(dest_root, exist_ok=True)

        run_id = _run_id()
        provenance_dir = os.path.realpath(args.provenance_dir or _default_provenance_dir(dest_root))
        journal_dir = os.path.realpath(args.journal_dir or _default_journal_dir(dest_root))
        journal_path = os.path.join(journal_dir, f"{run_id}.jsonl")
        journal = JournalWriter(journal_path)

        journal.write(
            "install_started",
            run_id=run_id,
            owner=source.owner,
            repo=source.repo,
            requested_ref=source.ref,
            requested_paths=source.paths,
            destination_root=dest_root,
            allow_unpinned_ref=bool(args.allow_unpinned_ref),
            trusted_source=source_trusted,
            requested_repo=requested_repo,
            validation_level=args.validation_level,
        )

        if not ref_pinned:
            journal.write("unpinned_ref_override", ref=source.ref)
        if not source_trusted:
            journal.write("untrusted_source_override", repo=requested_repo)

        tmp_dir = tempfile.mkdtemp(prefix="skill-install-", dir=_tmp_root())
        quarantine_root = os.path.join(dest_root, ".quarantine", f"skill-install-{run_id}")
        os.makedirs(quarantine_root, exist_ok=True)

        installed: list[StagedInstall] = []
        promoted_dirs: list[str] = []

        try:
            prepared = _prepare_repo(source, args.method, tmp_dir)
            journal.write(
                "source_prepared",
                method=prepared.source_method,
                resolved_commit=prepared.resolved_commit,
                repo_root=prepared.repo_root,
            )

            if ref_pinned and prepared.resolved_commit.lower() != source.ref.lower():
                raise InstallError(
                    "Resolved commit does not match requested pinned ref. "
                    f"requested={source.ref} resolved={prepared.resolved_commit}"
                )

            for path in source.paths:
                skill_name = args.name if len(source.paths) == 1 else None
                skill_name = skill_name or os.path.basename(path.rstrip("/"))
                _validate_skill_name(skill_name)
                if not skill_name:
                    raise InstallError("Unable to derive skill name.")

                destination_dir = os.path.join(dest_root, skill_name)
                if os.path.exists(destination_dir):
                    raise InstallError(f"Destination already exists: {destination_dir}")

                source_path = os.path.join(prepared.repo_root, path)
                _validate_skill(source_path)

                staged_dir = os.path.join(quarantine_root, skill_name)
                _copy_skill(source_path, staged_dir)
                _validate_skill(staged_dir)
                validation_result = _run_stage_validators(staged_dir, journal, args.validation_level)
                tree_sha256, file_count, bytes_total = _hash_tree(staged_dir)

                staged = StagedInstall(
                    skill_name=skill_name,
                    source_path=path,
                    staged_dir=staged_dir,
                    destination_dir=destination_dir,
                    tree_sha256=tree_sha256,
                    file_count=file_count,
                    bytes_total=bytes_total,
                    validation=validation_result,
                )
                installed.append(staged)
                journal.write(
                    "skill_staged",
                    skill_name=skill_name,
                    source_path=path,
                    staged_dir=staged_dir,
                    tree_sha256=tree_sha256,
                    file_count=file_count,
                    bytes_total=bytes_total,
                    validation=validation_result,
                )

            try:
                for staged in installed:
                    _promote_skill(staged.staged_dir, staged.destination_dir)
                    promoted_dirs.append(staged.destination_dir)
                    journal.write(
                        "skill_promoted",
                        skill_name=staged.skill_name,
                        destination=staged.destination_dir,
                    )
            except Exception as exc:  # noqa: BLE001
                journal.write("rollback_started", reason=str(exc), promoted_count=len(promoted_dirs))
                rollback_errors = _rollback_promoted(promoted_dirs, journal)
                if rollback_errors:
                    raise InstallError(
                        "Promotion failed and rollback encountered errors: " + "; ".join(rollback_errors)
                    ) from exc
                journal.write("rollback_completed", restored_count=len(promoted_dirs))
                raise InstallError(f"Promotion failed and rollback completed: {exc}") from exc

            manifest_path = os.path.join(provenance_dir, f"{run_id}.json")
            manifest_payload: dict[str, object] = {
                "schema_version": "1.1",
                "generated_at": _utc_now_iso(),
                "run_id": run_id,
                "source": {
                    "owner": source.owner,
                    "repo": source.repo,
                    "requested_ref": source.ref,
                    "resolved_commit": prepared.resolved_commit,
                    "method": prepared.source_method,
                },
                "policy": {
                    "ref_pinning_enforced": not args.allow_unpinned_ref,
                    "allow_unpinned_ref": bool(args.allow_unpinned_ref),
                    "trusted_source_enforced": not args.allow_untrusted_source,
                    "allow_untrusted_source": bool(args.allow_untrusted_source),
                    "requested_repo": requested_repo,
                    "trusted_repo_allowlist": sorted(trusted_repos),
                    "quarantine_to_promote": True,
                    "rollback_journal": journal_path,
                    "validation_level": args.validation_level,
                },
                "install": {
                    "destination_root": dest_root,
                    "quarantine_root": quarantine_root,
                    "skills": [
                        {
                            "name": staged.skill_name,
                            "source_path": staged.source_path,
                            "destination_path": staged.destination_dir,
                            "tree_sha256": staged.tree_sha256,
                            "file_count": staged.file_count,
                            "bytes_total": staged.bytes_total,
                            "validation": staged.validation,
                        }
                        for staged in installed
                    ],
                },
            }
            _write_json_atomic(manifest_path, manifest_payload)
            journal.write("provenance_manifest_written", path=manifest_path)

            for staged in installed:
                print(f"Installed {staged.skill_name} to {staged.destination_dir}")
            print(f"Provenance manifest: {manifest_path}")
            print(f"Rollback journal: {journal_path}")
            journal.write("install_completed", installed_count=len(installed), manifest_path=manifest_path)
            return 0
        finally:
            if os.path.isdir(tmp_dir):
                shutil.rmtree(tmp_dir, ignore_errors=True)
            if os.path.isdir(quarantine_root):
                shutil.rmtree(quarantine_root, ignore_errors=True)
    except InstallError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
