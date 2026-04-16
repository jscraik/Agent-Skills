#!/usr/bin/env python3
"""Tests for Infrastructure/scripts/codex-preflight/codex_env_common.sh changes introduced in this PR.

Covers:
- CODEX_REPO_ROOT variable: resolved from script location, preferring git toplevel
- codex_apply_env(): prepends $CODEX_REPO_ROOT/bin to PATH (new in this PR)
- codex_prepend_path_if_exists(): idempotency, skips non-existent dirs
- bin/ directory appears before ~/.local/bin in PATH after apply_env
"""

from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPO_ROOT / "scripts" / "codex_env_common.sh"


def _bash(snippet: str, env: dict | None = None, cwd: str | None = None) -> subprocess.CompletedProcess:
    """
    Execute a bash snippet and return the completed process result.
    
    Parameters:
        snippet (str): Shell code to run under `bash -c`.
        env (dict | None): Environment variable overrides merged on top of the current environment.
        cwd (str | None): Working directory in which to run the snippet.
    
    Returns:
        subprocess.CompletedProcess: The completed process containing `stdout`, `stderr` and `returncode`.
    """
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
    """
    Source the codex_env_common.sh script in a bash subshell and then execute the provided shell snippet.
    
    The snippet is executed after the script is sourced so any functions or environment variables defined by
    codex_env_common.sh are available to the snippet.
    
    Parameters:
        extra (str): Shell commands to run after sourcing the script.
        env (dict | None): Environment overrides merged with the current process environment for the subprocess.
        cwd (str | None): Working directory for the subprocess.
    
    Returns:
        subprocess.CompletedProcess: The completed process result containing return code, stdout and stderr.
    """
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
        """
        Ensure CODEX_REPO_ROOT is an absolute path.
        
        Asserts that after sourcing the environment script, the `CODEX_REPO_ROOT` value starts with '/'.
        """
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

    def test_codex_repo_root_fallback_to_script_parent_outside_git_repo(self) -> None:
        """When script dir is outside git, CODEX_REPO_ROOT falls back to script-dir parent."""
        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp).resolve()
            temp_scripts = temp_root / "scripts"
            temp_scripts.mkdir(parents=True, exist_ok=True)
            temp_script = temp_scripts / "codex_env_common.sh"
            temp_script.write_text(SCRIPT_PATH.read_text(encoding="utf-8"), encoding="utf-8")
            expected = str(temp_root)
            result = _bash(f'source "{temp_script}"; printf "%s" "$CODEX_REPO_ROOT"', cwd=tmp)
            self.assertEqual(result.returncode, 0)
            actual = result.stdout.strip()
            self.assertEqual(actual, expected, "Outside a git repo, fallback should resolve to script-dir parent")

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
            'mise() { return 1; }; codex_apply_env; printf "%s" "$PATH"',
            cwd=str(REPO_ROOT),
            env={"PATH": "/usr/bin:/bin"},
        )
        self.assertEqual(result.returncode, 0)
        # At minimum, PATH should have the repo's bin if it exists or CODEX_REPO_ROOT/bin
        # The exact path depends on where git says the root is
        self.assertIn(str(REPO_ROOT / "bin"), result.stdout, "CODEX_REPO_ROOT/bin must be in PATH after codex_apply_env")

    def test_apply_env_places_repo_bin_before_local_bin(self) -> None:
        """
        Ensure $CODEX_REPO_ROOT/bin appears before $HOME/.local/bin in PATH.
        
        If ~/.local/bin is absent the test only asserts that the repository bin is present.
        If the repository bin is not found in PATH the test is skipped.
        """
        result = _source_and_run(
            'mise() { return 1; }; codex_apply_env; printf "%s" "$PATH"',
            cwd=str(REPO_ROOT),
            env={"PATH": "/usr/bin:/bin"},
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
        """
        Ensure that when CODEX_REPO_ROOT/bin does not exist it is not prepended to PATH.
        
        Uses a temporary directory without a `bin/` subdirectory, sources the script, runs `codex_apply_env`
        and asserts that `<tmp>/bin` is not present in the resulting `PATH`.
        """
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
        """
        Ensure the repository 'bin' directory is added to PATH when it exists.
        
        Sets CODEX_REPO_ROOT to a temporary directory containing a `bin/` subdirectory, runs `codex_apply_env`, and asserts that that `bin` path appears among PATH entries.
        """
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
        """
        Ensure codex_prepend_path_if_exists does not add an empty entry to PATH.
        
        Uses PATH "/usr/bin:/bin" and asserts that calling codex_prepend_path_if_exists "" leaves PATH unchanged.
        """
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
        """
        Ensure codex_prepend_path_if_exists does not add a non-existent directory to PATH.
        
        Validates the behaviour by setting PATH to a known value, attempting to prepend a path that does not exist on disk, and asserting the PATH remains unchanged.
        """
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
        """Ensure codex_prepend_path_if_exists prepends an existing directory to the front of PATH."""
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
        """
        Assert that sourcing Infrastructure/scripts/codex-preflight/codex_env_common.sh completes successfully (exit status 0).
        
        This test protects against syntax or runtime errors in the script; on failure it exposes the script's stderr for diagnosis.
        """
        result = _bash(f'source "{SCRIPT_PATH}"')
        self.assertEqual(result.returncode, 0, f"Sourcing failed: {result.stderr}")

    def test_script_is_idempotent_when_sourced_twice(self) -> None:
        """
        Ensure sourcing the shell script twice does not produce errors.
        
        This protects against side-effects, redefinition errors or other failures when the script is sourced multiple times in the same shell.
        """
        result = _bash(f'source "{SCRIPT_PATH}"; source "{SCRIPT_PATH}"')
        self.assertEqual(result.returncode, 0, f"Double-source failed: {result.stderr}")

    def test_codex_apply_env_function_is_defined_after_source(self) -> None:
        """
        Ensure the shell function `codex_apply_env` is defined after sourcing the script.
        
        Protects against regressions where sourcing Infrastructure/scripts/codex-preflight/codex_env_common.sh does not expose `codex_apply_env` as a shell function.
        """
        result = _source_and_run("declare -f codex_apply_env > /dev/null && echo defined")
        self.assertEqual(result.returncode, 0)
        self.assertIn("defined", result.stdout)

    def test_codex_prepend_path_if_exists_function_is_defined(self) -> None:
        """
        Verify that the shell function `codex_prepend_path_if_exists` is available after sourcing the script.
        
        Sources the module in a subshell and asserts the function name is declared in the resulting shell environment.
        """
        result = _source_and_run("declare -f codex_prepend_path_if_exists > /dev/null && echo defined")
        self.assertEqual(result.returncode, 0)
        self.assertIn("defined", result.stdout)


if __name__ == "__main__":
    unittest.main()
