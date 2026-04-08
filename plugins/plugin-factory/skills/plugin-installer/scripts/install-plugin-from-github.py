#!/usr/bin/env python3
"""Install one plugin from GitHub into $CODEX_HOME/plugins with staged validation.

Installer guarantees:
- pinned refs required by default (40-char commit SHA unless override)
- source trust allowlist enforced by default
- plugin staged in quarantine before promotion
- strict mode runs plugin-builder validation before activation
- Python helper execution requires uv in PATH
- rollback journal and provenance manifest persisted for each run
"""

from __future__ import annotations

import argparse
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
PLUGIN_NAME_RE = re.compile(r"^[a-z0-9](?:-?[a-z0-9]){0,63}$")
VERIFICATION_TIME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
UV_INSTALL_HINT = "Install uv from https://docs.astral.sh/uv/getting-started/installation/."
SEMVER_RE = re.compile(
    r"^v?(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)
DEFAULT_TRUSTED_REPOS = {
    "openai/plugins",
    "jscraik/Agent-Skills",
}


class InstallError(Exception):
    pass


def _utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _request(url: str) -> bytes:
    return github_request(url, "codex-plugin-install")


def _is_pinned_ref(ref: str) -> bool:
    return bool(PINNED_REF_RE.fullmatch(ref.strip()))


def _codex_home() -> str:
    return os.environ.get("CODEX_HOME", os.path.expanduser("~/.codex"))


def _tmp_root() -> str:
    base = os.path.join(tempfile.gettempdir(), "codex")
    os.makedirs(base, exist_ok=True)
    return base


def _normalize_repo_id(text: str) -> str:
    parts = [p.strip() for p in text.split("/") if p.strip()]
    if len(parts) != 2:
        raise InstallError(f"Trusted repo must be owner/repo: {text}")
    return f"{parts[0].lower()}/{parts[1].lower()}"


def _parse_github_url(url: str, default_ref: str) -> tuple[str, str, str, str | None]:
    parsed = urllib.parse.urlparse(url)
    if parsed.netloc != "github.com":
        raise InstallError("Only GitHub URLs are supported.")

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
                raise InstallError("GitHub URL missing ref segment.")
            ref = parts[3]
            subpath = "/".join(parts[4:])
        else:
            subpath = "/".join(parts[2:])

    return owner, repo, ref, (subpath or None)


def _validate_relative_path(path: str) -> None:
    normalized = os.path.normpath(path)
    if os.path.isabs(path) or normalized.startswith(".."):
        raise InstallError("Plugin path must be relative and inside the fetched repo.")
    if normalized in ("", "."):
        raise InstallError("Plugin path must resolve to a concrete subdirectory.")
    if normalized.startswith("-"):
        raise InstallError("Plugin path must not start with '-'.")
    normalized_posix = path.replace("\\", "/")
    components = [part for part in normalized_posix.split("/") if part not in ("", ".")]
    if any(part == ".." for part in components):
        raise InstallError("Plugin path must not contain '..' segments.")


def _validate_ref_token(ref: str) -> None:
    clean_ref = ref.strip()
    if not clean_ref:
        raise InstallError("Ref cannot be empty.")
    if clean_ref.startswith("-"):
        raise InstallError("Ref must not start with '-'.")


def _resolve_commit_sha(owner: str, repo: str, ref: str) -> str:
    resolved_commit, _, _ = _resolve_commit_provenance(owner, repo, ref)
    return resolved_commit


def _resolve_commit_payload(owner: str, repo: str, ref: str) -> dict[str, object]:
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
    signature_value = verification.get("signature")
    signature_present = isinstance(signature_value, str) and bool(signature_value.strip())
    payload_value = verification.get("payload")
    payload_present = isinstance(payload_value, str) and bool(payload_value.strip())
    return {
        "verified": verified,
        "reason": reason,
        "verified_at": verified_at,
        "signature_present": signature_present,
        "payload_present": payload_present,
    }


def _extract_commit_signer_identity(commit_payload: dict[str, object]) -> dict[str, list[str]]:
    emails: set[str] = set()
    logins: set[str] = set()

    commit_obj = commit_payload.get("commit")
    if isinstance(commit_obj, dict):
        for actor_key in ("author", "committer"):
            actor = commit_obj.get(actor_key)
            if not isinstance(actor, dict):
                continue
            email = actor.get("email")
            if isinstance(email, str) and email.strip():
                emails.add(email.strip().lower())

    for actor_key in ("author", "committer"):
        actor = commit_payload.get(actor_key)
        if not isinstance(actor, dict):
            continue
        login = actor.get("login")
        if isinstance(login, str) and login.strip():
            logins.add(login.strip().lower())
        email = actor.get("email")
        if isinstance(email, str) and email.strip():
            emails.add(email.strip().lower())

    return {
        "emails": sorted(emails),
        "logins": sorted(logins),
    }


def _resolve_commit_provenance(
    owner: str,
    repo: str,
    ref: str,
) -> tuple[str, dict[str, object], dict[str, list[str]]]:
    data = _resolve_commit_payload(owner, repo, ref)
    sha = data.get("sha") if isinstance(data, dict) else None
    if not isinstance(sha, str) or not _is_pinned_ref(sha):
        raise InstallError("GitHub API did not return a valid commit SHA for provenance.")
    verification = _extract_commit_verification(data)
    signer_identity = _extract_commit_signer_identity(data)
    return sha.lower(), verification, signer_identity


def _normalize_allowlist(values: list[str]) -> set[str]:
    return {value.strip().lower() for value in values if isinstance(value, str) and value.strip()}


def _normalize_domain_allowlist(values: list[str]) -> set[str]:
    normalized: set[str] = set()
    for value in values:
        if not isinstance(value, str):
            continue
        candidate = value.strip().lower().lstrip("@")
        if candidate:
            normalized.add(candidate)
    return normalized


def _enforce_signed_commit_provenance(
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
    journal_path: str | None = None,
) -> None:
    verified = bool(commit_verification.get("verified") is True)
    reason = str(commit_verification.get("reason") or "unknown").strip().lower() or "unknown"
    if not verified and not allow_unsigned_provenance:
        raise InstallError(
            "Commit provenance is not signed/verified. "
            f"GitHub verification reason='{reason}' for {owner}/{repo}@{resolved_commit}. "
            "Pass --allow-unsigned-provenance only with explicit approval."
        )

    if verified and reason != "valid" and not allow_unsigned_provenance:
        raise InstallError(
            "Commit provenance verification reason must be 'valid' for signed installs. "
            f"Observed reason='{reason}' for {owner}/{repo}@{resolved_commit}."
        )

    signer_emails = {
        email.strip().lower()
        for email in signer_identity.get("emails", [])
        if isinstance(email, str) and email.strip()
    }
    signer_logins = {
        login.strip().lower()
        for login in signer_identity.get("logins", [])
        if isinstance(login, str) and login.strip()
    }
    signer_domains = {
        email.rsplit("@", 1)[1]
        for email in signer_emails
        if "@" in email and email.rsplit("@", 1)[1]
    }

    allowlist_enabled = bool(allowed_signer_emails or allowed_signer_domains or allowed_signer_logins)
    if allowlist_enabled:
        if not verified and allow_unsigned_provenance:
            raise InstallError(
                "Signer allowlist checks require a signed/verified commit. "
                f"Observed verification reason='{reason}' for {owner}/{repo}@{resolved_commit}."
            )

        matched_email = bool(signer_emails & allowed_signer_emails)
        matched_domain = bool(signer_domains & allowed_signer_domains)
        matched_login = bool(signer_logins & allowed_signer_logins)
        if not (matched_email or matched_domain or matched_login):
            raise InstallError(
                "Commit signer identity did not match allowlist policy. "
                f"allowed_emails={sorted(allowed_signer_emails)} "
                f"allowed_domains={sorted(allowed_signer_domains)} "
                f"allowed_logins={sorted(allowed_signer_logins)} "
                f"observed_emails={sorted(signer_emails)} "
                f"observed_domains={sorted(signer_domains)} "
                f"observed_logins={sorted(signer_logins)}."
            )

    if journal_path:
        _write_journal_row(
            journal_path,
            "provenance_signature_checked",
            {
                "owner": owner,
                "repo": repo,
                "resolved_commit": resolved_commit,
                "verified": verified,
                "reason": reason,
                "allow_unsigned_provenance": allow_unsigned_provenance,
                "allowlist_enabled": allowlist_enabled,
                "allowed_signer_emails": sorted(allowed_signer_emails),
                "allowed_signer_domains": sorted(allowed_signer_domains),
                "allowed_signer_logins": sorted(allowed_signer_logins),
                "observed_signer_emails": sorted(signer_emails),
                "observed_signer_domains": sorted(signer_domains),
                "observed_signer_logins": sorted(signer_logins),
            },
        )


def _safe_extract_zip(zip_file: zipfile.ZipFile, dest_dir: str) -> None:
    dest_root = os.path.realpath(dest_dir)
    for info in zip_file.infolist():
        extracted_path = os.path.realpath(os.path.join(dest_dir, info.filename))
        if extracted_path == dest_root or extracted_path.startswith(dest_root + os.sep):
            continue
        raise InstallError("Archive contains files outside the destination.")
    zip_file.extractall(dest_dir)


def _download_repo_zip(owner: str, repo: str, ref: str, dest_dir: str) -> str:
    zip_url = f"https://codeload.github.com/{owner}/{repo}/zip/{ref}"
    zip_path = os.path.join(dest_dir, "repo.zip")
    try:
        payload = _request(zip_url)
    except urllib.error.HTTPError as exc:
        raise InstallError(f"Download failed: HTTP {exc.code}") from exc

    with open(zip_path, "wb") as handle:
        handle.write(payload)

    with zipfile.ZipFile(zip_path, "r") as zip_file:
        _safe_extract_zip(zip_file, dest_dir)
        top_levels = {name.split("/")[0] for name in zip_file.namelist() if name}

    if len(top_levels) != 1:
        raise InstallError("Unexpected archive layout.")
    return os.path.join(dest_dir, next(iter(top_levels)))


def _run_checked_command(command: list[str], *, cwd: str | None = None, context: str) -> None:
    proc = subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode == 0:
        return
    stderr = (proc.stderr or "").strip()
    stdout = (proc.stdout or "").strip()
    details = stderr if stderr else stdout
    suffix = f": {details[-400:]}" if details else ""
    raise InstallError(f"{context} (exit {proc.returncode}){suffix}")


def _download_repo_git_sparse(owner: str, repo: str, ref: str, dest_dir: str, plugin_subpath: str) -> str:
    git_bin = shutil.which("git")
    if not git_bin:
        raise InstallError("Git fallback requested but 'git' is not available in PATH.")

    repo_root = os.path.join(dest_dir, "repo-git")
    remote = f"https://github.com/{owner}/{repo}.git"
    _run_checked_command(
        [git_bin, "clone", "--filter=blob:none", "--no-checkout", remote, repo_root],
        context="Git fallback clone failed",
    )

    sparse_path = os.path.normpath(plugin_subpath).replace("\\", "/")
    if sparse_path.startswith("./"):
        sparse_path = sparse_path[2:]
    if sparse_path:
        _run_checked_command(
            [git_bin, "-C", repo_root, "sparse-checkout", "init", "--cone"],
            context="Git fallback sparse-checkout init failed",
        )
        _run_checked_command(
            [git_bin, "-C", repo_root, "sparse-checkout", "set", sparse_path],
            context="Git fallback sparse-checkout set failed",
        )

    _run_checked_command(
        [git_bin, "-C", repo_root, "fetch", "--depth", "1", "origin", ref],
        context="Git fallback fetch failed",
    )
    _run_checked_command(
        [git_bin, "-C", repo_root, "checkout", "--detach", "FETCH_HEAD"],
        context="Git fallback checkout failed",
    )
    return repo_root


def _fetch_repo_with_fallback(
    owner: str,
    repo: str,
    ref: str,
    dest_dir: str,
    plugin_subpath: str,
) -> tuple[str, str]:
    try:
        return _download_repo_zip(owner, repo, ref, dest_dir), "zipball"
    except InstallError as zip_error:
        try:
            return (
                _download_repo_git_sparse(owner, repo, ref, dest_dir, plugin_subpath),
                "git_sparse_fallback",
            )
        except InstallError as git_error:
            raise InstallError(
                "Could not fetch repository via zipball or git fallback. "
                f"zip_error='{zip_error}' git_error='{git_error}'"
            ) from git_error


def _assert_path_within_repo(repo_root: str, candidate: str) -> None:
    repo_real = os.path.realpath(repo_root)
    candidate_real = os.path.realpath(candidate)
    if candidate_real == repo_real or candidate_real.startswith(repo_real + os.sep):
        return
    raise InstallError(
        "Resolved plugin path is outside fetched repository root. "
        f"repo={repo_real} candidate={candidate_real}"
    )


def _assert_tree_has_no_symlinks(path: str) -> None:
    if os.path.islink(path):
        raise InstallError(f"Plugin root must not be a symlink: {path}")

    for root, dirs, files in os.walk(path, followlinks=False):
        for directory in dirs:
            full = os.path.join(root, directory)
            if os.path.islink(full):
                raise InstallError(f"Symlinks are not allowed in imported plugins: {full}")
        for filename in files:
            full = os.path.join(root, filename)
            if os.path.islink(full):
                raise InstallError(f"Symlinks are not allowed in imported plugins: {full}")


def _validate_plugin_root(path: str) -> tuple[str, dict[str, object]]:
    _assert_tree_has_no_symlinks(path)
    manifest_path = os.path.join(path, ".codex-plugin", "plugin.json")
    if not os.path.isfile(manifest_path):
        raise InstallError(".codex-plugin/plugin.json not found in selected plugin directory.")

    try:
        payload = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise InstallError(f"plugin.json is invalid JSON: {exc}") from exc

    if not isinstance(payload, dict):
        raise InstallError("plugin.json must contain a JSON object.")

    name = payload.get("name")
    if not isinstance(name, str) or not name.strip():
        raise InstallError("plugin.json must include a non-empty 'name'.")

    return name.strip(), payload


def _resolve_install_plugin_name(
    *,
    detected_name: str,
    override_name: str | None,
    allow_manifest_name_mismatch: bool,
) -> str:
    plugin_name = override_name.strip() if override_name else detected_name
    if plugin_name != detected_name and not allow_manifest_name_mismatch:
        raise InstallError(
            "Installed plugin directory name must match plugin.json name by default. "
            f"manifest='{detected_name}' requested='{plugin_name}'. "
            "Pass --allow-manifest-name-mismatch to override."
        )
    return plugin_name


def _uv_python_command() -> list[str]:
    uv_bin = shutil.which("uv")
    if not uv_bin:
        raise InstallError(f"uv is required for plugin install validation but was not found in PATH. {UV_INSTALL_HINT}")
    return [uv_bin, "run", "python"]


def _read_manifest(path: str) -> dict[str, object]:
    manifest_path = Path(path) / ".codex-plugin" / "plugin.json"
    if not manifest_path.is_file():
        raise InstallError(f"Missing plugin manifest: {manifest_path}")
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise InstallError(f"plugin manifest is invalid JSON: {manifest_path}") from exc
    if not isinstance(payload, dict):
        raise InstallError(f"plugin manifest must contain an object: {manifest_path}")
    return payload


def _manifest_version(payload: dict[str, object]) -> str | None:
    version = payload.get("version")
    if isinstance(version, str) and version.strip():
        return version.strip()
    return None


def _manifest_dependencies(payload: dict[str, object]) -> list[str]:
    raw = payload.get("dependencies")
    if raw is None:
        return []
    if not isinstance(raw, list):
        raise InstallError("plugin.json field 'dependencies' must be an array of plugin names when present.")
    deps: list[str] = []
    for value in raw:
        if not isinstance(value, str) or not value.strip():
            raise InstallError("plugin.json field 'dependencies' must contain non-empty strings.")
        dep = value.strip()
        deps.append(dep)
    return deps


def _dependency_lookup_name(identifier: str) -> str:
    return identifier.split("@", 1)[0]


def _validate_dependency_identifier(
    dependency: str,
    *,
    allow_cross_marketplace_dependencies: bool,
) -> None:
    if "@" not in dependency:
        if not PLUGIN_NAME_RE.fullmatch(dependency):
            raise InstallError(
                f"Dependency '{dependency}' is invalid. Expected kebab-case plugin name "
                "matching `[a-z0-9](?:-?[a-z0-9]){0,63}`."
            )
        return

    if not allow_cross_marketplace_dependencies:
        raise InstallError(
            "Cross-marketplace dependency identifiers are blocked by default. "
            f"Dependency '{dependency}' uses a qualified form; "
            "pass --allow-cross-marketplace-dependencies to override."
        )

    parts = dependency.split("@")
    if len(parts) != 2:
        raise InstallError(
            f"Dependency '{dependency}' is invalid. Expected exactly one '@' separator."
        )
    plugin_name, marketplace_name = parts[0].strip(), parts[1].strip()
    if not PLUGIN_NAME_RE.fullmatch(plugin_name):
        raise InstallError(
            f"Dependency '{dependency}' has invalid plugin segment '{plugin_name}'."
        )
    if not PLUGIN_NAME_RE.fullmatch(marketplace_name):
        raise InstallError(
            f"Dependency '{dependency}' has invalid marketplace segment '{marketplace_name}'."
        )


def _parse_semver(value: str) -> tuple[int, int, int, list[str]] | None:
    match = SEMVER_RE.fullmatch(value.strip())
    if not match:
        return None
    major = int(match.group(1))
    minor = int(match.group(2))
    patch = int(match.group(3))
    prerelease = match.group(4)
    prerelease_parts = prerelease.split(".") if prerelease else []
    return major, minor, patch, prerelease_parts


def _compare_prerelease(left_parts: list[str], right_parts: list[str]) -> int:
    if not left_parts and not right_parts:
        return 0
    if not left_parts:
        return 1
    if not right_parts:
        return -1

    for left, right in zip(left_parts, right_parts):
        if left == right:
            continue
        left_is_digit = left.isdigit()
        right_is_digit = right.isdigit()
        if left_is_digit and right_is_digit:
            left_num = int(left)
            right_num = int(right)
            if left_num < right_num:
                return -1
            if left_num > right_num:
                return 1
            continue
        if left_is_digit and not right_is_digit:
            return -1
        if not left_is_digit and right_is_digit:
            return 1
        if left < right:
            return -1
        return 1

    if len(left_parts) < len(right_parts):
        return -1
    if len(left_parts) > len(right_parts):
        return 1
    return 0


def _compare_versions(candidate: str, current: str) -> int | None:
    left = _parse_semver(candidate)
    right = _parse_semver(current)
    if left is None or right is None:
        return None

    for left_part, right_part in zip(left[:3], right[:3]):
        if left_part < right_part:
            return -1
        if left_part > right_part:
            return 1
    return _compare_prerelease(left[3], right[3])


def _collect_installed_plugin_dependencies(dest_root: str, plugin_name: str) -> dict[str, list[str]]:
    graph: dict[str, list[str]] = {}
    for entry in Path(dest_root).iterdir():
        if not entry.is_dir() or entry.name.startswith("."):
            continue
        if entry.name == plugin_name:
            continue
        manifest_path = entry / ".codex-plugin" / "plugin.json"
        if not manifest_path.is_file():
            continue
        try:
            payload = _read_manifest(str(entry))
        except InstallError:
            continue
        node_name = payload.get("name") if isinstance(payload.get("name"), str) else entry.name
        graph[str(node_name)] = _manifest_dependencies(payload)
    return graph


def _find_dependency_cycle(graph: dict[str, list[str]], root: str) -> list[str] | None:
    visited: set[str] = set()
    active: list[str] = []

    def walk(node: str) -> list[str] | None:
        if node in active:
            start = active.index(node)
            return [*active[start:], node]
        if node in visited:
            return None
        visited.add(node)
        active.append(node)
        for dep in graph.get(node, []):
            cycle = walk(dep)
            if cycle:
                return cycle
        active.pop()
        return None

    return walk(root)


def _preflight_dependencies(
    *,
    plugin_name: str,
    plugin_dependencies: list[str],
    dest_root: str,
    allow_missing_dependencies: bool,
    allow_cross_marketplace_dependencies: bool,
    journal_path: str,
) -> None:
    normalized_dependencies: list[str] = []
    for dependency in plugin_dependencies:
        _validate_dependency_identifier(
            dependency,
            allow_cross_marketplace_dependencies=allow_cross_marketplace_dependencies,
        )
        normalized_dependencies.append(_dependency_lookup_name(dependency))

    graph = _collect_installed_plugin_dependencies(dest_root, plugin_name)
    graph[plugin_name] = normalized_dependencies
    cycle = _find_dependency_cycle(graph, plugin_name)
    if cycle:
        raise InstallError(
            "Dependency cycle detected during preflight: " + " -> ".join(cycle)
        )

    if not allow_missing_dependencies:
        known_plugins = set(graph)
        missing = sorted(dep for dep in normalized_dependencies if dep not in known_plugins)
        if missing:
            raise InstallError(
                "Dependency preflight failed. Missing installed dependencies: "
                + ", ".join(missing)
                + ". Install dependencies first or pass --allow-missing-dependencies."
            )

    _write_journal_row(
        journal_path,
        "dependency_preflight_passed",
        {
            "plugin_name": plugin_name,
            "dependency_count": len(plugin_dependencies),
            "allow_missing_dependencies": allow_missing_dependencies,
            "allow_cross_marketplace_dependencies": allow_cross_marketplace_dependencies,
        },
    )


def _should_upgrade_destination(
    *,
    upgrade_mode: str,
    staged_manifest: dict[str, object],
    existing_manifest: dict[str, object],
) -> tuple[bool, str]:
    if upgrade_mode == "force":
        return True, "forced upgrade enabled"

    staged_version = _manifest_version(staged_manifest)
    existing_version = _manifest_version(existing_manifest)
    if not staged_version:
        return False, "staged plugin does not declare a version; use --upgrade force to replace existing plugin"
    if not existing_version:
        return True, "existing plugin has no version; staged plugin declares version"

    comparison = _compare_versions(staged_version, existing_version)
    if comparison is None:
        return (
            False,
            f"cannot compare versions '{staged_version}' vs '{existing_version}' with semver rules; use --upgrade force",
        )
    if comparison <= 0:
        return (
            False,
            f"staged version {staged_version} is not newer than installed version {existing_version}",
        )
    return True, f"staged version {staged_version} is newer than installed version {existing_version}"


def _journal_path(dest_root: str, run_id: str) -> str:
    return os.path.join(dest_root, ".install-journal", "plugin-installer", f"{run_id}.jsonl")


def _provenance_path(dest_root: str, run_id: str) -> str:
    return os.path.join(dest_root, ".provenance", "plugin-installer", f"{run_id}.json")


def _write_journal_row(path: str, event: str, details: dict[str, object]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    row = {
        "timestamp": _utc_now_iso(),
        "event": event,
        "details": details,
    }
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def _write_json_atomic(path: str, payload: dict[str, object]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(target.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    os.replace(str(tmp), str(target))


def _plugin_builder_script() -> Path:
    repo_root = Path(__file__).resolve().parents[3]
    primary = repo_root / "utilities" / "plugin-builder" / "scripts" / "plugin_builder.py"
    if primary.exists():
        return primary
    fallback = repo_root / "utilities" / "codex-plugin-builder" / "scripts" / "plugin_builder.py"
    if fallback.exists():
        return fallback
    raise InstallError("Plugin validator script not found under utilities/plugin-builder or utilities/codex-plugin-builder.")


def _run_plugin_validation(
    plugin_dir: str,
    validation_level: str,
    journal_path: str,
    *,
    provenance_manifest_path: str | None = None,
    require_signed_provenance: bool = False,
    allowed_signer_emails: set[str] | None = None,
    allowed_signer_domains: set[str] | None = None,
    allowed_signer_logins: set[str] | None = None,
) -> None:
    if validation_level == "compat":
        _write_journal_row(journal_path, "stage_validation_skipped", {"validation_level": validation_level})
        return

    if require_signed_provenance and not provenance_manifest_path:
        raise InstallError("Signed provenance preflight requires a provenance manifest path.")

    builder_script = _plugin_builder_script()
    cmd = [*_uv_python_command(), str(builder_script), "validate", plugin_dir]
    if provenance_manifest_path:
        cmd.extend(["--provenance-manifest", provenance_manifest_path])
    if require_signed_provenance:
        cmd.append("--require-signed-provenance")
    for value in sorted(allowed_signer_emails or set()):
        cmd.extend(["--allow-signer-email", value])
    for value in sorted(allowed_signer_domains or set()):
        cmd.extend(["--allow-signer-domain", value])
    for value in sorted(allowed_signer_logins or set()):
        cmd.extend(["--allow-signer-login", value])
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    output = (proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")
    exit_code = proc.returncode

    _write_journal_row(
        journal_path,
        "stage_validator_result",
        {
            "validator": "plugin_builder.validate",
            "command": " ".join(cmd),
            "exit_code": exit_code,
            "stdout_tail": output[-1200:],
        },
    )

    if exit_code != 0:
        raise InstallError("Staged validation failed for plugin package. See rollback journal for validator output.")


def _rollback_install_state(
    *,
    destination: str | None,
    previous_destination_backup: str | None,
    journal_path: str | None,
) -> None:
    if destination and os.path.isdir(destination):
        shutil.rmtree(destination, ignore_errors=True)
        if journal_path:
            _write_journal_row(journal_path, "rollback_removed_destination", {"destination": destination})
    if previous_destination_backup and destination and os.path.isdir(previous_destination_backup):
        os.replace(previous_destination_backup, destination)
        if journal_path:
            _write_journal_row(
                journal_path,
                "rollback_restored_previous_destination",
                {"destination": destination, "backup_path": previous_destination_backup},
            )


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Install a Codex plugin from GitHub (requires uv in PATH).")
    parser.add_argument("--url", help="GitHub URL (supports /tree/<ref>/<path>).")
    parser.add_argument("--repo", help="GitHub repo in owner/repo format.")
    parser.add_argument("--path", required=False, help="Plugin directory path inside repo.")
    parser.add_argument("--ref", default=DEFAULT_REF, help="Git ref (default: main).")
    parser.add_argument("--dest", default=os.path.join(_codex_home(), "plugins"), help="Destination plugin root.")
    parser.add_argument("--name", help="Override installed plugin folder name.")
    parser.add_argument(
        "--allow-manifest-name-mismatch",
        action="store_true",
        help="Allow installed directory name to differ from plugin.json name.",
    )
    parser.add_argument("--validation-level", choices=("strict", "compat"), default="strict")
    parser.add_argument(
        "--upgrade",
        choices=("never", "if-newer", "force"),
        default="never",
        help="Upgrade policy when destination already exists.",
    )
    parser.add_argument("--trusted-repo", action="append", default=[], help="Additional trusted owner/repo.")
    parser.add_argument("--allow-untrusted-source", action="store_true", help="Allow install outside trusted allowlist.")
    parser.add_argument("--allow-unpinned-ref", action="store_true", help="Allow non-commit refs such as main.")
    parser.add_argument(
        "--allow-missing-dependencies",
        action="store_true",
        help="Allow installation even when plugin.json declares dependencies that are not currently installed.",
    )
    parser.add_argument(
        "--allow-cross-marketplace-dependencies",
        action="store_true",
        help="Allow dependency identifiers that use marketplace-qualified form (for example 'plugin@marketplace').",
    )
    parser.add_argument(
        "--allow-unsigned-provenance",
        action="store_true",
        help="Allow installation from commits that are not signature-verified by GitHub provenance checks.",
    )
    parser.add_argument(
        "--allow-signer-email",
        action="append",
        default=[],
        help="Allow only signed commits from these exact signer emails (repeatable).",
    )
    parser.add_argument(
        "--allow-signer-domain",
        action="append",
        default=[],
        help="Allow only signed commits from these signer email domains (repeatable).",
    )
    parser.add_argument(
        "--allow-signer-login",
        action="append",
        default=[],
        help="Allow only signed commits from these GitHub signer logins (repeatable).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv or sys.argv[1:])
    destination: str | None = None
    previous_destination_backup: str | None = None
    journal_path: str | None = None
    tmp_dir: str | None = None

    try:
        if not args.url and not args.repo:
            raise InstallError("Provide --url or --repo.")
        if args.url and args.repo:
            raise InstallError("Use only one source selector: --url or --repo.")

        if args.url:
            owner, repo, ref_from_url, path_from_url = _parse_github_url(args.url, args.ref)
            plugin_path = args.path or path_from_url
        else:
            repo_id = _normalize_repo_id(args.repo)
            owner, repo = repo_id.split("/")
            ref_from_url = args.ref
            plugin_path = args.path

        if not plugin_path:
            raise InstallError("Missing plugin path. Provide --path or include /tree/<ref>/<path> in --url.")

        _validate_relative_path(plugin_path)
        _validate_ref_token(ref_from_url)

        repo_id = f"{owner.lower()}/{repo.lower()}"
        trust_overridden = bool(args.allow_untrusted_source)
        pin_overridden = bool(args.allow_unpinned_ref)
        trust_policy = "allowlist_override" if trust_overridden else "allowlist_enforced"
        trust_allowlist = {_normalize_repo_id(text) for text in DEFAULT_TRUSTED_REPOS}
        trust_allowlist.update(_normalize_repo_id(text) for text in args.trusted_repo)
        if not args.allow_untrusted_source and repo_id not in trust_allowlist:
            raise InstallError(
                f"Repository '{repo_id}' is not in trusted allowlist. "
                "Use --trusted-repo owner/repo or --allow-untrusted-source with explicit approval."
            )

        if not args.allow_unpinned_ref and not _is_pinned_ref(ref_from_url):
            raise InstallError(
                "Ref must be pinned to a commit SHA for provenance safety. "
                "Use --allow-unpinned-ref only with explicit approval."
            )

        allowed_signer_emails = _normalize_allowlist(args.allow_signer_email)
        allowed_signer_domains = _normalize_domain_allowlist(args.allow_signer_domain)
        allowed_signer_logins = _normalize_allowlist(args.allow_signer_login)
        resolved_commit, commit_verification, signer_identity = _resolve_commit_provenance(owner, repo, ref_from_url)

        run_id = str(uuid.uuid4()).replace("-", "")
        dest_root = os.path.abspath(args.dest)
        os.makedirs(dest_root, exist_ok=True)
        journal_path = _journal_path(dest_root, run_id)

        tmp_dir = tempfile.mkdtemp(prefix="plugin-install-", dir=_tmp_root())
        _write_journal_row(journal_path, "run_started", {
            "run_id": run_id,
            "repo": repo_id,
            "ref": ref_from_url,
            "resolved_commit": resolved_commit,
            "path": plugin_path,
            "dest_root": dest_root,
            "validation_level": args.validation_level,
            "upgrade_mode": args.upgrade,
            "trust_policy": trust_policy,
            "trust_overridden": trust_overridden,
            "pin_overridden": pin_overridden,
            "allow_missing_dependencies": bool(args.allow_missing_dependencies),
            "allow_cross_marketplace_dependencies": bool(args.allow_cross_marketplace_dependencies),
            "allow_unsigned_provenance": bool(args.allow_unsigned_provenance),
            "commit_verification": commit_verification,
            "signer_identity": signer_identity,
            "allowed_signer_emails": sorted(allowed_signer_emails),
            "allowed_signer_domains": sorted(allowed_signer_domains),
            "allowed_signer_logins": sorted(allowed_signer_logins),
        })
        _enforce_signed_commit_provenance(
            owner=owner,
            repo=repo,
            resolved_commit=resolved_commit,
            commit_verification=commit_verification,
            signer_identity=signer_identity,
            allow_unsigned_provenance=bool(args.allow_unsigned_provenance),
            allowed_signer_emails=allowed_signer_emails,
            allowed_signer_domains=allowed_signer_domains,
            allowed_signer_logins=allowed_signer_logins,
            journal_path=journal_path,
        )

        repo_root, transport = _fetch_repo_with_fallback(
            owner,
            repo,
            resolved_commit,
            tmp_dir,
            plugin_path,
        )
        _write_journal_row(
            journal_path,
            "repository_fetched",
            {
                "repo": repo_id,
                "transport": transport,
                "resolved_commit": resolved_commit,
            },
        )
        candidate = os.path.join(repo_root, os.path.normpath(plugin_path))
        _assert_path_within_repo(repo_root, candidate)

        detected_name, detected_manifest = _validate_plugin_root(candidate)
        staged_version = _manifest_version(detected_manifest)
        plugin_name = _resolve_install_plugin_name(
            detected_name=detected_name,
            override_name=args.name,
            allow_manifest_name_mismatch=bool(args.allow_manifest_name_mismatch),
        )
        if not PLUGIN_NAME_RE.fullmatch(plugin_name):
            raise InstallError("Plugin name must be kebab-case and <=64 chars.")

        stage_root = os.path.join(tmp_dir, "stage")
        stage_dir = os.path.join(stage_root, plugin_name)
        os.makedirs(stage_root, exist_ok=True)
        shutil.copytree(candidate, stage_dir)
        validation_provenance_path = os.path.join(tmp_dir, "validation-provenance.json")
        _write_json_atomic(
            validation_provenance_path,
            {
                "schema_version": "1.0",
                "plugin_name": plugin_name,
                "source": {
                    "owner": owner,
                    "repo": repo,
                    "ref_requested": ref_from_url,
                    "resolved_commit": resolved_commit,
                    "path": plugin_path,
                },
                "commit_verification": commit_verification,
                "signer_identity": signer_identity,
            },
        )
        _write_journal_row(
            journal_path,
            "plugin_staged",
            {
                "stage_dir": stage_dir,
                "plugin_name": plugin_name,
                "staged_version": staged_version,
                "trust_overridden": trust_overridden,
                "pin_overridden": pin_overridden,
                "validation_provenance_path": validation_provenance_path,
            },
        )

        staged_dependencies = _manifest_dependencies(detected_manifest)
        _preflight_dependencies(
            plugin_name=plugin_name,
            plugin_dependencies=staged_dependencies,
            dest_root=dest_root,
            allow_missing_dependencies=bool(args.allow_missing_dependencies),
            allow_cross_marketplace_dependencies=bool(args.allow_cross_marketplace_dependencies),
            journal_path=journal_path,
        )

        _run_plugin_validation(
            stage_dir,
            args.validation_level,
            journal_path,
            provenance_manifest_path=validation_provenance_path,
            require_signed_provenance=not bool(args.allow_unsigned_provenance),
            allowed_signer_emails=allowed_signer_emails,
            allowed_signer_domains=allowed_signer_domains,
            allowed_signer_logins=allowed_signer_logins,
        )

        destination = os.path.join(dest_root, plugin_name)
        installed_version_before_upgrade: str | None = None
        if os.path.exists(destination):
            if args.upgrade == "never":
                raise InstallError(
                    f"Destination already exists: {destination}. "
                    "Use --upgrade if-newer or --upgrade force to replace it."
                )
            existing_manifest = _read_manifest(destination)
            installed_version_before_upgrade = _manifest_version(existing_manifest)
            should_upgrade, reason = _should_upgrade_destination(
                upgrade_mode=args.upgrade,
                staged_manifest=detected_manifest,
                existing_manifest=existing_manifest,
            )
            if not should_upgrade:
                raise InstallError(f"Upgrade blocked for '{plugin_name}': {reason}")

            previous_destination_backup = os.path.join(tmp_dir, f"existing-{plugin_name}")
            if os.path.exists(previous_destination_backup):
                shutil.rmtree(previous_destination_backup, ignore_errors=True)
            os.replace(destination, previous_destination_backup)
            _write_journal_row(
                journal_path,
                "plugin_upgrade_backup_created",
                {
                    "destination": destination,
                    "backup_path": previous_destination_backup,
                    "reason": reason,
                    "installed_version": installed_version_before_upgrade,
                    "staged_version": staged_version,
                },
            )
        os.replace(stage_dir, destination)
        install_path = os.path.relpath(destination, dest_root)
        _write_journal_row(
            journal_path,
            "plugin_promoted",
            {
                "destination": destination,
                "install_path": install_path,
                "upgrade_mode": args.upgrade,
                "installed_version_before_upgrade": installed_version_before_upgrade,
                "installed_version_after_upgrade": staged_version,
                "trust_overridden": trust_overridden,
                "pin_overridden": pin_overridden,
            },
        )

        provenance = {
            "schema_version": "1.0",
            "run_id": run_id,
            "timestamp": _utc_now_iso(),
            "source": {
                "owner": owner,
                "repo": repo,
                "ref_requested": ref_from_url,
                "resolved_commit": resolved_commit,
                "path": plugin_path,
            },
            "commit_verification": commit_verification,
            "signer_identity": signer_identity,
            "destination": destination,
            "install_path": install_path,
            "validation_level": args.validation_level,
            "upgrade_mode": args.upgrade,
            "trust_policy": trust_policy,
            "trust_overridden": trust_overridden,
            "pin_overridden": pin_overridden,
            "dependencies": staged_dependencies,
            "allow_missing_dependencies": bool(args.allow_missing_dependencies),
            "allow_cross_marketplace_dependencies": bool(args.allow_cross_marketplace_dependencies),
            "allowed_signer_emails": sorted(allowed_signer_emails),
            "allowed_signer_domains": sorted(allowed_signer_domains),
            "allowed_signer_logins": sorted(allowed_signer_logins),
            "staged_version": staged_version,
        }
        _write_json_atomic(_provenance_path(dest_root, run_id), provenance)
        _write_journal_row(journal_path, "run_completed", {"destination": destination})
        if previous_destination_backup and os.path.isdir(previous_destination_backup):
            shutil.rmtree(previous_destination_backup, ignore_errors=True)
            _write_journal_row(
                journal_path,
                "plugin_upgrade_backup_removed",
                {"backup_path": previous_destination_backup},
            )
            previous_destination_backup = None

        print(f"Installed {plugin_name} to {destination}")
        print("Restart Codex to refresh plugin discovery.")
        return 0

    except InstallError as exc:
        _rollback_install_state(
            destination=destination,
            previous_destination_backup=previous_destination_backup,
            journal_path=journal_path,
        )
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    except Exception as exc:  # noqa: BLE001
        _rollback_install_state(
            destination=destination,
            previous_destination_backup=previous_destination_backup,
            journal_path=journal_path,
        )
        print(f"ERROR: unexpected installer failure: {exc}", file=sys.stderr)
        return 1
    finally:
        if tmp_dir:
            shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
