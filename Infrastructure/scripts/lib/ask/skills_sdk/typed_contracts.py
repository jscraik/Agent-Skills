from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field


class _SdkContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class FileRecord(_SdkContractModel):
    source_path: str
    target_path: str
    digest: str


class RollbackMetadata(_SdkContractModel):
    status: str
    reason: str
    installed_files: list[str]


class InstallReceipt(_SdkContractModel):
    schema_version: Literal["skills-sdk.install-receipt.v1"]
    schema_uri: Literal[
        "https://jscraik.local/agent-skills/schemas/skills-sdk/install-receipt.v1.schema.json"
    ]
    status: Literal["success", "blocked", "partial"]
    operation: Literal["install"]
    scope: Literal["project"]
    source_path: str
    source_digest: str
    target_root: str
    target_paths: list[str]
    files_written: list[FileRecord]
    files_skipped: list[FileRecord]
    files_overwritten: list[FileRecord]
    conflicts: list[str]
    lockfile_path: str | None
    lockfile_before_digest: str | None
    lockfile_after_digest: str | None
    rollback_metadata: RollbackMetadata
    mutation_performed: bool
    acceptance_trace: list[str]


class LockfileEntry(_SdkContractModel):
    name: str
    source_path: str
    source_digest: str
    target_path: str
    receipt_ref: str
    installed_at: str
    files: list[FileRecord]


class Lockfile(_SdkContractModel):
    schema_version: Literal["skills-sdk.lockfile.v1"]
    schema_uri: Literal["https://jscraik.local/agent-skills/schemas/skills-sdk/lockfile.v1.schema.json"]
    generated_by: str
    entries: dict[str, LockfileEntry]


class FileAction(_SdkContractModel):
    target_path: str
    expected_digest: str
    action: str
    status: str
    reason: str
    current_digest: str | None = None


class LockfileChange(_SdkContractModel):
    before_digest: str | None
    after_digest: str | None
    path: str | None = None
    changed: bool | None = None
    operation: str | None = None
    removed_entries: list[str] | None = None
    reason: str | None = None


class DirectoryPruneResult(_SdkContractModel):
    path: str
    pruned: bool
    reason: str


class ManualAction(_SdkContractModel):
    path: str
    reason: str


class CleanupReceipt(_SdkContractModel):
    schema_version: Literal["skills-sdk.project-cleanup-receipt.v1"]
    schema_uri: Literal[
        "https://jscraik.local/agent-skills/schemas/skills-sdk/project-cleanup-receipt.v1.schema.json"
    ]
    operation: Literal["rollback", "uninstall"]
    status: Literal["preview", "success", "partial", "blocked"]
    target_root: str
    skill_id: str | None
    source_receipt_path: str
    source_receipt_digest: str
    install_receipt_identity: str
    target_root_identity: str
    live_project_validation: bool
    files_planned: list[FileAction]
    files_removed: list[FileAction]
    files_restored: list[FileAction]
    files_skipped: list[FileAction]
    files_blocked: list[FileAction]
    lockfile_changes: list[LockfileChange]
    directory_prune_results: list[DirectoryPruneResult]
    cleanup_journal_name: str | None
    journal_path: str | None
    manual_actions: list[ManualAction]
    mutation_performed: bool
    acceptance_trace: list[str]
    receipt_path: str | None = None


class ProjectRootIdentity(_SdkContractModel):
    identity_kind: Literal["realpath", "unresolved"]
    realpath: str
    exists: bool | None = None


class ProjectConformanceSkillRow(_SdkContractModel):
    skill_id: str
    target_path: str
    receipt_ref: str
    receipt_status: Literal["valid", "missing", "invalid"]
    status: Literal["healthy", "blocked"]
    rollback_ready: bool
    uninstall_ready: bool
    issue_codes: list[str]


class ProjectConformanceIssue(_SdkContractModel):
    code: str
    severity: Literal["info", "warning", "blocker"]
    message: str
    path: str
    skill_id: str | None


class ProjectConformanceManualAction(_SdkContractModel):
    action: str
    reason: str
    path: str
    skill_id: str | None


