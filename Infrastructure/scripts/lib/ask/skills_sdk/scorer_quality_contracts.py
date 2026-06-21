from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class _ScorerQualityModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class ScorerQualityCheck(_ScorerQualityModel):
    id: str = Field(min_length=1)
    status: Literal["pass", "blocker"]
    severity: Literal["blocker"]
    message: str = Field(min_length=1)
    evidence: list[Annotated[str, Field(min_length=1)]]


class ScorerQualityBlockerCheck(ScorerQualityCheck):
    status: Literal["blocker"]


class ScorerQualityParameters(_ScorerQualityModel):
    model: str = Field(min_length=1)
    temperature: int | float
    trial_count: int = Field(ge=1)


class ScorerQualityRationaleAudit(_ScorerQualityModel):
    required: bool
    sampled_count: int = Field(ge=0)


class ScorerQualityCalibrationCase(_ScorerQualityModel):
    id: str = Field(min_length=1)
    probe_type: Literal[
        "obvious_correct",
        "obvious_wrong",
        "short_correct_vs_verbose_wrong",
        "rubric_copying_rejected",
        "skill_name_mention_not_enough",
        "evidence_lane_overclaim_rejected",
    ]
    expected_score: int | float | None = None
    expected_label: Literal["pass", "fail"] | None = None
    expected_direction: Literal["short_correct_wins"] | None = None

    @model_validator(mode="after")
    def _expected_outcome_required(self) -> ScorerQualityCalibrationCase:
        if self.expected_score is None and self.expected_label is None and self.expected_direction is None:
            raise ValueError("calibration cases must include expected_score, expected_label, or expected_direction")
        return self


class ScorerQualityMetadata(_ScorerQualityModel):
    schema_version: Literal["skills-sdk.scorer-quality.v1"]
    scorer_id: str = Field(min_length=1)
    scorer_type: Literal["deterministic", "llm_judge", "hybrid", "external_tessl"]
    scope: Literal["span", "trace", "suite"]
    scorer_version_or_digest: str = Field(min_length=1)
    pass_threshold: float = Field(gt=0, le=1)
    deterministic_checks_first: Literal[True]
    parameters: ScorerQualityParameters | None = None
    rationale_audit: ScorerQualityRationaleAudit | None = None
    bias_probes: list[Literal["short_correct_vs_verbose_wrong", "verbosity_bias"]] = Field(default_factory=list)
    segmentation_fields: list[Literal["category", "claim_ids", "eval_modes"]] = Field(min_length=3)
    calibration_cases: list[ScorerQualityCalibrationCase] = Field(min_length=1)

    @model_validator(mode="after")
    def _judge_metadata_required(self) -> ScorerQualityMetadata:
        if self.scorer_type in {"llm_judge", "hybrid", "external_tessl"}:
            if self.parameters is None:
                raise ValueError("LLM-like scorers must include judge parameters")
            if self.rationale_audit is None:
                raise ValueError("LLM-like scorers must include rationale_audit")
        return self


class ScorerQualityReceipt(_ScorerQualityModel):
    schema_version: Literal["skills-sdk.scorer-quality-receipt.v0"]
    schema_uri: Literal[
        "https://jscraik.local/agent-skills/schemas/skills-sdk/scorer-quality-receipt.v0.schema.json"
    ]
    status: Literal["preview", "blocked"]
    operation: Literal["scorer_quality_preview"]
    query: str = Field(min_length=1)
    skill_path: str = Field(min_length=1)
    evals_path: str = Field(min_length=1)
    ready: bool
    quality_checks: list[ScorerQualityCheck] = Field(min_length=1)
    blockers: list[ScorerQualityBlockerCheck]
    mutation_performed: Literal[False]
    promotion_performed: Literal[False]
    acceptance_trace: list[Literal["Braintrust scorer validation", "PU-030", "VP-030"]] = Field(min_length=1)
    agent_summary: str = Field(min_length=1)

    @model_validator(mode="after")
    def _status_matches_blockers(self) -> ScorerQualityReceipt:
        if self.status == "preview" and (self.blockers or not self.ready):
            raise ValueError("preview scorer-quality receipts must be ready and have no blockers")
        if self.status == "blocked" and self.ready:
            raise ValueError("blocked scorer-quality receipts must set ready false")
        return self


def validate_scorer_quality_metadata(payload: object) -> ScorerQualityMetadata:
    return ScorerQualityMetadata.model_validate(payload)


def validate_scorer_quality_receipt(payload: object) -> ScorerQualityReceipt:
    return ScorerQualityReceipt.model_validate(payload)
