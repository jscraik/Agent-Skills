#!/usr/bin/env python3
"""Install a skill from a GitHub repo path into $CODEX_HOME/skills."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import os
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


@dataclass
class Source:
    owner: str
    repo: str
    ref: str
    paths: list[str]
    repo_url: str | None = None


class InstallError(Exception):
    pass


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


def _normalize_repo_id(text: str) -> str:
    parts = [part.strip() for part in text.split("/") if part.strip()]
    if len(parts) != 2:
        raise InstallError(f"Trusted repo must be owner/repo: {text}")
    return f"{parts[0].lower()}/{parts[1].lower()}"


def _normalize_allowlist(values: list[str] | None) -> set[str]:
    if not values:
        return set()
    return {value.strip().lower() for value in values if isinstance(value, str) and value.strip()}


def _normalize_domain_allowlist(values: list[str] | None) -> set[str]:
    if not values:
        return set()
    return {value.strip().lower().lstrip("@") for value in values if isinstance(value, str) and value.strip()}


def _validate_ref_token(ref: str) -> None:
    clean_ref = ref.strip()
    if not clean_ref:
        raise InstallError("Ref cannot be empty.")
    if clean_ref.startswith("-"):
        raise InstallError("Ref must not start with '-'.")


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

    reason_raw = verification.get("reason")
    reason = reason_raw.strip() if isinstance(reason_raw, str) and reason_raw.strip() else "unknown"
    return {
        "verified": verification.get("verified") is True,
        "reason": reason,
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

        for actor_key in ("author", "committer"):
            actor = commit_obj.get(actor_key)
            if isinstance(actor, dict):
                email = actor.get("email")
                if isinstance(email, str) and email.strip():
                    metadata_emails.add(email.strip().lower())

    if isinstance(verification_obj, dict):
        payload = verification_obj.get("payload")
        if isinstance(payload, str) and payload.strip():
            for raw_line in payload.splitlines():
                match = SIGNED_PAYLOAD_IDENTITY_RE.match(raw_line.strip())
                if match:
                    attested_emails.add(match.group(2).strip().lower())

    for actor_key in ("author", "committer"):
        actor = commit_payload.get(actor_key)
        if isinstance(actor, dict):
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
    sha = data.get("sha")
    if not isinstance(sha, str) or not _is_pinned_ref(sha):
        raise InstallError("GitHub API did not return a valid commit SHA for provenance.")
    return sha.lower(), _extract_commit_verification(data), _extract_commit_signer_identity(data)


def _signer_allowed(identity: dict[str, list[str]], args: argparse.Namespace | Args) -> bool:
    emails = _normalize_allowlist(
        list(identity.get("emails", []))
        + list(identity.get("attested_emails", []))
        + list(identity.get("metadata_emails", []))
    )
    logins = _normalize_allowlist(
        list(identity.get("logins", []))
        + list(identity.get("attested_logins", []))
        + list(identity.get("metadata_logins", []))
    )
    allowed_emails = _normalize_allowlist(args.allowed_signer_email)
    allowed_logins = _normalize_allowlist(args.allowed_signer_login)
    allowed_domains = _normalize_domain_allowlist(args.allowed_signer_domain)
    if allowed_emails and emails.isdisjoint(allowed_emails):
        return False
    if allowed_logins and logins.isdisjoint(allowed_logins):
        return False
    if allowed_domains and not any(email.rsplit("@", 1)[-1] in allowed_domains for email in emails if "@" in email):
        return False
    return True


def _enforce_source_provenance(source: Source, args: argparse.Namespace | Args) -> None:
    _validate_ref_token(source.ref)
    repo_key = _normalize_repo_id(f"{source.owner}/{source.repo}")
    trusted_repos = set(DEFAULT_TRUSTED_REPOS)
    trusted_repos.update(_normalize_repo_id(item) for item in (args.trusted_repo or []))

    if repo_key not in trusted_repos and not args.allow_untrusted_source:
        raise InstallError(
            f"Source '{repo_key}' is not in trusted allowlist. "
            "Pass --trusted-repo owner/repo or --allow-untrusted-source with explicit approval."
        )
    if not args.allow_unpinned_ref and not _is_pinned_ref(source.ref):
        raise InstallError(
            "Skill installs require a pinned 40-character commit ref. "
            "Pass --allow-unpinned-ref only with explicit approval."
        )

    resolved_commit, verification, identity = _resolve_commit_provenance(source.owner, source.repo, source.ref)
    verified = verification.get("verified") is True
    reason = str(verification.get("reason") or "unknown").strip().lower()
    if not args.allow_unsigned_provenance:
        if not verified:
            raise InstallError(
                "Commit provenance is not signed/verified. "
                f"GitHub verification reason='{reason}' for {repo_key}@{resolved_commit}."
            )
        if reason != "valid":
            raise InstallError(
                "Commit provenance verification reason must be 'valid' for signed installs. "
                f"Observed reason='{reason}' for {repo_key}@{resolved_commit}."
            )
    if not _signer_allowed(identity, args):
        raise InstallError("Commit signer does not match the allowed signer policy.")
    source.ref = resolved_commit


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
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
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
    _validate_no_symlinks(path)


def _validate_no_symlinks(path: str) -> None:
    for root, dirnames, filenames in os.walk(path, followlinks=False):
        if os.path.islink(root):
            raise InstallError("Skill directory contains symlinks.")
        for name in [*dirnames, *filenames]:
            if os.path.islink(os.path.join(root, name)):
                raise InstallError("Skill directory contains symlinks.")


def _copy_skill(src: str, dest_dir: str) -> None:
    os.makedirs(os.path.dirname(dest_dir), exist_ok=True)
    if os.path.exists(dest_dir):
        raise InstallError(f"Destination already exists: {dest_dir}")
    _validate_no_symlinks(src)
    shutil.copytree(src, dest_dir)


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


def _default_dest() -> str:
    return os.path.join(_codex_home(), "skills")


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
        "--name", help="Destination skill name (defaults to basename of path)"
    )
    parser.add_argument(
        "--method",
        choices=["auto", "download", "git"],
        default="auto",
    )
    parser.add_argument("--trusted-repo", action="append", default=[], help="Extra trusted owner/repo source (repeatable)")
    parser.add_argument("--allow-untrusted-source", action="store_true")
    parser.add_argument("--allow-unpinned-ref", action="store_true")
    parser.add_argument("--allow-unsigned-provenance", action="store_true")
    parser.add_argument("--allowed-signer-email", action="append", default=[])
    parser.add_argument("--allowed-signer-domain", action="append", default=[])
    parser.add_argument("--allowed-signer-login", action="append", default=[])
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
        _enforce_source_provenance(source, args)
        dest_root = args.dest or _default_dest()
        tmp_dir = tempfile.mkdtemp(prefix="skill-install-", dir=_tmp_root())
        try:
            prepared = _prepare_repo(source, args.method, tmp_dir)
            repo_root = prepared[0] if isinstance(prepared, tuple) else prepared
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
                _copy_skill(skill_src, dest_dir)
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
