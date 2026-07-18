from __future__ import annotations

import math
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from ask.skills_sdk.ab_contract_guards import (
    exact_variant_labels as _exact_variant_labels,
    run_gate_is_completed,
    validate_plan_gate_identity,
    validate_plan_gate_packet,
    validate_argv_output_last_message_path,
    validate_run_receipt_status,
)
from ask.skills_sdk.ab_profile_contracts import (
    AbLanePreflight,
    AbPreflightBlocker,
    EvalExecutionProfile,
    EvalJudgeProfile,
    EvalSecretBoundary,
)
from ask.skills_sdk.ab_transport_contracts import (
    is_approved_op_binary as _is_approved_op_binary,
    is_opaque_env_reference as _is_opaque_env_reference,
)
from ask.skills_sdk.eval_ab_rubric import AB_RUBRIC_DIMENSIONS, AB_RUBRIC_WINNER_POLICY


class _SdkContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class DurationValue(_SdkContractModel):
    value: Annotated[float, Field(ge=0)]
    unit: Literal["ms", "s", "min", "h"]


_DECISION_LABELS = {"skill_a", "skill_b", "inconclusive"}
_AB_JUDGE_DIMENSION_IDS = {str(dimension["id"]) for dimension in AB_RUBRIC_DIMENSIONS}
_AB_JUDGE_DIMENSION_WEIGHTS = {str(dimension["id"]): float(dimension["weight"]) for dimension in AB_RUBRIC_DIMENSIONS}
_EXPERIMENT_ID_PATTERN = r"^(?:ex_[a-z0-9]{16}|[0-9a-f]{16})$"


def _exact_decision_labels(rows: list[str]) -> bool:
    return set(rows) == _DECISION_LABELS


def _codex_profile_from_argv(argv: list[str]) -> str:
    if len(argv) < 4 or argv[:3] != ["codex", "exec", "--profile"]:
        raise ValueError("Codex argv must start with the installed CLI placement: codex exec --profile")
    if argv.count("--profile") != 1:
        raise ValueError("Codex argv must contain exactly one --profile option")
    profile = argv[3]
    if profile not in {"oss-local", "oss-cloud"}:
        raise ValueError("Codex argv profile must be an admitted Skills SDK runtime profile")
    return profile


def _codex_profile_from_judge_argv(argv: list[str], *, require_approval: bool = True) -> str:
    try:
        codex_index = _judge_codex_index(argv)
        profile = _judge_profile_token(argv, codex_index)
        _validate_judge_argv(argv, codex_index, require_approval)
    except (IndexError, ValueError) as exc:
        raise ValueError("judge Codex argv must contain an ordered profile option") from exc
    if profile not in _JUDGE_PROFILES:
        raise ValueError("judge Codex argv profile must be an admitted runtime profile")
    return profile


_JUDGE_PROFILES = ("oss-local", "oss-local-code", "oss-local-fallback", "oss-security", "oss-cloud")


def _judge_codex_index(argv: list[str]) -> int:
    if not argv:
        raise ValueError("empty argv")
    if argv[0] == "codex":
        return 0
    if (
        len(argv) >= 6
        and _is_approved_op_binary(argv[0])
        and argv[1:3] == ["run", "--env-file"]
        and _is_opaque_env_reference(argv[3])
        and argv[4] == "--"
    ):
        return 5
    raise ValueError("judge argv must use codex directly or the approved op wrapper")


def _judge_profile_token(argv: list[str], codex_index: int) -> str:
    profile_index = argv.index("--profile", codex_index)
    return argv[profile_index + 1]


def _validate_judge_argv(argv: list[str], codex_index: int, require_approval: bool) -> None:
    profile_index = argv.index("--profile", codex_index)
    if argv[codex_index + 1] != "exec" or argv.count("--profile") != 1 or profile_index != codex_index + 2:
        raise ValueError("judge Codex argv must contain an ordered profile option")
    if require_approval and (argv.count("--ask-for-approval") != 1 or argv[argv.index("--ask-for-approval", codex_index) + 1] != "on-request"):
        raise ValueError("judge Codex argv must prove the on-request approval policy")


def _validate_exact_decision_labels(value: list[str], *, message: str) -> list[str]:
    if not _exact_decision_labels(value):
        raise ValueError(message)
    return value


