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
    "skill-ir": "skill-ir.v0.schema.json",
    "package-manifest": "package-manifest.v0.schema.json",
    "package-digest-receipt": "package-digest-receipt.v0.schema.json",
    "package-hardening-receipt": "package-hardening-receipt.v0.schema.json",
    "signing-policy": "signing-policy.v0.schema.json",
    "signing-intent-receipt": "signing-intent-receipt.v0.schema.json",
    "sandbox-profile": "sandbox-profile.v0.schema.json",
    "sandbox-profile-receipt": "sandbox-profile-receipt.v0.schema.json",
    "eval-case": "eval-case.v0.schema.json",
    "eval-run-receipt": "eval-run-receipt.v0.schema.json",
    "project-conformance-receipt": "project-conformance-receipt.v1.schema.json",
    "placeholder-lifecycle": "placeholder-lifecycle.v1.schema.json",
    "review-plan-receipt": "sdk-review-plan-receipt.v1.schema.json",
    "review-plan-trace": "sdk-review-plan-trace.v1.schema.json",
    "review-handoff-receipt": "sdk-review-handoff-receipt.v1.schema.json",
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
                self.assertRegex(schema["$id"], r"\.v[01]\.schema\.json$")
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

    def test_skill_ir_fixture_records_read_only_package_spine(self) -> None:
        payload = self.assert_valid("skill-ir", "skill-ir.json")

        self.assertEqual(payload["identity"]["id"], "skills-sdk-valid-fixture")
        self.assertEqual(payload["risk"]["tier"], "local")
        self.assertEqual(payload["risk"]["source_kind"], "docs_only")
        self.assertFalse(payload["mutation_performed"])

    def test_package_digest_fixture_records_non_mutating_identity(self) -> None:
        payload = self.assert_valid("package-digest-receipt", "package-digest-receipt.json")

        self.assertEqual(payload["package_id"], "skills-sdk-valid-fixture")
        self.assertTrue(payload["source_digest"].startswith("sha256:"))
        self.assertEqual(payload["manifest"]["skill_ir_schema_version"], "skills-sdk.skill-ir.v0")
        self.assertEqual(payload["included_files"], ["Infrastructure/tests/fixtures/skills_sdk/valid_skill/SKILL.md"])
        self.assertFalse(payload["mutation_performed"])

    def test_package_hardening_fixture_records_non_mutating_checks(self) -> None:
        payload = self.assert_valid("package-hardening-receipt", "package-hardening-receipt.json")

        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["package_id"], "skills-sdk-valid-fixture")
        self.assertEqual(payload["blockers"], [])
        self.assertEqual(payload["hardening_checks"][0]["id"], "non_mutating_package_identity")
        self.assertFalse(payload["mutation_performed"])

    def test_signing_policy_fixture_records_external_key_boundary(self) -> None:
        payload = self.assert_valid("signing-policy", "signing-policy.json")

        self.assertEqual(payload["signer_id"], "skills-sdk-local-fixture-signer")
        self.assertEqual(payload["key_material_policy"], "keyless_required")
        self.assertFalse(payload["archive_required"])

    def test_signing_intent_fixture_records_no_signature_or_artifact(self) -> None:
        payload = self.assert_valid("signing-intent-receipt", "signing-intent-receipt.json")

        self.assertEqual(payload["status"], "ready")
        self.assertFalse(payload["signature_requested"])
        self.assertFalse(payload["signing_performed"])
        self.assertFalse(payload["key_material_accessed"])
        self.assertFalse(payload["artifact_emitted"])
        self.assertFalse(payload["mutation_performed"])

    def test_sandbox_profile_fixture_records_deny_by_default_contract(self) -> None:
        payload = self.assert_valid("sandbox-profile", "sandbox-profile.json")

        self.assertEqual(payload["default_policy"], "deny")
        self.assertEqual(payload["network"]["egress"], "deny")
        self.assertEqual(payload["execution"]["provider"], "none")

    def test_sandbox_profile_receipt_fixture_records_no_execution(self) -> None:
        payload = self.assert_valid("sandbox-profile-receipt", "sandbox-profile-receipt.json")

        self.assertEqual(payload["status"], "pass")
        self.assertFalse(payload["execution_performed"])
        self.assertFalse(payload["adapter_selected"])
        self.assertFalse(payload["mutation_performed"])

    def test_eval_case_fixture_records_deterministic_oracle(self) -> None:
        payload = self.assert_valid("eval-case", "eval-case.json")

        self.assertEqual(payload["oracle"], "exact_match")
        self.assertEqual(payload["expected"], payload["actual"])

    def test_eval_run_fixture_records_non_mutating_deterministic_receipt(self) -> None:
        payload = self.assert_valid("eval-run-receipt", "eval-run-receipt.json")

        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["runner"], "deterministic_jsonl_v0")
        self.assertEqual(payload["passed_count"], payload["case_count"])
        self.assertFalse(payload["mutation_performed"])

    def test_project_conformance_fixture_reports_read_only_project_health(self) -> None:
        payload = self.assert_valid("project-conformance-receipt", "project-conformance-receipt.json")

        self.assertEqual(payload["status"], "pass")
        self.assertFalse(payload["mutation_performed"])
        self.assertEqual(payload["installed_skill_count"], 1)
        self.assertEqual(payload["rollback_ready_count"], 1)

    def test_placeholder_lifecycle_fixture_keeps_unimplemented_surfaces_honest(self) -> None:
        payload = self.assert_valid("placeholder-lifecycle", "placeholder-lifecycle.json")

        self.assertIn(payload["status"], {"not_run", "skipped_optional", "blocked"})
        self.assertFalse(payload["feature_executed"])

    def test_review_plan_fixture_records_source_context_for_handoff(self) -> None:
        payload = self.assert_valid("review-plan-receipt", "review-plan-receipt.json")

        self.assertEqual(payload["source_context"]["branch_policy"], "same_head_required")
        self.assertEqual(payload["source_context"]["target_digest_status"], "available")
        self.assertFalse(payload["mutation_performed"])

    def test_review_plan_trace_fixture_records_sidecar_integrity(self) -> None:
        payload = self.assert_valid("review-plan-trace", "review-plan-trace.json")

        self.assertEqual(payload["schema_version"], "skills-sdk.review-plan-trace.v1")
        self.assertEqual(payload["branch_policy"], "same_head_required")

    def test_review_handoff_fixture_keeps_completion_lanes_not_proven(self) -> None:
        payload = self.assert_valid("review-handoff-receipt", "review-handoff-receipt.json")

        self.assertEqual(payload["source_review_plan"]["schema_version"], "skills-sdk.review-plan-receipt.v1")
        self.assertIn("reviewers_completed", payload["not_proven"])
        self.assertFalse(payload["mutation_performed"])

    def test_receipt_schema_rejects_non_contract_status_names(self) -> None:
        self.assert_invalid("check-receipt", "check-receipt-pass-placeholder.json")

    def test_install_preview_schema_rejects_write_claims(self) -> None:
        self.assert_invalid("install-preview", "install-preview-writes.json")

    def test_skill_ir_schema_rejects_mutation_claims(self) -> None:
        self.assert_invalid("skill-ir", "skill-ir-mutation-claim.json")

    def test_package_digest_schema_rejects_mutation_claims(self) -> None:
        self.assert_invalid("package-digest-receipt", "package-digest-mutation-claim.json")

    def test_package_digest_schema_rejects_empty_included_files(self) -> None:
        self.assert_invalid("package-digest-receipt", "package-digest-empty-included-files.json")

    def test_package_hardening_schema_rejects_mutation_claims(self) -> None:
        self.assert_invalid("package-hardening-receipt", "package-hardening-mutation-claim.json")

    def test_signing_policy_schema_rejects_archive_requirement(self) -> None:
        self.assert_invalid("signing-policy", "signing-policy-requires-archive.json")

    def test_signing_intent_schema_rejects_signature_claims(self) -> None:
        self.assert_invalid("signing-intent-receipt", "signing-intent-claims-signature.json")

    def test_sandbox_profile_receipt_schema_rejects_execution_claims(self) -> None:
        self.assert_invalid("sandbox-profile-receipt", "sandbox-profile-receipt-executes.json")

    def test_eval_run_schema_rejects_mutation_claims(self) -> None:
        self.assert_invalid("eval-run-receipt", "eval-run-mutation-claim.json")

    def test_project_conformance_schema_rejects_mutation_claims(self) -> None:
        """
        Ensures the project-conformance-receipt schema rejects fixtures that claim project mutations.
        
        Validates that the 'project-conformance-writes.json' fixture is invalid against the
        'project-conformance-receipt' schema.
        """
        self.assert_invalid("project-conformance-receipt", "project-conformance-writes.json")

    def test_placeholder_lifecycle_schema_rejects_pass_or_execution_claims(self) -> None:
        """
        Ensure the placeholder-lifecycle schema rejects fixtures that claim execution or passing.
        
        Asserts that the fixture "placeholder-claims-pass.json" does not conform to the placeholder-lifecycle schema and therefore validation fails.
        """
        self.assert_invalid("placeholder-lifecycle", "placeholder-claims-pass.json")


if __name__ == "__main__":
    unittest.main()
