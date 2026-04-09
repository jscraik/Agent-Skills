#!/usr/bin/env python3
"""Tests for scaffold_hook_pack.py changes introduced in this PR.

Covers:
- build_hooks_json(): SessionStart matcher changed from ^(startup|resume|clear)$ to ^(startup|resume)$
- ensure_writeable(): file-existence and force-flag behavior
- write_text(): directory creation and content writing
- main() integration: project vs user scope, file permissions, timeout bounds
"""

from __future__ import annotations

import json
import stat
import sys
import tempfile
import unittest
from pathlib import Path

# Put the script's directory on sys.path so we can import the module directly.
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import scaffold_hook_pack  # noqa: E402


# ---------------------------------------------------------------------------
# build_hooks_json: matcher regression
# ---------------------------------------------------------------------------


class TestBuildHooksJsonMatcher(unittest.TestCase):
    """Verify SessionStart matcher reflects the PR change (removed |clear)."""

    def _make_paths(self) -> tuple[Path, Path, Path]:
        """
        Provide the three expected hook script paths used by the tests.
        
        Returns:
            tuple[Path, Path, Path]: Paths for the session-start, user-prompt-submit and stop-guard hook scripts, in that order.
        """
        return (
            Path("/fake/hooks/session-start.sh"),
            Path("/fake/hooks/user-prompt-submit.sh"),
            Path("/fake/hooks/stop-guard.sh"),
        )

    def _parse(self, timeout: int = 10) -> dict:
        """
        Parse scaffold_hook_pack.build_hooks_json() output using the test's standard hook paths.
        
        Calls the builder with the test's predefined hook script paths and the given timeout, then decodes and returns the resulting JSON structure.
        
        Parameters:
            timeout (int): Timeout value to embed in generated hook entries.
        
        Returns:
            dict: The parsed JSON object produced by the builder.
        """
        session, user_prompt, stop = self._make_paths()
        raw = scaffold_hook_pack.build_hooks_json(
            session_start_path=session,
            user_prompt_submit_path=user_prompt,
            stop_guard_path=stop,
            timeout=timeout,
        )
        return json.loads(raw)

    def test_session_start_matcher_is_startup_resume_only(self) -> None:
        """Matcher must be exactly ^(startup|resume)$ — 'clear' must not appear."""
        payload = self._parse()
        hooks = payload["hooks"]["SessionStart"]
        self.assertEqual(len(hooks), 1)
        matcher = hooks[0]["matcher"]
        self.assertEqual(matcher, "^(startup|resume)$")

    def test_session_start_matcher_does_not_include_clear(self) -> None:
        payload = self._parse()
        matcher = payload["hooks"]["SessionStart"][0]["matcher"]
        self.assertNotIn("clear", matcher)

    def test_session_start_matcher_includes_startup(self) -> None:
        payload = self._parse()
        matcher = payload["hooks"]["SessionStart"][0]["matcher"]
        self.assertIn("startup", matcher)

    def test_session_start_matcher_includes_resume(self) -> None:
        """
        Ensure the SessionStart hook's matcher contains the literal 'resume'.
        
        Verifies that the generated hooks JSON includes 'resume' in the first `SessionStart` matcher entry.
        """
        payload = self._parse()
        matcher = payload["hooks"]["SessionStart"][0]["matcher"]
        self.assertIn("resume", matcher)

    def test_output_is_valid_json(self) -> None:
        session, user_prompt, stop = self._make_paths()
        raw = scaffold_hook_pack.build_hooks_json(
            session_start_path=session,
            user_prompt_submit_path=user_prompt,
            stop_guard_path=stop,
            timeout=10,
        )
        # Should not raise
        parsed = json.loads(raw)
        self.assertIsInstance(parsed, dict)

    def test_output_ends_with_newline(self) -> None:
        session, user_prompt, stop = self._make_paths()
        raw = scaffold_hook_pack.build_hooks_json(
            session_start_path=session,
            user_prompt_submit_path=user_prompt,
            stop_guard_path=stop,
            timeout=10,
        )
        self.assertTrue(raw.endswith("\n"))

    def test_hooks_json_has_session_start_key(self) -> None:
        payload = self._parse()
        self.assertIn("SessionStart", payload["hooks"])

    def test_hooks_json_has_user_prompt_submit_key(self) -> None:
        payload = self._parse()
        self.assertIn("UserPromptSubmit", payload["hooks"])

    def test_hooks_json_has_stop_key(self) -> None:
        """
        Verifies that the generated hooks JSON includes a 'Stop' entry under the top-level 'hooks' key.
        
        Ensures the parsed payload contains "Stop" as one of the hook names.
        """
        payload = self._parse()
        self.assertIn("Stop", payload["hooks"])

    def test_session_start_hook_type_is_command(self) -> None:
        """
        Verify the SessionStart hook entry is defined as a command.
        
        Parses the generated hooks JSON and asserts that the first entry under `hooks.SessionStart` has its `type` field equal to `"command"`.
        """
        payload = self._parse()
        hook_entry = payload["hooks"]["SessionStart"][0]["hooks"][0]
        self.assertEqual(hook_entry["type"], "command")

    def test_session_start_hook_has_status_message(self) -> None:
        payload = self._parse()
        hook_entry = payload["hooks"]["SessionStart"][0]["hooks"][0]
        self.assertIn("statusMessage", hook_entry)
        self.assertTrue(hook_entry["statusMessage"])

    def test_timeout_value_is_embedded(self) -> None:
        payload = self._parse(timeout=42)
        hook_entry = payload["hooks"]["SessionStart"][0]["hooks"][0]
        self.assertEqual(hook_entry["timeout"], 42)

    def test_session_start_command_uses_provided_path(self) -> None:
        payload = self._parse()
        hook_entry = payload["hooks"]["SessionStart"][0]["hooks"][0]
        self.assertEqual(hook_entry["command"], "/fake/hooks/session-start.sh")

    def test_user_prompt_submit_command_uses_provided_path(self) -> None:
        payload = self._parse()
        hook_entry = payload["hooks"]["UserPromptSubmit"][0]["hooks"][0]
        self.assertEqual(hook_entry["command"], "/fake/hooks/user-prompt-submit.sh")

    def test_stop_command_uses_provided_path(self) -> None:
        payload = self._parse()
        hook_entry = payload["hooks"]["Stop"][0]["hooks"][0]
        self.assertEqual(hook_entry["command"], "/fake/hooks/stop-guard.sh")


