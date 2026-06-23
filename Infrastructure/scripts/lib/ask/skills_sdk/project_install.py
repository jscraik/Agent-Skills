from __future__ import annotations

import hashlib
import json
import os
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


INSTALL_RECEIPT_SCHEMA_VERSION = "skills-sdk.install-receipt.v1"
INSTALL_RECEIPT_SCHEMA_URI = (
    "https://agent-skills.local/schemas/skills-sdk/install-receipt.v1.schema.json"
)
LOCKFILE_SCHEMA_VERSION = "skills-sdk.lockfile.v1"
LOCKFILE_SCHEMA_URI = "https://agent-skills.local/schemas/skills-sdk/lockfile.v1.schema.json"
DEFAULT_LOCKFILE_PATH = "skills.lock.json"
PROJECT_INSTALL_ACCEPTANCE_TRACE = [
    "PU-009-FR-001",
    "PU-009-FR-002",
    "PU-009-FR-003",
    "PU-009-SA-001",
    "PU-009-SA-002",
    "PU-009-VP-001",
]
PROJECT_MARKERS = ("AGENTS.md", ".git", ".agents")
APPROVED_TOP_LEVELS = frozenset({"SKILL.md", "agents", "references", "scripts", "assets"})
PROJECT_SKILL_ROOT = Path(".agents/skills")
RECEIPT_DIR = Path(".harness/receipts/skills-sdk/install")


@dataclass(frozen=True)
class ProjectInstallError(Exception):
    code: str
    message: str
    fix_suggestion: str
    receipt: dict[str, Any]


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


