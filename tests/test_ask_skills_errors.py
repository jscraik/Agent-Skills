import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

# Add scripts/lib to path for ask package imports.
repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root / "scripts" / "lib"))

from ask.commands.skills import audit_skill, _summarize_family_benchmark_failure


class TestAskSkillsErrors(unittest.TestCase):
    def test_summarize_family_benchmark_failure_extracts_failures(self):
        stdout = "\n".join([
            "[family-benchmark] checked skills:",
            "  - backend/cli-spec",
            "[family-benchmark] failures:",
            "  - FAIL CONTRACT_SCHEMA [backend/cli-spec] contract issue one",
            "  - FAIL EVALS_SCHEMA [backend/cli-spec] eval issue two",
            "  - FAIL TASK_PROFILE_KEYS [backend/cli-spec] profile issue three",
            "  - FAIL BASELINE_REGRESSION [backend/cli-spec] baseline issue four",
        ])

        summary = _summarize_family_benchmark_failure(stdout=stdout, stderr="", limit=3)
        self.assertIsNotNone(summary)
        self.assertIn("FAIL CONTRACT_SCHEMA", summary)
        self.assertIn("FAIL EVALS_SCHEMA", summary)
        self.assertIn("FAIL TASK_PROFILE_KEYS", summary)
        self.assertIn("+1 more", summary)

    def test_summarize_family_benchmark_failure_falls_back_to_stderr(self):
        summary = _summarize_family_benchmark_failure(stdout="", stderr="baseline file missing")
        self.assertEqual(summary, "baseline file missing")

    @patch("ask.commands.skills.subprocess.run")
    def test_audit_skill_strict_includes_family_failure_context(self, mock_run):
        family_stdout = "\n".join([
            "[family-benchmark] failures:",
            "  - FAIL CONTRACT_SCHEMA [backend/cli-spec] contract issue one",
            "  - FAIL EVALS_SCHEMA [backend/cli-spec] eval issue two",
            "  - FAIL TASK_PROFILE_KEYS [backend/cli-spec] profile issue three",
            "  - FAIL BASELINE_REGRESSION [backend/cli-spec] baseline issue four",
        ])

        mock_run.side_effect = [
            subprocess.CompletedProcess(args=[], returncode=0, stdout="diagnostics ok", stderr=""),
            subprocess.CompletedProcess(args=[], returncode=0, stdout="security gate ok", stderr=""),
            subprocess.CompletedProcess(args=[], returncode=2, stdout=family_stdout, stderr=""),
        ]

        result = audit_skill(repo_root=repo_root, skill_path="backend/cli-spec", level="strict")

        self.assertEqual(result.status, "error")
        self.assertTrue(result.errors)
        error = result.errors[0]
        self.assertEqual(error.code, "ERR_VALIDATION")
        self.assertIn("Family benchmarks validation failed.", error.message)
        self.assertIn("First failures:", error.message)
        self.assertIn("FAIL CONTRACT_SCHEMA", error.message)
        self.assertIn("+1 more", error.message)
        self.assertIsNotNone(error.fix_suggestion)
        self.assertIn("data.family_benchmarks", error.fix_suggestion)


if __name__ == "__main__":
    unittest.main()
