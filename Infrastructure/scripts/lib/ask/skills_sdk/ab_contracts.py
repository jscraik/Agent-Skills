from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class _SdkContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


_DECISION_LABELS = {"skill_a", "skill_b", "inconclusive"}


def _exact_decision_labels(rows: list[str]) -> bool:
    return set(rows) == _DECISION_LABELS


def _validate_exact_decision_labels(value: list[str], *, message: str) -> list[str]:
    if not _exact_decision_labels(value):
        raise ValueError(message)
    return value


class EvalExecutionProfile(_SdkContractModel):
    id: str = Field(min_length=1)
    runner: Literal["codex_exec"]
    sandbox_mode: Literal["read-only", "workspace-write"]
    approval_policy: Literal["on-request"]
    codex_json_events_required: Literal[True]
    output_schema_supported: Literal[True]
    mutation_allowed: bool


class EvalJudgeProfile(_SdkContractModel):
    id: str = Field(min_length=1)
    provider: Literal["ollama", "codex"]
    mode: Literal["local", "cloud", "codex-fast"]
    host: str | None
    model: str = Field(min_length=1)
    network_required: bool
    secret_env_names: list[str]
    auth_boundary: Literal["none", "env_secret", "codex_cli_auth"]
    receives_sanitized_outputs_only: Literal[True]


class EvalSecretBoundary(_SdkContractModel):
    skill_execution_env_secret_names: list[str]
    judge_env_secret_names: list[str]
    skill_execution_receives_judge_secrets: Literal[False]


class EvalProfilePreviewReceipt(_SdkContractModel):
    schema_version: Literal["skills-sdk.eval-profile-preview-receipt.v0"]
    schema_uri: Literal[
        "https://jscraik.local/agent-skills/schemas/skills-sdk/eval-profile-preview-receipt.v0.schema.json"
    ]
    status: Literal["preview", "blocked"]
    operation: Literal["eval_profile_preview"]
    execution_profiles: list[EvalExecutionProfile] = Field(min_length=1)
    judge_profiles: list[EvalJudgeProfile] = Field(min_length=1)
    secret_boundary: EvalSecretBoundary
    execution_boundary: Literal["codex_exec_sandbox"]
    external_intake_boundary: Literal["sdk_quarantine_only"]
    mutation_performed: Literal[False]
    network_accessed: Literal[False]
    provider_invoked: Literal[False]
    blockers: list[str]
    acceptance_trace: list[
        Literal["FR-003", "FR-008", "SA-003", "SA-004", "VP-021", "VP-022", "VP-030"]
    ] = Field(min_length=1)
    agent_summary: str = Field(min_length=1)


class AbRubricScoreScale(_SdkContractModel):
    minimum: Literal[0]
    maximum: Literal[5]


class AbRubricDimension(_SdkContractModel):
    id: Literal["task_success", "instruction_following", "evidence_quality", "repo_safety", "maintainability"]
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    weight: Annotated[float, Field(ge=0)]
    required_evidence: list[str] = Field(min_length=1)

    @field_validator("required_evidence")
    @classmethod
    def _required_evidence_unique(cls, value: list[str]) -> list[str]:
        if len(set(value)) != len(value):
            raise ValueError("rubric dimension evidence refs must be unique")
        return value


class AbRubricWinnerPolicy(_SdkContractModel):
    minimum_normalized_delta: Annotated[float, Field(ge=0)]
    minimum_confidence: Literal["low", "medium", "high"]
    tie_result: Literal["inconclusive"]
    allowed_winners: list[Literal["skill_a", "skill_b", "inconclusive"]] = Field(min_length=3, max_length=3)

    @field_validator("allowed_winners")
    @classmethod
    def _allowed_winners_exact(
        cls, value: list[Literal["skill_a", "skill_b", "inconclusive"]]
    ) -> list[Literal["skill_a", "skill_b", "inconclusive"]]:
        return _validate_exact_decision_labels(value, message="rubric winner policy must contain exact winner labels")


class AbRubricStagePolicy(_SdkContractModel):
    stage: Literal["local_oss_loop", "cloud_oss_loop", "external_validation"]
    judge_profile: Literal["oss-local", "oss-cloud", "tessl"]
    default_model: str = Field(min_length=1)
    confidence_weight: Literal["fast_signal", "second_pass_signal", "independent_confirmation"]
    promotion_gate: Literal["improvement_signal_only", "confirm_local_delta", "release_confirmation"]


