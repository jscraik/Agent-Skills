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
            ("eval-case.json", contracts.validate_eval_case),
            ("eval-run-receipt.json", contracts.validate_eval_run_receipt),
            ("check-receipt.json", contracts.validate_check_receipt),
            ("risk-classification.json", contracts.validate_risk_classification),
            ("install-preview.json", contracts.validate_install_preview),
            ("install-receipt.json", contracts.validate_install_receipt),
            ("lockfile.json", contracts.validate_lockfile),
            ("project-conformance-receipt.json", contracts.validate_project_conformance_receipt),
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

    def test_eval_run_contract_rejects_mutation_claims(self) -> None:
        payload = _json(FIXTURE_DIR / "valid" / "eval-run-receipt.json")
        self.assertIsInstance(payload, dict)
        payload["mutation_performed"] = True

        with self.assertRaises(ValidationError):
            contracts.validate_eval_run_receipt(payload)

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