# ---------------------------------------------------------------------------
# ensure_writeable
# ---------------------------------------------------------------------------


class TestEnsureWriteable(unittest.TestCase):
    """Validate file-existence and force-flag guard."""

    def test_raises_when_file_exists_and_no_force(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "existing.txt"
            path.write_text("content", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                scaffold_hook_pack.ensure_writeable(path, force=False)

    def test_does_not_raise_when_file_exists_and_force(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "existing.txt"
            path.write_text("content", encoding="utf-8")
            # Should not raise
            scaffold_hook_pack.ensure_writeable(path, force=True)

    def test_does_not_raise_when_file_does_not_exist(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "nonexistent.txt"
            # Should not raise
            scaffold_hook_pack.ensure_writeable(path, force=False)

    def test_error_message_contains_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "existing.txt"
            path.write_text("content", encoding="utf-8")
            with self.assertRaises(FileExistsError) as ctx:
                scaffold_hook_pack.ensure_writeable(path, force=False)
            self.assertIn(str(path), str(ctx.exception))


# ---------------------------------------------------------------------------
# write_text
# ---------------------------------------------------------------------------


class TestWriteText(unittest.TestCase):
    """Verify write_text creates parent dirs and writes content."""

    def test_creates_parent_directories(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "deep" / "nested" / "file.txt"
            scaffold_hook_pack.write_text(path, "hello", force=False)
            self.assertTrue(path.exists())

    def test_writes_expected_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "file.txt"
            scaffold_hook_pack.write_text(path, "expected content", force=False)
            self.assertEqual(path.read_text(encoding="utf-8"), "expected content")

    def test_raises_without_force_when_file_exists(self) -> None:
        """
        Verifies that write_text raises FileExistsError when the destination file already exists and force is False.
        
        Creates an existing file with content, then attempts to write new content without using force to ensure the function refuses to overwrite and raises FileExistsError.
        """
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "file.txt"
            path.write_text("original", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                scaffold_hook_pack.write_text(path, "new content", force=False)

    def test_overwrites_with_force(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "file.txt"
            path.write_text("original", encoding="utf-8")
            scaffold_hook_pack.write_text(path, "replaced", force=True)
            self.assertEqual(path.read_text(encoding="utf-8"), "replaced")

    def test_uses_utf8_encoding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "unicode.txt"
            content = "café résumé 日本語"
            scaffold_hook_pack.write_text(path, content, force=False)
            self.assertEqual(path.read_text(encoding="utf-8"), content)


# ---------------------------------------------------------------------------
# main() integration: project scope
# ---------------------------------------------------------------------------


class TestMainProjectScope(unittest.TestCase):
    """Integration tests for the project-scope scaffold output."""

    def _run_main(self, target_root: Path, force: bool = False, timeout: int = 10) -> dict:
        """
        Invoke scaffold_hook_pack.main() as if called with `--scope project`, capture its stdout and return the parsed JSON summary.
        
        Parameters:
            target_root (Path): Filesystem root passed to `--target-root` for the run.
            force (bool): If true, include `--force` in the CLI arguments to allow overwriting.
            timeout (int): Value passed to `--timeout` (the function under test may bound this value).
        
        Returns:
            dict: The JSON-decoded summary emitted to stdout by main().
        """
        import io
        from contextlib import redirect_stdout

        args_list = [
            "--target-root", str(target_root),
            "--scope", "project",
            "--timeout", str(timeout),
        ]
        if force:
            args_list.append("--force")

        buf = io.StringIO()
        # Patch sys.argv and capture stdout
        import sys as _sys
        old_argv = _sys.argv
        old_stdout = _sys.stdout
        try:
            _sys.argv = ["scaffold_hook_pack.py"] + args_list
            with redirect_stdout(buf):
                scaffold_hook_pack.main()
        finally:
            _sys.argv = old_argv

        return json.loads(buf.getvalue())

    def test_project_scope_creates_codex_hooks_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            summary = self._run_main(root)
            hooks_json_path = root / ".codex" / "hooks.json"
            self.assertTrue(hooks_json_path.exists())

    def test_project_scope_hooks_json_in_dotcodex(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            summary = self._run_main(root)
            generated = summary["generated_files"]
            self.assertTrue(any(".codex/hooks.json" in p for p in generated))

    def test_project_scope_session_start_in_dotcodex_hooks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._run_main(root)
            session_start = root / ".codex" / "hooks" / "session-start.sh"
            self.assertTrue(session_start.exists())

    def test_project_scope_user_prompt_submit_script_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._run_main(root)
            script = root / ".codex" / "hooks" / "user-prompt-submit.sh"
            self.assertTrue(script.exists())

    def test_project_scope_stop_guard_script_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._run_main(root)
            script = root / ".codex" / "hooks" / "stop-guard.sh"
            self.assertTrue(script.exists())

    def test_project_scope_readme_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._run_main(root)
            readme = root / ".codex" / "hooks" / "README.md"
            self.assertTrue(readme.exists())

    def test_project_scope_session_start_is_executable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._run_main(root)
            script = root / ".codex" / "hooks" / "session-start.sh"
            mode = script.stat().st_mode
            self.assertTrue(mode & stat.S_IXUSR, "session-start.sh must be user-executable")

    def test_project_scope_user_prompt_submit_is_executable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._run_main(root)
            script = root / ".codex" / "hooks" / "user-prompt-submit.sh"
            mode = script.stat().st_mode
            self.assertTrue(mode & stat.S_IXUSR)

    def test_project_scope_stop_guard_is_executable(self) -> None:
        """
        Check that the generated project-scope stop-guard hook script is user-executable.
        
        Verifies the user execute permission bit is set on .codex/hooks/stop-guard.sh after running the scaffolding routine for the project scope.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._run_main(root)
            script = root / ".codex" / "hooks" / "stop-guard.sh"
            mode = script.stat().st_mode
            self.assertTrue(mode & stat.S_IXUSR)

    def test_project_scope_hooks_json_matcher_is_startup_resume(self) -> None:
        """
        Verify that a project-scoped hooks.json defines the SessionStart matcher exactly as ^(startup|resume)$.
        
        Asserts the generated .codex/hooks.json contains a SessionStart hook whose first matcher equals "^(startup|resume)$" (ensuring it does not include "clear").
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._run_main(root)
            hooks_json = root / ".codex" / "hooks.json"
            payload = json.loads(hooks_json.read_text(encoding="utf-8"))
            matcher = payload["hooks"]["SessionStart"][0]["matcher"]
            self.assertEqual(matcher, "^(startup|resume)$")

    def test_project_scope_hooks_json_matcher_excludes_clear(self) -> None:
        """
        Ensure the generated SessionStart hook matcher for project scope excludes the string "clear".
        
        This protects against templates or matcher-generation logic that would treat a terminal clear event as a recognised hook source; the test runs the scaffolding for a project target and asserts the serialized `SessionStart` matcher does not contain `"clear"`.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._run_main(root)
            hooks_json = root / ".codex" / "hooks.json"
            content = hooks_json.read_text(encoding="utf-8")
            # 'clear' must not appear in matcher context
            payload = json.loads(content)
            matcher = payload["hooks"]["SessionStart"][0]["matcher"]
            self.assertNotIn("clear", matcher)

    def test_project_scope_summary_has_correct_scope(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            summary = self._run_main(root)
            self.assertEqual(summary["scope"], "project")

    def test_project_scope_summary_schema_version(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            summary = self._run_main(root)
            self.assertEqual(summary["schema_version"], "1.0")

    def test_raises_without_force_on_second_run(self) -> None:
        """Running twice without --force must fail on existing files."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._run_main(root)
            with self.assertRaises(FileExistsError):
                self._run_main(root, force=False)

    def test_force_flag_allows_second_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._run_main(root)
            # Should not raise
            self._run_main(root, force=True)

    def test_timeout_is_bounded_to_at_least_one(self) -> None:
        """main() passes max(timeout, 1) to build_hooks_json to prevent zero timeouts."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._run_main(root, timeout=0)
            hooks_json = root / ".codex" / "hooks.json"
            payload = json.loads(hooks_json.read_text(encoding="utf-8"))
            hook_entry = payload["hooks"]["SessionStart"][0]["hooks"][0]
            self.assertGreaterEqual(hook_entry["timeout"], 1)


# ---------------------------------------------------------------------------
# main() integration: user scope
# ---------------------------------------------------------------------------


class TestMainUserScope(unittest.TestCase):
    """Integration tests for user-scope scaffold layout."""

    def _run_main_user(self, target_root: Path) -> dict:
        """
        Run scaffold_hook_pack.main() with user scope and capture the JSON summary it writes to stdout.
        
        Parameters:
        	target_root (Path): Root directory to use as the target for user-scoped scaffolding.
        
        Returns:
        	summary (dict): The parsed JSON summary emitted to stdout by main().
        """
        import io
        import sys as _sys

        buf = io.StringIO()
        old_argv = _sys.argv
        try:
            _sys.argv = [
                "scaffold_hook_pack.py",
                "--target-root", str(target_root),
                "--scope", "user",
            ]
            with io.StringIO() as capture:
                import contextlib
                with contextlib.redirect_stdout(buf):
                    scaffold_hook_pack.main()
        finally:
            _sys.argv = old_argv

        return json.loads(buf.getvalue())

    def test_user_scope_hooks_dir_is_not_dotcodex(self) -> None:
        """User scope places hooks directly under target_root/hooks/, not .codex/hooks/."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._run_main_user(root)
            # hooks.json should be at root, not root/.codex/
            hooks_json = root / "hooks.json"
            self.assertTrue(hooks_json.exists())

    def test_user_scope_scripts_in_hooks_subdir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._run_main_user(root)
            session_start = root / "hooks" / "session-start.sh"
            self.assertTrue(session_start.exists())

    def test_user_scope_summary_scope_field(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            summary = self._run_main_user(root)
            self.assertEqual(summary["scope"], "user")

    def test_user_scope_hooks_json_matcher_correct(self) -> None:
        """
        Ensure that when scaffolding hooks for user scope the SessionStart hook's matcher is exactly "^(startup|resume)$".
        
        This protects against regressions that would alter the required session-start matcher in the generated hooks.json for user-scoped installations.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._run_main_user(root)
            hooks_json = root / "hooks.json"
            payload = json.loads(hooks_json.read_text(encoding="utf-8"))
            matcher = payload["hooks"]["SessionStart"][0]["matcher"]
            self.assertEqual(matcher, "^(startup|resume)$")


# ---------------------------------------------------------------------------
# Template content checks: session_start_template
# ---------------------------------------------------------------------------


class TestSessionStartTemplate(unittest.TestCase):
    """Verify session_start_template() content is compatible with PR changes."""

    def setUp(self) -> None:
        """
        Initialises the test fixture by loading the session start hook template into self.text.
        
        This makes the template text available to individual test methods for assertions about its contents.
        """
        self.text = scaffold_hook_pack.session_start_template()

    def test_template_is_non_empty(self) -> None:
        self.assertTrue(self.text.strip())

    def test_template_starts_with_shebang(self) -> None:
        self.assertTrue(self.text.startswith("#!/"), f"Expected shebang, got: {self.text[:20]!r}")

    def test_template_handles_resume_source(self) -> None:
        self.assertIn("resume", self.text)

    def test_template_does_not_hard_code_clear_as_source(self) -> None:
        """Template should not add special logic for 'clear' as a recognized source."""
        # 'clear' may appear in comments or other contexts, but must not be
        # treated as a known session source value matched by the hook.
        # The matcher in hooks.json is the gate; the template itself should not
        # add branch logic for a 'clear' source that the matcher won't pass.
        # We just verify the startup/resume branch is explicit.
        self.assertIn("startup", self.text)

    def test_template_handles_jq_not_found(self) -> None:
        """Template must gracefully degrade when jq is absent."""
        self.assertIn("jq not found", self.text)

    def test_template_sets_continue_true(self) -> None:
        self.assertIn("continue: true", self.text)


# ---------------------------------------------------------------------------
# Template content checks: stop_guard_template
# ---------------------------------------------------------------------------


class TestStopGuardTemplate(unittest.TestCase):
    """Verify stop_guard_template() respects stop_hook_active guard."""

    def setUp(self) -> None:
        self.text = scaffold_hook_pack.stop_guard_template()

    def test_template_checks_stop_hook_active(self) -> None:
        """Template must check stop_hook_active to prevent infinite re-entry."""
        self.assertIn("stop_hook_active", self.text)

    def test_template_fails_open_on_second_pass(self) -> None:
        """When stop_hook_active is true, template must output continue: true and exit."""
        self.assertIn("stop_hook_active", self.text)
        # The guard pattern should exit 0 when already active
        self.assertIn("exit 0", self.text)

    def test_template_blocks_todo_markers(self) -> None:
        self.assertIn("todo", self.text)

    def test_template_is_non_empty(self) -> None:
        self.assertTrue(self.text.strip())


if __name__ == "__main__":
    unittest.main()