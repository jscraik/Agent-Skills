from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


SKILL_INTAKE_SCHEMA_VERSION = "skills-sdk.skill-intake-receipt.v0"
SKILL_INTAKE_SCHEMA_URI = (
    "https://jscraik.local/agent-skills/schemas/skills-sdk/skill-intake-receipt.v0.schema.json"
)
SKILL_INTAKE_ACCEPTANCE_TRACE = ["PU-032", "FR-008", "FR-010", "SA-004", "SEC-001", "VP-032"]
ALLOWED_TOP_LEVELS = frozenset({"SKILL.md", "agents", "references", "scripts", "assets", "evals"})
REQUIRED_SKILL_FILE = "SKILL.md"


def _digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


def _digest_json(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"


def _check(
    check_id: str,
    status: str,
    message: str,
    evidence: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "id": check_id,
        "status": status,
        "severity": status,
        "message": message,
        "evidence": evidence or [],
    }


def _repo_label(repo_root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except (FileNotFoundError, RuntimeError, ValueError):
        return path.as_posix()


def _source_label(repo_root: Path, source_path: Path) -> str:
    expanded = source_path.expanduser()
    if not expanded.is_absolute():
        return expanded.as_posix()
    return _repo_label(repo_root, expanded)


def _source_root_is_broad(path: Path) -> bool:
    try:
        resolved = path.resolve(strict=True)
    except (FileNotFoundError, RuntimeError, OSError):
        return False
    home = Path.home().resolve()
    filesystem_root = Path(resolved.anchor).resolve()
    return resolved in {home, filesystem_root}


def _blocked_receipt(
    repo_root: Path,
    *,
    source_path: Path,
    source_kind: str,
    checks: list[dict[str, Any]],
    inspected_files: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    blockers = [check for check in checks if check["status"] == "blocker"]
    return {
        "schema_version": SKILL_INTAKE_SCHEMA_VERSION,
        "schema_uri": SKILL_INTAKE_SCHEMA_URI,
        "status": "blocked",
        "operation": "skill_intake_inspect",
        "source_kind": source_kind,
        "source_path": _source_label(repo_root, source_path),
        "source_digest": None,
        "skill_id": None,
        "file_count": len(inspected_files or []),
        "total_size_bytes": sum(int(item.get("size_bytes", 0)) for item in inspected_files or []),
        "inspected_files": inspected_files or [],
        "intake_checks": checks,
        "blockers": blockers,
        "execution_performed": False,
        "install_performed": False,
        "projection_mutation_performed": False,
        "network_accessed": False,
        "mutation_performed": False,
        "acceptance_trace": SKILL_INTAKE_ACCEPTANCE_TRACE,
        "agent_summary": f"External skill intake blocked {source_kind} source with {len(blockers)} blocker(s).",
    }


def _skill_id_from_skill_md(skill_file: Path) -> str | None:
    try:
        text = skill_file.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    in_frontmatter = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "---":
            if not in_frontmatter:
                in_frontmatter = True
                continue
            break
        if in_frontmatter and stripped.startswith("name:"):
            value = stripped.split(":", 1)[1].strip().strip('"').strip("'")
            return value or None
    return None


def _skill_md_check(source_root: Path) -> dict[str, Any]:
    skill_file = source_root / REQUIRED_SKILL_FILE
    if skill_file.is_file() and not skill_file.is_symlink():
        return _check("skill_md_present", "pass", "Source includes a regular SKILL.md file.", [REQUIRED_SKILL_FILE])
    return _check("skill_md_present", "blocker", "External skill intake requires a regular SKILL.md file.", [REQUIRED_SKILL_FILE])


def _top_level_findings(source_root: Path, children: list[Path]) -> tuple[list[str], list[str]]:
    unexpected: list[str] = []
    symlinks: list[str] = []
    for child in children:
        relative = child.relative_to(source_root).as_posix()
        if child.name not in ALLOWED_TOP_LEVELS:
            unexpected.append(relative)
        if child.is_symlink():
            symlinks.append(relative)
    return unexpected, symlinks


def _top_level_check(unexpected: list[str]) -> dict[str, Any]:
    if unexpected:
        return _check("approved_top_level_paths", "blocker", "Source contains top-level paths outside the skill package contract.", unexpected)
    return _check("approved_top_level_paths", "pass", "Source top-level paths match the skill package contract.", sorted(ALLOWED_TOP_LEVELS))


def _relative_package_path(source_root: Path, path: Path) -> Path | None:
    try:
        return path.relative_to(source_root)
    except ValueError:
        return None


def _inspect_allowed_path(
    path: Path,
    relative_path: Path,
    inspected_files: list[dict[str, Any]],
    symlinks: list[str],
    special_files: list[str],
    unreadable_files: list[str],
) -> None:
    relative = relative_path.as_posix()
    if path.is_symlink():
        symlinks.append(relative)
        return
    if path.is_dir():
        return
    if not path.is_file():
        special_files.append(relative)
        return
    try:
        size_bytes = path.stat().st_size
        digest = _digest_file(path)
    except OSError:
        unreadable_files.append(relative)
        return
    inspected_files.append({"path": relative, "digest": digest, "size_bytes": size_bytes})


def _iter_approved_package_paths(source_root: Path, top_level_children: list[Path]) -> list[Path]:
    approved_paths: list[Path] = []
    for child in top_level_children:
        if child.name not in ALLOWED_TOP_LEVELS:
            continue
        approved_paths.append(child)
        if child.is_dir() and not child.is_symlink():
            approved_paths.extend(sorted(child.rglob("*")))
    return approved_paths


def _symlink_check(symlinks: list[str]) -> dict[str, Any]:
    if symlinks:
        return _check("no_symlinks", "blocker", "External skill intake refuses symlinks before canonical install.", sorted(set(symlinks)))
    return _check("no_symlinks", "pass", "Source contains no symlinks.", [])


def _regular_files_check(special_files: list[str]) -> dict[str, Any]:
    if special_files:
        return _check("regular_files_only", "blocker", "External skill intake refuses special files.", sorted(set(special_files)))
    return _check("regular_files_only", "pass", "Source contains only regular files and directories.", [])


def _readable_files_check(unreadable_files: list[str]) -> dict[str, Any]:
    if unreadable_files:
        return _check("source_files_readable", "blocker", "External skill intake requires approved files to be readable.", sorted(set(unreadable_files)))
    return _check("source_files_readable", "pass", "Approved source files were readable.", [])


def _non_mutating_intake_checks() -> list[dict[str, Any]]:
    return [
        _check("execution_blocked", "pass", "Intake inspects files only and does not execute skill code.", []),
        _check("install_blocked", "pass", "Intake does not write canonical source, runtime projections, or install roots.", []),
    ]


def _inspect_directory(repo_root: Path, source_root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    skill_md_check = _skill_md_check(source_root)
    checks = [skill_md_check]
    inspected_files: list[dict[str, Any]] = []
    try:
        top_level_children = sorted(source_root.iterdir(), key=lambda path: path.name)
    except OSError as exc:
        checks.append(_check("source_readable", "blocker", f"Source directory could not be read: {exc}", [_repo_label(repo_root, source_root)]))
        return checks, inspected_files

    unexpected, symlinks = _top_level_findings(source_root, top_level_children)
    special_files: list[str] = []
    unreadable_files: list[str] = []
    checks.append(_top_level_check(unexpected))
    if skill_md_check["status"] == "blocker":
        checks.append(_symlink_check(symlinks))
        checks.append(_check("regular_files_only", "pass", "Recursive inspection skipped until SKILL.md is a regular file.", []))
        checks.append(_check("source_files_readable", "pass", "Recursive inspection skipped until SKILL.md is a regular file.", []))
    else:
        for path in _iter_approved_package_paths(source_root, top_level_children):
            relative_path = _relative_package_path(source_root, path)
            if relative_path is None:
                checks.append(_check("path_containment", "blocker", "Resolved path escaped the intake root.", [_repo_label(repo_root, path)]))
                continue
            _inspect_allowed_path(path, relative_path, inspected_files, symlinks, special_files, unreadable_files)

        checks.append(_symlink_check(symlinks))
        checks.append(_regular_files_check(special_files))
        checks.append(_readable_files_check(unreadable_files))
    checks.extend(_non_mutating_intake_checks())
    return checks, inspected_files


def _unsupported_source_kind_receipt(repo_root: Path, source_path: Path, source_kind: str) -> dict[str, Any]:
    return _blocked_receipt(
        repo_root,
        source_path=source_path,
        source_kind=source_kind,
        checks=[
            _check(
                "source_kind_supported",
                "blocker",
                "This slice only supports directory intake; archive unpacking is intentionally deferred.",
                [source_kind],
            )
        ],
    )


def _resolve_directory_source(repo_root: Path, source_path: Path, source_kind: str) -> Path | dict[str, Any]:
    if not source_path.is_absolute():
        source_path = repo_root / source_path
    if source_path.is_symlink():
        return _blocked_receipt(
            repo_root,
            source_path=source_path,
            source_kind=source_kind,
            checks=[_check("source_root_not_symlink", "blocker", "External skill intake refuses symlink source roots.", [_source_label(repo_root, source_path)])],
        )
    try:
        resolved_source = source_path.resolve(strict=True)
    except FileNotFoundError:
        return _blocked_receipt(
            repo_root,
            source_path=source_path,
            source_kind=source_kind,
            checks=[_check("source_exists", "blocker", "External skill intake source does not exist.", [_source_label(repo_root, source_path)])],
        )
    except (OSError, RuntimeError) as exc:
        return _blocked_receipt(
            repo_root,
            source_path=source_path,
            source_kind=source_kind,
            checks=[_check("source_resolvable", "blocker", f"External skill intake source could not be resolved: {exc}", [_source_label(repo_root, source_path)])],
        )
    return _validated_directory_source(repo_root, resolved_source, source_kind)


def _validated_directory_source(repo_root: Path, resolved_source: Path, source_kind: str) -> Path | dict[str, Any]:
    if _source_root_is_broad(resolved_source):
        return _blocked_receipt(
            repo_root,
            source_path=resolved_source,
            source_kind=source_kind,
            checks=[_check("source_root_not_broad", "blocker", "External skill intake refuses broad filesystem roots.", [_source_label(repo_root, resolved_source)])],
        )
    if not resolved_source.is_dir():
        return _blocked_receipt(
            repo_root,
            source_path=resolved_source,
            source_kind=source_kind,
            checks=[_check("source_is_directory", "blocker", "This slice only supports skill directory intake.", [_repo_label(repo_root, resolved_source)])],
        )
    return resolved_source


def _preview_receipt(repo_root: Path, source_root: Path, source_kind: str, checks: list[dict[str, Any]], inspected_files: list[dict[str, Any]]) -> dict[str, Any]:
    skill_file = source_root / REQUIRED_SKILL_FILE
    skill_id = _skill_id_from_skill_md(skill_file) or source_root.name
    source_digest = _digest_json(
        [{"path": item["path"], "digest": item["digest"], "size_bytes": item["size_bytes"]} for item in inspected_files]
    )
    return {
        "schema_version": SKILL_INTAKE_SCHEMA_VERSION,
        "schema_uri": SKILL_INTAKE_SCHEMA_URI,
        "status": "preview",
        "operation": "skill_intake_inspect",
        "source_kind": source_kind,
        "source_path": _repo_label(repo_root, source_root),
        "source_digest": source_digest,
        "skill_id": skill_id,
        "file_count": len(inspected_files),
        "total_size_bytes": sum(int(item["size_bytes"]) for item in inspected_files),
        "inspected_files": inspected_files,
        "intake_checks": checks,
        "blockers": [],
        "execution_performed": False,
        "install_performed": False,
        "projection_mutation_performed": False,
        "network_accessed": False,
        "mutation_performed": False,
        "acceptance_trace": SKILL_INTAKE_ACCEPTANCE_TRACE,
        "agent_summary": f"External skill intake inspected {len(inspected_files)} file(s) for {skill_id} without execution or install.",
    }


def build_skill_intake_receipt(
    repo_root: Path,
    *,
    source: str,
    source_kind: str = "directory",
) -> dict[str, Any]:
    source_path = Path(source).expanduser()
    if source_kind != "directory":
        return _unsupported_source_kind_receipt(repo_root, source_path, source_kind)

    resolved_source = _resolve_directory_source(repo_root, source_path, source_kind)
    if isinstance(resolved_source, dict):
        return resolved_source

    checks, inspected_files = _inspect_directory(repo_root, resolved_source)
    blockers = [check for check in checks if check["status"] == "blocker"]
    if blockers:
        return _blocked_receipt(
            repo_root,
            source_path=resolved_source,
            source_kind=source_kind,
            checks=checks,
            inspected_files=inspected_files,
        )

    return _preview_receipt(repo_root, resolved_source, source_kind, checks, inspected_files)
