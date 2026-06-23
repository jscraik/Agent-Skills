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
PROJECT_CONFORMANCE_SCHEMA_URI = "https://agent-skills.local/schemas/skills-sdk/project-conformance-receipt.v1.schema.json"
PROJECT_CONFORMANCE_ACCEPTANCE_TRACE = [
    "PU-012-FR-001",
    "PU-012-FR-002",
    "PU-012-FR-003",
    "PU-012-SA-001",
    "PU-012-SA-002",
    "PU-012-VP-001",
]

ConformanceMode = Literal["status", "doctor"]
ConformanceStatus = Literal["pass", "warn", "fail", "blocked"]


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
    """
    Constructs a project conformance receipt describing installed skills, detected issues, and operator actions for a project.

    Parameters:
        repo_root (Path): Filesystem path of the agent repository root used to validate safe project selection.
        project_root (str | None): Optional project-root hint or path to resolve inside the repository; may be None to allow resolution logic to select a default.
        mode (ConformanceMode): Conformance mode, either "status" or "doctor", which controls command metadata and validation behavior.

    Returns:
        receipt (dict[str, object]): A conformance receipt dictionary containing schema identity, project metadata, installed_skills (per-skill rows), issues, manual_actions, counters (installed_skill_count, rollback_ready_count, uninstall_ready_count), lockfile_status, status ("pass", "warning", or "blocked"), and agent_summary.

    Raises:
        ValueError: If `mode` is not "status" or "doctor".
        ProjectConformanceError: If conformance validation encounters a blocking error; the exception embeds the partially built receipt for diagnostics.
    """
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
    # Check if lockfile is a broken symlink before treating it as missing
    if lockfile_path.is_symlink() and not lockfile_path.is_file():
        issue = _issue(
            "lockfile_broken_symlink",
            "blocker",
            "skills.lock.json is a broken symlink.",
            DEFAULT_LOCKFILE_PATH,
        )
        receipt["issues"] = [issue]
        receipt["manual_actions"] = [
            _manual_action(
                "repair_lockfile",
                "Remove the broken symlink and regenerate skills.lock.json.",
                DEFAULT_LOCKFILE_PATH,
            )
        ]
        receipt["lockfile_status"] = "invalid"
        receipt["status"] = "blocked"
        receipt["agent_summary"] = (
            "Project conformance is blocked because skills.lock.json is a broken symlink."
        )
        raise _blocked_error(receipt, "skills.lock.json is a broken symlink.")

    if not lockfile_path.exists():
        # Check for installed SDK evidence
        receipt_dir = resolved_project_root / ".harness/receipts/skills-sdk/install"
        skills_dir = resolved_project_root / ".agents/skills"

        # Validate that evidence paths are readable directories
        receipt_dir_valid = receipt_dir.is_dir()
        skills_dir_valid = skills_dir.is_dir()
        has_installed_evidence = False
        has_corrupted_evidence = False

        if receipt_dir_valid:
            try:
                has_installed_evidence = any(receipt_dir.iterdir())
            except (OSError, PermissionError):
                has_corrupted_evidence = True
        elif receipt_dir.exists():
            # Path exists but is not a directory (file, broken symlink, etc.)
            has_corrupted_evidence = True

        if skills_dir_valid:
            try:
                has_installed_evidence = has_installed_evidence or any(
                    skills_dir.iterdir()
                )
            except (OSError, PermissionError):
                has_corrupted_evidence = True
        elif skills_dir.exists():
            # Path exists but is not a directory (file, broken symlink, etc.)
            has_corrupted_evidence = True

        if has_corrupted_evidence:
            receipt["lockfile_status"] = "corrupted_evidence"
            receipt["status"] = "blocked"
            issue = _issue(
                "corrupted_sdk_evidence",
                "blocker",
                "Installed SDK evidence directories are corrupted or unreadable.",
                DEFAULT_LOCKFILE_PATH,
            )
            receipt["issues"] = [issue]
            receipt["manual_actions"] = [
                _manual_action(
                    "repair_evidence",
                    "Remove or repair corrupted evidence directories (.harness/receipts/skills-sdk/install or .agents/skills).",
                    DEFAULT_LOCKFILE_PATH,
                )
            ]
            receipt["agent_summary"] = (
                "Project conformance is blocked because installed SDK evidence is corrupted."
            )
            raise _blocked_error(
                receipt, "Installed SDK evidence is corrupted or unreadable."
            )

        if has_installed_evidence:
            receipt["lockfile_status"] = "missing_with_installed_evidence"
            receipt["status"] = "blocked"
            issue = _issue(
                "missing_lockfile",
                "blocker",
                "skills.lock.json is missing but installed SDK evidence exists.",
                DEFAULT_LOCKFILE_PATH,
            )
            receipt["issues"] = [issue]
            receipt["manual_actions"] = [
                _manual_action(
                    "regenerate_lockfile",
                    "Regenerate skills.lock.json from install receipts or reinstall skills.",
                    DEFAULT_LOCKFILE_PATH,
                )
            ]
            receipt["agent_summary"] = (
                "Project conformance failed because skills.lock.json is missing but installed evidence exists."
            )
            raise _blocked_error(
                receipt, "skills.lock.json is missing but installed evidence exists."
            )

        receipt["lockfile_status"] = "empty_not_installed"
        receipt["agent_summary"] = (
            "Project is marked for Skills SDK adoption and has no installed skills yet."
        )
        return receipt
    if not lockfile_path.is_file():
        issue = _issue(
            "lockfile_not_file",
            "blocker",
            "skills.lock.json is not a regular file.",
            DEFAULT_LOCKFILE_PATH,
        )
        receipt["issues"] = [issue]
        receipt["manual_actions"] = [
            _manual_action(
                "repair_lockfile",
                "Replace skills.lock.json with a regular lockfile.",
                DEFAULT_LOCKFILE_PATH,
            )
        ]
        receipt["lockfile_status"] = "invalid"
        receipt["status"] = "blocked"
        receipt["agent_summary"] = (
            "Project conformance is blocked because skills.lock.json is not a regular file."
        )
        raise _blocked_error(receipt, "skills.lock.json is not a regular file.")

    lockfile = _load_lockfile(lockfile_path, receipt)
    entries = lockfile.get("entries")
    if not isinstance(entries, dict):
        issue = _issue(
            "invalid_lockfile_entries",
            "blocker",
            "skills.lock.json entries must be an object.",
            DEFAULT_LOCKFILE_PATH,
        )
        receipt["issues"] = [issue]
        receipt["manual_actions"] = [
            _manual_action(
                "repair_lockfile",
                "Regenerate skills.lock.json from valid install receipts.",
                DEFAULT_LOCKFILE_PATH,
            )
        ]
        receipt["lockfile_status"] = "invalid"
        receipt["status"] = "blocked"
        receipt["agent_summary"] = (
            "Project conformance is blocked because skills.lock.json has invalid entries."
        )
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
    receipt["rollback_ready_count"] = sum(
        1 for row in rows if row.get("rollback_ready") is True
    )
    receipt["uninstall_ready_count"] = sum(
        1 for row in rows if row.get("uninstall_ready") is True
    )
    receipt["lockfile_status"] = "valid" if not issues else "valid_with_diagnostics"
    status: ConformanceStatus = "pass"
    if any(issue.get("severity") == "blocker" for issue in issues):
        status = "blocked"
    elif any(issue.get("severity") == "warning" for issue in issues):
        status = "warn"
    elif issues:
        status = "fail"
    receipt["status"] = status
    receipt["agent_summary"] = _agent_summary(receipt)
    if status == "blocked":
        raise _blocked_error(receipt, str(receipt["agent_summary"]))
    return receipt


