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


if __name__ == "__main__":
    unittest.main()
