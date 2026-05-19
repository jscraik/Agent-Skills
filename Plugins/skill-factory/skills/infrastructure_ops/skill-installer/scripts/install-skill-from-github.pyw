#!/usr/bin/env python3
"""Compatibility entrypoint for the system skill installer script."""

from __future__ import annotations

import argparse
import importlib.util
import os
import re
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[6]
_SYSTEM_SCRIPT_DIR = _REPO_ROOT / "skills-system" / "skill-installer" / "scripts"
_SYSTEM_SCRIPT = _SYSTEM_SCRIPT_DIR / "install-skill-from-github.py"

if str(_SYSTEM_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SYSTEM_SCRIPT_DIR))

_SPEC = importlib.util.spec_from_file_location("_system_skill_installer", _SYSTEM_SCRIPT)
if _SPEC is None or _SPEC.loader is None:
    raise ImportError(f"Cannot load system skill installer: {_SYSTEM_SCRIPT}")

_MODULE = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = _MODULE
_SPEC.loader.exec_module(_MODULE)

for _name, _value in vars(_MODULE).items():
    if _name not in {"__name__", "__file__", "__package__", "__loader__", "__spec__", "main"}:
        globals()[_name] = _value

_PINNED_REF = re.compile(r"^[0-9a-f]{40}$")
_TRUSTED_REPOS = {"openai/skills"}


def _canonical_repo_dest() -> str | None:
    return os.environ.get("ASK_SKILLS_CANONICAL_DEST")


def _resolve_dest_root(dest: str | None) -> str:
    canonical = _canonical_repo_dest()
    if canonical is None:
        raise InstallError("Canonical skills destination is not configured.")

    canonical_path = Path(canonical).expanduser().resolve()
    repo_root = canonical_path.parents[1]
    if dest is None:
        return str(canonical_path)

    requested = Path(dest).expanduser()
    if not requested.is_absolute():
        requested = repo_root / requested if requested.parts and requested.parts[0] == "Skills" else repo_root / "Skills" / requested
    requested = requested.resolve()
    try:
        requested.relative_to(repo_root)
    except ValueError as exc:
        raise InstallError("Destination must stay inside the canonical skills repository.") from exc
    if requested == repo_root or "skills" not in {part.lower() for part in requested.parts}:
        raise InstallError("Destination must resolve to a skills category inside the repository.")
    return str(requested)


def _extract_commit_signer_identity(commit_payload: dict[str, object]) -> dict[str, list[str]]:
    commit = commit_payload.get("commit")
    commit_obj = commit if isinstance(commit, dict) else {}
    verification = commit_obj.get("verification")
    verification_obj = verification if isinstance(verification, dict) else {}
    payload = str(verification_obj.get("payload") or "")

    attested_emails = sorted(set(re.findall(r"<([^<>@\s]+@[^<>\s]+)>", payload)))
    metadata_emails = set()
    for key in ("author", "committer"):
        nested = commit_obj.get(key)
        if isinstance(nested, dict) and nested.get("email"):
            metadata_emails.add(str(nested["email"]))

    metadata_logins = set()
    for key in ("author", "committer"):
        nested = commit_payload.get(key)
        if isinstance(nested, dict) and nested.get("login"):
            metadata_logins.add(str(nested["login"]))

    return {
        "attested_emails": attested_emails,
        "attested_logins": [],
        "metadata_emails": sorted(metadata_emails),
        "metadata_logins": sorted(metadata_logins),
        "emails": sorted(set(attested_emails) | metadata_emails),
        "logins": sorted(metadata_logins),
    }


def _resolve_commit_provenance(owner: str, repo: str, ref: str) -> tuple[str, dict[str, object], dict[str, list[str]]]:
    return ref, {"verified": False, "reason": "not checked by compatibility wrapper"}, {
        "attested_emails": [],
        "attested_logins": [],
        "metadata_emails": [],
        "metadata_logins": [],
        "emails": [],
        "logins": [],
    }


def _signer_allowed(identity: dict[str, list[str]], args: argparse.Namespace) -> bool:
    emails = set(identity.get("emails", [])) | set(identity.get("attested_emails", [])) | set(identity.get("metadata_emails", []))
    logins = set(identity.get("logins", [])) | set(identity.get("attested_logins", [])) | set(identity.get("metadata_logins", []))
    allowed_emails = set(args.allowed_signer_email or [])
    allowed_logins = set(args.allowed_signer_login or [])
    allowed_domains = {domain.lower().lstrip("@") for domain in (args.allowed_signer_domain or [])}
    if allowed_emails and emails.isdisjoint(allowed_emails):
        return False
    if allowed_logins and logins.isdisjoint(allowed_logins):
        return False
    if allowed_domains and not any(email.rsplit("@", 1)[-1].lower() in allowed_domains for email in emails if "@" in email):
        return False
    return True


def _parse_compat_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Install a skill from GitHub.")
    parser.add_argument("--repo", required=True)
    parser.add_argument("--path", nargs="+", required=True)
    parser.add_argument("--ref", default=DEFAULT_REF)
    parser.add_argument("--dest")
    parser.add_argument("--name")
    parser.add_argument("--method", choices=["auto", "download", "git"], default="auto")
    parser.add_argument("--allow-untrusted-source", action="store_true")
    parser.add_argument("--trusted-repo", action="append", default=[])
    parser.add_argument("--allowed-signer-email", action="append", default=[])
    parser.add_argument("--allowed-signer-domain", action="append", default=[])
    parser.add_argument("--allowed-signer-login", action="append", default=[])
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = _parse_compat_args(argv)
    try:
        source = _resolve_source(Args(repo=args.repo, path=args.path, ref=args.ref, method=args.method))
        repo_key = f"{source.owner}/{source.repo}"
        trusted_repos = _TRUSTED_REPOS | set(args.trusted_repo or [])
        if repo_key not in trusted_repos and not args.allow_untrusted_source:
            raise InstallError("Untrusted source repo. Pass --trusted-repo owner/repo or --allow-untrusted-source with explicit approval.")
        if not _PINNED_REF.match(source.ref) and not args.allow_untrusted_source:
            raise InstallError("Skill installs require a pinned 40-character commit ref.")
        _, verification, identity = _resolve_commit_provenance(source.owner, source.repo, source.ref)
        if verification.get("verified") is False and not args.allow_untrusted_source:
            raise InstallError("Commit provenance is not verified.")
        if not _signer_allowed(identity, args):
            raise InstallError("Commit signer does not match the allowed signer policy.")
        for path in source.paths:
            _validate_relative_path(path)
        dest_root = _resolve_dest_root(args.dest)
        tmp_dir = tempfile.mkdtemp(prefix="skill-install-", dir=_tmp_root())
        try:
            prepared = _prepare_repo(source, args.method, tmp_dir)
            repo_root = prepared[0] if isinstance(prepared, tuple) else prepared
            installed = []
            for path in source.paths:
                skill_name = args.name if len(source.paths) == 1 else None
                skill_name = skill_name or os.path.basename(path.rstrip("/"))
                _validate_skill_name(skill_name)
                dest_dir = os.path.join(dest_root, skill_name)
                skill_src = os.path.join(repo_root, path)
                _validate_skill(skill_src)
                _copy_skill(skill_src, dest_dir)
                installed.append((skill_name, dest_dir))
        finally:
            import shutil

            shutil.rmtree(tmp_dir, ignore_errors=True)
        for skill_name, dest_dir in installed:
            print(f"Installed {skill_name} to {dest_dir}")
        return 0
    except InstallError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
