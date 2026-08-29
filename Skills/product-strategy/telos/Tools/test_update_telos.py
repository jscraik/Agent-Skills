import json
import os
import re
import subprocess
import stat
import tempfile
import time
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("UpdateTelos.ts")


class UpdateTelosTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="telos-update-")
        self.root = Path(self.temp.name)
        (self.root / "TOOLS").mkdir(parents=True)
        (self.root / "USER" / "TELOS").mkdir(parents=True)
        (self.root / "TOOLS" / "LifeosConfig.ts").write_text(
            f'export function loadLifeosConfig() {{ return {{ principal: {{ timezone: "Europe/London" }}, paths: {{ userDir: "{self.root / "USER"}" }} }}; }}\n',
            encoding="utf-8",
        )
        (self.root / "USER" / "TELOS" / "STRATEGIES.md").write_text(
            "# Strategies\n", encoding="utf-8"
        )

    def lifeos_env(self) -> dict[str, str]:
        env = os.environ.copy()
        env["LIFEOS_DIR"] = str(self.root)
        return env

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_update(
        self,
        filename: str,
        content: str = "- Added entry",
        description: str = "Added entry",
        *,
        env: dict[str, str] | None = None,
        extra_args: tuple[str, ...] = (),
    ) -> subprocess.CompletedProcess[str]:
        environment = env or self.lifeos_env()
        return subprocess.run(
            ["bun", str(SCRIPT), filename, *extra_args],
            input=json.dumps({"content": content, "changeDescription": description}),
            env=environment,
            text=True,
            capture_output=True,
            check=False,
        )

    def run_update_with_backup_close_failure(self, filename: str) -> subprocess.CompletedProcess[str]:
        harness = self.root / "close-failure-harness.ts"
        harness.write_text(
            f'import {{ main }} from "{SCRIPT.as_uri()}";\n'
            'await main(() => { throw new Error("injected backup close failure"); });\n',
            encoding="utf-8",
        )
        return subprocess.run(
            ["bun", str(harness), filename],
            input=json.dumps({"content": "- Added entry", "changeDescription": "Added entry"}),
            env=self.lifeos_env(),
            text=True,
            capture_output=True,
            check=False,
        )

    def test_updates_backs_up_and_records_change(self) -> None:
        result = self.run_update(
            "STRATEGIES.md", "- Prefer inspectable delivery", "Added career strategy"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            "- Prefer inspectable delivery",
            (self.root / "USER" / "TELOS" / "STRATEGIES.md").read_text(),
        )
        self.assertIn(
            "Added career strategy",
            (self.root / "USER" / "TELOS" / "updates.md").read_text(),
        )
        self.assertEqual(
            len(list((self.root / "USER" / "TELOS" / "Backups").glob("STRATEGIES-*.md"))),
            1,
        )

    def test_rejects_unsupported_file_without_writing(self) -> None:
        result = self.run_update("PRIVATE.md", "secret", "invalid")
        self.assertEqual(result.returncode, 1)
        self.assertIn("Invalid file", result.stderr)
        self.assertFalse((self.root / "USER" / "TELOS" / "PRIVATE.md").exists())

    def test_rejects_blank_content_and_description(self) -> None:
        for content, description in [("", "description"), ("content", " ")]:
            with self.subTest(content=content, description=description):
                result = self.run_update("STRATEGIES.md", content, description)
                self.assertEqual(result.returncode, 1)
                self.assertIn("non-empty strings", result.stderr)
        self.assertEqual(
            (self.root / "USER" / "TELOS" / "STRATEGIES.md").read_text(),
            "# Strategies\n",
        )

    def test_does_not_accept_private_values_as_arguments(self) -> None:
        result = self.run_update(
            "STRATEGIES.md",
            "secret content",
            "private description",
            extra_args=("secret content", "private description"),
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("Usage", result.stderr)

    def test_rejects_symlink_target(self) -> None:
        target = self.root / "USER" / "TELOS" / "STRATEGIES.md"
        target.unlink()
        target.symlink_to(self.root / "USER" / "TELOS" / "OTHER.md")
        result = self.run_update("STRATEGIES.md")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("symlink", result.stderr.lower())
        self.assertFalse((self.root / "USER" / "TELOS" / "OTHER.md").exists())

    def test_rejects_symlink_changelog_without_mutating_target(self) -> None:
        updates = self.root / "USER" / "TELOS" / "updates.md"
        updates.symlink_to(self.root / "USER" / "TELOS" / "OTHER-UPDATES.md")
        target = self.root / "USER" / "TELOS" / "STRATEGIES.md"
        before = target.read_bytes()
        result = self.run_update("STRATEGIES.md")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("symlink", result.stderr.lower())
        self.assertEqual(target.read_bytes(), before)
        self.assertFalse((self.root / "USER" / "TELOS" / "Backups").exists())

    def test_rejects_symlink_backup_directory_without_exposing_preimage(self) -> None:
        external = self.root / "external-backups"
        external.mkdir()
        backups = self.root / "USER" / "TELOS" / "Backups"
        backups.symlink_to(external, target_is_directory=True)
        target = self.root / "USER" / "TELOS" / "STRATEGIES.md"
        before = target.read_bytes()

        result = self.run_update("STRATEGIES.md")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("symlinked directory", result.stderr)
        self.assertEqual(target.read_bytes(), before)
        self.assertEqual(list(external.iterdir()), [])

    def test_rejects_invalid_backup_storage_before_creating_missing_target(self) -> None:
        external = self.root / "external-backups"
        external.mkdir()
        backups = self.root / "USER" / "TELOS" / "Backups"
        backups.symlink_to(external, target_is_directory=True)
        target = self.root / "USER" / "TELOS" / "BOOKS.md"

        result = self.run_update("BOOKS.md")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("symlinked directory", result.stderr)
        self.assertFalse(target.exists())
        self.assertEqual(list(external.iterdir()), [])

    def test_rejects_symlink_telos_directory(self) -> None:
        telos = self.root / "USER" / "TELOS"
        actual = self.root / "external-telos"
        telos.rename(actual)
        telos.symlink_to(actual, target_is_directory=True)

        result = self.run_update("STRATEGIES.md")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("symlinked directory", result.stderr)
        self.assertEqual((actual / "STRATEGIES.md").read_text(), "# Strategies\n")

    def test_rejects_symlinked_ancestor_beneath_lifeos_root(self) -> None:
        external = self.root / "external-owner"
        configured_user = external / "USER"
        configured_telos = configured_user / "TELOS"
        configured_telos.mkdir(parents=True)
        (configured_telos / "STRATEGIES.md").write_text("# Strategies\n", encoding="utf-8")
        ancestor = self.root / "owner-link"
        ancestor.symlink_to(external, target_is_directory=True)
        (self.root / "TOOLS" / "LifeosConfig.ts").write_text(
            f'export function loadLifeosConfig() {{ return {{ principal: {{ timezone: "Europe/London" }}, paths: {{ userDir: "{ancestor / "USER"}" }} }}; }}\n',
            encoding="utf-8",
        )

        result = self.run_update("STRATEGIES.md")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("symlinked directory", result.stderr)
        self.assertEqual((configured_telos / "STRATEGIES.md").read_text(), "# Strategies\n")
        self.assertFalse((configured_telos / "Backups").exists())

    def test_rolls_back_target_when_changelog_update_fails(self) -> None:
        updates = self.root / "USER" / "TELOS" / "updates.md"
        updates.mkdir()
        target = self.root / "USER" / "TELOS" / "STRATEGIES.md"
        before = target.read_bytes()

        result = self.run_update("STRATEGIES.md")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("without changing STRATEGIES.md", result.stderr)
        self.assertEqual(target.read_bytes(), before)
        self.assertEqual(list((self.root / "USER" / "TELOS" / "Backups").iterdir()), [])

    def test_new_target_is_removed_when_changelog_update_fails(self) -> None:
        updates = self.root / "USER" / "TELOS" / "updates.md"
        updates.mkdir()
        target = self.root / "USER" / "TELOS" / "BOOKS.md"

        result = self.run_update("BOOKS.md")

        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(target.exists())
        self.assertEqual(list((self.root / "USER" / "TELOS" / "Backups").iterdir()), [])

    def test_empty_target_backup_preserves_exact_empty_preimage(self) -> None:
        target = self.root / "USER" / "TELOS" / "BOOKS.md"
        target.touch()

        result = self.run_update("BOOKS.md")

        self.assertEqual(result.returncode, 0, result.stderr)
        backup = next((self.root / "USER" / "TELOS" / "Backups").glob("BOOKS-*.md"))
        self.assertEqual(backup.read_bytes(), b"")
        self.assertIn("# BOOKS", target.read_text())

    def test_backup_close_failure_leaves_no_transaction_state(self) -> None:
        target = self.root / "USER" / "TELOS" / "STRATEGIES.md"
        before = target.read_bytes()

        result = self.run_update_with_backup_close_failure("STRATEGIES.md")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("injected backup close failure", result.stderr)
        self.assertEqual(target.read_bytes(), before)
        self.assertFalse((self.root / "USER" / "TELOS" / "updates.md").exists())
        self.assertEqual(list((self.root / "USER" / "TELOS" / "Backups").iterdir()), [])

    def test_requires_an_explicit_configured_root(self) -> None:
        env = self.lifeos_env()
        env.pop("LIFEOS_DIR", None)
        env.pop("CODEX_LIFEOS_DIR", None)
        env["HOME"] = str(self.root)
        result = self.run_update("STRATEGIES.md", env=env)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must be set explicitly", result.stderr)
        self.assertFalse((self.root / ".codex" / "LIFEOS").exists())

    def test_uses_configured_user_directory_instead_of_root_user_path(self) -> None:
        configured_user = self.root / "configured-user"
        configured_telos = configured_user / "TELOS"
        configured_telos.mkdir(parents=True)
        (configured_telos / "STRATEGIES.md").write_text("# Strategies\n", encoding="utf-8")
        (self.root / "TOOLS" / "LifeosConfig.ts").write_text(
            f'export function loadLifeosConfig() {{ return {{ principal: {{ timezone: "Europe/London" }}, paths: {{ userDir: "{configured_user}" }} }}; }}\n',
            encoding="utf-8",
        )

        result = self.run_update("STRATEGIES.md")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Added entry", (configured_telos / "STRATEGIES.md").read_text())
        self.assertFalse((self.root / "USER" / "TELOS" / "updates.md").exists())

    def test_preserves_crlf_footer(self) -> None:
        target = self.root / "USER" / "TELOS" / "STRATEGIES.md"
        target.write_bytes(b"# Strategies\r\n- Existing\r\n---\r\n* Footer *\r\n")
        result = self.run_update("STRATEGIES.md", "- Added\nsecond line", "Added CRLF entry")
        self.assertEqual(result.returncode, 0, result.stderr)
        updated = target.read_bytes()
        self.assertIn(b"- Added\r\nsecond line\r\n---\r\n* Footer *\r\n", updated)
        self.assertNotIn(b"\n---\n", updated)

    def test_replacements_write_complete_bytes_without_padding(self) -> None:
        result = self.run_update("STRATEGIES.md", "- Short", "Short entry")
        self.assertEqual(result.returncode, 0, result.stderr)
        target = self.root / "USER" / "TELOS" / "STRATEGIES.md"
        updates = self.root / "USER" / "TELOS" / "updates.md"
        self.assertNotIn(b"\x00", target.read_bytes())
        self.assertNotIn(b"\x00", updates.read_bytes())

    def test_preserves_changelog_crlf_without_mixed_endings(self) -> None:
        updates = self.root / "USER" / "TELOS" / "updates.md"
        updates.write_bytes(b"# TELOS Updates\r\n\r\n## Future Changes\r\nDocument changes below.\r\n")
        result = self.run_update("STRATEGIES.md", "- CRLF log", "CRLF log entry")
        self.assertEqual(result.returncode, 0, result.stderr)
        updated = updates.read_bytes()
        self.assertNotIn(b"\n", updated.replace(b"\r\n", b""))
        self.assertIn(b"CRLF log entry\r\n", updated)

    def test_fails_closed_when_changelog_lock_is_held(self) -> None:
        lock = self.root / "USER" / "TELOS" / ".updates.lock"
        lock.mkdir()
        target = self.root / "USER" / "TELOS" / "STRATEGIES.md"
        before = target.read_bytes()
        env = self.lifeos_env()
        env["TELOS_UPDATES_LOCK_TIMEOUT_MS"] = "10"
        result = self.run_update("STRATEGIES.md", env=env)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("changelog lock", result.stderr)
        self.assertIn(".updates.lock", result.stderr)
        self.assertIn("confirm no updater is running", result.stderr)
        self.assertEqual(target.read_bytes(), before)
        self.assertEqual(list((self.root / "USER" / "TELOS").glob("Backups/*")), [])

    def test_serializes_concurrent_changelog_updates(self) -> None:
        processes = [
            subprocess.Popen(
                ["bun", str(SCRIPT), "STRATEGIES.md"],
                env=self.lifeos_env(),
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            for _ in range(2)
        ]
        for index, process in enumerate(processes):
            assert process.stdin is not None
            process.stdin.write(json.dumps({"content": f"- Concurrent {index}", "changeDescription": f"Concurrent {index}"}))
            process.stdin.close()
        results = []
        for process in processes:
            self.assertEqual(process.wait(timeout=10), 0)
            assert process.stdout is not None and process.stderr is not None
            results.append((process.stdout.read(), process.stderr.read()))
            process.stdout.close()
            process.stderr.close()
        for stdout, stderr in results:
            self.assertEqual(stderr, "", stderr)
        updates = (self.root / "USER" / "TELOS" / "updates.md").read_text()
        self.assertIn("Concurrent 0", updates)
        self.assertIn("Concurrent 1", updates)

    def test_backup_names_are_collision_safe_and_retained(self) -> None:
        for index in range(4):
            result = self.run_update("STRATEGIES.md", f"- Entry {index}", f"Entry {index}")
            self.assertEqual(result.returncode, 0, result.stderr)
            time.sleep(0.001)
        backups = list((self.root / "USER" / "TELOS" / "Backups").glob("STRATEGIES-*.md"))
        self.assertEqual(len(backups), 4)
        self.assertEqual(len({backup.name for backup in backups}), 4)

    def test_updater_remains_executable(self) -> None:
        self.assertTrue(SCRIPT.stat().st_mode & stat.S_IXUSR)

    def test_workflow_command_uses_documented_stdin_contract(self) -> None:
        workflow = SCRIPT.parent.parent / "Workflows" / "Update.md"
        content = workflow.read_text(encoding="utf-8")
        self.assertIn('bun "${CODEX_HOME:-$HOME/.codex}/skills/telos/Tools/UpdateTelos.ts" "$FILE"', content)
        self.assertNotIn("$UPDATE_JSON", content)
        self.assertIn('JSON on stdin', content)

    def test_documented_workflow_command_executes_with_json_stdin(self) -> None:
        workflow = SCRIPT.parent.parent / "Workflows" / "Update.md"
        content = workflow.read_text(encoding="utf-8")
        match = re.search(r"!`(FILE=\"\$1\"; .*?bun .*?\"\$FILE\")`", content)
        self.assertIsNotNone(match)
        command = match.group(1)
        self.assertNotIn("$HOME/.codex/LIFEOS", command)
        skill_tools = self.root / "skills" / "telos"
        skill_tools.parent.mkdir()
        skill_tools.symlink_to(SCRIPT.parent.parent, target_is_directory=True)
        env = self.lifeos_env()
        env["CODEX_HOME"] = str(self.root)
        result = subprocess.run(
            ["bash", "-c", command, "workflow", "STRATEGIES.md"],
            input=json.dumps({"content": "- Workflow entry", "changeDescription": "Workflow test"}),
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Workflow entry", (self.root / "USER" / "TELOS" / "STRATEGIES.md").read_text())

    def test_workflow_uses_configured_owner_paths_and_current_runtime(self) -> None:
        workflow = SCRIPT.parent.parent / "Workflows" / "Update.md"
        content = workflow.read_text(encoding="utf-8")
        commands = "\n".join(
            line for line in content.splitlines() if line.startswith("!`")
        )

        self.assertNotIn("$HOME/.codex/LIFEOS", content)
        self.assertNotIn("/USER/TELOS", commands)
        self.assertNotIn("~/.claude/skills/Telos", content)
        self.assertNotIn("bottom of `${LIFEOS_DIR", content)
        self.assertIn("LifeosConfig.paths.userDir/TELOS", content)
        self.assertIn("updates.md", content)
        self.assertIn("Updates.md", content)
        self.assertIn('${CODEX_HOME:-$HOME/.codex}/skills/telos/Tools/UpdateTelos.ts', content)
        self.assertNotIn("printf '%s' '{\"content\"", content)


if __name__ == "__main__":
    unittest.main()
