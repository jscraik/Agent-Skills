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
    required_receipts: list[Literal["package_digest_receipt", "eval_run_receipt"]] = Field(min_length=2)
    prompt_digest: str | None = Field(default=None, min_length=71)
    failure_summary: str | None = Field(default=None, min_length=1)
    gap_summary: str | None = Field(default=None, min_length=1)

    @field_validator("required_receipts")
    @classmethod
    def _require_both_receipts(
        cls,
        value: list[Literal["package_digest_receipt", "eval_run_receipt"]],
    ) -> list[Literal["package_digest_receipt", "eval_run_receipt"]]:
        if set(value) != {"package_digest_receipt", "eval_run_receipt"}:
            raise ValueError("required_receipts must include package_digest_receipt and eval_run_receipt")
        return value


class ObservabilityFeedbackReceipt(_ObservabilityModel):
    schema_version: Literal["skills-sdk.observability-feedback-receipt.v0"]
    schema_uri: Literal[
        "https://jscraik.local/agent-skills/schemas/skills-sdk/observability-feedback-receipt.v0.schema.json"
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
