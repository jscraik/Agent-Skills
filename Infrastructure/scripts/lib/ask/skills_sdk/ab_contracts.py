from __future__ import annotations

import math
from typing import Any, Annotated, Literal

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
    OSS_CLOUD_REQUIRED_ENV,
    configs_oss_cloud_exec_command as _configs_oss_cloud_exec_command,
    configs_oss_local_exec_command as _configs_oss_local_exec_command,
    is_configs_auth_wrapper as _is_configs_auth_wrapper,
    is_configs_codex_exec_wrapper as _is_configs_codex_exec_wrapper,
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


def _validate_runtime_gate_sequence(execution_lane: str, gates: list[Any], *, message: str) -> None:
    expected_lanes = ["oss-local", "oss-cloud"] if execution_lane == "all" else [execution_lane]
    expected_orders = list(range(1, len(expected_lanes) + 1))
    if ([gate.lane for gate in gates] != expected_lanes
            or [gate.order for gate in gates] != expected_orders):
        raise ValueError(message)


def _codex_profile_from_argv(argv: list[str]) -> str:
    if len(argv) < 4 or argv[:3] != ["codex", "exec", "--profile"]:
        raise ValueError("Codex argv must start with the installed CLI placement: codex exec --profile")
    if argv.count("--profile") != 1:
        raise ValueError("Codex argv must contain exactly one --profile option")
    profile = argv[3]
    if profile not in {"oss-local", "oss-cloud"}:
        raise ValueError("Codex argv profile must be an admitted Skills SDK runtime profile")
    return profile


def _argv_proves_approval(argv: list[str], expected: str = "on-request") -> bool:
    legacy = [
        argv[index + 1]
        for index, value in enumerate(argv[:-1])
        if value == "--ask-for-approval"
    ]
    config = [
        argv[index + 1]
        for index, value in enumerate(argv[:-1])
        if value == "-c" and argv[index + 1].startswith("approval_policy=")
    ]
    return (legacy == [expected] and not config) or (
        not legacy and config == [f'approval_policy="{expected}"']
    )


def _codex_profile_from_judge_argv(argv: list[str], *, require_approval: bool = True) -> str:
    if _is_configs_judge_argv(argv):
        profile = argv[10]
        if profile not in _JUDGE_PROFILES:
            raise ValueError("judge Codex argv profile must be an admitted runtime profile")
        _validate_configs_judge_argv(argv, require_approval)
        return profile
    try:
        codex_index = _judge_codex_index(argv)
        profile = _judge_profile_token(argv, codex_index)
        _validate_judge_argv(argv, codex_index, require_approval)
    except (IndexError, ValueError) as exc:
        raise ValueError("judge Codex argv must contain an ordered profile option") from exc
    if profile not in _JUDGE_PROFILES:
        raise ValueError("judge Codex argv profile must be an admitted runtime profile")
    return profile


def _is_configs_judge_argv(argv: list[str]) -> bool:
    return (
        len(argv) >= 12
        and argv[0] == "bash"
        and _is_configs_auth_wrapper(argv[1])
        and argv[2] == "--env-file"
        and _is_opaque_env_reference(argv[3])
        and argv[4:7] == ["--require-env", OSS_CLOUD_REQUIRED_ENV, "--"]
        and argv[7] == "bash"
        and _is_configs_codex_exec_wrapper(argv[8])
        and argv[9] == "--profile"
    )


def _validate_configs_judge_argv(argv: list[str], require_approval: bool) -> None:
    if argv.count("--profile") != 1 or argv[10] != "oss-cloud":
        raise ValueError("Configs judge argv must use exactly the oss-cloud profile")
    if argv.count("--strict-config") != 1 or argv.count("--ephemeral") != 1:
        raise ValueError("Configs judge argv must use strict disposable cloud execution")
    sandbox_values = [
        argv[index + 1]
        for index, value in enumerate(argv[:-1])
        if value == "--sandbox"
    ]
    if sandbox_values != ["read-only"]:
        raise ValueError("Configs judge argv must use read-only sandboxing")
    if require_approval:
        approval_values = [
            argv[index + 1]
            for index, value in enumerate(argv[:-1])
            if value == "-c"
        ]
        if approval_values.count('approval_policy="on-request"') != 1:
            raise ValueError("Configs judge argv must prove the on-request approval policy")


