from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field


class _SigningContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class SigningPolicy(_SigningContractModel):
    schema_version: Literal["skills-sdk.signing-policy.v0"]
    schema_uri: Literal[
        "https://agent-skills.local/schemas/skills-sdk/signing-policy.v0.schema.json"
    ]
    policy_id: str = Field(min_length=1)
    signer_id: str = Field(min_length=1)
    allowed_algorithms: list[Literal["cosign-keyless", "minisign", "ssh-sig"]] = Field(min_length=1)
    allowed_package_ids: list[Annotated[str, Field(min_length=1)]] = Field(min_length=1)
    allowed_package_digests: list[Annotated[str, Field(min_length=71)]] = Field(min_length=1)
    requires_hardening_pass: Literal[True]
    key_material_policy: Literal["external_ref_required", "keyless_required"]
    redaction_policy: Literal["manifest_only", "manifest_and_receipts"]
    archive_required: Literal[False]
    acceptance_trace: list[Literal["FR-003", "FR-008", "SA-003", "SA-004", "SEC-001", "VP-021"]] = Field(
        min_length=1
    )


class SigningCheck(_SigningContractModel):
    id: str = Field(min_length=1)
    status: Literal["pass", "warning", "blocker"]
    severity: Literal["info", "warning", "blocker"]
    message: str = Field(min_length=1)
    evidence: list[str]


class SigningIntentReceipt(_SigningContractModel):
    schema_version: Literal["skills-sdk.signing-intent-receipt.v0"]
    schema_uri: Literal[
        "https://agent-skills.local/schemas/skills-sdk/signing-intent-receipt.v0.schema.json"
    ]
    status: Literal["ready", "blocked"]
    policy_path: str = Field(min_length=1)
    policy_digest: str | None = Field(min_length=71)
    package_id: str = Field(min_length=1)
    version: str = Field(min_length=1)
    source_digest: str = Field(min_length=71)
    manifest_digest: str = Field(min_length=71)
    package_digest: str = Field(min_length=71)
    signing_checks: list[SigningCheck] = Field(min_length=1)
    blockers: list[SigningCheck]
    warnings: list[SigningCheck]
    signature_requested: Literal[False]
    signing_performed: Literal[False]
    key_material_accessed: Literal[False]
    artifact_emitted: Literal[False]
    mutation_performed: Literal[False]
    acceptance_trace: list[Literal["FR-003", "FR-008", "SA-003", "SA-004", "SEC-001", "VP-021"]] = Field(
        min_length=1
    )
    agent_summary: str = Field(min_length=1)


def validate_signing_policy(payload: object) -> SigningPolicy:
    return SigningPolicy.model_validate(payload)


def validate_signing_intent_receipt(payload: object) -> SigningIntentReceipt:
    return SigningIntentReceipt.model_validate(payload)
