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
import skillset_model  # noqa: E402
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
        lines = manifest.read_text(encoding="utf-8").splitlines()
        self.assertTrue(lines, "Expected at least one manifest row")
        first_row = json.loads(lines[0])
        self.assertEqual(first_row["provenance"]["projection_mode"], "rooted")
        self.assertTrue(first_row["provenance"]["source_sha256"])

    def test_skillset_inference_uses_segment_before_nested_plugin_skills_root(self) -> None:
        source_dir = REPO_ROOT / "Plugins" / "example-org" / "harness-engineering" / "skills" / "he-work"

        skill_set, source = skillset_model.infer_skill_set(source_dir, {})

        self.assertEqual(skill_set, "harness-engineering")
        self.assertEqual(source, "inferred")

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

    def test_router_ignores_generic_stopwords_when_scoring(self) -> None:
        manifest = self.temp_dir / ".skillsets" / "agent-ops" / "manifest.jsonl"
        manifest.parent.mkdir(parents=True)
        manifest.write_text(
            "\n".join(
                [
                    json.dumps(
                        {
                            "id": "generic-stage",
                            "description": "Use when the request says and with before",
                            "level": "atom",
                            "source_path": "Skills/agent-ops/verification-before-completion/SKILL.md",
                            "triggers": ["and with before"],
                        }
                    ),
                    json.dumps(
                        {
                            "id": "specific-stage",
                            "description": "Use for branch review readiness",
                            "level": "atom",
                            "source_path": "Skills/agent-ops/gh-workflow/SKILL.md",
                            "triggers": ["branch review readiness"],
                        }
                    ),
                ]
            )
            + "\n",
            encoding="utf-8",
        )

        payload = route_skillset.route(
            "agent-ops",
            "implemented branch with review before merge",
            skillsets_dir=self.temp_dir / ".skillsets",
        )

        self.assertEqual(payload["status"], "selected")
        self.assertEqual(payload["selected"]["id"], "specific-stage")

    def test_harness_engineering_routes_review_state_before_work_or_tdd(self) -> None:
        report = generate_skillset_manifests.build_manifest_report(self.temp_dir / ".skillsets")
        generate_skillset_manifests.write_manifests(report, self.temp_dir / ".skillsets")

        payload = route_skillset.route(
            "harness-engineering",
            "implemented branch with green CI and linked Linear QA issues, review before more work",
            skillsets_dir=self.temp_dir / ".skillsets",
        )

        self.assertEqual(payload["status"], "selected")
        self.assertEqual(payload["selected"]["id"], "he-code-review")
        self.assertIn("review-before-more-work", payload["candidates"][0]["reason"])

    def test_harness_engineering_routes_regression_first_to_tdd(self) -> None:
        report = generate_skillset_manifests.build_manifest_report(self.temp_dir / ".skillsets")
        generate_skillset_manifests.write_manifests(report, self.temp_dir / ".skillsets")

        payload = route_skillset.route(
            "harness-engineering",
            "write failing regression test first for a broken harness engineering workflow",
            skillsets_dir=self.temp_dir / ".skillsets",
        )

        self.assertEqual(payload["status"], "selected")
        self.assertEqual(payload["selected"]["id"], "he-tdd")
        self.assertIn("test-first-work", payload["candidates"][0]["reason"])

    def test_harness_engineering_multistage_rules_route_to_router(self) -> None:
        report = generate_skillset_manifests.build_manifest_report(self.temp_dir / ".skillsets")
        generate_skillset_manifests.write_manifests(report, self.temp_dir / ".skillsets")

        payload = route_skillset.route(
            "harness-engineering",
            "QA says the workflow is confusing but expected behavior is unclear, clarify the issue",
            skillsets_dir=self.temp_dir / ".skillsets",
        )

        self.assertEqual(payload["status"], "selected")
        self.assertEqual(payload["selected"]["id"], "he-router")
        self.assertIn("qa-intake-by-clarity", payload["candidates"][0]["reason"])

    def test_harness_engineering_stage_correctness_questions_route_to_router(self) -> None:
        report = generate_skillset_manifests.build_manifest_report(self.temp_dir / ".skillsets")
        generate_skillset_manifests.write_manifests(report, self.temp_dir / ".skillsets")

        for task in (
            "validate whether he-plan is the right stage",
            "is he-plan correct for this request?",
            "is he-plan right for this request?",
        ):
            with self.subTest(task=task):
                payload = route_skillset.route(
                    "harness-engineering",
                    task,
                    skillsets_dir=self.temp_dir / ".skillsets",
                )

                self.assertEqual(payload["status"], "selected")
                self.assertEqual(payload["selected"]["id"], "he-router")
                self.assertIn("stage-correctness-question", payload["candidates"][0]["reason"])

    def test_harness_engineering_direct_stage_with_whether_stays_direct(self) -> None:
        report = generate_skillset_manifests.build_manifest_report(self.temp_dir / ".skillsets")
        generate_skillset_manifests.write_manifests(report, self.temp_dir / ".skillsets")

        payload = route_skillset.route(
            "harness-engineering",
            "use he-plan to determine whether the rollout needs sequencing changes",
            skillsets_dir=self.temp_dir / ".skillsets",
        )

        self.assertEqual(payload["status"], "selected")
        self.assertEqual(payload["selected"]["id"], "he-plan")
        self.assertIn("direct-stage-invocation", payload["candidates"][0]["reason"])

    def test_harness_engineering_multiple_named_stages_route_to_router(self) -> None:
        report = generate_skillset_manifests.build_manifest_report(self.temp_dir / ".skillsets")
        generate_skillset_manifests.write_manifests(report, self.temp_dir / ".skillsets")

        payload = route_skillset.route(
            "harness-engineering",
            "should we use he-work or he-code-review next?",
            skillsets_dir=self.temp_dir / ".skillsets",
        )

        self.assertEqual(payload["status"], "selected")
        self.assertEqual(payload["selected"]["id"], "he-router")
        self.assertIn("named-stage-ambiguity", payload["candidates"][0]["reason"])

    def test_context_budget_validates_written_manifest_provenance(self) -> None:
        skillsets_dir = self.temp_dir / ".skillsets"
        report = generate_skillset_manifests.build_manifest_report(skillsets_dir)
        generate_skillset_manifests.write_manifests(report, skillsets_dir)

        violations = check_context_budget.validate_written_manifest_provenance(
            skillsets_dir=skillsets_dir,
            repo_root_path=REPO_ROOT,
        )

        self.assertFalse(violations)

    def test_context_budget_accepts_nested_canonical_plugin_source_paths(self) -> None:
        repo_root = self.temp_dir / "repo"
        skill_path = repo_root / "Plugins" / "sample-org" / "sample-plugin" / "skills" / "sample-skill" / "SKILL.md"
        skill_path.parent.mkdir(parents=True)
        skill_path.write_text("# Sample skill\n", encoding="utf-8")
        manifest = self.temp_dir / ".skillsets" / "agent-ops" / "manifest.jsonl"
        manifest.parent.mkdir(parents=True)
        manifest.write_text(json.dumps({
            "skill_set": "agent-ops",
            "source_path": "Plugins/sample-org/sample-plugin/skills/sample-skill/SKILL.md",
            "provenance": {
                "generator": "test",
                "projection_mode": "rooted",
                "policy_identity": "test",
                "source_revision": "test",
                "source_sha256": check_context_budget.file_hash(skill_path),
            },
        }) + "\n", encoding="utf-8")

        violations = check_context_budget.validate_written_manifest_provenance(
            skillsets_dir=self.temp_dir / ".skillsets",
            repo_root_path=repo_root,
        )

        self.assertFalse(violations)

    def test_context_budget_rejects_lowercase_runtime_plugin_source_paths(self) -> None:
        repo_root = self.temp_dir / "repo"
        skill_path = repo_root / "plugins" / "sample-plugin" / "skills" / "sample-skill" / "SKILL.md"
        skill_path.parent.mkdir(parents=True)
        skill_path.write_text("# Sample skill\n", encoding="utf-8")
        manifest = self.temp_dir / ".skillsets" / "agent-ops" / "manifest.jsonl"
        manifest.parent.mkdir(parents=True)
        manifest.write_text(json.dumps({
            "skill_set": "agent-ops",
            "source_path": "plugins/sample-plugin/skills/sample-skill/SKILL.md",
        }) + "\n", encoding="utf-8")

        violations = check_context_budget.validate_written_manifest_provenance(
            skillsets_dir=self.temp_dir / ".skillsets",
            repo_root_path=repo_root,
        )

        self.assertIn("SKILLSET_SOURCE_PATH_NOT_CANONICAL", {violation["code"] for violation in violations})

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

    def test_context_budget_rejects_noncanonical_source_path(self) -> None:
        manifest = self.temp_dir / ".skillsets" / "agent-ops" / "manifest.jsonl"
        manifest.parent.mkdir(parents=True)
        manifest.write_text(json.dumps({
            "skill_set": "agent-ops",
            "source_path": "skills-system/openai-docs/SKILL.md",
        }) + "\n", encoding="utf-8")

        violations = check_context_budget.validate_written_manifest_provenance(
            skillsets_dir=self.temp_dir / ".skillsets",
            repo_root_path=REPO_ROOT,
        )

        self.assertIn("SKILLSET_SOURCE_PATH_NOT_CANONICAL", {violation["code"] for violation in violations})

    def test_context_budget_rejects_traversal_source_path(self) -> None:
        manifest = self.temp_dir / ".skillsets" / "agent-ops" / "manifest.jsonl"
        manifest.parent.mkdir(parents=True)
        manifest.write_text(json.dumps({
            "skill_set": "agent-ops",
            "source_path": "../Skills/agent-ops/autofix/SKILL.md",
        }) + "\n", encoding="utf-8")

        violations = check_context_budget.validate_written_manifest_provenance(
            skillsets_dir=self.temp_dir / ".skillsets",
            repo_root_path=REPO_ROOT,
        )

        self.assertIn("SKILLSET_SOURCE_PATH_NOT_CANONICAL", {violation["code"] for violation in violations})

    def test_context_budget_rejects_symlink_source_escaping_repo(self) -> None:
        repo_root = self.temp_dir / "repo"
        external = self.temp_dir / "external" / "SKILL.md"
        external.parent.mkdir(parents=True)
        external.write_text("# External skill\n", encoding="utf-8")
        skill_path = repo_root / "Skills" / "agent-ops" / "external" / "SKILL.md"
        skill_path.parent.mkdir(parents=True)
        skill_path.symlink_to(external)
        manifest = self.temp_dir / ".skillsets" / "agent-ops" / "manifest.jsonl"
        manifest.parent.mkdir(parents=True)
        manifest.write_text(json.dumps({
            "skill_set": "agent-ops",
            "source_path": "Skills/agent-ops/external/SKILL.md",
            "provenance": {
                "generator": "test",
                "projection_mode": "rooted",
                "policy_identity": "test",
                "source_revision": "test",
                "source_sha256": check_context_budget.file_hash(skill_path),
            },
        }) + "\n", encoding="utf-8")

        violations = check_context_budget.validate_written_manifest_provenance(
            skillsets_dir=self.temp_dir / ".skillsets",
            repo_root_path=repo_root,
        )

        self.assertIn("SKILLSET_SOURCE_PATH_ESCAPES_REPO", {violation["code"] for violation in violations})

    def test_router_returns_structured_error_for_malformed_manifest(self) -> None:
        manifest = self.temp_dir / ".skillsets" / "agent-ops" / "manifest.jsonl"
        manifest.parent.mkdir(parents=True)
        manifest.write_text("{bad json\n", encoding="utf-8")

        payload = route_skillset.route(
            "agent-ops",
            "verify implementation before completion",
            skillsets_dir=self.temp_dir / ".skillsets",
        )

        self.assertEqual(payload["status"], "manifest_invalid")
        self.assertEqual(payload["selected"], None)
        self.assertIn("Invalid manifest JSON", payload["error"])


if __name__ == "__main__":
    unittest.main()
