from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class _CiPolicyModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class CiPolicyCheck(_CiPolicyModel):
    id: str = Field(min_length=1)
    status: Literal["pass", "blocker"]
    severity: Literal["blocker"]
    message: str = Field(min_length=1)
    evidence: list[str]


class RequiredCheck(_CiPolicyModel):
    name: str = Field(min_length=1)
    required: Literal[True]
    source: Literal["base", "risk_tier"]


class CiPolicyPreviewReceipt(_CiPolicyModel):
    schema_version: Literal["skills-sdk.ci-policy-preview-receipt.v0"]
    schema_uri: Literal[
        "https://jscraik.local/agent-skills/schemas/skills-sdk/ci-policy-preview-receipt.v0.schema.json"
    ]
    status: Literal["preview", "blocked"]
    operation: Literal["ci_policy_preview"]
    risk_tier: Literal["low", "medium", "high", "privileged", "published"]
    required_checks: list[RequiredCheck]
    policy_checks: list[CiPolicyCheck] = Field(min_length=1)
    blockers: list[CiPolicyCheck]
    live_ci_evidence_attached: Literal[False]
    branch_protection_mutated: Literal[False]
    mutation_performed: Literal[False]
    acceptance_trace: list[Literal["PU-028", "FR-008", "SA-004", "VP-028"]] = Field(min_length=1)
    agent_summary: str = Field(min_length=1)


def validate_ci_policy_preview_receipt(payload: object) -> CiPolicyPreviewReceipt:
    return CiPolicyPreviewReceipt.model_validate(payload)
