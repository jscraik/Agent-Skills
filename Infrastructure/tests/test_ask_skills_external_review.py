import importlib
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

_skills_impl = importlib.import_module("ask.commands.skills_impl")

ExternalReviewRequest = _skills_impl.ExternalReviewRequest
external_review_skill = _skills_impl.external_review_skill


def _completed(args, stdout, *, returncode=0, stderr=""):
    return subprocess.CompletedProcess(args=args, returncode=returncode, stdout=stdout, stderr=stderr)


def _skill_fixture(repo_root, skill_dir, *, description=None):
    target = repo_root / skill_dir
    target.mkdir(parents=True)
    detail = f"\ndescription: {description}" if description else ""
    (target / "SKILL.md").write_text(f"---\nname: example-skill{detail}\n---\n\n# Example\n", encoding="utf-8")


def _successful_audit(data):
    audit = type("AuditResult", (), {})()
    audit.status = "success"
    audit.data = data
    audit.errors = []
    return audit


def _tool_path(name):
    return f"/usr/local/bin/{name}" if name in {"plugin-eval", "tessl"} else None


def _run_explicit_review(mock_run, mock_which, mock_audit):
    skill_dir = "Skills/backend-platform/example-skill"
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_root = Path(tmpdir)
        _skill_fixture(repo_root, skill_dir)
        mock_audit.return_value = _successful_audit({"diagnostics": {"exit_code": 0}})
        mock_which.side_effect = _tool_path
        mock_run.side_effect = [
            _completed(["/usr/local/bin/plugin-eval", "analyze", skill_dir, "--format", "markdown"], "Score: 91/100\nGrade: A\nRisk: low\nChecks: 0 fail, 0 warn"),
            _completed(["/usr/local/bin/tessl", "plugin", "lint", skill_dir], "tessl lint ok"),
            _completed(["/usr/local/bin/tessl", "skill", "review", "--json", "--threshold", "85", skill_dir], '{"reviewScore": 96, "summary": "ok"}'),
        ]
        return external_review_skill(repo_root=repo_root, skill_path=skill_dir, with_tessl_review=True)


def _assert_explicit_review(case, result, mock_run):
    case.assertEqual(result.status, "success")
    case.assertTrue(result.data["policy"]["no_publish"])
    case.assertFalse(result.data["policy"]["uses_npx"])
    case.assertEqual(result.data["plugin_eval"]["status"], "success")
    case.assertEqual(result.data["plugin_eval_context"]["mode"], "agent_context_staging")
    case.assertIn("references/evals.yaml", result.data["plugin_eval_context"]["excluded_package_surfaces"])
    case.assertIn("/ask-plugin-eval-reviews/", mock_run.call_args_list[0].args[0][2])
    case.assertEqual(result.data["tessl_lint"]["status"], "success")
    case.assertEqual(result.data["tessl_review"]["status"], "success")
    case.assertEqual(result.data["tessl_review"]["target_score"], 90)
    case.assertEqual(result.data["tessl_review"]["summary"]["target_score"], 90)
    case.assertEqual(mock_run.call_count, 3)
    for call in mock_run.call_args_list:
        case.assertNotIn("npx", call.args[0])
        case.assertNotIn("publish", call.args[0])
    tessl_call, review_call = mock_run.call_args_list[1:]
    case.assertEqual(tessl_call.args[0][1:3], ["plugin", "lint"])
    case.assertEqual(review_call.args[0][1:3], ["skill", "review"])
    case.assertEqual(review_call.args[0][3:5], ["--json", "--threshold"])
    case.assertEqual(review_call.args[0][5], "85")
    for call in (tessl_call, review_call):
        case.assertNotIn("agent-skills-tessl-", call.kwargs["env"].get("HOME", ""))
    case.assertTrue(result.data["tessl_plugin"]["support_refs_included"])
    case.assertTrue(result.data["tessl_plugin"]["plugin_manifest"].endswith("/.tessl-plugin/plugin.json"))


