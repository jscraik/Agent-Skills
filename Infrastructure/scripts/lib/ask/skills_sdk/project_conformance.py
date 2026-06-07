from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, cast

from ask.skills_sdk.project_install import (
    DEFAULT_LOCKFILE_PATH,
    INSTALL_RECEIPT_SCHEMA_URI,
    INSTALL_RECEIPT_SCHEMA_VERSION,
    LOCKFILE_SCHEMA_URI,
    LOCKFILE_SCHEMA_VERSION,
    ProjectInstallError,
    _relative_to,
    _resolve_project_root,
    _sha256_file,
    _sha256_json,
)


PROJECT_CONFORMANCE_SCHEMA_VERSION = "skills-sdk.project-conformance-receipt.v1"
PROJECT_CONFORMANCE_SCHEMA_URI = (
    "https://jscraik.local/agent-skills/schemas/skills-sdk/project-conformance-receipt.v1.schema.json"
)
PROJECT_CONFORMANCE_ACCEPTANCE_TRACE = [
    "PU-012-FR-001",
    "PU-012-FR-002",
    "PU-012-FR-003",
    "PU-012-SA-001",
    "PU-012-SA-002",
    "PU-012-VP-001",
]

ConformanceMode = Literal["status", "doctor"]
ConformanceStatus = Literal["pass", "warning", "blocked"]


@dataclass(frozen=True)
class ProjectConformanceError(Exception):
    code: str
    message: str
    fix_suggestion: str
    receipt: dict[str, object]


def build_project_conformance_receipt(
    repo_root: Path,
    *,
    project_root: str | None,
    mode: ConformanceMode,
) -> dict[str, object]:
    if mode not in {"status", "doctor"}:
        raise ValueError(f"unsupported project conformance mode: {mode}")
    resolved_project_root = _resolve_conformance_root(repo_root, project_root, mode)
    lockfile_path = resolved_project_root / DEFAULT_LOCKFILE_PATH
    receipt = _base_receipt(
        command=f"skills-sdk project {mode}",
        mode=mode,
        project_root=str(resolved_project_root),
        project_managed=True,
        lockfile_path=DEFAULT_LOCKFILE_PATH,
        lockfile_status="missing",
        status="pass",
    )
    if not lockfile_path.exists():
        receipt["agent_summary"] = "Project is marked for Skills SDK adoption and has no installed skills yet."
        return receipt
    if not lockfile_path.is_file():
        issue = _issue("lockfile_not_file", "blocker", "skills.lock.json is not a regular file.", DEFAULT_LOCKFILE_PATH)
        receipt["issues"] = [issue]
        receipt["manual_actions"] = [_manual_action("repair_lockfile", "Replace skills.lock.json with a regular lockfile.", DEFAULT_LOCKFILE_PATH)]
        receipt["lockfile_status"] = "invalid"
        receipt["status"] = "blocked"
        receipt["agent_summary"] = "Project conformance is blocked because skills.lock.json is not a regular file."
        raise _blocked_error(receipt, "skills.lock.json is not a regular file.")

    lockfile = _load_lockfile(lockfile_path, receipt)
    entries = lockfile.get("entries")
    if not isinstance(entries, dict):
        issue = _issue("invalid_lockfile_entries", "blocker", "skills.lock.json entries must be an object.", DEFAULT_LOCKFILE_PATH)
        receipt["issues"] = [issue]
        receipt["manual_actions"] = [_manual_action("repair_lockfile", "Regenerate skills.lock.json from valid install receipts.", DEFAULT_LOCKFILE_PATH)]
        receipt["lockfile_status"] = "invalid"
        receipt["status"] = "blocked"
        receipt["agent_summary"] = "Project conformance is blocked because skills.lock.json has invalid entries."
        raise _blocked_error(receipt, "skills.lock.json has invalid entries.")

    rows: list[dict[str, object]] = []
    issues: list[dict[str, object]] = []
    manual_actions: list[dict[str, object]] = []
    for skill_id, entry_value in sorted(entries.items(), key=lambda item: str(item[0])):
        row, row_issues, row_actions = _inspect_lockfile_entry(
            resolved_project_root,
            skill_id=str(skill_id),
            entry_value=entry_value,
        )
        rows.append(row)
        issues.extend(row_issues)
        manual_actions.extend(row_actions)

    receipt["installed_skills"] = rows
    receipt["issues"] = issues
    receipt["manual_actions"] = manual_actions
    receipt["installed_skill_count"] = len(rows)
    receipt["rollback_ready_count"] = sum(1 for row in rows if row.get("rollback_ready") is True)
    receipt["uninstall_ready_count"] = sum(1 for row in rows if row.get("uninstall_ready") is True)
    receipt["lockfile_status"] = "valid" if not issues else "valid_with_diagnostics"
    status: ConformanceStatus = "pass"
    if any(issue.get("severity") == "blocker" for issue in issues):
        status = "blocked"
    elif issues:
        status = "warning"
    receipt["status"] = status
    receipt["agent_summary"] = _agent_summary(receipt)
    if status == "blocked":
        raise _blocked_error(receipt, str(receipt["agent_summary"]))
    return receipt


