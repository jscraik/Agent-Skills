import os
import subprocess
import unittest
from typing import Optional


SYNC_SCRIPT = "Infrastructure/scripts/lifecycle-and-sync/sync_skills.sh"


def _run_sync_script(args: list[str], *, env: Optional[dict[str, str]] = None) -> subprocess.CompletedProcess[str]:
    merged_env = os.environ.copy()
    merged_env.update(env or {})
    return subprocess.run(
        ["bash", SYNC_SCRIPT, *args],
        capture_output=True,
        text=True,
        timeout=30,
        env=merged_env,
        check=False,
    )


class TestSyncSkillsShellProjection(unittest.TestCase):
    def test_shell_entrypoint_delegates_runtime_mutation_to_ask_engine(self) -> None:
        with open(SYNC_SCRIPT, encoding="utf-8") as script_file:
            script = script_file.read()

        self.assertIn("ask_sync_args=(skills sync", script)
        self.assertIn('[[ "$dry_run" == "1" || "${SYNC_SKILLS_RESOLVED_PROJECTION_MODE:-flat}" != "flat" || "$plugin_cache_refresh" != "auto" ]]', script)
        self.assertIn('ask_sync_args+=(--plugin-cache-refresh "$plugin_cache_refresh")', script)
        self.assertIn("start_watchdog", script)
        self.assertIn("exit 124", script)

    def test_shell_entrypoint_keeps_flat_legacy_path_reachable(self) -> None:
        with open(SYNC_SCRIPT, encoding="utf-8") as script_file:
            script = script_file.read()

        delegated_block = script.split("ask_sync_args=(skills sync", 1)[0]
        self.assertNotIn('"$sync_scope" == "user"', delegated_block)
        self.assertNotIn('"$sync_scope" == "workspace"', delegated_block)

    def test_rooted_projection_delegates_to_ask_engine_in_dry_run(self) -> None:
        result = _run_sync_script(["--workspace", "--projection", "rooted", "--dry-run"])

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("rooted", result.stdout)
        self.assertIn("Dry-run rooted projection", result.stdout)

    def test_project_local_is_legacy_workspace_alias(self) -> None:
        result = _run_sync_script(["--project-local", "--projection", "rooted", "--dry-run"])

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("rooted", result.stdout)

    def test_invalid_scope_fails_before_projection_policy(self) -> None:
        result = _run_sync_script(["--projection", "rooted"], env={"SYNC_SKILLS_SCOPE": "elsewhere"})

        self.assertEqual(result.returncode, 2)
        self.assertIn("Invalid sync scope: elsewhere", result.stderr)
        self.assertNotIn("Projection mode 'rooted' is parsed", result.stderr)

    def test_user_scope_reaches_legacy_shell_path(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory() as tmp_home:
            result = _run_sync_script(
                ["--user", "--dry-run"],
                env={"HOME": tmp_home},
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("user", result.stdout.lower())

    def test_plugin_cache_only_delegates_to_ask_engine(self) -> None:
        result = _run_sync_script(["--workspace", "--plugin-cache-refresh", "only", "--dry-run"])

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("plugin runtime cache refresh only", result.stdout)
        self.assertIn(".agents/plugins-runtime/cache", result.stdout)

    def test_invalid_plugin_cache_refresh_mode_fails(self) -> None:
        result = _run_sync_script(["--workspace", "--plugin-cache-refresh", "sometimes", "--dry-run"])

        self.assertEqual(result.returncode, 2)
        self.assertIn("Invalid --plugin-cache-refresh value: sometimes", result.stderr)


if __name__ == "__main__":
    unittest.main()
