from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class _ScenarioQualityModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class ScenarioQualityCheck(_ScenarioQualityModel):
    id: str = Field(min_length=1)
    status: Literal["pass", "blocker"]
    severity: Literal["blocker"]
    message: str = Field(min_length=1)
    evidence: list[str]


class ScenarioQualityRow(_ScenarioQualityModel):
    id: str = Field(min_length=1)
    category: str = Field(min_length=1)
    realistic: bool
    promotion_status: Literal["promotion_ready", "blocked_quality_gate"]
    checks: list[ScenarioQualityCheck] = Field(min_length=1)
    blockers: list[ScenarioQualityCheck]


class ScenarioSetParity(_ScenarioQualityModel):
    canonical_count: int = Field(ge=0)
    reviewed_fixture_count: int = Field(ge=0)
    staged_tessl_count: int | None = Field(default=None, ge=0)
    score_receipt_path_count: int | None = Field(default=None, ge=0)
    score_receipt_declared_count: int | None = Field(default=None, ge=0)
    missing_from_staged: list[str]
    extra_in_staged: list[str]
    missing_from_score_receipt: list[str]
    extra_in_score_receipt: list[str]


class ScenarioQualityReceipt(_ScenarioQualityModel):
    schema_version: Literal["skills-sdk.scenario-quality-receipt.v0"]
    schema_uri: Literal[
        "https://agent-skills.local/schemas/skills-sdk/scenario-quality-receipt.v0.schema.json"
    ]
    status: Literal["preview", "blocked"]
    operation: Literal["scenario_quality_preview"]
    query: str = Field(min_length=1)
    skill_path: str = Field(min_length=1)
    evals_path: str = Field(min_length=1)
    scenario_count: int = Field(ge=0)
    promotion_ready_count: int = Field(ge=0)
    blocked_count: int = Field(ge=0)
    scenario_set_parity: ScenarioSetParity | None = None
    scenario_rows: list[ScenarioQualityRow]
    quality_checks: list[ScenarioQualityCheck] = Field(min_length=1)
    blockers: list[ScenarioQualityCheck]
    mutation_performed: Literal[False]
    promotion_performed: Literal[False]
    acceptance_trace: list[Literal["PU-030", "FR-003", "FR-008", "SA-003", "VP-030"]] = Field(min_length=1)
    agent_summary: str = Field(min_length=1)


def validate_scenario_quality_receipt(payload: object) -> ScenarioQualityReceipt:
    return ScenarioQualityReceipt.model_validate(payload)
