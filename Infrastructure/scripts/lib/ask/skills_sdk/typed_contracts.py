from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict


class _SdkContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


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


def validate_install_receipt(payload: object) -> InstallReceipt:
    return InstallReceipt.model_validate(payload)


def validate_lockfile(payload: object) -> Lockfile:
    return Lockfile.model_validate(payload)


def validate_cleanup_receipt(payload: object) -> CleanupReceipt:
    return CleanupReceipt.model_validate(payload)
