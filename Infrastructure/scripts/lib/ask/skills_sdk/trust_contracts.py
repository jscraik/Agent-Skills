from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class _TrustContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class TrustCheck(_TrustContractModel):
    id: str = Field(min_length=1)
    status: Literal["pass", "warning", "blocker"]
    severity: Literal["info", "warning", "blocker"]
    message: str = Field(min_length=1)
    evidence: list[str]


class TrustLedgerEntry(_TrustContractModel):
    schema_version: Literal["skills-sdk.trust-decision-receipt.v0"]
    recorded_at: str = Field(min_length=1)
    package_id_digest: str = Field(min_length=71)
    version_digest: str = Field(min_length=71)
    package_digest_digest: str = Field(min_length=71)
    decision: Literal["trust", "distrust", "revoke"]
    reason_digest: str = Field(min_length=71)
    owner_digest: str = Field(min_length=71)
    expires_at_digest: str | None = Field(default=None, min_length=71)
    revoked_package_digest_digest: str | None = Field(default=None, min_length=71)


class TrustDecisionReceipt(_TrustContractModel):
    schema_version: Literal["skills-sdk.trust-decision-receipt.v0"]
    schema_uri: Literal[
        "https://agent-skills.local/schemas/skills-sdk/trust-decision-receipt.v0.schema.json"
    ]
    status: Literal["preview", "recorded", "blocked"]
    operation: Literal["trust_decision"]
    decision: Literal["trust", "distrust", "revoke"]
    reason: str = Field(min_length=1)
    owner: str = Field(min_length=1)
    expires_at: str | None = Field(default=None, min_length=1)
    revoked_package_digest: str | None = Field(default=None, min_length=71)
    package_id: str = Field(min_length=1)
    version: str = Field(min_length=1)
    source_digest: str = Field(min_length=71)
    manifest_digest: str = Field(min_length=71)
    package_digest: str = Field(min_length=71)
    ledger_path: str = Field(min_length=1)
    ledger_before_digest: str | None = Field(default=None, min_length=71)
    ledger_after_digest: str | None = Field(default=None, min_length=71)
    ledger_entry: TrustLedgerEntry | None
    ledger_entry_digest: str | None = Field(default=None, min_length=71)
    trust_checks: list[TrustCheck] = Field(min_length=1)
    blockers: list[TrustCheck]
    warnings: list[TrustCheck]
    mutation_performed: bool
    trust_store_mutated: Literal[False]
    acceptance_trace: list[Literal["FR-003", "FR-008", "SA-003", "SA-004", "SEC-001", "VP-025"]] = Field(
        min_length=1
    )
    agent_summary: str = Field(min_length=1)

    @model_validator(mode="after")
    def _recorded_receipts_include_ledger_evidence(self) -> TrustDecisionReceipt:
        if self.status == "recorded":
            if not self.mutation_performed:
                raise ValueError("recorded trust decisions must set mutation_performed true")
            if self.ledger_after_digest is None or self.ledger_entry is None or self.ledger_entry_digest is None:
                raise ValueError("recorded trust decisions must include ledger mutation evidence")
        elif self.mutation_performed:
            raise ValueError("preview and blocked trust decisions must set mutation_performed false")
        return self


def validate_trust_decision_receipt(payload: object) -> TrustDecisionReceipt:
    return TrustDecisionReceipt.model_validate(payload)
