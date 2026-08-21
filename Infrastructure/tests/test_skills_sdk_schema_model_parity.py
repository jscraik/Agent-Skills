from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import unittest

from pydantic import ValidationError
import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk import schema_validation  # noqa: E402
from ask.skills_sdk import typed_contracts as contracts  # noqa: E402


SCHEMA_DIR = REPO_ROOT / "Infrastructure/config/schemas/skills-sdk"
FIXTURE_DIR = REPO_ROOT / "Infrastructure/tests/fixtures/skills_sdk/schema_spine"
SCHEMA_FILES = {
    "manifest-source": "manifest-source.v1.schema.json",
    "check-receipt": "check-receipt.v1.schema.json",
    "sdk-check": "sdk-check.v1.schema.json",
    "risk-classification": "risk-classification.v1.schema.json",
    "install-preview": "install-preview.v1.schema.json",
    "install-receipt": "install-receipt.v1.schema.json",
    "lockfile-preview": "lockfile-preview.v1.schema.json",
    "lockfile": "lockfile.v1.schema.json",
    "skill-intake-receipt": "skill-intake-receipt.v0.schema.json",
}


def _json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def _sdk_check_with_verdict(
    payload: dict, status: str, doctor_status: str | None, exit_code: int
) -> dict:
    return {
        **payload,
        "status": status,
        "failure_class": "validation_failed",
        "doctor_status": doctor_status,
        "receipt": {
            **payload["receipt"],
            "status": status,
            "failure_class": "validation_failed",
            "exit_code": exit_code,
        },
    }


