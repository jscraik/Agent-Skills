from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class _HandoffReadinessModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class HandoffReadinessCheck(_HandoffReadinessModel):
    id: str = Field(min_length=1)
    status: Literal["pass", "blocker"]
    severity: Literal["blocker"]
    message: str = Field(min_length=1)
    evidence: list[str]


HandoffReadinessLaneId = Literal[
    "mechanical_validation",
    "security_risk_modes",
    "scenario_quality",
    "scorer_quality",
    "scorer_calibration",
    "deterministic_local_gates",
    "oss-local",
    "oss-cloud",
    "tessl-local-proof",
    "tessl-live-dry-run",
]

REQUIRED_HANDOFF_LANE_IDS: tuple[HandoffReadinessLaneId, ...] = (
    "mechanical_validation",
    "security_risk_modes",
    "scenario_quality",
    "scorer_quality",
    "scorer_calibration",
    "deterministic_local_gates",
    "oss-local",
    "oss-cloud",
    "tessl-local-proof",
    "tessl-live-dry-run",
)


class HandoffReadinessLane(_HandoffReadinessModel):
    id: HandoffReadinessLaneId
    status: Literal["pass", "blocked", "skip"] | None = None
    declared_status: str | None = None
    command: str | None = None
    receipt_path: str | None = None
    blocker: str | None = None
    checks: list[HandoffReadinessCheck] = Field(min_length=1)
    blockers: list[HandoffReadinessCheck]

    @model_validator(mode="after")
    def _passed_lanes_have_evidence(self) -> "HandoffReadinessLane":
        if self.status == "pass" and (not self.command or not self.receipt_path):
            raise ValueError("passed lanes must include command and receipt_path")
        if self.status in {"blocked", "skip"} and not self.blocker:
            raise ValueError("blocked or skipped lanes must include blocker")
        return self


class HandoffReadinessTesslScoreSummary(_HandoffReadinessModel):
    status: str | None = None
    blocker_class: str | None = None
    feedback_loop_status: str | None = None
    regression_count: int | None = Field(default=None, ge=0)
    usage_percent: int | float | None = None
    baseline_percent: int | float | None = None
    scenario_count: int | None = Field(default=None, ge=0)


class HandoffReadinessCandidate(_HandoffReadinessModel):
    source_path: str = Field(min_length=1)
    candidate_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    scenario_set_digest: str = Field(pattern=r"^[a-f0-9]{64}$")


class HandoffReadinessReceipt(_HandoffReadinessModel):
    schema_version: Literal["skills-sdk.eval-handoff-readiness.v1"]
    schema_uri: Literal[
        "https://agent-skills.local/schemas/skills-sdk/eval-handoff-readiness.v1.schema.json"
    ]
    status: Literal["preview", "blocked"]
    operation: Literal["eval_handoff_readiness_preview"]
    query: str = Field(min_length=1)
    skill_path: str = Field(min_length=1)
    candidate: HandoffReadinessCandidate
    readiness_path: str = Field(min_length=1)
    tessl_score_path: str | None = None
    tessl_score_summary: HandoffReadinessTesslScoreSummary | None = None
    required_lanes: list[HandoffReadinessLaneId]
    required_order: list[str] = Field(min_length=9)
    lanes: list[HandoffReadinessLane] = Field(min_length=5)
    quality_checks: list[HandoffReadinessCheck] = Field(min_length=1)
    blockers: list[HandoffReadinessCheck]
    next_gate_allowed: bool
    blocked_next_gates: list[str]
    ready_for_live_tessl: bool
    required_next_actions: list[str]
    mutation_performed: Literal[False]
    promotion_performed: Literal[False]
    agent_summary: str = Field(min_length=1)

    @model_validator(mode="after")
    def _status_matches_readiness(self) -> "HandoffReadinessReceipt":
        lane_ids = [lane.id for lane in self.lanes]
        if lane_ids != self.required_lanes:
            raise ValueError("lane order must match required_lanes")
        if tuple(self.required_lanes) != REQUIRED_HANDOFF_LANE_IDS:
            raise ValueError("required_lanes must include the complete current SDK handoff sequence")
        if self.status == "preview" and (self.blockers or not self.ready_for_live_tessl):
            raise ValueError("preview handoff readiness receipts must be ready and have no blockers")
        if self.status == "blocked" and self.ready_for_live_tessl:
            raise ValueError("blocked handoff readiness receipts must set ready_for_live_tessl false")
        return self


def validate_handoff_readiness_receipt(payload: object) -> HandoffReadinessReceipt:
    return HandoffReadinessReceipt.model_validate(payload)
