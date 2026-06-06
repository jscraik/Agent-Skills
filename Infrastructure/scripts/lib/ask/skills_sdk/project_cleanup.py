from __future__ import annotations

import json
import os
import stat
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ask.skills_sdk.project_install import (
    DEFAULT_LOCKFILE_PATH,
    INSTALL_RECEIPT_SCHEMA_URI,
    INSTALL_RECEIPT_SCHEMA_VERSION,
    LOCKFILE_SCHEMA_URI,
    LOCKFILE_SCHEMA_VERSION,
    ProjectInstallError,
    _json_atomic_replace,
    _metadata_path_conflicts,
    _relative_to,
    _resolve_project_root,
    _sha256_file,
    _sha256_json,
)


CLEANUP_RECEIPT_SCHEMA_VERSION = "skills-sdk.project-cleanup-receipt.v1"
CLEANUP_RECEIPT_SCHEMA_URI = (
    "https://jscraik.local/agent-skills/schemas/skills-sdk/project-cleanup-receipt.v1.schema.json"
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


@dataclass(frozen=True)
class ProjectCleanupError(Exception):
    code: str
    message: str
    fix_suggestion: str
    receipt: dict[str, Any]


def rollback_project_install(
    repo_root: Path,
    *,
    receipt_path: str,
    project_root: str | None,
    apply: bool,
) -> dict[str, Any]:
    source_receipt_path = _resolve_receipt_path(receipt_path)
    source_receipt, source_digest = _load_install_receipt(source_receipt_path, operation="rollback")
    resolved_project_root = _resolve_cleanup_root(repo_root, project_root, source_receipt, require_root=apply)
    plan = _rollback_plan(source_receipt, source_receipt_path, source_digest, resolved_project_root)
    if resolved_project_root is not None:
        _validate_plan_paths(plan, resolved_project_root)
        _classify_current_files(plan, resolved_project_root)
    receipt = _cleanup_receipt(
        operation="rollback",
        status="preview",
        target_root=str(resolved_project_root) if resolved_project_root else str(source_receipt.get("target_root", "")),
        source_receipt_path=str(source_receipt_path),
        source_receipt_digest=source_digest,
        files_planned=plan,
        mutation_performed=False,
        live_project_validation=resolved_project_root is not None,
    )
    if not apply:
        return receipt
    if resolved_project_root is None:
        raise ProjectCleanupError(
            code="ERR_VALIDATION",
            message="Rollback apply requires an explicit --project-root.",
            fix_suggestion="ask sdk rollback --receipt <path> --apply --project-root /path/to/project --json --robot",
            receipt={**receipt, "status": "blocked", "files_blocked": _block_all(plan, "missing_project_root")},
        )
    _validate_rollback_lockfile_binding(source_receipt, source_receipt_path, resolved_project_root)
    return _execute_cleanup(
        operation="rollback",
        repo_root=repo_root,
        project_root=resolved_project_root,
        source_receipt_path=source_receipt_path,
        source_receipt_digest=source_digest,
        files_planned=plan,
        skill_id=_skill_id_from_receipt(source_receipt),
    )


def uninstall_project_skill(
    repo_root: Path,
    *,
    skill_id: str,
    project_root: str | None,
    apply: bool,
) -> dict[str, Any]:
    resolved_project_root = _resolve_project_root_for_cleanup(repo_root, project_root, "uninstall")
    lockfile_path = resolved_project_root / DEFAULT_LOCKFILE_PATH
    lockfile = _load_lockfile(lockfile_path, operation="uninstall")
    entry = _lockfile_entry(lockfile, skill_id, resolved_project_root)
    receipt_ref = entry.get("receipt_ref")
    source_receipt_path = (resolved_project_root / str(receipt_ref)).resolve()
    try:
        _relative_to(source_receipt_path, resolved_project_root)
    except ProjectInstallError as exc:
        conflicts = [str(conflict) for conflict in exc.receipt.get("conflicts", [])] or ["unsafe_receipt_ref"]
        raise ProjectCleanupError(
            code=exc.code,
            message=exc.message,
            fix_suggestion=exc.fix_suggestion,
            receipt=_blocked_receipt("uninstall", str(source_receipt_path), str(resolved_project_root), conflicts),
        ) from exc
    source_receipt, source_digest = _load_install_receipt(source_receipt_path, operation="uninstall")
    _validate_receipt_root(source_receipt, resolved_project_root)
    plan = _uninstall_plan(entry, source_receipt, source_receipt_path, source_digest, resolved_project_root)
    _validate_plan_paths(plan, resolved_project_root)
    _classify_current_files(plan, resolved_project_root)
    receipt = _cleanup_receipt(
        operation="uninstall",
        status="preview",
        target_root=str(resolved_project_root),
        source_receipt_path=str(source_receipt_path),
        source_receipt_digest=source_digest,
        files_planned=plan,
        mutation_performed=False,
        live_project_validation=True,
        skill_id=skill_id,
    )
    if not apply:
        return receipt
    return _execute_cleanup(
        operation="uninstall",
        repo_root=repo_root,
        project_root=resolved_project_root,
        source_receipt_path=source_receipt_path,
        source_receipt_digest=source_digest,
        files_planned=plan,
        skill_id=skill_id,
    )


def _resolve_receipt_path(value: str) -> Path:
    if not value:
        raise ProjectCleanupError(
            code="ERR_VALIDATION",
            message="Rollback requires --receipt <path>.",
            fix_suggestion="ask sdk rollback --receipt <path> --preview --json --robot",
            receipt=_blocked_receipt("rollback", "missing", "missing", ["missing_receipt_path"]),
        )
    candidate = Path(value).expanduser()
    if not candidate.is_absolute():
        candidate = Path.cwd() / candidate
    try:
        return candidate.resolve(strict=True)
    except FileNotFoundError as exc:
        raise ProjectCleanupError(
            code="ERR_VALIDATION",
            message=f"Install receipt does not exist: {candidate}",
            fix_suggestion="Pass a readable Skills SDK install receipt.",
            receipt=_blocked_receipt("rollback", str(candidate), "unknown", ["missing_receipt"]),
        ) from exc


def _load_install_receipt(path: Path, *, operation: str) -> tuple[dict[str, Any], str]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ProjectCleanupError(
            code="ERR_VALIDATION",
            message=f"Install receipt does not exist: {path}",
            fix_suggestion="Pass a readable Skills SDK install receipt or repair skills.lock.json.",
            receipt=_blocked_receipt(operation, str(path), "unknown", ["missing_receipt"]),
        ) from exc
    except OSError as exc:
        raise ProjectCleanupError(
            code="ERR_IO",
            message=f"Cannot read install receipt: {path}",
            fix_suggestion="Verify file permissions and that the receipt path is readable.",
            receipt=_blocked_receipt(operation, str(path), "unknown", ["unreadable_receipt"]),
        ) from exc
    except json.JSONDecodeError as exc:
        raise ProjectCleanupError(
            code="ERR_SCHEMA_INVALID",
            message=f"Install receipt JSON is malformed: {path}",
            fix_suggestion="Pass a schema-valid Skills SDK install receipt.",
            receipt=_blocked_receipt(operation, str(path), "unknown", ["malformed_receipt"]),
        ) from exc
    if not isinstance(payload, dict):
        raise ProjectCleanupError(
            code="ERR_SCHEMA_INVALID",
            message="Install receipt root must be an object.",
            fix_suggestion="Pass a schema-valid Skills SDK install receipt.",
            receipt=_blocked_receipt(operation, str(path), "unknown", ["invalid_receipt_root"]),
        )
    conflicts = []
    if payload.get("schema_version") != INSTALL_RECEIPT_SCHEMA_VERSION:
        conflicts.append("unsupported_receipt_schema_version")
    if payload.get("schema_uri") != INSTALL_RECEIPT_SCHEMA_URI:
        conflicts.append("unsupported_receipt_schema_uri")
    if payload.get("operation") != "install":
        conflicts.append("unsupported_receipt_operation")
    if payload.get("scope") != "project":
        conflicts.append("unsupported_receipt_scope")
    if payload.get("status") not in {"success", "partial"}:
        conflicts.append("unsupported_receipt_status")
    if payload.get("mutation_performed") is not True:
        conflicts.append("source_receipt_without_mutation")
    if not isinstance(payload.get("files_written"), list):
        conflicts.append("missing_files_written")
    if not isinstance(payload.get("target_root"), str) or not payload.get("target_root"):
        conflicts.append("missing_target_root")
    digest = _sha256_json(payload)
    if conflicts:
        raise ProjectCleanupError(
            code="ERR_SCHEMA_INVALID",
            message="Install receipt is not valid cleanup authority.",
            fix_suggestion="Pass a successful project install receipt with file metadata.",
            receipt=_blocked_receipt(operation, str(path), str(payload.get("target_root", "unknown")), conflicts, source_digest=digest),
        )
    return payload, digest


def _resolve_cleanup_root(
    repo_root: Path,
    project_root: str | None,
    receipt: dict[str, Any],
    *,
    require_root: bool,
) -> Path | None:
    if not project_root:
        if require_root:
            _resolve_project_root_for_cleanup(repo_root, project_root, "rollback")
        return None
    root = _resolve_project_root_for_cleanup(repo_root, project_root, "rollback")
    _validate_receipt_root(receipt, root)
    return root


def _resolve_project_root_for_cleanup(repo_root: Path, project_root: str | None, operation: str) -> Path:
    try:
        return _resolve_project_root(project_root, repo_root)
    except ProjectInstallError as exc:
        target_root = str(exc.receipt.get("target_root") or project_root or "missing")
        conflicts = [str(conflict) for conflict in exc.receipt.get("conflicts", [])] or ["invalid_project_root"]
        raise ProjectCleanupError(
            code=exc.code,
            message=exc.message,
            fix_suggestion=exc.fix_suggestion,
            receipt=_blocked_receipt(operation, "unknown", target_root, conflicts),
        ) from exc


def _validate_receipt_root(receipt: dict[str, Any], root: Path) -> None:
    try:
        receipt_root = Path(str(receipt["target_root"])).expanduser().resolve(strict=True)
    except FileNotFoundError as exc:
        raise ProjectCleanupError(
            code="ERR_VALIDATION",
            message="Install receipt target_root no longer exists.",
            fix_suggestion="Pass the original project root or inspect the receipt manually.",
            receipt=_blocked_receipt("rollback", "unknown", str(root), ["missing_receipt_target_root"]),
        ) from exc
    if receipt_root != root:
        raise ProjectCleanupError(
            code="ERR_VALIDATION",
            message="Install receipt target_root does not match --project-root.",
            fix_suggestion="Use the project root recorded by the install receipt.",
            receipt=_blocked_receipt("rollback", "unknown", str(root), ["mismatched_project_root"]),
        )


def _load_lockfile(path: Path, *, operation: str = "uninstall") -> dict[str, Any]:
    if not path.is_file():
        raise ProjectCleanupError(
            code="ERR_VALIDATION",
            message=f"skills.lock.json is required for {operation}.",
            fix_suggestion=f"Run {operation} in the project root that owns the installed skill.",
            receipt=_blocked_receipt(operation, "missing", str(path.parent), ["missing_lockfile"]),
        )
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ProjectCleanupError(
            code="ERR_SCHEMA_INVALID",
            message="skills.lock.json is malformed.",
            fix_suggestion=f"Repair skills.lock.json or restore it from version control before {operation}.",
            receipt=_blocked_receipt(operation, str(path), str(path.parent), ["malformed_lockfile"]),
        ) from exc
    if (
        not isinstance(payload, dict)
        or payload.get("schema_version") != LOCKFILE_SCHEMA_VERSION
        or payload.get("schema_uri") != LOCKFILE_SCHEMA_URI
        or not isinstance(payload.get("entries"), dict)
    ):
        raise ProjectCleanupError(
            code="ERR_SCHEMA_INVALID",
            message="skills.lock.json is not a supported Skills SDK lockfile.",
            fix_suggestion="Use a project lockfile written by ask sdk install --apply.",
            receipt=_blocked_receipt(operation, str(path), str(path.parent), ["unsupported_lockfile_schema"]),
        )
    return payload


def _validate_rollback_lockfile_binding(receipt: dict[str, Any], receipt_path: Path, project_root: Path) -> None:
    lockfile = _load_lockfile(project_root / DEFAULT_LOCKFILE_PATH, operation="rollback")
    try:
        receipt_ref = _relative_to(receipt_path, project_root)
    except ProjectInstallError as exc:
        conflicts = [str(conflict) for conflict in exc.receipt.get("conflicts", [])] or ["unsafe_receipt_ref"]
        raise ProjectCleanupError(
            code=exc.code,
            message=exc.message,
            fix_suggestion=exc.fix_suggestion,
            receipt=_blocked_receipt("rollback", str(receipt_path), str(project_root), conflicts),
        ) from exc
    matches = [entry for entry in lockfile["entries"].values() if isinstance(entry, dict) and entry.get("receipt_ref") == receipt_ref]
    if len(matches) != 1:
        raise ProjectCleanupError(
            code="ERR_CONFLICT",
            message="Install receipt is not bound to exactly one active lockfile entry.",
            fix_suggestion="Use the active install receipt referenced by skills.lock.json or repair the lockfile before rollback.",
            receipt=_blocked_receipt("rollback", str(receipt_path), str(project_root), ["mismatched_lockfile_receipt_binding"]),
        )
    _validate_entry_receipt_files("rollback", matches[0], receipt, project_root)


def _lockfile_entry(lockfile: dict[str, Any], skill_id: str, project_root: Path) -> dict[str, Any]:
    entries = lockfile["entries"]
    matches = [entry for key, entry in entries.items() if key == skill_id or entry.get("name") == skill_id]
    if not matches:
        raise ProjectCleanupError(
            code="ERR_VALIDATION",
            message=f"No active Skills SDK install matched skill id '{skill_id}'.",
            fix_suggestion="Run ask sdk uninstall <skill-id> from the project root containing skills.lock.json.",
            receipt=_blocked_receipt("uninstall", skill_id, str(project_root), ["unknown_skill_id"]),
        )
    if len(matches) != 1:
        raise ProjectCleanupError(
            code="ERR_CONFLICT",
            message=f"Multiple active lockfile entries matched skill id '{skill_id}'.",
            fix_suggestion="Use a future install-instance cleanup slice or repair duplicate lockfile entries manually.",
            receipt=_blocked_receipt("uninstall", skill_id, str(project_root), ["duplicate_active_skill_id"]),
        )
    entry = matches[0]
    if not isinstance(entry, dict) or not entry.get("receipt_ref"):
        raise ProjectCleanupError(
            code="ERR_SCHEMA_INVALID",
            message=f"Lockfile entry for '{skill_id}' is missing receipt_ref.",
            fix_suggestion="Repair the lockfile entry or use rollback with the install receipt.",
            receipt=_blocked_receipt("uninstall", skill_id, str(project_root), ["missing_receipt_ref"]),
        )
    return entry


def _rollback_plan(
    receipt: dict[str, Any],
    receipt_path: Path,
    receipt_digest: str,
    project_root: Path | None,
) -> list[dict[str, Any]]:
    del receipt_path, receipt_digest
    files = []
    for item in receipt.get("files_written", []):
        if isinstance(item, dict) and isinstance(item.get("target_path"), str) and isinstance(item.get("digest"), str):
            files.append(_planned_file(item["target_path"], item["digest"], "remove"))
    if not files:
        raise ProjectCleanupError(
            code="ERR_VALIDATION",
            message="Install receipt has no written file metadata to clean up.",
            fix_suggestion="Use a receipt with files_written records or perform manual cleanup.",
            receipt=_blocked_receipt("rollback", "unknown", str(project_root or receipt.get("target_root", "unknown")), ["missing_written_file_metadata"]),
        )
    return files


def _validate_entry_receipt_files(operation: str, entry: dict[str, Any], receipt: dict[str, Any], project_root: Path) -> list[dict[str, Any]]:
    receipt_files = {
        item.get("target_path"): item
        for item in receipt.get("files_written", [])
        if isinstance(item, dict) and isinstance(item.get("target_path"), str)
    }
    files = []
    for item in entry.get("files", []):
        target_path = item.get("target_path") if isinstance(item, dict) else None
        digest = item.get("digest") if isinstance(item, dict) else None
        if not isinstance(target_path, str) or not isinstance(digest, str):
            continue
        receipt_item = receipt_files.get(target_path)
        if not receipt_item or receipt_item.get("digest") != digest:
            raise ProjectCleanupError(
                code="ERR_CONFLICT",
                message="Lockfile and install receipt file metadata do not match.",
                fix_suggestion="Inspect skills.lock.json and the install receipt before cleanup.",
                receipt=_blocked_receipt(operation, str(entry.get("name", "unknown")), str(project_root), ["mismatched_lockfile_receipt_binding"]),
            )
        files.append(_planned_file(target_path, digest, "remove"))
    if not files:
        raise ProjectCleanupError(
            code="ERR_VALIDATION",
            message="Lockfile entry has no file metadata to clean up.",
            fix_suggestion="Repair skills.lock.json or perform manual cleanup.",
            receipt=_blocked_receipt(operation, str(entry.get("name", "unknown")), str(project_root), ["missing_lockfile_file_metadata"]),
        )
    return files


def _uninstall_plan(
    entry: dict[str, Any],
    receipt: dict[str, Any],
    receipt_path: Path,
    receipt_digest: str,
    project_root: Path,
) -> list[dict[str, Any]]:
    del receipt_path, receipt_digest
    return _validate_entry_receipt_files("uninstall", entry, receipt, project_root)


def _planned_file(target_path: str, digest: str, action: str) -> dict[str, Any]:
    return {
        "target_path": target_path,
        "expected_digest": digest,
        "action": action,
        "status": "planned",
        "reason": "receipt_proven",
    }


def _validate_plan_paths(files: list[dict[str, Any]], project_root: Path) -> None:
    for item in files:
        relative = Path(item["target_path"])
        if relative.is_absolute() or ".." in relative.parts:
            item["status"] = "blocked"
            item["reason"] = "path_escape"
            continue
        conflicts = _metadata_path_conflicts(project_root, relative)
        if conflicts:
            item["status"] = "blocked"
            item["reason"] = conflicts[0]
            continue
        target = (project_root / relative).resolve()
        try:
            _relative_to(target, project_root)
        except Exception:
            item["status"] = "blocked"
            item["reason"] = "path_escape"
            continue
        _case_collision_status(project_root, relative, item)


def _case_collision_status(project_root: Path, relative: Path, item: dict[str, Any]) -> None:
    current = project_root
    for part in relative.parts:
        if not current.is_dir():
            return
        matches = [child.name for child in current.iterdir() if child.name.lower() == part.lower()]
        if len(set(matches)) > 1:
            item["status"] = "blocked"
            item["reason"] = "case_colliding_path"
            return
        current = current / part


def _classify_current_files(files: list[dict[str, Any]], project_root: Path) -> None:
    for item in files:
        if item["status"] == "blocked":
            continue
        target = project_root / item["target_path"]
        if not target.exists():
            item["status"] = "skipped"
            item["reason"] = "already_absent"
            continue
        try:
            metadata = target.lstat()
        except OSError:
            item["status"] = "blocked"
            item["reason"] = "lstat_failed"
            continue
        if stat.S_ISLNK(metadata.st_mode):
            item["status"] = "blocked"
            item["reason"] = "target_symlink"
            continue
        if not stat.S_ISREG(metadata.st_mode):
            item["status"] = "blocked"
            item["reason"] = "target_not_regular_file"
            continue
        if metadata.st_nlink > 1:
            item["status"] = "blocked"
            item["reason"] = "target_hardlink"
            continue
        current_digest = _sha256_file(target)
        item["current_digest"] = current_digest
        if current_digest != item["expected_digest"]:
            item["status"] = "skipped"
            item["reason"] = "modified_file_digest_mismatch"
            continue
        item["status"] = "ready"
        item["reason"] = "digest_match"


def _execute_cleanup(
    *,
    operation: str,
    repo_root: Path,
    project_root: Path,
    source_receipt_path: Path,
    source_receipt_digest: str,
    files_planned: list[dict[str, Any]],
    skill_id: str | None,
) -> dict[str, Any]:
    del repo_root
    blocked = [item for item in files_planned if item["status"] == "blocked"]
    ready = [item for item in files_planned if item["status"] == "ready"]
    skipped = [item for item in files_planned if item["status"] == "skipped"]
    if blocked:
        receipt = _cleanup_receipt(
            operation=operation,
            status="blocked",
            target_root=str(project_root),
            source_receipt_path=str(source_receipt_path),
            source_receipt_digest=source_receipt_digest,
            files_planned=files_planned,
            mutation_performed=False,
            live_project_validation=True,
            skill_id=skill_id,
        )
        raise ProjectCleanupError(
            code="ERR_CONFLICT",
            message=f"{operation} blocked before mutation because at least one file is unsafe.",
            fix_suggestion="Inspect files_blocked and resolve unsafe paths before retrying.",
            receipt=receipt,
        )
    journal_path = _journal_path(project_root, operation, source_receipt_digest, skill_id)
    if journal_path.exists():
        receipt = _cleanup_receipt(
            operation=operation,
            status="blocked",
            target_root=str(project_root),
            source_receipt_path=str(source_receipt_path),
            source_receipt_digest=source_receipt_digest,
            files_planned=files_planned,
            mutation_performed=False,
            live_project_validation=True,
            skill_id=skill_id,
            journal_path=_relative_to(journal_path, project_root),
        )
        receipt["manual_actions"].append({"path": _relative_to(journal_path, project_root), "reason": "unresolved_cleanup_journal"})
        raise ProjectCleanupError(
            code="ERR_CONFLICT",
            message="Cleanup journal already exists for this operation.",
            fix_suggestion="Inspect the journal and rerun after manual recovery.",
            receipt=receipt,
        )
    conflicts = []
    for metadata_relative in (CLEANUP_JOURNAL_DIR / journal_path.name, CLEANUP_RECEIPT_DIR / _receipt_name(operation, source_receipt_digest, skill_id)):
        conflicts.extend(_metadata_path_conflicts(project_root, metadata_relative))
    if conflicts:
        raise ProjectCleanupError(
            code="ERR_CONFLICT",
            message="Refusing to write cleanup metadata through an unsafe target path.",
            fix_suggestion="Remove the conflicting metadata path or choose another project root.",
            receipt=_blocked_receipt(operation, str(source_receipt_path), str(project_root), conflicts, source_digest=source_receipt_digest),
        )
    journal = {
        "schema_version": "skills-sdk.cleanup-journal.v1",
        "operation": operation,
        "target_root": str(project_root),
        "source_receipt_path": str(source_receipt_path),
        "source_receipt_digest": source_receipt_digest,
        "skill_id": skill_id,
        "pending_actions": ready,
        "completed_actions": [],
    }
    _json_atomic_replace(journal_path, journal)
    if os.environ.get("ASK_SKILLS_SDK_CLEANUP_INTERRUPT_AFTER_JOURNAL") == "1":
        receipt = _cleanup_receipt(
            operation=operation,
            status="blocked",
            target_root=str(project_root),
            source_receipt_path=str(source_receipt_path),
            source_receipt_digest=source_receipt_digest,
            files_planned=files_planned,
            mutation_performed=False,
            live_project_validation=True,
            skill_id=skill_id,
            journal_path=_relative_to(journal_path, project_root),
        )
        receipt["manual_actions"].append(
            {"path": _relative_to(journal_path, project_root), "reason": "interrupted_after_cleanup_journal"}
        )
        raise ProjectCleanupError(
            code="ERR_CONFLICT",
            message="Cleanup interrupted after journal write before filesystem mutation.",
            fix_suggestion="Inspect the cleanup journal and rerun after manual recovery.",
            receipt=receipt,
        )
    removed = []
    directory_prune_results: list[dict[str, Any]] = []
    mutation_performed = False
    parent_dirs_to_prune: set[Path] = set()
    try:
        for item in ready:
            target = project_root / item["target_path"]
            target.unlink()
            mutation_performed = True
            removed.append({**item, "status": "removed"})
            parent_dirs_to_prune.add(target.parent)
        for parent_dir in parent_dirs_to_prune:
            directory_prune_results.extend(_prune_empty_owned_dirs(parent_dir, project_root))
        lockfile_change = (
            {
                "path": DEFAULT_LOCKFILE_PATH,
                "changed": False,
                "reason": "partial_cleanup_preserves_lockfile_entry",
            }
            if skipped
            else _update_lockfile_after_cleanup(project_root, operation, skill_id, source_receipt_path)
        )
        if lockfile_change["changed"]:
            mutation_performed = True
        receipt = _cleanup_receipt(
            operation=operation,
            status="success" if not skipped else "partial",
            target_root=str(project_root),
            source_receipt_path=str(source_receipt_path),
            source_receipt_digest=source_receipt_digest,
            files_planned=[*removed, *skipped],
            mutation_performed=mutation_performed,
            live_project_validation=True,
            skill_id=skill_id,
            journal_path=_relative_to(journal_path, project_root),
            lockfile_changes=[lockfile_change] if lockfile_change["changed"] else [],
            directory_prune_results=directory_prune_results,
        )
        receipt_path = project_root / CLEANUP_RECEIPT_DIR / _receipt_name(operation, source_receipt_digest, skill_id)
        _json_atomic_replace(receipt_path, receipt)
        journal_path.unlink(missing_ok=True)
        return {**receipt, "receipt_path": _relative_to(receipt_path, project_root)}
    except OSError as exc:
        receipt = _cleanup_receipt(
            operation=operation,
            status="partial" if mutation_performed else "blocked",
            target_root=str(project_root),
            source_receipt_path=str(source_receipt_path),
            source_receipt_digest=source_receipt_digest,
            files_planned=[*removed, *ready[len(removed):], *skipped],
            mutation_performed=mutation_performed,
            live_project_validation=True,
            skill_id=skill_id,
            journal_path=_relative_to(journal_path, project_root),
            directory_prune_results=directory_prune_results,
        )
        raise ProjectCleanupError(
            code="ERR_RUNTIME",
            message=f"{operation} failed during cleanup: {exc}",
            fix_suggestion="Inspect the cleanup journal and receipt before retrying.",
            receipt=receipt,
        ) from exc


def _update_lockfile_after_cleanup(project_root: Path, operation: str, skill_id: str | None, source_receipt_path: Path) -> dict[str, Any]:
    lockfile_path = project_root / DEFAULT_LOCKFILE_PATH
    before_digest = _sha256_file(lockfile_path) if lockfile_path.is_file() else None
    if not lockfile_path.is_file():
        return {"path": DEFAULT_LOCKFILE_PATH, "changed": False, "operation": operation, "removed_entries": [], "reason": "missing_lockfile", "before_digest": before_digest, "after_digest": before_digest}
    lockfile = _load_lockfile(lockfile_path)
    receipt_ref = _relative_to(source_receipt_path, project_root)
    entries = lockfile["entries"]
    removed_keys = []
    for key, entry in list(entries.items()):
        if (skill_id and (key == skill_id or entry.get("name") == skill_id)) or entry.get("receipt_ref") == receipt_ref:
            removed_keys.append(key)
            del entries[key]
    if not removed_keys:
        return {"path": DEFAULT_LOCKFILE_PATH, "changed": False, "operation": operation, "removed_entries": [], "reason": "no_matching_entry", "before_digest": before_digest, "after_digest": before_digest}
    _json_atomic_replace(lockfile_path, lockfile)
    return {
        "path": DEFAULT_LOCKFILE_PATH,
        "changed": True,
        "operation": operation,
        "removed_entries": removed_keys,
        "before_digest": before_digest,
        "after_digest": _sha256_file(lockfile_path),
    }


def _prune_empty_owned_dirs(path: Path, project_root: Path) -> list[dict[str, Any]]:
    skill_root = project_root / ".agents" / "skills"
    current = path
    results: list[dict[str, Any]] = []
    while current != project_root and current != skill_root.parent and current.is_relative_to(skill_root):
        relative = _relative_to(current, project_root)
        try:
            current.rmdir()
        except OSError:
            results.append({"path": relative, "pruned": False, "reason": "not_empty_or_unavailable"})
            return results
        results.append({"path": relative, "pruned": True, "reason": "empty_owned_directory"})
        current = current.parent
    return results


def _journal_path(project_root: Path, operation: str, source_digest: str, skill_id: str | None) -> Path:
    token = _safe_token(f"{operation}-{skill_id or 'receipt'}-{source_digest}")
    return project_root / CLEANUP_JOURNAL_DIR / f"{token}.json"


def _receipt_name(operation: str, source_digest: str, skill_id: str | None) -> str:
    return f"{_safe_token(f'{operation}-{skill_id or source_digest}')}.json"


def _safe_token(value: str) -> str:
    return "".join(ch if ch.isalnum() else "-" for ch in value.replace("sha256:", ""))[:96].strip("-") or "cleanup"


def _skill_id_from_receipt(receipt: dict[str, Any]) -> str | None:
    files = receipt.get("files_written")
    if not isinstance(files, list) or not files:
        return None
    first = files[0]
    if not isinstance(first, dict):
        return None
    parts = Path(str(first.get("target_path", ""))).parts
    if len(parts) >= 3 and parts[0] == ".agents" and parts[1] == "skills":
        return parts[2]
    return None


def _cleanup_receipt(
    *,
    operation: str,
    status: str,
    target_root: str,
    source_receipt_path: str,
    source_receipt_digest: str,
    files_planned: list[dict[str, Any]],
    mutation_performed: bool,
    live_project_validation: bool,
    skill_id: str | None = None,
    journal_path: str | None = None,
    lockfile_changes: list[dict[str, Any]] | None = None,
    directory_prune_results: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    removed = [item for item in files_planned if item["status"] == "removed"]
    skipped = [item for item in files_planned if item["status"] == "skipped"]
    blocked = [item for item in files_planned if item["status"] == "blocked"]
    restored: list[dict[str, Any]] = []
    manual_actions = [
        {"path": item["target_path"], "reason": item["reason"]}
        for item in [*skipped, *blocked]
        if item["reason"] not in {"already_absent"}
    ]
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
        "files_restored": restored,
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
