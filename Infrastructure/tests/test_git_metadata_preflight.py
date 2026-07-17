#!/usr/bin/env python3
"""Regression tests for the git-metadata-preflight/v1 adapter."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "validation-and-linting"
    / "git_metadata_preflight.py"
)


def lsof_available() -> bool:
    return shutil.which("lsof") is not None or Path("/usr/sbin/lsof").is_file()


def git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.update(
        {
            "GIT_AUTHOR_NAME": "preflight-test",
            "GIT_AUTHOR_EMAIL": "preflight-test@example.invalid",
            "GIT_COMMITTER_NAME": "preflight-test",
            "GIT_COMMITTER_EMAIL": "preflight-test@example.invalid",
        }
    )
    return subprocess.run(
        ["git", *args], cwd=repo, env=env, text=True, capture_output=True, check=False
    )


def make_repo(root: Path) -> Path:
    repo = root / "repo"
    repo.mkdir()
    assert git(repo, "init", "-q").returncode == 0
    (repo / "README.md").write_text("preflight\n", encoding="utf-8")
    assert git(repo, "add", "README.md").returncode == 0
    assert git(repo, "commit", "-qm", "initial").returncode == 0
    return repo


def run_preflight(repo: Path, **env_overrides: str) -> tuple[int, dict[str, object]]:
    env = os.environ.copy()
    env.update(env_overrides)
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--repo-root", str(repo), "--json"],
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    return proc.returncode, json.loads(proc.stdout)


class GitMetadataPreflightTests(unittest.TestCase):
    def test_clean_checkout_passes_and_reports_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = make_repo(Path(temp_dir))
            code, payload = run_preflight(repo)

            self.assertEqual(code, 0, payload)
            self.assertEqual(payload["contract"], "git-metadata-preflight/v1")
            self.assertEqual(payload["status"], "pass")
            self.assertTrue(payload["write_probe"])

    def test_inherited_git_context_does_not_override_repo_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = make_repo(root)
            poison = root / "poison"
            poison.mkdir()
            code, payload = run_preflight(
                repo,
                GIT_DIR=str(poison),
                GIT_WORK_TREE=str(poison),
                GIT_INDEX_FILE=str(poison / "index"),
            )

            self.assertEqual(code, 0, payload)
            self.assertEqual(Path(str(payload["repo_root"])), repo.resolve())

    def test_current_index_lock_blocks_without_cleanup(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = make_repo(Path(temp_dir))
            _, clean = run_preflight(repo)
            lock_path = Path(str(clean["index_lock_path"]))
            lock_path.touch()
            code, payload = run_preflight(
                repo, GIT_METADATA_PREFLIGHT_LOCK_MAX_AGE_SECONDS="0"
            )

            self.assertEqual(code, 78, payload)
            self.assertEqual(payload["status"], "blocked")
            self.assertIn("stale_index_lock_candidate", payload["reason_codes"])
            self.assertTrue(lock_path.exists(), "preflight must never remove locks")

    def test_unowned_current_index_lock_is_not_waived_for_pre_commit(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = make_repo(Path(temp_dir))
            _, clean = run_preflight(repo)
            lock_path = Path(str(clean["index_lock_path"]))
            lock_path.touch()
            code, payload = run_preflight(
                repo,
                GIT_METADATA_PREFLIGHT_LOCK_MAX_AGE_SECONDS="0",
            )

            self.assertEqual(code, 78, payload)
            self.assertIn("stale_index_lock_candidate", payload["reason_codes"])

            allowed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--repo-root",
                    str(repo),
                    "--allow-current-index-lock",
                    "--json",
                ],
                env={**os.environ, "GIT_METADATA_PREFLIGHT_LOCK_MAX_AGE_SECONDS": "0"},
                text=True,
                capture_output=True,
                check=False,
            )
            allowed_payload = json.loads(allowed.stdout)
            self.assertEqual(allowed.returncode, 78, allowed_payload)
            expected_reason = (
                "stale_index_lock_candidate"
                if lsof_available()
                else "lock_owner_detector_unavailable"
            )
            self.assertIn(expected_reason, allowed_payload["reason_codes"])
            self.assertTrue(lock_path.exists(), "preflight must never remove locks")

    def test_owned_current_index_lock_is_advisory_for_pre_commit(self) -> None:
        if not lsof_available():
            self.skipTest("lsof is required to prove parent lock ownership")
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = make_repo(Path(temp_dir))
            _, clean = run_preflight(repo)
            lock_path = Path(str(clean["index_lock_path"]))
            with lock_path.open("w", encoding="utf-8"):
                owned = subprocess.run(
                    [
                        sys.executable,
                        str(SCRIPT),
                        "--repo-root",
                        str(repo),
                        "--allow-current-index-lock",
                        "--json",
                    ],
                    env={
                        **os.environ,
                        "GIT_METADATA_PREFLIGHT_LOCK_MAX_AGE_SECONDS": "0",
                    },
                    text=True,
                    capture_output=True,
                    check=False,
                )
            owned_payload = json.loads(owned.stdout)
            self.assertEqual(owned.returncode, 0, owned_payload)
            self.assertIn("expected_current_index_lock", owned_payload["advisories"])

    def test_non_regular_index_lock_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = make_repo(Path(temp_dir))
            _, clean = run_preflight(repo)
            lock_path = Path(str(clean["index_lock_path"]))
            lock_path.mkdir()
            code, payload = run_preflight(repo)
            self.assertEqual(code, 78, payload)
            self.assertIn("index_lock_non_regular", payload["reason_codes"])

    def test_linked_worktree_and_locked_metadata_are_visible(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = make_repo(root)
            linked = root / "linked"
            created = git(repo, "worktree", "add", "-q", str(linked), "-b", "linked")
            self.assertEqual(created.returncode, 0, created.stderr)
            code, payload = run_preflight(linked)
            self.assertEqual(code, 0, payload)
            self.assertTrue(payload["linked_worktree"])
            self.assertIn("/worktrees/", str(payload["index_path"]))

            locked = git(repo, "worktree", "lock", "--reason", "initializing", str(linked))
            self.assertEqual(locked.returncode, 0, locked.stderr)
            code, payload = run_preflight(linked)
            self.assertEqual(code, 0, payload)
            self.assertIn("locked_worktree", payload["advisories"])

    def test_lock_in_other_worktree_does_not_block_current_worktree(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = make_repo(root)
            linked = root / "linked"
            created = git(repo, "worktree", "add", "-q", str(linked), "-b", "linked")
            self.assertEqual(created.returncode, 0, created.stderr)
            _, linked_payload = run_preflight(linked)
            linked_lock = Path(str(linked_payload["index_lock_path"]))
            linked_lock.touch()

            code, payload = run_preflight(
                repo, GIT_METADATA_PREFLIGHT_LOCK_MAX_AGE_SECONDS="0"
            )
            self.assertEqual(code, 0, payload)
            self.assertEqual(payload["status"], "pass")
            self.assertEqual(payload["locks"], [])

    def test_current_head_and_ref_locks_are_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = make_repo(Path(temp_dir))
            _, clean = run_preflight(repo)
            for key, kind in (("head_lock_path", "head"), ("ref_lock_path", "current_ref")):
                lock_path = Path(str(clean[key]))
                lock_path.parent.mkdir(parents=True, exist_ok=True)
                lock_path.touch()
                code, payload = run_preflight(
                    repo, GIT_METADATA_PREFLIGHT_LOCK_MAX_AGE_SECONDS="0"
                )
                self.assertEqual(code, 78, payload)
                self.assertIn("stale_index_lock_candidate", payload["reason_codes"])
                self.assertIn(kind, {item["kind"] for item in payload["locks"]})
                lock_path.unlink()

    def test_worktree_inspection_failure_is_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = make_repo(root)
            fake_bin = root / "bin"
            fake_bin.mkdir()
            git_binary = shutil.which("git")
            self.assertIsNotNone(git_binary)
            fake_git = fake_bin / "git"
            fake_git.write_text(
                "#!/bin/sh\n"
                'if [ "$1" = "worktree" ]; then echo unavailable >&2; exit 9; fi\n'
                f'exec "{git_binary}" "$@"\n',
                encoding="utf-8",
            )
            fake_git.chmod(0o755)

            code, payload = run_preflight(
                repo, PATH=f"{fake_bin}{os.pathsep}{os.environ['PATH']}"
            )
            self.assertEqual(code, 78, payload)
            self.assertIn("worktree_state_unavailable", payload["reason_codes"])
            self.assertIn("unavailable", str(payload["worktree_list_diagnostic"]))

    def test_prunable_worktree_is_advisory_until_explicit_cleanup(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = make_repo(root)
            linked = root / "prunable"
            created = git(repo, "worktree", "add", "-q", str(linked), "-b", "prunable")
            self.assertEqual(created.returncode, 0, created.stderr)
            shutil.rmtree(linked)

            code, payload = run_preflight(repo)
            self.assertEqual(code, 0, payload)
            self.assertEqual(payload["status"], "pass")
            self.assertTrue(payload["prunable_worktrees"])
            self.assertEqual(payload["advisories"], ["prunable_worktree"])

    def test_metadata_permission_denial_is_fail_closed_when_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = make_repo(Path(temp_dir))
            _, clean = run_preflight(repo)
            metadata_dir = Path(str(clean["git_dir"]))
            original_mode = metadata_dir.stat().st_mode & 0o777
            try:
                metadata_dir.chmod(0o555)
                if os.access(metadata_dir, os.W_OK):
                    self.skipTest("filesystem permits writes despite chmod(0555)")
                code, payload = run_preflight(repo)
                self.assertEqual(code, 78, payload)
                self.assertIn("metadata_write_denied", payload["reason_codes"])
            finally:
                metadata_dir.chmod(original_mode)


if __name__ == "__main__":
    unittest.main()
