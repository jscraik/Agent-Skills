import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
LIFECYCLE_DIR = REPO_ROOT / "Infrastructure" / "scripts" / "lifecycle-and-sync"
VALIDATION_DIR = REPO_ROOT / "Infrastructure" / "scripts" / "validation-and-linting"
sys.path.insert(0, str(LIFECYCLE_DIR))
sys.path.insert(0, str(VALIDATION_DIR))

import check_context_budget  # noqa: E402
import generate_root_skill_sets  # noqa: E402
import generate_skillset_manifests  # noqa: E402
import route_skillset  # noqa: E402
from selection_policy import ROOT_SKILL_SET_NAMES  # noqa: E402


BUDGET_CONFIG = check_context_budget.load_config()
RUNTIME_BUDGET = BUDGET_CONFIG["runtime_projection"]
ROUTING_BUDGET = BUDGET_CONFIG["routing"]

class TestContextBudgetedSkillsets(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="context-budgeted-skillsets-"))

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_root_skill_generation_stays_inside_budget(self) -> None:
        report = generate_root_skill_sets.build_roots(self.temp_dir / "skills")

        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["root_count"], len(ROOT_SKILL_SET_NAMES))
        self.assertLessEqual(report["root_count"], RUNTIME_BUDGET["max_root_skill_sets"])
        self.assertFalse(report["violations"])
        self.assertLessEqual(
            sum(root["description_words"] for root in report["roots"]),
            RUNTIME_BUDGET["max_root_description_words_total"],
        )
        self.assertTrue(
            all(root["body_words"] <= RUNTIME_BUDGET["max_root_body_words_each"] for root in report["roots"])
        )

    def test_manifest_generation_writes_provenance_rich_rows(self) -> None:
        report = generate_skillset_manifests.build_manifest_report(self.temp_dir / ".skillsets")
        writes = generate_skillset_manifests.write_manifests(report, self.temp_dir / ".skillsets")

        self.assertEqual(report["status"], "pass")
        self.assertEqual(len(writes), len(ROOT_SKILL_SET_NAMES))
        manifest = self.temp_dir / ".skillsets" / "agent-ops" / "manifest.jsonl"
        self.assertTrue(manifest.is_file())
        first_row = json.loads(manifest.read_text(encoding="utf-8").splitlines()[0])
        self.assertEqual(first_row["provenance"]["projection_mode"], "rooted")
        self.assertTrue(first_row["provenance"]["source_sha256"])

    def test_router_returns_bounded_candidates_without_manifest_dump(self) -> None:
        report = generate_skillset_manifests.build_manifest_report(self.temp_dir / ".skillsets")
        generate_skillset_manifests.write_manifests(report, self.temp_dir / ".skillsets")

        payload = route_skillset.route(
            "agent-ops",
            "verify implementation before completion",
            top_k=99,
            skillsets_dir=self.temp_dir / ".skillsets",
        )

        self.assertEqual(payload["status"], "selected")
        self.assertEqual(payload["top_k"], ROUTING_BUDGET["max_candidates_returned"])
        self.assertEqual(payload["selected"]["id"], "verification-before-completion")
        self.assertLessEqual(len(payload["candidates"]), ROUTING_BUDGET["max_candidates_returned"])
        self.assertNotIn("source_path", payload["candidates"][0])

    def test_context_budget_validates_written_manifest_provenance(self) -> None:
        skillsets_dir = self.temp_dir / ".skillsets"
        report = generate_skillset_manifests.build_manifest_report(skillsets_dir)
        generate_skillset_manifests.write_manifests(report, skillsets_dir)

        violations = check_context_budget.validate_written_manifest_provenance(
            skillsets_dir=skillsets_dir,
            repo_root_path=REPO_ROOT,
        )

        self.assertFalse(violations)

    def test_context_budget_rejects_noncanonical_skillset_file(self) -> None:
        rogue = self.temp_dir / ".skillsets" / "agent-ops" / "notes.md"
        rogue.parent.mkdir(parents=True)
        rogue.write_text("manual note\n", encoding="utf-8")

        violations = check_context_budget.validate_written_manifest_provenance(
            skillsets_dir=self.temp_dir / ".skillsets",
            repo_root_path=REPO_ROOT,
        )

        self.assertIn("UNOWNED_SKILLSET_FILE", {violation["code"] for violation in violations})

    def test_context_budget_reports_non_object_manifest_rows(self) -> None:
        manifest = self.temp_dir / ".skillsets" / "agent-ops" / "manifest.jsonl"
        manifest.parent.mkdir(parents=True)
        manifest.write_text("[]\n", encoding="utf-8")

        violations = check_context_budget.validate_written_manifest_provenance(
            skillsets_dir=self.temp_dir / ".skillsets",
            repo_root_path=REPO_ROOT,
        )

        self.assertIn("INVALID_SKILLSET_MANIFEST_ROW_TYPE", {violation["code"] for violation in violations})


if __name__ == "__main__":
    unittest.main()