def _resolve_conformance_root(repo_root: Path, project_root: str | None, mode: ConformanceMode) -> Path:
    try:
        root = _resolve_project_root(project_root, repo_root)
    except ProjectInstallError as exc:
        receipt = _base_receipt(
            command=f"skills-sdk project {mode}",
            mode=mode,
            project_root=str(exc.receipt.get("target_root") or project_root or "missing"),
            project_managed=False,
            lockfile_path=None,
            lockfile_status="not_checked",
            status="blocked",
        )
        conflicts = [str(item) for item in _list_value(exc.receipt.get("conflicts"))] or [exc.code.lower()]
        receipt["issues"] = [
            _issue(conflict, "blocker", exc.message, str(exc.receipt.get("target_root") or project_root or "missing"))
            for conflict in conflicts
        ]
        receipt["manual_actions"] = [
            _manual_action("choose_project_root", exc.fix_suggestion, str(exc.receipt.get("target_root") or project_root or "missing"))
        ]
        receipt["agent_summary"] = exc.message
        raise ProjectConformanceError(exc.code, exc.message, exc.fix_suggestion, receipt) from exc
    repo_identity = repo_root.resolve()
    if root != repo_identity and repo_identity.is_relative_to(root):
        receipt = _base_receipt(
            command=f"skills-sdk project {mode}",
            mode=mode,
            project_root=str(root),
            project_managed=False,
            lockfile_path=None,
            lockfile_status="not_checked",
            status="blocked",
        )
        message = "Refusing to treat an ancestor of the live agent-skills repository as a project root."
        receipt["issues"] = [_issue("live_repo_ancestor_root", "blocker", message, str(root))]
        receipt["manual_actions"] = [_manual_action("choose_project_root", "Use a separate marked project checkout.", str(root))]
        receipt["agent_summary"] = message
        raise ProjectConformanceError("ERR_VALIDATION", message, "Use a separate marked project checkout.", receipt)
    return root