def _resolve_conformance_root(
    repo_root: Path, project_root: str | None, mode: ConformanceMode
) -> Path:
    """
    Resolve and validate the project root for conformance checks, returning a safe absolute Path.

    Parameters:
        repo_root (Path): Path to the live agent-skills repository used to enforce safety (ancestor checks).
        project_root (str | None): User-provided project root hint; may be None.
        mode (ConformanceMode): Operation mode used to populate the generated receipt metadata (e.g., "status" or "doctor").

    Returns:
        Path: The resolved absolute project root that is safe to use.

    Raises:
        ProjectConformanceError: Raised with an embedded conformance receipt when the project root cannot be resolved
            (e.g., resolution errors) or when the chosen root would be an ancestor of the live agent repository.
    """
    try:
        root = _resolve_project_root(project_root, repo_root)
    except ProjectInstallError as exc:
        receipt = _base_receipt(
            command=f"skills-sdk project {mode}",
            mode=mode,
            project_root=str(
                exc.receipt.get("target_root") or project_root or "missing"
            ),
            project_managed=False,
            lockfile_path=None,
            lockfile_status="not_checked",
            status="blocked",
        )
        conflicts = [
            str(item) for item in _list_value(exc.receipt.get("conflicts"))
        ] or [exc.code.lower()]
        receipt["issues"] = [
            _issue(
                conflict,
                "blocker",
                exc.message,
                str(exc.receipt.get("target_root") or project_root or "missing"),
            )
            for conflict in conflicts
        ]
        receipt["manual_actions"] = [
            _manual_action(
                "choose_project_root",
                exc.fix_suggestion,
                str(exc.receipt.get("target_root") or project_root or "missing"),
            )
        ]
        receipt["agent_summary"] = exc.message
        raise ProjectConformanceError(
            exc.code, exc.message, exc.fix_suggestion, receipt
        ) from exc
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
        receipt["issues"] = [
            _issue("live_repo_ancestor_root", "blocker", message, str(root))
        ]
        receipt["manual_actions"] = [
            _manual_action(
                "choose_project_root",
                "Use a separate marked project checkout.",
                str(root),
            )
        ]
        receipt["agent_summary"] = message
        raise ProjectConformanceError(
            "ERR_VALIDATION",
            message,
            "Use a separate marked project checkout.",
            receipt,
        )
    return root


