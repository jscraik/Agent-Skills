import os
import subprocess
import unittest
from typing import Optional


SYNC_SCRIPT = "Infrastructure/scripts/lifecycle-and-sync/sync_skills.sh"


def _run_sync_script(args: list[str], *, env: Optional[dict[str, str]] = None) -> subprocess.CompletedProcess[str]:
    """
    Run the sync skills shell script with the given command-line arguments and optional environment overrides.
    
    Parameters:
        args (list[str]): Command-line arguments to pass to the script (appended after the script path).
        env (Optional[dict[str, str]]): Environment variables to overlay on the current process environment; provided keys override existing ones.
    
    Returns:
        subprocess.CompletedProcess[str]: The completed process object containing `returncode`, `stdout`, and `stderr`.
    """
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
    def test_user_scope_flat_projection_delegates_to_ask_engine(self) -> None:
        with open(SYNC_SCRIPT, encoding="utf-8") as script_file:
            script = script_file.read()

        self.assertIn('"$sync_scope" == "user"', script)

    def test_rooted_projection_delegates_to_ask_engine_in_dry_run(self) -> None:
        """
        Verifies that running the sync script in workspace mode with the 'rooted' projection in dry-run mode delegates to the ask engine.
        
        Runs the script with ["--workspace", "--projection", "rooted", "--dry-run"] and asserts the process exits with code 0, that stdout contains "rooted", and that stdout contains the "Dry-run rooted projection" message.
        """
        result = _run_sync_script(["--workspace", "--projection", "rooted", "--dry-run"])

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("rooted", result.stdout)
        self.assertIn("Dry-run rooted projection", result.stdout)

    def test_project_local_is_legacy_workspace_alias(self) -> None:
        result = _run_sync_script(["--project-local", "--projection", "rooted", "--dry-run"])

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("rooted", result.stdout)

    def test_invalid_scope_fails_before_projection_policy(self) -> None:
        """
        Verifies the sync script exits with an invalid-scope error and does not reach projection-policy parsing when SYNC_SKILLS_SCOPE is set to an unsupported value.
        
        Asserts that the script returns exit code 2, emits "Invalid sync scope: elsewhere" to stderr, and does not include "Projection mode 'rooted' is parsed" in stderr.
        """
        result = _run_sync_script(["--projection", "rooted"], env={"SYNC_SKILLS_SCOPE": "elsewhere"})

        self.assertEqual(result.returncode, 2)
        self.assertIn("Invalid sync scope: elsewhere", result.stderr)
        self.assertNotIn("Projection mode 'rooted' is parsed", result.stderr)


if __name__ == "__main__":
    unittest.main()
