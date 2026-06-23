from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class _ObservabilityModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class FeedbackCheck(_ObservabilityModel):
    id: str = Field(min_length=1)
    status: Literal["pass", "blocker"]
    severity: Literal["blocker"]
    message: str = Field(min_length=1)
    evidence: list[str]


class FeedbackCandidate(_ObservabilityModel):
    id: str = Field(min_length=1)
    candidate_type: Literal["eval_scenario", "skill_gap"]
    source_event_digest: str = Field(min_length=71)
    skill_id: str = Field(min_length=1)
    promotion_status: Literal["blocked_pending_package_eval"]
    required_receipts: list[Literal["package_digest_receipt", "eval_run_receipt"]] = Field(
        min_length=2,
        max_length=2,
    )
    prompt_digest: str | None = Field(default=None, min_length=71)
    failure_summary: str | None = Field(default=None, min_length=1)
    gap_summary: str | None = Field(default=None, min_length=1)

    @field_validator("required_receipts")
    @classmethod
    def _require_both_receipts(
        cls,
        value: list[Literal["package_digest_receipt", "eval_run_receipt"]],
    ) -> list[Literal["package_digest_receipt", "eval_run_receipt"]]:
        if len(set(value)) != len(value) or set(value) != {"package_digest_receipt", "eval_run_receipt"}:
            raise ValueError("required_receipts must include package_digest_receipt and eval_run_receipt")
        return value


class ObservabilityFeedbackReceipt(_ObservabilityModel):
    schema_version: Literal["skills-sdk.observability-feedback-receipt.v0"]
    schema_uri: Literal[
        "https://agent-skills.local/schemas/skills-sdk/observability-feedback-receipt.v0.schema.json"
    ]
    status: Literal["preview", "blocked"]
    operation: Literal["observability_feedback_preview"]
    package_id: str = Field(min_length=1)
    package_digest: str = Field(min_length=71)
    events_path: str = Field(min_length=1)
    event_count: int = Field(ge=0)
    accepted_event_count: int = Field(ge=0)
    scenario_candidates: list[FeedbackCandidate]
    skill_gap_candidates: list[FeedbackCandidate]
    promotion_blockers: list[Literal["package_digest_receipt", "eval_run_receipt"]]
    feedback_checks: list[FeedbackCheck] = Field(min_length=1)
    blockers: list[FeedbackCheck]
    mutation_performed: Literal[False]
    acceptance_trace: list[Literal["PU-026", "FR-003", "FR-008", "SA-003", "VP-026"]] = Field(min_length=1)
    agent_summary: str = Field(min_length=1)


def validate_observability_feedback_receipt(payload: object) -> ObservabilityFeedbackReceipt:
    return ObservabilityFeedbackReceipt.model_validate(payload)


class PromotionCheck(_ObservabilityModel):
    id: str = Field(min_length=1)
    status: Literal["pass", "blocker"]
    severity: Literal["blocker"]
    message: str = Field(min_length=1)
    evidence: list[str]


class PromotionCandidateDecision(_ObservabilityModel):
    id: str = Field(min_length=1)
    candidate_type: Literal["eval_scenario", "skill_gap"]
    source_event_digest: str = Field(min_length=71)
    skill_id: str = Field(min_length=1)
    decision: Literal["promotion_ready", "blocked"]
    promotion_status: Literal["promotion_ready", "blocked_pending_package_eval"]
    required_receipts: list[Literal["package_digest_receipt", "eval_run_receipt"]] = Field(
        min_length=2,
        max_length=2,
    )
    evidence_refs: list[Literal["feedback_receipt", "package_digest_receipt", "eval_run_receipt"]] = Field(
        min_length=3,
        max_length=3,
    )
    blockers: list[str]

    @field_validator("required_receipts")
    @classmethod
    def _require_both_receipts(
        cls,
        value: list[Literal["package_digest_receipt", "eval_run_receipt"]],
    ) -> list[Literal["package_digest_receipt", "eval_run_receipt"]]:
        if len(set(value)) != len(value) or set(value) != {"package_digest_receipt", "eval_run_receipt"}:
            raise ValueError("required_receipts must include package_digest_receipt and eval_run_receipt")
        return value

    @field_validator("evidence_refs")
    @classmethod
    def _require_all_evidence_refs(
        cls,
        value: list[Literal["feedback_receipt", "package_digest_receipt", "eval_run_receipt"]],
    ) -> list[Literal["feedback_receipt", "package_digest_receipt", "eval_run_receipt"]]:
        expected = {"feedback_receipt", "package_digest_receipt", "eval_run_receipt"}
        if len(set(value)) != len(value) or set(value) != expected:
            raise ValueError("evidence_refs must include feedback, package, and eval receipts")
        return value


class ObservabilityPromotionReceipt(_ObservabilityModel):
    schema_version: Literal["skills-sdk.observability-promotion-receipt.v0"]
    schema_uri: Literal[
        "https://agent-skills.local/schemas/skills-sdk/observability-promotion-receipt.v0.schema.json"
    ]
    status: Literal["preview", "blocked"]
    operation: Literal["observability_promotion_preview"]
    package_id: str | None = Field(default=None, min_length=1)
    package_digest: str | None = Field(default=None, min_length=71)
    feedback_receipt_path: str | None = Field(default=None, min_length=1)
    feedback_receipt_digest: str | None = Field(default=None, min_length=71)
    package_receipt_path: str | None = Field(default=None, min_length=1)
    package_receipt_digest: str | None = Field(default=None, min_length=71)
    eval_run_receipt_path: str | None = Field(default=None, min_length=1)
    eval_run_receipt_digest: str | None = Field(default=None, min_length=71)
    candidate_count: int = Field(ge=0)
    promotion_ready_count: int = Field(ge=0)
    blocked_count: int = Field(ge=0)
    candidate_decisions: list[PromotionCandidateDecision]
    promotion_checks: list[PromotionCheck] = Field(min_length=1)
    blockers: list[PromotionCheck]
    mutation_performed: Literal[False]
    acceptance_trace: list[Literal["PU-026", "FR-003", "FR-008", "SA-003", "VP-026"]] = Field(min_length=1)
    agent_summary: str = Field(min_length=1)


def validate_observability_promotion_receipt(payload: object) -> ObservabilityPromotionReceipt:
    return ObservabilityPromotionReceipt.model_validate(payload)
