from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class _SkillIntakeModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class SkillIntakeFile(_SkillIntakeModel):
    path: str = Field(min_length=1)
    digest: str = Field(min_length=71)
    size_bytes: int = Field(ge=0)


class SkillIntakeCheck(_SkillIntakeModel):
    id: str = Field(min_length=1)
    status: Literal["pass", "blocker"]
    severity: Literal["blocker"]
    message: str = Field(min_length=1)
    evidence: list[str]


class SkillIntakeReceipt(_SkillIntakeModel):
    schema_version: Literal["skills-sdk.skill-intake-receipt.v0"]
    schema_uri: Literal[
        "https://jscraik.local/agent-skills/schemas/skills-sdk/skill-intake-receipt.v0.schema.json"
    ]
    status: Literal["preview", "blocked"]
    operation: Literal["skill_intake_inspect"]
    source_kind: Literal["directory", "archive"]
    source_path: str = Field(min_length=1)
    source_digest: str | None = Field(default=None, min_length=71)
    skill_id: str | None = Field(default=None, min_length=1)
    file_count: int = Field(ge=0)
    total_size_bytes: int = Field(ge=0)
    inspected_files: list[SkillIntakeFile]
    intake_checks: list[SkillIntakeCheck] = Field(min_length=1)
    blockers: list[SkillIntakeCheck]
    execution_performed: Literal[False]
    install_performed: Literal[False]
    projection_mutation_performed: Literal[False]
    network_accessed: Literal[False]
    mutation_performed: Literal[False]
    acceptance_trace: list[Literal["PU-032", "FR-008", "FR-010", "SA-004", "SEC-001", "VP-032"]] = Field(
        min_length=1
    )
    agent_summary: str = Field(min_length=1)


def validate_skill_intake_receipt(payload: object) -> SkillIntakeReceipt:
    return SkillIntakeReceipt.model_validate(payload)