_JUDGE_PROFILES = ("oss-local", "oss-local-code", "oss-local-fallback", "oss-security", "oss-cloud")


def _judge_codex_index(argv: list[str]) -> int:
    if not argv:
        raise ValueError("empty argv")
    if argv[0] == "codex":
        return 0
    if (
        len(argv) >= 9
        and argv[0] == "bash"
        and _is_configs_auth_wrapper(argv[1])
        and argv[2] == "--env-file"
        and _is_opaque_env_reference(argv[3])
        and argv[4:7] == ["--require-env", OSS_CLOUD_REQUIRED_ENV, "--"]
    ):
        return 7
    raise ValueError("judge argv must use codex directly or the Configs auth-backed wrapper")


def _judge_profile_token(argv: list[str], codex_index: int) -> str:
    profile_index = argv.index("--profile", codex_index)
    return argv[profile_index + 1]


def _validate_judge_argv(argv: list[str], codex_index: int, require_approval: bool) -> None:
    profile_index = argv.index("--profile", codex_index)
    if argv[codex_index + 1] != "exec" or argv.count("--profile") != 1 or profile_index != codex_index + 2:
        raise ValueError("judge Codex argv must contain an ordered profile option")
    if require_approval and not _argv_proves_approval(argv[codex_index:]):
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
        if not _argv_proves_approval(self.command_argv, self.approval_policy):
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
    execution_lane: Literal["all", "oss-local", "oss-cloud"] = "all"
    codex_profile: Literal["oss-local", "oss-cloud"] | None
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
        if not _exact_variant_labels(self.command_plan) or self.command_variant_labels != ["A", "B"]:
            raise ValueError("planned A/B receipts require exact A/B command packets and labels")
        _validate_runtime_gate_sequence(
            self.execution_lane,
            self.runtime_profile_gates,
            message="A/B plan must preserve the declared execution lane order",
        )
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
        if not _argv_proves_approval(self.command_argv):
            raise ValueError("executed Codex argv must prove on-request approval")
        validate_argv_output_last_message_path(self.command_argv, self.output_last_message_path, message="executed Codex argv must prove output_last_message_path")
        if bool(self.blockers) != (self.status == "blocked"):
            raise ValueError("A/B variant blocker status is inconsistent")
        return self


def _validate_execution_argv(execution_argv: list[str], command_argv: list[str], codex_profile: str) -> None:
    if codex_profile == "oss-local":
        if execution_argv != command_argv and execution_argv != _configs_oss_local_exec_command(command_argv):
            raise ValueError("local execution argv must use the logical Codex command or Configs disposable executor")
        return
    expected_child = _configs_oss_cloud_exec_command(command_argv)
    if len(execution_argv) != len(expected_child) + 7:
        raise ValueError("cloud execution argv must include the Configs auth-backed wrapper")
    if execution_argv[0] != "bash" or not _is_configs_auth_wrapper(execution_argv[1]):
        raise ValueError("cloud execution argv must invoke the Configs auth-backed wrapper")
    if execution_argv[2:7] != ["--env-file", "<operator-approved-opaque-env-stream>", "--require-env", OSS_CLOUD_REQUIRED_ENV, "--"]:
        raise ValueError("cloud execution argv must use the Configs FIFO wrapper contract")
    if execution_argv[7:] != expected_child:
        raise ValueError("cloud execution argv must use the Configs strict executor contract")


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
        if self.lane != self.codex_profile or self.order not in {1, 2}:
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
    execution_lane: Literal["all", "oss-local", "oss-cloud"] = "all"
    codex_profile: Literal["oss-local", "oss-cloud"] | None
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


from ask.skills_sdk.ab_judge_contracts import (  # noqa: E402,F401
    AbJudgeComparisonPayload,
    AbJudgeDecision,
    AbJudgeDimensionScore,
    AbJudgeFixtureIdentity,
    AbJudgePackageIdentity,
    AbJudgePreviewReceipt,
    AbJudgeSanitizedVariantResult,
    AbJudgeScoreReceipt,
)
