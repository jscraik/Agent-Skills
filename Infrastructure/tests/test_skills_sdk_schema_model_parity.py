from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

from pydantic import ValidationError


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk import schema_validation  # noqa: E402
from ask.skills_sdk import typed_contracts as contracts  # noqa: E402


SCHEMA_DIR = REPO_ROOT / "Infrastructure/config/schemas/skills-sdk"
FIXTURE_DIR = REPO_ROOT / "Infrastructure/tests/fixtures/skills_sdk/schema_spine"
SCHEMA_FILES = {
    "manifest-source": "manifest-source.v1.schema.json",
    "check-receipt": "check-receipt.v1.schema.json",
    "risk-classification": "risk-classification.v1.schema.json",
    "install-preview": "install-preview.v1.schema.json",
    "install-receipt": "install-receipt.v1.schema.json",
    "lockfile-preview": "lockfile-preview.v1.schema.json",
    "lockfile": "lockfile.v1.schema.json",
}


def _json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


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
            ("risk-classification", "risk-classification.json", contracts.validate_risk_classification),
            ("install-preview", "install-preview.json", contracts.validate_install_preview),
            ("install-receipt", "install-receipt.json", contracts.validate_install_receipt),
            ("lockfile", "lockfile.json", contracts.validate_lockfile),
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


if __name__ == "__main__":
    unittest.main()
