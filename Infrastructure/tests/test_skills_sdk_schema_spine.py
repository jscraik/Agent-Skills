import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "tests"))

from helpers.schema_validator import _validate_schema_subset  # noqa: E402
from helpers.skills_sdk_schema_spine import (  # noqa: E402
    FIXTURE_DIR,
    SchemaSpineTestCase,
    _json,
)


class TestSkillsSdkSchemaSpine(SchemaSpineTestCase):

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

    def test_evidence_status_fixture_is_valid(self) -> None:
        payload = self.assert_valid("evidence-status", "evidence-status.json")
        self.assertEqual(payload["selected_lane"], "local-build")
        self.assertTrue(payload["qa_dispatch_record"]["controller_owned"])

    def test_phoenix_smoke_receipt_fixture_is_valid(self) -> None:
        payload = self.assert_valid("phoenix-smoke-receipt", "phoenix-smoke-receipt.json")

        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["project_name"], "agent-skills-skills-sdk-evals")
        self.assertTrue(payload["mutation_performed"])

    def test_phoenix_smoke_receipt_rejects_wrong_project(self) -> None:
        self.assert_invalid("phoenix-smoke-receipt", "phoenix-smoke-receipt-wrong-project.json")

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

    def test_sdk_check_fixture_binds_source_and_claims_boundary(self) -> None:
        payload = self.assert_valid("sdk-check", "sdk-check.json")

        self.assertEqual(payload["canonical_source_path"], "Skills/agent-ops/simplify/SKILL.md")
        self.assertIn("does not prove package readiness", payload["claims_boundary"])

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

    def test_eval_profile_preview_fixture_records_local_profile_boundaries(self) -> None:
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

    def test_eval_profile_preview_fixture_records_cloud_and_security_boundaries(self) -> None:
        payload = self.assert_valid("eval-profile-preview-receipt", "eval-profile-preview-receipt.json")
        judge_by_id = {profile["id"]: profile for profile in payload["judge_profiles"]}
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
        self.assertEqual(judge_by_id["oss-cloud"]["model"], "deepseek-v4-flash:0731-cloud")
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

if __name__ == "__main__":
    unittest.main()