def _run_dashboard_review(mock_run, mock_which, mock_audit):
    skill_dir = "Plugins/skill-factory/skills/code_quality_review/example-skill"
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_root = Path(tmpdir)
        _skill_fixture(repo_root, skill_dir, description="Use when reviewing examples.")
        mock_audit.return_value = _successful_audit({"openclaw": {"stdout": "Summary: 0 critical · 0 warn"}})
        mock_which.side_effect = _tool_path
        mock_run.side_effect = [
            _completed([], "Score: 91/100\nGrade: A\nRisk: low\nChecks: 0 fail, 0 warn"),
            _completed([], "Overall: PASSED (0 errors, 0 warnings)"),
            _completed([], "Review Score: 92%\nDescription: 100%\nContent: 85%\n  specificity: 3/3 - Specific trigger terms.\n  conciseness: 2/3 - Slightly verbose.\n    Suggestions:\n      - Tighten repeated guidance.\n"),
        ]
        result = external_review_skill(repo_root=repo_root, skill_path=skill_dir, audit_level="compat", report_path="Infrastructure/artifacts/skill-reviews/example-skill.json", dashboard=True, dashboard_path="Infrastructure/artifacts/skill-reviews/example-skill.html")
        html_text = (repo_root / result.data["dashboard_path"]).read_text(encoding="utf-8")
        report_payload = json.loads((repo_root / result.data["report_path"]).read_text(encoding="utf-8"))
    return result, html_text, report_payload


def _assert_dashboard_review(result, html_text, report_payload):
    assert result.status == "success"
    assert result.data["dashboard_path"] == "Infrastructure/artifacts/skill-reviews/example-skill.html"
    assert result.data["dashboard_url"] == result.data["dashboard_path"]
    assert report_payload["data"]["dashboard"] == {"status": "rendered", "tab": "quality"}
    assert report_payload["data"]["dashboard_path"] == result.data["dashboard_path"]
    for marker in ("ASK Local Review", 'data-auto-refresh-seconds="0"', "Static evidence snapshot", 'role="tablist"', 'role="tabpanel"', "Quality", "Evals Not Run Yet", "Snyk Advisory", "local_internal_only", "disabled_until_requested"):
        assert marker in html_text


def test_external_review_accepts_explicit_request_object():
    result = external_review_skill(
        repo_root,
        ExternalReviewRequest(
            skill_path="Skills/backend-platform/example-skill",
            with_tessl_review=True,
            skip_tessl=True,
        ),
    )

    assert result.status == "error"
    assert result.data["external_review"]["blocker_class"] == "blocked_validation"
    assert result.errors[0].code == "ERR_VALIDATION"


@patch("ask.commands.skills_impl.audit_skill")
def test_external_review_keeps_review_result_when_dashboard_report_staging_is_unavailable(mock_audit):
    skill_dir = "Skills/backend-platform/example-skill"
    with tempfile.TemporaryDirectory() as tmpdir:
        local_root = Path(tmpdir)
        _skill_fixture(local_root, skill_dir)
        mock_audit.return_value = _successful_audit({"diagnostics": {"exit_code": 0}})
        with patch.object(Path, "mkdir", side_effect=OSError("read-only dashboard root")):
            result = external_review_skill(repo_root=local_root, skill_path=skill_dir, skip_plugin_eval=True, skip_tessl=True, dashboard=True)

    assert result.status == "success"
    assert result.errors == []
    assert result.data["dashboard"] == {"status": "unavailable", "reason": "render_failed", "error_type": "OSError", "tab": "quality"}
    assert "report_path" not in result.data


class TestAskSkillsExternalReview(unittest.TestCase):
    @patch("ask.commands.skills_impl.audit_skill")
    @patch("ask.commands.skills_impl.shutil.which")
    @patch("ask.commands.skills_impl.subprocess.run")
    def test_external_review_runs_tessl_review_only_when_explicitly_requested(
        self,
        mock_run,
        mock_which,
        mock_audit,
    ):
        _assert_explicit_review(self, _run_explicit_review(mock_run, mock_which, mock_audit), mock_run)

    @patch("ask.commands.skills_impl.audit_skill")
    @patch("ask.commands.skills_impl.shutil.which")
    @patch("ask.commands.skills_impl.subprocess.run")
    def test_external_review_dashboard_writes_local_html(
        self,
        mock_run,
        mock_which,
        mock_audit,
    ):
        _assert_dashboard_review(*_run_dashboard_review(mock_run, mock_which, mock_audit))


if __name__ == "__main__":
    unittest.main()
