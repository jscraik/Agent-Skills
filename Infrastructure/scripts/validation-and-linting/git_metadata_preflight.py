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


def _initial_result(repo_root: Path) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "contract": CONTRACT,
        "status": "blocked",
        "repo_root": str(repo_root),
        "reason_codes": [],
        "locks": [],
        "locked_worktrees": [],
        "prunable_worktrees": [],
    }


def _resolve_toplevel(repo_root: Path, result: dict[str, Any]) -> Path | None:
    code, toplevel, stderr = _run_git(repo_root, "rev-parse", "--show-toplevel")
    if code == 0 and toplevel:
        resolved = Path(toplevel).resolve()
        result["repo_root"] = str(resolved)
        return resolved
    result["reason_codes"] = ["not_git_worktree"]
    result["diagnostic"] = stderr or "git rev-parse --show-toplevel failed"
    result["next_action"] = "run the hook from a Git worktree"
    return None


def _resolve_metadata_paths(repo_root: Path, result: dict[str, Any]) -> dict[str, Path] | None:
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
            result["reason_codes"] = ["git_metadata_unavailable"]
            result["diagnostic"] = stderr or f"git {' '.join(args)} failed"
            result["next_action"] = "repair the Git checkout or use a writable clone"
            return None
        resolved[key] = _resolve_git_path(repo_root, value)
        result[key] = str(resolved[key])
    return resolved


def _write_probe_records(metadata_dirs: list[Path], probe_write: bool) -> list[dict[str, Any]]:
    if probe_write:
        return [_probe_write(path) for path in metadata_dirs]
    return [{"path": str(path), "status": "skipped"} for path in metadata_dirs]


def _lock_records(index_lock_path: Path, worktrees_dir: Path, max_age_seconds: int) -> list[dict[str, Any]]:
    lock_paths = [index_lock_path] if index_lock_path.is_file() else []
    if worktrees_dir.is_dir():
        lock_paths.extend(sorted(worktrees_dir.glob("*/index.lock")))
    return [_classify_lock(path, max_age_seconds) for path in _unique_paths(lock_paths)]


def _locked_worktree_records(worktrees_dir: Path, git_dir: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for locked_path in sorted(worktrees_dir.glob("*/locked")) if worktrees_dir.is_dir() else []:
        try:
            reason = locked_path.read_text(encoding="utf-8").strip()
        except OSError as exc:
            reason = f"unreadable: {exc}"
        metadata_dir = locked_path.parent.resolve()
        records.append({"metadata_dir": str(metadata_dir), "reason": reason, "current": metadata_dir == git_dir})
    return records


def _record_prunable_worktrees(repo_root: Path, result: dict[str, Any]) -> None:
    code, output, stderr = _run_git(repo_root, "worktree", "list", "--porcelain")
    if code == 0:
        result["prunable_worktrees"] = [
            record for record in _parse_worktree_records(output) if "prunable_reason" in record
        ]
    elif stderr:
        result["worktree_list_diagnostic"] = stderr


def _write_reason_codes(write_results: list[dict[str, Any]]) -> list[str]:
    reasons = []
    if any(item.get("reason") == "path_missing" for item in write_results):
        reasons.append("metadata_path_missing")
    if any(item.get("reason") in {"write_denied", "cleanup_denied"} for item in write_results):
        reasons.append("metadata_write_denied")
    return reasons


def _lock_reason_codes(lock_records: list[dict[str, Any]]) -> list[str]:
    if any(item.get("classification") == "lock_stat_failed" for item in lock_records):
        return ["metadata_lock_uninspectable"]
    return []


def _current_lock_reason(
    lock_records: list[dict[str, Any]],
    index_lock_path: Path,
    allow_current_index_lock: bool,
    result: dict[str, Any],
) -> str | None:
    current_lock = next((item for item in lock_records if item.get("path") == str(index_lock_path)), None)
    if current_lock is None:
        return None
    if allow_current_index_lock:
        result.setdefault("advisories", []).append("expected_current_index_lock")
        return None
    return str(current_lock.get("classification", "index_lock"))


def _reason_codes(
    write_results: list[dict[str, Any]],
    lock_records: list[dict[str, Any]],
    index_lock_path: Path,
    locked_worktrees: list[dict[str, Any]],
    allow_current_index_lock: bool,
    result: dict[str, Any],
) -> list[str]:
    reasons = _write_reason_codes(write_results) + _lock_reason_codes(lock_records)
    current_lock_reason = _current_lock_reason(
        lock_records, index_lock_path, allow_current_index_lock, result
    )
    if current_lock_reason:
        reasons.append(current_lock_reason)
    if any(item.get("current") for item in locked_worktrees):
        reasons.append("locked_current_worktree")
    return list(dict.fromkeys(reasons))


def _finish_result(result: dict[str, Any]) -> None:
    reasons = result["reason_codes"]
    if not reasons:
        result["status"] = "pass"
        result["next_action"] = "Git metadata is writable and no current-worktree lock blocks the hook"
    elif any(reason in reasons for reason in ("active_index_lock", "recent_index_lock_unknown")):
        result["next_action"] = "wait for the lock owner or stop the owning process; do not delete the lock"
    elif "stale_index_lock_candidate" in reasons:
        result["next_action"] = "prove no owner, then use explicit Git worktree recovery; this preflight never removes locks"
    elif "metadata_write_denied" in reasons:
        result["next_action"] = "grant write access to the exact Git metadata directories or use a writable checkout"
    elif "locked_current_worktree" in reasons:
        result["next_action"] = "inspect the owning worktree and unlock it deliberately; do not delete metadata"
    else:
        result["next_action"] = "repair Git metadata authority before running the hook again"


def inspect(
    repo_root: Path,
    probe_write: bool,
    lock_max_age_seconds: int,
    allow_current_index_lock: bool = False,
) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    result = _initial_result(repo_root)
    repo_root = _resolve_toplevel(repo_root, result)
    if repo_root is None:
        return result
    resolved = _resolve_metadata_paths(repo_root, result)
    if resolved is None:
        return result
    common_dir, git_dir = resolved["git_common_dir"], resolved["git_dir"]
    index_path, index_lock_path = resolved["index_path"], resolved["index_lock_path"]
    worktrees_dir = common_dir / "worktrees"
    result["worktrees_dir"] = str(worktrees_dir)
    result["linked_worktree"] = git_dir != common_dir
    metadata_dirs = _unique_paths([index_path.parent, git_dir, common_dir])
    result["metadata_dirs"] = [str(path) for path in metadata_dirs]
    write_results = _write_probe_records(metadata_dirs, probe_write)
    result["write_probe"] = write_results
    lock_records = _lock_records(index_lock_path, worktrees_dir, lock_max_age_seconds)
    result["locks"] = lock_records
    locked_worktrees = _locked_worktree_records(worktrees_dir, git_dir)
    result["locked_worktrees"] = locked_worktrees
    _record_prunable_worktrees(repo_root, result)
    if result["prunable_worktrees"]:
        result.setdefault("advisories", []).append("prunable_worktree")
    result["reason_codes"] = _reason_codes(
        write_results, lock_records, index_lock_path, locked_worktrees, allow_current_index_lock, result
    )
    _finish_result(result)
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