def _load_lockfile(path: Path, receipt: dict[str, object]) -> dict[str, object]:
    """
    Load and validate the skills.lock.json located at `path`, updating `receipt` with diagnostics when fatal problems are found.

    Parameters:
        path (Path): Filesystem path to the lockfile to read.
        receipt (dict[str, object]): In-progress conformance receipt that will be mutated with issues, manual_actions, lockfile_status, status, and agent_summary when validation fails.

    Returns:
        payload (dict[str, object]): The parsed lockfile payload (root object) when validation succeeds.

    Raises:
        ProjectConformanceError: If the file is malformed JSON, its root is not an object, or its schema identity (version/URI) is unsupported; the raised error embeds the updated `receipt`.
    """
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError, OSError) as exc:
        issue = _issue(
            "malformed_lockfile",
            "blocker",
            f"skills.lock.json is malformed JSON: {exc}",
            DEFAULT_LOCKFILE_PATH,
        )
        receipt["issues"] = [issue]
        receipt["manual_actions"] = [
            _manual_action(
                "repair_lockfile",
                "Replace skills.lock.json with valid JSON.",
                DEFAULT_LOCKFILE_PATH,
            )
        ]
        receipt["lockfile_status"] = "invalid"
        receipt["status"] = "blocked"
        receipt["agent_summary"] = (
            "Project conformance is blocked because skills.lock.json is malformed."
        )
        raise _blocked_error(receipt, "skills.lock.json is malformed.") from exc
    if not isinstance(payload, dict):
        issue = _issue(
            "invalid_lockfile_root",
            "blocker",
            "skills.lock.json root must be an object.",
            DEFAULT_LOCKFILE_PATH,
        )
        receipt["issues"] = [issue]
        receipt["manual_actions"] = [
            _manual_action(
                "repair_lockfile",
                "Regenerate skills.lock.json as an object.",
                DEFAULT_LOCKFILE_PATH,
            )
        ]
        receipt["lockfile_status"] = "invalid"
        receipt["status"] = "blocked"
        receipt["agent_summary"] = (
            "Project conformance is blocked because skills.lock.json root is invalid."
        )
        raise _blocked_error(receipt, "skills.lock.json root is invalid.")
    conflicts: list[str] = []
    if payload.get("schema_version") != LOCKFILE_SCHEMA_VERSION:
        conflicts.append("unsupported_lockfile_schema_version")
    if payload.get("schema_uri") != LOCKFILE_SCHEMA_URI:
        conflicts.append("unsupported_lockfile_schema_uri")
    if conflicts:
        receipt["issues"] = [
            _issue(
                conflict,
                "blocker",
                "skills.lock.json schema identity is unsupported.",
                DEFAULT_LOCKFILE_PATH,
            )
            for conflict in conflicts
        ]
        receipt["manual_actions"] = [
            _manual_action(
                "repair_lockfile",
                "Regenerate skills.lock.json with the current SDK.",
                DEFAULT_LOCKFILE_PATH,
            )
        ]
        receipt["lockfile_status"] = "unsupported"
        receipt["status"] = "blocked"
        receipt["agent_summary"] = (
            "Project conformance is blocked because skills.lock.json has an unsupported schema identity."
        )
        raise _blocked_error(
            receipt, "skills.lock.json has an unsupported schema identity."
        )
    return cast(dict[str, object], payload)


