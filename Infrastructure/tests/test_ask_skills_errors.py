import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

# Add Infrastructure/scripts/lib to path for ask package imports.
repo_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(repo_root / "Infrastructure" / "scripts" / "lib"))

from ask.commands.skills import (
    _subprocess_env_with_uv_cache,
    _summarize_family_benchmark_failure,
    audit_skill,
    install_skill,
)


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

    @patch.dict("ask.commands.skills.os.environ", {"TMPDIR": "/tmp/codex-test"}, clear=True)
    def test_subprocess_env_defaults_uv_cache_to_tmp(self):
        env = _subprocess_env_with_uv_cache()

        self.assertEqual(env["UV_CACHE_DIR"], "/tmp/codex-test/agent-skills-uv-cache")

    @patch.dict("ask.commands.skills.os.environ", {"UV_CACHE_DIR": "/custom/uv-cache"}, clear=True)
    def test_subprocess_env_preserves_existing_uv_cache(self):
        env = _subprocess_env_with_uv_cache()

        self.assertEqual(env["UV_CACHE_DIR"], "/custom/uv-cache")

    @patch("ask.commands.skills._get_python_command", return_value=["python3"])
    @patch("ask.commands.skills.subprocess.run")
    def test_audit_skill_strict_includes_family_failure_context(self, mock_run, _mock_python):
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

    @patch("ask.commands.skills._get_python_command", return_value=["python3"])
    @patch("ask.commands.skills.subprocess.run")
    def test_audit_skill_strict_normalizes_skill_file_for_strict_gates(self, mock_run, _mock_python):
        mock_run.side_effect = [
            subprocess.CompletedProcess(args=[], returncode=0, stdout="diagnostics ok", stderr=""),
            subprocess.CompletedProcess(args=[], returncode=0, stdout="security gate ok", stderr=""),
            subprocess.CompletedProcess(args=[], returncode=0, stdout="family ok", stderr=""),
            subprocess.CompletedProcess(args=[], returncode=0, stdout="openclaw ok", stderr=""),
        ]

        result = audit_skill(repo_root=repo_root, skill_path="Skills/agent-ops/autofix/SKILL.md", level="strict")

        self.assertEqual(result.status, "success")
        for call in mock_run.call_args_list:
            self.assertIn("UV_CACHE_DIR", call.kwargs["env"])
            self.assertTrue(call.kwargs["env"]["UV_CACHE_DIR"].endswith("agent-skills-uv-cache"))
        security_cmd = mock_run.call_args_list[1].args[0]
        family_cmd = mock_run.call_args_list[2].args[0]
        openclaw_cmd = mock_run.call_args_list[3].args[0]
        self.assertIn("Skills/agent-ops/autofix", security_cmd)
        self.assertIn("Skills/agent-ops/autofix", family_cmd)
        self.assertIn("Skills/agent-ops/autofix", openclaw_cmd)
        self.assertNotIn("Skills/agent-ops/autofix/SKILL.md", security_cmd)
        self.assertNotIn("Skills/agent-ops/autofix/SKILL.md", family_cmd)
        self.assertNotIn("Skills/agent-ops/autofix/SKILL.md", openclaw_cmd)

    @patch("ask.commands.skills.subprocess.run")
    def test_install_skill_skips_validation_flag_when_unsupported(self, mock_run):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            (repo_root / "github").mkdir(parents=True, exist_ok=True)
            mock_run.side_effect = [
                subprocess.CompletedProcess(args=[], returncode=0, stdout="usage: installer [--url URL --dest DEST]", stderr=""),
                subprocess.CompletedProcess(
                    args=[],
                    returncode=0,
                    stdout="Installed review-duplication to /tmp/review-duplication",
                    stderr="",
                ),
            ]

            with patch("ask.commands.skills._get_python_command", return_value=["python3"]):
                result = install_skill(
                    repo_root=repo_root,
                    url="https://github.com/google-openai/openai-cli/tree/main/.openai/skills/review-duplication",
                    dest="github",
                )

        self.assertEqual(result.status, "success")
        self.assertEqual(result.data.get("validation_level"), "compat_skipped_unsupported")
        install_cmd = mock_run.call_args_list[1].args[0]
        self.assertNotIn("--validation-level", install_cmd)

    @patch("ask.commands.skills.subprocess.run")
    def test_install_skill_uses_validation_flag_when_supported(self, mock_run):
        """
        Verifies that when the installer advertises `--validation-level` in its usage output, install_skill enables and passes that flag.
        
        Mocks subprocess output so the first call returns usage text containing `--validation-level` and the second simulates a successful install. Asserts the result is successful, `result.data["validation_level"] == "compat"`, and the actual install command includes `--validation-level`.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            (repo_root / "github").mkdir(parents=True, exist_ok=True)
            mock_run.side_effect = [
                subprocess.CompletedProcess(args=[], returncode=0, stdout="usage: installer --validation-level", stderr=""),
                subprocess.CompletedProcess(
                    args=[],
                    returncode=0,
                    stdout="Installed review-duplication to /tmp/review-duplication",
                    stderr="",
                ),
            ]

            with patch("ask.commands.skills._get_python_command", return_value=["python3"]):
                result = install_skill(
                    repo_root=repo_root,
                    url="https://github.com/google-openai/openai-cli/tree/main/.openai/skills/review-duplication",
                    dest="github",
                )

        self.assertEqual(result.status, "success")
        self.assertEqual(result.data.get("validation_level"), "compat")
        install_cmd = mock_run.call_args_list[1].args[0]
        self.assertIn("--validation-level", install_cmd)

    @patch("ask.commands.skills.subprocess.run")
    def test_install_skill_remediate_requires_flag_support(self, mock_run):
        """
        Verifies that install_skill errors when remediation is requested but the installer does not support `--remediate`.
        
        Sets up a temporary repo with a `github` dest and mocks the installer usage output to omit `--remediate`. Calls install_skill(..., remediate=True) and asserts that the result has status "error", contains an `ERR_VALIDATION` error whose message mentions "does not support --remediate", and that the installer was probed exactly once (no install attempt).
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            (repo_root / "github").mkdir(parents=True, exist_ok=True)
            mock_run.side_effect = [
                subprocess.CompletedProcess(args=[], returncode=0, stdout="usage: installer [--url URL --dest DEST]", stderr=""),
            ]

            with patch("ask.commands.skills._get_python_command", return_value=["python3"]):
                result = install_skill(
                    repo_root=repo_root,
                    url="https://github.com/google-openai/openai-cli/tree/main/.openai/skills/review-duplication",
                    dest="github",
                    remediate=True,
                )

        self.assertEqual(result.status, "error")
        self.assertTrue(result.errors)
        self.assertEqual(result.errors[0].code, "ERR_VALIDATION")
        self.assertIn("does not support --remediate", result.errors[0].message)
        self.assertEqual(mock_run.call_count, 1)


if __name__ == "__main__":
    unittest.main()
