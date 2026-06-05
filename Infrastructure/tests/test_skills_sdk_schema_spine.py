import json
import unittest
from pathlib import Path

from helpers.schema_validator import _validate_schema_subset


REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_DIR = REPO_ROOT / "Infrastructure/config/schemas/skills-sdk"
FIXTURE_DIR = REPO_ROOT / "Infrastructure/tests/fixtures/skills_sdk/schema_spine"

SCHEMA_NAMES = {
    "manifest-source": "manifest-source.v1.schema.json",
    "check-receipt": "check-receipt.v1.schema.json",
    "risk-classification": "risk-classification.v1.schema.json",
    "install-preview": "install-preview.v1.schema.json",
    "install-receipt": "install-receipt.v1.schema.json",
    "lockfile-preview": "lockfile-preview.v1.schema.json",
    "lockfile": "lockfile.v1.schema.json",
    "placeholder-lifecycle": "placeholder-lifecycle.v1.schema.json",
}


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class TestSkillsSdkSchemaSpine(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schemas = {
            name: _json(SCHEMA_DIR / schema_name)
            for name, schema_name in SCHEMA_NAMES.items()
        }
        cls.schemas_by_file = {
            schema_name: _json(SCHEMA_DIR / schema_name)
            for schema_name in SCHEMA_NAMES.values()
        }

    def assert_valid(self, schema_key: str, fixture_name: str) -> dict:
        payload = _json(FIXTURE_DIR / "valid" / fixture_name)
        _validate_schema_subset(
            self.schemas[schema_key],
            payload,
            {**self.schemas, **self.schemas_by_file},
        )
        return payload

    def assert_invalid(self, schema_key: str, fixture_name: str) -> None:
        payload = _json(FIXTURE_DIR / "invalid" / fixture_name)
        with self.assertRaises(AssertionError):
            _validate_schema_subset(
                self.schemas[schema_key],
                payload,
                {**self.schemas, **self.schemas_by_file},
            )

    def test_schema_files_have_versioned_ids_and_disallow_extra_fields(self) -> None:
        for schema_key, schema in self.schemas.items():
            with self.subTest(schema=schema_key):
                self.assertIn("/skills-sdk/", schema["$id"])
                self.assertTrue(schema["$id"].endswith(".v1.schema.json"))
                self.assertFalse(schema["additionalProperties"])

    def test_manifest_source_fixture_covers_source_shape_contract(self) -> None:
        payload = self.assert_valid("manifest-source", "manifest-source.json")

        self.assertEqual(payload["source_kind"], "minimal_skill")
        self.assertTrue(payload["canonical_source"])
        self.assertFalse(payload["runtime_projection"])
        self.assertIn("SA-003", payload["acceptance_trace"])

    def test_check_receipt_fixture_encodes_status_failure_and_proof_metadata(self) -> None:
        payload = self.assert_valid("check-receipt", "check-receipt.json")

        self.assertEqual(payload["status"], "blocked")
        self.assertEqual(payload["failure_class"], "placeholder_not_available")
        self.assertEqual(payload["work_mode"], "computational")
        self.assertEqual(payload["actor"]["role"], "agent")
        self.assertIn("VP-011", payload["acceptance_trace"])

    def test_risk_classification_fixture_encodes_dimensions_and_sensor_ids(self) -> None:
        payload = self.assert_valid("risk-classification", "risk-classification.json")

        self.assertEqual(payload["risk_tier"], "high")
        self.assertEqual(payload["blocking_behavior"], "block")
        self.assertTrue(payload["receipt_required"])
        self.assertIn("static_script_scan", payload["sensor_ids"])
        self.assertIn("sandbox_placeholder", payload["sensor_ids"])
        self.assertEqual(payload["sensors"][0]["placement"], "source")

    def test_install_preview_fixture_embeds_read_only_lockfile_delta(self) -> None:
        payload = self.assert_valid("install-preview", "install-preview.json")

        self.assertFalse(payload["mutation_performed"])
        self.assertFalse(payload["lockfile_delta_preview"]["would_write"])
        self.assertEqual(payload["lockfile_delta_preview"]["lockfile_path"], "skills.lock.json")

    def test_install_receipt_fixture_embeds_real_project_mutation(self) -> None:
        payload = self.assert_valid("install-receipt", "install-receipt.json")

        self.assertTrue(payload["mutation_performed"])
        self.assertEqual(payload["scope"], "project")
        self.assertEqual(payload["status"], "success")
        self.assertIn(".agents/skills/sample/SKILL.md", payload["target_paths"])

    def test_lockfile_fixture_records_project_install_entry(self) -> None:
        payload = self.assert_valid("lockfile", "lockfile.json")

        self.assertIn("sample", payload["entries"])
        self.assertEqual(payload["entries"]["sample"]["target_path"], ".agents/skills/sample")

    def test_placeholder_lifecycle_fixture_keeps_unimplemented_surfaces_honest(self) -> None:
        payload = self.assert_valid("placeholder-lifecycle", "placeholder-lifecycle.json")

        self.assertIn(payload["status"], {"not_run", "skipped_optional", "blocked"})
        self.assertFalse(payload["feature_executed"])

    def test_receipt_schema_rejects_non_contract_status_names(self) -> None:
        self.assert_invalid("check-receipt", "check-receipt-pass-placeholder.json")

    def test_install_preview_schema_rejects_write_claims(self) -> None:
        self.assert_invalid("install-preview", "install-preview-writes.json")

    def test_placeholder_lifecycle_schema_rejects_pass_or_execution_claims(self) -> None:
        self.assert_invalid("placeholder-lifecycle", "placeholder-claims-pass.json")


if __name__ == "__main__":
    unittest.main()