def _inspect_lockfile_entry(
    project_root: Path,
    *,
    skill_id: str,
    entry_value: object,
) -> tuple[dict[str, object], list[dict[str, object]], list[dict[str, object]]]:
    """
    Inspect a single skills.lock.json entry and produce a per-skill row, detected issues, and required manual actions.

    Parameters:
        project_root (Path): Absolute project root used to resolve receipt and file paths.
        skill_id (str): The skill identifier for the lockfile entry being inspected.
        entry_value (object): The raw lockfile entry value; expected to be a mapping with keys like `target_path`, `receipt_ref`, and optional file metadata.

    Returns:
        tuple:
            row (dict[str, object]): Per-skill record summarizing target path, receipt reference/status, overall status, rollback/uninstall readiness, and list of issue codes.
            issues (list[dict[str, object]]): Collected issue objects describing validation or integrity problems discovered for this entry.
            actions (list[dict[str, object]]): Manual-action objects advising operator remediation steps for the discovered issues.
    """
    issues: list[dict[str, object]] = []
    actions: list[dict[str, object]] = []
    if not isinstance(entry_value, dict):
        row = _skill_row(
            skill_id,
            "unresolved",
            "missing",
            "invalid",
            "blocked",
            False,
            False,
            ["invalid_lockfile_entry"],
        )
        issues.append(
            _issue(
                "invalid_lockfile_entry",
                "blocker",
                "Lockfile entry must be an object.",
                DEFAULT_LOCKFILE_PATH,
                skill_id,
            )
        )
        actions.append(
            _manual_action(
                "repair_lockfile_entry",
                "Regenerate this lockfile entry from a valid receipt.",
                DEFAULT_LOCKFILE_PATH,
                skill_id,
            )
        )
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
        issues.append(
            _issue(
                "missing_receipt_ref",
                "blocker",
                "Lockfile entry has no receipt_ref.",
                DEFAULT_LOCKFILE_PATH,
                skill_id,
            )
        )
    else:
        receipt_path = _resolve_inside_project(project_root, receipt_ref)
        if receipt_path is None:
            row_issue_codes.append("unsafe_receipt_ref")
            receipt_issue_codes.append("unsafe_receipt_ref")
            issues.append(
                _issue(
                    "unsafe_receipt_ref",
                    "blocker",
                    "receipt_ref escapes the project root.",
                    receipt_ref,
                    skill_id,
                )
            )
        elif not receipt_path.is_file():
            row_issue_codes.append("missing_receipt")
            receipt_issue_codes.append("missing_receipt")
            issues.append(
                _issue(
                    "missing_receipt",
                    "blocker",
                    "Install receipt referenced by skills.lock.json is missing.",
                    receipt_ref,
                    skill_id,
                )
            )
        else:
            receipt_payload, receipt_digest, receipt_conflicts = (
                _load_install_receipt_for_status(receipt_path, project_root)
            )
            row_issue_codes.extend(receipt_conflicts)
            receipt_issue_codes.extend(receipt_conflicts)
            for conflict in receipt_conflicts:
                issues.append(
                    _issue(
                        conflict,
                        "blocker",
                        "Install receipt is not valid project cleanup authority.",
                        receipt_ref,
                        skill_id,
                    )
                )

    file_conflicts = _inspect_installed_files(
        project_root, entry, receipt_payload, skill_id
    )
    row_issue_codes.extend(file_conflicts)
    for conflict in file_conflicts:
        path = conflict.split(":", 1)[1] if ":" in conflict else target_path
        issues.append(
            _issue(
                conflict.split(":", 1)[0],
                "blocker",
                "Installed file metadata does not match the project state.",
                path,
                skill_id,
            )
        )

    for issue in row_issue_codes:
        actions.append(
            _manual_action(
                "manual_review",
                f"Resolve {issue} before rollback or uninstall.",
                target_path,
                skill_id,
            )
        )

    blocked = bool(row_issue_codes)
    return (
        _skill_row(
            skill_id,
            target_path,
            receipt_ref,
            "valid"
            if receipt_payload is not None and not receipt_issue_codes
            else ("missing" if receipt_digest == "sha256:missing" else "invalid"),
            "healthy" if not blocked else "blocked",
            not blocked,
            not blocked,
            row_issue_codes,
        ),
        issues,
        actions,
    )


