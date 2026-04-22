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


class _FakePopen:
    def __init__(self, lines: list[str], returncode: int = 0):
        """
        Initialize a fake subprocess with predetermined stdout lines and an exit code.
        
        Parameters:
            lines (list[str]): Lines to be yielded by the subprocess's stdout iterator in order.
            returncode (int): Exit code that wait() will return; defaults to 0.
        """
        self.stdout = iter(lines)
        self.returncode = returncode

    def __enter__(self):
        """
        Return the context manager instance.
        
        Returns:
            self: The context manager instance to be bound to the target of the `with` statement.
        """
        return self

    def __exit__(self, exc_type, exc, tb):
        """
        Indicate that exceptions raised inside the context should propagate.
        
        @return:
            `False` to ensure any exception raised within the context manager is not suppressed and is re-raised.
        """
        return False

    def wait(self) -> int:
        """
        Return the preconfigured process exit code.
        
        Returns:
            int: The configured process return code.
        """
        return self.returncode


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
                "ask.commands.repo.subprocess.Popen",
                return_value=_FakePopen(lines, returncode=0),
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
                "ask.commands.repo.subprocess.Popen",
                return_value=_FakePopen(lines, returncode=1),
            ):
                result = repo_validate(repo, ephemeral=True)

        self.assertEqual(result.status, "error")
        self.assertEqual(result.data["required_failures"], 1)
        self.assertEqual(result.errors[0].code, "ERR_VALIDATION")


if __name__ == "__main__":
    unittest.main()
