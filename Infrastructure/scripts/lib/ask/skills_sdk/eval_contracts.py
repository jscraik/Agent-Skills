from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class _EvalContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class EvalQualityAssertion(_EvalContractModel):
    id: str = Field(min_length=1)
    status: Literal["pass", "fail"]
    expected: str = Field(min_length=1)
    actual: str


class EvalExpectedSignalSummary(_EvalContractModel):
    runs: int = Field(ge=0)
    average: float | None
    minimum: float | None
    risky_cases: list[str]


class EvalQualityGates(_EvalContractModel):
    source: Literal["internal_scorecard"]
    scorecard_schema_version: str | None
    decision: str | None
    passed: bool | None
    promotion_eligible: bool | None
    blocked_cases: int = Field(ge=0)
    tier1_failures: int = Field(ge=0)
    tier2_findings: int = Field(ge=0)
    preflight_warning_count: int = Field(ge=0)
    readiness_summary: dict[str, int]
    expected_signal_summary: EvalExpectedSignalSummary
    security_dependency_screening_status: str | None
    assertions: list[EvalQualityAssertion] = Field(min_length=1)
    failed_assertions: list[str]