class ProjectConformanceReceipt(_SdkContractModel):
    schema_version: Literal["skills-sdk.project-conformance-receipt.v1"]
    schema_uri: Literal[
        "https://jscraik.local/agent-skills/schemas/skills-sdk/project-conformance-receipt.v1.schema.json"
    ]
    command: str
    mode: Literal["status", "doctor"]
    status: Literal["pass", "warn", "fail", "blocked"]
    project_root: str
    project_root_identity: ProjectRootIdentity
    project_managed: bool
    lockfile_path: str | None
    lockfile_status: Literal[
        "not_checked",
        "missing",
        "empty_not_installed",
        "missing_with_installed_evidence",
        "valid",
        "valid_with_diagnostics",
        "invalid",
        "unsupported",
    ]
    installed_skill_count: int
    installed_skills: list[ProjectConformanceSkillRow]
    rollback_ready_count: int
    uninstall_ready_count: int
    issues: list[ProjectConformanceIssue]
    manual_actions: list[ProjectConformanceManualAction]
    mutation_performed: Literal[False]
    acceptance_trace: list[str]
    agent_summary: str


class RobotMetadata(_SdkContractModel):
    version: str
    command: str
    next_steps: list[str]
    correction_note: str | None


class RobotTelemetry(_SdkContractModel):
    model_config = ConfigDict(extra="allow")


class RobotError(_SdkContractModel):
    code: str
    message: str
    fix_suggestion: str | None = None
    help_url: str | None = None


class RobotEnvelope(_SdkContractModel):
    status: Literal["success", "error"]
    trace_id: str
    metadata: RobotMetadata
    data: dict[str, object]
    telemetry: RobotTelemetry
    errors: list[RobotError]


class CapabilityRow(_SdkContractModel):
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


class CapabilitySummary(_SdkContractModel):
    total: int
    by_status: dict[str, int]
    feature_executed_count: int
    mutation_performed_count: int


class CapabilityStatus(_SdkContractModel):
    schema_version: Literal["skills-sdk.capability-status.v1"]
    schema_uri: Literal[
        "https://jscraik.local/agent-skills/schemas/skills-sdk/capability-status.v1.schema.json"
    ]
    status: Literal["truth_surface"]
    generated_from: str
    capabilities: list[CapabilityRow]
    summary: CapabilitySummary
    source_artifacts: list[str]
    validation_commands: list[str]
    agent_summary: str


class ManifestSource(_SdkContractModel):
    schema_version: Literal["skills-sdk.manifest-source.v1"]
    schema_uri: Literal[
        "https://jscraik.local/agent-skills/schemas/skills-sdk/manifest-source.v1.schema.json"
    ]
    source_kind: Literal[
        "minimal_skill",
        "referenced_skill",
        "scripted_skill",
        "manifest_declared_project_source",
        "generated_projection",
        "external_package",
        "placeholder",
    ]
    source_path: str
    skill_md_path: str
    canonical_source: bool
    runtime_projection: bool
    manifest_fields: list[str]
    optional_surfaces: list[
        Literal[
            "agents_openai_yaml",
            "scripts",
            "references",
            "assets",
            "evals",
            "package_manifest",
            "lockfile_preview",
        ]
    ]
    acceptance_trace: list[Literal["FR-003", "SA-003", "VP-001", "VP-021"]]


class SkillIrIdentity(_SdkContractModel):
    id: str
    name: str
    version: str


class SkillIrSource(_SdkContractModel):
    root: str
    skill_md: str
    readme: str | None
    references: list[str]
    scripts: list[str]
    assets: list[str]
    evals: list[str]


class SkillIrBehavior(_SdkContractModel):
    trigger: str
    inputs: list[str]
    outputs: list[str]
    procedure_summary: str


class SkillIrPermissions(_SdkContractModel):
    filesystem: Literal["none", "read", "write"]
    network: Literal["none", "restricted", "open"]
    secrets: Literal["none", "handles", "raw"]
    tools: list[str]


class SkillIrRisk(_SdkContractModel):
    tier: Literal["draft", "local", "scripted", "team", "privileged", "published"]
    reasons: list[str]
    source_kind: Literal["docs_only", "referenced", "scripted", "external", "placeholder"]


class SkillIrEvidence(_SdkContractModel):
    checks: list[str]
    receipts: list[str]


class SkillIr(_SdkContractModel):
    schema_version: Literal["skills-sdk.skill-ir.v0"]
    schema_uri: Literal["https://jscraik.local/agent-skills/schemas/skills-sdk/skill-ir.v0.schema.json"]
    identity: SkillIrIdentity
    source: SkillIrSource
    behavior: SkillIrBehavior
    permissions: SkillIrPermissions
    risk: SkillIrRisk
    evidence: SkillIrEvidence
    mutation_performed: Literal[False]
    acceptance_trace: list[Literal["FR-003", "FR-008", "SA-003", "SA-004", "VP-021", "VP-022"]] = Field(
        min_length=1
    )