def _computed_judge_scores(rows: list[AbJudgeDimensionScore]) -> dict[str, float]:
    score_a = sum(row.skill_a_score * _AB_JUDGE_DIMENSION_WEIGHTS[row.dimension_id] for row in rows) / 5
    score_b = sum(row.skill_b_score * _AB_JUDGE_DIMENSION_WEIGHTS[row.dimension_id] for row in rows) / 5
    return {"normalized_score_a": score_a, "normalized_score_b": score_b}


def _judge_scores_match(decision: AbJudgeDecision, computed_scores: dict[str, float]) -> bool:
    return all(
        math.isclose(getattr(decision, key), computed_scores[key], rel_tol=0, abs_tol=1e-9)
        for key in computed_scores
    )


def _judge_confidence_meets_minimum(value: str, minimum: str) -> bool:
    confidence_rank = {"low": 0, "medium": 1, "high": 2}
    return confidence_rank[value] >= confidence_rank[minimum]


def _expected_judge_winner(decision: AbJudgeDecision, computed_scores: dict[str, float]) -> str:
    delta = computed_scores["normalized_score_b"] - computed_scores["normalized_score_a"]
    minimum_delta = float(AB_RUBRIC_WINNER_POLICY["minimum_normalized_delta"])
    tie_result = str(AB_RUBRIC_WINNER_POLICY["tie_result"])
    if abs(delta) < minimum_delta:
        return tie_result
    minimum_confidence = str(AB_RUBRIC_WINNER_POLICY["minimum_confidence"])
    if not _judge_confidence_meets_minimum(decision.confidence, minimum_confidence):
        return tie_result
    return "skill_b" if delta > 0 else "skill_a"


