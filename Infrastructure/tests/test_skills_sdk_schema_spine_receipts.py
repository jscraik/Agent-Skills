import copy
from helpers.schema_validator import _validate_schema_subset  # noqa: E402
from helpers.skills_sdk_schema_spine import (  # noqa: E402
    FIXTURE_DIR,
    SCHEMA_DIR,
    SchemaSpineTestCase,
    _json,
)


class TestSkillsSdkSchemaSpineReceipts(SchemaSpineTestCase):

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

    def test_ab_run_schema_rejects_completed_receipt_without_ordered_variant_proof(self) -> None:
        payload = _json(FIXTURE_DIR / "valid" / "ab-run-receipt.v1.json")
        payload["command_variant_labels"] = ["B", "A"]

        with self.assertRaises(AssertionError):
            _validate_schema_subset(
                self.schemas["ab-run-receipt-v1"],
                payload,
                {**self.schemas, **self.schemas_by_file},
            )

        payload = _json(FIXTURE_DIR / "valid" / "ab-run-receipt.v1.json")
        payload["variant_results"][0]["variant_label"] = "B"
        payload["variant_results"][1]["variant_label"] = "A"

        with self.assertRaises(AssertionError):
            _validate_schema_subset(
                self.schemas["ab-run-receipt-v1"],
                payload,
                {**self.schemas, **self.schemas_by_file},
            )

    def test_ab_run_schema_rejects_completed_receipt_without_execution_side_effects(self) -> None:
        payload = _json(FIXTURE_DIR / "valid" / "ab-run-receipt.v1.json")
        payload["provider_invoked"] = False

        with self.assertRaises(AssertionError):
            _validate_schema_subset(
                self.schemas["ab-run-receipt-v1"],
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

    def test_ab_run_schema_requires_top_level_blocker_after_cloud_gate_blocks(self) -> None:
        payload = _json(FIXTURE_DIR / "valid" / "ab-run-receipt.v1.json")
        payload["status"] = "blocked"
        payload["blockers"] = []
        payload["runtime_profile_gates"][1]["status"] = "blocked"
        payload["runtime_profile_gates"][1]["blockers"] = ["cloud_auth_unavailable"]

        with self.assertRaises(AssertionError):
            _validate_schema_subset(
                self.schemas["ab-run-receipt-v1"],
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

    def test_judge_schemas_accept_versioned_experiment_identifiers(self) -> None:
        preview = _json(FIXTURE_DIR / "valid" / "ab-judge-preview-receipt.json")
        preview["experiment_id"] = "ex_0123456789abcdef"
        preview["comparison_payload"]["experiment_id"] = "ex_0123456789abcdef"
        _validate_schema_subset(
            self.schemas["ab-judge-preview-receipt"],
            preview,
            {**self.schemas, **self.schemas_by_file},
        )

        score = _json(FIXTURE_DIR / "valid" / "ab-judge-score-receipt.json")
        score["experiment_id"] = "ex_0123456789abcdef"
        score["decision"]["experiment_id"] = "ex_0123456789abcdef"
        _validate_schema_subset(
            self.schemas["ab-judge-score-receipt"],
            score,
            {**self.schemas, **self.schemas_by_file},
        )

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

    def test_sdk_check_schema_requires_source_and_claims_boundary(self) -> None:
        self.assert_invalid("sdk-check", "sdk-check-missing-canonical-source-path.json")
        self.assert_invalid("sdk-check", "sdk-check-missing-claims-boundary.json")

    def _assert_sdk_check_invalid(self, payload: dict) -> None:
        with self.assertRaises(AssertionError):
            _validate_schema_subset(
                self.schemas["sdk-check"],
                copy.deepcopy(payload),
                {**self.schemas, **self.schemas_by_file},
            )

    def _assert_sdk_check_invalid_payloads(self, payloads: tuple[dict, ...]) -> None:
        for payload in payloads:
            with self.subTest(payload=payload):
                self._assert_sdk_check_invalid(payload)

    def test_sdk_check_schema_rejects_empty_contract_values(self) -> None:
        payload = self.assert_valid("sdk-check", "sdk-check.json")
        invalid_payloads = (
            {**payload, "canonical_source_path": ""},
            {**payload, "canonical_source_path": None},
            {**payload, "validation_commands": []},
            {**payload, "claims_boundary": "This proves package readiness."},
            {**payload, "doctor_status": "blocked"},
        )
        self._assert_sdk_check_invalid_payloads(invalid_payloads)

    def test_sdk_check_schema_rejects_blocked_receipt_contradictions(self) -> None:
        payload = self.assert_valid("sdk-check", "sdk-check.json")
        invalid_payloads = (
            {
                **payload,
                "receipt": {
                    **payload["receipt"],
                    "status": "blocked",
                    "failure_class": "validation_failed",
                },
            },
            {**payload, "receipt": {**payload["receipt"], "exit_code": 2}},
            {
                **payload,
                "status": "blocked",
                "failure_class": "validation_failed",
                "doctor_status": "warning",
                "receipt": {
                    **payload["receipt"],
                    "status": "blocked",
                    "failure_class": "validation_failed",
                    "exit_code": 2,
                },
            },
        )
        self._assert_sdk_check_invalid_payloads(invalid_payloads)

    def test_sdk_check_schema_rejects_status_and_doctor_contradictions(self) -> None:
        payload = self.assert_valid("sdk-check", "sdk-check.json")
        invalid_payloads = (
            {
                **payload,
                "status": "blocked",
                "failure_class": "validation_failed",
                "doctor_status": "blocked",
                "receipt": {
                    **payload["receipt"],
                    "status": "blocked",
                    "failure_class": "validation_failed",
                    "exit_code": 0,
                },
            },
            {
                **payload,
                "status": "degraded",
                "failure_class": "validation_failed",
                "doctor_status": "warning",
                "receipt": {
                    **payload["receipt"],
                    "status": "degraded",
                    "failure_class": "validation_failed",
                    "exit_code": 2,
                },
            },
        )
        self._assert_sdk_check_invalid_payloads(invalid_payloads)

    def test_sdk_check_schema_rejects_degraded_without_doctor(self) -> None:
        payload = self.assert_valid("sdk-check", "sdk-check.json")
        invalid_payload = {
            **payload,
            "status": "degraded",
            "failure_class": "validation_failed",
            "doctor_status": None,
            "receipt": {
                **payload["receipt"],
                "status": "degraded",
                "failure_class": "validation_failed",
                "exit_code": 0,
            },
        }
        self._assert_sdk_check_invalid(invalid_payload)

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
