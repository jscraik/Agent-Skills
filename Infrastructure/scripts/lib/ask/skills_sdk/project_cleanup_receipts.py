from __future__ import annotations

from pathlib import Path
from typing import Any

from ask.skills_sdk.project_install import _sha256_json

CLEANUP_RECEIPT_SCHEMA_VERSION = "skills-sdk.project-cleanup-receipt.v1"
CLEANUP_RECEIPT_SCHEMA_URI = (
    "https://agent-skills.local/schemas/skills-sdk/project-cleanup-receipt.v1.schema.json"
)
CLEANUP_RECEIPT_DIR = Path(".harness/receipts/skills-sdk/cleanup")
CLEANUP_JOURNAL_DIR = Path(".harness/state/skills-sdk/cleanup")
CLEANUP_ACCEPTANCE_TRACE = [
    "PU-010-TR-001",
    "PU-010-TR-002",
    "PU-010-TR-005",
    "PU-010-TR-007",
    "PU-010-TR-009",
    "PU-010-TR-010",
    "PU-010-TR-016",
    "PU-010-TR-017",
]


def _cleanup_receipt(
    *,
    operation: str,
    status: str,
    target_root: str,
    source_receipt_path: str, source_receipt_digest: str,
    files_planned: list[dict[str, Any]],
    mutation_performed: bool,
    live_project_validation: bool,
    skill_id: str | None = None,
    journal_path: str | None = None,
    lockfile_changes: list[dict[str, Any]] | None = None,
    directory_prune_results: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    removed, skipped, blocked = _cleanup_file_groups(files_planned)
    manual_actions = _manual_actions(skipped, blocked)
    return _cleanup_receipt_payload(
        operation=operation,
        status=status,
        target_root=target_root,
        source_receipt_path=source_receipt_path,
        source_receipt_digest=source_receipt_digest,
        files_planned=files_planned,
        mutation_performed=mutation_performed,
        live_project_validation=live_project_validation,
        skill_id=skill_id,
        journal_path=journal_path,
        lockfile_changes=lockfile_changes,
        directory_prune_results=directory_prune_results,
        removed=removed,
        skipped=skipped,
        blocked=blocked,
        manual_actions=manual_actions,
    )


def _cleanup_file_groups(
    files_planned: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    return (
        [item for item in files_planned if item["status"] == "removed"],
        [item for item in files_planned if item["status"] == "skipped"],
        [item for item in files_planned if item["status"] == "blocked"],
    )


def _manual_actions(
    skipped: list[dict[str, Any]], blocked: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    return [
        {"path": item["target_path"], "reason": item["reason"]}
        for item in [*skipped, *blocked]
        if item["reason"] not in {"already_absent"}
    ]


def _cleanup_receipt_payload(
    *,
    operation: str,
    status: str,
    target_root: str,
    source_receipt_path: str,
    source_receipt_digest: str,
    files_planned: list[dict[str, Any]],
    mutation_performed: bool,
    live_project_validation: bool,
    skill_id: str | None, journal_path: str | None,
    lockfile_changes: list[dict[str, Any]] | None, directory_prune_results: list[dict[str, Any]] | None,
    removed: list[dict[str, Any]], skipped: list[dict[str, Any]],
    blocked: list[dict[str, Any]], manual_actions: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "schema_version": CLEANUP_RECEIPT_SCHEMA_VERSION,
        "schema_uri": CLEANUP_RECEIPT_SCHEMA_URI,
        "operation": operation,
        "status": status,
        "target_root": target_root,
        "skill_id": skill_id,
        "source_receipt_path": source_receipt_path,
        "source_receipt_digest": source_receipt_digest,
        "install_receipt_identity": source_receipt_digest,
        "target_root_identity": _sha256_json({"target_root": target_root}),
        "live_project_validation": live_project_validation,
        "files_planned": files_planned,
        "files_removed": removed,
        "files_restored": [],
        "files_skipped": skipped,
        "files_blocked": blocked,
        "lockfile_changes": lockfile_changes or [],
        "directory_prune_results": directory_prune_results or [],
        "cleanup_journal_name": Path(journal_path).name if journal_path else None,
        "journal_path": journal_path,
        "manual_actions": manual_actions,
        "mutation_performed": mutation_performed,
        "acceptance_trace": CLEANUP_ACCEPTANCE_TRACE,
    }


def _blocked_receipt(
    operation: str,
    source_receipt_path: str,
    target_root: str,
    conflicts: list[str],
    *,
    source_digest: str = "sha256:blocked",
) -> dict[str, Any]:
    blocked = [
        {
            "target_path": conflict,
            "expected_digest": "sha256:blocked",
            "action": "block",
            "status": "blocked",
            "reason": conflict,
        }
        for conflict in conflicts
    ]
    return _cleanup_receipt(
        operation=operation,
        status="blocked",
        target_root=target_root,
        source_receipt_path=source_receipt_path,
        source_receipt_digest=source_digest,
        files_planned=blocked,
        mutation_performed=False,
        live_project_validation=False,
        lockfile_changes=[],
    )


def _block_all(files: list[dict[str, Any]], reason: str) -> list[dict[str, Any]]:
    return [{**item, "status": "blocked", "reason": reason} for item in files]
