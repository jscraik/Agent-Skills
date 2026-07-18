import json
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "tests"))

from helpers.schema_validator import _validate_schema_subset  # noqa: E402

SCHEMA_DIR = REPO_ROOT / "Infrastructure/config/schemas/skills-sdk"
FIXTURE_DIR = REPO_ROOT / "Infrastructure/tests/fixtures/skills_sdk/schema_spine"

SCHEMA_NAMES = {
    "manifest-source": "manifest-source.v1.schema.json",
    "check-receipt": "check-receipt.v1.schema.json",
    "capability-evidence-receipt": "capability-evidence-receipt.v0.schema.json",
    "risk-classification": "risk-classification.v1.schema.json",
    "risk-mode-taxonomy-receipt": "risk-mode-taxonomy-receipt.v0.schema.json",
    "skill-intake-review-receipt": "skill-intake-review-receipt.v0.schema.json",
    "install-preview": "install-preview.v1.schema.json",
    "install-receipt": "install-receipt.v1.schema.json",
    "lockfile-preview": "lockfile-preview.v1.schema.json",
    "lockfile": "lockfile.v1.schema.json",
    "skill-ir": "skill-ir.v0.schema.json",
    "package-manifest": "package-manifest.v0.schema.json",
    "package-digest-receipt": "package-digest-receipt.v0.schema.json",
    "package-hardening-receipt": "package-hardening-receipt.v0.schema.json",
    "package-security-signature-receipt": "package-security-signature-receipt.v0.schema.json",
    "security-lane-receipt": "security-lane-receipt.v0.schema.json",
    "trust-decision-receipt": "trust-decision-receipt.v0.schema.json",
    "observability-feedback-receipt": "observability-feedback-receipt.v0.schema.json",
    "observability-promotion-receipt": "observability-promotion-receipt.v0.schema.json",
    "emitter-preview-receipt": "emitter-preview-receipt.v0.schema.json",
    "ci-policy-preview-receipt": "ci-policy-preview-receipt.v0.schema.json",
    "security-adapter-discovery-receipt": "security-adapter-discovery-receipt.v0.schema.json",
    "static-explorer-receipt": "static-explorer-receipt.v0.schema.json",
    "scenario-quality-receipt": "scenario-quality-receipt.v0.schema.json",
    "scenario-registry-entry": "scenario-registry-entry.v0.schema.json",
    "scenario-adaptation-receipt": "scenario-adaptation-receipt.v0.schema.json",
    "scorer-quality-receipt": "scorer-quality-receipt.v0.schema.json",
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
    "ab-plan-receipt-v1": "ab-plan-receipt.v1.schema.json",
    "ab-run-receipt-v1": "ab-run-receipt.v1.schema.json",
    "ab-judge-preview-receipt": "ab-judge-preview-receipt.v0.schema.json",
    "ab-judge-score-receipt": "ab-judge-score-receipt.v0.schema.json",
    "eval-case": "eval-case.v0.schema.json",
    "eval-run-receipt": "eval-run-receipt.v0.schema.json",
    "phoenix-eval-trace-receipt": "phoenix-eval-trace-receipt.v1.schema.json",
    "project-conformance-receipt": "project-conformance-receipt.v1.schema.json",
    "placeholder-lifecycle": "placeholder-lifecycle.v1.schema.json",
    "review-plan-receipt": "sdk-review-plan-receipt.v1.schema.json",
    "review-plan-trace": "sdk-review-plan-trace.v1.schema.json",
    "review-handoff-receipt": "sdk-review-handoff-receipt.v1.schema.json",
    "pipeline-start": "pipeline-start.v1.schema.json",
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

    def test_phoenix_eval_trace_receipt_fixture_is_valid(self) -> None:
        payload = self.assert_valid("phoenix-eval-trace-receipt", "phoenix-eval-trace-receipt.json")

        self.assertEqual(payload["observability_status"], "not_run")
        self.assertEqual(payload["eval_status"], "pass")
        self.assertEqual(payload["project_name"], "agent-skills-skills-sdk-evals")

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

    def test_capability_evidence_fixture_preserves_lane_boundaries(self) -> None:
        payload = self.assert_valid("capability-evidence-receipt", "capability-evidence-receipt.json")

        self.assertEqual(payload["status"], "pass")
        self.assertFalse(payload["mutation_performed"])
        self.assertFalse(payload["command_execution_performed"])
        statuses_by_kind = {row["kind"]: row["status"] for row in payload["evidence_rows"]}
        self.assertEqual(statuses_by_kind["schema"], "pass")
        self.assertEqual(statuses_by_kind["command"], "not_run")
        self.assertEqual(statuses_by_kind["external_lane"], "not_run")

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

    def test_package_security_signature_fixture_records_non_executing_scan_boundary(self) -> None:
        payload = self.assert_valid("package-security-signature-receipt", "package-security-signature-receipt.json")

        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["package_id"], "skills-sdk-valid-fixture")
        self.assertTrue(payload["redaction_performed"])
        self.assertFalse(payload["redacted_content_emitted"])
        self.assertFalse(payload["binary_content_embedded"])
        self.assertFalse(payload["execution_performed"])
        self.assertFalse(payload["scanner_execution_performed"])
        self.assertFalse(payload["network_accessed"])
        self.assertFalse(payload["credentials_accessed"])
        self.assertFalse(payload["mutation_performed"])

    def test_package_security_signature_schema_rejects_execution_claims(self) -> None:
        self.assert_invalid("package-security-signature-receipt", "package-security-signature-executes.json")

    def test_security_lane_fixture_records_deterministic_security_commands(self) -> None:
        payload = self.assert_valid("security-lane-receipt", "security-lane-receipt.json")

        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["package_id"], "skills-sdk-valid-fixture")
        command_text = "\n".join(row["command"] for row in payload["commands"])
        self.assertIn("package-signature", command_text)
        self.assertIn("risk-modes", command_text)
        self.assertFalse(payload["execution_performed"])
        self.assertFalse(payload["scanner_execution_performed"])
        self.assertFalse(payload["network_accessed"])
        self.assertFalse(payload["credentials_accessed"])
        self.assertFalse(payload["mutation_performed"])

    def test_security_lane_schema_rejects_execution_claims(self) -> None:
        self.assert_invalid("security-lane-receipt", "security-lane-executes.json")

    def test_scenario_registry_entry_fixture_records_governed_seed(self) -> None:
        payload = self.assert_valid("scenario-registry-entry", "scenario-registry-entry.json")

        self.assertEqual(payload["promotion_status"], "candidate")
        self.assertIn("technical-writing", payload["domain_tags"])
        self.assertIn("expected_signal", payload["acceptance_schema"])

    def test_scenario_registry_entry_requires_demotion_reason_only_for_demoted_states(self) -> None:
        schema = self.schemas["scenario-registry-entry"]
        payload = self.assert_valid("scenario-registry-entry", "scenario-registry-entry.json")
        payload["promotion_status"] = "deprecated"

        with self.assertRaisesRegex(AssertionError, "demotion_reason"):
            _validate_schema_subset(schema, payload, {**self.schemas, **self.schemas_by_file})

        payload["demotion_reason"] = "Superseded by stronger release-lane coverage."
        _validate_schema_subset(schema, payload, {**self.schemas, **self.schemas_by_file})

    def test_scenario_adaptation_receipt_fixture_records_sdk_authorized_localization(self) -> None:
        payload = self.assert_valid("scenario-adaptation-receipt", "scenario-adaptation-receipt.json")

        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["authorized_stage"], "scenario_generation")
        self.assertTrue(payload["criteria_ownership"]["local_criteria_authoritative"])
        self.assertEqual(payload["target_case_id"], "proof-boundary")

    def test_scenario_adaptation_receipt_links_status_and_blockers(self) -> None:
        schema = self.schemas["scenario-adaptation-receipt"]
        payload = self.assert_valid("scenario-adaptation-receipt", "scenario-adaptation-receipt.json")
        payload["status"] = "blocked"

        with self.assertRaisesRegex(AssertionError, "minItems"):
            _validate_schema_subset(schema, payload, {**self.schemas, **self.schemas_by_file})

        payload["blockers"] = ["missing local adaptation receipt"]
        _validate_schema_subset(schema, payload, {**self.schemas, **self.schemas_by_file})

        payload["status"] = "pass"
        with self.assertRaisesRegex(AssertionError, "maxItems"):
            _validate_schema_subset(schema, payload, {**self.schemas, **self.schemas_by_file})

    def test_scenario_adaptation_receipt_pass_status_requires_pass_validation_rows(self) -> None:
        schema = self.schemas["scenario-adaptation-receipt"]
        payload = self.assert_valid("scenario-adaptation-receipt", "scenario-adaptation-receipt.json")
        payload["validation"][0]["status"] = "fail"

        with self.assertRaisesRegex(AssertionError, "expected const 'pass'"):
            _validate_schema_subset(schema, payload, {**self.schemas, **self.schemas_by_file})

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

    def test_observability_promotion_fixture_records_receipt_backed_candidate_decisions(self) -> None:
        payload = self.assert_valid("observability-promotion-receipt", "observability-promotion-receipt.json")

        self.assertEqual(payload["status"], "preview")
        self.assertEqual(payload["operation"], "observability_promotion_preview")
        self.assertEqual(payload["candidate_count"], 1)
        self.assertEqual(payload["promotion_ready_count"], 1)
        self.assertEqual(payload["candidate_decisions"][0]["decision"], "promotion_ready")
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

    def test_scorer_quality_fixture_records_non_mutating_gate(self) -> None:
        payload = self.assert_valid("scorer-quality-receipt", "scorer-quality-receipt.json")

        self.assertEqual(payload["status"], "preview")
        self.assertTrue(payload["ready"])
        self.assertFalse(payload["mutation_performed"])
        self.assertFalse(payload["promotion_performed"])

    def test_scorer_quality_schema_rejects_empty_check_evidence(self) -> None:
        payload = _json(FIXTURE_DIR / "valid" / "scorer-quality-receipt.json")
        payload["quality_checks"][0]["evidence"] = [""]

        with self.assertRaises(AssertionError):
            _validate_schema_subset(
                self.schemas["scorer-quality-receipt"],
                payload,
                {**self.schemas, **self.schemas_by_file},
            )

    def test_eval_profile_preview_fixture_records_codex_profile_boundaries(self) -> None:
        payload = self.assert_valid("eval-profile-preview-receipt", "eval-profile-preview-receipt.json")

        self.assertEqual(payload["status"], "preview")
        self.assertEqual(payload["execution_boundary"], "codex_exec_sandbox")
        self.assertEqual(payload["external_intake_boundary"], "sdk_quarantine_only")
        self.assertFalse(payload["secret_boundary"]["skill_execution_receives_judge_secrets"])
        judge_by_id = {profile["id"]: profile for profile in payload["judge_profiles"]}
        self.assertEqual(judge_by_id["oss-local"]["provider"], "codex")
        self.assertEqual(judge_by_id["oss-local"]["codex_profile"], "oss-local")
        self.assertEqual(judge_by_id["oss-local"]["model"], "qwen3.5:9b-mlx")
        self.assertEqual(judge_by_id["oss-local"]["model_role"], "local_sandbox_eval_default")
        self.assertEqual(
            judge_by_id["oss-local"]["model_settings"],
            {"num_ctx": 8192, "num_predict": 1024, "temperature": 0.1, "top_p": 0.9},
        )
        self.assertEqual(judge_by_id["oss-local"]["runtime_metadata"]["model_id"], "203e30078279")
        self.assertEqual(judge_by_id["oss-local"]["runtime_metadata"]["metadata_source"], "ollama_show")
        self.assertTrue(judge_by_id["oss-local"]["smoke_guard"]["forbid_fallback_metadata"])
        self.assertTrue(judge_by_id["oss-local"]["smoke_guard"]["forbid_visible_thinking"])
        self.assertTrue(judge_by_id["oss-local"]["smoke_guard"]["allow_codex_jsonl_reasoning_events"])
        self.assertEqual(judge_by_id["oss-local"]["host"], "codex-cli-profile")
        self.assertEqual(judge_by_id["oss-local-large-transcript"]["model"], "qwen3.5:9b-mlx")
        self.assertEqual(judge_by_id["oss-local-large-transcript"]["model_settings"]["num_ctx"], 16384)
        self.assertEqual(judge_by_id["oss-local-large-transcript"]["model_settings"]["num_predict"], 1536)
        self.assertEqual(judge_by_id["oss-local-code"]["codex_profile"], "oss-local-code")
        self.assertEqual(judge_by_id["oss-local-code"]["model"], "qwen3-coder:30b")
        self.assertEqual(judge_by_id["oss-local-fallback"]["codex_profile"], "oss-local-fallback")
        self.assertEqual(judge_by_id["oss-local-fallback"]["model"], "qwen3.5:latest")
        self.assertEqual(judge_by_id["oss-security"]["codex_profile"], "oss-security")
        self.assertEqual(judge_by_id["oss-security"]["model"], "CyberCrew/notmythos-8b")
        self.assertEqual(judge_by_id["oss-security"]["model_role"], "local_security_specialist")
        self.assertEqual(judge_by_id["oss-security"]["model_settings"]["num_predict"], 1024)
        self.assertEqual(judge_by_id["oss-security"]["model_settings"]["repeat_penalty"], 1.15)
        self.assertEqual(judge_by_id["oss-security"]["model_settings"]["top_k"], 40)
        self.assertEqual(judge_by_id["oss-cloud"]["provider"], "codex")
        self.assertEqual(judge_by_id["oss-cloud"]["model"], "minimax-m2.7:cloud")
        self.assertEqual(judge_by_id["oss-cloud"]["host"], "codex-cli-profile")
        self.assertEqual(judge_by_id["oss-cloud"]["secret_env_names"], ["OLLAMA_API_KEY"])
        self.assertEqual(judge_by_id["oss-cloud"]["auth_boundary"], "codex_cli_auth")
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
        self.assertEqual(payload["judge_profile"]["model"], "qwen3.5:9b-mlx")
        self.assertEqual(payload["judge_profile"]["model_settings"]["num_ctx"], 8192)
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
        self.assertEqual(
            payload["command_plan"][0]["command_argv"][:8],
            ["codex", "exec", "--sandbox", "read-only", "--ask-for-approval", "on-request", "--cd", "."],
        )
        self.assertEqual(payload["command_plan"][0]["approval_policy"], "on-request")
        self.assertIn("--ask-for-approval", payload["command_plan"][0]["command_argv"])
        self.assertEqual(payload["command_plan"][0]["runner_stdout_capture_path"], payload["command_plan"][0]["event_log_path"])
        self.assertNotIn(payload["command_plan"][0]["event_log_path"], payload["command_plan"][0]["planned_write_paths"])
        self.assertEqual({plan["variant_label"] for plan in payload["command_plan"]}, {"A", "B"})
        self.assertFalse(payload["codex_exec_invoked"])
        self.assertFalse(payload["provider_invoked"])
        self.assertFalse(payload["network_accessed"])
        self.assertFalse(payload["mutation_performed"])

    def test_ab_v1_fixtures_require_typed_ordered_preflight(self) -> None:
        plan = _json(FIXTURE_DIR / "valid" / "ab-plan-receipt.v1.json")
        run = _json(FIXTURE_DIR / "valid" / "ab-run-receipt.v1.json")
        self.assertEqual([gate["lane"] for gate in plan["runtime_profile_gates"]], ["oss-local", "oss-cloud"])
        self.assertTrue(all(gate["preflight"]["admission"]["status"] == "pass" for gate in plan["runtime_profile_gates"]))
        self.assertEqual([gate["lane"] for gate in run["runtime_profile_gates"]], ["oss-local", "oss-cloud"])
        self.assertTrue(all(gate["status"] == "completed" for gate in run["runtime_profile_gates"]))

    def test_ab_v1_full_receipts_are_valid_against_their_versioned_schemas(self) -> None:
        plan = self.assert_valid("ab-plan-receipt-v1", "ab-plan-receipt.v1.json")
        run = self.assert_valid("ab-run-receipt-v1", "ab-run-receipt.v1.json")
        self.assertEqual(plan["schema_version"], "skills-sdk.ab-plan-receipt.v1")
        self.assertEqual(run["schema_version"], "skills-sdk.ab-run-receipt.v1")

    def test_ab_plan_v1_schema_rejects_status_packet_contradictions(self) -> None:
        schema = _json(SCHEMA_DIR / "ab-plan-receipt.v1.schema.json")
        status_packet_guard = {"allOf": schema["allOf"]}
        planned = _json(FIXTURE_DIR / "valid" / "ab-plan-receipt.v1.json")

        planned["command_plan"] = []
        with self.assertRaises(AssertionError):
            _validate_schema_subset(status_packet_guard, planned, {})

        blocked = _json(FIXTURE_DIR / "valid" / "ab-plan-receipt.v1.json")
        blocked.update(
            {
                "status": "blocked",
                "blockers": ["typed_preflight_blocker"],
                "command_variant_labels": [],
                "command_plan": [],
            }
        )
        with self.assertRaises(AssertionError):
            _validate_schema_subset(status_packet_guard, blocked, {})

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
        self.assertEqual(payload["judge_profile"]["model"], "qwen3.5:9b-mlx")
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

    def test_ab_judge_score_fixture_records_codex_profile_advisory_decision(self) -> None:
        payload = self.assert_valid("ab-judge-score-receipt", "ab-judge-score-receipt.json")

        self.assertEqual(payload["status"], "scored")
        self.assertEqual(payload["operation"], "ab_judge_score")
        self.assertEqual(payload["judge_profile"]["id"], "oss-local")
        self.assertEqual(payload["judge_profile"]["provider"], "codex")
        self.assertEqual(payload["judge_profile"]["model"], "qwen3.5:9b-mlx")
        self.assertEqual(payload["codex_profile"], "oss-local")
        self.assertTrue(payload["codex_exec_invoked"])
        self.assertEqual(payload["judge_command_argv"][:4], ["codex", "exec", "--profile", "oss-local"])
        self.assertEqual(payload["decision"]["winner"], "skill_b")
        self.assertTrue(payload["provider_invoked"])
        self.assertTrue(payload["network_accessed"])
        self.assertTrue(payload["mutation_performed"])
        self.assertTrue(payload["advisory_only"])
        self.assertTrue(payload["calibration_required"])

    def test_ab_judge_score_schema_rejects_missing_dimension_score(self) -> None:
        payload = _json(FIXTURE_DIR / "valid" / "ab-judge-score-receipt.json")
        payload["decision"]["dimension_scores"].pop()

        with self.assertRaises(AssertionError):
            _validate_schema_subset(
                self.schemas["ab-judge-score-receipt"],
                payload,
                {**self.schemas, **self.schemas_by_file},
            )

    def test_ab_judge_score_schema_rejects_duplicate_dimension_score(self) -> None:
        payload = _json(FIXTURE_DIR / "valid" / "ab-judge-score-receipt.json")
        payload["decision"]["dimension_scores"][1]["dimension_id"] = "task_success"

        with self.assertRaises(AssertionError):
            _validate_schema_subset(
                self.schemas["ab-judge-score-receipt"],
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

    def test_skill_intake_schema_rejects_preview_with_blockers(self) -> None:
        payload = _json(FIXTURE_DIR / "valid" / "skill-intake-receipt.json")
        payload["blockers"] = [
            {
                "id": "source_files_readable",
                "status": "blocker",
                "severity": "blocker",
                "message": "Unreadable source files were found.",
                "evidence": ["assets/closed"],
            }
        ]

        with self.assertRaises(AssertionError):
            _validate_schema_subset(
                self.schemas["skill-intake-receipt"],
                payload,
                {**self.schemas, **self.schemas_by_file},
            )

    def test_skill_intake_schema_rejects_preview_blocker_checks(self) -> None:
        payload = _json(FIXTURE_DIR / "valid" / "skill-intake-receipt.json")
        payload["intake_checks"][0]["status"] = "blocker"
        payload["intake_checks"][0]["severity"] = "blocker"

        with self.assertRaises(AssertionError):
            _validate_schema_subset(
                self.schemas["skill-intake-receipt"],
                payload,
                {**self.schemas, **self.schemas_by_file},
            )

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

    def test_pipeline_start_schema_rejects_lanes_without_commands(self) -> None:
        payload = {
            "schema_version": "skills-sdk.pipeline-start.v1",
            "schema_uri": "https://agent-skills.local/schemas/skills-sdk/pipeline-start.v1.schema.json",
            "status": "pass",
            "target": "Skills/agent-ops/testing",
            "target_class": "global_skill",
            "current_lane": "mechanical_validation",
            "lanes": [{"id": "mechanical_validation", "status": "required_not_run"}],
            "next_action": {
                "lane": "mechanical_validation",
                "command": "./bin/ask skills audit Skills/agent-ops/testing --level strict --json --robot",
                "why": "Run mechanical validation first.",
            },
            "blocked_downstream_lanes": ["scenario_quality"],
            "what_this_proves": "target classification",
            "what_this_does_not_prove": "runtime readiness",
        }

        with self.assertRaises(AssertionError):
            _validate_schema_subset(
                self.schemas["pipeline-start"],
                payload,
                {**self.schemas, **self.schemas_by_file},
            )

        payload["lanes"][0]["command"] = "./bin/ask skills audit Skills/agent-ops/testing --level strict --json --robot"
        _validate_schema_subset(
            self.schemas["pipeline-start"],
            payload,
            {**self.schemas, **self.schemas_by_file},
        )

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
        Verify the placeholder-lifecycle schema rejects fixtures that claim execution or passing.
        """
        self.assert_invalid("placeholder-lifecycle", "placeholder-claims-pass.json")

    def test_risk_mode_taxonomy_receipt_fixture_records_non_execution_boundary(self) -> None:
        payload = self.assert_valid("risk-mode-taxonomy-receipt", "risk-mode-taxonomy-receipt.json")

        self.assertEqual(payload["schema_version"], "skills-sdk.risk-mode-taxonomy-receipt.v0")
        self.assertEqual(payload["operation"], "risk_mode_taxonomy_preview")
        self.assertEqual(payload["primary_mode"], "vulnerable_operation")
        self.assertIn("vulnerable_operation", payload["detected_modes"])
        self.assertEqual(len(payload["mode_results"]), 4)
        self.assertFalse(payload["execution_performed"])
        self.assertFalse(payload["scanner_execution_performed"])
        self.assertFalse(payload["network_accessed"])
        self.assertFalse(payload["credentials_accessed"])
        self.assertFalse(payload["mutation_performed"])
        self.assertIn("PU-033", payload["acceptance_trace"])

    def test_risk_mode_taxonomy_receipt_schema_rejects_execution_claims(self) -> None:
        """
        Verify that the risk-mode-taxonomy-receipt schema rejects fixtures containing execution claims.
        """
        self.assert_invalid("risk-mode-taxonomy-receipt", "risk-mode-taxonomy-executes.json")

    def test_risk_mode_taxonomy_receipt_schema_requires_exactly_four_mode_results(self) -> None:
        payload = _json(FIXTURE_DIR / "valid" / "risk-mode-taxonomy-receipt.json")
        payload["mode_results"] = payload["mode_results"][:3]

        with self.assertRaises(AssertionError):
            _validate_schema_subset(
                self.schemas["risk-mode-taxonomy-receipt"],
                payload,
                {**self.schemas, **self.schemas_by_file},
            )

    def test_risk_mode_taxonomy_receipt_schema_requires_valid_sha256_digest(self) -> None:
        payload = _json(FIXTURE_DIR / "valid" / "risk-mode-taxonomy-receipt.json")
        payload["package_digest"] = "notadigest"

        with self.assertRaises(AssertionError):
            _validate_schema_subset(
                self.schemas["risk-mode-taxonomy-receipt"],
                payload,
                {**self.schemas, **self.schemas_by_file},
            )

    def test_skill_intake_review_receipt_fixture_records_needs_human_review(self) -> None:
        payload = self.assert_valid("skill-intake-review-receipt", "skill-intake-review-receipt.json")

        self.assertEqual(payload["schema_version"], "skills-sdk.skill-intake-review-receipt.v0")
        self.assertEqual(payload["operation"], "skill_intake_review_preview")
        self.assertEqual(payload["status"], "review")
        self.assertEqual(payload["review_decision"], "needs_human_review")
        self.assertEqual(
            set(payload["required_receipts"]),
            {
                "skills-sdk.skill-intake-receipt.v0",
                "skills-sdk.package-security-signature-receipt.v0",
                "skills-sdk.risk-mode-taxonomy-receipt.v0",
            },
        )
        self.assertEqual(payload["intake_receipt"]["schema_version"], "skills-sdk.skill-intake-receipt.v0")
        self.assertEqual(
            payload["package_security_signature_receipt"]["schema_version"],
            "skills-sdk.package-security-signature-receipt.v0",
        )
        self.assertEqual(payload["risk_mode_receipt"]["schema_version"], "skills-sdk.risk-mode-taxonomy-receipt.v0")
        self.assertFalse(payload["execution_performed"])
        self.assertFalse(payload["scanner_execution_performed"])
        self.assertFalse(payload["install_performed"])
        self.assertFalse(payload["projection_mutation_performed"])
        self.assertFalse(payload["network_accessed"])
        self.assertFalse(payload["credentials_accessed"])
        self.assertFalse(payload["mutation_performed"])
        self.assertIn("PU-034", payload["acceptance_trace"])

    def test_skill_intake_review_receipt_schema_rejects_execution_claims(self) -> None:
        """
        Validates that the skill-intake-review-receipt schema rejects fixtures with execution performance claims.
        """
        self.assert_invalid("skill-intake-review-receipt", "skill-intake-review-executes.json")

    def test_skill_intake_review_receipt_schema_rejects_review_status_without_review_items(self) -> None:
        payload = _json(FIXTURE_DIR / "valid" / "skill-intake-review-receipt.json")
        # Remove all review items to break the minContains=1 for review status
        payload["review_items"] = [
            item for item in payload["review_items"] if item["status"] != "review"
        ]

        with self.assertRaises(AssertionError):
            _validate_schema_subset(
                self.schemas["skill-intake-review-receipt"],
                payload,
                {**self.schemas, **self.schemas_by_file},
            )

    def test_skill_intake_review_receipt_schema_rejects_unknown_review_item_ids(self) -> None:
        payload = _json(FIXTURE_DIR / "valid" / "skill-intake-review-receipt.json")
        payload["review_items"][0]["id"] = "unknown_custom_check"

        with self.assertRaises(AssertionError):
            _validate_schema_subset(
                self.schemas["skill-intake-review-receipt"],
                payload,
                {**self.schemas, **self.schemas_by_file},
            )

    def test_skill_intake_review_receipt_schema_rejects_review_without_package_signature(self) -> None:
        payload = _json(FIXTURE_DIR / "valid" / "skill-intake-review-receipt.json")
        payload["package_security_signature_receipt"] = None

        with self.assertRaises(AssertionError):
            _validate_schema_subset(
                self.schemas["skill-intake-review-receipt"],
                payload,
                {**self.schemas, **self.schemas_by_file},
            )

    def test_skill_intake_review_receipt_schema_rejects_pass_without_package_signature(self) -> None:
        payload = _json(FIXTURE_DIR / "valid" / "skill-intake-review-receipt.json")
        payload["status"] = "pass"
        payload["review_decision"] = "ready_for_adoption_decision"
        payload["package_security_signature_receipt"] = None
        for item in payload["review_items"]:
            item["status"] = "pass"

        with self.assertRaises(AssertionError):
            _validate_schema_subset(
                self.schemas["skill-intake-review-receipt"],
                payload,
                {**self.schemas, **self.schemas_by_file},
            )


if __name__ == "__main__":
    unittest.main()