class TestSkillsSdkSchemaModelParity(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schemas = {
            name: _json(SCHEMA_DIR / filename)
            for name, filename in SCHEMA_FILES.items()
        }
        cls.schemas_by_file = {
            filename: _json(SCHEMA_DIR / filename)
            for filename in SCHEMA_FILES.values()
        }

    def assert_schema_passes(self, schema_key: str, fixture_name: str) -> object:
        payload = _json(FIXTURE_DIR / "valid" / fixture_name)
        result = schema_validation.validate_payload_against_schema(
            payload,
            self.schemas[schema_key],
            {**self.schemas, **self.schemas_by_file},
            schema_path=SCHEMA_DIR / SCHEMA_FILES[schema_key],
            payload_source=f"fixture:{fixture_name}",
            truth_lane="schema_contract",
        )
        self.assertEqual(result.status, "pass", result.diagnostics)
        return payload

    def assert_schema_fails(self, schema_key: str, fixture_name: str) -> schema_validation.SchemaValidationResult:
        payload = _json(FIXTURE_DIR / "invalid" / fixture_name)
        result = schema_validation.validate_payload_against_schema(
            payload,
            self.schemas[schema_key],
            {**self.schemas, **self.schemas_by_file},
            schema_path=SCHEMA_DIR / SCHEMA_FILES[schema_key],
            payload_source=f"fixture:{fixture_name}",
            truth_lane="schema_contract",
        )
        self.assertEqual(result.status, "fail")
        self.assertEqual(result.diagnostics[0].status, "fail")
        self.assertEqual(result.diagnostics[0].truth_lane, "schema_contract")
        return result

    def test_positive_fixtures_pass_schema_and_pydantic_models(self) -> None:
        cases = (
            ("manifest-source", "manifest-source.json", contracts.validate_manifest_source),
            ("check-receipt", "check-receipt.json", contracts.validate_check_receipt),
            ("sdk-check", "sdk-check.json", contracts.validate_skills_sdk_check),
            ("risk-classification", "risk-classification.json", contracts.validate_risk_classification),
            ("install-preview", "install-preview.json", contracts.validate_install_preview),
            ("install-receipt", "install-receipt.json", contracts.validate_install_receipt),
            ("lockfile", "lockfile.json", contracts.validate_lockfile),
            ("skill-intake-receipt", "skill-intake-receipt.json", contracts.validate_skill_intake_receipt),
        )

        for schema_key, fixture_name, validator in cases:
            with self.subTest(fixture_name=fixture_name):
                payload = self.assert_schema_passes(schema_key, fixture_name)
                validator(payload)

    def test_invalid_install_preview_fails_schema_and_model(self) -> None:
        result = self.assert_schema_fails("install-preview", "install-preview-writes.json")
        self.assertIn("$.lockfile_delta_preview.would_write", result.diagnostics[0].json_path)

        with self.assertRaises(ValidationError):
            contracts.validate_install_preview(_json(FIXTURE_DIR / "invalid" / "install-preview-writes.json"))

    def test_invalid_check_receipt_status_fails_schema_and_model(self) -> None:
        result = self.assert_schema_fails("check-receipt", "check-receipt-pass-placeholder.json")
        self.assertIn("$.status", result.diagnostics[0].json_path)

        with self.assertRaises(ValidationError):
            contracts.validate_check_receipt(_json(FIXTURE_DIR / "invalid" / "check-receipt-pass-placeholder.json"))

    def test_check_receipt_rejects_waiver_values(self) -> None:
        payload = _json(FIXTURE_DIR / "valid" / "check-receipt.json")
        self.assertIsInstance(payload, dict)
        cases = (
            ("manual_waiver_evidence", {**payload, "proof": {**payload["proof"], "evidence_kind": "manual_waiver"}}),
            ("waived_approval", {**payload, "approval_decision": "waived"}),
        )

        for case_name, invalid_payload in cases:
            with self.subTest(case_name=case_name):
                result = schema_validation.validate_payload_against_schema(
                    invalid_payload,
                    self.schemas["check-receipt"],
                    {**self.schemas, **self.schemas_by_file},
                    schema_path=SCHEMA_DIR / SCHEMA_FILES["check-receipt"],
                    payload_source=f"inline:{case_name}",
                    truth_lane="schema_contract",
                )
                self.assertEqual(result.status, "fail", result.diagnostics)
                with pytest.raises(ValidationError):
                    contracts.validate_check_receipt(copy.deepcopy(invalid_payload))

    def test_invalid_sdk_check_missing_contract_fields_fails_schema_and_model(self) -> None:
        for fixture_name, missing_field in (
            ("sdk-check-missing-canonical-source-path.json", "canonical_source_path"),
            ("sdk-check-missing-claims-boundary.json", "claims_boundary"),
        ):
            with self.subTest(fixture_name=fixture_name):
                result = self.assert_schema_fails("sdk-check", fixture_name)
                self.assertIn(missing_field, result.diagnostics[0].json_path)

                with self.assertRaises(ValidationError):
                    contracts.validate_skills_sdk_check(_json(FIXTURE_DIR / "invalid" / fixture_name))

    def test_sdk_check_model_rejects_empty_or_contradictory_contract_values(self) -> None:
        payload = _json(FIXTURE_DIR / "valid" / "sdk-check.json")
        self.assertIsInstance(payload, dict)
        cases = (
            ("empty_query", {**payload, "query": ""}),
            ("empty_canonical_source_path", {**payload, "canonical_source_path": ""}),
            ("empty_canonical_command", {**payload, "canonical_command": ""}),
            ("empty_agent_summary", {**payload, "agent_summary": ""}),
            ("empty_validation_commands", {**payload, "validation_commands": []}),
            ("empty_validation_command", {**payload, "validation_commands": [""]}),
            ("empty_next_command", {**payload, "next_command": ""}),
            ("broadened_claims_boundary", {**payload, "claims_boundary": "This proves package readiness."}),
            (
                "contradictory_receipt_status",
                {**payload, "receipt": {**payload["receipt"], "status": "blocked", "failure_class": "validation_failed"}},
            ),
        )

        for case_name, invalid_payload in cases:
            with self.subTest(case_name=case_name):
                with self.assertRaises(ValidationError):
                    contracts.validate_skills_sdk_check(copy.deepcopy(invalid_payload))

    def test_sdk_check_model_rejects_passing_contract_contradictions(self) -> None:
        payload = _json(FIXTURE_DIR / "valid" / "sdk-check.json")
        self.assertIsInstance(payload, dict)
        cases = (
            ("passing_check_without_source", {**payload, "canonical_source_path": None}),
            ("passing_check_with_blocked_doctor", {**payload, "doctor_status": "blocked"}),
            ("passing_check_with_failure_exit_code", {**payload, "receipt": {**payload["receipt"], "exit_code": 2}}),
        )

        for case_name, invalid_payload in cases:
            with self.subTest(case_name=case_name):
                with self.assertRaises(ValidationError):
                    contracts.validate_skills_sdk_check(copy.deepcopy(invalid_payload))

    def test_sdk_check_model_rejects_blocked_contract_contradictions(self) -> None:
        payload = _json(FIXTURE_DIR / "valid" / "sdk-check.json")
        self.assertIsInstance(payload, dict)
        blocked_payload = _sdk_check_with_verdict(payload, "blocked", "blocked", 2)
        cases = (
            (
                "blocked_check_with_warning_doctor",
                {**blocked_payload, "doctor_status": "warning"},
            ),
            (
                "blocked_check_with_success_exit_code",
                {**blocked_payload, "receipt": {**blocked_payload["receipt"], "exit_code": 0}},
            ),
        )

        for case_name, invalid_payload in cases:
            with self.subTest(case_name=case_name):
                with self.assertRaises(ValidationError):
                    contracts.validate_skills_sdk_check(copy.deepcopy(invalid_payload))

    def test_sdk_check_model_rejects_degraded_contract_contradictions(self) -> None:
        payload = _json(FIXTURE_DIR / "valid" / "sdk-check.json")
        self.assertIsInstance(payload, dict)
        degraded_payload = _sdk_check_with_verdict(payload, "degraded", None, 2)
        cases = (
            (
                "degraded_check_with_known_doctor_status",
                {**degraded_payload, "doctor_status": "warning"},
            ),
            (
                "degraded_check_with_success_exit_code",
                {**degraded_payload, "receipt": {**degraded_payload["receipt"], "exit_code": 0}},
            ),
        )

        for case_name, invalid_payload in cases:
            with self.subTest(case_name=case_name):
                with self.assertRaises(ValidationError):
                    contracts.validate_skills_sdk_check(copy.deepcopy(invalid_payload))

    def test_sdk_check_contract_accepts_degraded_unknown_doctor_status(self) -> None:
        payload = _json(FIXTURE_DIR / "valid" / "sdk-check.json")
        self.assertIsInstance(payload, dict)
        degraded_payload = _sdk_check_with_verdict(payload, "degraded", "unexpected_future_status", 2)
        result = schema_validation.validate_payload_against_schema(
            degraded_payload,
            self.schemas["sdk-check"],
            {**self.schemas, **self.schemas_by_file},
            schema_path=SCHEMA_DIR / SCHEMA_FILES["sdk-check"],
            payload_source="inline:degraded-sdk-check",
            truth_lane="schema_contract",
        )
        self.assertEqual(result.status, "pass", result.diagnostics)
        contracts.validate_skills_sdk_check(degraded_payload)

    def test_invalid_skill_intake_execution_claim_fails_schema_and_model(self) -> None:
        result = self.assert_schema_fails("skill-intake-receipt", "skill-intake-executes.json")
        self.assertTrue(
            any("$.execution_performed" in diagnostic.json_path for diagnostic in result.diagnostics),
            "Expected at least one diagnostic to contain $.execution_performed in json_path"
        )

        with self.assertRaises(ValidationError):
            contracts.validate_skill_intake_receipt(
                _json(FIXTURE_DIR / "invalid" / "skill-intake-executes.json")
            )


if __name__ == "__main__":
    unittest.main()
