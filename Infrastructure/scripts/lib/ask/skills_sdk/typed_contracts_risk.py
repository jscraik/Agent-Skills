from __future__ import annotations

from typing import Literal

from ask.skills_sdk.typed_contracts_base import SdkContractModel


class RiskSensor(SdkContractModel):
    id: str
    placement: Literal["source", "schema", "static", "runtime_adapter", "external_adapter", "preview"]
    required: bool
    cost: Literal["low", "medium", "high"]
    blocking_behavior: Literal["block", "warn", "advisory", "skip_optional"]
    status: Literal["selected", "available_not_run", "skipped_optional", "blocked"]
    receipt_required: bool


class RiskClassification(SdkContractModel):
    schema_version: Literal["skills-sdk.risk-classification.v1"]
    schema_uri: Literal[
        "https://agent-skills.local/schemas/skills-sdk/risk-classification.v1.schema.json"
    ]
    source_kind: Literal["docs_only", "referenced", "scripted", "external", "placeholder"]
    risk_tier: Literal["low", "medium", "high", "privileged", "published"]
    probability: Literal["low", "medium", "high", "unknown"]
    impact: Literal["low", "medium", "high", "unknown"]
    detectability: Literal["low", "medium", "high", "unknown"]
    cost: Literal["low", "medium", "high"]
    blocking_behavior: Literal["block", "warn", "advisory", "skip_optional"]
    receipt_required: bool
    sensor_ids: list[str]
    sensors: list[RiskSensor]
    acceptance_trace: list[str]


class ArtifactStatusRow(SdkContractModel):
    artifact_path: str
    artifact_type: Literal["json", "json_schema", "markdown", "yaml", "html"]
    authority: Literal["runtime_truth", "schema_contract", "source_artifact", "visual_projection"]
    status: Literal["current", "drifted", "blocked", "deferred"]
    evidence_refs: list[str]


class SourceArtifactContract(SdkContractModel):
    artifact_path: str
    artifact_class: Literal["skill_md", "sdk_spec", "sdk_plan", "implementation_notes"]
    required_sections: list[str]
    evidence_refs: list[str]