class AbRubricJudgeOutputContract(_SdkContractModel):
    decision_schema_version: Literal["skills-sdk.ab-judge-decision.v0"]
    requires_dimension_scores: Literal[True]
    requires_evidence_refs: Literal[True]
    requires_reason_per_dimension: Literal[True]
    unvalidated_judges_are_advisory: Literal[True]


class AbRubricContract(_SdkContractModel):
    rubric_id: Literal["skills-sdk.ab-rubric.v0"]
    rubric_version: Literal["v0"]
    stable_across_stages: Literal[True]
    score_scale: AbRubricScoreScale
    normalization: Literal["weighted_sum_divided_by_five"]
    dimensions: list[AbRubricDimension] = Field(min_length=5, max_length=5)
    winner_policy: AbRubricWinnerPolicy
    stage_policies: list[AbRubricStagePolicy] = Field(min_length=3, max_length=3)
    judge_output_contract: AbRubricJudgeOutputContract

    @model_validator(mode="after")
    def _rubric_is_canonical(self) -> AbRubricContract:
        expected_dimensions = {"task_success", "instruction_following", "evidence_quality", "repo_safety", "maintainability"}
        if {dimension.id for dimension in self.dimensions} != expected_dimensions:
            raise ValueError("A/B rubric must contain the exact canonical dimensions")
        if abs(sum(dimension.weight for dimension in self.dimensions) - 1.0) > 0.000001:
            raise ValueError("A/B rubric dimension weights must sum to 1.0")
        if {policy.stage for policy in self.stage_policies} != {
            "local_oss_loop",
            "cloud_oss_loop",
            "external_validation",
        }:
            raise ValueError("A/B rubric must cover local, cloud, and external validation stages")
        return self


class AbRubricReceipt(_SdkContractModel):
    schema_version: Literal["skills-sdk.ab-rubric-receipt.v0"]
    schema_uri: Literal["https://jscraik.local/agent-skills/schemas/skills-sdk/ab-rubric-receipt.v0.schema.json"]
    status: Literal["preview"]
    operation: Literal["ab_rubric"]
    rubric: AbRubricContract
    rubric_digest: str = Field(min_length=71)
    calibration_required: Literal[True]
    provider_invoked: Literal[False]
    network_accessed: Literal[False]
    mutation_performed: Literal[False]
    blockers: list[str] = Field(max_length=0)
    acceptance_trace: list[Literal["FR-003", "FR-008", "SA-004", "VP-021", "VP-022", "VP-030"]] = Field(
        min_length=1
    )
    agent_summary: str = Field(min_length=1)


class AbSkillVariant(_SdkContractModel):
    label: Literal["A", "B"]
    query: str = Field(min_length=1)
    skill_ir_schema_version: str = Field(min_length=1)
    package_id: str = Field(min_length=1)
    package_digest: str = Field(min_length=71)


class AbFixtureIdentity(_SdkContractModel):
    path: str = Field(min_length=1)
    digest: str = Field(min_length=71)
    size_bytes: int = Field(ge=0)


class AbEvidencePlan(_SdkContractModel):
    codex_json_events: Literal[True]
    output_diff: Literal[True]
    validation_results: Literal[True]
    judge_decision: Literal[True]
    winner_values: list[Literal["skill_a", "skill_b", "inconclusive"]] = Field(min_length=3, max_length=3)

    @field_validator("winner_values")
    @classmethod
    def _winner_values_exact(
        cls, value: list[Literal["skill_a", "skill_b", "inconclusive"]]
    ) -> list[Literal["skill_a", "skill_b", "inconclusive"]]:
        return _validate_exact_decision_labels(value, message="winner_values must contain the exact A/B decision labels")


def _exact_variant_labels(rows: list[object], *, attr: str = "variant_label") -> bool:
    return len(rows) == 2 and {getattr(row, attr) for row in rows} == {"A", "B"}


def _exact_command_labels(rows: list[str]) -> bool:
    return set(rows) == {"A", "B"}


