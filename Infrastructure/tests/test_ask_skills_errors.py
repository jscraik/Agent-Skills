import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

# Add Infrastructure/scripts/lib to path for ask package imports.
repo_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(repo_root / "Infrastructure" / "scripts" / "lib"))

from ask.commands.skills_impl import (
    _subprocess_env_with_uv_cache,
    _summarize_family_benchmark_failure,
    _write_tessl_tile_wrapper,
    audit_skill,
    external_review_skill,
    install_skill,
)
from ask.skill_review_dashboard import render_skill_review_dashboard


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

    @patch.dict("ask.commands.skills_impl.os.environ", {"TMPDIR": "/tmp/codex-test"}, clear=True)
    def test_subprocess_env_defaults_uv_cache_to_tmp(self):
        env = _subprocess_env_with_uv_cache()

        self.assertEqual(env["UV_CACHE_DIR"], "/tmp/codex-test/agent-skills-uv-cache")

    @patch.dict("ask.commands.skills_impl.os.environ", {"UV_CACHE_DIR": "/custom/uv-cache"}, clear=True)
    def test_subprocess_env_preserves_existing_uv_cache(self):
        env = _subprocess_env_with_uv_cache()

        self.assertEqual(env["UV_CACHE_DIR"], "/custom/uv-cache")

    def test_tessl_wrapper_includes_package_local_support_dirs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            skill_dir = repo_root / "Plugins/harness-engineering/skills/he-phase-work"
            shared_refs = repo_root / "Plugins/harness-engineering/references"
            skill_dir.mkdir(parents=True)
            shared_refs.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                "---\nname: he-phase-work\ndescription: Use when running phase work.\n---\n\n"
                "[shared](../../references/deferred-context-index.md)\n",
                encoding="utf-8",
            )
            (skill_dir / "references").mkdir()
            (skill_dir / "references/local.md").write_text("local", encoding="utf-8")
            (shared_refs / "deferred-context-index.md").write_text("shared", encoding="utf-8")

            tile_path, info = _write_tessl_tile_wrapper(
                repo_root,
                "Plugins/harness-engineering/skills/he-phase-work",
                repo_root / "tmp-tessl",
            )

            tile_skill_dir = Path(info["review_path"])
            tile_root = tile_path.parent
            self.assertTrue(tile_path.is_file())
            self.assertEqual((tile_skill_dir / "SKILL.md").read_text(encoding="utf-8"), (skill_dir / "SKILL.md").read_text(encoding="utf-8"))
            self.assertFalse((tile_root / "references").exists())
            self.assertEqual((tile_skill_dir / "references" / "local.md").read_text(encoding="utf-8"), "local")
            self.assertFalse((tile_skill_dir / ".." / ".." / "references").resolve().exists())

    @patch("ask.commands.skills_impl._get_python_command", return_value=["python3"])
    @patch("ask.commands.skills_impl.subprocess.run")
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

    @patch("ask.commands.skills_impl._get_python_command", return_value=["python3"])
    @patch("ask.commands.skills_impl.subprocess.run")
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

    @patch("ask.commands.skills_impl.subprocess.run")
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

            with patch("ask.commands.skills_impl._get_python_command", return_value=["python3"]):
                result = install_skill(
                    repo_root=repo_root,
                    url="https://github.com/google-openai/openai-cli/tree/main/.openai/skills/review-duplication",
                    dest="github",
                )

        self.assertEqual(result.status, "success")
        self.assertEqual(result.data.get("validation_level"), "compat_skipped_unsupported")
        install_cmd = mock_run.call_args_list[1].args[0]
        self.assertNotIn("--validation-level", install_cmd)

    @patch("ask.commands.skills_impl.subprocess.run")
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

            with patch("ask.commands.skills_impl._get_python_command", return_value=["python3"]):
                result = install_skill(
                    repo_root=repo_root,
                    url="https://github.com/google-openai/openai-cli/tree/main/.openai/skills/review-duplication",
                    dest="github",
                )

        self.assertEqual(result.status, "success")
        self.assertEqual(result.data.get("validation_level"), "compat")
        install_cmd = mock_run.call_args_list[1].args[0]
        self.assertIn("--validation-level", install_cmd)

    @patch("ask.commands.skills_impl.subprocess.run")
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

            with patch("ask.commands.skills_impl._get_python_command", return_value=["python3"]):
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

    @patch("ask.commands.skills_impl.audit_skill")
    @patch("ask.commands.skills_impl.shutil.which")
    @patch("ask.commands.skills_impl.subprocess.run")
    def test_external_review_runs_tessl_review_by_default(
        self,
        mock_run,
        mock_which,
        mock_audit,
    ):
        """
        Verify that external_review_skill runs plugin-eval and tessl (lint and review) by default and records expected policy and tessl outputs.
        
        Asserts that:
        - The overall result status is "success".
        - Policy fields indicate no_publish and not using npx.
        - plugin-eval, tessl lint, and tessl review stages are marked "success".
        - Exactly three subprocess invocations occur and none invoke "npx" or "publish".
        - The HOME environment used for tessl invocations does not contain the "agent-skills-tessl-" marker.
        - The tessl review invocation uses the arguments sequence ["skill", "review", "--json", "--threshold", "95", <skill_dir>].
        - The returned tessl_tile marks support_refs_included as truthy.
        
        Parameters:
            mock_run: patched subprocess.run used to simulate external tool invocations.
            mock_which: patched shutil.which used to indicate presence of required binaries.
            mock_audit: patched audit_skill used to simulate a prior audit result.
        """
        skill_dir = "Skills/backend-platform/example-skill"
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            target = repo_root / skill_dir
            target.mkdir(parents=True)
            (target / "SKILL.md").write_text("---\nname: example-skill\n---\n\n# Example\n", encoding="utf-8")

            audit = type("AuditResult", (), {})()
            audit.status = "success"
            audit.data = {"diagnostics": {"exit_code": 0}}
            audit.errors = []
            mock_audit.return_value = audit
            mock_which.side_effect = lambda name: f"/usr/local/bin/{name}" if name in {"plugin-eval", "tessl"} else None
            mock_run.side_effect = [
                subprocess.CompletedProcess(
                    args=["/usr/local/bin/plugin-eval", "analyze", skill_dir, "--format", "markdown"],
                    returncode=0,
                    stdout="Score: 91/100\nGrade: A\nRisk: low\nChecks: 0 fail, 0 warn",
                    stderr="",
                ),
                subprocess.CompletedProcess(
                    args=["/usr/local/bin/tessl", "skill", "lint", skill_dir],
                    returncode=0,
                    stdout="tessl lint ok",
                    stderr="",
                ),
                subprocess.CompletedProcess(
                    args=["/usr/local/bin/tessl", "skill", "review", "--json", "--threshold", "95", skill_dir],
                    returncode=0,
                    stdout='{"reviewScore": 96, "summary": "ok"}',
                    stderr="",
                ),
            ]

            result = external_review_skill(repo_root=repo_root, skill_path=skill_dir)

        self.assertEqual(result.status, "success")
        self.assertTrue(result.data["policy"]["no_publish"])
        self.assertFalse(result.data["policy"]["uses_npx"])
        self.assertEqual(result.data["plugin_eval"]["status"], "success")
        self.assertEqual(result.data["tessl_lint"]["status"], "success")
        self.assertEqual(result.data["tessl_review"]["status"], "success")
        self.assertEqual(mock_run.call_count, 3)
        for call in mock_run.call_args_list:
            self.assertNotIn("npx", call.args[0])
            self.assertNotIn("publish", call.args[0])
        tessl_call = mock_run.call_args_list[1]
        self.assertNotIn("agent-skills-tessl-", tessl_call.kwargs["env"].get("HOME", ""))
        review_call = mock_run.call_args_list[2]
        self.assertEqual(review_call.args[0][1:3], ["skill", "review"])
        self.assertEqual(review_call.args[0][3:5], ["--json", "--threshold"])
        self.assertEqual(review_call.args[0][5], "95")
        self.assertNotIn("agent-skills-tessl-", review_call.kwargs["env"].get("HOME", ""))
        self.assertTrue(result.data["tessl_tile"]["support_refs_included"])

    @patch("ask.commands.skills_impl.audit_skill")
    @patch("ask.commands.skills_impl.shutil.which")
    @patch("ask.commands.skills_impl.subprocess.run")
    def test_external_review_dashboard_writes_local_html(
        self,
        mock_run,
        mock_which,
        mock_audit,
    ):
        skill_dir = "Plugins/skill-factory/skills/code_quality_review/example-skill"
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            target = repo_root / skill_dir
            target.mkdir(parents=True)
            (target / "SKILL.md").write_text("---\nname: example-skill\ndescription: Use when reviewing examples.\n---\n\n# Example\n", encoding="utf-8")

            audit = type("AuditResult", (), {})()
            audit.status = "success"
            audit.data = {"openclaw": {"stdout": "Summary: 0 critical · 0 warn"}}
            audit.errors = []
            mock_audit.return_value = audit
            mock_which.side_effect = lambda name: f"/usr/local/bin/{name}" if name in {"plugin-eval", "tessl"} else None
            mock_run.side_effect = [
                subprocess.CompletedProcess(args=[], returncode=0, stdout="Score: 91/100\nGrade: A\nRisk: low\nChecks: 0 fail, 0 warn", stderr=""),
                subprocess.CompletedProcess(args=[], returncode=0, stdout="Overall: PASSED (0 errors, 0 warnings)", stderr=""),
                subprocess.CompletedProcess(
                    args=[],
                    returncode=0,
                    stdout=(
                        "Review Score: 92%\n"
                        "Description: 100%\n"
                        "Content: 85%\n"
                        "  specificity: 3/3 - Specific trigger terms.\n"
                        "  conciseness: 2/3 - Slightly verbose.\n"
                        "    Suggestions:\n"
                        "      - Tighten repeated guidance.\n"
                    ),
                    stderr="",
                ),
            ]

            result = external_review_skill(
                repo_root=repo_root,
                skill_path=skill_dir,
                audit_level="compat",
                report_path="Infrastructure/artifacts/skill-reviews/example-skill.json",
                dashboard=True,
                dashboard_path="Infrastructure/artifacts/skill-reviews/example-skill.html",
            )

            html_path = repo_root / result.data["dashboard_path"]
            html_text = html_path.read_text(encoding="utf-8")

        self.assertEqual(result.status, "success")
        self.assertEqual(result.data["dashboard_path"], "Infrastructure/artifacts/skill-reviews/example-skill.html")
        self.assertEqual(result.data["dashboard_url"], "Infrastructure/artifacts/skill-reviews/example-skill.html")
        self.assertIn("ASK Local Review", html_text)
        self.assertIn('data-auto-refresh-seconds="0"', html_text)
        self.assertIn("Static evidence snapshot", html_text)
        self.assertIn('role="tablist"', html_text)
        self.assertIn('role="tabpanel"', html_text)
        self.assertIn("Quality", html_text)
        self.assertIn("Evals Not Run Yet", html_text)
        self.assertIn("Snyk Advisory", html_text)
        self.assertIn("local_internal_only", html_text)
        self.assertIn("disabled_until_requested", html_text)

    def test_review_dashboard_reads_openclaw_guard_security_output(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            report_path = repo_root / "Infrastructure/artifacts/skill-reviews/example-skill.json"
            report_path.parent.mkdir(parents=True)
            report_path.write_text(
                json.dumps({
                    "status": "success",
                    "data": {
                        "target": "Plugins/skill-factory/skills/code_quality_review/example-skill",
                        "ask_audit": {
                            "data": {
                                "openclaw_guard": {
                                    "status": "warning",
                                    "stdout": "Summary: 0 critical - 2 warn\nwarning: capability boundary drift",
                                }
                            }
                        },
                        "plugin_eval": {"stdout": "Score: 88/100\nGrade: B"},
                        "tessl_review": {"stdout": "Review Score: 90%\nDescription: 100%\nContent: 80%"},
                    },
                    "errors": [],
                }),
                encoding="utf-8",
            )

            html_path = repo_root / "Infrastructure/artifacts/skill-reviews/example-skill.html"
            render_skill_review_dashboard(report_path=report_path, output_path=html_path, repo_root=repo_root)
            html_text = html_path.read_text(encoding="utf-8")

        self.assertIn("warning: capability boundary drift", html_text)
        self.assertIn(">70%</span>", html_text)

    @patch("ask.commands.skills_impl.audit_skill")
    @patch("ask.commands.skills_impl.shutil.which")
    @patch("ask.commands.skills_impl.subprocess.run")
    def test_external_review_blocks_snyk_when_cli_is_missing(
        self,
        mock_run,
        mock_which,
        mock_audit,
    ):
        skill_dir = "Skills/backend-platform/example-skill"
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            target = repo_root / skill_dir
            target.mkdir(parents=True)
            (target / "SKILL.md").write_text("---\nname: example-skill\n---\n\n# Example\n", encoding="utf-8")

            audit = type("AuditResult", (), {})()
            audit.status = "success"
            audit.data = {"diagnostics": {"exit_code": 0}}
            audit.errors = []
            mock_audit.return_value = audit
            mock_which.side_effect = lambda name: f"/usr/local/bin/{name}" if name in {"plugin-eval", "tessl"} else None
            mock_run.side_effect = [
                subprocess.CompletedProcess(args=[], returncode=0, stdout="Score: 91/100\nGrade: A", stderr=""),
                subprocess.CompletedProcess(args=[], returncode=0, stdout="Overall: PASSED (0 errors, 0 warnings)", stderr=""),
                subprocess.CompletedProcess(args=[], returncode=0, stdout="Review Score: 90%", stderr=""),
            ]

            result = external_review_skill(repo_root=repo_root, skill_path=skill_dir, include_snyk=True)

        self.assertEqual(result.status, "error")
        self.assertEqual(result.data["snyk"]["status"], "blocked_missing_binary")
        self.assertEqual(mock_run.call_count, 3)
        self.assertTrue(any(error.code == "ERR_DEPENDENCY" for error in result.errors))

    @patch("ask.commands.skills_impl.audit_skill")
    @patch("ask.commands.skills_impl.shutil.which")
    @patch("ask.commands.skills_impl.subprocess.run")
    def test_external_review_can_include_snyk_advisory(
        self,
        mock_run,
        mock_which,
        mock_audit,
    ):
        skill_dir = "Skills/backend-platform/example-skill"
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            target = repo_root / skill_dir
            target.mkdir(parents=True)
            (target / "SKILL.md").write_text("---\nname: example-skill\n---\n\n# Example\n", encoding="utf-8")

            audit = type("AuditResult", (), {})()
            audit.status = "success"
            audit.data = {"diagnostics": {"exit_code": 0}}
            audit.errors = []
            mock_audit.return_value = audit
            mock_which.side_effect = lambda name: f"/usr/local/bin/{name}" if name in {"plugin-eval", "tessl", "snyk"} else None
            mock_run.side_effect = [
                subprocess.CompletedProcess(args=[], returncode=0, stdout="Score: 91/100\nGrade: A", stderr=""),
                subprocess.CompletedProcess(args=[], returncode=0, stdout="Overall: PASSED (0 errors, 0 warnings)", stderr=""),
                subprocess.CompletedProcess(args=[], returncode=0, stdout="Review Score: 90%", stderr=""),
                subprocess.CompletedProcess(
                    args=[],
                    returncode=0,
                    stdout='{"ok": true, "vulnerabilities": [], "summary": "No known vulnerabilities"}',
                    stderr="",
                ),
            ]

            result = external_review_skill(repo_root=repo_root, skill_path=skill_dir, include_snyk=True)

        self.assertEqual(result.status, "success")
        self.assertEqual(result.data["snyk"]["status"], "success")
        self.assertEqual(mock_run.call_count, 4)
        snyk_cmd = mock_run.call_args_list[3].args[0]
        self.assertEqual(
            snyk_cmd[1:5],
            ["test", "--all-projects", "--detection-depth=6", "--severity-threshold=high"],
        )
        self.assertIn(skill_dir, snyk_cmd)

    @patch("ask.commands.skills_impl.audit_skill")
    @patch("ask.commands.skills_impl.shutil.which")
    @patch("ask.commands.skills_impl.subprocess.run")
    def test_external_review_marks_snyk_not_applicable_for_skill_only_folder(
        self,
        mock_run,
        mock_which,
        mock_audit,
    ):
        skill_dir = "Skills/backend-platform/example-skill"
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            target = repo_root / skill_dir
            target.mkdir(parents=True)
            (target / "SKILL.md").write_text("---\nname: example-skill\n---\n\n# Example\n", encoding="utf-8")

            audit = type("AuditResult", (), {})()
            audit.status = "success"
            audit.data = {"diagnostics": {"exit_code": 0}}
            audit.errors = []
            mock_audit.return_value = audit
            mock_which.side_effect = lambda name: f"/usr/local/bin/{name}" if name in {"plugin-eval", "tessl", "snyk"} else None
            mock_run.side_effect = [
                subprocess.CompletedProcess(args=[], returncode=0, stdout="Score: 91/100\nGrade: A", stderr=""),
                subprocess.CompletedProcess(args=[], returncode=0, stdout="Overall: PASSED (0 errors, 0 warnings)", stderr=""),
                subprocess.CompletedProcess(args=[], returncode=0, stdout="Review Score: 90%", stderr=""),
                subprocess.CompletedProcess(
                    args=[],
                    returncode=3,
                    stdout='{"ok": false, "error": "Could not detect supported target files"}',
                    stderr="",
                ),
            ]

            result = external_review_skill(repo_root=repo_root, skill_path=skill_dir, include_snyk=True)

        self.assertEqual(result.status, "success")
        self.assertEqual(result.data["snyk"]["status"], "not_applicable")
        self.assertIn("SKILL.md-first", result.data["snyk"]["reason"])

    @patch("ask.commands.skills_impl.audit_skill")
    @patch("ask.commands.skills_impl.shutil.which")
    @patch("ask.commands.skills_impl.subprocess.run")
    def test_external_review_fails_when_snyk_reports_advisory(
        self,
        mock_run,
        mock_which,
        mock_audit,
    ):
        skill_dir = "Skills/backend-platform/example-skill"
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            target = repo_root / skill_dir
            target.mkdir(parents=True)
            (target / "SKILL.md").write_text("---\nname: example-skill\n---\n\n# Example\n", encoding="utf-8")

            audit = type("AuditResult", (), {})()
            audit.status = "success"
            audit.data = {"diagnostics": {"exit_code": 0}}
            audit.errors = []
            mock_audit.return_value = audit
            mock_which.side_effect = lambda name: f"/usr/local/bin/{name}" if name in {"plugin-eval", "tessl", "snyk"} else None
            mock_run.side_effect = [
                subprocess.CompletedProcess(args=[], returncode=0, stdout="Score: 91/100\nGrade: A", stderr=""),
                subprocess.CompletedProcess(args=[], returncode=0, stdout="Overall: PASSED (0 errors, 0 warnings)", stderr=""),
                subprocess.CompletedProcess(args=[], returncode=0, stdout="Review Score: 90%", stderr=""),
                subprocess.CompletedProcess(
                    args=[],
                    returncode=1,
                    stdout='{"ok": false, "vulnerabilities": [{"severity": "high"}]}',
                    stderr="",
                ),
            ]

            result = external_review_skill(repo_root=repo_root, skill_path=skill_dir, include_snyk=True)

        self.assertEqual(result.status, "error")
        self.assertEqual(result.data["snyk"]["status"], "advisory")
        self.assertTrue(any(error.code == "ERR_VALIDATION" for error in result.errors))

    @patch("ask.commands.skills_impl.audit_skill")
    @patch("ask.commands.skills_impl.shutil.which")
    @patch("ask.commands.skills_impl.subprocess.run")
    def test_external_review_classifies_snyk_auth_blocker(
        self,
        mock_run,
        mock_which,
        mock_audit,
    ):
        skill_dir = "Skills/backend-platform/example-skill"
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            target = repo_root / skill_dir
            target.mkdir(parents=True)
            (target / "SKILL.md").write_text("---\nname: example-skill\n---\n\n# Example\n", encoding="utf-8")

            audit = type("AuditResult", (), {})()
            audit.status = "success"
            audit.data = {"diagnostics": {"exit_code": 0}}
            audit.errors = []
            mock_audit.return_value = audit
            mock_which.side_effect = lambda name: f"/usr/local/bin/{name}" if name in {"plugin-eval", "tessl", "snyk"} else None
            mock_run.side_effect = [
                subprocess.CompletedProcess(args=[], returncode=0, stdout="Score: 91/100\nGrade: A", stderr=""),
                subprocess.CompletedProcess(args=[], returncode=0, stdout="Overall: PASSED (0 errors, 0 warnings)", stderr=""),
                subprocess.CompletedProcess(args=[], returncode=0, stdout="Review Score: 90%", stderr=""),
                subprocess.CompletedProcess(
                    args=[],
                    returncode=2,
                    stdout="",
                    stderr="Use snyk auth to authenticate.",
                ),
            ]

            result = external_review_skill(repo_root=repo_root, skill_path=skill_dir, include_snyk=True)

        self.assertEqual(result.status, "error")
        self.assertEqual(result.data["snyk"]["status"], "blocked_auth")
        self.assertTrue(any(error.code == "ERR_AUTH" for error in result.errors))

    def test_review_dashboard_renders_latest_eval_scorecard(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            report_path = repo_root / "Infrastructure/artifacts/skill-reviews/example-skill.json"
            report_path.parent.mkdir(parents=True)
            report_path.write_text(
                json.dumps({
                    "status": "success",
                    "data": {
                        "target": "Plugins/skill-factory/skills/code_quality_review/example-skill",
                        "ask_audit": {"data": {"openclaw": {"stdout": "Summary: 0 critical · 0 warn"}}},
                        "plugin_eval": {"stdout": "Score: 88/100\nGrade: B"},
                        "tessl_review": {
                            "stdout": (
                                "Review Score: 90%\n"
                                "Description: 100%\n"
                                "Content: 80%\n"
                                "Overall: PASSED (0 errors, 0 warnings)\n"
                                "  actionability: 3/3 - Clear steps."
                            )
                        },
                    },
                    "errors": [],
                }),
                encoding="utf-8",
            )
            scorecard_path = repo_root / "Infrastructure/artifacts/skills/example-skill/20260515-180000-000000/scorecard.json"
            scorecard_path.parent.mkdir(parents=True)
            scorecard_path.write_text(
                """{
  "skill_path": "Plugins/skill-factory/skills/code_quality_review/example-skill",
  "run_id": "20260515-180000-000000",
  "eval_mode": "smoke",
  "runner_mode": "codex",
  "cases": [
    {"id": "happy-path", "name": "Happy Path", "category": "happy", "passed": true, "tier1_failures": [], "warnings": []},
    {"id": "edge-case", "name": "Edge Case", "category": "edge", "passed": false, "tier1_failures": ["missing required output"], "warnings": []}
  ]
}
""",
                encoding="utf-8",
            )

            html_path = repo_root / "Infrastructure/artifacts/skill-reviews/example-skill.html"
            render_skill_review_dashboard(report_path=report_path, output_path=html_path, repo_root=repo_root)
            html_text = html_path.read_text(encoding="utf-8")

        self.assertIn("Evaluation Results", html_text)
        self.assertIn("Happy Path", html_text)
        self.assertIn("Edge Case", html_text)
        self.assertIn("Not run", html_text)
        self.assertIn("50%", html_text)

    def test_review_dashboard_ignores_basename_only_scorecard_match(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            report_path = repo_root / "Infrastructure/artifacts/skill-reviews/example-skill.json"
            report_path.parent.mkdir(parents=True)
            report_path.write_text(
                json.dumps({
                    "status": "success",
                    "data": {
                        "target": "Skills/agent-ops/example-skill",
                        "ask_audit": {"data": {}},
                    },
                    "errors": [],
                }),
                encoding="utf-8",
            )
            scorecard_path = repo_root / "Infrastructure/artifacts/skills/example-skill/20260515-180000-000000/scorecard.json"
            scorecard_path.parent.mkdir(parents=True)
            scorecard_path.write_text(
                json.dumps({
                    "run_id": "20260515-180000-000000",
                    "cases": [{"id": "wrong-skill", "name": "Wrong Skill", "passed": True}],
                }),
                encoding="utf-8",
            )

            html_path = repo_root / "Infrastructure/artifacts/skill-reviews/example-skill.html"
            render_skill_review_dashboard(report_path=report_path, output_path=html_path, repo_root=repo_root)
            html_text = html_path.read_text(encoding="utf-8")

        self.assertIn("Evals Not Run Yet", html_text)
        self.assertNotIn("Wrong Skill", html_text)

    @patch("ask.commands.skills_impl.audit_skill")
    @patch("ask.commands.skills_impl.shutil.which")
    def test_external_review_can_skip_tessl_review(self, mock_which, mock_audit):
        """
        Verify that external_review_skill skips the tessl review when skip_tessl_review is True.
        
        Sets up a minimal skill directory, fakes plugin binaries and a successful audit, and asserts:
        - overall result status is "success"
        - the tessl_review entry in result.data is marked as "skipped"
        - only the expected subprocess calls (plugin-eval and tessl lint) are made (call count == 2)
        """
        skill_dir = "Skills/backend-platform/example-skill"
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            target = repo_root / skill_dir
            target.mkdir(parents=True)
            (target / "SKILL.md").write_text("---\nname: example-skill\n---\n\n# Example\n", encoding="utf-8")

            audit = type("AuditResult", (), {})()
            audit.status = "success"
            audit.data = {"diagnostics": {"exit_code": 0}}
            audit.errors = []
            mock_audit.return_value = audit
            mock_which.side_effect = lambda name: f"/usr/local/bin/{name}" if name in {"plugin-eval", "tessl"} else None

            with patch("ask.commands.skills_impl.subprocess.run") as mock_run:
                mock_run.side_effect = [
                    subprocess.CompletedProcess(
                        args=[],
                        returncode=0,
                        stdout="Score: 91/100\nGrade: A\nRisk: low\nChecks: 0 fail, 0 warn",
                        stderr="",
                    ),
                    subprocess.CompletedProcess(args=[], returncode=0, stdout="tessl lint ok", stderr=""),
                ]
                result = external_review_skill(
                    repo_root=repo_root,
                    skill_path=skill_dir,
                    skip_tessl_review=True,
                )

        self.assertEqual(result.status, "success")
        self.assertEqual(result.data["tessl_review"]["status"], "skipped")
        self.assertEqual(mock_run.call_count, 2)


if __name__ == "__main__":
    unittest.main()