class EvalProfilePreviewReceipt(_SdkContractModel):
    schema_version: Literal["skills-sdk.eval-profile-preview-receipt.v0"]
    schema_uri: Literal[
        "https://agent-skills.local/schemas/skills-sdk/eval-profile-preview-receipt.v0.schema.json"
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
    id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    weight: Annotated[float, Field(ge=0)]
    required_evidence: list[str] = Field(min_length=1)

    @field_validator("id")
    @classmethod
    def _id_canonical(cls, value: str) -> str:
        if value not in _AB_JUDGE_DIMENSION_IDS:
            raise ValueError("rubric dimension id must be canonical")
        return value

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
        if {dimension.id for dimension in self.dimensions} != _AB_JUDGE_DIMENSION_IDS:
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
    schema_uri: Literal["https://agent-skills.local/schemas/skills-sdk/ab-rubric-receipt.v0.schema.json"]
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


class AbPreviewReceipt(_SdkContractModel):
    schema_version: Literal["skills-sdk.ab-preview-receipt.v0"]
    schema_uri: Literal["https://agent-skills.local/schemas/skills-sdk/ab-preview-receipt.v0.schema.json"]
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
    codex_profile: Literal["oss-local", "oss-cloud"]
    command_argv: list[str] = Field(min_length=10)
    execution_argv: list[str] = Field(min_length=10)
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

    @model_validator(mode="after")
    def _argv_proves_profile(self) -> AbCodexCommandPlan:
        if _codex_profile_from_argv(self.command_argv) != self.codex_profile:
            raise ValueError("Codex command argv profile must match codex_profile")
        _validate_execution_argv(self.execution_argv, self.command_argv, self.codex_profile)
        if self.command_argv.count("--ask-for-approval") != 1 or self.command_argv[self.command_argv.index("--ask-for-approval") + 1] != self.approval_policy:
            raise ValueError("Codex command argv must prove the declared approval policy")
        validate_argv_output_last_message_path(self.command_argv, self.output_last_message_path, message="Codex command argv must prove output_last_message_path")
        return self


class AbRuntimeProfilePlanGate(_SdkContractModel):
    order: Literal[1, 2]
    lane: Literal["oss-local", "oss-cloud"]
    codex_profile: Literal["oss-local", "oss-cloud"]
    judge_profile: EvalJudgeProfile
    status: Literal["planned", "blocked"]
    blockers: list[AbPreflightBlocker]
    preflight: AbLanePreflight
    command_plan: list[AbCodexCommandPlan] = Field(max_length=2)

    @model_validator(mode="after")
    def _gate_identity_matches(self) -> AbRuntimeProfilePlanGate:
        validate_plan_gate_identity(self)
        validate_plan_gate_packet(self)
        return self


class AbPlanReceipt(_SdkContractModel):
    schema_version: Literal["skills-sdk.ab-plan-receipt.v1"]
    schema_uri: Literal["https://agent-skills.local/schemas/skills-sdk/ab-plan-receipt.v1.schema.json"]
    status: Literal["planned", "blocked"]
    operation: Literal["ab_plan"]
    skill_a: AbSkillVariant | None
    skill_b: AbSkillVariant | None
    fixture: AbFixtureIdentity | None
    execution_profile: EvalExecutionProfile | None
    judge_profile: EvalJudgeProfile | None
    codex_profile: Literal["oss-local"] | None
    runtime_profile_gates: list[AbRuntimeProfilePlanGate] = Field(max_length=2)
    evidence_root: str | None = Field(default=None, min_length=1)
    experiment_id: str = Field(pattern=_EXPERIMENT_ID_PATTERN)
    command_variant_labels: list[Literal["A", "B"]] = Field(max_length=2)
    command_plan: list[AbCodexCommandPlan] = Field(max_length=2)
    secret_boundary: EvalSecretBoundary
    execution_boundary: Literal["codex_exec_sandbox"]
    judge_boundary: Literal["post_run_sanitized_evidence_only"]
    mutation_performed: Literal[False]
    network_accessed: bool
    provider_invoked: Literal[False]
    codex_exec_invoked: Literal[False]
    blockers: list[str]
    acceptance_trace: list[Literal["FR-003", "FR-008", "SA-003", "SA-004", "VP-021", "VP-022", "VP-030"]]
    agent_summary: str = Field(min_length=1)

    @model_validator(mode="after")
    def _status_matches_plan(self) -> AbPlanReceipt:
        if self.status == "planned":
            self._validate_planned_packet()
        else:
            self._validate_blocked_packet()
        return self

    def _validate_blocked_packet(self) -> None:
        if not self.blockers:
            raise ValueError("blocked A/B plan receipts must include blockers")
        if self.command_plan or self.command_variant_labels:
            raise ValueError("blocked A/B plan receipts cannot expose executable command packets")
        if any(gate.command_plan for gate in self.runtime_profile_gates):
            raise ValueError("blocked A/B runtime gates cannot expose executable command packets")
        if any(gate.status == "blocked" and not gate.blockers for gate in self.runtime_profile_gates):
            raise ValueError("blocked A/B runtime gates must carry typed blockers")
        if any(gate.status == "planned" and gate.blockers for gate in self.runtime_profile_gates):
            raise ValueError("planned A/B runtime gates must not carry blockers")

    def _validate_planned_packet(self) -> None:
        if self.blockers or not self._has_plan_evidence():
            raise ValueError("planned A/B receipts require complete evidence and no blockers")
        if not _exact_variant_labels(self.command_plan) or set(self.command_variant_labels) != {"A", "B"}:
            raise ValueError("planned A/B receipts require exact A/B command packets and labels")
        if [gate.lane for gate in self.runtime_profile_gates] != ["oss-local", "oss-cloud"]:
            raise ValueError("A/B plan must require ordered oss-local then oss-cloud gates")
        if any(gate.status != "planned" or not _exact_variant_labels(gate.command_plan) for gate in self.runtime_profile_gates):
            raise ValueError("planned A/B receipts require both command variants for every admitted runtime gate")
        if self.command_plan != self.runtime_profile_gates[0].command_plan:
            raise ValueError("top-level command plan must match the oss-local runtime gate")

    def _has_plan_evidence(self) -> bool:
        evidence = (self.skill_a, self.skill_b, self.fixture, self.execution_profile,
                    self.judge_profile, self.codex_profile, self.evidence_root, self.experiment_id)
        return all(item is not None for item in evidence)


class AbVariantRunResult(_SdkContractModel):
    variant_label: Literal["A", "B"]
    codex_profile: Literal["oss-local", "oss-cloud"] | None
    status: Literal["pass", "blocked"]
    exit_code: int
    command_argv: list[str] = Field(min_length=10)
    execution_argv: list[str] | None = Field(default=None, min_length=10)
    sandbox_mode: Literal["read-only", "workspace-write"]
    prompt_stdin_path: str = Field(min_length=1)
    prompt_stdin_digest: str = Field(min_length=71)
    runner_stdout_capture_path: str = Field(min_length=1)
    runner_stdout_digest: str = Field(min_length=71)
    runner_stderr_capture_path: str = Field(min_length=1)
    runner_stderr_digest: str = Field(min_length=71)
    output_last_message_path: str = Field(min_length=1)
    output_last_message_digest: str | None = Field(default=None, min_length=71)
    semantic_output_excerpt: str | None = Field(default=None, min_length=1)
    blockers: list[str]

    @model_validator(mode="after")
    def _status_matches_blockers(self) -> AbVariantRunResult:
        if self.execution_argv is None:
            if self.status == "pass" or not any("executed_argv_missing" in blocker for blocker in self.blockers) or self.codex_profile is not None:
                raise ValueError("blocked A/B results must carry executed_argv_missing and no Codex profile")
        else:
            if _codex_profile_from_argv(self.command_argv) != self.codex_profile:
                raise ValueError("executed Codex argv profile must match codex_profile")
            _validate_execution_argv(self.execution_argv, self.command_argv, self.codex_profile)
        if self.command_argv.count("--ask-for-approval") != 1 or self.command_argv[self.command_argv.index("--ask-for-approval") + 1] != "on-request":
            raise ValueError("executed Codex argv must prove on-request approval")
        validate_argv_output_last_message_path(self.command_argv, self.output_last_message_path, message="executed Codex argv must prove output_last_message_path")
        if bool(self.blockers) != (self.status == "blocked"):
            raise ValueError("A/B variant blocker status is inconsistent")
        return self


def _validate_execution_argv(execution_argv: list[str], command_argv: list[str], codex_profile: str) -> None:
    if codex_profile == "oss-local":
        if execution_argv != command_argv:
            raise ValueError("local execution argv must equal the Codex command argv")
        return
    if len(execution_argv) < len(command_argv) + 5:
        raise ValueError("cloud execution argv must include the approved op run wrapper")
    if not _is_approved_op_binary(execution_argv[0]):
        raise ValueError("cloud execution argv must invoke the approved op binary")
    if execution_argv[1:5] != ["run", "--env-file", execution_argv[3], "--"] or execution_argv[3] != "<operator-approved-opaque-env-stream>":
        raise ValueError("cloud execution argv must use op run --env-file <opaque> --")
    if execution_argv[5:] != command_argv:
        raise ValueError("cloud execution argv must preserve the canonical Codex command argv")
    if _codex_profile_from_argv(execution_argv[5:]) != codex_profile:
        raise ValueError("executed Codex argv profile must match codex_profile")


class AbRuntimeProfileRunGate(_SdkContractModel):
    order: Literal[1, 2]
    lane: Literal["oss-local", "oss-cloud"]
    codex_profile: Literal["oss-local", "oss-cloud"]
    status: Literal["completed", "blocked", "not_run_with_reason"]
    blockers: list[str | AbPreflightBlocker]
    preflight: AbLanePreflight
    command_plan: list[AbCodexCommandPlan] = Field(max_length=2)
    variant_results: list[AbVariantRunResult] = Field(max_length=2)

    @model_validator(mode="after")
    def _gate_status_matches(self) -> AbRuntimeProfileRunGate:
        expected_order = 1 if self.lane == "oss-local" else 2
        if self.lane != self.codex_profile or self.order != expected_order:
            raise ValueError("runtime run gate identity or order is invalid")
        if self.status == "completed" and not self._is_completed_gate():
            raise ValueError("completed runtime gate requires both variants and no blockers")
        if self.status != "completed" and not self.blockers:
            raise ValueError("blocked/not-run runtime gate requires a reason")
        if self.status == "not_run_with_reason" and self.variant_results:
            raise ValueError("not-run runtime gate cannot include variant results")
        if any(result.codex_profile not in {None, self.codex_profile} for result in self.variant_results):
            raise ValueError("runtime result profile mismatch")
        return self

    def _is_completed_gate(self) -> bool:
        return run_gate_is_completed(self)


class AbRunReceipt(_SdkContractModel):
    schema_version: Literal["skills-sdk.ab-run-receipt.v1"]
    schema_uri: Literal["https://agent-skills.local/schemas/skills-sdk/ab-run-receipt.v1.schema.json"]
    status: Literal["completed", "blocked"]
    operation: Literal["ab_run"]
    skill_a: AbSkillVariant | None
    skill_b: AbSkillVariant | None
    fixture: AbFixtureIdentity | None
    execution_profile: EvalExecutionProfile | None
    judge_profile: EvalJudgeProfile | None
    codex_profile: Literal["oss-local"]
    runtime_profile_gates: list[AbRuntimeProfileRunGate] = Field(max_length=2)
    evidence_root: str | None = Field(default=None, min_length=1)
    experiment_id: str = Field(pattern=_EXPERIMENT_ID_PATTERN)
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
    timeout: DurationValue
    blockers: list[str]
    acceptance_trace: list[
        Literal["FR-003", "FR-008", "SA-003", "SA-004", "VP-021", "VP-022", "VP-030"]
    ] = Field(min_length=1)
    agent_summary: str = Field(min_length=1)

    @model_validator(mode="after")
    def _status_matches_run(self) -> AbRunReceipt:
        validate_run_receipt_status(self)
        return self


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
    semantic_output_excerpt: str = Field(min_length=1)
    blockers: list[str]


class AbJudgeComparisonPayload(_SdkContractModel):
    schema_version: Literal["skills-sdk.ab-judge-decision.v0"]
    experiment_id: str = Field(pattern=_EXPERIMENT_ID_PATTERN)
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
        "https://agent-skills.local/schemas/skills-sdk/ab-judge-preview-receipt.v0.schema.json"
    ]
    status: Literal["preview", "blocked"]
    operation: Literal["ab_judge_preview"]
    run_receipt_path: str | None = Field(default=None, min_length=1)
    run_receipt_digest: str | None = Field(default=None, min_length=71)
    experiment_id: str | None = Field(default=None, pattern=_EXPERIMENT_ID_PATTERN)
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


