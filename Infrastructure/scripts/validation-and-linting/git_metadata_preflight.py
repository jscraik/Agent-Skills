#!/usr/bin/env python3
"""Fail-closed Git metadata preflight for ordinary and linked worktrees.

This is the shared ``git-metadata-preflight/v1`` leaf adapter.  It checks the
metadata directories that Git must write before a hook spends time on source
validation.  It reports stale or active locks but never removes them.
"""

from __future__ import annotations

import argparse
from enum import Enum
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
SUBPROCESS_TIMEOUT_SECONDS = 5
GIT_CONTEXT_ENV_VARS = frozenset({
    "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    "GIT_COMMON_DIR",
    "GIT_DIR",
    "GIT_INDEX_FILE",
    "GIT_OBJECT_DIRECTORY",
    "GIT_WORK_TREE",
})


class CurrentIndexLockPolicy(Enum):
    STRICT = "strict"
    ALLOW_PARENT_OWNED = "allow_parent_owned"


class UsageError(ValueError):
    """Raised for invalid command-line input."""


class UsageArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise UsageError(message)


def _run_git(repo_root: Path, *args: str) -> tuple[int, str, str]:
    env = os.environ.copy()
    for name in GIT_CONTEXT_ENV_VARS:
        env.pop(name, None)
    git_binary = shutil.which("git") or "git"
    try:
        proc = subprocess.run(
            [git_binary, *args], cwd=repo_root, env=env, text=True,
            capture_output=True, check=False, timeout=SUBPROCESS_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        return 124, "", f"git {' '.join(args)} timed out after {SUBPROCESS_TIMEOUT_SECONDS}s"
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def _resolve_git_path(repo_root: Path, value: str, *, preserve_leaf: bool = False) -> Path:
    path = Path(value)
    path = path if path.is_absolute() else repo_root / path
    if preserve_leaf:
        return path.parent.resolve() / path.name
    return path.resolve()


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


def _lsof_binary() -> str | None:
    discovered = shutil.which("lsof")
    if discovered:
        return discovered
    for candidate in (Path("/usr/sbin/lsof"), Path("/usr/bin/lsof")):
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
    return None


def _lock_owner(path: Path) -> str | None:
    lsof = _lsof_binary()
    if lsof is None:
        return None
    try:
        proc = subprocess.run(
            [lsof, "-nP", "--", str(path)],
            text=True, capture_output=True, check=False,
            timeout=SUBPROCESS_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if proc.returncode != 0:
        return None
    lines = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    return " | ".join(lines[:4]) if lines else None


def _lock_owner_pids(path: Path) -> set[int] | None:
    lsof = _lsof_binary()
    if lsof is None:
        return None
    try:
        proc = subprocess.run(
            [lsof, "-nP", "-t", "--", str(path)],
            text=True, capture_output=True, check=False,
            timeout=SUBPROCESS_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    pids: set[int] = set()
    for line in proc.stdout.splitlines():
        try:
            pids.add(int(line.strip()))
        except ValueError:
            continue
    return pids


def _lsof_parent_pid(pid: int) -> int | None:
    lsof = _lsof_binary()
    if lsof is None:
        return None
    try:
        proc = subprocess.run(
            [lsof, "-nP", "-F", "pR", "-R", "-p", str(pid)],
            text=True, capture_output=True, check=False,
            timeout=SUBPROCESS_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    for line in proc.stdout.splitlines():
        if line.startswith("R"):
            try:
                return int(line[1:])
            except ValueError:
                return None
    return None


def _parent_process_ids() -> set[int]:
    ancestors: set[int] = set()
    pid = os.getppid()
    while pid > 1 and pid not in ancestors:
        ancestors.add(pid)
        lsof_parent_pid = _lsof_parent_pid(pid)
        if lsof_parent_pid is not None:
            pid = lsof_parent_pid
            continue
        try:
            proc = subprocess.run(
                ["ps", "-o", "ppid=", "-p", str(pid)],
                text=True, capture_output=True, check=False,
                timeout=SUBPROCESS_TIMEOUT_SECONDS,
            )
            pid = int(proc.stdout.strip())
        except (OSError, ValueError, subprocess.TimeoutExpired):
            break
    return ancestors


def _has_expected_git_hook_transaction(git_dir: Path) -> bool:
    raw_git_dir = os.environ.get("GIT_DIR")
    raw_index_file = os.environ.get("GIT_INDEX_FILE")
    if not raw_git_dir or not raw_index_file:
        return False
    try:
        expected_dir = git_dir.resolve()
        hook_dir = Path(raw_git_dir).resolve()
        temporary_index = Path(raw_index_file).resolve()
    except OSError:
        return False
    return (
        hook_dir == expected_dir
        and temporary_index.parent == expected_dir
        and temporary_index.name.startswith("next-index-")
        and temporary_index.suffix == ".lock"
        and temporary_index.is_file()
    )


def _lock_owned_by_parent(path: Path) -> bool:
    owner_pids = _lock_owner_pids(path)
    return owner_pids is not None and bool(owner_pids & _parent_process_ids())


def _classify_lock(path: Path, max_age_seconds: int, kind: str) -> dict[str, Any]:
    prefix = "index" if kind == "index" else "git_metadata"
    if not path.is_file():
        return {
            "path": str(path),
            "classification": f"{prefix}_lock_non_regular",
        }
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
        classification = f"active_{prefix}_lock"
    elif age_seconds >= max_age_seconds:
        classification = f"stale_{prefix}_lock_candidate"
    else:
        classification = f"recent_{prefix}_lock_unknown"

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
        "head_lock_path": ("rev-parse", "--git-path", "HEAD.lock"),
        "objects_dir": ("rev-parse", "--git-path", "objects"),
    }
    resolved: dict[str, Path] = {}
    for key, args in commands.items():
        code, value, stderr = _run_git(repo_root, *args)
        if code != 0 or not value:
            raise MetadataPreflightError(stderr or f"git {' '.join(args)} failed")
        resolved[key] = _resolve_git_path(
            repo_root,
            value,
            preserve_leaf=key.endswith("_lock_path"),
        )
    resolved.update(_resolve_head_metadata(repo_root))
    return resolved


def _resolve_head_metadata(repo_root: Path) -> dict[str, Path]:
    code, head_ref, _ = _run_git(repo_root, "symbolic-ref", "-q", "HEAD")
    resolved: dict[str, Path] = {}
    if code == 0 and head_ref:
        code, value, stderr = _run_git(repo_root, "rev-parse", "--git-path", f"{head_ref}.lock")
        if code != 0 or not value:
            raise MetadataPreflightError(stderr or "git could not resolve the current ref lock")
        resolved["ref_lock_path"] = _resolve_git_path(
            repo_root, value, preserve_leaf=True
        )
        code, value, stderr = _run_git(
            repo_root, "rev-parse", "--git-path", f"logs/{head_ref}"
        )
        if code != 0 or not value:
            raise MetadataPreflightError(stderr or "git could not resolve the current reflog")
        resolved["ref_log_path"] = _resolve_git_path(
            repo_root, value, preserve_leaf=True
        )
    else:
        code, value, stderr = _run_git(repo_root, "rev-parse", "--git-path", "logs/HEAD")
        if code != 0 or not value:
            raise MetadataPreflightError(stderr or "git could not resolve the detached HEAD reflog")
        resolved["ref_log_path"] = _resolve_git_path(
            repo_root, value, preserve_leaf=True
        )
    return resolved


def _write_probes(metadata_dirs: list[Path], probe_write: bool) -> list[dict[str, Any]]:
    if probe_write:
        return [_probe_write(path) for path in metadata_dirs]
    return [
        {"path": str(path), "status": "blocked", "reason": "write_probe_disabled"}
        for path in metadata_dirs
    ]


def _metadata_dirs(
    resolved: dict[str, Path], git_dir: Path, common_dir: Path
) -> list[Path]:
    paths = [resolved["index_path"].parent, resolved["objects_dir"], git_dir, common_dir]
    ref_lock_path = resolved.get("ref_lock_path")
    if ref_lock_path is not None:
        paths.append(_nearest_existing_directory(ref_lock_path.parent))
    ref_log_path = resolved.get("ref_log_path")
    if ref_log_path is not None:
        paths.append(_nearest_existing_directory(ref_log_path.parent))
    return _unique_paths(paths)


def _non_directory_path_components(paths: list[Path]) -> list[str]:
    blocked: list[str] = []
    for path in paths:
        candidate = path
        while not candidate.exists() and candidate.parent != candidate:
            candidate = candidate.parent
        if candidate.exists() and not candidate.is_dir():
            blocked.append(str(candidate))
    return list(dict.fromkeys(blocked))


def _nearest_existing_directory(path: Path) -> Path:
    """Return the deepest existing parent Git can use for a packed ref."""
    candidate = path
    while not candidate.is_dir():
        parent = candidate.parent
        if parent == candidate:
            return candidate
        candidate = parent
    return candidate


def _lock_records(
    index_lock_path: Path,
    head_lock_path: Path,
    ref_lock_path: Path | None,
    lock_max_age_seconds: int,
) -> list[dict[str, Any]]:
    candidates = [("index", index_lock_path), ("head", head_lock_path)]
    if ref_lock_path is not None:
        candidates.append(("current_ref", ref_lock_path))
    records: list[dict[str, Any]] = []
    for kind, path in candidates:
        if not (path.exists() or path.is_symlink()):
            continue
        record = _classify_lock(path, lock_max_age_seconds, kind)
        record["kind"] = kind
        records.append(record)
    return records


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
        for index_lock in sorted(worktrees_dir.glob("*/index.lock")):
            locked.append(
                {
                    "metadata_dir": str(index_lock.parent.resolve()),
                    "reason": "index.lock exists",
                    "current": index_lock.parent.resolve() == git_dir,
                    "index_lock": str(index_lock),
                }
            )
    code, output, stderr = _run_git(repo_root, "worktree", "list", "--porcelain")
    prunable = [
        record
        for record in _parse_worktree_records(output)
        if "prunable_reason" in record
    ] if code == 0 else []
    return locked, prunable, stderr if code != 0 else None


def _apply_worktree_state(
    result: dict[str, Any], repo_root: Path, worktrees_dir: Path, git_dir: Path
) -> str | None:
    locked, prunable, error = _worktree_state(repo_root, worktrees_dir, git_dir)
    result.update(locked_worktrees=locked, prunable_worktrees=prunable)
    if error:
        result["worktree_list_diagnostic"] = error
    return error


def _metadata_reasons(write_results: list[dict[str, Any]]) -> list[str]:
    reasons: list[str] = []
    if any(item.get("reason") == "path_missing" for item in write_results):
        reasons.append("metadata_path_missing")
    if any(item.get("reason") in {"write_denied", "cleanup_denied"} for item in write_results):
        reasons.append("metadata_write_denied")
    if any(item.get("reason") == "write_probe_disabled" for item in write_results):
        reasons.append("metadata_write_probe_disabled")
    if any(item.get("reason") == "path_component_not_directory" for item in write_results):
        reasons.append("metadata_path_component_not_directory")
    return reasons


def _lock_reasons(
    result: dict[str, Any],
    lock_records: list[dict[str, Any]],
    index_lock_path: Path,
    allow_current_index_lock: bool,
    expected_hook_transaction: bool,
) -> tuple[list[str], list[str]]:
    reasons: list[str] = []
    advisories: list[str] = []
    if any(item.get("classification") == "lock_stat_failed" for item in lock_records):
        reasons.append("metadata_lock_uninspectable")
    for record in lock_records:
        path = Path(str(record.get("path", "")))
        classification = str(record.get("classification", "index_lock"))
        is_current = path == index_lock_path
        if is_current and allow_current_index_lock:
            owner_pids = _lock_owner_pids(index_lock_path)
            if expected_hook_transaction or (
                owner_pids is not None and owner_pids & _parent_process_ids()
            ):
                advisories.append("expected_current_index_lock")
            elif owner_pids is None:
                reasons.append("lock_owner_detector_unavailable")
            else:
                reasons.append(classification)
        else:
            reasons.append(classification)
    reasons.extend(
        _worktree_lock_reasons(
            result["locked_worktrees"],
            index_lock_path=index_lock_path,
            allow_current_index_lock=allow_current_index_lock,
        )
    )
    if result["prunable_worktrees"]:
        advisories.append("prunable_worktree")
    return list(dict.fromkeys(reasons)), advisories


def _worktree_lock_reasons(
    locked_worktrees: list[dict[str, Any]],
    *,
    index_lock_path: Path,
    allow_current_index_lock: bool,
) -> list[str]:
    reasons: list[str] = []
    has_blocking_current_worktree_lock = any(
        item.get("current")
        and (
            not allow_current_index_lock
            or item.get("index_lock") != str(index_lock_path)
        )
        for item in locked_worktrees
    )
    if has_blocking_current_worktree_lock:
        reasons.append("current_worktree_locked")
    if any(not item.get("current") for item in locked_worktrees):
        reasons.append("related_worktree_locked")
    return reasons


def _reason_codes(
    result: dict[str, Any],
    write_results: list[dict[str, Any]],
    lock_records: list[dict[str, Any]],
    index_lock_path: Path,
    allow_current_index_lock: bool,
    expected_hook_transaction: bool,
) -> tuple[list[str], list[str]]:
    reasons = _metadata_reasons(write_results)
    lock_reasons, advisories = _lock_reasons(
        result, lock_records, index_lock_path, allow_current_index_lock,
        expected_hook_transaction,
    )
    reasons.extend(lock_reasons)
    return list(dict.fromkeys(reasons)), advisories


def _next_action(reasons: list[str]) -> str:
    if not reasons:
        return "Git metadata is writable and no current-worktree lock blocks the hook"
    if any(reason.startswith(("active_", "recent_")) for reason in reasons):
        return "wait for the lock owner or stop the owning process; do not delete the lock"
    if any(reason.startswith("stale_") for reason in reasons):
        return "prove no owner, then use explicit Git worktree recovery; this preflight never removes locks"
    if "metadata_write_denied" in reasons:
        return "grant write access to the exact Git metadata directories or use a writable checkout"
    return "repair Git metadata authority before running the hook again"


def _finalize(
    result: dict[str, Any],
    write_results: list[dict[str, Any]],
    lock_records: list[dict[str, Any]],
    index_lock_path: Path,
    allow_current_index_lock: bool,
    expected_hook_transaction: bool,
) -> None:
    reasons, advisories = _reason_codes(
        result, write_results, lock_records, index_lock_path, allow_current_index_lock,
        expected_hook_transaction,
    )
    if advisories:
        result.setdefault("advisories", []).extend(advisories)
    result["reason_codes"] = reasons
    result["status"] = "blocked" if reasons else "pass"
    result["next_action"] = _next_action(reasons)


def _finalize_inspection(
    result: dict[str, Any],
    write_results: list[dict[str, Any]],
    index_lock_path: Path,
    lock_policy: CurrentIndexLockPolicy,
    worktree_error: str | None,
    expected_hook_transaction: bool,
) -> None:
    _finalize(
        result,
        write_results,
        result["locks"],
        index_lock_path,
        lock_policy is CurrentIndexLockPolicy.ALLOW_PARENT_OWNED,
        expected_hook_transaction,
    )
    if worktree_error:
        result["reason_codes"] = list(
            dict.fromkeys([*result["reason_codes"], "worktree_state_unavailable"])
        )
        result["status"] = "blocked"
        result["next_action"] = _next_action(result["reason_codes"])


def _initial_result(repo_root: Path) -> dict[str, Any]:
    return {
        "schema_version": 1, "contract": CONTRACT, "status": "blocked",
        "repo_root": str(repo_root.resolve()), "reason_codes": [],
        "locks": [], "locked_worktrees": [], "prunable_worktrees": [],
    }


def _prepare_metadata_inspection(
    result: dict[str, Any], resolved: dict[str, Path], probe_write: bool
) -> tuple[list[dict[str, Any]], Path, Path]:
    common_dir, git_dir = resolved["git_common_dir"], resolved["git_dir"]
    result.update({key: str(path) for key, path in resolved.items()})
    result.update(
        worktrees_dir=str(common_dir / "worktrees"),
        linked_worktree=git_dir != common_dir,
    )
    metadata_dirs = _metadata_dirs(resolved, git_dir, common_dir)
    result["metadata_dirs"] = [str(path) for path in metadata_dirs]
    write_results = _write_probes(metadata_dirs, probe_write)
    invalid_components = _non_directory_path_components([
        resolved["index_path"].parent,
        resolved["objects_dir"],
        resolved.get("ref_lock_path", common_dir).parent,
        resolved.get("ref_log_path", common_dir).parent,
    ])
    if invalid_components:
        result["non_directory_path_components"] = invalid_components
        write_results.append({
            "path": invalid_components[0], "status": "blocked",
            "reason": "path_component_not_directory",
        })
    return write_results, common_dir, git_dir


def inspect(
    repo_root: Path,
    probe_write: bool,
    lock_max_age_seconds: int,
    current_index_lock_policy: CurrentIndexLockPolicy = CurrentIndexLockPolicy.STRICT,
) -> dict[str, Any]:
    result = _initial_result(repo_root)
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
    write_results, common_dir, git_dir = _prepare_metadata_inspection(
        result, resolved, probe_write
    )
    worktrees_dir = common_dir / "worktrees"
    result["write_probe"] = write_results
    result["locks"] = _lock_records(
        resolved["index_lock_path"],
        resolved["head_lock_path"],
        resolved.get("ref_lock_path"),
        lock_max_age_seconds,
    )
    worktree_error = _apply_worktree_state(result, repo_root, worktrees_dir, git_dir)
    expected_hook_transaction = _has_expected_git_hook_transaction(git_dir)
    result["expected_hook_transaction"] = expected_hook_transaction
    _finalize_inspection(
        result, write_results, resolved["index_lock_path"], current_index_lock_policy,
        worktree_error, expected_hook_transaction,
    )
    return result


def parse_args() -> argparse.Namespace:
    raw_lock_age = os.environ.get(
        "GIT_METADATA_PREFLIGHT_LOCK_MAX_AGE_SECONDS",
        str(DEFAULT_LOCK_MAX_AGE_SECONDS),
    )
    try:
        default_lock_age = int(raw_lock_age)
    except (TypeError, ValueError) as exc:
        raise UsageError(
            "GIT_METADATA_PREFLIGHT_LOCK_MAX_AGE_SECONDS must be an integer"
        ) from exc
    parser = UsageArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    parser.add_argument("--no-write-probe", action="store_true")
    parser.add_argument(
        "--allow-parent-owned-index-lock",
        "--allow-current-index-lock",
        dest="allow_parent_owned_index_lock",
        action="store_true",
        help="treat index.lock as expected only when its owner is a Git ancestor (pre-commit only)",
    )
    parser.add_argument(
        "--lock-max-age-seconds",
        type=int,
        default=default_lock_age,
    )
    return parser.parse_args()


def main() -> int:
    try:
        args = parse_args()
        if args.lock_max_age_seconds < 0:
            raise UsageError("--lock-max-age-seconds must be non-negative")
        payload = inspect(
            args.repo_root,
            probe_write=not args.no_write_probe,
            lock_max_age_seconds=args.lock_max_age_seconds,
            current_index_lock_policy=(
                CurrentIndexLockPolicy.ALLOW_PARENT_OWNED
                if args.allow_parent_owned_index_lock
                else CurrentIndexLockPolicy.STRICT
            ),
        )
    except UsageError as exc:
        print(json.dumps({"schema_version": 1, "contract": CONTRACT, "status": "blocked", "reason_codes": ["invalid_usage"], "diagnostic": str(exc)}, sort_keys=True))
        return EXIT_USAGE
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
