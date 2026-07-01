#!/usr/bin/env python3
"""Validate that PR sweep closeout accounts for primary worktree dirt."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[3]
SCHEMA_VERSION = "pr-sweep-dirty-closeout-validation/v1"


@dataclass(frozen=True)
class GitDirtyState:
    staged_paths: tuple[str, ...]
    unstaged_paths: tuple[str, ...]
    untracked_paths: tuple[str, ...]

    @property
    def dirty_paths(self) -> tuple[str, ...]:
        return tuple(sorted(set(self.staged_paths + self.unstaged_paths + self.untracked_paths)))


def _run_git(repo_root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            ["/usr/bin/git", *args],
            cwd=repo_root,
            text=True,
            capture_output=True,
            check=False,
            timeout=30,
        )
    except subprocess.TimeoutExpired as exc:
        return subprocess.CompletedProcess(
            args=exc.cmd,
            returncode=-1,
            stdout=exc.stdout.decode("utf-8") if isinstance(exc.stdout, bytes) else (exc.stdout or ""),
            stderr=f"git command timed out after 30 seconds: {exc}",
        )


def _parse_porcelain_path(raw_path: str) -> tuple[str, ...]:
    if "\x00" in raw_path:
        paths = tuple(path for path in raw_path.split("\x00") if path)
        return paths or ("",)
    if " -> " in raw_path:
        before, after = raw_path.split(" -> ", 1)
        return (before, after)
    return (raw_path,)


def parse_porcelain(output: str) -> GitDirtyState:
    staged: set[str] = set()
    unstaged: set[str] = set()
    untracked: set[str] = set()
    records = output.split("\x00") if "\x00" in output else output.splitlines()
    index = 0
    while index < len(records):
        line = records[index]
        index += 1
        if not line:
            continue
        status = line[:2]
        path_part = line[3:]
        if "\x00" in output and status.strip() in {"R", "C"} and index < len(records):
            path_part = f"{path_part}\x00{records[index]}"
            index += 1
        paths = _parse_porcelain_path(path_part)
        if status == "??":
            untracked.update(paths)
            continue
        if status[0] != " ":
            staged.update(paths)
        if status[1] != " ":
            unstaged.update(paths)
    return GitDirtyState(
        staged_paths=tuple(sorted(staged)),
        unstaged_paths=tuple(sorted(unstaged)),
        untracked_paths=tuple(sorted(untracked)),
    )


def git_dirty_state(repo_root: Path) -> tuple[GitDirtyState | None, str | None]:
    result = _run_git(repo_root, ["status", "--porcelain=v1", "-z", "--untracked-files=all"])
    if result.returncode != 0:
        return None, (result.stderr or result.stdout or "git status failed").strip()
    return parse_porcelain(result.stdout), None


def _collect_path_strings(value: Any) -> set[str]:
    paths: set[str] = set()
    if isinstance(value, str):
        if "/" in value or value.startswith("."):
            paths.add(value)
    elif isinstance(value, list):
        for item in value:
            paths.update(_collect_path_strings(item))
    elif isinstance(value, dict):
        for key, item in value.items():
            if key in {"path", "file", "files", "paths", "changed_files", "dirty_paths", "ledgered_paths"}:
                paths.update(_collect_recognized_paths(item))
            elif isinstance(item, (dict, list)):
                paths.update(_collect_path_strings(item))
    return paths


def _collect_recognized_paths(item: Any) -> set[str]:
    """Collect strings nested under a recognized ledger key without the bare-string heuristic."""
    if isinstance(item, str) and item:
        return {item}
    if isinstance(item, list):
        collected: set[str] = set()
        for entry in item:
            collected.update(_collect_recognized_paths(entry))
        return collected
    if isinstance(item, dict):
        return _collect_path_strings(item)
    return set()

def read_ledger_paths(ledger_path: Path | None) -> tuple[set[str], str | None]:
    if ledger_path is None:
        return set(), None
    try:
        payload = json.loads(ledger_path.read_text(encoding="utf-8"))
    except OSError as exc:
        return set(), f"could not read ledger: {exc}"
    except json.JSONDecodeError as exc:
        return set(), f"ledger is not valid JSON: {exc}"
    return _collect_path_strings(payload), None


def _dirty_state_payload(state: GitDirtyState) -> dict[str, list[str]]:
    return {
        "staged_paths": list(state.staged_paths),
        "unstaged_paths": list(state.unstaged_paths),
        "untracked_paths": list(state.untracked_paths),
        "dirty_paths": list(state.dirty_paths),
    }


def _payload(
    repo_root: Path,
    *,
    ledger_path: Path | None,
    dirty_state: GitDirtyState | None,
    ledger_paths: set[str],
    unledgered_paths: list[str],
    findings: list[dict[str, Any]],
    status: str | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": status or ("pass" if not findings else "fail"),
        "repo_root": str(repo_root),
        "ledger_path": str(ledger_path) if ledger_path else None,
        "dirty_state": _dirty_state_payload(dirty_state) if dirty_state else None,
        "ledgered_paths": sorted(ledger_paths),
        "unledgered_paths": unledgered_paths,
        "findings": findings,
    }


def _git_status_finding(git_error: str) -> dict[str, Any]:
    return {
        "code": "git_status_unavailable",
        "message": "Unable to inspect primary worktree dirty state.",
        "path": ".",
        "detail": git_error,
    }


def _ledger_error_finding(ledger_path: Path | None, ledger_error: str) -> dict[str, Any]:
    return {
        "code": "ledger_unreadable",
        "message": "Dirty worktree ledger could not be read.",
        "path": str(ledger_path) if ledger_path else None,
        "detail": ledger_error,
    }


def _dirty_findings(
    *,
    dirty_paths: set[str],
    ledger_path: Path | None,
    unledgered_paths: list[str],
    require_clean: bool,
) -> list[dict[str, Any]]:
    if require_clean and dirty_paths:
        return [
            {
                "code": "primary_worktree_dirty",
                "message": "Primary worktree has dirty paths; branch movement requires a clean checkout.",
                "path": ".",
                "dirty_count": len(dirty_paths),
            }
        ]
    if dirty_paths and ledger_path is None:
        return [
            {
                "code": "dirty_worktree_ledger_required",
                "message": "Primary worktree has dirty paths but no dirty-worktree ledger was supplied.",
                "path": ".",
                "dirty_count": len(dirty_paths),
            }
        ]
    if unledgered_paths:
        return [
            {
                "code": "dirty_worktree_unledgered_paths",
                "message": "Primary worktree has dirty paths missing from the closeout ledger.",
                "path": ".",
                "unledgered_count": len(unledgered_paths),
            }
        ]
    return []


def validate(repo_root: Path, *, ledger_path: Path | None = None, require_clean: bool = False) -> dict[str, Any]:
    state, git_error = git_dirty_state(repo_root)
    ledger_paths, ledger_error = read_ledger_paths(ledger_path)
    findings: list[dict[str, Any]] = []

    if git_error is not None:
        findings.append(_git_status_finding(git_error))
        return _payload(
            repo_root,
            ledger_path=ledger_path,
            dirty_state=None,
            ledger_paths=ledger_paths,
            unledgered_paths=[],
            findings=findings,
            status="blocked",
        )

    if ledger_error is not None:
        findings.append(_ledger_error_finding(ledger_path, ledger_error))

    assert state is not None
    dirty_paths = set(state.dirty_paths)
    unledgered_paths = sorted(dirty_paths - ledger_paths)
    findings.extend(
        _dirty_findings(
            dirty_paths=dirty_paths,
            ledger_path=ledger_path,
            unledgered_paths=unledgered_paths,
            require_clean=require_clean,
        )
    )
    return _payload(
        repo_root,
        ledger_path=ledger_path,
        dirty_state=state,
        ledger_paths=ledger_paths,
        unledgered_paths=unledgered_paths,
        findings=findings,
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--ledger", type=Path, default=None)
    parser.add_argument(
        "--require-clean",
        action="store_true",
        help="Fail on any dirty path even when it is represented in the ledger.",
    )
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = _parser().parse_args(list(argv) if argv is not None else None)
    payload = validate(args.repo_root, ledger_path=args.ledger, require_clean=args.require_clean)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(payload["status"])
        for finding in payload["findings"]:
            print(f"{finding['code']}: {finding['message']}")
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