class AbPreviewReceipt(_SdkContractModel):
    schema_version: Literal["skills-sdk.ab-preview-receipt.v0"]
    schema_uri: Literal["https://jscraik.local/agent-skills/schemas/skills-sdk/ab-preview-receipt.v0.schema.json"]
    status: Literal["preview", "blocked"]
    operation: Literal["ab_preview"]
    skill_a: AbSkillVariant | None
    skill_b: AbSkillVariant | None
    fixture: AbFixtureIdentity | None
    execution_profile: EvalExecutionProfile | None
    judge_profile: EvalJudgeProfile | None
    evidence_plan: AbEvidencePlan
    secret_boundary: EvalSecretBoundary
    execution_boundary: Literal["codex_exec_sandbox"]
    judge_boundary: Literal["post_run_sanitized_evidence_only"]
    mutation_performed: Literal[False]
    network_accessed: Literal[False]
    provider_invoked: Literal[False]
    codex_exec_invoked: Literal[False]
    blockers: list[str]
    acceptance_trace: list[
        Literal["FR-003", "FR-008", "SA-003", "SA-004", "VP-021", "VP-022", "VP-030"]
    ] = Field(min_length=1)
    agent_summary: str = Field(min_length=1)

    @model_validator(mode="after")
    def _status_matches_evidence(self) -> AbPreviewReceipt:
        if self.status == "preview":
            if self.blockers:
                raise ValueError("preview A/B receipts must not include blockers")
            if not self._has_preview_evidence():
                raise ValueError("preview A/B receipts must include complete experiment evidence")
        elif not self.blockers:
            raise ValueError("blocked A/B receipts must include blockers")
        return self

    def _has_preview_evidence(self) -> bool:
        return all(
            item is not None
            for item in (self.skill_a, self.skill_b, self.fixture, self.execution_profile, self.judge_profile)
        )


class AbCodexCommandPlan(_SdkContractModel):
    variant_label: Literal["A", "B"]
    command_argv: list[str] = Field(min_length=10)
    sandbox_mode: Literal["read-only", "workspace-write"]
    approval_policy: Literal["on-request"]
    event_log_path: str = Field(min_length=1)
    output_last_message_path: str = Field(min_length=1)
    prompt_stdin_path: str = Field(min_length=1)
    runner_stdout_capture_path: str = Field(min_length=1)
    runner_prompt_input_path: str = Field(min_length=1)
    prompt_stdin_digest: str = Field(min_length=71)
    planned_write_paths: list[str]
    allowed_secret_env_names: list[str]


class AbPlanReceipt(_SdkContractModel):
    schema_version: Literal["skills-sdk.ab-plan-receipt.v0"]
    schema_uri: Literal["https://jscraik.local/agent-skills/schemas/skills-sdk/ab-plan-receipt.v0.schema.json"]
    status: Literal["planned", "blocked"]
    operation: Literal["ab_plan"]
    skill_a: AbSkillVariant | None
    skill_b: AbSkillVariant | None
    fixture: AbFixtureIdentity | None
    execution_profile: EvalExecutionProfile | None
    judge_profile: EvalJudgeProfile | None
    evidence_root: str | None = Field(default=None, min_length=1)
    experiment_id: str | None = Field(default=None, min_length=16, max_length=16)
    command_variant_labels: list[Literal["A", "B"]] = Field(max_length=2)
    command_plan: list[AbCodexCommandPlan] = Field(max_length=2)
    secret_boundary: EvalSecretBoundary
    execution_boundary: Literal["codex_exec_sandbox"]
    judge_boundary: Literal["post_run_sanitized_evidence_only"]
    mutation_performed: Literal[False]
    network_accessed: Literal[False]
    provider_invoked: Literal[False]
    codex_exec_invoked: Literal[False]
    blockers: list[str]
    acceptance_trace: list[
        Literal["FR-003", "FR-008", "SA-003", "SA-004", "VP-021", "VP-022", "VP-030"]
    ] = Field(min_length=1)
    agent_summary: str = Field(min_length=1)

    @model_validator(mode="after")
    def _status_matches_plan(self) -> AbPlanReceipt:
        if self.status == "planned":
            if self.blockers:
                raise ValueError("planned A/B receipts must not include blockers")
            if not self._has_plan_evidence():
                raise ValueError("planned A/B receipts must include complete plan evidence")
            if not _exact_variant_labels(self.command_plan):
                raise ValueError("planned A/B receipts must include exactly one command plan per variant")
            if not _exact_command_labels(self.command_variant_labels):
                raise ValueError("planned A/B receipts must include exact command variant labels")
        elif not self.blockers:
            raise ValueError("blocked A/B plan receipts must include blockers")
        return self

    def _has_plan_evidence(self) -> bool:
        return all(
            item is not None
            for item in (
                self.skill_a,
                self.skill_b,
                self.fixture,
                self.execution_profile,
                self.judge_profile,
                self.evidence_root,
                self.experiment_id,
            )
        )


