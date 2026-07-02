from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


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
    case_count: int = Field(ge=0)
    blocked_cases: int = Field(ge=0)
    tier1_failures: int = Field(ge=0)
    tier2_findings: int = Field(ge=0)
    preflight_warning_count: int = Field(ge=0)
    readiness_summary: dict[str, int]
    expected_signal_summary: EvalExpectedSignalSummary
    security_dependency_screening_status: str | None
    assertions: list[EvalQualityAssertion] = Field(min_length=1)
    failed_assertions: list[str]

    @field_validator("readiness_summary")
    @classmethod
    def _validate_readiness_summary_values(cls, v: dict[str, int]) -> dict[str, int]:
        """Ensure all readiness_summary values are non-negative integers."""
        for key, value in v.items():
            if value < 0:
                raise ValueError(f"readiness_summary values must be non-negative integers, got {value} for key {key}")
        return v

    @field_validator("failed_assertions")
    @classmethod
    def _validate_no_empty_strings(cls, v: list[str]) -> list[str]:
        """Ensure no empty strings in failed_assertions."""
        if any(assertion == "" for assertion in v):
            raise ValueError("failed_assertions must not contain empty strings")
        return v
