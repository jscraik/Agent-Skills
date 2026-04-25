import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "validation-and-linting"))
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.commands import runtime  # noqa: E402
from ask.envelope import CallResult, ErrorCode, ErrorObject  # noqa: E402
from verify_runtime_budget import build_report  # noqa: E402


class TestRuntimeSurfaceReport(unittest.TestCase):
    def test_report_contains_phase_a_surface_fields(self) -> None:
        report = build_report()

        required_fields = {
            "projection_mode",
            "first_level_default_entries",
            "hidden_system_entries",
            "primary_runtime_entries",
            "plugin_runtime_entries",
            "system_bridge_skills",
            "duplicate_default_names",
            "largest_descriptions",
            "root_skill_set_count",
            "unmapped_skill_names",
            "estimated_description_words",
            "estimated_description_tokens",
            "budget_status",
            "scope_counts",
            "shadowed_entries",
            "suppressed_entries",
        }
        self.assertTrue(required_fields.issubset(report.keys()))
        self.assertIn(report["projection_mode"], {"flat", "rooted"})
        self.assertEqual(report["budget_status"], report["status"])

    def test_scope_counts_include_known_scope_lanes(self) -> None:
        report = build_report()

        for scope in ("global", "project", "local-plugin", "system", "primary-runtime"):
            self.assertIn(scope, report["scope_counts"])
            self.assertIsInstance(report["scope_counts"][scope], int)

    def test_description_estimates_are_non_negative(self) -> None:
        report = build_report()

        self.assertGreaterEqual(report["estimated_description_words"], 0)
        self.assertGreaterEqual(report["estimated_description_tokens"], 0)
        for payload in report["largest_descriptions"]:
            self.assertIn("name", payload)
            self.assertIn("path", payload)
            self.assertIn("description_words", payload)

    def test_runtime_surface_reports_budget_status_without_gating(self) -> None:
        budget_result = CallResult(status="error")
        budget_result.data["runtime_budget"] = {
            "status": "fail",
            "projection_mode": "flat",
        }
        budget_result.errors.append(
            ErrorObject(
                code=ErrorCode.ERR_VALIDATION,
                message="default skill budget exceeded",
            )
        )

        with mock.patch.object(runtime, "skills_budget", return_value=budget_result):
            result = runtime.dispatch_runtime(
                REPO_ROOT,
                SimpleNamespace(action="surface", default_max=30),
            )

        self.assertEqual(result.status, "success")
        self.assertEqual(result.errors, [])
        self.assertEqual(result.data["runtime_surface_status"], "error")
        self.assertEqual(result.data["runtime_surface"]["status"], "fail")


if __name__ == "__main__":
    unittest.main()
