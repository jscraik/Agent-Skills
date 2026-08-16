"""Behavior tests for the Ask detached-HEAD attachment command."""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.commands.repo import repo_attach_detached_head  # noqa: E402


def _git(
    repo: Path,
    *args: str,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=check,
    )


def _init_repo(repo: Path) -> None:
    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.name", "Test")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "commit.gpgsign", "false")
    (repo / "README.md").write_text("init\n", encoding="utf-8")
    _git(repo, "add", "README.md")
    _git(repo, "commit", "-m", "init")


def _detach(repo: Path) -> str:
    short_sha = _git(repo, "rev-parse", "--short", "HEAD").stdout.strip()
    _git(repo, "checkout", "--detach", "HEAD")
    return short_sha


def _slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "worktree"


class TestRepoAttachDetachedHead(unittest.TestCase):
    def test_non_repository_is_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = repo_attach_detached_head(Path(tmp))
        self.assertEqual(result.status, "success")
        self.assertFalse(result.data["attached"])
        self.assertEqual(result.data["reason"], "not_in_work_tree")

    def test_named_branch_is_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _init_repo(repo)
            result = repo_attach_detached_head(repo)
        self.assertEqual(result.status, "success")
        self.assertEqual(result.data["reason"], "already_attached")
        self.assertEqual(result.data["branch"], "main")

    def test_detached_head_gets_collision_safe_branch(self) -> None:
        with tempfile.TemporaryDirectory(suffix="-Repo Name") as tmp:
            repo = Path(tmp)
            _init_repo(repo)
            short_sha = _detach(repo)
            base = f"codex/feature/{_slug(repo.name)}-worktree-{short_sha}"
            _git(repo, "branch", base)
            result = repo_attach_detached_head(repo)
            current = _git(repo, "symbolic-ref", "--short", "HEAD").stdout.strip()
        self.assertEqual(result.status, "success")
        self.assertTrue(result.data["attached"])
        self.assertEqual(current, f"{base}-1")

    def test_unreachable_origin_does_not_block_local_attachment(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _init_repo(repo)
            _git(repo, "remote", "add", "origin", str(repo / "missing-origin.git"))
            _detach(repo)
            result = repo_attach_detached_head(repo)
            current = _git(repo, "symbolic-ref", "--short", "HEAD").stdout.strip()
        self.assertEqual(result.status, "success")
        self.assertTrue(result.data["attached"])
        self.assertTrue(current.startswith("codex/feature/"))

    def test_invalid_branch_prefix_fails_without_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _init_repo(repo)
            _detach(repo)
            result = repo_attach_detached_head(repo, branch_prefix="-unsafe")
            current = _git(
                repo,
                "symbolic-ref",
                "--short",
                "-q",
                "HEAD",
                check=False,
            ).stdout.strip()
        self.assertEqual(result.status, "error")
        self.assertEqual(current, "")

    def test_new_branch_tracks_and_fast_forwards_origin_main(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            remote = root / "remote.git"
            seed = root / "seed"
            checkout = root / "checkout"
            subprocess.run(
                ["git", "init", "--bare", str(remote)], check=True, capture_output=True
            )
            seed.mkdir()
            _init_repo(seed)
            _git(seed, "remote", "add", "origin", str(remote))
            _git(seed, "push", "-u", "origin", "main")
            subprocess.run(
                ["git", "clone", "--branch", "main", str(remote), str(checkout)],
                check=True,
                capture_output=True,
            )
            _git(checkout, "config", "commit.gpgsign", "false")
            _detach(checkout)
            (seed / "update.txt").write_text("update\n", encoding="utf-8")
            _git(seed, "add", "update.txt")
            _git(seed, "commit", "-m", "update")
            _git(seed, "push", "origin", "main")
            expected_head = _git(seed, "rev-parse", "HEAD").stdout.strip()

            result = repo_attach_detached_head(checkout)
            actual_head = _git(checkout, "rev-parse", "HEAD").stdout.strip()
            upstream = _git(
                checkout, "rev-parse", "--abbrev-ref", "@{u}"
            ).stdout.strip()

        self.assertEqual(result.status, "success")
        self.assertTrue(result.data["fast_forwarded"])
        self.assertEqual(actual_head, expected_head)
        self.assertEqual(upstream, "origin/main")


if __name__ == "__main__":
    unittest.main()
