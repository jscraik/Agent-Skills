# pylint: disable=import-error,import-outside-toplevel,wrong-import-position
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


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


class ContextBudgetTempDirTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="context-budgeted-skillsets-"))

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)


class TestRootSkillsetProjection(ContextBudgetTempDirTestCase):
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

    def test_root_skill_generation_preserves_security_contract_sections(self) -> None:
        report = generate_root_skill_sets.build_roots(self.temp_dir / "skills")

        for root in report["roots"]:
            with self.subTest(root=root["name"]):
                content = root["content"]
                self.assertIn("## Philosophy", content)
                self.assertIn("## Validation", content)
                self.assertIn("## Execution Boundaries", content)
                self.assertIn("## Failure Mode", content)
                self.assertIn("## Gotchas", content)

    def test_root_skill_evals_use_typed_acceptance_checks(self) -> None:
        report = generate_root_skill_sets.build_roots(self.temp_dir / "skills")

        for root in report["roots"]:
            evals = json.loads(root["evals"])
            for case in evals["cases"]:
                with self.subTest(root=root["name"], case=case["id"]):
                    self.assertTrue(case["acceptance"])
                    self.assertTrue(all(isinstance(check, dict) for check in case["acceptance"]))
                    self.assertTrue(all(check.get("type") for check in case["acceptance"]))
                    self.assertTrue(all(check.get("value") for check in case["acceptance"]))

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

    def test_system_manifest_provenance_hashes_canonical_system_store(self) -> None:
        report = generate_skillset_manifests.build_manifest_report(self.temp_dir / ".skillsets")
        agent_ops = next(manifest for manifest in report["manifests"] if manifest["skill_set"] == "agent-ops")
        row = next(row for row in agent_ops["rows"] if row["id"] == "openai-docs")
        source_file = REPO_ROOT / row["source_path"]

        self.assertEqual(row["source_path"], "skills-system/openai-docs/SKILL.md")
        self.assertEqual(row["provenance"]["source_sha256"], skillset_model.file_hash(source_file))

    def test_file_hash_uses_symlink_blob_for_provenance(self) -> None:
        target = self.temp_dir / "target.md"
        target.write_text("# Target\n", encoding="utf-8")
        link = self.temp_dir / "SKILL.md"
        link.symlink_to("target.md")

        expected = hashlib.sha256(b"target.md").hexdigest()

        self.assertEqual(skillset_model.file_hash(link), expected)
        self.assertEqual(check_context_budget.file_hash(link), expected)

    def test_write_roots_replaces_stale_reference_symlinks_before_writing(self) -> None:
        repo_root = self.temp_dir / "repo"
        output_dir = repo_root / ".agents" / "skills"
        target_dir = output_dir / "agent-ops"
        refs_dir = target_dir / "references"
        refs_dir.mkdir(parents=True)
        outside = self.temp_dir / "outside-contract.yaml"
        outside.write_text("keep me\n", encoding="utf-8")
        (refs_dir / "contract.yaml").symlink_to(outside)
        report = {
            "roots": [
                {
                    "name": "agent-ops",
                    "content": "# Agent Ops\n",
                    "contract": "{}\n",
                    "evals": "{}\n",
                    "task_profile": "{}\n",
                    "prompt_injection_context": "{}\n",
                }
            ]
        }

        generate_root_skill_sets.write_roots(report, output_dir, repo_root_path=repo_root)

        self.assertEqual(outside.read_text(encoding="utf-8"), "keep me\n")
        self.assertFalse((refs_dir / "contract.yaml").is_symlink())
        self.assertEqual((refs_dir / "contract.yaml").read_text(encoding="utf-8"), "{}\n")

    def test_insight_report_documented_runner_path_stays_runnable(self) -> None:
        runner = REPO_ROOT / "Skills" / "agent-ops" / "insight-report" / "scripts" / "run_insight_report.py"

        result = subprocess.run(
            [sys.executable, str(runner), "--help"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Generate Codex insights report", result.stdout)

    def test_skillset_inference_uses_segment_before_nested_plugin_skills_root(self) -> None:
        source_dir = REPO_ROOT / "Plugins" / "example-org" / "harness-engineering" / "skills" / "he-work"

        skill_set, source = skillset_model.infer_skill_set(source_dir, {})

        self.assertEqual(skill_set, "harness-engineering")
        self.assertEqual(source, "inferred")


class TestSkillsetRouting(ContextBudgetTempDirTestCase):
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

    def test_router_rejects_manifest_source_path_symlink_escape(self) -> None:
        repo_root = self.temp_dir / "repo"
        outside = self.temp_dir / "outside.md"
        outside.write_text("# Outside\n", encoding="utf-8")
        source_dir = repo_root / "Skills" / "agent-ops" / "evil"
        source_dir.mkdir(parents=True)
        (source_dir / "SKILL.md").symlink_to(outside)
        manifest = repo_root / ".skillsets" / "agent-ops" / "manifest.jsonl"
        manifest.parent.mkdir(parents=True)
        manifest.write_text(
            json.dumps(
                {
                    "id": "evil",
                    "description": "Use for evil routing.",
                    "level": "atom",
                    "source_path": "Skills/agent-ops/evil/SKILL.md",
                    "triggers": ["evil routing"],
                }
            )
            + "\n",
            encoding="utf-8",
        )

        with self.assertRaises(ValueError) as ctx:
            route_skillset.read_manifest("agent-ops", skillsets_dir=repo_root / ".skillsets")

        self.assertIn("source_path", str(ctx.exception))

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
                            "source_path": "Skills/agent-ops/docs-expert/SKILL.md",
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
        self.assertEqual(payload["selected"]["id"], "he-work")
        self.assertIn("test-first-work", payload["candidates"][0]["reason"])
        self.assertIn("folded stage alias 'he-tdd'", payload["candidates"][0]["reason"])

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


class TestContextBudgetManifestValidation(ContextBudgetTempDirTestCase):
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
        from selection_policy import policy_identity  # noqa: PLC0415
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
                "policy_identity": policy_identity(),
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

    def test_context_budget_rejects_stale_policy_identity(self) -> None:
        from selection_policy import policy_identity  # noqa: PLC0415
        repo_root = self.temp_dir / "repo"
        skill_path = repo_root / "Skills" / "agent-ops" / "test" / "SKILL.md"
        skill_path.parent.mkdir(parents=True)
        skill_path.write_text("# Test skill\n", encoding="utf-8")
        manifest = self.temp_dir / ".skillsets" / "agent-ops" / "manifest.jsonl"
        manifest.parent.mkdir(parents=True)
        manifest.write_text(json.dumps({
            "skill_set": "agent-ops",
            "source_path": "Skills/agent-ops/test/SKILL.md",
            "provenance": {
                "generator": "test",
                "projection_mode": "rooted",
                "policy_identity": "stale-old-identity",
                "source_revision": "test",
                "source_sha256": check_context_budget.file_hash(skill_path),
            },
        }) + "\n", encoding="utf-8")

        violations = check_context_budget.validate_written_manifest_provenance(
            skillsets_dir=self.temp_dir / ".skillsets",
            repo_root_path=repo_root,
        )

        self.assertIn("SKILLSET_POLICY_IDENTITY_STALE", {violation["code"] for violation in violations})
        stale = [v for v in violations if v["code"] == "SKILLSET_POLICY_IDENTITY_STALE"][0]
        self.assertEqual(stale["expected"], policy_identity())
        self.assertEqual(stale["actual"], "stale-old-identity")


class TestRuntimeBudgetAndConfig(ContextBudgetTempDirTestCase):
    def test_active_projection_mode_detects_mixed(self) -> None:
        import verify_runtime_budget  # noqa: PLC0415
        # All roots present -> rooted
        self.assertEqual(
            verify_runtime_budget._active_projection_mode(set(ROOT_SKILL_SET_NAMES)),
            "rooted",
        )
        # No roots present -> flat
        self.assertEqual(
            verify_runtime_budget._active_projection_mode({"other"}),
            "flat",
        )
        # Some but not all roots present -> mixed
        self.assertEqual(
            verify_runtime_budget._active_projection_mode({ROOT_SKILL_SET_NAMES[0], "other"}),
            "mixed",
        )

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

    # ------------------------------------------------------------------
    # New in this PR: workouts section in context-budget.yaml
    # ------------------------------------------------------------------

    def test_load_config_returns_workouts_section(self) -> None:
        """load_config() must expose workouts.max_skill_context_tokens from context-budget.yaml."""
        config = check_context_budget.load_config()

        self.assertIn("workouts", config)
        self.assertIn("max_skill_context_tokens", config["workouts"])
        self.assertEqual(config["workouts"]["max_skill_context_tokens"], 1500)

    def test_load_config_workouts_defaults_apply_when_file_missing(self) -> None:
        """When no config file exists, workouts defaults are used."""
        missing = self.temp_dir / "nonexistent-budget.yaml"

        config = check_context_budget.load_config(missing)

        self.assertIn("workouts", config)
        self.assertEqual(config["workouts"]["max_skill_context_tokens"], 1500)

    def test_load_config_workouts_can_be_overridden(self) -> None:
        """A YAML file with a custom workouts.max_skill_context_tokens replaces the default."""
        custom_yaml = self.temp_dir / "budget.yaml"
        custom_yaml.write_text(
            "workouts:\n  max_skill_context_tokens: 999\n",
            encoding="utf-8",
        )

        config = check_context_budget.load_config(custom_yaml)

        self.assertEqual(config["workouts"]["max_skill_context_tokens"], 999)

    def test_load_config_workouts_default_preserved_when_section_absent(self) -> None:
        """YAML without a workouts section preserves the default value."""
        partial_yaml = self.temp_dir / "budget.yaml"
        partial_yaml.write_text(
            "routing:\n  max_candidates_returned: 3\n",
            encoding="utf-8",
        )

        config = check_context_budget.load_config(partial_yaml)

        self.assertEqual(config["workouts"]["max_skill_context_tokens"], 1500)

    # ------------------------------------------------------------------
    # New in this PR: command-surface.json allowed in skillsets directory
    # ------------------------------------------------------------------


class TestCommandSurfaceBudgetValidation(ContextBudgetTempDirTestCase):
    def test_context_budget_accepts_valid_command_surface_json(self) -> None:
        """command-surface.json with a handles list must not produce violations."""
        skillsets_dir = self.temp_dir / ".skillsets"
        surface_path = skillsets_dir / "command-surface.json"
        surface_path.parent.mkdir(parents=True)
        surface_path.write_text(
            json.dumps({"generated_from": "rooted_manifests", "handles": [], "handle_count": 0}),
            encoding="utf-8",
        )

        violations = check_context_budget.validate_written_manifest_provenance(
            skillsets_dir=skillsets_dir,
            repo_root_path=REPO_ROOT,
        )

        codes = {v["code"] for v in violations}
        self.assertNotIn("UNOWNED_SKILLSET_FILE", codes)
        self.assertNotIn("INVALID_COMMAND_SURFACE_JSON", codes)
        self.assertNotIn("INVALID_COMMAND_SURFACE_SHAPE", codes)

    def test_context_budget_rejects_invalid_json_in_command_surface(self) -> None:
        """command-surface.json with malformed JSON must trigger INVALID_COMMAND_SURFACE_JSON."""
        skillsets_dir = self.temp_dir / ".skillsets"
        surface_path = skillsets_dir / "command-surface.json"
        surface_path.parent.mkdir(parents=True)
        surface_path.write_text("{bad json!!!", encoding="utf-8")

        violations = check_context_budget.validate_written_manifest_provenance(
            skillsets_dir=skillsets_dir,
            repo_root_path=REPO_ROOT,
        )

        codes = {v["code"] for v in violations}
        self.assertIn("INVALID_COMMAND_SURFACE_JSON", codes)

    def test_context_budget_rejects_command_surface_missing_handles_list(self) -> None:
        """command-surface.json without a handles array must trigger INVALID_COMMAND_SURFACE_SHAPE."""
        skillsets_dir = self.temp_dir / ".skillsets"
        surface_path = skillsets_dir / "command-surface.json"
        surface_path.parent.mkdir(parents=True)
        surface_path.write_text(
            json.dumps({"generated_from": "rooted_manifests", "handle_count": 0}),
            encoding="utf-8",
        )

        violations = check_context_budget.validate_written_manifest_provenance(
            skillsets_dir=skillsets_dir,
            repo_root_path=REPO_ROOT,
        )

        codes = {v["code"] for v in violations}
        self.assertIn("INVALID_COMMAND_SURFACE_SHAPE", codes)

    def test_context_budget_rejects_command_surface_with_non_list_handles(self) -> None:
        """command-surface.json where handles is not a list must trigger INVALID_COMMAND_SURFACE_SHAPE."""
        skillsets_dir = self.temp_dir / ".skillsets"
        surface_path = skillsets_dir / "command-surface.json"
        surface_path.parent.mkdir(parents=True)
        surface_path.write_text(
            json.dumps({"handles": "not-a-list", "handle_count": 0}),
            encoding="utf-8",
        )

        violations = check_context_budget.validate_written_manifest_provenance(
            skillsets_dir=skillsets_dir,
            repo_root_path=REPO_ROOT,
        )

        codes = {v["code"] for v in violations}
        self.assertIn("INVALID_COMMAND_SURFACE_SHAPE", codes)

    def test_context_budget_command_surface_is_not_flagged_as_unowned(self) -> None:
        """command-surface.json at the canonical path must not appear in UNOWNED_SKILLSET_FILE violations."""
        skillsets_dir = self.temp_dir / ".skillsets"
        surface_path = skillsets_dir / "command-surface.json"
        surface_path.parent.mkdir(parents=True)
        surface_path.write_text(
            json.dumps({"generated_from": "rooted_manifests", "handles": [], "handle_count": 0}),
            encoding="utf-8",
        )

        violations = check_context_budget.validate_written_manifest_provenance(
            skillsets_dir=skillsets_dir,
            repo_root_path=REPO_ROOT,
        )

        unowned_paths = [v["path"] for v in violations if v["code"] == "UNOWNED_SKILLSET_FILE"]
        self.assertNotIn(".skillsets/command-surface.json", unowned_paths)

    # ------------------------------------------------------------------
    # New in this PR: updated policy_identity in committed manifests
    # ------------------------------------------------------------------


class TestCommittedManifestProjection(unittest.TestCase):
    def test_committed_manifests_use_current_policy_identity(self) -> None:
        """All rows in every committed manifest.jsonl must carry the current policy identity."""
        skillsets_dir = REPO_ROOT / ".skillsets"
        if not skillsets_dir.exists():
            self.skipTest(".skillsets directory not present")

        from selection_policy import policy_identity  # noqa: PLC0415
        current_identity = policy_identity()

        for manifest_path in sorted(skillsets_dir.rglob("manifest.jsonl")):
            lines = manifest_path.read_text(encoding="utf-8").splitlines()
            for line_no, line in enumerate(lines, start=1):
                if not line.strip():
                    continue
                row = json.loads(line)
                prov = row.get("provenance", {})
                self.assertEqual(
                    prov.get("policy_identity"),
                    current_identity,
                    f"{manifest_path.relative_to(REPO_ROOT)}:{line_no} — "
                    f"expected policy_identity {current_identity!r}, "
                    f"got {prov.get('policy_identity')!r}",
                )

    def test_committed_manifests_have_rooted_projection_mode(self) -> None:
        """All rows in committed manifests must have projection_mode == 'rooted'."""
        skillsets_dir = REPO_ROOT / ".skillsets"
        if not skillsets_dir.exists():
            self.skipTest(".skillsets directory not present")

        for manifest_path in sorted(skillsets_dir.rglob("manifest.jsonl")):
            lines = manifest_path.read_text(encoding="utf-8").splitlines()
            for line_no, line in enumerate(lines, start=1):
                if not line.strip():
                    continue
                row = json.loads(line)
                prov = row.get("provenance", {})
                self.assertEqual(
                    prov.get("projection_mode"),
                    "rooted",
                    f"{manifest_path.relative_to(REPO_ROOT)}:{line_no} — "
                    f"projection_mode must be 'rooted', got {prov.get('projection_mode')!r}",
                )


class TestContextBudgetReport(ContextBudgetTempDirTestCase):
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


if __name__ == "__main__":
    unittest.main()
