#!/usr/bin/env python3
"""Behavior tests for .codex/environments/detach-head-helper.sh."""

from __future__ import annotations

import os
import re
import shlex
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
HELPER_PATH = REPO_ROOT / ".codex/environments/detach-head-helper.sh"
HELPER_SNIPPET = "\n".join(
    [
        "set -euo pipefail",
        f"source {shlex.quote(str(HELPER_PATH))}",
        "codex_attach_detached_head",
    ]
)


def _run_snippet(snippet: str, cwd: Path, extra_env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env.setdefault("GIT_AUTHOR_NAME", "Test")
    env.setdefault("GIT_AUTHOR_EMAIL", "test@example.com")
    env.setdefault("GIT_COMMITTER_NAME", "Test")
    env.setdefault("GIT_COMMITTER_EMAIL", "test@example.com")
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        ["/bin/bash", "-c", snippet],
        cwd=str(cwd),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def _run_git(repo: Path, *args: str, check: bool = True, text: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=text,
        check=check,
    )


def _init_repo(repo: Path, branch: str = "main") -> None:
    _run_git(repo, "init", "-b", branch)
    _run_git(repo, "config", "user.email", "test@example.com")
    _run_git(repo, "config", "user.name", "Test")
    (repo / "README.md").write_text("init\n", encoding="utf-8")
    _run_git(repo, "add", ".")
    _run_git(repo, "commit", "-m", "init")


def _detach_head(repo: Path) -> str:
    short_sha = _run_git(repo, "rev-parse", "--short", "HEAD").stdout.strip()
    _run_git(repo, "checkout", "--detach", "HEAD")
    return short_sha


def _current_branch(repo: Path) -> str:
    return _run_git(repo, "symbolic-ref", "--short", "-q", "HEAD", check=False).stdout.strip()


def _repo_slug(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or "worktree"


class TestDetachHeadHelperContract(unittest.TestCase):
    def test_helper_exists(self) -> None:
        self.assertTrue(HELPER_PATH.exists(), f"Missing helper script: {HELPER_PATH}")


class TestDetachHeadHelperBehavior(unittest.TestCase):
    def test_noop_outside_git_repo(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = _run_snippet(HELPER_SNIPPET, Path(tmp))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn("[codex]", result.stdout)

    def test_noop_when_git_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as empty_path:
            repo = Path(tmp)
            _init_repo(repo)
            _detach_head(repo)
            result = _run_snippet(HELPER_SNIPPET, repo, extra_env={"PATH": empty_path})
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn("[codex]", result.stdout)

    def test_noop_on_named_branch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _init_repo(repo)
            result = _run_snippet(HELPER_SNIPPET, repo)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn("[codex]", result.stdout)
            self.assertEqual(_current_branch(repo), "main")

    def test_creates_branch_for_detached_head(self) -> None:
        with tempfile.TemporaryDirectory(suffix="-My Repo") as tmp:
            repo = Path(tmp)
            _init_repo(repo)
            short_sha = _detach_head(repo)
            result = _run_snippet(HELPER_SNIPPET, repo)
            self.assertEqual(result.returncode, 0, result.stderr)
            branch = _current_branch(repo)
            self.assertEqual(branch, f"codex/{_repo_slug(repo.name)}-worktree-{short_sha}")
            self.assertIn("[codex] detached HEAD detected", result.stdout)

    def test_appends_suffix_on_collision(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _init_repo(repo)
            short_sha = _detach_head(repo)
            base_branch = f"codex/{_repo_slug(repo.name)}-worktree-{short_sha}"
            _run_git(repo, "branch", base_branch)
            result = _run_snippet(HELPER_SNIPPET, repo)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(_current_branch(repo), f"{base_branch}-1")

    def test_leading_hyphen_slug_is_stripped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            repo = parent / "__repo"
            repo.mkdir(parents=True)
            _init_repo(repo)
            short_sha = _detach_head(repo)
            result = _run_snippet(HELPER_SNIPPET, repo)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(_current_branch(repo), f"codex/repo-worktree-{short_sha}")

    def test_tracks_origin_main_if_available(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            remote = root / "remote.git"
            seed = root / "seed"
            clone = root / "clone"
            seed.mkdir(parents=True)

            subprocess.run(["git", "init", "--bare", str(remote)], check=True, capture_output=True)
            _init_repo(seed)
            _run_git(seed, "remote", "add", "origin", str(remote))
            _run_git(seed, "push", "-u", "origin", "main")
            subprocess.run(
                ["git", "clone", "--branch", "main", str(remote), str(clone)],
                check=True,
                capture_output=True,
            )

            _detach_head(clone)

            # Create a new commit on seed and push to origin/main
            (seed / "update.txt").write_text("update\n", encoding="utf-8")
            _run_git(seed, "add", ".")
            _run_git(seed, "commit", "-m", "update")
            _run_git(seed, "push", "origin", "main")

            # Get the new commit hash from seed
            new_commit = _run_git(seed, "rev-parse", "HEAD").stdout.strip()

            result = _run_snippet(HELPER_SNIPPET, clone)
            self.assertEqual(result.returncode, 0, result.stderr)
            upstream = _run_git(clone, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}")
            self.assertEqual(upstream.stdout.strip(), "origin/main")

            # Assert that fast-forward happened
            main_commit = _run_git(clone, "rev-parse", "main").stdout.strip()
            self.assertEqual(main_commit, new_commit)

            self.assertIn("[codex] tracking origin/main", result.stdout)
            self.assertIn("[codex] fast-forwarding", result.stdout)

    def test_skips_tracking_without_origin_main(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _init_repo(repo)
            _detach_head(repo)
            result = _run_snippet(HELPER_SNIPPET, repo)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn("[codex] tracking origin/main", result.stdout)


if __name__ == "__main__":
    unittest.main()