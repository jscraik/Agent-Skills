from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class _RegressionPlanModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class RegressionPlanCheck(_RegressionPlanModel):
    id: str = Field(min_length=1)
    status: Literal["pass", "blocker"]
    severity: Literal["blocker"]
    message: str = Field(min_length=1)
    evidence: list[str]


class PatchPlanItem(_RegressionPlanModel):
    file: str = Field(min_length=1)
    change: str = Field(min_length=1)


class RetainedRegression(_RegressionPlanModel):
    status: Literal["retained", "imported"]
    path: str = Field(min_length=1)


class RegressionPlanRow(_RegressionPlanModel):
    scenario_id: str = Field(min_length=1)
    usage_score: int | float | None = None
    baseline_score: int | float | None = None
    max_score: int | float | None = None
    owner: Literal["skill", "task", "criteria", "scorer", "environment"] | None = None
    failure_mode: str | None = None
    patch_plan: list[PatchPlanItem]
    retained_regression: RetainedRegression | None = None
    validation_commands: list[str]
    checks: list[RegressionPlanCheck] = Field(min_length=1)
    blockers: list[RegressionPlanCheck]

    @model_validator(mode="after")
    def _status_matches_blockers(self) -> "RegressionPlanRow":
        if self.blockers:
            return self
        if self.owner is None or self.failure_mode is None or self.retained_regression is None:
            raise ValueError("unblocked regression rows must include owner, failure_mode, and retained_regression")
        if not self.patch_plan or not self.validation_commands:
            raise ValueError("unblocked regression rows must include patch_plan and validation_commands")
        return self


class RegressionPlanReceipt(_RegressionPlanModel):
    schema_version: Literal["skills-sdk.eval-regression-plan.v0"]
    schema_uri: Literal[
        "https://jscraik.local/agent-skills/schemas/skills-sdk/eval-regression-plan.v0.schema.json"
    ]
    status: Literal["preview", "blocked"]
    operation: Literal["eval_regression_plan_preview"]
    query: str = Field(min_length=1)
    skill_path: str = Field(min_length=1)
    view_json: str = Field(min_length=1)
    plan_path: str | None = None
    run_id: str = Field(min_length=1)
    source_score: dict[str, Any]
    regression_count: int = Field(ge=0)
    regressions: list[RegressionPlanRow]
    quality_checks: list[RegressionPlanCheck] = Field(min_length=1)
    blockers: list[RegressionPlanCheck]
    ready_for_live_rerun: bool
    required_next_actions: list[str]
    mutation_performed: Literal[False]
    promotion_performed: Literal[False]
    agent_summary: str = Field(min_length=1)

    @model_validator(mode="after")
    def _status_matches_readiness(self) -> "RegressionPlanReceipt":
        if self.status == "preview" and (self.blockers or not self.ready_for_live_rerun):
            raise ValueError("preview regression plans must be ready and have no blockers")
        if self.status == "blocked" and self.ready_for_live_rerun:
            raise ValueError("blocked regression plans must set ready_for_live_rerun false")
        return self


def validate_regression_plan_receipt(payload: object) -> RegressionPlanReceipt:
    return RegressionPlanReceipt.model_validate(payload)
