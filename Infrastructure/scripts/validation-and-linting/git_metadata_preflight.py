#!/usr/bin/env python3
"""Fail-closed Git metadata preflight for ordinary and linked worktrees.

This is the shared ``git-metadata-preflight/v1`` leaf adapter.  It checks the
metadata directories that Git must write before a hook spends time on source
validation.  It reports stale or active locks but never removes them.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
from typing import Any


CONTRACT = "git-metadata-preflight/v1"
EXIT_BLOCKED = 78
EXIT_INTERNAL = 70
EXIT_USAGE = 64
DEFAULT_LOCK_MAX_AGE_SECONDS = 900


def _run_git(repo_root: Path, *args: str) -> tuple[int, str, str]:
    proc = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def _resolve_git_path(repo_root: Path, value: str) -> Path:
    path = Path(value)
    return (path if path.is_absolute() else repo_root / path).resolve()


def _probe_write(path: Path) -> dict[str, Any]:
    if not path.is_dir():
        return {"path": str(path), "status": "blocked", "reason": "path_missing"}
    fd: int | None = None
    probe_path: Path | None = None
    result: dict[str, Any]
    try:
        fd, raw_path = tempfile.mkstemp(prefix=".git-metadata-preflight.", dir=path)
        probe_path = Path(raw_path)
        os.write(fd, b"git-metadata-preflight/v1\n")
        result = {"path": str(path), "status": "pass"}
    except OSError as exc:
        result = {
            "path": str(path),
            "status": "blocked",
            "reason": "write_denied",
            "error": str(exc),
        }
    finally:
        if fd is not None:
            os.close(fd)
        if probe_path is not None:
            try:
                probe_path.unlink()
            except OSError as exc:
                result = {
                    "path": str(path),
                    "status": "blocked",
                    "reason": "cleanup_denied",
                    "error": str(exc),
                }
    return result


def _lock_owner(path: Path) -> str | None:
    lsof = shutil.which("lsof")
    if lsof is None:
        return None
    try:
        proc = subprocess.run(
            [lsof, "-nP", "--", str(path)],
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError:
        return None
    if proc.returncode != 0:
        return None
    lines = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    return " | ".join(lines[:4]) if lines else None


def _classify_lock(path: Path, max_age_seconds: int) -> dict[str, Any]:
    now = time.time()
    try:
        age_seconds = max(0, int(now - path.stat().st_mtime))
    except OSError as exc:
        return {
            "path": str(path),
            "classification": "lock_stat_failed",
            "error": str(exc),
        }

    owner = _lock_owner(path)
    if owner:
        classification = "active_index_lock"
    elif age_seconds >= max_age_seconds:
        classification = "stale_index_lock_candidate"
    else:
        classification = "recent_index_lock_unknown"

    result: dict[str, Any] = {
        "path": str(path),
        "classification": classification,
        "age_seconds": age_seconds,
    }
    if owner:
        result["owner"] = owner
    return result


def _parse_worktree_records(output: str) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    current: dict[str, str] = {}
    for line in output.splitlines():
        if not line:
            if current:
                records.append(current)
                current = {}
            continue
        key, _, value = line.partition(" ")
        if key == "worktree":
            if current:
                records.append(current)
                current = {}
            current["path"] = value
        elif key == "prunable":
            current["prunable_reason"] = value
        elif key == "locked":
            current["locked_reason"] = value
    if current:
        records.append(current)
    return records


def _unique_paths(paths: list[Path]) -> list[Path]:
    result: list[Path] = []
    seen: set[str] = set()
    for path in paths:
        key = str(path)
        if key not in seen:
            result.append(path)
            seen.add(key)
    return result


class MetadataPreflightError(RuntimeError):
    """Raised when Git metadata cannot be resolved."""


def _resolve_metadata(repo_root: Path) -> dict[str, Path]:
    commands = {
        "git_common_dir": ("rev-parse", "--git-common-dir"),
        "git_dir": ("rev-parse", "--git-dir"),
        "index_path": ("rev-parse", "--git-path", "index"),
        "index_lock_path": ("rev-parse", "--git-path", "index.lock"),
    }
    resolved: dict[str, Path] = {}
    for key, args in commands.items():
        code, value, stderr = _run_git(repo_root, *args)
        if code != 0 or not value:
            raise MetadataPreflightError(stderr or f"git {' '.join(args)} failed")
        resolved[key] = _resolve_git_path(repo_root, value)
    return resolved


def _write_probes(metadata_dirs: list[Path], probe_write: bool) -> list[dict[str, Any]]:
    if probe_write:
        return [_probe_write(path) for path in metadata_dirs]
    return [{"path": str(path), "status": "skipped"} for path in metadata_dirs]


def _lock_records(
    index_lock_path: Path, worktrees_dir: Path, lock_max_age_seconds: int
) -> list[dict[str, Any]]:
    lock_paths = [index_lock_path] if index_lock_path.is_file() else []
    if worktrees_dir.is_dir():
        lock_paths.extend(sorted(worktrees_dir.glob("*/index.lock")))
    return [
        _classify_lock(path, lock_max_age_seconds)
        for path in _unique_paths(lock_paths)
    ]


def _worktree_state(
    repo_root: Path, worktrees_dir: Path, git_dir: Path
) -> tuple[list[dict[str, Any]], list[dict[str, str]], str | None]:
    locked: list[dict[str, Any]] = []
    if worktrees_dir.is_dir():
        for locked_path in sorted(worktrees_dir.glob("*/locked")):
            try:
                reason = locked_path.read_text(encoding="utf-8").strip()
            except OSError as exc:
                reason = f"unreadable: {exc}"
            locked.append(
                {
                    "metadata_dir": str(locked_path.parent.resolve()),
                    "reason": reason,
                    "current": locked_path.parent.resolve() == git_dir,
                }
            )
    code, output, stderr = _run_git(repo_root, "worktree", "list", "--porcelain")
    prunable = [
        record
        for record in _parse_worktree_records(output)
        if "prunable_reason" in record
    ] if code == 0 else []
    return locked, prunable, stderr if code != 0 else None


def _metadata_reasons(write_results: list[dict[str, Any]]) -> list[str]:
    reasons: list[str] = []
    if any(item.get("reason") == "path_missing" for item in write_results):
        reasons.append("metadata_path_missing")
    if any(item.get("reason") in {"write_denied", "cleanup_denied"} for item in write_results):
        reasons.append("metadata_write_denied")
    return reasons


def _lock_reasons(
    result: dict[str, Any],
    lock_records: list[dict[str, Any]],
    index_lock_path: Path,
    allow_current_index_lock: bool,
) -> tuple[list[str], list[str]]:
    reasons: list[str] = []
    advisories: list[str] = []
    if any(item.get("classification") == "lock_stat_failed" for item in lock_records):
        reasons.append("metadata_lock_uninspectable")
    current_lock = [item for item in lock_records if item.get("path") == str(index_lock_path)]
    if current_lock and allow_current_index_lock:
        advisories.append("expected_current_index_lock")
    elif current_lock:
        reasons.append(str(current_lock[0].get("classification", "index_lock")))
    if any(item.get("current") for item in result["locked_worktrees"]):
        reasons.append("locked_current_worktree")
    if result["prunable_worktrees"]:
        advisories.append("prunable_worktree")
    return list(dict.fromkeys(reasons)), advisories


def _reason_codes(
    result: dict[str, Any],
    write_results: list[dict[str, Any]],
    lock_records: list[dict[str, Any]],
    index_lock_path: Path,
    allow_current_index_lock: bool,
) -> tuple[list[str], list[str]]:
    reasons = _metadata_reasons(write_results)
    lock_reasons, advisories = _lock_reasons(
        result, lock_records, index_lock_path, allow_current_index_lock
    )
    reasons.extend(lock_reasons)
    return list(dict.fromkeys(reasons)), advisories


def _next_action(reasons: list[str]) -> str:
    if not reasons:
        return "Git metadata is writable and no current-worktree lock blocks the hook"
    if any(reason in reasons for reason in ("active_index_lock", "recent_index_lock_unknown")):
        return "wait for the lock owner or stop the owning process; do not delete the lock"
    if "stale_index_lock_candidate" in reasons:
        return "prove no owner, then use explicit Git worktree recovery; this preflight never removes locks"
    if "metadata_write_denied" in reasons:
        return "grant write access to the exact Git metadata directories or use a writable checkout"
    if "locked_current_worktree" in reasons:
        return "inspect the owning worktree and unlock it deliberately; do not delete metadata"
    return "repair Git metadata authority before running the hook again"


def _finalize(
    result: dict[str, Any],
    write_results: list[dict[str, Any]],
    lock_records: list[dict[str, Any]],
    index_lock_path: Path,
    allow_current_index_lock: bool,
) -> None:
    reasons, advisories = _reason_codes(
        result, write_results, lock_records, index_lock_path, allow_current_index_lock
    )
    if advisories:
        result.setdefault("advisories", []).extend(advisories)
    result["reason_codes"] = reasons
    result["status"] = "blocked" if reasons else "pass"
    result["next_action"] = _next_action(reasons)


def inspect(
    repo_root: Path,
    probe_write: bool,
    lock_max_age_seconds: int,
    allow_current_index_lock: bool = False,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "schema_version": 1, "contract": CONTRACT, "status": "blocked",
        "repo_root": str(repo_root.resolve()), "reason_codes": [],
        "locks": [], "locked_worktrees": [], "prunable_worktrees": [],
    }
    code, toplevel, stderr = _run_git(repo_root, "rev-parse", "--show-toplevel")
    if code != 0 or not toplevel:
        result.update(reason_codes=["not_git_worktree"], diagnostic=stderr or "git rev-parse --show-toplevel failed", next_action="run the hook from a Git worktree")
        return result
    repo_root = Path(toplevel).resolve()
    result["repo_root"] = str(repo_root)
    try:
        resolved = _resolve_metadata(repo_root)
    except MetadataPreflightError as exc:
        result.update(reason_codes=["git_metadata_unavailable"], diagnostic=str(exc), next_action="repair the Git checkout or use a writable clone")
        return result
    result.update({key: str(path) for key, path in resolved.items()})
    common_dir, git_dir = resolved["git_common_dir"], resolved["git_dir"]
    worktrees_dir = common_dir / "worktrees"
    result.update(worktrees_dir=str(worktrees_dir), linked_worktree=git_dir != common_dir)
    metadata_dirs = _unique_paths([resolved["index_path"].parent, git_dir, common_dir])
    result["metadata_dirs"] = [str(path) for path in metadata_dirs]
    write_results = _write_probes(metadata_dirs, probe_write)
    result["write_probe"] = write_results
    result["locks"] = _lock_records(resolved["index_lock_path"], worktrees_dir, lock_max_age_seconds)
    locked, prunable, worktree_error = _worktree_state(repo_root, worktrees_dir, git_dir)
    result.update(locked_worktrees=locked, prunable_worktrees=prunable)
    if worktree_error:
        result["worktree_list_diagnostic"] = worktree_error
    _finalize(result, write_results, result["locks"], resolved["index_lock_path"], allow_current_index_lock)
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    parser.add_argument("--no-write-probe", action="store_true")
    parser.add_argument(
        "--allow-current-index-lock",
        action="store_true",
        help="treat the current index.lock as an expected parent Git transaction (pre-commit only)",
    )
    parser.add_argument(
        "--lock-max-age-seconds",
        type=int,
        default=int(os.environ.get("GIT_METADATA_PREFLIGHT_LOCK_MAX_AGE_SECONDS", DEFAULT_LOCK_MAX_AGE_SECONDS)),
    )
    return parser.parse_args()


def main() -> int:
    try:
        args = parse_args()
        if args.lock_max_age_seconds < 0:
            raise ValueError("--lock-max-age-seconds must be non-negative")
        payload = inspect(
            args.repo_root,
            probe_write=not args.no_write_probe,
            lock_max_age_seconds=args.lock_max_age_seconds,
            allow_current_index_lock=args.allow_current_index_lock,
        )
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(json.dumps({"schema_version": 1, "contract": CONTRACT, "status": "blocked", "reason_codes": ["internal_error"], "diagnostic": str(exc)}, sort_keys=True))
        return EXIT_INTERNAL

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(
            f"[{CONTRACT}] {payload.get('status')} "
            f"reasons={','.join(payload.get('reason_codes', [])) or 'none'}"
        )
    return 0 if payload.get("status") == "pass" else EXIT_BLOCKED


if __name__ == "__main__":
    raise SystemExit(main())
