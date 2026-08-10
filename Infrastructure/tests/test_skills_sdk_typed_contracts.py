from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest

from pydantic import ValidationError


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk import typed_contracts as contracts  # noqa: E402
from ask.skills_sdk.ci_contracts import validate_ci_policy_preview_receipt  # noqa: E402
from ask.skills_sdk.emitter_contracts import validate_emitter_preview_receipt  # noqa: E402
from ask.skills_sdk.scenario_quality_contracts import validate_scenario_quality_receipt  # noqa: E402
from ask.skills_sdk.scorer_quality_contracts import validate_scorer_quality_receipt  # noqa: E402
from ask.skills_sdk.regression_plan_contracts import validate_regression_plan_receipt  # noqa: E402
from ask.skills_sdk.handoff_readiness_contracts import validate_handoff_readiness_receipt  # noqa: E402
from ask.skills_sdk.static_explorer_contracts import validate_static_explorer_receipt  # noqa: E402


FIXTURE_DIR = REPO_ROOT / "Infrastructure/tests/fixtures/skills_sdk/schema_spine"
PUBLIC_CONTRACT_MODULES = (
    REPO_ROOT / "Infrastructure/scripts/lib/ask/skills_sdk/typed_contracts.py",
    REPO_ROOT / "Infrastructure/scripts/lib/ask/envelope.py",
)


def _json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