class PackageManifestFile(_SdkContractModel):
    path: str
    sha256: str = Field(min_length=64, max_length=64)
    size_bytes: int = Field(ge=0)
    role: Literal["skill_md", "readme", "reference", "script", "asset", "eval"]


class PackageManifestProvenance(_SdkContractModel):
    source: list[str] = Field(min_length=1)
    builder: str


class PackageManifest(_SdkContractModel):
    schema_version: Literal["skills-sdk.package-manifest.v0"]
    schema_uri: Literal[
        "https://jscraik.local/agent-skills/schemas/skills-sdk/package-manifest.v0.schema.json"
    ]
    package_id: str = Field(min_length=1)
    version: str = Field(min_length=1)
    skill_ir_schema_version: Literal["skills-sdk.skill-ir.v0"]
    source: SkillIrSource
    files: list[PackageManifestFile] = Field(min_length=1)
    provenance: PackageManifestProvenance
    mutation_performed: Literal[False]


class PackageDigestReceipt(_SdkContractModel):
    schema_version: Literal["skills-sdk.package-digest-receipt.v0"]
    schema_uri: Literal[
        "https://jscraik.local/agent-skills/schemas/skills-sdk/package-digest-receipt.v0.schema.json"
    ]
    status: Literal["built", "blocked"]
    package_id: str = Field(min_length=1)
    version: str = Field(min_length=1)
    source_digest: str = Field(min_length=71)
    manifest_digest: str = Field(min_length=71)
    package_digest: str = Field(min_length=71)
    manifest: PackageManifest
    included_files: list[str] = Field(min_length=1)
    excluded_files: list[str]
    mutation_performed: Literal[False]
    acceptance_trace: list[Literal["FR-003", "FR-008", "SA-003", "SA-004", "VP-021", "VP-022"]] = Field(
        min_length=1
    )


class PackageHardeningCheck(_SdkContractModel):
    id: str = Field(min_length=1)
    status: Literal["pass", "warning", "blocker"]
    severity: Literal["info", "warning", "blocker"]
    message: str = Field(min_length=1)
    evidence: list[str]


NonEmptyPackagePath = Annotated[str, Field(min_length=1)]


class PackageHardeningReceipt(_SdkContractModel):
    schema_version: Literal["skills-sdk.package-hardening-receipt.v0"]
    schema_uri: Literal[
        "https://jscraik.local/agent-skills/schemas/skills-sdk/package-hardening-receipt.v0.schema.json"
    ]
    status: Literal["pass", "blocked"]
    package_id: str = Field(min_length=1)
    version: str = Field(min_length=1)
    source_digest: str = Field(min_length=71)
    manifest_digest: str = Field(min_length=71)
    package_digest: str = Field(min_length=71)
    included_files: list[NonEmptyPackagePath]
    file_count: int = Field(ge=0)
    total_size_bytes: int = Field(ge=0)
    hardening_checks: list[PackageHardeningCheck] = Field(min_length=1)
    blockers: list[PackageHardeningCheck]
    warnings: list[PackageHardeningCheck]
    mutation_performed: Literal[False]
    acceptance_trace: list[Literal["FR-003", "FR-008", "SA-003", "SA-004", "VP-021", "VP-022"]] = Field(
        min_length=1
    )


class EvalCase(_SdkContractModel):
    schema_version: Literal["skills-sdk.eval-case.v0"]
    case_id: str = Field(min_length=1)
    input: str = Field(min_length=1)
    expected: str = Field(min_length=1)
    actual: str
    oracle: Literal["exact_match"]
    acceptance_trace: list[Literal["FR-003", "FR-008", "SA-003", "SA-004", "VP-021", "VP-022"]] = Field(
        min_length=1
    )


class EvalCaseResult(_SdkContractModel):
    case_id: str = Field(min_length=1)
    status: Literal["pass", "fail"]
    oracle: Literal["exact_match"]
    expected: str = Field(min_length=1)
    actual: str


