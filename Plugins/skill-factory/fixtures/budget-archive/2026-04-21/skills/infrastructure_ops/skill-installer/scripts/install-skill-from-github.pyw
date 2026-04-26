#!/usr/bin/env python3
"""Install one or more skills from GitHub into canonical repository categories.

Security defaults:
- trusted source allowlist enforced by default
- pinned refs required by default (40-char commit SHA)
- commit provenance must be signed/verified by default
- staged quarantine copy + promotion into destination
- rollback/provenance artifacts emitted per run
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import datetime as dt
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
import uuid
import zipfile

from github_utils import github_request


DEFAULT_REF = "main"
PINNED_REF_RE = re.compile(r"^[0-9a-fA-F]{40}$")
VERIFICATION_TIME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
SIGNED_PAYLOAD_IDENTITY_RE = re.compile(r"^(author|committer)\s+.+<([^>]+)>\s+\d+\s+[+-]\d{4}$")
DEFAULT_TRUSTED_REPOS = {
    "openai/skills",
    "jscraik/agent-skills",
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
    allow_untrusted_source: bool = False
    trusted_repo: list[str] | None = None
    allow_unpinned_ref: bool = False
    allow_unsigned_provenance: bool = False
    allowed_signer_email: list[str] | None = None
    allowed_signer_domain: list[str] | None = None
    allowed_signer_login: list[str] | None = None
    validation_level: str = "compat"
    remediate: bool = False


@dataclass
class Source:
    owner: str
    repo: str
    ref: str
    paths: list[str]
    repo_url: str | None = None


class InstallError(Exception):
    """Raised when skill installation input or staged validation fails."""


def _utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _tmp_root() -> str:
    base = os.path.join(tempfile.gettempdir(), "codex")
    os.makedirs(base, exist_ok=True)
    return base


def _request(url: str) -> bytes:
    return github_request(url, "codex-skill-install")


def _is_pinned_ref(ref: str) -> bool:
    return bool(PINNED_REF_RE.fullmatch(ref.strip()))


def _normalize_repo_id(text: str) -> str:
    parts = [p.strip() for p in text.split("/") if p.strip()]
    if len(parts) != 2:
        raise InstallError(f"Trusted repo must be owner/repo: {text}")
    return f"{parts[0].lower()}/{parts[1].lower()}"


def _validate_ref_token(ref: str) -> None:
    clean_ref = ref.strip()
    if not clean_ref:
        raise InstallError("Ref cannot be empty.")
    if clean_ref.startswith("-"):
        raise InstallError("Ref must not start with '-'.")


def _parse_github_url(url: str, default_ref: str) -> tuple[str, str, str, str | None]:
    parsed = urllib.parse.urlparse(url)
    if parsed.netloc != "github.com":
        raise InstallError("Only GitHub URLs are supported for download mode.")
    parts = [p for p in parsed.path.split("/") if p]
    if len(parts) < 2:
        raise InstallError("Invalid GitHub URL.")

    owner, repo = parts[0], parts[1]
    if repo.endswith(".git"):
        repo = repo[:-4]
        if not repo:
            raise InstallError("Invalid GitHub URL repo segment.")

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


def _resolve_commit_payload(owner: str, repo: str, ref: str) -> dict[str, object]:
    encoded_ref = urllib.parse.quote(ref, safe="")
    api_url = f"https://api.github.com/repos/{owner}/{repo}/commits/{encoded_ref}"
    try:
        payload = _request(api_url)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            raise InstallError(f"Ref not found for provenance resolution: {owner}/{repo}@{ref}") from exc
        raise InstallError(f"Provenance resolution failed: HTTP {exc.code}") from exc
    except urllib.error.URLError as exc:
        raise InstallError(f"Provenance resolution failed: {exc.reason}") from exc

    try:
        data = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise InstallError("Could not parse commit provenance response from GitHub API.") from exc

    if not isinstance(data, dict):
        raise InstallError("Could not parse commit provenance response from GitHub API.")
    return data


def _extract_commit_verification(commit_payload: dict[str, object]) -> dict[str, object]:
    verification: dict[str, object] = {}
    commit_obj = commit_payload.get("commit")
    if isinstance(commit_obj, dict):
        raw = commit_obj.get("verification")
        if isinstance(raw, dict):
            verification = raw
    if not verification:
        raw = commit_payload.get("verification")
        if isinstance(raw, dict):
            verification = raw

    verified = bool(verification.get("verified") is True)
    reason_raw = verification.get("reason")
    reason = reason_raw.strip() if isinstance(reason_raw, str) and reason_raw.strip() else "unknown"
    verified_at_raw = verification.get("verified_at")
    verified_at = (
        verified_at_raw.strip()
        if isinstance(verified_at_raw, str) and VERIFICATION_TIME_RE.fullmatch(verified_at_raw.strip())
        else None
    )
    return {
        "verified": verified,
        "reason": reason,
        "verified_at": verified_at,
        "signature_present": isinstance(verification.get("signature"), str) and bool(verification.get("signature", "").strip()),
        "payload_present": isinstance(verification.get("payload"), str) and bool(verification.get("payload", "").strip()),
    }


def _extract_commit_signer_identity(commit_payload: dict[str, object]) -> dict[str, list[str]]:
    attested_emails: set[str] = set()
    metadata_emails: set[str] = set()
    metadata_logins: set[str] = set()

    commit_obj = commit_payload.get("commit")
    verification_obj = commit_payload.get("verification")
    if isinstance(commit_obj, dict):
        nested_verification = commit_obj.get("verification")
        if isinstance(nested_verification, dict):
            verification_obj = nested_verification

    if isinstance(verification_obj, dict):
        payload = verification_obj.get("payload")
        if isinstance(payload, str) and payload.strip():
            for raw_line in payload.splitlines():
                line = raw_line.strip()
                match = SIGNED_PAYLOAD_IDENTITY_RE.match(line)
                if not match:
                    continue
                email = match.group(2).strip().lower()
                if email:
                    attested_emails.add(email)

    if isinstance(commit_obj, dict):
        for actor_key in ("author", "committer"):
            actor = commit_obj.get(actor_key)
            if not isinstance(actor, dict):
                continue
            email = actor.get("email")
            if isinstance(email, str) and email.strip():
                metadata_emails.add(email.strip().lower())

    for actor_key in ("author", "committer"):
        actor = commit_payload.get(actor_key)
        if not isinstance(actor, dict):
            continue
        login = actor.get("login")
        if isinstance(login, str) and login.strip():
            metadata_logins.add(login.strip().lower())
        email = actor.get("email")
        if isinstance(email, str) and email.strip():
            metadata_emails.add(email.strip().lower())

    return {
        "emails": sorted(attested_emails),
        "logins": sorted(metadata_logins),
        "attested_emails": sorted(attested_emails),
        "attested_logins": [],
        "metadata_emails": sorted(metadata_emails),
        "metadata_logins": sorted(metadata_logins),
    }


def _resolve_commit_provenance(owner: str, repo: str, ref: str) -> tuple[str, dict[str, object], dict[str, list[str]]]:
    data = _resolve_commit_payload(owner, repo, ref)
    sha = data.get("sha") if isinstance(data, dict) else None
    if not isinstance(sha, str) or not _is_pinned_ref(sha):
        raise InstallError("GitHub API did not return a valid commit SHA for provenance.")
    verification = _extract_commit_verification(data)
    signer_identity = _extract_commit_signer_identity(data)
    return sha.lower(), verification, signer_identity


def _normalize_allowlist(values: list[str] | None) -> set[str]:
    if not values:
        return set()
    return {value.strip().lower() for value in values if isinstance(value, str) and value.strip()}


def _normalize_domain_allowlist(values: list[str] | None) -> set[str]:
    if not values:
        return set()
    normalized: set[str] = set()
    for value in values:
        if not isinstance(value, str):
            continue
        candidate = value.strip().lower().lstrip("@")
        if candidate:
            normalized.add(candidate)
    return normalized


def _enforce_signer_allowlist(
    *,
    owner: str,
    repo: str,
    resolved_commit: str,
    commit_verification: dict[str, object],
    signer_identity: dict[str, list[str]],
    allow_unsigned_provenance: bool,
    allowed_signer_emails: set[str],
    allowed_signer_domains: set[str],
    allowed_signer_logins: set[str],
) -> None:
    allowlist_enabled = bool(allowed_signer_emails or allowed_signer_domains or allowed_signer_logins)
    if not allowlist_enabled:
        return

    verified = bool(commit_verification.get("verified") is True)
    reason = str(commit_verification.get("reason") or "unknown").strip().lower()
    if not verified and allow_unsigned_provenance:
        raise InstallError(
            "Signer allowlist checks require a signed/verified commit. "
            f"Observed verification reason='{reason}' for {owner}/{repo}@{resolved_commit}."
        )
    if reason != "valid":
        raise InstallError(
            "Signer allowlist checks require GitHub verification reason='valid'. "
            f"Observed reason='{reason}' for {owner}/{repo}@{resolved_commit}."
        )

    attested_emails = {
        email.strip().lower()
        for email in signer_identity.get("attested_emails", signer_identity.get("emails", []))
        if isinstance(email, str) and email.strip()
    }
    metadata_emails = {
        email.strip().lower()
        for email in signer_identity.get("metadata_emails", [])
        if isinstance(email, str) and email.strip()
    }
    attested_logins = {
        login.strip().lower()
        for login in signer_identity.get("attested_logins", [])
        if isinstance(login, str) and login.strip()
    }
    metadata_logins = {
        login.strip().lower()
        for login in signer_identity.get("metadata_logins", signer_identity.get("logins", []))
        if isinstance(login, str) and login.strip()
    }

    signer_emails = attested_emails
    signer_logins = attested_logins if attested_logins else metadata_logins
    login_identity_source = "attested" if attested_logins else ("metadata" if metadata_logins else "none")
    signer_domains = {email.rsplit("@", 1)[1] for email in signer_emails if "@" in email}

    matched_email = (not allowed_signer_emails) or bool(signer_emails & allowed_signer_emails)
    matched_domain = (not allowed_signer_domains) or bool(signer_domains & allowed_signer_domains)
    matched_login = (not allowed_signer_logins) or bool(signer_logins & allowed_signer_logins)
    if not (matched_email and matched_domain and matched_login):
        raise InstallError(
            "Commit signer identity did not match allowlist policy. "
            f"allowed_emails={sorted(allowed_signer_emails)} "
            f"allowed_domains={sorted(allowed_signer_domains)} "
            f"allowed_logins={sorted(allowed_signer_logins)} "
            f"observed_attested_emails={sorted(signer_emails)} "
            f"observed_domains={sorted(signer_domains)} "
            f"observed_signer_logins={sorted(signer_logins)} "
            f"observed_signer_login_source={login_identity_source} "
            f"metadata_emails={sorted(metadata_emails)} "
            f"metadata_logins={sorted(metadata_logins)}."
        )


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
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise InstallError(result.stderr.strip() or "Git command failed.")


def _safe_extract_zip(zip_file: zipfile.ZipFile, dest_dir: str) -> None:
    dest_root = os.path.realpath(dest_dir)
    for info in zip_file.infolist():
        extracted_path = os.path.realpath(os.path.join(dest_dir, info.filename))
        if extracted_path != dest_root and not extracted_path.startswith(dest_root + os.sep):
            raise InstallError("Archive contains files outside the destination.")
    zip_file.extractall(dest_dir)


def _validate_relative_path(path: str) -> None:
    normalized = os.path.normpath(path)
    if os.path.isabs(path) or normalized.startswith(".."):
        raise InstallError("Skill path must be a relative path inside the repo.")
    if normalized in ("", "."):
        raise InstallError("Skill path must resolve to a concrete subdirectory.")


def _validate_skill_name(name: str) -> None:
    altsep = os.path.altsep
    if not name or os.path.sep in name or (altsep and altsep in name):
        raise InstallError("Skill name must be a single path segment.")
    if name in (".", ".."):
        raise InstallError("Invalid skill name.")


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


def _assert_tree_has_no_symlinks(path: str) -> None:
    if os.path.islink(path):
        raise InstallError(f"Skill root must not be a symlink: {path}")

    for root, dirs, files in os.walk(path, followlinks=False):
        for directory in dirs:
            full = os.path.join(root, directory)
            if os.path.islink(full):
                raise InstallError(f"Symlinks are not allowed in imported skills: {full}")
        for filename in files:
            full = os.path.join(root, filename)
            if os.path.islink(full):
                raise InstallError(f"Symlinks are not allowed in imported skills: {full}")


def _validate_skill(path: str) -> None:
    if not os.path.isdir(path):
        raise InstallError(f"Skill path not found: {path}")
    skill_md = os.path.join(path, "SKILL.md")
    if not os.path.isfile(skill_md):
        raise InstallError("SKILL.md not found in selected skill directory.")
    _assert_tree_has_no_symlinks(path)


def _build_repo_url(owner: str, repo: str) -> str:
    return f"https://github.com/{owner}/{repo}.git"


def _build_repo_ssh(owner: str, repo: str) -> str:
    return f"git@github.com:{owner}/{repo}.git"


def _prepare_repo(source: Source, method: str, tmp_dir: str) -> tuple[str, str]:
    if method in ("download", "auto"):
        try:
            return _download_repo_zip(source.owner, source.repo, source.ref, tmp_dir), "zipball"
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
            return _git_sparse_checkout(repo_url, source.ref, source.paths, tmp_dir), "git_sparse"
        except InstallError:
            repo_url = _build_repo_ssh(source.owner, source.repo)
            return _git_sparse_checkout(repo_url, source.ref, source.paths, tmp_dir), "git_sparse_ssh"
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
    paths = list(args.path)
    return Source(owner=repo_parts[0], repo=repo_parts[1], ref=args.ref, paths=paths)


def _canonical_repo_dest() -> str | None:
    override = os.environ.get("ASK_SKILLS_CANONICAL_DEST", "").strip()
    if override:
        return override

    script_path = Path(__file__).resolve()
    for parent in [script_path.parent, *script_path.parents]:
        if _is_canonical_repo_root(parent):
            return str(parent / "Skills" / "github")
    return None


def _is_canonical_repo_root(path: Path) -> bool:
    return (
        (path / ".git").exists()
        and (path / "AGENTS.md").is_file()
        and (path / "Infrastructure" / "scripts" / "lifecycle-and-sync" / "sync_skills.sh").is_file()
        and ((path / "plugins").is_dir() or (path / "Plugins").is_dir())
    )


def _resolve_dest_root(dest: str | None) -> str:
    requested_token = (dest or "").strip()
    requested = Path(requested_token) if requested_token else None

    repo_root: Path

    if requested and requested.is_absolute():
        resolved = requested.resolve()
        resolved_repo_root = next((candidate for candidate in [resolved, *resolved.parents] if _is_canonical_repo_root(candidate)), None)
        if resolved_repo_root is None:
            raise InstallError(
                "Absolute --dest must point under a canonical agent-skills repository root "
                f"(missing markers for '{resolved}')."
            )
        repo_root = resolved_repo_root
    else:
        canonical = _canonical_repo_dest()
        if not canonical:
            raise InstallError(
                "Canonical skill destination was not detected. "
                "Set ASK_SKILLS_CANONICAL_DEST or run inside the canonical agent-skills repository."
            )

        canonical_dest = Path(canonical).resolve()
        repo_root = canonical_dest.parents[1]
        if not requested:
            return str(canonical_dest)
        if len(requested.parts) == 1:
            requested = Path("Skills") / requested
        resolved = (repo_root / requested).resolve()

    try:
        rel = resolved.relative_to(repo_root)
    except ValueError as exc:
        raise InstallError(f"Destination must stay inside canonical repository root: {repo_root}") from exc

    if resolved.exists() and not resolved.is_dir():
        raise InstallError(
            f"Destination must be a directory under the canonical repo root, but '{resolved}' exists and is not a directory."
        )

    rel_parts = rel.parts
    if len(rel_parts) != 2 or rel_parts[0] != "Skills":
        raise InstallError("Destination must target Skills/<category> inside the canonical repository root.")
    return str(resolved)


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    fd = os.open(tmp_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(rendered)
    tmp_path.replace(path)
    os.chmod(path, 0o600)


def _redact_manifest_payload_for_storage(payload: dict[str, object]) -> dict[str, object]:
    sanitized = json.loads(json.dumps(payload))
    security_policy = sanitized.get("security_policy")
    if isinstance(security_policy, dict):
        signer_allowlist = security_policy.get("signer_allowlist")
        if isinstance(signer_allowlist, dict):
            signer_allowlist["emails"] = ["[redacted]"] if signer_allowlist.get("emails") else []
            signer_allowlist["domains"] = ["[redacted]"] if signer_allowlist.get("domains") else []
            signer_allowlist["logins"] = ["[redacted]"] if signer_allowlist.get("logins") else []
        if "trusted_repos" in security_policy:
            security_policy["trusted_repos"] = ["[redacted]"]
    return sanitized


def _append_journal(path: Path, event: str, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "ts": _utc_now_iso(),
        "event": event,
        "payload": payload,
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True) + "\n")


def _parse_args(argv: list[str]) -> Args:
    parser = argparse.ArgumentParser(description="Install a skill from GitHub.")
    parser.add_argument("--repo", help="owner/repo")
    parser.add_argument("--url", help="https://github.com/owner/repo[/tree/ref/path]")
    parser.add_argument("--path", nargs="+", help="Path(s) to skill(s) inside repo")
    parser.add_argument("--ref", default=DEFAULT_REF)
    parser.add_argument(
        "--dest",
        help="Canonical destination under Skills/<category> (repo-relative, shorthand category, or absolute inside canonical repo)",
    )
    parser.add_argument("--name", help="Destination skill name (defaults to basename of path)")
    parser.add_argument("--method", choices=["auto", "download", "git"], default="auto")
    parser.add_argument("--trusted-repo", action="append", default=[], help="Extra trusted owner/repo source (repeatable)")
    parser.add_argument(
        "--allow-untrusted-source",
        action="store_true",
        help="Allow installation from sources outside trusted allowlist",
    )
    parser.add_argument(
        "--allow-unpinned-ref",
        action="store_true",
        help="Allow non-SHA refs (branches/tags). Default requires pinned commit SHA.",
    )
    parser.add_argument(
        "--allow-unsigned-provenance",
        action="store_true",
        help="Allow install when GitHub commit verification is not signed/valid.",
    )
    parser.add_argument("--allowed-signer-email", action="append", default=[], help="Allowed signer email (repeatable)")
    parser.add_argument("--allowed-signer-domain", action="append", default=[], help="Allowed signer email domain (repeatable)")
    parser.add_argument("--allowed-signer-login", action="append", default=[], help="Allowed signer GitHub login (repeatable)")
    parser.add_argument(
        "--validation-level",
        choices=["compat", "strict"],
        default="compat",
        help="Accepted for ask CLI compatibility; install always validates SKILL.md presence.",
    )
    parser.add_argument(
        "--remediate",
        action="store_true",
        help="Accepted for ask CLI compatibility; no auto-remediation is performed by this installer.",
    )
    return parser.parse_args(argv, namespace=Args())


def main(argv: list[str]) -> int:
    args = _parse_args(argv)
    run_id = uuid.uuid4().hex

    try:
        source = _resolve_source(args)
        source.ref = source.ref or args.ref

        if not source.paths:
            raise InstallError("No skill paths provided.")
        for path in source.paths:
            _validate_relative_path(path)

        _validate_ref_token(source.ref)
        if not args.allow_unpinned_ref and not _is_pinned_ref(source.ref):
            raise InstallError(
                "Pinned commit SHA is required by default. "
                f"Received ref '{source.ref}'. Pass --allow-unpinned-ref only with explicit approval."
            )

        repo_id = _normalize_repo_id(f"{source.owner}/{source.repo}")
        trusted_repos = set(DEFAULT_TRUSTED_REPOS)
        trusted_repos.update(_normalize_repo_id(item) for item in (args.trusted_repo or []))
        if not args.allow_untrusted_source and repo_id not in trusted_repos:
            raise InstallError(
                f"Source '{repo_id}' is not in trusted allowlist. "
                "Pass --trusted-repo owner/repo or --allow-untrusted-source with explicit approval."
            )

        resolved_commit, commit_verification, signer_identity = _resolve_commit_provenance(source.owner, source.repo, source.ref)
        verified = bool(commit_verification.get("verified") is True)
        reason = str(commit_verification.get("reason") or "unknown").strip().lower()
        allowed_signer_emails = _normalize_allowlist(args.allowed_signer_email)
        allowed_signer_domains = _normalize_domain_allowlist(args.allowed_signer_domain)
        allowed_signer_logins = _normalize_allowlist(args.allowed_signer_login)
        if not args.allow_unsigned_provenance:
            if not verified:
                raise InstallError(
                    "Commit provenance is not signed/verified. "
                    f"GitHub verification reason='{reason}' for {repo_id}@{resolved_commit}. "
                    "Pass --allow-unsigned-provenance only with explicit approval."
                )
            if reason != "valid":
                raise InstallError(
                    "Commit provenance verification reason must be 'valid' for signed installs. "
                    f"Observed reason='{reason}' for {repo_id}@{resolved_commit}."
                )
        _enforce_signer_allowlist(
            owner=source.owner,
            repo=source.repo,
            resolved_commit=resolved_commit,
            commit_verification=commit_verification,
            signer_identity=signer_identity,
            allow_unsigned_provenance=args.allow_unsigned_provenance,
            allowed_signer_emails=allowed_signer_emails,
            allowed_signer_domains=allowed_signer_domains,
            allowed_signer_logins=allowed_signer_logins,
        )

        source.ref = resolved_commit
        dest_root = _resolve_dest_root(args.dest)
        os.makedirs(dest_root, exist_ok=True)

        artifacts_root = Path(dest_root) / ".install-artifacts"
        journal_path = artifacts_root / "journals" / f"skill-install-{run_id}.jsonl"
        manifest_path = artifacts_root / "provenance" / f"skill-install-{run_id}.json"
        quarantine_run_root = artifacts_root / "quarantine" / run_id

        _append_journal(
            journal_path,
            "run_started",
            {
                "repo": repo_id,
                "requested_ref": args.ref,
                "resolved_commit": resolved_commit,
                "paths": source.paths,
                "dest_root": dest_root,
                "trusted_repo_enforced": not args.allow_untrusted_source,
                "pinned_ref_enforced": not args.allow_unpinned_ref,
                "signed_provenance_enforced": not args.allow_unsigned_provenance,
                "signer_allowlist": {
                    "emails": sorted(allowed_signer_emails),
                    "domains": sorted(allowed_signer_domains),
                    "logins": sorted(allowed_signer_logins),
                },
            },
        )

        tmp_dir = tempfile.mkdtemp(prefix="skill-install-", dir=_tmp_root())
        installed: list[tuple[str, str]] = []
        fetch_method = ""

        try:
            prepared_repo = _prepare_repo(source, args.method, tmp_dir)
            if isinstance(prepared_repo, tuple):
                repo_root, fetch_method = prepared_repo
            elif isinstance(prepared_repo, str):
                # Backward compatibility with callers/tests that still return
                # _prepare_repo() as a plain repo-root string.
                repo_root = prepared_repo
                fetch_method = "unknown"
            else:
                raise InstallError("Installer internal error: _prepare_repo returned unsupported result type.")
            _append_journal(journal_path, "repo_fetched", {"method": fetch_method, "tmp_dir": tmp_dir})

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

                stage_dir = quarantine_run_root / skill_name
                if stage_dir.exists():
                    shutil.rmtree(stage_dir)
                stage_dir.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(skill_src, stage_dir)
                _append_journal(
                    journal_path,
                    "staged",
                    {"skill_name": skill_name, "source": skill_src, "stage_dir": str(stage_dir)},
                )

                os.makedirs(os.path.dirname(dest_dir), exist_ok=True)
                try:
                    os.replace(str(stage_dir), dest_dir)
                except OSError:
                    shutil.move(str(stage_dir), dest_dir)

                _append_journal(
                    journal_path,
                    "promoted",
                    {"skill_name": skill_name, "dest_dir": dest_dir},
                )
                installed.append((skill_name, dest_dir))
        except Exception:
            _append_journal(journal_path, "run_failed", {"tmp_dir": tmp_dir})
            raise
        finally:
            if os.path.isdir(tmp_dir):
                shutil.rmtree(tmp_dir, ignore_errors=True)
            if quarantine_run_root.exists():
                shutil.rmtree(quarantine_run_root, ignore_errors=True)

        manifest_payload = {
            "run_id": run_id,
            "timestamp": _utc_now_iso(),
            "source": {
                "owner": source.owner,
                "repo": source.repo,
                "requested_ref": args.ref,
                "resolved_commit": resolved_commit,
                "paths": source.paths,
                "fetch_method": fetch_method,
            },
            "provenance": commit_verification,
            "security_policy": {
                "trusted_repo_enforced": not args.allow_untrusted_source,
                "trusted_repos": sorted(trusted_repos),
                "pinned_ref_enforced": not args.allow_unpinned_ref,
                "signed_provenance_enforced": not args.allow_unsigned_provenance,
                "signer_allowlist": {
                    "emails": sorted(allowed_signer_emails),
                    "domains": sorted(allowed_signer_domains),
                    "logins": sorted(allowed_signer_logins),
                },
            },
            "install": {
                "dest_root": dest_root,
                "skills": [
                    {
                        "name": skill_name,
                        "dest_dir": dest_dir,
                    }
                    for skill_name, dest_dir in installed
                ],
            },
        }
        _write_json(manifest_path, _redact_manifest_payload_for_storage(manifest_payload))
        _append_journal(
            journal_path,
            "run_completed",
            {
                "installed_count": len(installed),
                "manifest_path": str(manifest_path),
            },
        )

        for skill_name, dest_dir in installed:
            print(f"Installed {skill_name} to {dest_dir}")
        print(f"Provenance manifest: {manifest_path}")
        print(f"Rollback journal: {journal_path}")
        return 0
    except InstallError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
