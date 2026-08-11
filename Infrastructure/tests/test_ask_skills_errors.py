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

from ask.commands import skills_impl, skills_impl_catalog, skills_impl_core  # noqa: E402
from ask.commands.skills_impl import (  # noqa: E402
    _safe_tessl_staging_path,
    _subprocess_env_with_uv_cache,
    _summarize_family_benchmark_failure,
    _write_tessl_plugin_wrapper,
    audit_skill,
    external_review_skill,
    install_skill,
    skills_budget,
)
from ask.skill_review_dashboard import render_skill_review_dashboard  # noqa: E402


def _completed(args, stdout, *, returncode=0, stderr=""):
    return subprocess.CompletedProcess(args=args, returncode=returncode, stdout=stdout, stderr=stderr)


def test_validation_timeout_retains_decoded_output() -> None:
    timeout = subprocess.TimeoutExpired(
        cmd=["fixture-check"], timeout=1, output=b"partial\xff", stderr=b"slow\xff"
    )

    with patch.object(skills_impl_core.subprocess, "run", side_effect=timeout):
        result = skills_impl_core._run_validation_command(
            repo_root, ["fixture-check"], "fixture", "Fixture validation failed.", timeout=1
        )

    payload = json.loads(result.to_json())
    assert payload["data"]["fixture"]["stdout"] == "partial\ufffd"
    assert payload["data"]["fixture"]["stderr"] == "slow\ufffd\nvalidation command timed out after 1 seconds"


def test_install_skill_accepts_legacy_positional_remediate_flag() -> None:
    expected = object()
    with patch.object(skills_impl, "_install_skill", return_value=expected) as install:
        result = install_skill(repo_root, "https://example.invalid/demo.git", True)

    assert result is expected
    install.assert_called_once_with(
        repo_root,
        "https://example.invalid/demo.git",
        remediate=True,
        dest="Skills/github",
        dry_run=False,
    )


def test_builder_module_cache_is_qualified_by_resolved_path() -> None:
    with tempfile.TemporaryDirectory() as first_dir, tempfile.TemporaryDirectory() as second_dir:
        first_root, second_root = Path(first_dir), Path(second_dir)
        (first_root / "builder.py").write_text("VALUE = 'first'\n", encoding="utf-8")
        (second_root / "builder.py").write_text("VALUE = 'second'\n", encoding="utf-8")
        with patch.object(
            skills_impl_catalog, "_resolve_skill_builder_script", return_value="builder.py"
        ):
            first = skills_impl_catalog._load_builder_module(first_root, "fixture")
            second = skills_impl_catalog._load_builder_module(second_root, "fixture")

    assert first is not None and first.VALUE == "first"
    assert second is not None and second.VALUE == "second"


def test_skills_budget_returns_structured_timeout() -> None:
    timeout = subprocess.TimeoutExpired(
        cmd=["budget"], timeout=600, output=b"partial", stderr=b"hung"
    )
    with (
        patch("ask.commands.skills_impl._get_python_command", return_value=["python3"]),
        patch("ask.commands.skills_impl.subprocess.run", side_effect=timeout),
    ):
        result = skills_budget(repo_root)

    assert result.status == "error"
    assert result.errors[0].code == "ERR_TIMEOUT"
    assert result.data["runtime_budget"]["stdout"] == "partial"


def _write_skill_fixture(repo_root, skill_dir):
    target = repo_root / skill_dir
    target.mkdir(parents=True)
    (target / "SKILL.md").write_text("---\nname: example-skill\n---\n\n# Example\n", encoding="utf-8")


def _successful_audit(data):
    audit = type("AuditResult", (), {})()
    audit.status = "success"
    audit.data = data
    audit.errors = []
    return audit


def _external_tool_path(name):
    return f"/usr/local/bin/{name}" if name in {"plugin-eval", "tessl", "snyk"} else None


class SkillReviewDashboardImportTests(unittest.TestCase):
    def test_facade_defers_renderer_import_until_rendering(self) -> None:
        """The public dashboard module must keep renderer loading lazy."""
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                (
                    "import sys; "
                    "sys.path.insert(0, sys.argv[1]); "
                    "from ask.skill_review_dashboard import render_skill_review_dashboard; "
                    "assert callable(render_skill_review_dashboard); "
                    "assert 'ask.skill_review_dashboard_render' not in sys.modules, "
                    "'dashboard facade imported the renderer eagerly'"
                ),
                str(repo_root / "Infrastructure" / "scripts" / "lib"),
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=120,
        )
        self.assertEqual(result.returncode, 0, result.stderr)


