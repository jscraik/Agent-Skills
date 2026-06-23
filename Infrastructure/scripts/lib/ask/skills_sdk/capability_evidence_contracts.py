from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class _CapabilityEvidenceModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class CapabilityEvidenceRow(_CapabilityEvidenceModel):
    capability_id: str
    ref: str
    kind: Literal["file", "command", "schema", "receipt", "external_lane", "unknown"]
    status: Literal["pass", "blocked", "not_run", "unknown"]
    reason: str
    evidence: list[str]
    lane: Literal["local", "local_command", "external"]
    executes_command: bool


class CapabilityEvidenceReceipt(_CapabilityEvidenceModel):
    schema_version: Literal["skills-sdk.capability-evidence-receipt.v0"]
    schema_uri: Literal[
        "https://agent-skills.local/schemas/skills-sdk/capability-evidence-receipt.v0.schema.json"
    ]
    status: Literal["pass", "blocked"]
    operation: Literal["capability_evidence_verify"]
    scope: Literal["capability-matrix"]
    matrix_path: Literal["Infrastructure/config/skills-sdk/capability-matrix.v1.json"]
    capability_count: int = Field(ge=0)
    evidence_ref_count: int = Field(ge=0)
    pass_count: int = Field(ge=0)
    blocked_count: int = Field(ge=0)
    not_run_count: int = Field(ge=0)
    unknown_count: int = Field(ge=0)
    evidence_rows: list[CapabilityEvidenceRow]
    blockers: list[CapabilityEvidenceRow]
    mutation_performed: Literal[False]
    command_execution_performed: Literal[False]
    acceptance_trace: list[Literal["PU-032", "FR-008", "SA-003", "VP-032"]]
    agent_summary: str


def validate_capability_evidence_receipt(payload: object) -> CapabilityEvidenceReceipt:
    return CapabilityEvidenceReceipt.model_validate(payload)
