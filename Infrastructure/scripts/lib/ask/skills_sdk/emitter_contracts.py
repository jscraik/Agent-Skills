from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class _EmitterModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class EmitterCheck(_EmitterModel):
    id: str = Field(min_length=1)
    status: Literal["pass", "blocker"]
    severity: Literal["blocker"]
    message: str = Field(min_length=1)
    evidence: list[str]


class EmitterWriteAction(_EmitterModel):
    action: Literal["write", "skip"]
    source_path: str = Field(min_length=1)
    target_path: str = Field(min_length=1)
    source_digest: str | None = Field(default=None, min_length=64)
    reason: str = Field(min_length=1)


class EmitterPreviewReceipt(_EmitterModel):
    schema_version: Literal["skills-sdk.emitter-preview-receipt.v0"]
    schema_uri: Literal[
        "https://jscraik.local/agent-skills/schemas/skills-sdk/emitter-preview-receipt.v0.schema.json"
    ]
    status: Literal["preview", "blocked"]
    operation: Literal["emitter_write_plan_preview"]
    projection: Literal["runtime-skill"]
    package_id: str = Field(min_length=1)
    version: str = Field(min_length=1)
    package_digest: str = Field(min_length=71)
    target_root: Literal[".agents/skills"]
    write_plan: list[EmitterWriteAction]
    required_receipts: list[
        Literal["package_digest_receipt", "package_hardening_receipt"]
    ] = Field(min_length=2, max_length=2)
    emitter_checks: list[EmitterCheck] = Field(min_length=1)
    blockers: list[EmitterCheck]
    mutation_performed: Literal[False]
    artifact_emitted: Literal[False]
    remote_publish_requested: Literal[False]
    acceptance_trace: list[Literal["PU-027", "FR-003", "FR-008", "SA-003", "VP-027"]] = Field(
        min_length=1
    )
    agent_summary: str = Field(min_length=1)

    @field_validator("required_receipts")
    @classmethod
    def _require_both_receipts(
        cls,
        value: list[Literal["package_digest_receipt", "package_hardening_receipt"]],
    ) -> list[Literal["package_digest_receipt", "package_hardening_receipt"]]:
        expected = {"package_digest_receipt", "package_hardening_receipt"}
        if len(set(value)) != len(value) or set(value) != expected:
            raise ValueError("required_receipts must include package_digest_receipt and package_hardening_receipt")
        return value


def validate_emitter_preview_receipt(payload: object) -> EmitterPreviewReceipt:
    return EmitterPreviewReceipt.model_validate(payload)