class CommandFacadeScriptModeTests(unittest.TestCase):
    def test_refactored_facades_remain_importable_as_scripts(self) -> None:
        """File-mode facades must retain package context for relative imports."""
        for command in ("skills.py", "repo.py"):
            result = subprocess.run(
                [sys.executable, str(repo_root / "Infrastructure" / "scripts" / "lib" / "ask" / "commands" / command)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, f"{command}: {result.stderr}")


def _run_snyk_review(mock_run, mock_which, mock_audit, *, snyk_result, returncode=0, stderr="", skill_dir="Skills/backend-platform/example-skill"):
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_root = Path(tmpdir)
        _write_skill_fixture(repo_root, skill_dir)
        mock_audit.return_value = _successful_audit({"diagnostics": {"exit_code": 0}})
        mock_which.side_effect = _external_tool_path
        mock_run.side_effect = [
            _completed([], "Score: 91/100\nGrade: A"),
            _completed([], "Overall: PASSED (0 errors, 0 warnings)"),
            _completed([], "Review Score: 90%"),
            _completed([], snyk_result, returncode=returncode, stderr=stderr),
        ]
        return external_review_skill(repo_root=repo_root, skill_path=skill_dir, include_snyk=True, with_tessl_review=True)


def _run_tessl_default_review(mock_run, mock_which, mock_audit):
    skill_dir = "Skills/backend-platform/example-skill"
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_root = Path(tmpdir)
        _write_skill_fixture(repo_root, skill_dir)
        mock_audit.return_value = _successful_audit({"diagnostics": {"exit_code": 0}})
        mock_which.side_effect = lambda name: f"/usr/local/bin/{name}" if name in {"plugin-eval", "tessl"} else None
        mock_run.side_effect = [_completed([], "Score: 91/100\nGrade: A\nRisk: low\nChecks: 0 fail, 0 warn"), _completed([], "tessl lint ok")]
        return external_review_skill(repo_root=repo_root, skill_path=skill_dir)


def _render_eval_scorecard(repo_root):
    report_path = repo_root / "Infrastructure/artifacts/skill-reviews/example-skill.json"
    report_path.parent.mkdir(parents=True)
    report_path.write_text(json.dumps({
        "status": "success",
        "data": {
            "target": "Plugins/skill-factory/skills/code_quality_review/example-skill",
            "ask_audit": {"data": {"openclaw": {"stdout": "Summary: 0 critical · 0 warn"}}},
            "plugin_eval": {"stdout": "Score: 88/100\nGrade: B"},
            "tessl_review": {"stdout": "Review Score: 90%\nDescription: 100%\nContent: 80%\nOverall: PASSED (0 errors, 0 warnings)\n  actionability: 3/3 - Clear steps."},
        },
        "errors": [],
    }), encoding="utf-8")
    scorecard_path = repo_root / "Infrastructure/artifacts/skills/example-skill/20260515-180000-000000/scorecard.json"
    scorecard_path.parent.mkdir(parents=True)
    scorecard_path.write_text(json.dumps({
        "skill_path": "Plugins/skill-factory/skills/code_quality_review/example-skill",
        "run_id": "20260515-180000-000000", "eval_mode": "smoke", "runner_mode": "codex",
        "cases": [{"id": "happy-path", "name": "Happy Path", "category": "happy", "passed": True, "tier1_failures": [], "warnings": []}, {"id": "edge-case", "name": "Edge Case", "category": "edge", "passed": False, "tier1_failures": ["missing required output"], "warnings": []}],
    }), encoding="utf-8")
    html_path = repo_root / "Infrastructure/artifacts/skill-reviews/example-skill.html"
    render_skill_review_dashboard(report_path=report_path, output_path=html_path, repo_root=repo_root)
    return html_path.read_text(encoding="utf-8")


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

            plugin_root, info = _write_tessl_plugin_wrapper(
                repo_root,
                "Plugins/harness-engineering/skills/he-phase-work",
                repo_root / "tmp-tessl",
            )

            staged_skill_dir = Path(info["review_path"])
            self.assertTrue((plugin_root / ".tessl-plugin" / "plugin.json").is_file())
            self.assertFalse((plugin_root / "tile.json").exists())
            self.assertEqual((staged_skill_dir / "SKILL.md").read_text(encoding="utf-8"), (skill_dir / "SKILL.md").read_text(encoding="utf-8"))
            self.assertFalse((plugin_root / "references").exists())
            self.assertEqual((staged_skill_dir / "references" / "local.md").read_text(encoding="utf-8"), "local")
            self.assertFalse((staged_skill_dir / ".." / ".." / "references").resolve().exists())

    @unittest.skipIf(not hasattr(Path, "symlink_to"), "symlink support unavailable")
    def test_tessl_wrapper_rejects_symlinked_support_dirs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            skill_dir = repo_root / "Skills/example-skill"
            target_refs = repo_root / "shared-references"
            skill_dir.mkdir(parents=True)
            target_refs.mkdir()
            (skill_dir / "SKILL.md").write_text("---\nname: example-skill\n---\n\n# Example\n", encoding="utf-8")
            (skill_dir / "references").symlink_to(target_refs, target_is_directory=True)

            with self.assertRaisesRegex(ValueError, "symlinked support path"):
                _write_tessl_plugin_wrapper(repo_root, "Skills/example-skill", repo_root / "tmp-tessl")

    @unittest.skipIf(not hasattr(Path, "symlink_to"), "symlink support unavailable")
    def test_tessl_wrapper_rejects_nested_support_symlinks(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            skill_dir = repo_root / "Skills/example-skill"
            references = skill_dir / "references"
            outside = repo_root / "outside.md"
            references.mkdir(parents=True)
            outside.write_text("outside", encoding="utf-8")
            (skill_dir / "SKILL.md").write_text("---\nname: example-skill\n---\n\n# Example\n", encoding="utf-8")
            (references / "leak.md").symlink_to(outside)

            with self.assertRaisesRegex(ValueError, "symlinked support path"):
                _write_tessl_plugin_wrapper(repo_root, "Skills/example-skill", repo_root / "tmp-tessl")

    def test_tessl_staged_json_path_rejects_escaping_parent_before_mkdir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            staging_root = Path(tmpdir) / "staging"
            escaped = Path(tmpdir) / "outside" / "plugin.json"

            with self.assertRaisesRegex(ValueError, "parent escaped"):
                _safe_tessl_staging_path(escaped, str(staging_root.resolve(strict=False)), "plugin manifest")

            self.assertFalse(escaped.parent.exists())

    @patch("ask.commands.skills_impl._get_python_command", return_value=["python3"])
    @patch("ask.commands.skills_impl.subprocess.run")
    def test_audit_skill_stops_after_diagnostics_fail(self, mock_run, _mock_python):
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=2, stdout="invalid target", stderr="missing SKILL.md"
        )

        result = audit_skill(repo_root=repo_root, skill_path="backend/cli-spec", level="strict")

        self.assertEqual(result.status, "error")
        self.assertEqual(result.errors[0].code, "ERR_VALIDATION")
        self.assertIn("Structural diagnostics failed", result.errors[0].message)
        self.assertEqual(mock_run.call_count, 1)

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
    @patch.dict("ask.commands.skills_impl.os.environ", {"TMPDIR": "/tmp/codex-test"}, clear=True)
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

    @patch("ask.commands.skills_impl._get_python_command", return_value=["python3"])
    @patch("ask.commands.skills_impl.subprocess.run")
    @patch(
        "ask.commands.skills_impl.resolve_skill_handle",
        return_value={
            "status": "ok",
            "handle": "autofix",
            "source_path": "Skills/agent-ops/autofix/SKILL.md",
        },
    )
    def test_audit_skill_strict_resolves_handle_before_strict_gates(
        self,
        _mock_resolve,
        mock_run,
        _mock_python,
    ):
        mock_run.side_effect = [
            subprocess.CompletedProcess(args=[], returncode=0, stdout="diagnostics ok", stderr=""),
            subprocess.CompletedProcess(args=[], returncode=0, stdout="security gate ok", stderr=""),
            subprocess.CompletedProcess(args=[], returncode=0, stdout="family ok", stderr=""),
            subprocess.CompletedProcess(args=[], returncode=0, stdout="openclaw ok", stderr=""),
        ]

        result = audit_skill(repo_root=repo_root, skill_path="autofix", level="strict")

        self.assertEqual(result.status, "success")
        self.assertEqual(result.data["target"], "Skills/agent-ops/autofix")
        for call in mock_run.call_args_list:
            self.assertIn("Skills/agent-ops/autofix", call.args[0])
            self.assertNotIn("autofix", call.args[0][2:])

    @patch("ask.commands.skills_impl.subprocess.run")
    def test_install_skill_returns_structured_timeout(self, mock_run):
        timeout = subprocess.TimeoutExpired(
            cmd=["installer"], timeout=600, output=b"partial", stderr=b"hung"
        )
        mock_run.side_effect = [
            subprocess.CompletedProcess(
                args=[], returncode=0, stdout="usage: installer --validation-level", stderr=""
            ),
            timeout,
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "github").mkdir()
            with patch("ask.commands.skills_impl._get_python_command", return_value=["python3"]):
                result = install_skill(root, "https://example.com/example.git", dest="github")

        self.assertEqual(result.status, "error")
        self.assertEqual(result.errors[0].code, "ERR_TIMEOUT")
        self.assertEqual(result.data["install_process"]["stdout"], "partial")

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

            result = external_review_skill(
                repo_root=repo_root,
                skill_path=skill_dir,
                include_snyk=True,
                with_tessl_review=True,
            )

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
        result = _run_snyk_review(mock_run, mock_which, mock_audit, snyk_result='{"ok": true, "vulnerabilities": [], "summary": "No known vulnerabilities"}')
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
        result = _run_snyk_review(mock_run, mock_which, mock_audit, snyk_result='{"ok": false, "error": "Could not detect supported target files"}', returncode=3)
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
        result = _run_snyk_review(mock_run, mock_which, mock_audit, snyk_result='{"ok": false, "vulnerabilities": [{"severity": "high"}]}', returncode=1)
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
        result = _run_snyk_review(mock_run, mock_which, mock_audit, snyk_result="", returncode=2, stderr="Use snyk auth to authenticate.")
        self.assertEqual(result.status, "error")
        self.assertEqual(result.data["snyk"]["status"], "blocked_auth")
        self.assertTrue(any(error.code == "ERR_AUTH" for error in result.errors))

    def test_review_dashboard_renders_latest_eval_scorecard(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            html_text = _render_eval_scorecard(Path(tmpdir))

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
    def test_external_review_skips_tessl_content_review_by_default(self, mock_which, mock_audit):
        with patch("ask.commands.skills_impl.subprocess.run") as mock_run:
            result = _run_tessl_default_review(mock_run, mock_which, mock_audit)
        self.assertEqual(result.status, "success")
        self.assertEqual(result.data["tessl_review"]["status"], "skipped")
        self.assertIn("Disabled by default", result.data["tessl_review"]["reason"])
        self.assertEqual(mock_run.call_count, 2)

    def test_external_review_rejects_conflicting_tessl_review_flags(self):
        result = external_review_skill(
            repo_root=repo_root,
            skill_path="Skills/backend-platform/example-skill",
            with_tessl_review=True,
            skip_tessl_review=True,
        )

        self.assertEqual(result.status, "error")
        self.assertEqual(result.data["external_review"]["status"], "blocked")
        self.assertEqual(result.errors[0].code, "ERR_VALIDATION")

    def test_external_review_rejects_with_tessl_review_when_skip_tessl_enabled(self):
        result = external_review_skill(
            repo_root=repo_root,
            skill_path="Skills/backend-platform/example-skill",
            with_tessl_review=True,
            skip_tessl=True,
        )

        self.assertEqual(result.status, "error")
        self.assertEqual(result.data["external_review"]["status"], "blocked")
        self.assertEqual(result.data["external_review"]["blocker_class"], "blocked_validation")
        self.assertIn("--skip-tessl", result.data["external_review"]["blocker"])
        self.assertEqual(result.errors[0].code, "ERR_VALIDATION")


if __name__ == "__main__":
    unittest.main()