class EvalRunReceipt(_SdkContractModel):
    schema_version: Literal["skills-sdk.eval-run-receipt.v0"]
    schema_uri: Literal[
        "https://jscraik.local/agent-skills/schemas/skills-sdk/eval-run-receipt.v0.schema.json"
    ]
    status: Literal["pass", "fail", "blocked"]
    runner: Literal["deterministic_jsonl_v0", "internal_skill_builder_v0"]
    dataset_path: str = Field(min_length=1)
    dataset_digest: str = Field(min_length=71)
    skill_ir_schema_version: str | None
    target_path: str | None
    mode: str | None
    case_count: int = Field(ge=0)
    passed_count: int = Field(ge=0)
    failed_count: int = Field(ge=0)
    cases: list[EvalCaseResult]
    blockers: list[str]
    mutation_performed: Literal[False]
    acceptance_trace: list[Literal["FR-003", "FR-008", "SA-003", "SA-004", "VP-021", "VP-022"]] = Field(
        min_length=1
    )


class SkillFrontmatter(_SdkContractModel):
    name: str
    description: str
    version: str | None = None
    risk: Literal["low", "medium", "high", "privileged", "published"] | None = None


class LockfilePreview(_SdkContractModel):
    schema_version: Literal["skills-sdk.lockfile-preview.v1"]
    schema_uri: Literal[
        "https://jscraik.local/agent-skills/schemas/skills-sdk/lockfile-preview.v1.schema.json"
    ]
    lockfile_path: Literal["skills.lock.json"]
    operation: Literal["add", "update", "remove", "quarantine", "none"]
    before_digest: str | None
    after_digest: str | None
    would_write: Literal[False]
    acceptance_trace: list[Literal["FR-006", "SA-020", "SA-021", "VP-021"]]


class InstallPreview(_SdkContractModel):
    schema_version: Literal["skills-sdk.install-preview.v1"]
    schema_uri: Literal[
        "https://jscraik.local/agent-skills/schemas/skills-sdk/install-preview.v1.schema.json"
    ]
    scope: Literal["project", "workspace", "global"]
    target_paths: list[str]
    digest: str
    permission_summary: list[
        Literal["filesystem_read", "filesystem_write", "network", "secrets", "process", "none"]
    ]
    trust_state: Literal["trusted", "untrusted", "requires_approval", "blocked"]
    conflicts: list[str]
    lockfile_delta_preview: LockfilePreview
    rollback_note: str
    mutation_performed: Literal[False]
    receipt_ref: str
    acceptance_trace: list[Literal["FR-006", "FR-010", "SA-020", "SA-021", "VP-021"]]


class ProofRecord(_SdkContractModel):
    type: Literal[
        "schema_validation",
        "fixture_test",
        "command_output",
        "no_write_assertion",
        "placeholder_state",
    ]
    evidence_kind: Literal["json_schema", "pytest", "receipt", "artifact", "manual_waiver"]
    evidence_ref: str


class CheckSensor(_SdkContractModel):
    id: str
    placement: Literal["preflight", "schema", "risk", "preview", "placeholder", "closeout"]
    required: bool


class CheckActor(_SdkContractModel):
    role: Literal["agent", "human", "ci", "system"]


class CheckReceipt(_SdkContractModel):
    schema_version: Literal["skills-sdk.check-receipt.v1"]
    schema_uri: Literal[
        "https://jscraik.local/agent-skills/schemas/skills-sdk/check-receipt.v1.schema.json"
    ]
    command: str
    command_version: str
    status: Literal["pass", "warning", "blocked", "degraded", "quarantined", "not_run", "skipped_optional"]
    failure_class: Literal[
        "none",
        "manifest_invalid",
        "receipt_invalid",
        "risk_classifier_unavailable",
        "preview_would_write",
        "placeholder_not_available",
        "permission_denied",
        "tool_missing",
        "external_source_untrusted",
        "validation_failed",
    ]
    exit_code: int
    work_mode: Literal["computational", "inferential", "hybrid"]
    proof: ProofRecord
    sensor: CheckSensor
    actor: CheckActor
    approval_decision: Literal["not_required", "approved", "denied", "waived", "pending"]
    redaction: Literal["none", "redacted", "not_applicable"]
    acceptance_trace: list[Literal["FR-008", "FR-009", "SA-004", "SA-005", "VP-002", "VP-011", "VP-021"]]