class TestSkillsSdkTypedContracts(unittest.TestCase):
    def test_valid_schema_spine_fixtures_load_through_pydantic_contracts(self) -> None:
        cases = (
            ("manifest-source.json", contracts.validate_manifest_source),
            ("skill-ir.json", contracts.validate_skill_ir),
            ("package-digest-receipt.json", contracts.validate_package_digest_receipt),
            ("package-hardening-receipt.json", contracts.validate_package_hardening_receipt),
            ("signing-policy.json", contracts.validate_signing_policy),
            ("signing-intent-receipt.json", contracts.validate_signing_intent_receipt),
            ("sandbox-profile.json", contracts.validate_sandbox_profile),
            ("sandbox-profile-receipt.json", contracts.validate_sandbox_profile_receipt),
            ("eval-case.json", contracts.validate_eval_case),
            ("eval-run-receipt.json", contracts.validate_eval_run_receipt),
            ("check-receipt.json", contracts.validate_check_receipt),
            ("risk-classification.json", contracts.validate_risk_classification),
            ("install-preview.json", contracts.validate_install_preview),
            ("install-receipt.json", contracts.validate_install_receipt),
            ("lockfile.json", contracts.validate_lockfile),
            ("project-conformance-receipt.json", contracts.validate_project_conformance_receipt),
            ("ab-judge-score-receipt.json", contracts.validate_ab_judge_score_receipt),
        )

        for filename, validator in cases:
            with self.subTest(filename=filename):
                model = validator(_json(FIXTURE_DIR / "valid" / filename))
                self.assertEqual(model.model_config["extra"], "forbid")
                self.assertTrue(model.model_config["strict"])

    def test_sdk_status_output_loads_through_status_contract(self) -> None:
        completed = subprocess.run(
            ["./bin/ask", "sdk", "status", "--json", "--robot"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        envelope = contracts.validate_robot_envelope(json.loads(completed.stdout))
        model = contracts.validate_capability_status(envelope.data["skills_sdk_status"])

        self.assertEqual(model.schema_version, "skills-sdk.capability-status.v1")
        self.assertEqual(model.summary.total, len(model.capabilities))
        self.assertGreater(model.summary.total, 0)

    def test_invalid_fixture_is_rejected_by_pydantic_contract(self) -> None:
        with self.assertRaises(ValidationError):
            contracts.validate_install_preview(_json(FIXTURE_DIR / "invalid" / "install-preview-writes.json"))
        with self.assertRaises(ValidationError):
            contracts.validate_project_conformance_receipt(
                _json(FIXTURE_DIR / "invalid" / "project-conformance-writes.json")
            )

    def test_skill_ir_contract_rejects_mutation_claims(self) -> None:
        payload = _json(FIXTURE_DIR / "valid" / "skill-ir.json")
        self.assertIsInstance(payload, dict)
        payload["mutation_performed"] = True

        with self.assertRaises(ValidationError):
            contracts.validate_skill_ir(payload)

    def test_skill_ir_contract_rejects_empty_acceptance_trace(self) -> None:
        payload = _json(FIXTURE_DIR / "valid" / "skill-ir.json")
        self.assertIsInstance(payload, dict)
        payload["acceptance_trace"] = []

        with self.assertRaises(ValidationError):
            contracts.validate_skill_ir(payload)

    def test_package_digest_contract_rejects_mutation_claims(self) -> None:
        payload = _json(FIXTURE_DIR / "valid" / "package-digest-receipt.json")
        self.assertIsInstance(payload, dict)
        payload["mutation_performed"] = True

        with self.assertRaises(ValidationError):
            contracts.validate_package_digest_receipt(payload)

    def test_package_hardening_contract_rejects_mutation_claims(self) -> None:
        payload = _json(FIXTURE_DIR / "valid" / "package-hardening-receipt.json")
        self.assertIsInstance(payload, dict)
        payload["mutation_performed"] = True

        with self.assertRaises(ValidationError):
            contracts.validate_package_hardening_receipt(payload)

    def test_package_hardening_contract_rejects_empty_included_file_items(self) -> None:
        payload = _json(FIXTURE_DIR / "valid" / "package-hardening-receipt.json")
        self.assertIsInstance(payload, dict)
        payload["included_files"] = [""]

        with self.assertRaises(ValidationError):
            contracts.validate_package_hardening_receipt(payload)

    def test_sandbox_profile_receipt_rejects_short_profile_digest(self) -> None:
        payload = _json(FIXTURE_DIR / "valid" / "sandbox-profile-receipt.json")
        self.assertIsInstance(payload, dict)
        payload["profile_digest"] = "x"

        with self.assertRaises(ValidationError):
            contracts.validate_sandbox_profile_receipt(payload)

    def test_signing_intent_contract_rejects_signature_claims(self) -> None:
        payload = _json(FIXTURE_DIR / "valid" / "signing-intent-receipt.json")
        self.assertIsInstance(payload, dict)
        payload["signing_performed"] = True

        with self.assertRaises(ValidationError):
            contracts.validate_signing_intent_receipt(payload)

    def test_signing_intent_contract_rejects_key_material_access_claims(self) -> None:
        payload = _json(FIXTURE_DIR / "valid" / "signing-intent-receipt.json")
        self.assertIsInstance(payload, dict)
        payload["key_material_accessed"] = True

        with self.assertRaises(ValidationError):
            contracts.validate_signing_intent_receipt(payload)

    def test_signing_policy_contract_rejects_archive_requirement(self) -> None:
        payload = _json(FIXTURE_DIR / "valid" / "signing-policy.json")
        self.assertIsInstance(payload, dict)
        payload["archive_required"] = True

        with self.assertRaises(ValidationError):
            contracts.validate_signing_policy(payload)

    def test_signing_policy_contract_rejects_short_package_digest(self) -> None:
        payload = _json(FIXTURE_DIR / "valid" / "signing-policy.json")
        self.assertIsInstance(payload, dict)
        payload["allowed_package_digests"] = ["x"]

        with self.assertRaises(ValidationError):
            contracts.validate_signing_policy(payload)

    def test_sandbox_profile_receipt_contract_rejects_execution_claims(self) -> None:
        payload = _json(FIXTURE_DIR / "valid" / "sandbox-profile-receipt.json")
        self.assertIsInstance(payload, dict)
        payload["execution_performed"] = True

        with self.assertRaises(ValidationError):
            contracts.validate_sandbox_profile_receipt(payload)

    def test_eval_run_contract_rejects_mutation_claims(self) -> None:
        payload = _json(FIXTURE_DIR / "valid" / "eval-run-receipt.json")
        self.assertIsInstance(payload, dict)
        payload["mutation_performed"] = True

        with self.assertRaises(ValidationError):
            contracts.validate_eval_run_receipt(payload)

    def test_blocked_eval_run_contract_accepts_unavailable_dataset_digest(self) -> None:
        payload = _json(FIXTURE_DIR / "valid" / "eval-run-receipt.json")
        self.assertIsInstance(payload, dict)
        payload["status"] = "blocked"
        payload["dataset_digest"] = None
        payload["blockers"] = ["blocked_missing_artifact:dataset"]

        receipt = contracts.validate_eval_run_receipt(payload)

        self.assertIsNone(receipt.dataset_digest)

    def test_emitter_preview_contract_rejects_emission_claims(self) -> None:
        payload = _json(FIXTURE_DIR / "valid" / "emitter-preview-receipt.json")
        self.assertIsInstance(payload, dict)
        payload["artifact_emitted"] = True

        with self.assertRaises(ValidationError):
            validate_emitter_preview_receipt(payload)

    def test_emitter_preview_contract_rejects_duplicate_required_receipts(self) -> None:
        payload = _json(FIXTURE_DIR / "valid" / "emitter-preview-receipt.json")
        self.assertIsInstance(payload, dict)
        payload["required_receipts"] = [
            "package_digest_receipt",
            "package_digest_receipt",
        ]

        with self.assertRaises(ValidationError):
            validate_emitter_preview_receipt(payload)

    def test_emitter_preview_fixture_loads_through_dedicated_contract(self) -> None:
        model = validate_emitter_preview_receipt(_json(FIXTURE_DIR / "valid" / "emitter-preview-receipt.json"))

        self.assertEqual(model.model_config["extra"], "forbid")
        self.assertTrue(model.model_config["strict"])
        self.assertEqual(model.projection, "runtime-skill")

    def test_ci_policy_preview_contract_rejects_hosted_ci_claims(self) -> None:
        payload = _json(FIXTURE_DIR / "valid" / "ci-policy-preview-receipt.json")
        self.assertIsInstance(payload, dict)
        payload["live_ci_evidence_attached"] = True

        with self.assertRaises(ValidationError):
            validate_ci_policy_preview_receipt(payload)

    def test_ci_policy_preview_fixture_loads_through_dedicated_contract(self) -> None:
        model = validate_ci_policy_preview_receipt(_json(FIXTURE_DIR / "valid" / "ci-policy-preview-receipt.json"))

        self.assertEqual(model.model_config["extra"], "forbid")
        self.assertTrue(model.model_config["strict"])
        self.assertEqual(model.risk_tier, "high")

    def test_static_explorer_contract_rejects_html_render_claims(self) -> None:
        payload = _json(FIXTURE_DIR / "valid" / "static-explorer-receipt.json")
        self.assertIsInstance(payload, dict)
        payload["html_rendered"] = True

        with self.assertRaises(ValidationError):
            validate_static_explorer_receipt(payload)

    def test_static_explorer_contract_rejects_unknown_capability_status(self) -> None:
        payload = _json(FIXTURE_DIR / "valid" / "static-explorer-receipt.json")
        self.assertIsInstance(payload, dict)
        payload["capability_index"][0]["status"] = "unknown"

        with self.assertRaises(ValidationError):
            validate_static_explorer_receipt(payload)

    def test_static_explorer_contract_rejects_empty_skill_set_items(self) -> None:
        payload = _json(FIXTURE_DIR / "valid" / "static-explorer-receipt.json")
        self.assertIsInstance(payload, dict)
        payload["skill_sets"] = [""]

        with self.assertRaises(ValidationError):
            validate_static_explorer_receipt(payload)

    def test_static_explorer_contract_rejects_empty_evidence_items(self) -> None:
        payload = _json(FIXTURE_DIR / "valid" / "static-explorer-receipt.json")
        self.assertIsInstance(payload, dict)
        payload["explorer_checks"][0]["evidence"] = [""]

        with self.assertRaises(ValidationError):
            validate_static_explorer_receipt(payload)

    def test_static_explorer_fixture_loads_through_dedicated_contract(self) -> None:
        model = validate_static_explorer_receipt(_json(FIXTURE_DIR / "valid" / "static-explorer-receipt.json"))

        self.assertEqual(model.model_config["extra"], "forbid")
        self.assertTrue(model.model_config["strict"])
        self.assertEqual(model.capability_count, 1)

    def test_scenario_quality_contract_rejects_promotion_claims(self) -> None:
        payload = _json(FIXTURE_DIR / "valid" / "scenario-quality-receipt.json")
        self.assertIsInstance(payload, dict)
        payload["promotion_performed"] = True

        with self.assertRaises(ValidationError):
            validate_scenario_quality_receipt(payload)

    def test_scenario_quality_fixture_loads_through_dedicated_contract(self) -> None:
        model = validate_scenario_quality_receipt(_json(FIXTURE_DIR / "valid" / "scenario-quality-receipt.json"))

        self.assertEqual(model.model_config["extra"], "forbid")
        self.assertTrue(model.model_config["strict"])
        self.assertEqual(model.scenario_count, 1)

    def test_scorer_quality_contract_rejects_promotion_claims(self) -> None:
        payload = _json(FIXTURE_DIR / "valid" / "scorer-quality-receipt.json")
        self.assertIsInstance(payload, dict)
        payload["promotion_performed"] = True

        with self.assertRaises(ValidationError):
            validate_scorer_quality_receipt(payload)

    def test_scorer_quality_fixture_loads_through_dedicated_contract(self) -> None:
        model = validate_scorer_quality_receipt(_json(FIXTURE_DIR / "valid" / "scorer-quality-receipt.json"))

        self.assertEqual(model.model_config["extra"], "forbid")
        self.assertTrue(model.model_config["strict"])
        self.assertTrue(model.ready)

    def test_regression_plan_contract_rejects_readiness_claims_with_blockers(self) -> None:
        payload = _json(FIXTURE_DIR / "valid" / "regression-plan-receipt.json")
        self.assertIsInstance(payload, dict)
        payload["ready_for_live_rerun"] = False

        with self.assertRaises(ValidationError):
            validate_regression_plan_receipt(payload)

    def test_regression_plan_fixture_loads_through_dedicated_contract(self) -> None:
        model = validate_regression_plan_receipt(_json(FIXTURE_DIR / "valid" / "regression-plan-receipt.json"))

        self.assertEqual(model.model_config["extra"], "forbid")
        self.assertTrue(model.model_config["strict"])
        self.assertTrue(model.ready_for_live_rerun)
        self.assertEqual(model.regression_count, 1)

    def test_handoff_readiness_contract_rejects_readiness_claims_with_blockers(self) -> None:
        payload = _json(FIXTURE_DIR / "valid" / "handoff-readiness-receipt.json")
        self.assertIsInstance(payload, dict)
        payload["ready_for_live_tessl"] = False

        with self.assertRaises(ValidationError):
            validate_handoff_readiness_receipt(payload)

    def test_handoff_readiness_contract_rejects_legacy_partial_lane_receipt(self) -> None:
        with self.assertRaises(ValidationError):
            validate_handoff_readiness_receipt(_json(FIXTURE_DIR / "valid" / "handoff-readiness-receipt.json"))

    def test_eval_run_contract_accepts_legacy_receipt_without_package_identity(self) -> None:
        payload = _json(FIXTURE_DIR / "valid" / "eval-run-receipt.json")
        self.assertIsInstance(payload, dict)
        payload.pop("package_id")
        payload.pop("package_digest")

        model = contracts.validate_eval_run_receipt(payload)

        self.assertIsNone(model.package_id)
        self.assertIsNone(model.package_digest)

    def test_eval_run_contract_accepts_internal_quality_gates(self) -> None:
        payload = _json(FIXTURE_DIR / "valid" / "eval-run-receipt.json")
        self.assertIsInstance(payload, dict)
        payload["runner"] = "internal_skill_builder_v0"
        payload["quality_gates"] = {
            "source": "internal_scorecard",
            "scorecard_schema_version": "2.1",
            "decision": "pass",
            "passed": True,
            "promotion_eligible": None,
            "case_count": 1,
            "blocked_cases": 0,
            "tier1_failures": 0,
            "tier2_findings": 0,
            "preflight_warning_count": 0,
            "readiness_summary": {"unknown": 1},
            "expected_signal_summary": {"runs": 0, "average": None, "minimum": None, "risky_cases": []},
            "security_dependency_screening_status": "skipped",
            "assertions": [
                {
                    "id": "scorecard_decision_passes",
                    "status": "pass",
                    "expected": "decision == pass",
                    "actual": "pass",
                }
            ],
            "failed_assertions": [],
        }

        model = contracts.validate_eval_run_receipt(payload)

        self.assertIsNotNone(model.quality_gates)
        self.assertEqual(model.quality_gates.source, "internal_scorecard")
        self.assertEqual(model.quality_gates.assertions[0].id, "scorecard_decision_passes")

    def test_trust_decision_contract_rejects_recorded_receipt_without_mutation(self) -> None:
        payload = _json(FIXTURE_DIR / "valid" / "trust-decision-receipt.json")
        self.assertIsInstance(payload, dict)
        payload["status"] = "recorded"
        payload["mutation_performed"] = False

        with self.assertRaises(ValidationError):
            contracts.validate_trust_decision_receipt(payload)

    def test_trust_decision_contract_rejects_mutating_preview_receipt(self) -> None:
        payload = _json(FIXTURE_DIR / "valid" / "trust-decision-receipt.json")
        self.assertIsInstance(payload, dict)
        payload["status"] = "preview"
        payload["mutation_performed"] = True

        with self.assertRaises(ValidationError):
            contracts.validate_trust_decision_receipt(payload)

    def test_contracts_reject_type_coercion(self) -> None:
        """
        Verify that the check-receipt contract enforces strict types for fields.

        This test loads the canonical valid check-receipt fixture, changes the `exit_code`
        value from a numeric type to the string `"0"`, and asserts that validating the
        modified payload raises a `ValidationError`.

        Raises:
            ValidationError if the contract incorrectly accepts a coerced `exit_code` (this test expects a ValidationError).
        """
        payload = _json(FIXTURE_DIR / "valid" / "check-receipt.json")
        self.assertIsInstance(payload, dict)
        payload["exit_code"] = "0"

        with self.assertRaises(ValidationError):
            contracts.validate_check_receipt(payload)

    def test_robot_envelope_contract_accepts_standard_success_shape(self) -> None:
        payload = {
            "status": "success",
            "trace_id": "trace-1",
            "metadata": {
                "version": "0.1.0",
                "command": "repo validate --scope=skills-sdk",
                "next_steps": [],
                "correction_note": None,
            },
            "data": {"required_failures": 0},
            "telemetry": {"latency_ms": 12},
            "errors": [],
        }

        model = contracts.validate_robot_envelope(payload)

        self.assertEqual(model.metadata.command, "repo validate --scope=skills-sdk")
        self.assertEqual(model.data["required_failures"], 0)


if __name__ == "__main__":
    unittest.main()