def _sha256_json(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"


def _json_atomic_replace(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    tmp_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp_path, path)


def _relative_to(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError as exc:
        raise ProjectInstallError(
            code="ERR_PATH_TRAVERSAL",
            message=f"resolved path escapes the project root: {path}",
            fix_suggestion="Choose a target inside --project-root.",
            receipt=_blocked_receipt(
                source_path=str(path),
                source_digest="sha256:blocked",
                target_root=str(root),
                conflicts=[f"path_escape:{path}"],
            ),
        ) from exc


def _first_symlink_in_path(root: Path, relative_path: Path) -> Path | None:
    current = root
    for part in relative_path.parts:
        current = current / part
        if current.is_symlink():
            return current
    return None


def _metadata_path_conflicts(root: Path, relative_path: Path) -> list[str]:
    conflicts: list[str] = []
    current = root
    parts = relative_path.parts
    for index, part in enumerate(parts):
        current = current / part
        current_relative = _relative_to(current, root)
        if current.is_symlink():
            conflicts.append(f"target_symlink:{current_relative}")
            break
        if not current.exists():
            continue
        is_leaf = index == len(parts) - 1
        if is_leaf:
            if not current.is_file():
                conflicts.append(f"metadata_invalid:{current_relative}")
        elif not current.is_dir():
            conflicts.append(f"metadata_invalid:{current_relative}")
            break
    return conflicts


def _missing_parent_dirs(path: Path, root: Path) -> list[str]:
    missing: list[str] = []
    current = root
    for part in path.parent.relative_to(root).parts:
        current = current / part
        if not current.exists():
            missing.append(_relative_to(current, root))
    return missing


def _package_name(query: str, source_root: Path, target_info: dict[str, Any]) -> str:
    handle = target_info.get("handle")
    package_name = str(handle or source_root.name or Path(query).stem).lstrip("$")
    return package_name.replace("/", "-")


def _resolve_project_root(project_root: str | None, repo_root: Path) -> Path:
    if not project_root:
        raise ProjectInstallError(
            code="ERR_VALIDATION",
            message="Real Skills SDK installs require an explicit --project-root.",
            fix_suggestion="ask sdk install <target> --apply --project-root /path/to/project --json --robot",
            receipt=_blocked_receipt(
                source_path="unknown",
                source_digest="sha256:blocked",
                target_root="missing",
                conflicts=["missing_project_root"],
            ),
        )
    candidate = Path(project_root).expanduser()
    if not candidate.is_absolute():
        raise ProjectInstallError(
            code="ERR_VALIDATION",
            message="--project-root must be an absolute path.",
            fix_suggestion="Pass an absolute project root path.",
            receipt=_blocked_receipt(
                source_path="unknown",
                source_digest="sha256:blocked",
                target_root=str(candidate),
                conflicts=["ambiguous_project_root"],
            ),
        )
    try:
        root = candidate.resolve(strict=True)
    except FileNotFoundError as exc:
        raise ProjectInstallError(
            code="ERR_VALIDATION",
            message=f"--project-root does not exist: {candidate}",
            fix_suggestion="Create the project root first, then retry with --apply.",
            receipt=_blocked_receipt(
                source_path="unknown",
                source_digest="sha256:blocked",
                target_root=str(candidate),
                conflicts=["missing_project_root"],
            ),
        ) from exc
    if not root.is_dir():
        raise ProjectInstallError(
            code="ERR_VALIDATION",
            message=f"--project-root must be a directory: {candidate}",
            fix_suggestion="Pass a directory that represents the target project.",
            receipt=_blocked_receipt(
                source_path="unknown",
                source_digest="sha256:blocked",
                target_root=str(root),
                conflicts=["project_root_not_directory"],
            ),
        )
    if root == Path(root.anchor).resolve() or root == Path.home().resolve():
        raise ProjectInstallError(
            code="ERR_VALIDATION",
            message="Refusing to install into filesystem root or operator home.",
            fix_suggestion="Pass a marked project directory instead of a broad root.",
            receipt=_blocked_receipt(
                source_path="unknown",
                source_digest="sha256:blocked",
                target_root=str(root),
                conflicts=["unsafe_project_root"],
            ),
        )
    if root == repo_root.resolve():
        raise ProjectInstallError(
            code="ERR_VALIDATION",
            message="Refusing to use the live agent-skills repository as the install target.",
            fix_suggestion="Use a marked temp project or a separate project checkout.",
            receipt=_blocked_receipt(
                source_path="unknown",
                source_digest="sha256:blocked",
                target_root=str(root),
                conflicts=["live_repo_target_root"],
            ),
        )
    if not any((root / marker).exists() for marker in PROJECT_MARKERS):
        raise ProjectInstallError(
            code="ERR_VALIDATION",
            message="--project-root must contain a project marker such as AGENTS.md, .git, or .agents.",
            fix_suggestion="Pass a real project root or add an explicit marker to the temp project.",
            receipt=_blocked_receipt(
                source_path="unknown",
                source_digest="sha256:blocked",
                target_root=str(root),
                conflicts=["missing_project_marker"],
            ),
        )
    return root


def _resolve_source_root(source_path: Path | None, query: str) -> Path:
    if source_path is None:
        source_path = Path(query)
    source = source_path.expanduser()
    if source.is_symlink():
        raise _source_error(str(source), "source_path_is_symlink")
    try:
        source = source.resolve(strict=True)
    except FileNotFoundError as exc:
        raise _source_error(str(source_path), "missing_source") from exc
    if source.is_symlink():
        raise _source_error(str(source), "source_path_is_symlink")
    if source.is_file() and source.name == "SKILL.md":
        source_root = source.parent
    elif source.is_dir():
        source_root = source
    else:
        raise _source_error(str(source), "source_must_be_skill_file_or_directory")
    skill_file = source_root / "SKILL.md"
    if not skill_file.is_file() or skill_file.is_symlink():
        raise _source_error(str(source_root), "missing_readable_skill_md")
    return source_root


def _source_error(source_path: str, conflict: str) -> ProjectInstallError:
    return ProjectInstallError(
        code="ERR_VALIDATION",
        message=f"Invalid Skills SDK install source: {conflict}.",
        fix_suggestion="Pass a local skill directory or SKILL.md file with regular files only.",
        receipt=_blocked_receipt(
            source_path=source_path,
            source_digest="sha256:blocked",
            target_root="unknown",
            conflicts=[conflict],
        ),
    )


def _source_files(source_root: Path) -> list[Path]:
    files: list[Path] = []
    for child in sorted(source_root.iterdir(), key=lambda path: path.name):
        if child.name not in APPROVED_TOP_LEVELS:
            if child.is_symlink():
                raise _source_error(str(child), "source_contains_symlink")
            if child.is_file() or child.is_dir():
                raise _source_error(str(child), "source_contains_unapproved_top_level")
            raise _source_error(str(child), "source_contains_special_file")
        if child.is_symlink():
            raise _source_error(str(child), "source_contains_symlink")
        if child.is_file():
            files.append(child)
            continue
        if not child.is_dir():
            raise _source_error(str(child), "source_contains_special_file")
        for path in sorted(child.rglob("*")):
            if path.is_symlink():
                raise _source_error(str(path), "source_contains_symlink")
            if path.is_file():
                files.append(path)
            elif not path.is_dir():
                raise _source_error(str(path), "source_contains_special_file")
    if source_root / "SKILL.md" not in files:
        files.insert(0, source_root / "SKILL.md")
    return files


def install_project_skill(
    repo_root: Path,
    *,
    query: str,
    source_path: Path | None,
    target_info: dict[str, Any],
    project_root: str | None,
    installed_at: str | None = None,
) -> dict[str, Any]:
    """Install a local skill into an explicit project root and emit durable evidence."""
    resolved_project_root = _resolve_project_root(project_root, repo_root)
    source_root = _resolve_source_root(source_path, query)
    files = _source_files(source_root)
    package_name = _package_name(query, source_root, target_info)
    target_base = resolved_project_root / PROJECT_SKILL_ROOT / package_name
    receipt_path = resolved_project_root / RECEIPT_DIR / f"{package_name}.json"
    lockfile_path = resolved_project_root / DEFAULT_LOCKFILE_PATH
    lockfile_before_digest = _sha256_file(lockfile_path) if lockfile_path.is_file() else None
    source_digest = _sha256_json(
        [{"path": path.relative_to(source_root).as_posix(), "digest": _sha256_file(path)} for path in files]
    )

    planned: list[dict[str, str]] = []
    conflicts: list[str] = []
    if target_base.exists():
        conflicts.append(f"target_exists:{_relative_to(target_base.resolve(), resolved_project_root)}")
    for source_file in files:
        relative = source_file.relative_to(source_root)
        target_relative_path = PROJECT_SKILL_ROOT / package_name / relative
        symlink_path = _first_symlink_in_path(resolved_project_root, target_relative_path)
        if symlink_path is not None:
            conflicts.append(f"target_symlink:{_relative_to(symlink_path, resolved_project_root)}")
        target_file = (target_base / relative).resolve()
        _relative_to(target_file, resolved_project_root)
        target_relative = _relative_to(target_file, resolved_project_root)
        planned.append(
            {
                "source_path": relative.as_posix(),
                "target_path": target_relative,
                "digest": _sha256_file(source_file),
            }
        )
        if target_file.exists():
            conflicts.append(f"target_exists:{target_relative}")
    if conflicts:
        raise ProjectInstallError(
            code="ERR_CONFLICT",
            message="Refusing to overwrite an existing Skills SDK install target.",
            fix_suggestion="Remove the existing target or wait for an explicit overwrite lifecycle slice.",
            receipt=_blocked_receipt(
                source_path=str(source_root),
                source_digest=source_digest,
                target_root=str(resolved_project_root),
                target_paths=[item["target_path"] for item in planned],
                conflicts=conflicts,
                lockfile_path=DEFAULT_LOCKFILE_PATH,
                lockfile_before_digest=lockfile_before_digest,
            ),
        )

    files_written: list[dict[str, str]] = []
    receipt_ref = _relative_to(receipt_path, resolved_project_root)
    for metadata_relative in (Path(DEFAULT_LOCKFILE_PATH), RECEIPT_DIR / f"{package_name}.json"):
        conflicts.extend(_metadata_path_conflicts(resolved_project_root, metadata_relative))
    if conflicts:
        raise ProjectInstallError(
            code="ERR_CONFLICT",
            message="Refusing to write Skills SDK install metadata through an unsafe target path.",
            fix_suggestion="Remove the conflicting metadata path or choose another project root.",
            receipt=_blocked_receipt(
                source_path=str(source_root),
                source_digest=source_digest,
                target_root=str(resolved_project_root),
                target_paths=[
                    *[item["target_path"] for item in planned],
                    DEFAULT_LOCKFILE_PATH,
                    receipt_ref,
                ],
                conflicts=conflicts,
                lockfile_path=DEFAULT_LOCKFILE_PATH,
                lockfile_before_digest=lockfile_before_digest,
            ),
        )
    dirs_created: list[str] = []
    lockfile_after_digest = lockfile_before_digest
    try:
        for item in planned:
            source_file = source_root / item["source_path"]
            target_file = resolved_project_root / item["target_path"]
            dirs_created.extend(path for path in _missing_parent_dirs(target_file, resolved_project_root) if path not in dirs_created)
            target_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source_file, target_file)
            files_written.append(item)

        installed_at_value = installed_at or os.environ.get("ASK_SKILLS_SDK_INSTALL_TIMESTAMP")
        if not installed_at_value:
            installed_at_value = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        lockfile = _load_lockfile(lockfile_path)
        lockfile["entries"][package_name] = {
            "name": package_name,
            "source_path": str(source_root),
            "source_digest": source_digest,
            "target_path": _relative_to(target_base.resolve(), resolved_project_root),
            "receipt_ref": receipt_ref,
            "installed_at": installed_at_value,
            "files": planned,
        }
        _json_atomic_replace(lockfile_path, lockfile)
        lockfile_after_digest = _sha256_file(lockfile_path)
        receipt = {
            "schema_version": INSTALL_RECEIPT_SCHEMA_VERSION,
            "schema_uri": INSTALL_RECEIPT_SCHEMA_URI,
            "status": "success",
            "operation": "install",
            "scope": "project",
            "source_path": str(source_root),
            "source_digest": source_digest,
            "target_root": str(resolved_project_root),
            "target_paths": [
                *[item["target_path"] for item in planned],
                DEFAULT_LOCKFILE_PATH,
                receipt_ref,
            ],
            "files_written": files_written,
            "files_skipped": [],
            "files_overwritten": [],
            "conflicts": [],
            "lockfile_path": DEFAULT_LOCKFILE_PATH,
            "lockfile_before_digest": lockfile_before_digest,
            "lockfile_after_digest": lockfile_after_digest,
            "rollback_metadata": {
                "status": "seed_only",
                "reason": "PU-009 records enough metadata for a future rollback/uninstall slice; it does not execute rollback.",
                "installed_files": [item["target_path"] for item in files_written],
            },
            "mutation_performed": True,
            "acceptance_trace": PROJECT_INSTALL_ACCEPTANCE_TRACE,
        }
        _json_atomic_replace(receipt_path, receipt)
        return receipt
    except OSError as exc:
        partial_receipt = {
            "schema_version": INSTALL_RECEIPT_SCHEMA_VERSION,
            "schema_uri": INSTALL_RECEIPT_SCHEMA_URI,
            "status": "partial",
            "operation": "install",
            "scope": "project",
            "source_path": str(source_root),
            "source_digest": source_digest,
            "target_root": str(resolved_project_root),
            "target_paths": [
                *dirs_created,
                *[item["target_path"] for item in files_written],
                DEFAULT_LOCKFILE_PATH,
                receipt_ref,
            ],
            "files_written": files_written,
            "files_skipped": [],
            "files_overwritten": [],
            "conflicts": [f"write_failed:{exc.__class__.__name__}"],
            "lockfile_path": DEFAULT_LOCKFILE_PATH,
            "lockfile_before_digest": lockfile_before_digest,
            "lockfile_after_digest": lockfile_after_digest,
            "rollback_metadata": {
                "status": "manual_cleanup_required",
                "reason": "Install write phase failed; inspect files_written and created directories before retrying.",
                "installed_files": [*dirs_created, *[item["target_path"] for item in files_written]],
            },
            "mutation_performed": bool(files_written or dirs_created),
            "acceptance_trace": PROJECT_INSTALL_ACCEPTANCE_TRACE,
        }
        try:
            _json_atomic_replace(receipt_path, partial_receipt)
        except OSError:
            pass
        raise ProjectInstallError(
            code="ERR_RUNTIME",
            message=f"Skills SDK project install failed during the write phase: {exc}",
            fix_suggestion="Inspect receipt data and remove partial files before retrying.",
            receipt=partial_receipt,
        ) from exc


def _load_lockfile(path: Path) -> dict[str, Any]:
    if path.is_file():
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            payload = {}
        if isinstance(payload, dict) and isinstance(payload.get("entries"), dict):
            payload.setdefault("schema_version", LOCKFILE_SCHEMA_VERSION)
            payload.setdefault("schema_uri", LOCKFILE_SCHEMA_URI)
            payload.setdefault("generated_by", "ask skills-sdk")
            return payload
    return {
        "schema_version": LOCKFILE_SCHEMA_VERSION,
        "schema_uri": LOCKFILE_SCHEMA_URI,
        "generated_by": "ask skills-sdk",
        "entries": {},
    }


def _blocked_receipt(
    *,
    source_path: str,
    source_digest: str,
    target_root: str,
    target_paths: list[str] | None = None,
    conflicts: list[str] | None = None,
    lockfile_path: str | None = None,
    lockfile_before_digest: str | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": INSTALL_RECEIPT_SCHEMA_VERSION,
        "schema_uri": INSTALL_RECEIPT_SCHEMA_URI,
        "status": "blocked",
        "operation": "install",
        "scope": "project",
        "source_path": source_path,
        "source_digest": source_digest,
        "target_root": target_root,
        "target_paths": target_paths or [],
        "files_written": [],
        "files_skipped": [],
        "files_overwritten": [],
        "conflicts": conflicts or [],
        "lockfile_path": lockfile_path,
        "lockfile_before_digest": lockfile_before_digest,
        "lockfile_after_digest": lockfile_before_digest,
        "rollback_metadata": {
            "status": "not_available",
            "reason": "Install was blocked before mutation; no rollback metadata was written.",
            "installed_files": [],
        },
        "mutation_performed": False,
        "acceptance_trace": PROJECT_INSTALL_ACCEPTANCE_TRACE,
    }