class AbVariantRunResult(_SdkContractModel):
    variant_label: Literal["A", "B"]
    status: Literal["pass", "blocked"]
    exit_code: int
    command_argv: list[str] = Field(min_length=10)
    sandbox_mode: Literal["read-only", "workspace-write"]
    prompt_stdin_path: str = Field(min_length=1)
    prompt_stdin_digest: str = Field(min_length=71)
    runner_stdout_capture_path: str = Field(min_length=1)
    runner_stdout_digest: str = Field(min_length=71)
    runner_stderr_capture_path: str = Field(min_length=1)
    runner_stderr_digest: str = Field(min_length=71)
    output_last_message_path: str = Field(min_length=1)
    output_last_message_digest: str | None = Field(default=None, min_length=71)
    blockers: list[str]

    @model_validator(mode="after")
    def _status_matches_blockers(self) -> AbVariantRunResult:
        if self.status == "pass" and self.blockers:
            raise ValueError("passing A/B variant results must not include blockers")
        if self.status == "blocked" and not self.blockers:
            raise ValueError("blocked A/B variant results must include blockers")
        return self


class AbRunReceipt(_SdkContractModel):
    schema_version: Literal["skills-sdk.ab-run-receipt.v0"]
    schema_uri: Literal["https://jscraik.local/agent-skills/schemas/skills-sdk/ab-run-receipt.v0.schema.json"]
    status: Literal["completed", "blocked"]
    operation: Literal["ab_run"]
    skill_a: AbSkillVariant | None
    skill_b: AbSkillVariant | None
    fixture: AbFixtureIdentity | None
    execution_profile: EvalExecutionProfile | None
    judge_profile: EvalJudgeProfile | None
    evidence_root: str | None = Field(default=None, min_length=1)
    experiment_id: str | None = Field(default=None, min_length=16, max_length=16)
    command_variant_labels: list[Literal["A", "B"]] = Field(max_length=2)
    command_plan: list[AbCodexCommandPlan] = Field(max_length=2)
    variant_results: list[AbVariantRunResult] = Field(max_length=2)
    secret_boundary: EvalSecretBoundary
    execution_boundary: Literal["codex_exec_sandbox"]
    judge_boundary: Literal["post_run_sanitized_evidence_only"]
    mutation_performed: bool
    network_accessed: bool
    provider_invoked: bool
    judge_provider_invoked: Literal[False]
    codex_exec_invoked: bool
    timeout_seconds: int = Field(ge=1)
    blockers: list[str]
    acceptance_trace: list[
        Literal["FR-003", "FR-008", "SA-003", "SA-004", "VP-021", "VP-022", "VP-030"]
    ] = Field(min_length=1)
    agent_summary: str = Field(min_length=1)

    @model_validator(mode="after")
    def _status_matches_run(self) -> AbRunReceipt:
        if self.status == "completed":
            if self.blockers:
                raise ValueError("completed A/B run receipts must not include blockers")
            if not self._has_run_evidence():
                raise ValueError("completed A/B run receipts must include complete run evidence")
            if not _exact_variant_labels(self.command_plan):
                raise ValueError("completed A/B run receipts must include exactly one command plan per variant")
            if not _exact_variant_labels(self.variant_results):
                raise ValueError("completed A/B run receipts must include exactly one result per variant")
            if set(self.command_variant_labels) != {"A", "B"}:
                raise ValueError("completed A/B run receipts must include exact command variant labels")
            if not self._reports_codex_side_effects():
                raise ValueError("completed A/B run receipts must report Codex execution side effects")
        elif not self.blockers:
            raise ValueError("blocked A/B run receipts must include blockers")
        return self

    def _has_run_evidence(self) -> bool:
        return all(
            item is not None
            for item in (
                self.skill_a,
                self.skill_b,
                self.fixture,
                self.execution_profile,
                self.judge_profile,
                self.evidence_root,
                self.experiment_id,
            )
        )

    def _reports_codex_side_effects(self) -> bool:
        return self.mutation_performed and self.network_accessed and self.provider_invoked and self.codex_exec_invoked