class AbJudgeDimensionScore(_SdkContractModel):
    dimension_id: str = Field(min_length=1)
    skill_a_score: Annotated[float, Field(ge=0, le=5)]
    skill_b_score: Annotated[float, Field(ge=0, le=5)]
    reason: str = Field(min_length=1)
    evidence_refs: list[str] = Field(min_length=1)

    @field_validator("dimension_id")
    @classmethod
    def _dimension_id_canonical(cls, value: str) -> str:
        if value not in _AB_JUDGE_DIMENSION_IDS:
            raise ValueError("judge dimension id must be canonical")
        return value

    @field_validator("evidence_refs")
    @classmethod
    def _evidence_refs_non_empty(cls, value: list[str]) -> list[str]:
        if any(not item for item in value):
            raise ValueError("judge dimension evidence refs must be non-empty")
        return value


class AbJudgeDecision(_SdkContractModel):
    schema_version: Literal["skills-sdk.ab-judge-decision.v0"]
    experiment_id: str = Field(pattern=_EXPERIMENT_ID_PATTERN)
    dimension_scores: list[AbJudgeDimensionScore] = Field(min_length=5, max_length=5)
    normalized_score_a: Annotated[float, Field(ge=0, le=1)]
    normalized_score_b: Annotated[float, Field(ge=0, le=1)]
    winner: Literal["skill_a", "skill_b", "inconclusive"]
    confidence: Literal["low", "medium", "high"]
    reason: str = Field(min_length=1)
    evidence_refs: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def _decision_has_canonical_dimensions(self) -> AbJudgeDecision:
        if {row.dimension_id for row in self.dimension_scores} != _AB_JUDGE_DIMENSION_IDS:
            raise ValueError("A/B judge decisions must score every canonical dimension exactly once")
        if any(not item for item in self.evidence_refs):
            raise ValueError("judge decision evidence refs must be non-empty")
        return self