def _load_install_receipt_for_status(
    path: Path, project_root: Path
) -> tuple[dict[str, object] | None, str, list[str]]:
    """
    Validate and load an install receipt JSON file and compute its content digest.

    Parameters:
        path (Path): Path to the install receipt file to read and validate.
        project_root (Path): Expected project root; the receipt's `target_root` must resolve to this path.

    Returns:
        tuple:
            receipt (dict[str, object] | None): Parsed receipt dict when the payload is valid and no validation conflicts were found; `None` otherwise.
            digest (str): SHA-256 digest label for the parsed JSON (e.g. `"sha256:<hex>"`) or the sentinel `"sha256:malformed"` when JSON parsing failed.
            conflicts (list[str]): List of validation conflict codes (empty when `receipt` is returned). When JSON is malformed the list is `["malformed_receipt"]`; other codes indicate schema/operation/scope/mutation/target/files_written mismatches.
    """
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError, OSError):
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
    if not target_root:
        conflicts.append("receipt_project_root_mismatch")
    elif not Path(target_root).is_absolute():
        conflicts.append("receipt_relative_target_root")
    elif Path(target_root).resolve() != project_root:
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
    """
    Validate installed-file metadata for a single lockfile entry and return a list of conflict codes describing problems found.

    Parameters:
        project_root (Path): Absolute project root used to resolve file targets.
        entry (dict): The lockfile entry for the skill (may contain a "files" list and "name").
        receipt (dict | None): The install receipt associated with the entry (may contain "files_written"); may be None.
        skill_id (str): The skill identifier expected for the entry.

    Returns:
        list[str]: A list of conflict codes found while inspecting installed files. Possible codes:
            - "missing_file_metadata": no file metadata available in entry or receipt
            - "invalid_file_metadata": file metadata item is missing/invalid fields or not a mapping
            - "file_path_escape:<path>": target path resolves outside the project root
            - "installed_file_missing:<path>": expected target file does not exist
            - "installed_file_modified:<path>": file exists but its digest does not match expected
            - "skill_id_name_mismatch": entry name does not match the provided skill_id
    """
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
    """
    Resolve a candidate path inside the given project root, ensuring the resolved path is contained within the project.

    Parameters:
        project_root (Path): The project root directory used as the base for resolution.
        relative_path (str): A path relative to the project root to resolve.

    Returns:
        Path: The absolute resolved path when it is safely contained by project_root.
        None: If resolution escapes the project root or is otherwise unsafe.
    """
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
    """
    Construct the initial project conformance receipt dictionary with default counters, lists, and identity metadata.

    Parameters:
        command (str): The command that produced this receipt (e.g., "skills-sdk project status").
        mode (ConformanceMode): Operation mode, either "status" or "doctor".
        project_root (str): The chosen project root path (or sentinel like "missing"/"unresolved").
        project_managed (bool): Whether the project is managed by the SDK (affects diagnostics and actions).
        lockfile_path (str | None): Path to the project's lockfile, or `None` when not applicable.
        lockfile_status (str): One-word status describing lockfile state (e.g., "missing", "valid", "invalid").
        status (ConformanceStatus): Overall conformance status seed ("pass", "warning", or "blocked").

    Returns:
        dict[str, object]: A receipt dictionary populated with schema identity, supplied metadata,
        zeroed counters (`installed_skill_count`, `rollback_ready_count`, `uninstall_ready_count`),
        empty lists for `installed_skills`, `issues`, and `manual_actions`, and a default
        `agent_summary` indicating evaluation has not yet been performed.
    """
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
    """
    Builds an identity dictionary describing the provided project root.

    If `project_root` is one of the sentinel values "missing", "unresolved", or an empty string,
    the returned identity will use `"identity_kind": "unresolved"` and include the original
    `realpath` value. Otherwise the function checks the filesystem: when the path exists the
    returned `realpath` is the resolved absolute path and `exists` is True; when it does not
    exist `realpath` is the original input string and `exists` is False.

    Parameters:
        project_root (str): Path string identifying the project root, or one of the sentinel
            values "missing", "unresolved", or "".

    Returns:
        dict[str, object]: A mapping with keys:
            - `identity_kind` ("unresolved" or "realpath")
            - `realpath` (resolved absolute path when it exists, otherwise the original input)
            - `exists` (bool) present when `identity_kind` is "realpath" indicating filesystem existence
    """
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
    """
    Constructs a per-skill record describing an installed skill's metadata, status, and required actions.

    Parameters:
        skill_id (str): Identifier of the skill.
        target_path (str): Declared installation path for the skill inside the project.
        receipt_ref (str): Relative reference to the install receipt as recorded in the lockfile (or marker like "missing"/"unresolved").
        receipt_status (str): Normalized receipt state such as "valid", "missing", or "invalid".
        status (str): Per-skill overall status such as "healthy" or "blocked".
        rollback_ready (bool): True when the skill can be safely rolled back without manual intervention.
        uninstall_ready (bool): True when the skill can be safely uninstalled without manual intervention.
        issue_codes (list[str]): List of machine-readable issue codes that apply to this skill row.

    Returns:
        dict: A mapping with keys:
            - "skill_id": skill identifier (str)
            - "target_path": installation path (str)
            - "receipt_ref": receipt reference (str)
            - "receipt_status": receipt state (str)
            - "status": per-skill status (str)
            - "rollback_ready": rollback readiness (bool)
            - "uninstall_ready": uninstall readiness (bool)
            - "issue_codes": list of issue codes (list[str])
    """
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
    """
    Create a standardized issue object describing a project conformance problem.

    Parameters:
        code (str): Short machine-readable issue code.
        severity (Literal["info","warning","blocker"]): Issue severity level.
        message (str): Human-readable explanation of the issue.
        path (str): Project-relative path or identifier associated with the issue.
        skill_id (str | None): Optional skill identifier related to the issue.

    Returns:
        issue (dict): Dictionary with keys `code`, `severity`, `message`, `path`, and `skill_id` (may be None).
    """
    return {
        "code": code,
        "severity": severity,
        "message": message,
        "path": path,
        "skill_id": skill_id,
    }