class AbJudgePackageIdentity(_SdkContractModel):
    package_id: str = Field(min_length=1)
    package_digest: str = Field(min_length=71)


class AbJudgeFixtureIdentity(_SdkContractModel):
    path: str = Field(min_length=1)
    digest: str = Field(min_length=71)


class AbJudgeSanitizedVariantResult(_SdkContractModel):
    variant_label: Literal["A", "B"]
    status: Literal["pass", "blocked"]
    exit_code: int
    sandbox_mode: Literal["read-only", "workspace-write"]
    output_last_message_digest: str = Field(min_length=71)
    runner_stdout_digest: str = Field(min_length=71)
    runner_stderr_digest: str = Field(min_length=71)
    blockers: list[str]


class AbJudgeComparisonPayload(_SdkContractModel):
    schema_version: Literal["skills-sdk.ab-judge-decision.v0"]
    experiment_id: str = Field(min_length=16, max_length=16)
    rubric: AbRubricContract
    rubric_digest: str = Field(min_length=71)
    skill_a: AbJudgePackageIdentity
    skill_b: AbJudgePackageIdentity
    fixture: AbJudgeFixtureIdentity
    execution_profile: str = Field(min_length=1)
    variant_results: list[AbJudgeSanitizedVariantResult] = Field(min_length=2, max_length=2)
    allowed_winners: list[Literal["skill_a", "skill_b", "inconclusive"]] = Field(min_length=3, max_length=3)

    @model_validator(mode="after")
    def _comparison_has_exact_labels(self) -> AbJudgeComparisonPayload:
        if {result.variant_label for result in self.variant_results} != {"A", "B"}:
            raise ValueError("A/B judge comparison must contain exactly one result per variant")
        if set(self.allowed_winners) != {"skill_a", "skill_b", "inconclusive"}:
            raise ValueError("A/B judge comparison must contain exact winner labels")
        return self


class AbJudgePreviewReceipt(_SdkContractModel):
    schema_version: Literal["skills-sdk.ab-judge-preview-receipt.v0"]
    schema_uri: Literal[
        "https://jscraik.local/agent-skills/schemas/skills-sdk/ab-judge-preview-receipt.v0.schema.json"
    ]
    status: Literal["preview", "blocked"]
    operation: Literal["ab_judge_preview"]
    run_receipt_path: str | None = Field(default=None, min_length=1)
    run_receipt_digest: str | None = Field(default=None, min_length=71)
    experiment_id: str | None = Field(default=None, min_length=16, max_length=16)
    judge_profile: EvalJudgeProfile | None
    rubric_id: Literal["skills-sdk.ab-rubric.v0"] | None
    rubric_digest: str | None = Field(default=None, min_length=71)
    comparison_payload: AbJudgeComparisonPayload | None
    judge_prompt_digest: str | None = Field(default=None, min_length=71)
    decision_schema_version: Literal["skills-sdk.ab-judge-decision.v0"]
    allowed_winners: list[Literal["skill_a", "skill_b", "inconclusive"]] = Field(min_length=3, max_length=3)
    calibration_required: Literal[True]
    provider_invoked: Literal[False]
    network_accessed: Literal[False]
    mutation_performed: Literal[False]
    blockers: list[str]
    acceptance_trace: list[
        Literal["FR-003", "FR-008", "SA-003", "SA-004", "VP-021", "VP-022", "VP-030"]
    ] = Field(min_length=1)
    agent_summary: str = Field(min_length=1)

    @model_validator(mode="after")
    def _status_matches_judge_preview(self) -> AbJudgePreviewReceipt:
        if not _exact_decision_labels(self.allowed_winners):
            raise ValueError("A/B judge preview must contain exact winner labels")
        if self.status == "preview":
            if self.blockers:
                raise ValueError("preview A/B judge receipts must not include blockers")
            if not self._has_judge_input_evidence():
                raise ValueError("preview A/B judge receipts must include complete judge input evidence")
        elif not self.blockers:
            raise ValueError("blocked A/B judge receipts must include blockers")
        return self

    def _has_judge_input_evidence(self) -> bool:
        return all(
            item is not None
            for item in (
                self.run_receipt_path,
                self.run_receipt_digest,
                self.experiment_id,
                self.judge_profile,
                self.rubric_id,
                self.rubric_digest,
                self.comparison_payload,
                self.judge_prompt_digest,
            )
        )
