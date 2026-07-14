from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

from ask.skills_sdk.ab_contracts import (
    AbFixtureIdentity,
    AbSkillVariant,
    EvalExecutionProfile,
    EvalJudgeProfile,
    EvalSecretBoundary,
)


class _SdkContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


LegacySeconds = Annotated[int, Field(ge=1)]
_EXPERIMENT_ID_PATTERN = r"^(?:ex_[a-z0-9]{16}|[0-9a-f]{16})$"


class AbCodexCommandPlanV0(_SdkContractModel):
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


class AbPlanReceiptV0(_SdkContractModel):
    schema_version: Literal["skills-sdk.ab-plan-receipt.v0"]
    schema_uri: Literal["https://agent-skills.local/schemas/skills-sdk/ab-plan-receipt.v0.schema.json"]
    status: Literal["planned", "blocked"]
    operation: Literal["ab_plan"]
    skill_a: AbSkillVariant | None
    skill_b: AbSkillVariant | None
    fixture: AbFixtureIdentity | None
    execution_profile: EvalExecutionProfile | None
    judge_profile: EvalJudgeProfile | None
    evidence_root: str | None = Field(default=None, min_length=1)
    experiment_id: str | None = Field(default=None, pattern=_EXPERIMENT_ID_PATTERN)
    command_variant_labels: list[Literal["A", "B"]] = Field(max_length=2)
    command_plan: list[AbCodexCommandPlanV0] = Field(max_length=2)
    secret_boundary: EvalSecretBoundary
    execution_boundary: Literal["codex_exec_sandbox"]
    judge_boundary: Literal["post_run_sanitized_evidence_only"]
    mutation_performed: Literal[False]
    network_accessed: Literal[False]
    provider_invoked: Literal[False]
    codex_exec_invoked: Literal[False]
    blockers: list[str]
    acceptance_trace: list[Literal["FR-003", "FR-008", "SA-003", "SA-004", "VP-021", "VP-022", "VP-030"]]
    agent_summary: str = Field(min_length=1)


class AbVariantRunResultV0(_SdkContractModel):
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
    semantic_output_excerpt: str | None = Field(default=None, min_length=1)
    blockers: list[str]


class AbRunReceiptV0(_SdkContractModel):
    schema_version: Literal["skills-sdk.ab-run-receipt.v0"]
    schema_uri: Literal["https://agent-skills.local/schemas/skills-sdk/ab-run-receipt.v0.schema.json"]
    status: Literal["completed", "blocked"]
    operation: Literal["ab_run"]
    skill_a: AbSkillVariant | None
    skill_b: AbSkillVariant | None
    fixture: AbFixtureIdentity | None
    execution_profile: EvalExecutionProfile | None
    judge_profile: EvalJudgeProfile | None
    evidence_root: str | None = Field(default=None, min_length=1)
    experiment_id: str | None = Field(default=None, pattern=_EXPERIMENT_ID_PATTERN)
    command_variant_labels: list[Literal["A", "B"]] = Field(max_length=2)
    command_plan: list[AbCodexCommandPlanV0] = Field(max_length=2)
    variant_results: list[AbVariantRunResultV0] = Field(max_length=2)
    secret_boundary: EvalSecretBoundary
    execution_boundary: Literal["codex_exec_sandbox"]
    judge_boundary: Literal["post_run_sanitized_evidence_only"]
    mutation_performed: bool
    network_accessed: bool
    provider_invoked: bool
    judge_provider_invoked: Literal[False]
    codex_exec_invoked: bool
    timeout_seconds: LegacySeconds
    blockers: list[str]
    acceptance_trace: list[Literal["FR-003", "FR-008", "SA-003", "SA-004", "VP-021", "VP-022", "VP-030"]]
    agent_summary: str = Field(min_length=1)
