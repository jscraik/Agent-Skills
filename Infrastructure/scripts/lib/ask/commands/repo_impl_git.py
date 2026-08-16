"""Bounded Git operations exposed through the public repository command surface."""

from __future__ import annotations

import re
import shlex
import subprocess
from pathlib import Path

from ask.envelope import CallResult, ErrorCode, ErrorObject


def _run_git(repo_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo_root), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def _valid_branch_prefix(repo_root: Path, branch_prefix: str) -> bool:
    if (
        not branch_prefix
        or branch_prefix.startswith("-")
        or re.search(r"\s", branch_prefix)
    ):
        return False
    return (
        _run_git(
            repo_root, "check-ref-format", "--branch", f"{branch_prefix}/probe"
        ).returncode
        == 0
    )


def _origin_branch_exists(repo_root: Path, branch_name: str) -> bool:
    if _run_git(repo_root, "remote", "get-url", "origin").returncode != 0:
        return False
    completed = _run_git(
        repo_root, "ls-remote", "--exit-code", "--heads", "origin", branch_name
    )
    if completed.returncode in {0, 2}:
        return completed.returncode == 0
    return False


def _next_branch_name(repo_root: Path, branch_prefix: str) -> str:
    repo_slug = (
        re.sub(r"[^a-z0-9]+", "-", repo_root.name.lower()).strip("-") or "worktree"
    )
    short_sha = _run_git(repo_root, "rev-parse", "--short", "HEAD").stdout.strip()
    branch_base = f"{branch_prefix}/{repo_slug}-worktree-{short_sha}"
    branch_name = branch_base
    suffix = 1
    while _run_git(
        repo_root, "show-ref", "--verify", "--quiet", f"refs/heads/{branch_name}"
    ).returncode == 0 or _origin_branch_exists(repo_root, branch_name):
        branch_name = f"{branch_base}-{suffix}"
        suffix += 1
    return branch_name


def _fast_forward_from_main(repo_root: Path, branch_name: str) -> tuple[bool, str]:
    if (
        _run_git(
            repo_root, "show-ref", "--verify", "--quiet", "refs/remotes/origin/main"
        ).returncode
        != 0
    ):
        return False, "origin_main_unavailable"
    _run_git(repo_root, "branch", "--set-upstream-to=origin/main", branch_name)
    fetched = _run_git(repo_root, "fetch", "--quiet", "origin", "main")
    target_ref = "FETCH_HEAD" if fetched.returncode == 0 else "origin/main"
    if (
        _run_git(
            repo_root, "merge-base", "--is-ancestor", "HEAD", target_ref
        ).returncode
        != 0
    ):
        return False, "diverged_from_origin_main"
    merged = _run_git(repo_root, "merge", "--ff-only", target_ref)
    if merged.returncode != 0:
        raise RuntimeError(
            merged.stderr.strip() or "failed to fast-forward from origin/main"
        )
    return True, target_ref


def _attach_branch(repo_root: Path, branch_prefix: str) -> dict[str, object]:
    branch_name = _next_branch_name(repo_root, branch_prefix)
    switched = _run_git(repo_root, "switch", "-c", branch_name)
    if switched.returncode != 0:
        raise RuntimeError(
            switched.stderr.strip() or f"failed to create branch {branch_name}"
        )
    fast_forwarded, target = _fast_forward_from_main(repo_root, branch_name)
    return {
        "attached": True,
        "branch": branch_name,
        "fast_forwarded": fast_forwarded,
        "target": target,
    }


def repo_attach_detached_head(
    repo_root: Path, branch_prefix: str = "codex/feature"
) -> CallResult:
    """Attach a detached checkout to a collision-safe branch and fast-forward when safe."""
    result = CallResult()
    result.data["validation_commands"] = [
        "./bin/ask repo attach-detached-head --branch-prefix "
        f"{shlex.quote(branch_prefix)} --json --robot"
    ]
    if not _valid_branch_prefix(repo_root, branch_prefix):
        result.status = "error"
        result.errors.append(
            ErrorObject(
                ErrorCode.ERR_VALIDATION, f"Invalid branch prefix: {branch_prefix}"
            )
        )
        return result
    if _run_git(repo_root, "rev-parse", "--is-inside-work-tree").returncode != 0:
        result.data.update({"attached": False, "reason": "not_in_work_tree"})
        return result
    current = _run_git(
        repo_root, "symbolic-ref", "--short", "-q", "HEAD"
    ).stdout.strip()
    if current:
        result.data.update(
            {"attached": False, "reason": "already_attached", "branch": current}
        )
        return result
    try:
        result.data.update(_attach_branch(repo_root, branch_prefix))
    except RuntimeError as exc:
        result.status = "error"
        result.errors.append(ErrorObject(ErrorCode.ERR_RUNTIME, str(exc)))
        return result
    return result


__all__ = [name for name in globals() if not name.startswith("__")]
