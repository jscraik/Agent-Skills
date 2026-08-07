"""Pydantic contracts for post-run A/B judge evidence.

The lifecycle and plan/run models stay in ab_contracts; this module keeps
judge comparison models separate while importing their shared primitives.
"""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import Field, field_validator, model_validator

from ask.skills_sdk.ab_contracts import (
    AbRubricContract,
    EvalJudgeProfile,
    _SdkContractModel,
    _AB_JUDGE_DIMENSION_IDS,
    _EXPERIMENT_ID_PATTERN,
    _codex_profile_from_judge_argv,
    _computed_judge_scores,
    _exact_decision_labels,
    _expected_judge_winner,
    _judge_scores_match,
)


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
    judge_command_shape: list[str] | None = None
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
