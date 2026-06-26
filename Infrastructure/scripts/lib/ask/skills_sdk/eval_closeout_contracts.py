from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class EvalCloseoutContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class EvalCloseoutValidationCheck(EvalCloseoutContractModel):
    id: str = Field(min_length=1)
    status: Literal["pass", "blocker"]
    message: str = Field(min_length=1)
    evidence: list[str]


class EvalCloseoutValidation(EvalCloseoutContractModel):
    schema_version: Literal["skills-sdk.eval-closeout-validation.v1"]
    status: Literal["pass", "blocked"]
    checks: list[EvalCloseoutValidationCheck]
    blockers: list[EvalCloseoutValidationCheck]