class RiskSensor(_SdkContractModel):
    id: str
    placement: Literal["source", "schema", "static", "runtime_adapter", "external_adapter", "preview"]
    required: bool
    cost: Literal["low", "medium", "high"]
    blocking_behavior: Literal["block", "warn", "advisory", "skip_optional"]
    status: Literal["selected", "available_not_run", "skipped_optional", "blocked"]
    receipt_required: bool


class RiskClassification(_SdkContractModel):
    schema_version: Literal["skills-sdk.risk-classification.v1"]
    schema_uri: Literal[
        "https://jscraik.local/agent-skills/schemas/skills-sdk/risk-classification.v1.schema.json"
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


class ArtifactStatusRow(_SdkContractModel):
    artifact_path: str
    artifact_type: Literal["json", "json_schema", "markdown", "yaml", "html"]
    authority: Literal["runtime_truth", "schema_contract", "source_artifact", "visual_projection"]
    status: Literal["current", "drifted", "blocked", "deferred"]
    evidence_refs: list[str]


class SourceArtifactContract(_SdkContractModel):
    artifact_path: str
    artifact_class: Literal["skill_md", "sdk_spec", "sdk_plan", "implementation_notes"]
    required_sections: list[str]
    evidence_refs: list[str]


def validate_install_receipt(payload: object) -> InstallReceipt:
    return InstallReceipt.model_validate(payload)


def validate_lockfile(payload: object) -> Lockfile:
    return Lockfile.model_validate(payload)


def validate_cleanup_receipt(payload: object) -> CleanupReceipt:
    """
    Validate and parse an arbitrary payload into a CleanupReceipt.
    
    Parameters:
    	payload (object): Unvalidated payload (typically a dict) representing a cleanup receipt.
    
    Returns:
    	cleanup_receipt (CleanupReceipt): The parsed and validated `CleanupReceipt` model instance.
    """
    return CleanupReceipt.model_validate(payload)


def validate_project_conformance_receipt(payload: object) -> ProjectConformanceReceipt:
    """
    Validate and parse an arbitrary payload into a ProjectConformanceReceipt model.
    
    Parameters:
    	payload (object): Unvalidated payload to be parsed and validated against the ProjectConformanceReceipt schema.
    
    Returns:
    	project_conformance_receipt (ProjectConformanceReceipt): The validated ProjectConformanceReceipt instance.
    """
    return ProjectConformanceReceipt.model_validate(payload)


def validate_robot_envelope(payload: object) -> RobotEnvelope:
    """
    Validate and parse a raw payload into a RobotEnvelope model.
    
    Parameters:
        payload (object): Unvalidated input (typically a dict) representing a robot envelope.
    
    Returns:
        RobotEnvelope: The validated and parsed RobotEnvelope model instance.
    """
    return RobotEnvelope.model_validate(payload)


def validate_capability_status(payload: object) -> CapabilityStatus:
    return CapabilityStatus.model_validate(payload)


def validate_manifest_source(payload: object) -> ManifestSource:
    return ManifestSource.model_validate(payload)


def validate_skill_ir(payload: object) -> SkillIr:
    return SkillIr.model_validate(payload)


def validate_package_manifest(payload: object) -> PackageManifest:
    return PackageManifest.model_validate(payload)


def validate_package_digest_receipt(payload: object) -> PackageDigestReceipt:
    return PackageDigestReceipt.model_validate(payload)


def validate_package_hardening_receipt(payload: object) -> PackageHardeningReceipt:
    return PackageHardeningReceipt.model_validate(payload)


def validate_eval_case(payload: object) -> EvalCase:
    return EvalCase.model_validate(payload)


def validate_eval_run_receipt(payload: object) -> EvalRunReceipt:
    return EvalRunReceipt.model_validate(payload)


def validate_skill_frontmatter(payload: object) -> SkillFrontmatter:
    return SkillFrontmatter.model_validate(payload)


def validate_install_preview(payload: object) -> InstallPreview:
    return InstallPreview.model_validate(payload)


def validate_check_receipt(payload: object) -> CheckReceipt:
    return CheckReceipt.model_validate(payload)


def validate_risk_classification(payload: object) -> RiskClassification:
    return RiskClassification.model_validate(payload)


def validate_artifact_status_row(payload: object) -> ArtifactStatusRow:
    return ArtifactStatusRow.model_validate(payload)


def validate_source_artifact_contract(payload: object) -> SourceArtifactContract:
    return SourceArtifactContract.model_validate(payload)
