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
        """
        Create a temporary directory for the test and store its path on self.temp_dir.
        
        The directory is created with the prefix "context-budgeted-skillsets-" and is intended for use by the test case.
        """
        self.temp_dir = Path(tempfile.mkdtemp(prefix="context-budgeted-skillsets-"))

    def tearDown(self) -> None:
        """
        Remove the temporary directory created for the test.
        
        Deletes self.temp_dir and all its contents recursively; any filesystem errors raised during removal are ignored.
        """
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
        """
        Verify that manifest generation produces provenance-rich JSONL rows and writes them to disk.
        
        Asserts that the manifest build report signals success, the number of written manifests matches the expected root skillset count, a manifest.jsonl file exists for the "agent-ops" skillset, the file contains at least one JSON line, and the first manifest row includes a `provenance.projection_mode` equal to "rooted" and a non-empty `provenance.source_sha256`.
        """
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

    def test_router_returns_bounded_candidates_without_manifest_dump(self) -> None:
        """
        Verify routing selects a skill, bounds candidates to the configured routing budget, and does not expose manifest dump data.
        
        Asserts that:
        - the router reports a "selected" status and normalizes the returned top_k to ROUTING_BUDGET["max_candidates_returned"];
        - the selected skill id is "verification-before-completion";
        - the number of returned candidates is <= ROUTING_BUDGET["max_candidates_returned"];
        - candidate entries do not include manifest-only fields such as "source_path".
        """
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
                            "source_path": "Skills/agent-ops/generic-stage/SKILL.md",
                            "triggers": ["and with before"],
                        }
                    ),
                    json.dumps(
                        {
                            "id": "specific-stage",
                            "description": "Use for branch review readiness",
                            "level": "atom",
                            "source_path": "Skills/agent-ops/specific-stage/SKILL.md",
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
        """
        Verify harness-engineering routes regression-first intent to the TDD lane.
        
        Builds and writes skillset manifests, routes a request asking to "write failing regression test first" to the "harness-engineering" skillset, and asserts the router selects the "he-tdd" lane and that the top candidate's reason contains "test-first-work".
        """
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
        """
        Ensure multistage harness-engineering requests about unclear expected behavior route to the router stage.
        
        Builds and writes manifests, routes a clarifying QA request for the `harness-engineering` skillset, and asserts the router (`he-router`) is selected and the top candidate's reason includes `qa-intake-by-clarity`.
        """
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
        """
        Verify that stage-correctness inquiries for the harness-engineering skillset are routed to the router stage.
        
        For each task variant asking whether "he-plan" is the correct stage, generates manifests, routes the request to the "harness-engineering" skillset, and asserts:
        - the payload status is "selected";
        - the selected stage id is "he-router";
        - the top candidate's reason contains "stage-correctness-question".
        """
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

    def test_harness_engineering_multiple_named_stages_route_to_router(self) -> None:
        """
        Verify that a harness-engineering request mentioning multiple named stages is routed to the router lane and that the chosen candidate's reason contains "named-stage-ambiguity".
        """
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

    def test_plugin_factory_routes_create_to_plugin_creator(self) -> None:
        report = generate_skillset_manifests.build_manifest_report(self.temp_dir / ".skillsets")
        generate_skillset_manifests.write_manifests(report, self.temp_dir / ".skillsets")

        payload = route_skillset.route(
            "plugin-factory",
            "create a new plugin from this workflow",
            skillsets_dir=self.temp_dir / ".skillsets",
        )

        self.assertEqual(payload["status"], "selected")
        self.assertEqual(payload["selected"]["id"], "plugin-creator")
        self.assertIn("plugin-create", payload["candidates"][0]["reason"])

    def test_plugin_factory_routes_harden_and_install_to_owned_lanes(self) -> None:
        """
        Verify that plugin-factory routes "harden" and "install" intents to their owned lanes and annotates the chosen candidate with the expected routing rule.
        
        For each test phrase, asserts that the router selects a candidate (status "selected"), that the selected skillset id matches the expected lane ("plugin-builder" or "plugin-installer"), and that the top candidate's reason string contains the expected rule identifier (e.g., "plugin-harden-convert", "plugin-install").
        """
        report = generate_skillset_manifests.build_manifest_report(self.temp_dir / ".skillsets")
        generate_skillset_manifests.write_manifests(report, self.temp_dir / ".skillsets")

        cases = (
            ("harden this imported plugin before release", "plugin-builder", "plugin-harden-convert"),
            ("install this plugin from GitHub and repair plugin visibility", "plugin-installer", "plugin-install"),
        )
        for task, expected_id, expected_rule in cases:
            with self.subTest(task=task):
                payload = route_skillset.route(
                    "plugin-factory",
                    task,
                    skillsets_dir=self.temp_dir / ".skillsets",
                )

                self.assertEqual(payload["status"], "selected")
                self.assertEqual(payload["selected"]["id"], expected_id)
                self.assertIn(expected_rule, payload["candidates"][0]["reason"])

    def test_plugin_factory_routes_multi_lane_questions_to_router(self) -> None:
        report = generate_skillset_manifests.build_manifest_report(self.temp_dir / ".skillsets")
        generate_skillset_manifests.write_manifests(report, self.temp_dir / ".skillsets")

        payload = route_skillset.route(
            "plugin-factory",
            "should we use plugin-creator or plugin-builder next?",
            skillsets_dir=self.temp_dir / ".skillsets",
        )

        self.assertEqual(payload["status"], "selected")
        self.assertEqual(payload["selected"]["id"], "plugin-factory-router")
        self.assertIn("named-lane-ambiguity", payload["candidates"][0]["reason"])

    def test_plugin_factory_routes_mixed_intent_to_router(self) -> None:
        report = generate_skillset_manifests.build_manifest_report(self.temp_dir / ".skillsets")
        generate_skillset_manifests.write_manifests(report, self.temp_dir / ".skillsets")

        payload = route_skillset.route(
            "plugin-factory",
            "create and install plugin for this repo",
            skillsets_dir=self.temp_dir / ".skillsets",
        )

        self.assertEqual(payload["status"], "selected")
        self.assertEqual(payload["selected"]["id"], "plugin-factory-router")
        self.assertIn("mixed-intent-ambiguity", payload["candidates"][0]["reason"])

    def test_plugin_factory_blocks_internal_router_as_root_lane(self) -> None:
        report = generate_skillset_manifests.build_manifest_report(self.temp_dir / ".skillsets")
        generate_skillset_manifests.write_manifests(report, self.temp_dir / ".skillsets")

        payload = route_skillset.route(
            "plugin-factory",
            "route this with plugin-router",
            skillsets_dir=self.temp_dir / ".skillsets",
        )

        self.assertEqual(payload["status"], "selected")
        self.assertEqual(payload["selected"]["id"], "plugin-factory-router")
        self.assertIn("internal-router-root-invocation", payload["candidates"][0]["reason"])

    def test_skill_factory_routes_core_lanes_deterministically(self) -> None:
        """
        Verify that skill-factory routing maps specific user requests deterministically to expected core lanes.
        
        Generates and writes manifests, then for a set of example task phrasings asserts each route selection:
        - returns status "selected",
        - chooses the expected lane id for the skill-factory,
        - and includes the expected rule identifier substring in the top candidate's reason.
        """
        report = generate_skillset_manifests.build_manifest_report(self.temp_dir / ".skillsets")
        generate_skillset_manifests.write_manifests(report, self.temp_dir / ".skillsets")

        cases = (
            ("create a new skill from this workflow note", "skill-creator", "skill-create"),
            ("skillify this completed workflow into a reusable skill package", "skillify", "direct-lane-invocation"),
            ("harden this existing skill and fix skill warnings", "skill-builder", "skill-harden"),
            ("install this skill from github", "skill-installer", "skill-install"),
            ("compare skills for reliability failures and coverage gaps", "skill-refactor", "skill-refactor-analysis"),
        )
        for task, expected_id, expected_rule in cases:
            with self.subTest(task=task):
                payload = route_skillset.route(
                    "skill-factory",
                    task,
                    skillsets_dir=self.temp_dir / ".skillsets",
                )

                self.assertEqual(payload["status"], "selected")
                self.assertEqual(payload["selected"]["id"], expected_id)
                self.assertIn(expected_rule, payload["candidates"][0]["reason"])

    def test_skill_factory_routes_multi_lane_questions_to_router(self) -> None:
        """
        Verifies that an ambiguous skill-factory request referencing multiple lanes is routed to the skill-factory router.
        
        Ensures the router selects the "skill-factory-router" as the chosen lane and that the top candidate's reason includes "named-lane-ambiguity".
        """
        report = generate_skillset_manifests.build_manifest_report(self.temp_dir / ".skillsets")
        generate_skillset_manifests.write_manifests(report, self.temp_dir / ".skillsets")

        payload = route_skillset.route(
            "skill-factory",
            "should we use skill-creator or skill-builder for this?",
            skillsets_dir=self.temp_dir / ".skillsets",
        )

        self.assertEqual(payload["status"], "selected")
        self.assertEqual(payload["selected"]["id"], "skill-factory-router")
        self.assertIn("named-lane-ambiguity", payload["candidates"][0]["reason"])

    def test_skill_factory_routes_mixed_intent_to_router(self) -> None:
        """
        Verifies that a request mixing "create" and "install" intents is routed to the skill-factory router.
        
        Generates and writes skillset manifests, routes the query "create and install a skill package" against the "skill-factory" skillset, and asserts that the router selects the router lane ("skill-factory-router") and that the top candidate's reason includes "mixed-intent-ambiguity".
        """
        report = generate_skillset_manifests.build_manifest_report(self.temp_dir / ".skillsets")
        generate_skillset_manifests.write_manifests(report, self.temp_dir / ".skillsets")

        payload = route_skillset.route(
            "skill-factory",
            "create and install a skill package",
            skillsets_dir=self.temp_dir / ".skillsets",
        )

        self.assertEqual(payload["status"], "selected")
        self.assertEqual(payload["selected"]["id"], "skill-factory-router")
        self.assertIn("mixed-intent-ambiguity", payload["candidates"][0]["reason"])

    def test_context_budget_validates_written_manifest_provenance(self) -> None:
        skillsets_dir = self.temp_dir / ".skillsets"
        report = generate_skillset_manifests.build_manifest_report(skillsets_dir)
        generate_skillset_manifests.write_manifests(report, skillsets_dir)

        violations = check_context_budget.validate_written_manifest_provenance(
            skillsets_dir=skillsets_dir,
            repo_root_path=REPO_ROOT,
        )

        self.assertFalse(violations)

    def test_context_budget_accepts_lowercase_plugin_source_paths(self) -> None:
        repo_root = self.temp_dir / "repo"
        skill_path = repo_root / "plugins" / "sample-plugin" / "skills" / "sample-skill" / "SKILL.md"
        skill_path.parent.mkdir(parents=True)
        skill_path.write_text("# Sample skill\n", encoding="utf-8")
        manifest = self.temp_dir / ".skillsets" / "agent-ops" / "manifest.jsonl"
        manifest.parent.mkdir(parents=True)
        manifest.write_text(json.dumps({
            "skill_set": "agent-ops",
            "source_path": "plugins/sample-plugin/skills/sample-skill/SKILL.md",
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

    def test_context_budget_rejects_noncanonical_skillset_file(self) -> None:
        """
        Verifies that stray files inside a skillset directory are reported as unowned by the provenance validator.
        
        Creates a non-manifest file under `.skillsets/<skillset>/` and asserts that
        check_context_budget.validate_written_manifest_provenance returns at least one
        violation whose `code` is `"UNOWNED_SKILLSET_FILE"`.
        """
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


if __name__ == "__main__":
    unittest.main()
