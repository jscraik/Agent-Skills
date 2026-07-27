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

    def test_disabled_write_probe_is_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = make_repo(Path(temp_dir))
            proc = subprocess.run(
                [sys.executable, str(SCRIPT), "--repo-root", str(repo), "--no-write-probe", "--json"],
                text=True, capture_output=True, check=False,
            )
            payload = json.loads(proc.stdout)
            self.assertEqual(proc.returncode, 78, payload)
            self.assertIn("metadata_write_probe_disabled", payload["reason_codes"])

    def test_invalid_cli_inputs_return_usage_exit(self) -> None:
        for args in (("--unknown-option",), ("--lock-max-age-seconds", "-1")):
            proc = subprocess.run(
                [sys.executable, str(SCRIPT), *args, "--json"],
                text=True, capture_output=True, check=False,
            )
            payload = json.loads(proc.stdout)
            self.assertEqual(proc.returncode, 64, payload)
            self.assertEqual(payload["reason_codes"], ["invalid_usage"])

        invalid_env = subprocess.run(
            [sys.executable, str(SCRIPT), "--json"],
            env={
                **os.environ,
                "GIT_METADATA_PREFLIGHT_LOCK_MAX_AGE_SECONDS": "not-an-integer",
            },
            text=True,
            capture_output=True,
            check=False,
        )
        invalid_payload = json.loads(invalid_env.stdout)
        self.assertEqual(invalid_env.returncode, 64, invalid_payload)
        self.assertEqual(invalid_payload["reason_codes"], ["invalid_usage"])

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
                    "--allow-parent-owned-index-lock",
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
                        "--allow-parent-owned-index-lock",
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

    def test_owned_linked_worktree_index_lock_is_advisory_for_pre_commit(self) -> None:
        if not lsof_available():
            self.skipTest("lsof is required to prove parent lock ownership")
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = make_repo(root)
            linked = root / "linked"
            created = git(repo, "worktree", "add", "-q", str(linked), "-b", "linked")
            self.assertEqual(created.returncode, 0, created.stderr)
            _, clean = run_preflight(linked)
            lock_path = Path(str(clean["index_lock_path"]))

            with lock_path.open("w", encoding="utf-8"):
                owned = subprocess.run(
                    [
                        sys.executable,
                        str(SCRIPT),
                        "--repo-root",
                        str(linked),
                        "--allow-parent-owned-index-lock",
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
            self.assertNotIn("current_worktree_locked", owned_payload["reason_codes"])

    def test_lsof_parent_chain_waives_owned_lock_without_ps(self) -> None:
        if not lsof_available():
            self.skipTest("lsof is required to prove lock ownership")
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = make_repo(Path(temp_dir))
            _, clean = run_preflight(repo)
            lock_path = Path(str(clean["index_lock_path"]))
            tool_bin = Path(temp_dir) / "no-ps-bin"
            tool_bin.mkdir()
            git_binary = shutil.which("git")
            self.assertIsNotNone(git_binary)
            (tool_bin / "git").symlink_to(str(git_binary))
            with lock_path.open("w", encoding="utf-8"):
                owned = subprocess.run(
                    [
                        "/bin/bash",
                        "-c",
                        (
                            f'"{sys.executable}" "{SCRIPT}" --repo-root "{repo}" '
                            "--allow-parent-owned-index-lock --json"
                        ),
                    ],
                    env={
                        **os.environ,
                        "GIT_METADATA_PREFLIGHT_LOCK_MAX_AGE_SECONDS": "0",
                        "PATH": str(tool_bin),
                    },
                    text=True,
                    capture_output=True,
                    check=False,
                )

            owned_payload = json.loads(owned.stdout)
            self.assertEqual(owned.returncode, 0, owned_payload)
            self.assertIn("expected_current_index_lock", owned_payload["advisories"])

    def test_git_hook_transaction_waives_current_index_lock(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = make_repo(Path(temp_dir))
            _, clean = run_preflight(repo)
            git_dir = Path(str(clean["git_dir"]))
            lock_path = Path(str(clean["index_lock_path"]))
            transaction_index = git_dir / "next-index-123.lock"
            transaction_index.write_text("hook transaction\n", encoding="utf-8")
            lock_path.write_text("current commit\n", encoding="utf-8")

            allowed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--repo-root",
                    str(repo),
                    "--allow-parent-owned-index-lock",
                    "--json",
                ],
                env={
                    **os.environ,
                    "GIT_DIR": str(git_dir),
                    "GIT_INDEX_FILE": str(transaction_index),
                    "GIT_METADATA_PREFLIGHT_LOCK_MAX_AGE_SECONDS": "0",
                },
                text=True,
                capture_output=True,
                check=False,
            )

            allowed_payload = json.loads(allowed.stdout)
            self.assertEqual(allowed.returncode, 0, allowed_payload)
            self.assertTrue(allowed_payload["expected_hook_transaction"])
            self.assertIn("expected_current_index_lock", allowed_payload["advisories"])

    def test_nontransaction_git_index_file_does_not_waive_current_lock(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = make_repo(Path(temp_dir))
            _, clean = run_preflight(repo)
            git_dir = Path(str(clean["git_dir"]))
            lock_path = Path(str(clean["index_lock_path"]))
            foreign_index = git_dir / "foreign-index.lock"
            foreign_index.write_text("foreign transaction\n", encoding="utf-8")
            lock_path.write_text("current commit\n", encoding="utf-8")

            blocked = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--repo-root",
                    str(repo),
                    "--allow-parent-owned-index-lock",
                    "--json",
                ],
                env={
                    **os.environ,
                    "GIT_DIR": str(git_dir),
                    "GIT_INDEX_FILE": str(foreign_index),
                    "GIT_METADATA_PREFLIGHT_LOCK_MAX_AGE_SECONDS": "0",
                },
                text=True,
                capture_output=True,
                check=False,
            )

            blocked_payload = json.loads(blocked.stdout)
            self.assertEqual(blocked.returncode, 78, blocked_payload)
            self.assertFalse(blocked_payload["expected_hook_transaction"])
            self.assertIn("stale_index_lock_candidate", blocked_payload["reason_codes"])

    def test_unowned_linked_worktree_index_lock_is_not_waived_for_pre_commit(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = make_repo(root)
            linked = root / "linked"
            created = git(repo, "worktree", "add", "-q", str(linked), "-b", "linked")
            self.assertEqual(created.returncode, 0, created.stderr)
            _, clean = run_preflight(linked)
            lock_path = Path(str(clean["index_lock_path"]))
            lock_path.touch()

            unowned = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--repo-root",
                    str(linked),
                    "--allow-parent-owned-index-lock",
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

            unowned_payload = json.loads(unowned.stdout)
            self.assertEqual(unowned.returncode, 78, unowned_payload)
            expected_reason = (
                "stale_index_lock_candidate"
                if lsof_available()
                else "lock_owner_detector_unavailable"
            )
            self.assertIn(expected_reason, unowned_payload["reason_codes"])
            self.assertTrue(lock_path.exists(), "preflight must never remove locks")

    def test_explicit_current_worktree_lock_is_not_waived_for_pre_commit(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = make_repo(root)
            linked = root / "linked"
            created = git(repo, "worktree", "add", "-q", str(linked), "-b", "linked")
            self.assertEqual(created.returncode, 0, created.stderr)
            locked = git(repo, "worktree", "lock", "--reason", "manual", str(linked))
            self.assertEqual(locked.returncode, 0, locked.stderr)

            current = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--repo-root",
                    str(linked),
                    "--allow-parent-owned-index-lock",
                    "--json",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            current_payload = json.loads(current.stdout)
            self.assertEqual(current.returncode, 78, current_payload)
            self.assertIn("current_worktree_locked", current_payload["reason_codes"])

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
            self.assertEqual(code, 78, payload)
            self.assertIn("current_worktree_locked", payload["reason_codes"])

    def test_lock_in_other_worktree_blocks_current_worktree(self) -> None:
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
            self.assertEqual(code, 78, payload)
            self.assertEqual(payload["status"], "blocked")
            self.assertIn("related_worktree_locked", payload["reason_codes"])

    def test_object_store_and_reflog_parents_are_write_probed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = make_repo(Path(temp_dir))
            code, payload = run_preflight(repo)
            self.assertEqual(code, 0, payload)
            probed = {item["path"] for item in payload["write_probe"]}
            self.assertIn(payload["objects_dir"], probed)
            self.assertIn(str(Path(str(payload["ref_log_path"])).parent), probed)

    def test_detached_head_reflog_is_resolved_and_probed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = make_repo(Path(temp_dir))
            self.assertEqual(git(repo, "checkout", "--detach", "-q", "HEAD").returncode, 0)
            code, payload = run_preflight(repo)

            self.assertEqual(code, 0, payload)
            self.assertTrue(str(payload["ref_log_path"]).endswith("logs/HEAD"), payload)
            probed = {item["path"] for item in payload["write_probe"]}
            self.assertIn(str(Path(str(payload["ref_log_path"])).parent), probed)

    def test_non_directory_ref_component_is_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = make_repo(Path(temp_dir))
            self.assertEqual(git(repo, "checkout", "-qb", "feature/topic").returncode, 0)
            self.assertEqual(git(repo, "pack-refs", "--all", "--prune").returncode, 0)
            ref_component = repo / ".git" / "refs" / "heads" / "feature"
            ref_component.write_text("blocked\n", encoding="utf-8")
            code, payload = run_preflight(repo)
            self.assertEqual(code, 78, payload)
            self.assertIn("metadata_path_component_not_directory", payload["reason_codes"])

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
                self.assertIn("stale_git_metadata_lock_candidate", payload["reason_codes"])
                self.assertIn(kind, {item["kind"] for item in payload["locks"]})
                lock_path.unlink()

    def test_packed_ref_parent_is_probed_at_nearest_existing_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = make_repo(Path(temp_dir))
            created = git(repo, "checkout", "-qb", "feature/foo")
            self.assertEqual(created.returncode, 0, created.stderr)
            packed = git(repo, "pack-refs", "--all", "--prune")
            self.assertEqual(packed.returncode, 0, packed.stderr)

            code, payload = run_preflight(repo)

            self.assertEqual(code, 0, payload)
            self.assertEqual(payload["status"], "pass")
            ref_parent = Path(str(payload["ref_lock_path"])).parent
            self.assertFalse(ref_parent.is_dir())
            self.assertIn(str(ref_parent.parent), payload["metadata_dirs"])
            self.assertNotIn(str(ref_parent), payload["metadata_dirs"])

    def test_symlinked_ref_locks_are_classified_from_original_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = make_repo(Path(temp_dir))
            _, clean = run_preflight(repo)
            lock_path = Path(str(clean["ref_lock_path"]))
            lock_path.parent.mkdir(parents=True, exist_ok=True)
            for live in (False, True):
                target = Path(temp_dir) / ("live-target" if live else "missing-target")
                if live:
                    target.touch()
                lock_path.symlink_to(target)
                code, payload = run_preflight(repo)
                self.assertEqual(code, 78, payload)
                record = next(item for item in payload["locks"] if item["kind"] == "current_ref")
                self.assertEqual(Path(str(record["path"])), lock_path)
                if live:
                    self.assertIn("recent_git_metadata_lock_unknown", payload["reason_codes"])
                else:
                    self.assertIn("git_metadata_lock_non_regular", payload["reason_codes"])
                lock_path.unlink()
                if live:
                    target.unlink()

    def test_ref_lock_parent_permission_denial_is_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = make_repo(Path(temp_dir))
            _, clean = run_preflight(repo)
            metadata_dir = Path(str(clean["ref_lock_path"])).parent
            original_mode = metadata_dir.stat().st_mode & 0o777
            try:
                metadata_dir.chmod(0o555)
                if os.access(metadata_dir, os.W_OK):
                    self.skipTest("filesystem permits writes despite chmod(0555)")
                code, payload = run_preflight(repo)
                self.assertEqual(code, 78, payload)
                self.assertIn("metadata_write_denied", payload["reason_codes"])
                self.assertIn(str(metadata_dir), [item["path"] for item in payload["write_probe"]])
            finally:
                metadata_dir.chmod(original_mode)

    def test_git_subprocess_timeout_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = make_repo(root)
            fake_bin = root / "bin"
            fake_bin.mkdir()
            fake_git = fake_bin / "git"
            fake_git.write_text("#!/bin/sh\nsleep 6\n", encoding="utf-8")
            fake_git.chmod(0o755)
            code, payload = run_preflight(
                repo, PATH=f"{fake_bin}{os.pathsep}{os.environ['PATH']}"
            )
            self.assertEqual(code, 78, payload)
            self.assertEqual(payload["reason_codes"], ["not_git_worktree"])
            self.assertIn("timed out after 5s", str(payload["diagnostic"]))

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
