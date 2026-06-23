from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field


class _StaticExplorerModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


NonEmptyString = Annotated[str, Field(min_length=1)]
CapabilityStatus = Literal[
    "implemented",
    "preview_only",
    "placeholder_optional",
    "placeholder_blocked",
    "blocked_missing_adapter",
    "deferred",
    "out_of_scope",
]


class StaticExplorerCheck(_StaticExplorerModel):
    id: str = Field(min_length=1)
    status: Literal["pass", "blocker"]
    severity: Literal["blocker"]
    message: str = Field(min_length=1)
    evidence: list[NonEmptyString]


class CapabilityIndexRow(_StaticExplorerModel):
    id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    status: CapabilityStatus
    owner_surface: str = Field(min_length=1)


class SkillIndexRow(_StaticExplorerModel):
    id: str = Field(min_length=1)
    skill_set: str = Field(min_length=1)
    source_path: str = Field(min_length=1)


class StaticExplorerReceipt(_StaticExplorerModel):
    schema_version: Literal["skills-sdk.static-explorer-receipt.v0"]
    schema_uri: Literal[
        "https://agent-skills.local/schemas/skills-sdk/static-explorer-receipt.v0.schema.json"
    ]
    status: Literal["preview", "blocked"]
    operation: Literal["static_explorer_preview"]
    capability_count: int = Field(ge=0)
    skill_count: int = Field(ge=0)
    skill_sets: list[NonEmptyString]
    capability_index: list[CapabilityIndexRow]
    skill_index: list[SkillIndexRow]
    projection_inputs: list[str] = Field(min_length=1)
    explorer_checks: list[StaticExplorerCheck] = Field(min_length=1)
    blockers: list[StaticExplorerCheck]
    html_rendered: Literal[False]
    hosted_publish_requested: Literal[False]
    mutation_performed: Literal[False]
    acceptance_trace: list[Literal["PU-029", "FR-003", "FR-008", "VP-029"]] = Field(min_length=1)
    agent_summary: str = Field(min_length=1)


def validate_static_explorer_receipt(payload: object) -> StaticExplorerReceipt:
    return StaticExplorerReceipt.model_validate(payload)
