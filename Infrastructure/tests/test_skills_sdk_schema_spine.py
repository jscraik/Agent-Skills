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
    "trust-decision-receipt": "trust-decision-receipt.v0.schema.json",
    "observability-feedback-receipt": "observability-feedback-receipt.v0.schema.json",
    "emitter-preview-receipt": "emitter-preview-receipt.v0.schema.json",
    "ci-policy-preview-receipt": "ci-policy-preview-receipt.v0.schema.json",
    "security-adapter-discovery-receipt": "security-adapter-discovery-receipt.v0.schema.json",
    "static-explorer-receipt": "static-explorer-receipt.v0.schema.json",
    "scenario-quality-receipt": "scenario-quality-receipt.v0.schema.json",
    "signing-policy": "signing-policy.v0.schema.json",
    "signing-intent-receipt": "signing-intent-receipt.v0.schema.json",
    "sandbox-profile": "sandbox-profile.v0.schema.json",
    "sandbox-profile-receipt": "sandbox-profile-receipt.v0.schema.json",
    "skill-intake-receipt": "skill-intake-receipt.v0.schema.json",
    "eval-profile-preview-receipt": "eval-profile-preview-receipt.v0.schema.json",
    "ab-rubric-receipt": "ab-rubric-receipt.v0.schema.json",
    "ab-preview-receipt": "ab-preview-receipt.v0.schema.json",
    "ab-plan-receipt": "ab-plan-receipt.v0.schema.json",
    "ab-run-receipt": "ab-run-receipt.v0.schema.json",
    "ab-judge-preview-receipt": "ab-judge-preview-receipt.v0.schema.json",
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

    def test_schema_subset_validator_applies_minimum_to_float_numbers(self) -> None:
        schema = {"type": "number", "minimum": 1}

        with self.assertRaisesRegex(AssertionError, "smaller than minimum"):
            _validate_schema_subset(schema, 0.5, {})

    def test_schema_subset_validator_uses_json_equality_for_unique_items(self) -> None:
        schema = {"type": "array", "uniqueItems": True}

        with self.assertRaisesRegex(AssertionError, "duplicate items"):
            _validate_schema_subset(schema, [{"a": 1, "b": 2}, {"b": 2, "a": 1}], {})

    def test_schema_subset_validator_applies_max_length_to_strings(self) -> None:
        schema = {"type": "string", "maxLength": 2}

        with self.assertRaisesRegex(AssertionError, "longer than maxLength"):
            _validate_schema_subset(schema, "abc", {})

    def test_schema_subset_validator_applies_contains_cardinality(self) -> None:
        schema = {
            "type": "array",
            "contains": {"type": "object", "properties": {"kind": {"const": "wanted"}}},
            "minContains": 1,
            "maxContains": 1,
        }

        with self.assertRaisesRegex(AssertionError, "more than 1 matching items"):
            _validate_schema_subset(schema, [{"kind": "wanted"}, {"kind": "wanted"}], {})

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
        self.assertIn("codex_sandbox_boundary", payload["sensor_ids"])
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

    def test_trust_decision_fixture_records_local_ledger_preview(self) -> None:
        payload = self.assert_valid("trust-decision-receipt", "trust-decision-receipt.json")

        self.assertEqual(payload["status"], "preview")
        self.assertEqual(payload["decision"], "trust")
        self.assertEqual(payload["package_id"], "skills-sdk-valid-fixture")
        self.assertFalse(payload["mutation_performed"])
        self.assertFalse(payload["trust_store_mutated"])

    def test_observability_feedback_fixture_records_blocked_promotion_candidates(self) -> None:
        payload = self.assert_valid("observability-feedback-receipt", "observability-feedback-receipt.json")

        self.assertEqual(payload["status"], "preview")
        self.assertEqual(payload["event_count"], 1)
        self.assertEqual(payload["scenario_candidates"][0]["promotion_status"], "blocked_pending_package_eval")
        self.assertEqual(payload["skill_gap_candidates"][0]["promotion_status"], "blocked_pending_package_eval")
        self.assertFalse(payload["mutation_performed"])

    def test_emitter_preview_fixture_records_non_mutating_write_plan(self) -> None:
        payload = self.assert_valid("emitter-preview-receipt", "emitter-preview-receipt.json")

        self.assertEqual(payload["status"], "preview")
        self.assertEqual(payload["projection"], "runtime-skill")
        self.assertEqual(payload["target_root"], ".agents/skills")
        self.assertEqual(payload["write_plan"][0]["action"], "write")
        self.assertFalse(payload["mutation_performed"])
        self.assertFalse(payload["artifact_emitted"])
        self.assertFalse(payload["remote_publish_requested"])

    def test_ci_policy_preview_fixture_records_no_hosted_ci_claims(self) -> None:
        payload = self.assert_valid("ci-policy-preview-receipt", "ci-policy-preview-receipt.json")

        self.assertEqual(payload["status"], "preview")
        self.assertEqual(payload["risk_tier"], "high")
        self.assertTrue(any(check["name"] == "risk-policy-gate" for check in payload["required_checks"]))
        self.assertFalse(payload["live_ci_evidence_attached"])
        self.assertFalse(payload["branch_protection_mutated"])
        self.assertFalse(payload["mutation_performed"])

    def test_security_adapter_discovery_fixture_records_no_scanner_execution(self) -> None:
        payload = self.assert_valid(
            "security-adapter-discovery-receipt",
            "security-adapter-discovery-receipt.json",
        )

        self.assertEqual(payload["status"], "preview")
        self.assertEqual(payload["adapter_count"], 2)
        self.assertFalse(payload["scanner_execution_performed"])
        self.assertFalse(payload["network_accessed"])
        self.assertFalse(payload["credentials_accessed"])
        self.assertFalse(payload["mutation_performed"])

    def test_security_adapter_discovery_schema_rejects_execution_claims(self) -> None:
        self.assert_invalid(
            "security-adapter-discovery-receipt",
            "security-adapter-discovery-executes.json",
        )

    def test_static_explorer_fixture_records_json_only_projection(self) -> None:
        payload = self.assert_valid("static-explorer-receipt", "static-explorer-receipt.json")

        self.assertEqual(payload["status"], "preview")
        self.assertEqual(payload["capability_count"], 1)
        self.assertEqual(payload["skill_count"], 1)
        self.assertFalse(payload["html_rendered"])
        self.assertFalse(payload["hosted_publish_requested"])
        self.assertFalse(payload["mutation_performed"])

    def test_scenario_quality_fixture_records_non_mutating_gate(self) -> None:
        payload = self.assert_valid("scenario-quality-receipt", "scenario-quality-receipt.json")

        self.assertEqual(payload["status"], "preview")
        self.assertEqual(payload["scenario_count"], 1)
        self.assertEqual(payload["promotion_ready_count"], 1)
        self.assertFalse(payload["mutation_performed"])
        self.assertFalse(payload["promotion_performed"])

    def test_scenario_quality_schema_rejects_empty_check_evidence(self) -> None:
        payload = _json(FIXTURE_DIR / "valid" / "scenario-quality-receipt.json")
        payload["scenario_rows"][0]["checks"][0]["evidence"] = [""]

        with self.assertRaises(AssertionError):
            _validate_schema_subset(
                self.schemas["scenario-quality-receipt"],
                payload,
                {**self.schemas, **self.schemas_by_file},
            )

    def test_eval_profile_preview_fixture_records_codex_and_ollama_boundaries(self) -> None:
        payload = self.assert_valid("eval-profile-preview-receipt", "eval-profile-preview-receipt.json")

        self.assertEqual(payload["status"], "preview")
        self.assertEqual(payload["execution_boundary"], "codex_exec_sandbox")
        self.assertEqual(payload["external_intake_boundary"], "sdk_quarantine_only")
        self.assertFalse(payload["secret_boundary"]["skill_execution_receives_judge_secrets"])
        judge_by_id = {profile["id"]: profile for profile in payload["judge_profiles"]}
        self.assertEqual(judge_by_id["oss-local"]["model"], "qwen3.5:latest")
        self.assertEqual(judge_by_id["oss-cloud"]["model"], "deepseek-v4-flash:cloud")
        self.assertEqual(judge_by_id["oss-cloud"]["secret_env_names"], ["OLLAMA_API_KEY"])
        self.assertEqual(judge_by_id["oss-cloud"]["auth_boundary"], "env_secret")
        self.assertTrue(judge_by_id["codex-fast"]["network_required"])
        self.assertEqual(judge_by_id["codex-fast"]["auth_boundary"], "codex_cli_auth")
        self.assertFalse(payload["provider_invoked"])
        self.assertFalse(payload["mutation_performed"])

    def test_ab_rubric_fixture_records_stable_cross_stage_scorecard(self) -> None:
        payload = self.assert_valid("ab-rubric-receipt", "ab-rubric-receipt.json")

        rubric = payload["rubric"]
        self.assertEqual(rubric["rubric_id"], "skills-sdk.ab-rubric.v0")
        self.assertTrue(rubric["stable_across_stages"])
        self.assertAlmostEqual(sum(dimension["weight"] for dimension in rubric["dimensions"]), 1.0)
        self.assertEqual(
            {stage["stage"] for stage in rubric["stage_policies"]},
            {"local_oss_loop", "cloud_oss_loop", "external_validation"},
        )
        self.assertTrue(rubric["judge_output_contract"]["unvalidated_judges_are_advisory"])

    def test_ab_preview_fixture_records_non_executing_codex_experiment_contract(self) -> None:
        payload = self.assert_valid("ab-preview-receipt", "ab-preview-receipt.json")

        self.assertEqual(payload["status"], "preview")
        self.assertEqual(payload["execution_boundary"], "codex_exec_sandbox")
        self.assertEqual(payload["judge_boundary"], "post_run_sanitized_evidence_only")
        self.assertEqual(payload["execution_profile"]["id"], "codex-read-only")
        self.assertEqual(payload["judge_profile"]["id"], "oss-local")
        self.assertEqual(payload["judge_profile"]["model"], "qwen3.5:latest")
        self.assertEqual(payload["secret_boundary"]["skill_execution_env_secret_names"], [])
        self.assertEqual(payload["secret_boundary"]["judge_env_secret_names"], [])
        self.assertFalse(payload["secret_boundary"]["skill_execution_receives_judge_secrets"])
        self.assertFalse(payload["codex_exec_invoked"])
        self.assertFalse(payload["provider_invoked"])
        self.assertFalse(payload["mutation_performed"])

    def test_ab_preview_schema_rejects_preview_with_blockers(self) -> None:
        payload = _json(FIXTURE_DIR / "valid" / "ab-preview-receipt.json")
        payload["blockers"] = ["unexpected_blocker"]

        with self.assertRaises(AssertionError):
            _validate_schema_subset(
                self.schemas["ab-preview-receipt"],
                payload,
                {**self.schemas, **self.schemas_by_file},
            )

    def test_ab_plan_fixture_records_non_executing_codex_command_plan(self) -> None:
        payload = self.assert_valid("ab-plan-receipt", "ab-plan-receipt.json")

        self.assertEqual(payload["status"], "planned")
        self.assertEqual(payload["operation"], "ab_plan")
        self.assertEqual(payload["execution_profile"]["id"], "codex-read-only")
        self.assertEqual(payload["command_variant_labels"], ["A", "B"])
        self.assertEqual(payload["command_plan"][0]["command_argv"][:4], ["codex", "exec", "--sandbox", "read-only"])
        self.assertEqual(payload["command_plan"][0]["approval_policy"], "on-request")
        self.assertIn("--ask-for-approval", payload["command_plan"][0]["command_argv"])
        self.assertEqual(payload["command_plan"][0]["runner_stdout_capture_path"], payload["command_plan"][0]["event_log_path"])
        self.assertNotIn(payload["command_plan"][0]["event_log_path"], payload["command_plan"][0]["planned_write_paths"])
        self.assertEqual({plan["variant_label"] for plan in payload["command_plan"]}, {"A", "B"})
        self.assertFalse(payload["codex_exec_invoked"])
        self.assertFalse(payload["provider_invoked"])
        self.assertFalse(payload["network_accessed"])
        self.assertFalse(payload["mutation_performed"])

    def test_ab_plan_schema_rejects_duplicate_command_variant_labels(self) -> None:
        payload = _json(FIXTURE_DIR / "valid" / "ab-plan-receipt.json")
        payload["command_variant_labels"] = ["A", "A"]

        with self.assertRaises(AssertionError):
            _validate_schema_subset(
                self.schemas["ab-plan-receipt"],
                payload,
                {**self.schemas, **self.schemas_by_file},
            )

    def test_ab_plan_schema_rejects_duplicate_command_plan_variants(self) -> None:
        payload = _json(FIXTURE_DIR / "valid" / "ab-plan-receipt.json")
        payload["command_plan"][1]["variant_label"] = "A"

        with self.assertRaises(AssertionError):
            _validate_schema_subset(
                self.schemas["ab-plan-receipt"],
                payload,
                {**self.schemas, **self.schemas_by_file},
            )

    def test_ab_plan_schema_allows_preflight_blocked_empty_command_plan(self) -> None:
        payload = _json(FIXTURE_DIR / "valid" / "ab-plan-receipt.json")
        payload["status"] = "blocked"
        payload["command_variant_labels"] = []
        payload["command_plan"] = []
        payload["blockers"] = ["fixture_missing"]

        _validate_schema_subset(
            self.schemas["ab-plan-receipt"],
            payload,
            {**self.schemas, **self.schemas_by_file},
        )

    def test_ab_run_fixture_records_codex_execution_without_judge_invocation(self) -> None:
        payload = self.assert_valid("ab-run-receipt", "ab-run-receipt.json")

        self.assertEqual(payload["status"], "completed")
        self.assertEqual(payload["operation"], "ab_run")
        self.assertEqual(payload["command_variant_labels"], ["A", "B"])
        self.assertEqual({result["variant_label"] for result in payload["variant_results"]}, {"A", "B"})
        self.assertTrue(payload["codex_exec_invoked"])
        self.assertTrue(payload["provider_invoked"])
        self.assertTrue(payload["network_accessed"])
        self.assertTrue(payload["mutation_performed"])
        self.assertFalse(payload["judge_provider_invoked"])

    def test_ab_run_schema_rejects_duplicate_result_variants(self) -> None:
        payload = _json(FIXTURE_DIR / "valid" / "ab-run-receipt.json")
        payload["variant_results"][1]["variant_label"] = "A"

        with self.assertRaises(AssertionError):
            _validate_schema_subset(
                self.schemas["ab-run-receipt"],
                payload,
                {**self.schemas, **self.schemas_by_file},
            )

    def test_ab_run_schema_allows_preflight_blocked_empty_command_plan(self) -> None:
        payload = _json(FIXTURE_DIR / "valid" / "ab-run-receipt.json")
        payload["status"] = "blocked"
        payload["command_variant_labels"] = []
        payload["command_plan"] = []
        payload["variant_results"] = []
        payload["mutation_performed"] = False
        payload["network_accessed"] = False
        payload["provider_invoked"] = False
        payload["codex_exec_invoked"] = False
        payload["blockers"] = ["fixture_missing"]

        _validate_schema_subset(
            self.schemas["ab-run-receipt"],
            payload,
            {**self.schemas, **self.schemas_by_file},
        )

    def test_ab_judge_preview_fixture_records_sanitized_non_invoking_judge_input(self) -> None:
        payload = self.assert_valid("ab-judge-preview-receipt", "ab-judge-preview-receipt.json")

        self.assertEqual(payload["status"], "preview")
        self.assertEqual(payload["operation"], "ab_judge_preview")
        self.assertEqual(payload["judge_profile"]["model"], "qwen3.5:latest")
        self.assertEqual(payload["allowed_winners"], ["skill_a", "skill_b", "inconclusive"])
        self.assertTrue(payload["calibration_required"])
        self.assertFalse(payload["provider_invoked"])
        self.assertFalse(payload["network_accessed"])
        self.assertFalse(payload["mutation_performed"])
        self.assertNotIn("command_argv", payload["comparison_payload"]["variant_results"][0])

    def test_ab_judge_preview_schema_rejects_duplicate_result_variants(self) -> None:
        payload = _json(FIXTURE_DIR / "valid" / "ab-judge-preview-receipt.json")
        payload["comparison_payload"]["variant_results"][1]["variant_label"] = "A"

        with self.assertRaises(AssertionError):
            _validate_schema_subset(
                self.schemas["ab-judge-preview-receipt"],
                payload,
                {**self.schemas, **self.schemas_by_file},
            )

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

    def test_skill_intake_receipt_fixture_records_quarantine_boundary(self) -> None:
        payload = self.assert_valid("skill-intake-receipt", "skill-intake-receipt.json")

        self.assertEqual(payload["status"], "preview")
        self.assertEqual(payload["source_kind"], "directory")
        self.assertEqual(payload["skill_id"], "skills-sdk-valid-fixture")
        self.assertFalse(payload["execution_performed"])
        self.assertFalse(payload["install_performed"])
        self.assertFalse(payload["projection_mutation_performed"])
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

    def test_eval_run_v0_schema_accepts_legacy_receipt_without_package_identity(self) -> None:
        payload = _json(FIXTURE_DIR / "valid" / "eval-run-receipt.json")
        payload.pop("package_id")
        payload.pop("package_digest")

        _validate_schema_subset(
            self.schemas["eval-run-receipt"],
            payload,
            {**self.schemas, **self.schemas_by_file},
        )

    def test_eval_run_v0_schema_accepts_internal_quality_gates(self) -> None:
        payload = _json(FIXTURE_DIR / "valid" / "eval-run-receipt.json")
        payload["runner"] = "internal_skill_builder_v0"
        payload["quality_gates"] = {
            "source": "internal_scorecard",
            "scorecard_schema_version": "2.1",
            "decision": "pass",
            "passed": True,
            "promotion_eligible": None,
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

        _validate_schema_subset(
            self.schemas["eval-run-receipt"],
            payload,
            {**self.schemas, **self.schemas_by_file},
        )

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

    def test_trust_decision_schema_rejects_preview_write_claims(self) -> None:
        self.assert_invalid("trust-decision-receipt", "trust-decision-preview-writes.json")

    def test_trust_decision_schema_rejects_recorded_without_ledger_evidence(self) -> None:
        self.assert_invalid("trust-decision-receipt", "trust-decision-recorded-without-ledger-evidence.json")

    def test_observability_feedback_schema_rejects_mutation_claims(self) -> None:
        self.assert_invalid("observability-feedback-receipt", "observability-feedback-mutates.json")

    def test_observability_feedback_schema_rejects_duplicate_required_receipts(self) -> None:
        self.assert_invalid("observability-feedback-receipt", "observability-feedback-duplicate-required-receipts.json")

    def test_signing_policy_schema_rejects_archive_requirement(self) -> None:
        self.assert_invalid("signing-policy", "signing-policy-requires-archive.json")

    def test_signing_intent_schema_rejects_signature_claims(self) -> None:
        self.assert_invalid("signing-intent-receipt", "signing-intent-claims-signature.json")

    def test_sandbox_profile_receipt_schema_rejects_execution_claims(self) -> None:
        self.assert_invalid("sandbox-profile-receipt", "sandbox-profile-receipt-executes.json")

    def test_skill_intake_schema_rejects_execution_claims(self) -> None:
        self.assert_invalid("skill-intake-receipt", "skill-intake-executes.json")

    def test_sandbox_profile_receipt_schema_rejects_short_digest(self) -> None:
        payload = _json(FIXTURE_DIR / "valid" / "sandbox-profile-receipt.json")
        payload["profile_digest"] = "x"

        with self.assertRaises(AssertionError):
            _validate_schema_subset(
                self.schemas["sandbox-profile-receipt"],
                payload,
                {**self.schemas, **self.schemas_by_file},
            )

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
