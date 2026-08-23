# pylint: disable=import-error,wrong-import-position
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[2]
VALIDATION_DIR = REPO_ROOT / "Infrastructure" / "scripts" / "validation-and-linting"
sys.path.insert(0, str(VALIDATION_DIR))

import check_context_budget  # noqa: E402
from selection_policy import ROOT_SKILL_SET_NAMES  # noqa: E402


class TestContextBudgetReport(unittest.TestCase):
    def test_context_budget_allows_declared_direct_rooted_runtime_handle(self) -> None:
        direct_manifest = {
            "manifests": [{
                "path": ".skillsets/agent-ops/manifest.jsonl",
                "rows": [{
                    "id": "improve-agent-native",
                    "runtime_visibility": "flat",
                    "source_path": "Skills/agent-ops/improve-agent-native/SKILL.md",
                }],
            }],
            "manifest_count": 1,
            "module_count": 1,
            "unmapped": [],
            "violations": [],
        }
        runtime_entries = list(ROOT_SKILL_SET_NAMES) + ["improve-agent-native"]
        with (
            mock.patch.object(check_context_budget, "build_manifest_report", return_value=direct_manifest),
            mock.patch.object(check_context_budget, "first_level_runtime_entries", return_value=runtime_entries),
            mock.patch.object(check_context_budget, "validate_written_manifest_provenance", return_value=[]),
        ):
            report = check_context_budget.validate_context_budget(projection_mode="rooted")

        codes = {violation["code"] for violation in report["violations"]}
        self.assertNotIn("LATENT_SKILLS_EXPOSED_FIRST_LEVEL", codes)

    def test_context_budget_reports_missing_manifest_files_in_rooted_mode(self) -> None:
        with (
            mock.patch.object(
                check_context_budget,
                "build_manifest_report",
                return_value={
                    "manifests": [{"path": ".skillsets/nonexistent/manifest.jsonl"}],
                    "manifest_count": 1,
                    "module_count": 1,
                    "unmapped": [],
                    "violations": [],
                },
            ),
            mock.patch.object(
                check_context_budget,
                "validate_written_manifest_provenance",
                return_value=[],
            ),
        ):
            report = check_context_budget.validate_context_budget(projection_mode="rooted")

        codes = {violation["code"] for violation in report["violations"]}
        self.assertIn("MANIFEST_FILES_MISSING", codes)
        missing = next(
            (v for v in report["violations"] if v["code"] == "MANIFEST_FILES_MISSING"),
            None,
        )
        self.assertIsNotNone(missing)
        self.assertIn(".skillsets/nonexistent/manifest.jsonl", missing["paths"])

    def test_context_budget_uses_injected_root_for_manifest_checks(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            manifest_path = repo_root / ".skillsets/agent-ops/manifest.jsonl"
            manifest_path.parent.mkdir(parents=True)
            manifest_path.write_text("", encoding="utf-8")
            report_payload = {
                "manifests": [{"path": ".skillsets/agent-ops/manifest.jsonl"}],
                "manifest_count": 1,
                "module_count": 0,
                "unmapped": [],
                "violations": [],
            }
            with (
                mock.patch.object(
                    check_context_budget,
                    "build_manifest_report",
                    return_value=report_payload,
                ),
                mock.patch.object(
                    check_context_budget,
                    "validate_written_manifest_provenance",
                    return_value=[],
                ) as provenance,
            ):
                report = check_context_budget.validate_context_budget(
                    projection_mode="rooted", repo_root_path=repo_root
                )

        self.assertNotIn(
            "MANIFEST_FILES_MISSING",
            {violation["code"] for violation in report["violations"]},
        )
        provenance.assert_called_once_with(repo_root_path=repo_root)


if __name__ == "__main__":
    unittest.main()