def _manual_action(
    action: str, reason: str, path: str, skill_id: str | None = None
) -> dict[str, object]:
    """
    Construct a manual action record describing an operator task for a skill.

    Parameters:
        action (str): Identifier of the manual action to perform.
        reason (str): Human-readable explanation of why the action is required.
        path (str): Path related to the action (typically a file or receipt path).
        skill_id (str | None): Optional skill identifier associated with the action.

    Returns:
        dict[str, object]: Manual action object containing keys "action", "reason", "path", and "skill_id".
    """
    return {
        "action": action,
        "reason": reason,
        "path": path,
        "skill_id": skill_id,
    }


def _blocked_error(receipt: dict[str, object], message: str) -> ProjectConformanceError:
    """
    Create a ProjectConformanceError representing a blocking validation failure for the given receipt.

    Parameters:
        receipt (dict[str, object]): The conformance receipt to embed in the error.
        message (str): Human-facing error message explaining the validation failure.

    Returns:
        ProjectConformanceError: Error with code "ERR_VALIDATION", the provided message, a standard fix suggestion, and the embedded receipt.
    """
    return ProjectConformanceError(
        code="ERR_VALIDATION",
        message=message,
        fix_suggestion="Repair the project metadata or run ask sdk project doctor with an explicit project root.",
        receipt=receipt,
    )


def _agent_summary(receipt: dict[str, object]) -> str:
    """
    Builds a human-readable summary string from a project conformance receipt.

    Parameters:
        receipt (dict[str, object]): Conformance receipt containing at least the keys
            "status" (one of "pass", "warning", "blocked") and "installed_skill_count";
            may include "issues" (a list) to report outstanding problems.

    Returns:
        str: A summary stating the receipt status and installed skill count; if the
        status is not "pass", includes the number of issues that require operator action.
    """
    status = str(receipt["status"])
    count = int(receipt["installed_skill_count"])
    if status == "pass":
        return f"Project conformance passed for {count} installed skill(s); no writes were performed."
    return (
        f"Project conformance is {status} for {count} installed skill(s); "
        f"{len(_list_value(receipt.get('issues')))} issue(s) require operator action."
    )


def _string_value(value: object) -> str | None:
    """
    Coerce a value to a non-empty string or return None.

    Parameters:
        value (object): Value to check.

    Returns:
        The original string when `value` is a non-empty `str`, otherwise `None`.
    """
    return value if isinstance(value, str) and value else None


def _list_value(value: object) -> list[object]:
    """
    Coerce a value to a list: return the value if it's already a list, otherwise return an empty list.

    Parameters:
        value (object): The value to inspect.

    Returns:
        list_value (list[object]): `value` when it is a list, otherwise an empty list.
    """
    return value if isinstance(value, list) else []