def _load_lockfile(path: Path, receipt: dict[str, object]) -> dict[str, object]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        issue = _issue("malformed_lockfile", "blocker", f"skills.lock.json is malformed JSON: {exc}", DEFAULT_LOCKFILE_PATH)
        receipt["issues"] = [issue]
        receipt["manual_actions"] = [_manual_action("repair_lockfile", "Replace skills.lock.json with valid JSON.", DEFAULT_LOCKFILE_PATH)]
        receipt["lockfile_status"] = "invalid"
        receipt["status"] = "blocked"
        receipt["agent_summary"] = "Project conformance is blocked because skills.lock.json is malformed."
        raise _blocked_error(receipt, "skills.lock.json is malformed.") from exc
    if not isinstance(payload, dict):
        issue = _issue("invalid_lockfile_root", "blocker", "skills.lock.json root must be an object.", DEFAULT_LOCKFILE_PATH)
        receipt["issues"] = [issue]
        receipt["manual_actions"] = [_manual_action("repair_lockfile", "Regenerate skills.lock.json as an object.", DEFAULT_LOCKFILE_PATH)]
        receipt["lockfile_status"] = "invalid"
        receipt["status"] = "blocked"
        receipt["agent_summary"] = "Project conformance is blocked because skills.lock.json root is invalid."
        raise _blocked_error(receipt, "skills.lock.json root is invalid.")
    conflicts: list[str] = []
    if payload.get("schema_version") != LOCKFILE_SCHEMA_VERSION:
        conflicts.append("unsupported_lockfile_schema_version")
    if payload.get("schema_uri") != LOCKFILE_SCHEMA_URI:
        conflicts.append("unsupported_lockfile_schema_uri")
    if conflicts:
        receipt["issues"] = [
            _issue(conflict, "blocker", "skills.lock.json schema identity is unsupported.", DEFAULT_LOCKFILE_PATH)
            for conflict in conflicts
        ]
        receipt["manual_actions"] = [_manual_action("repair_lockfile", "Regenerate skills.lock.json with the current SDK.", DEFAULT_LOCKFILE_PATH)]
        receipt["lockfile_status"] = "unsupported"
        receipt["status"] = "blocked"
        receipt["agent_summary"] = "Project conformance is blocked because skills.lock.json has an unsupported schema identity."
        raise _blocked_error(receipt, "skills.lock.json has an unsupported schema identity.")
    return cast(dict[str, object], payload)


def _inspect_lockfile_entry(
    project_root: Path,
    *,
    skill_id: str,
    entry_value: object,
) -> tuple[dict[str, object], list[dict[str, object]], list[dict[str, object]]]:
    issues: list[dict[str, object]] = []
    actions: list[dict[str, object]] = []
    if not isinstance(entry_value, dict):
        row = _skill_row(skill_id, "unresolved", "missing", "invalid", "blocked", False, False, ["invalid_lockfile_entry"])
        issues.append(_issue("invalid_lockfile_entry", "blocker", "Lockfile entry must be an object.", DEFAULT_LOCKFILE_PATH, skill_id))
        actions.append(_manual_action("repair_lockfile_entry", "Regenerate this lockfile entry from a valid receipt.", DEFAULT_LOCKFILE_PATH, skill_id))
        return row, issues, actions
    entry = cast(dict[str, object], entry_value)
    target_path = _string_value(entry.get("target_path")) or "unresolved"
    receipt_ref = _string_value(entry.get("receipt_ref")) or "missing"
    row_issue_codes: list[str] = []
    receipt_issue_codes: list[str] = []

    receipt_payload: dict[str, object] | None = None
    receipt_digest = "sha256:missing"
    if receipt_ref == "missing":
        row_issue_codes.append("missing_receipt_ref")
        receipt_issue_codes.append("missing_receipt_ref")
        issues.append(_issue("missing_receipt_ref", "blocker", "Lockfile entry has no receipt_ref.", DEFAULT_LOCKFILE_PATH, skill_id))
    else:
        receipt_path = _resolve_inside_project(project_root, receipt_ref)
        if receipt_path is None:
            row_issue_codes.append("unsafe_receipt_ref")
            receipt_issue_codes.append("unsafe_receipt_ref")
            issues.append(_issue("unsafe_receipt_ref", "blocker", "receipt_ref escapes the project root.", receipt_ref, skill_id))
        elif not receipt_path.is_file():
            row_issue_codes.append("missing_receipt")
            receipt_issue_codes.append("missing_receipt")
            issues.append(_issue("missing_receipt", "blocker", "Install receipt referenced by skills.lock.json is missing.", receipt_ref, skill_id))
        else:
            receipt_payload, receipt_digest, receipt_conflicts = _load_install_receipt_for_status(receipt_path, project_root)
            row_issue_codes.extend(receipt_conflicts)
            receipt_issue_codes.extend(receipt_conflicts)
            for conflict in receipt_conflicts:
                issues.append(_issue(conflict, "blocker", "Install receipt is not valid project cleanup authority.", receipt_ref, skill_id))

    file_conflicts = _inspect_installed_files(project_root, entry, receipt_payload, skill_id)
    row_issue_codes.extend(file_conflicts)
    for conflict in file_conflicts:
        path = conflict.split(":", 1)[1] if ":" in conflict else target_path
        issues.append(_issue(conflict.split(":", 1)[0], "blocker", "Installed file metadata does not match the project state.", path, skill_id))

    for issue in row_issue_codes:
        actions.append(_manual_action("manual_review", f"Resolve {issue} before rollback or uninstall.", target_path, skill_id))

    blocked = bool(row_issue_codes)
    return (
        _skill_row(
            skill_id,
            target_path,
            receipt_ref,
            "valid" if receipt_payload is not None and not receipt_issue_codes else ("missing" if receipt_digest == "sha256:missing" else "invalid"),
            "healthy" if not blocked else "blocked",
            not blocked,
            not blocked,
            row_issue_codes,
        ),
        issues,
        actions,
    )