class AbJudgeScoreReceipt(_SdkContractModel):
    schema_version: Literal["skills-sdk.ab-judge-score-receipt.v0"]
    schema_uri: Literal[
        "https://agent-skills.local/schemas/skills-sdk/ab-judge-score-receipt.v0.schema.json"
    ]
    status: Literal["scored", "blocked"]
    operation: Literal["ab_judge_score"]
    run_receipt_path: str | None = Field(default=None, min_length=1)
    run_receipt_digest: str | None = Field(default=None, min_length=71)
    experiment_id: str | None = Field(default=None, pattern=_EXPERIMENT_ID_PATTERN)
    judge_profile: EvalJudgeProfile | None
    rubric_id: Literal["skills-sdk.ab-rubric.v0"] | None
    rubric_digest: str | None = Field(default=None, min_length=71)
    decision_schema_version: Literal["skills-sdk.ab-judge-decision.v0"]
    allowed_winners: list[Literal["skill_a", "skill_b", "inconclusive"]] = Field(min_length=3, max_length=3)
    judge_prompt_digest: str | None = Field(default=None, min_length=71)
    judge_output_path: str | None = Field(default=None, min_length=1)
    judge_output_digest: str | None = Field(default=None, min_length=71)
    judge_command_argv: list[str]
    codex_profile: Literal["oss-local", "oss-local-code", "oss-local-fallback", "oss-security", "oss-cloud"] | None
    codex_exec_invoked: bool
    decision: AbJudgeDecision | None
    calibration_required: Literal[True]
    advisory_only: Literal[True]
    provider_invoked: bool
    network_accessed: bool
    mutation_performed: bool
    blockers: list[str]
    acceptance_trace: list[
        Literal["FR-003", "FR-008", "SA-003", "SA-004", "VP-021", "VP-022", "VP-030"]
    ] = Field(min_length=1)
    agent_summary: str = Field(min_length=1)

    @model_validator(mode="after")
    def _status_matches_score(self) -> AbJudgeScoreReceipt:
        if not _exact_decision_labels(self.allowed_winners):
            raise ValueError("A/B judge score receipts must contain exact winner labels")
        if self.status == "scored":
            self._validate_scored_receipt()
        elif not self.blockers:
            raise ValueError("blocked A/B judge score receipts must include blockers")
        return self

    def _validate_scored_receipt(self) -> None:
        if self.blockers:
            raise ValueError("scored A/B judge receipts must not include blockers")
        if not self._has_score_evidence():
            raise ValueError("scored A/B judge receipts must include complete score evidence")
        if not (self.provider_invoked and self.network_accessed and self.mutation_performed and self.codex_exec_invoked):
            raise ValueError("scored A/B judge receipts must report provider side effects")
        try:
            # v0 judge receipts predate the explicit approval-policy argv contract.
            # Keep them readable while all newly planned/executed v1 lanes remain
            # strict through their plan/run validators and runner evidence.
            executed_profile = _codex_profile_from_judge_argv(
                self.judge_command_argv,
                require_approval=False,
            )
        except ValueError as exc:
            raise ValueError("scored A/B judge receipts must prove profile in executed Codex argv") from exc
        if self.codex_profile != executed_profile:
            raise ValueError("scored A/B judge receipts must derive Codex profile from executed argv")
        if self.codex_profile != self.judge_profile.codex_profile:
            raise ValueError("scored A/B judge receipts must bind intended judge profile to executed profile")
        self._validate_decision_consistency()

    def _validate_decision_consistency(self) -> None:
        if self.decision is None:
            return
        if self.decision.experiment_id != self.experiment_id:
            raise ValueError("scored A/B judge receipts must bind decision to receipt experiment")
        computed_scores = _computed_judge_scores(self.decision.dimension_scores)
        if not _judge_scores_match(self.decision, computed_scores):
            raise ValueError("scored A/B judge receipts must match normalized rubric scores")
        if self.decision.winner != _expected_judge_winner(self.decision, computed_scores):
            raise ValueError("scored A/B judge receipts must match rubric winner policy")

    def _has_score_evidence(self) -> bool:
        return all(
            item is not None
            for item in (
                self.run_receipt_path,
                self.run_receipt_digest,
                self.experiment_id,
                self.judge_profile,
                self.rubric_id,
                self.rubric_digest,
                self.judge_prompt_digest,
                self.judge_output_path,
                self.judge_output_digest,
                self.judge_command_argv,
                self.codex_profile,
                self.decision,
            )
        )
