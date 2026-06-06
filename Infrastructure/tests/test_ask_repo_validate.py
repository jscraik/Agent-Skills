import io
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lifecycle-and-sync"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from ask.commands.repo import repo_validate


class _FakeCompletedProcess:
    def __init__(self, lines: list[str], returncode: int = 0):
        self.stdout = "".join(lines)
        self.returncode = returncode
        self.args: list[str] = []


class TestAskRepoValidate(unittest.TestCase):
    def test_repo_validate_streams_progress_and_parses_summary(self) -> None:
        lines = [
            "🔍 Running all validations...\n",
            "📊 Validating plan graphs...\n",
            "Validation summary:\n",
            "- required_failures: 0\n",
            "- warn_only_issues: 1\n",
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            stderr = io.StringIO()
            with patch(
                "ask.commands.repo.subprocess.run",
                return_value=_FakeCompletedProcess(lines, returncode=0),
            ):
                with redirect_stderr(stderr):
                    result = repo_validate(repo, ephemeral=True)

        self.assertEqual(result.status, "success")
        self.assertEqual(result.data["required_failures"], 0)
        self.assertEqual(result.data["warn_only_issues"], 1)
        self.assertEqual(result.data["raw_output"], "".join(lines))
        self.assertIn("📊 Validating plan graphs...", stderr.getvalue())

    def test_repo_validate_returns_error_when_summary_missing(self) -> None:
        lines = ["validator crashed before summary\n"]

        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            with patch(
                "ask.commands.repo.subprocess.run",
                return_value=_FakeCompletedProcess(lines, returncode=1),
            ):
                result = repo_validate(repo, ephemeral=True)

        self.assertEqual(result.status, "error")
        self.assertEqual(result.data["required_failures"], 1)
        self.assertEqual(result.errors[0].code, "ERR_VALIDATION")

    def test_repo_validate_forwards_scope_to_validate_all(self) -> None:
        lines = [
            "🔍 Running all validations...\n",
            "🎯 Validation scope: lint\n",
            "Validation summary:\n",
            "- required_failures: 0\n",
            "- warn_only_issues: 0\n",
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            with patch(
                "ask.commands.repo.subprocess.run",
                return_value=_FakeCompletedProcess(lines, returncode=0),
            ) as run:
                result = repo_validate(repo, ephemeral=True, scope="lint")

        self.assertEqual(result.status, "success")
        self.assertEqual(result.data["scope"], "lint")
        cmd = run.call_args.args[0]
        self.assertIn("--scope", cmd)
        self.assertIn("lint", cmd)

    def test_repo_validate_forwards_skills_sdk_scope_to_validate_all(self) -> None:
        lines = [
            "🔍 Running all validations...\n",
            "🎯 Validation scope: skills-sdk\n",
            "Validation summary:\n",
            "- required_failures: 0\n",
            "- warn_only_issues: 0\n",
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            with patch(
                "ask.commands.repo.subprocess.run",
                return_value=_FakeCompletedProcess(lines, returncode=0),
            ) as run:
                result = repo_validate(repo, ephemeral=True, scope="skills-sdk")

        self.assertEqual(result.status, "success")
        self.assertEqual(result.data["scope"], "skills-sdk")
        cmd = run.call_args.args[0]
        self.assertIn("--scope", cmd)
        self.assertIn("skills-sdk", cmd)


if __name__ == "__main__":
    unittest.main()