def _load_install_receipt_for_status(path: Path, project_root: Path) -> tuple[dict[str, object] | None, str, list[str]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None, "sha256:malformed", ["malformed_receipt"]
    if not isinstance(payload, dict):
        return None, "sha256:invalid", ["invalid_receipt_root"]
    receipt = cast(dict[str, object], payload)
    digest = _sha256_json(receipt)
    conflicts: list[str] = []
    if receipt.get("schema_version") != INSTALL_RECEIPT_SCHEMA_VERSION:
        conflicts.append("unsupported_receipt_schema_version")
    if receipt.get("schema_uri") != INSTALL_RECEIPT_SCHEMA_URI:
        conflicts.append("unsupported_receipt_schema_uri")
    if receipt.get("operation") != "install":
        conflicts.append("unsupported_receipt_operation")
    if receipt.get("scope") != "project":
        conflicts.append("unsupported_receipt_scope")
    if receipt.get("mutation_performed") is not True:
        conflicts.append("source_receipt_without_mutation")
    target_root = _string_value(receipt.get("target_root"))
    if not target_root or Path(target_root).resolve() != project_root:
        conflicts.append("receipt_project_root_mismatch")
    if not isinstance(receipt.get("files_written"), list):
        conflicts.append("missing_files_written")
    return (receipt if not conflicts else None), digest, conflicts


def _inspect_installed_files(
    project_root: Path,
    entry: dict[str, object],
    receipt: dict[str, object] | None,
    skill_id: str,
) -> list[str]:
    conflicts: list[str] = []
    files_value = entry.get("files")
    files = files_value if isinstance(files_value, list) else []
    receipt_files = receipt.get("files_written") if receipt is not None else []
    if not files and isinstance(receipt_files, list):
        files = receipt_files
    if not files:
        return ["missing_file_metadata"]
    for item in files:
        if not isinstance(item, dict):
            conflicts.append("invalid_file_metadata")
            continue
        metadata = cast(dict[str, object], item)
        target_path = _string_value(metadata.get("target_path"))
        expected_digest = _string_value(metadata.get("digest"))
        if not target_path or not expected_digest:
            conflicts.append("invalid_file_metadata")
            continue
        target = _resolve_inside_project(project_root, target_path)
        if target is None:
            conflicts.append(f"file_path_escape:{target_path}")
            continue
        if not target.is_file():
            conflicts.append(f"installed_file_missing:{target_path}")
            continue
        actual_digest = _sha256_file(target)
        if actual_digest != expected_digest:
            conflicts.append(f"installed_file_modified:{target_path}")
    if skill_id and _string_value(entry.get("name")) not in {None, skill_id}:
        conflicts.append("skill_id_name_mismatch")
    return conflicts


def _resolve_inside_project(project_root: Path, relative_path: str) -> Path | None:
    try:
        resolved = (project_root / relative_path).resolve()
        _relative_to(resolved, project_root)
    except ProjectInstallError:
        return None
    return resolved


def _base_receipt(
    *,
    command: str,
    mode: ConformanceMode,
    project_root: str,
    project_managed: bool,
    lockfile_path: str | None,
    lockfile_status: str,
    status: ConformanceStatus,
) -> dict[str, object]:
    return {
        "schema_version": PROJECT_CONFORMANCE_SCHEMA_VERSION,
        "schema_uri": PROJECT_CONFORMANCE_SCHEMA_URI,
        "command": command,
        "mode": mode,
        "status": status,
        "project_root": project_root,
        "project_root_identity": _project_identity(project_root),
        "project_managed": project_managed,
        "lockfile_path": lockfile_path,
        "lockfile_status": lockfile_status,
        "installed_skill_count": 0,
        "installed_skills": [],
        "rollback_ready_count": 0,
        "uninstall_ready_count": 0,
        "issues": [],
        "manual_actions": [],
        "mutation_performed": False,
        "acceptance_trace": PROJECT_CONFORMANCE_ACCEPTANCE_TRACE,
        "agent_summary": "Project conformance status has not been evaluated.",
    }


def _project_identity(project_root: str) -> dict[str, object]:
    if project_root in {"missing", "unresolved", ""}:
        return {"identity_kind": "unresolved", "realpath": project_root}
    path = Path(project_root)
    exists = path.exists()
    return {
        "identity_kind": "realpath",
        "realpath": str(path.resolve()) if exists else project_root,
        "exists": exists,
    }


def _skill_row(
    skill_id: str,
    target_path: str,
    receipt_ref: str,
    receipt_status: str,
    status: str,
    rollback_ready: bool,
    uninstall_ready: bool,
    issue_codes: list[str],
) -> dict[str, object]:
    return {
        "skill_id": skill_id,
        "target_path": target_path,
        "receipt_ref": receipt_ref,
        "receipt_status": receipt_status,
        "status": status,
        "rollback_ready": rollback_ready,
        "uninstall_ready": uninstall_ready,
        "issue_codes": issue_codes,
    }


def _issue(
    code: str,
    severity: Literal["info", "warning", "blocker"],
    message: str,
    path: str,
    skill_id: str | None = None,
) -> dict[str, object]:
    return {
        "code": code,
        "severity": severity,
        "message": message,
        "path": path,
        "skill_id": skill_id,
    }


def _manual_action(action: str, reason: str, path: str, skill_id: str | None = None) -> dict[str, object]:
    return {
        "action": action,
        "reason": reason,
        "path": path,
        "skill_id": skill_id,
    }


def _blocked_error(receipt: dict[str, object], message: str) -> ProjectConformanceError:
    return ProjectConformanceError(
        code="ERR_VALIDATION",
        message=message,
        fix_suggestion="Repair the project metadata or run ask sdk project doctor with an explicit project root.",
        receipt=receipt,
    )


def _agent_summary(receipt: dict[str, object]) -> str:
    status = str(receipt["status"])
    count = int(receipt["installed_skill_count"])
    if status == "pass":
        return f"Project conformance passed for {count} installed skill(s); no writes were performed."
    return (
        f"Project conformance is {status} for {count} installed skill(s); "
        f"{len(_list_value(receipt.get('issues')))} issue(s) require operator action."
    )


def _string_value(value: object) -> str | None:
    return value if isinstance(value, str) and value else None


def _list_value(value: object) -> list[object]:
    return value if isinstance(value, list) else []
