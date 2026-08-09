from __future__ import annotations

from typing import Literal

from ask.skills_sdk.typed_contracts_base import SdkContractModel


class CapabilityRow(SdkContractModel):
    id: str
    title: str
    status: Literal[
        "implemented",
        "preview_only",
        "placeholder_optional",
        "placeholder_blocked",
        "blocked_missing_adapter",
        "deferred",
        "out_of_scope",
    ]
    owner_surface: str
    pipeline_sections: list[str]
    feature_executed: bool
    mutation_performed: bool
    evidence_refs: list[str]
    next_slice: str
    notes: str


class CapabilitySummary(SdkContractModel):
    total: int
    by_status: dict[str, int]
    feature_executed_count: int
    mutation_performed_count: int


class CapabilityStatus(SdkContractModel):
    schema_version: Literal["skills-sdk.capability-status.v1"]
    schema_uri: Literal[
        "https://agent-skills.local/schemas/skills-sdk/capability-status.v1.schema.json"
    ]
    status: Literal["truth_surface"]
    generated_from: str
    capabilities: list[CapabilityRow]
    summary: CapabilitySummary
    source_artifacts: list[str]
    validation_commands: list[str]
    agent_summary: str
