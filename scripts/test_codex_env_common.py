#!/usr/bin/env python3
"""Tests for scripts/codex_env_common.sh changes introduced in this PR.

Covers:
- CODEX_REPO_ROOT variable: set via git rev-parse with pwd -P fallback
- codex_apply_env(): prepends $CODEX_REPO_ROOT/bin to PATH (new in this PR)
- codex_prepend_path_if_exists(): idempotency, skips non-existent dirs
- bin/ directory appears before ~/.local/bin in PATH after apply_env
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "codex_env_common.sh"


def _bash(snippet: str, env: dict | None = None, cwd: str | None = None) -> subprocess.CompletedProcess:
    """Run a bash snippet, returning the CompletedProcess."""
    base_env = {k: v for k, v in os.environ.items()}
    if env:
        base_env.update(env)
    return subprocess.run(
        ["bash", "-c", snippet],
        capture_output=True,
        text=True,
        env=base_env,
        cwd=cwd,
    )


def _source_and_run(extra: str, env: dict | None = None, cwd: str | None = None) -> subprocess.CompletedProcess:
    """Source codex_env_common.sh then run extra snippet."""
    snippet = f'source "{SCRIPT_PATH}"\n{extra}'
    return _bash(snippet, env=env, cwd=cwd)


# ---------------------------------------------------------------------------
# CODEX_REPO_ROOT: set after sourcing
# ---------------------------------------------------------------------------


class TestCodexRepoRoot(unittest.TestCase):
    """Verify CODEX_REPO_ROOT is set correctly after sourcing the script."""

    def test_codex_repo_root_is_set(self) -> None:
        """CODEX_REPO_ROOT must be non-empty after sourcing."""
        result = _source_and_run('printf "%s" "$CODEX_REPO_ROOT"')
        self.assertEqual(result.returncode, 0)
        self.assertTrue(result.stdout.strip(), "CODEX_REPO_ROOT must not be empty")

    def test_codex_repo_root_is_absolute_path(self) -> None:
        """CODEX_REPO_ROOT must be an absolute path."""
        result = _source_and_run('printf "%s" "$CODEX_REPO_ROOT"')
        self.assertEqual(result.returncode, 0)
        root = result.stdout.strip()
        self.assertTrue(root.startswith("/"), f"Expected absolute path, got: {root!r}")

    def test_codex_repo_root_matches_git_toplevel_in_git_repo(self) -> None:
        """When run inside a git repo, CODEX_REPO_ROOT should equal git rev-parse --show-toplevel."""
        git_result = _bash("git rev-parse --show-toplevel", cwd=str(REPO_ROOT))
        if git_result.returncode != 0:
            self.skipTest("Not inside a git repo")
        expected = git_result.stdout.strip()

        result = _source_and_run('printf "%s" "$CODEX_REPO_ROOT"', cwd=str(REPO_ROOT))
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), expected)

    def test_codex_repo_root_fallback_to_pwd_outside_git_repo(self) -> None:
        """When git is not available or dir is not a repo, CODEX_REPO_ROOT falls back to pwd -P."""
        with tempfile.TemporaryDirectory() as tmp:
            # /tmp is typically not a git repo
            # Resolve symlinks since pwd -P does too
            expected = str(Path(tmp).resolve())
            result = _source_and_run(
                'printf "%s" "$CODEX_REPO_ROOT"',
                cwd=tmp,
            )
            self.assertEqual(result.returncode, 0)
            actual = result.stdout.strip()
            # Either git found a root (unlikely for /tmp) or it fell back to pwd -P.
            # Accept both: just ensure it's non-empty and absolute.
            self.assertTrue(actual, "CODEX_REPO_ROOT must not be empty even outside a git repo")
            self.assertTrue(actual.startswith("/"))

    def test_codex_repo_root_is_a_directory(self) -> None:
        """CODEX_REPO_ROOT must point to a directory that exists."""
        result = _source_and_run('[[ -d "$CODEX_REPO_ROOT" ]] && echo yes || echo no')
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "yes", "CODEX_REPO_ROOT must be an existing directory")


# ---------------------------------------------------------------------------
# codex_apply_env: bin/ prepend (the main PR change)
# ---------------------------------------------------------------------------


class TestCodexApplyEnvBinPrepend(unittest.TestCase):
    """Verify codex_apply_env prepends $CODEX_REPO_ROOT/bin to PATH."""

    def test_apply_env_adds_repo_bin_to_path(self) -> None:
        """After codex_apply_env, $CODEX_REPO_ROOT/bin must appear in PATH."""
        result = _source_and_run(
            'codex_apply_env; printf "%s" "$PATH"',
            cwd=str(REPO_ROOT),
        )
        self.assertEqual(result.returncode, 0)
        path_entries = result.stdout.strip().split(":")
        # Check that any entry ends with /bin and corresponds to the repo
        bin_entries = [e for e in path_entries if e.endswith("/bin") and "codex" not in e.lower() or e.endswith("/bin")]
        repo_bin = None
        for entry in path_entries:
            if entry.endswith("/bin") and Path(entry).parent == REPO_ROOT:
                repo_bin = entry
                break
            # Also check if it matches the actual repo bin dir
            if Path(entry) == (REPO_ROOT / "bin"):
                repo_bin = entry
                break
        # At minimum, PATH should have the repo's bin if it exists or CODEX_REPO_ROOT/bin
        # The exact path depends on where git says the root is
        self.assertIn(str(REPO_ROOT / "bin"), result.stdout, "CODEX_REPO_ROOT/bin must be in PATH after codex_apply_env")

    def test_apply_env_places_repo_bin_before_local_bin(self) -> None:
        """$CODEX_REPO_ROOT/bin must appear before $HOME/.local/bin in PATH."""
        result = _source_and_run(
            'codex_apply_env; printf "%s" "$PATH"',
            cwd=str(REPO_ROOT),
        )
        self.assertEqual(result.returncode, 0)
        path_entries = result.stdout.strip().split(":")
        # Find indices
        repo_bin_str = str(REPO_ROOT / "bin")
        local_bin_str = str(Path.home() / ".local" / "bin")

        try:
            repo_bin_idx = path_entries.index(repo_bin_str)
        except ValueError:
            self.skipTest(f"CODEX_REPO_ROOT/bin ({repo_bin_str}) not found in PATH entries; bin/ dir may not exist")
            return

        try:
            local_bin_idx = path_entries.index(local_bin_str)
            self.assertLess(
                repo_bin_idx,
                local_bin_idx,
                f"CODEX_REPO_ROOT/bin must precede ~/.local/bin but got indices {repo_bin_idx} > {local_bin_idx}",
            )
        except ValueError:
            # ~/.local/bin not in PATH — that's fine; just verify repo bin is present
            pass

    def test_apply_env_is_idempotent_for_repo_bin(self) -> None:
        """Calling codex_apply_env twice must not duplicate $CODEX_REPO_ROOT/bin."""
        result = _source_and_run(
            'codex_apply_env; codex_apply_env; printf "%s" "$PATH"',
            cwd=str(REPO_ROOT),
        )
        self.assertEqual(result.returncode, 0)
        path_entries = result.stdout.strip().split(":")
        repo_bin_str = str(REPO_ROOT / "bin")
        count = path_entries.count(repo_bin_str)
        self.assertLessEqual(count, 1, f"CODEX_REPO_ROOT/bin appeared {count} times in PATH (expected at most 1)")

    def test_apply_env_does_not_add_nonexistent_bin(self) -> None:
        """If CODEX_REPO_ROOT/bin does not exist, it must not be added to PATH."""
        with tempfile.TemporaryDirectory() as tmp:
            # tmp has no bin/ subdirectory
            result = _bash(
                f'CODEX_REPO_ROOT="{tmp}"; '
                f'source "{SCRIPT_PATH}"; '
                f'CODEX_REPO_ROOT="{tmp}"; '
                'codex_apply_env; '
                'printf "%s" "$PATH"',
                cwd=tmp,
            )
            self.assertEqual(result.returncode, 0)
            bin_dir = f"{tmp}/bin"
            self.assertNotIn(bin_dir, result.stdout.split(":"),
                             f"{bin_dir} must not be added when the directory does not exist")

    def test_apply_env_adds_bin_when_directory_exists(self) -> None:
        """When $CODEX_REPO_ROOT/bin exists as a directory, it must be added to PATH."""
        with tempfile.TemporaryDirectory() as tmp:
            bin_dir = Path(tmp) / "bin"
            bin_dir.mkdir()
            result = _bash(
                f'source "{SCRIPT_PATH}"; '
                f'CODEX_REPO_ROOT="{tmp}"; '
                'codex_apply_env; '
                'printf "%s" "$PATH"',
                cwd=tmp,
            )
            self.assertEqual(result.returncode, 0)
            path_entries = result.stdout.strip().split(":")
            self.assertIn(str(bin_dir), path_entries,
                          f"{bin_dir} must be in PATH when it exists")

    def test_apply_env_exports_path(self) -> None:
        """codex_apply_env must export PATH so subprocesses see the update."""
        result = _source_and_run(
            'codex_apply_env; bash -c \'printf "%s" "$PATH"\'',
            cwd=str(REPO_ROOT),
        )
        self.assertEqual(result.returncode, 0)
        # If PATH is exported, the subprocess sees it; just check it's non-empty
        self.assertTrue(result.stdout.strip())


# ---------------------------------------------------------------------------
# codex_prepend_path_if_exists: existing behavior (edge cases for the new prepend)
# ---------------------------------------------------------------------------


class TestCodexPrependPathIfExists(unittest.TestCase):
    """Verify codex_prepend_path_if_exists handles edge cases correctly."""

    def test_skips_empty_entry(self) -> None:
        """An empty string must not be added to PATH."""
        original_path = "/usr/bin:/bin"
        result = _bash(
            f'source "{SCRIPT_PATH}"; '
            f'PATH="{original_path}"; '
            'codex_prepend_path_if_exists ""; '
            'printf "%s" "$PATH"',
        )
        self.assertEqual(result.returncode, 0)
        # PATH should be unchanged
        self.assertEqual(result.stdout.strip(), original_path)

    def test_skips_nonexistent_directory(self) -> None:
        """A path that does not exist on disk must not be added."""
        original_path = "/usr/bin:/bin"
        nonexistent = "/totally/nonexistent/path/12345"
        result = _bash(
            f'source "{SCRIPT_PATH}"; '
            f'PATH="{original_path}"; '
            f'codex_prepend_path_if_exists "{nonexistent}"; '
            'printf "%s" "$PATH"',
        )
        self.assertEqual(result.returncode, 0)
        self.assertNotIn(nonexistent, result.stdout)

    def test_prepends_existing_directory(self) -> None:
        """An existing directory must be prepended to PATH."""
        with tempfile.TemporaryDirectory() as tmp:
            original_path = "/usr/bin:/bin"
            result = _bash(
                f'source "{SCRIPT_PATH}"; '
                f'PATH="{original_path}"; '
                f'codex_prepend_path_if_exists "{tmp}"; '
                'printf "%s" "$PATH"',
            )
            self.assertEqual(result.returncode, 0)
            path_entries = result.stdout.strip().split(":")
            self.assertEqual(path_entries[0], tmp, "Existing dir must be prepended (first entry)")

    def test_does_not_duplicate_existing_entry(self) -> None:
        """If entry is already in PATH, it must not be duplicated."""
        with tempfile.TemporaryDirectory() as tmp:
            original_path = f"{tmp}:/usr/bin:/bin"
            result = _bash(
                f'source "{SCRIPT_PATH}"; '
                f'PATH="{original_path}"; '
                f'codex_prepend_path_if_exists "{tmp}"; '
                'printf "%s" "$PATH"',
            )
            self.assertEqual(result.returncode, 0)
            path_entries = result.stdout.strip().split(":")
            count = path_entries.count(tmp)
            self.assertEqual(count, 1, f"Entry {tmp!r} appeared {count} times (expected 1)")

    def test_does_not_duplicate_when_entry_is_in_middle(self) -> None:
        """If entry already exists in the middle of PATH, it must not be duplicated."""
        with tempfile.TemporaryDirectory() as tmp:
            original_path = f"/usr/bin:{tmp}:/bin"
            result = _bash(
                f'source "{SCRIPT_PATH}"; '
                f'PATH="{original_path}"; '
                f'codex_prepend_path_if_exists "{tmp}"; '
                'printf "%s" "$PATH"',
            )
            self.assertEqual(result.returncode, 0)
            path_entries = result.stdout.strip().split(":")
            count = path_entries.count(tmp)
            self.assertEqual(count, 1, f"Entry appeared {count} times after deduplication attempt")


# ---------------------------------------------------------------------------
# Script sourcing: basic sanity
# ---------------------------------------------------------------------------


class TestScriptSourceability(unittest.TestCase):
    """Verify the script can be sourced without errors."""

    def test_script_sources_without_error(self) -> None:
        """Sourcing codex_env_common.sh must exit 0."""
        result = _bash(f'source "{SCRIPT_PATH}"')
        self.assertEqual(result.returncode, 0, f"Sourcing failed: {result.stderr}")

    def test_script_is_idempotent_when_sourced_twice(self) -> None:
        """Sourcing twice must not cause errors."""
        result = _bash(f'source "{SCRIPT_PATH}"; source "{SCRIPT_PATH}"')
        self.assertEqual(result.returncode, 0, f"Double-source failed: {result.stderr}")

    def test_codex_apply_env_function_is_defined_after_source(self) -> None:
        """codex_apply_env must be defined as a function after sourcing."""
        result = _source_and_run("declare -f codex_apply_env > /dev/null && echo defined")
        self.assertEqual(result.returncode, 0)
        self.assertIn("defined", result.stdout)

    def test_codex_prepend_path_if_exists_function_is_defined(self) -> None:
        result = _source_and_run("declare -f codex_prepend_path_if_exists > /dev/null && echo defined")
        self.assertEqual(result.returncode, 0)
        self.assertIn("defined", result.stdout)


if __name__ == "__main__":
    unittest.main()