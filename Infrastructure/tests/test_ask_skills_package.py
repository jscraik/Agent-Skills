import importlib
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

skills_impl = importlib.import_module("ask.commands.skills_impl")
_package_verify = importlib.import_module("ask.skills_sdk.package_verify")
_fixtures = importlib.import_module("helpers.ask_skills_package_fixtures")

skills_package = skills_impl.skills_package
skills_package_verify = skills_impl.skills_package_verify
skills_package_verify_strict = skills_impl.skills_package_verify_strict
_quality_blockers = _package_verify._quality_blockers
_quality_checks = _package_verify._quality_checks
_write_gold_quality_skill = _fixtures.write_gold_quality_skill
_write_minimal_sdk_package_companions = _fixtures.write_minimal_sdk_package_companions
_write_advisory_quality_skill = _fixtures.write_advisory_quality_skill
_write_package_metadata_skill = _fixtures.write_package_metadata_skill
_write_weak_quality_skill = _fixtures.write_weak_quality_skill


class TestAskSkillsPackage(unittest.TestCase):
    def test_package_accepts_legacy_positional_strict_flag(self) -> None:
        expected = object()
        with patch.object(skills_impl, "_skills_package", return_value=expected) as package:
            result = skills_package(REPO_ROOT, "example-skill", True)

        self.assertIs(result, expected)
        package.assert_called_once_with(
            REPO_ROOT,
            "example-skill",
            strict=True,
            checkout_test=False,
        )

    def test_package_merges_legacy_positional_and_keyword_options(self) -> None:
        expected = object()
        with patch.object(skills_impl, "_skills_package", return_value=expected) as package:
            result = skills_package(REPO_ROOT, "example-skill", True, checkout_test=True)

        self.assertIs(result, expected)
        package.assert_called_once_with(
            REPO_ROOT,
            "example-skill",
            strict=True,
            checkout_test=True,
        )

    def test_package_verify_blocks_weak_skill_writing_quality(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "packaged-skill"
            _write_weak_quality_skill(skill_dir)

            result = skills_package_verify(repo_root, "Skills/agent-ops/packaged-skill")

        self.assertEqual(result.status, "error")
        verification = result.data["skill_package_verification"]
        self.assertEqual(verification["status"], "blocked")
        self.assertEqual(verification["blockers"][0]["rule_id"], "skill_writing_quality_blocked")
        writing_quality = verification["sdk_contract"]["values"]["writing_quality"]
        self.assertEqual(writing_quality["schema_version"], "skills-sdk.skill-writing-quality.v1")
        self.assertEqual(writing_quality["status"], "blocked_validation")
        rule_ids = {blocker["rule_id"] for blocker in writing_quality["blockers"]}
        self.assertIn("weak_description_triggers", rule_ids)
        self.assertIn("scenario_alignment_gold_shape_incomplete", rule_ids)
        self.assertIn(
            "behavioral_eval_pass",
            writing_quality["what_this_does_not_prove"],
        )

    def test_package_verify_accepts_gold_standard_writing_quality(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "packaged-skill"
            _write_gold_quality_skill(skill_dir)

            result = skills_package_verify(repo_root, "Skills/agent-ops/packaged-skill")

        self.assertEqual(result.status, "success", result.data)
        verification = result.data["skill_package_verification"]
        self.assertEqual(verification["status"], "pass")
        writing_quality = verification["sdk_contract"]["values"]["writing_quality"]
        self.assertEqual(writing_quality["status"], "pass")
        self.assertEqual(writing_quality["blockers"], [])
        self.assertEqual(writing_quality["advisories"], [])
        self.assertIn("writing_quality", [check["name"] for check in verification["checks"]])

    def test_package_verify_strict_requires_package_readiness(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "packaged-skill"
            _write_gold_quality_skill(skill_dir)
            skill_path = skill_dir / "SKILL.md"
            skill_path.write_text(
                skill_path.read_text(encoding="utf-8").replace(
                    "  compatible_roles:\n    - worker\n  runtime_needs:\n    - filesystem\n  maturity: beta\n",
                    "",
                ).replace("  share_readiness: ready\n", ""),
                encoding="utf-8",
            )

            non_strict = skills_package_verify(repo_root, "Skills/agent-ops/packaged-skill")
            strict = skills_package_verify_strict(
                repo_root,
                "Skills/agent-ops/packaged-skill",
            )

        self.assertEqual(non_strict.status, "success", non_strict.data)
        self.assertEqual(strict.status, "error", strict.data)
        non_strict_verification = non_strict.data["skill_package_verification"]
        self.assertFalse(non_strict_verification["strict"])
        self.assertEqual(non_strict_verification["status"], "pass")
        verification = strict.data["skill_package_verification"]
        self.assertTrue(verification["strict"])
        self.assertEqual(verification["status"], "blocked")
        self.assertEqual(
            verification["next_command"],
            "./bin/ask skills package Skills/agent-ops/packaged-skill --strict --json --robot",
        )
        readiness = verification["strict_package_readiness"]
        self.assertEqual(readiness["canonical_source_path"], "Skills/agent-ops/packaged-skill/SKILL.md")
        self.assertEqual(
            readiness["package_contract"]["required_fields"]["missing"],
            ["compatible_roles", "maturity", "runtime_needs", "share_readiness"],
        )

    def test_package_verify_strict_pass_advances_to_target_proof(self) -> None:
        """A passing strict package gate advances the same target to outcome proof."""
        result = skills_package_verify_strict(
            REPO_ROOT,
            "Skills/agent-ops/simplify",
        )

        self.assertEqual(result.status, "success", result.data)
        verification = result.data["skill_package_verification"]
        self.assertEqual(verification["status"], "pass")
        self.assertEqual(
            verification["next_command"],
            "./bin/ask skills prove Skills/agent-ops/simplify --json --robot",
        )

    def test_package_verify_missing_target_starts_target_resolution(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = skills_package_verify(Path(temp_dir), "missing-skill")

        self.assertEqual(result.status, "error")
        verification = result.data["skill_package_verification"]
        self.assertEqual(
            verification["next_command"],
            "./bin/ask sdk start missing-skill --json --robot",
        )

    def test_package_verify_reports_orphaned_bundle_reference_advisory(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "review-advisory"
            _write_advisory_quality_skill(skill_dir)

            result = skills_package_verify(repo_root, "Skills/agent-ops/review-advisory")

        self.assertEqual(result.status, "success", result.data)
        verification = result.data["skill_package_verification"]
        writing_quality = verification["sdk_contract"]["values"]["writing_quality"]
        self.assertEqual(writing_quality["status"], "pass", writing_quality)
        self.assertEqual(writing_quality["blockers"], [])
        advisory_ids = {advisory["rule_id"] for advisory in writing_quality["advisories"]}
        self.assertGreaterEqual(
            advisory_ids,
            {
                "description_trigger_terms_missing",
                "review_lens_output_contract_missing",
                "missing_untrusted_input_boundary",
                "improvement_claim_without_before_after_evidence",
                "orphaned_bundle_reference",
            },
        )

    def test_package_verify_quality_helpers_block_empty_blocked_validation_details(self) -> None:
        quality = {
            "reference_quality": {"status": "pass", "blockers": []},
            "writing_quality": {"status": "blocked_validation", "blockers": []},
            "authoring_contract": {"status": "not_applicable", "blockers": []},
            "openai_platform_compat": {"status": "blocked_validation", "blockers": "malformed"},
        }

        blockers = _quality_blockers(quality)
        blocker_ids = {blocker["rule_id"] for blocker in blockers}
        checks = {check["name"]: check for check in _quality_checks(quality)}

        self.assertIn("skill_writing_quality_blocked", blocker_ids)
        self.assertIn("openai_platform_compat_blocked", blocker_ids)
        self.assertEqual(checks["writing_quality"]["status"], "fail")
        self.assertEqual(checks["openai_platform_compat"]["status"], "fail")

    def test_package_reports_versioned_role_ready_contract(self) -> None:
        with patch("ask.commands.skills_impl.resolve_skill_handle", return_value={
            "status": "ok",
            "handle": "skill-factory-router",
            "source_path": "Plugins/skill-factory/skills/skill-factory-router/SKILL.md",
        }):
            result = skills_package(REPO_ROOT, "skill-factory-router")

        self.assertEqual(result.status, "success")
        package = result.data["skill_package"]
        self.assertEqual(package["schema_version"], "skill-package-readiness.v1")
        self.assertEqual(package["gate_summary"]["promotion_status"], "ready_pending_checkout")
        self.assertFalse(package["gate_summary"]["promotion_ready"])
        contract = package["package_contract"]
        self.assertEqual(contract["values"]["version"], "1.0.0")
        self.assertEqual(contract["values"]["maturity"], "canonical")
        self.assertEqual(contract["required_fields"]["missing"], [])
        self.assertTrue(contract["install_gate"]["install_ready"])
        self.assertEqual(contract["install_gate"]["blocked_reasons"], [])
        self.assertEqual(contract["install_gate"]["checkout_test"]["status"], "not_run")
        self.assertEqual(contract["promotion_gate"]["status"], "ready_pending_checkout")
        self.assertFalse(contract["promotion_gate"]["promotion_ready"])
        self.assertTrue(contract["promotion_gate"]["share_ready"])
        self.assertEqual(contract["promotion_gate"]["blocked_reasons"], [])
        self.assertEqual(contract["promotion_gate"]["recommended_next_fields"], [])
        self.assertEqual(package["lifecycle_event"]["event_type"], "package_readiness_checked")
        self.assertEqual(
            [event["event_type"] for event in package["lifecycle_events"]],
            ["skill_loaded", "package_readiness_checked"],
        )
        self.assertNotIn("details", package["lifecycle_events"][0])
        self.assertEqual(
            package["lifecycle_events"][1]["details"]["gate_summary"],
            package["gate_summary"],
        )
        self.assertIn("package_readiness_checked", [event["event_type"] for event in package["lifecycle_events"]])

    def test_package_strict_accepts_complete_package_metadata(self) -> None:
        with patch("ask.commands.skills_impl.resolve_skill_handle", return_value={
            "status": "ok",
            "handle": "skill-factory-router",
            "source_path": "Plugins/skill-factory/skills/skill-factory-router/SKILL.md",
        }):
            result = skills_package(REPO_ROOT, "skill-factory-router", strict=True)

        self.assertEqual(result.status, "success")
        package = result.data["skill_package"]
        self.assertEqual(package["status"], "pass")
        self.assertEqual(package["blockers"], [])
        self.assertIn("package_readiness_checked", [event["event_type"] for event in package["lifecycle_events"]])
        self.assertEqual(package["gate_summary"]["promotion_status"], "ready_pending_checkout")
        self.assertEqual(package["package_contract"]["required_fields"]["missing"], [])
        self.assertEqual(result.errors, [])

    def test_package_blocks_missing_source(self) -> None:
        with patch("ask.commands.skills_impl.resolve_skill_handle", return_value={
            "status": "ok",
            "handle": "missing-skill",
            "source_path": "Skills/agent-ops/missing-skill/SKILL.md",
        }):
            result = skills_package(REPO_ROOT, "missing-skill")

        self.assertEqual(result.status, "error")
        package = result.data["skill_package"]
        self.assertEqual(package["status"], "blocked")
        self.assertEqual(package["blockers"][0]["class"], "blocked_missing_source")
        self.assertFalse(package["package_contract"]["install_gate"]["install_ready"])
        self.assertEqual(
            package["package_contract"]["install_gate"]["checkout_test"]["status"],
            "not_run",
        )
        self.assertEqual(
            package["package_contract"]["promotion_gate"]["status"],
            "blocked_missing_source",
        )
        self.assertEqual(package["next_command"], "./bin/ask skills doctor missing-skill --json --robot")

    def test_package_checkout_test_blocks_missing_source(self) -> None:
        with patch("ask.commands.skills_impl.resolve_skill_handle", return_value={
            "status": "ok",
            "handle": "missing-skill",
            "source_path": "Skills/agent-ops/missing-skill/SKILL.md",
        }):
            result = skills_package(REPO_ROOT, "missing-skill", checkout_test=True)

        self.assertEqual(result.status, "error")
        package = result.data["skill_package"]
        self.assertEqual(package["status"], "blocked")
        self.assertEqual(
            package["package_contract"]["install_gate"]["checkout_test"]["status"],
            "blocked_missing_source",
        )
        self.assertEqual(package["next_command"], "./bin/ask skills doctor missing-skill --json --robot")

    def test_package_reads_nested_block_list_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "packaged-skill"
            _write_package_metadata_skill(
                skill_dir,
                roles=("worker", "reviewer"),
                runtime_needs=("network", "filesystem"),
            )
            _write_minimal_sdk_package_companions(skill_dir)

            result = skills_package(repo_root, "Skills/agent-ops/packaged-skill")

        self.assertEqual(result.status, "success")
        package = result.data["skill_package"]
        self.assertEqual(package["status"], "pass")
        self.assertEqual(package["gate_summary"]["promotion_status"], "ready_pending_checkout")
        self.assertFalse(package["gate_summary"]["promotion_ready"])
        self.assertEqual(package["gate_summary"]["checkout_test_status"], "not_run")
        contract = package["package_contract"]
        self.assertEqual(contract["required_fields"]["missing"], [])
        self.assertEqual(contract["role_compatibility"]["roles"], ["worker", "reviewer"])
        self.assertEqual(contract["runtime_contract"]["needs"], ["network", "filesystem"])
        self.assertTrue(contract["install_gate"]["install_ready"])
        self.assertEqual(contract["install_gate"]["blocked_reasons"], [])
        self.assertEqual(contract["install_gate"]["checkout_test"]["status"], "not_run")
        self.assertEqual(contract["promotion_gate"]["status"], "ready_pending_checkout")
        self.assertFalse(contract["promotion_gate"]["promotion_ready"])
        self.assertEqual(contract["promotion_gate"]["checkout_test_status"], "not_run")
        self.assertEqual(contract["promotion_gate"]["blocked_reasons"], [])
        self.assertTrue(contract["promotion_gate"]["share_ready"])

    def test_package_reads_top_level_package_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "packaged-skill"
            _write_package_metadata_skill(
                skill_dir,
                nested_metadata=False,
                roles=("worker", "reviewer"),
            )
            _write_minimal_sdk_package_companions(skill_dir)

            result = skills_package(repo_root, "Skills/agent-ops/packaged-skill")

        self.assertEqual(result.status, "success")
        contract = result.data["skill_package"]["package_contract"]
        self.assertEqual(contract["required_fields"]["missing"], [])
        self.assertEqual(contract["role_compatibility"]["roles"], ["worker", "reviewer"])
        self.assertEqual(contract["runtime_contract"]["needs"], ["filesystem"])
        self.assertTrue(contract["install_gate"]["install_ready"])

    def test_package_blocks_declared_non_ready_share_readiness(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "packaged-skill"
            _write_package_metadata_skill(skill_dir, share_readiness="draft")
            _write_minimal_sdk_package_companions(skill_dir)

            result = skills_package(repo_root, "Skills/agent-ops/packaged-skill")

        self.assertEqual(result.status, "success")
        package = result.data["skill_package"]
        self.assertEqual(package["status"], "warning")
        contract = package["package_contract"]
        self.assertEqual(contract["required_fields"]["missing"], [])
        self.assertFalse(contract["install_gate"]["install_ready"])
        self.assertIn("share_readiness_not_ready", contract["install_gate"]["blocked_reasons"])
        self.assertEqual(contract["promotion_gate"]["status"], "blocked_validation")
        self.assertFalse(contract["promotion_gate"]["promotion_ready"])
        self.assertFalse(contract["promotion_gate"]["share_ready"])
        self.assertEqual(contract["promotion_gate"]["recommended_next_fields"], ["share_readiness"])

    def test_package_checkout_test_records_local_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "packaged-skill"
            _write_package_metadata_skill(skill_dir)
            _write_minimal_sdk_package_companions(skill_dir)

            result = skills_package(repo_root, "Skills/agent-ops/packaged-skill", checkout_test=True)

        self.assertEqual(result.status, "success")
        checkout = result.data["skill_package"]["package_contract"]["install_gate"]["checkout_test"]
        self.assertEqual(checkout["status"], "pass")
        self.assertIn("source_path:Skills/agent-ops/packaged-skill/SKILL.md", checkout["evidence"])
        self.assertIn("package_metadata_complete:true", checkout["evidence"])
        self.assertEqual(
            result.data["skill_package"]["gate_summary"],
            {
                "install_ready": True,
                "checkout_test_status": "pass",
                "promotion_status": "ready",
                "promotion_ready": True,
                "blocked_reasons": [],
            },
        )
        self.assertEqual(
            result.data["skill_package"]["lifecycle_events"][1]["details"]["gate_summary"],
            result.data["skill_package"]["gate_summary"],
        )
        promotion = result.data["skill_package"]["package_contract"]["promotion_gate"]
        self.assertEqual(promotion["status"], "ready")
        self.assertTrue(promotion["promotion_ready"])
        self.assertEqual(promotion["checkout_test_status"], "pass")

    def test_package_checkout_test_records_skill_builder_evidence(self) -> None:
        with patch("ask.commands.skills_impl.resolve_skill_handle", return_value={
            "status": "ok",
            "handle": "skill-factory-router",
            "source_path": "Plugins/skill-factory/skills/skill-factory-router/SKILL.md",
        }):
            result = skills_package(REPO_ROOT, "skill-factory-router", checkout_test=True)

        self.assertEqual(result.status, "success")
        package = result.data["skill_package"]
        self.assertEqual(package["status"], "pass")
        checkout = package["package_contract"]["install_gate"]["checkout_test"]
        self.assertEqual(checkout["status"], "pass")
        self.assertIn(
            "source_path:Plugins/skill-factory/skills/skill-factory-router/SKILL.md",
            checkout["evidence"],
        )
        self.assertIn("package_metadata_complete:true", checkout["evidence"])
        self.assertEqual(package["gate_summary"]["promotion_status"], "ready")
        self.assertTrue(package["gate_summary"]["promotion_ready"])

    def test_package_checkout_test_blocks_incomplete_identity(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "packaged-skill"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                """---
version: "2.0.0"
metadata:
  compatible_roles:
    - worker
  runtime_needs:
    - filesystem
  maturity: beta
  provenance: internal
  share_readiness: ready
---

# Packaged Skill
""",
                encoding="utf-8",
            )

            result = skills_package(repo_root, "Skills/agent-ops/packaged-skill", strict=True, checkout_test=True)

        self.assertEqual(result.status, "error")
        package = result.data["skill_package"]
        contract = package["package_contract"]
        self.assertEqual(contract["readiness_level"], "incomplete_identity")
        self.assertEqual(contract["install_gate"]["checkout_test"]["status"], "blocked_validation")
        self.assertIn("identity_incomplete", contract["promotion_gate"]["blocked_reasons"])
        self.assertFalse(contract["promotion_gate"]["promotion_ready"])
        self.assertFalse(package["gate_summary"]["promotion_ready"])

    def test_package_checkout_test_blocks_non_ready_share_readiness(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "packaged-skill"
            _write_package_metadata_skill(skill_dir, share_readiness="draft")
            _write_minimal_sdk_package_companions(skill_dir)

            result = skills_package(repo_root, "Skills/agent-ops/packaged-skill", checkout_test=True)

        self.assertEqual(result.status, "success")
        checkout = result.data["skill_package"]["package_contract"]["install_gate"]["checkout_test"]
        self.assertEqual(checkout["status"], "blocked_validation")
        self.assertIn("promotion_gate_blocked:share_readiness_not_ready", checkout["evidence"])


if __name__ == "__main__":
    unittest.main()
