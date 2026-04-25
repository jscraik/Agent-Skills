import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "validation-and-linting"))

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
        """
        Verify that the report's scope_counts contains expected scope lanes and that each lane's count is an integer.
        
        Asserts that the keys "global", "project", "local-plugin", "system", and "primary-runtime" exist in report["scope_counts"] and that each associated value is of type int.
        """
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


if __name__ == "__main__":
    unittest.main()
