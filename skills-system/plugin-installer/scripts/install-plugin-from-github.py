#!/usr/bin/env python3
"""Install one plugin from GitHub into $CODEX_HOME/plugins with staged validation.

Installer guarantees:
- pinned refs required by default (40-char commit SHA unless override)
- source trust allowlist enforced by default
- plugin staged in quarantine before promotion
- strict mode runs plugin-builder validation before activation
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
DEFAULT_TRUSTED_REPOS = {
    "openai/plugins",
    "jamiecraik/agent-skills",
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


def _validate_ref_token(ref: str) -> None:
    clean_ref = ref.strip()
    if not clean_ref:
        raise InstallError("Ref cannot be empty.")
    if clean_ref.startswith("-"):
        raise InstallError("Ref must not start with '-'.")


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


def _validate_plugin_root(path: str) -> str:
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

    return name.strip()


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


def _run_plugin_validation(plugin_dir: str, validation_level: str, journal_path: str) -> None:
    if validation_level == "compat":
        _write_journal_row(journal_path, "stage_validation_skipped", {"validation_level": validation_level})
        return

    builder_script = _plugin_builder_script()
    cmd = [sys.executable, str(builder_script), "validate", plugin_dir]
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


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Install a Codex plugin from GitHub.")
    parser.add_argument("--url", help="GitHub URL (supports /tree/<ref>/<path>).")
    parser.add_argument("--repo", help="GitHub repo in owner/repo format.")
    parser.add_argument("--path", required=False, help="Plugin directory path inside repo.")
    parser.add_argument("--ref", default=DEFAULT_REF, help="Git ref (default: main).")
    parser.add_argument("--dest", default=os.path.join(_codex_home(), "plugins"), help="Destination plugin root.")
    parser.add_argument("--name", help="Override installed plugin folder name.")
    parser.add_argument("--validation-level", choices=("strict", "compat"), default="strict")
    parser.add_argument("--trusted-repo", action="append", default=[], help="Additional trusted owner/repo.")
    parser.add_argument("--allow-untrusted-source", action="store_true", help="Allow install outside trusted allowlist.")
    parser.add_argument("--allow-unpinned-ref", action="store_true", help="Allow non-commit refs such as main.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv or sys.argv[1:])
    destination: str | None = None
    journal_path: str | None = None

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
        trust_allowlist = set(DEFAULT_TRUSTED_REPOS)
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

        resolved_commit = _resolve_commit_sha(owner, repo, ref_from_url)

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
        })

        repo_root = _download_repo_zip(owner, repo, ref_from_url, tmp_dir)
        candidate = os.path.join(repo_root, os.path.normpath(plugin_path))
        _assert_path_within_repo(repo_root, candidate)

        detected_name = _validate_plugin_root(candidate)
        plugin_name = args.name.strip() if args.name else detected_name
        if not re.fullmatch(r"[a-z0-9](?:-?[a-z0-9]){0,63}", plugin_name):
            raise InstallError("Plugin name must be kebab-case and <=64 chars.")

        stage_root = os.path.join(tmp_dir, "stage")
        stage_dir = os.path.join(stage_root, plugin_name)
        os.makedirs(stage_root, exist_ok=True)
        shutil.copytree(candidate, stage_dir)
        _write_journal_row(journal_path, "plugin_staged", {"stage_dir": stage_dir, "plugin_name": plugin_name})

        _run_plugin_validation(stage_dir, args.validation_level, journal_path)

        destination = os.path.join(dest_root, plugin_name)
        if os.path.exists(destination):
            raise InstallError(f"Destination already exists: {destination}")
        os.replace(stage_dir, destination)
        _write_journal_row(journal_path, "plugin_promoted", {"destination": destination})

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
            "destination": destination,
            "validation_level": args.validation_level,
        }
        _write_json_atomic(_provenance_path(dest_root, run_id), provenance)
        _write_journal_row(journal_path, "run_completed", {"destination": destination})

        print(f"Installed {plugin_name} to {destination}")
        print("Restart Codex to refresh plugin discovery.")
        return 0

    except InstallError as exc:
        if destination and os.path.isdir(destination):
            shutil.rmtree(destination, ignore_errors=True)
            if journal_path:
                _write_journal_row(journal_path, "rollback_removed_destination", {"destination": destination})
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    except Exception as exc:  # noqa: BLE001
        if destination and os.path.isdir(destination):
            shutil.rmtree(destination, ignore_errors=True)
            if journal_path:
                _write_journal_row(journal_path, "rollback_removed_destination", {"destination": destination})
        print(f"ERROR: unexpected installer failure: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
