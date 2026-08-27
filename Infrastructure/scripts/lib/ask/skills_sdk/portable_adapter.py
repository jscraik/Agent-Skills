from __future__ import annotations

import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from skills_sdk.models.packaging import PackageReceipt
from skills_sdk.models.validation import SkillPackageValidation
from skills_sdk.packaging import build_skill_package
from skills_sdk.validation import SkillValidationPolicy, validate_skill_package


_GIT_REVISION_RE = re.compile(r"^[0-9a-f]{40}$")
_GIT_DISCOVERY_ENVIRONMENT = frozenset(
    {
        "GIT_ALTERNATE_OBJECT_DIRECTORIES",
        "GIT_CEILING_DIRECTORIES",
        "GIT_COMMON_DIR",
        "GIT_DIR",
        "GIT_INDEX_FILE",
        "GIT_OBJECT_DIRECTORY",
        "GIT_PREFIX",
        "GIT_WORK_TREE",
    }
)
PortableOperation = Literal["validate", "build"]


@dataclass(frozen=True, slots=True)
class PortableAdapterBlocker:
    """A host-side provenance blocker raised before portable SDK delegation."""

    code: Literal[
        "source_not_git",
        "source_revision_unavailable",
        "source_status_unavailable",
        "source_changed_during_validation",
        "source_owner_mismatch",
        "source_not_immutable",
    ]
    message: str


@dataclass(frozen=True, slots=True)
class PortableSource:
    """Git provenance resolved for one standalone package source."""

    package_root: Path
    owner_root: Path
    source_revision: str
    dirty: bool


@dataclass(frozen=True, slots=True)
class PortableAdapterSuccess:
    """SDK result plus host provenance that must not enter portable payloads."""

    operation: PortableOperation
    source: PortableSource
    payload: SkillPackageValidation | PackageReceipt


PortableResult = PortableAdapterSuccess | PortableAdapterBlocker


def _git_result(directory: Path, *arguments: str) -> tuple[bool, str]:
    environment = {
        name: value
        for name, value in os.environ.items()
        if name not in _GIT_DISCOVERY_ENVIRONMENT
    }
    try:
        completed = subprocess.run(
            ["git", "-C", str(directory), *arguments],
            check=False,
            capture_output=True,
            env=environment,
            text=True,
        )
    except OSError:
        return False, ""
    return completed.returncode == 0, completed.stdout.strip()


def _git_output(directory: Path, *arguments: str) -> str | None:
    succeeded, value = _git_result(directory, *arguments)
    return value if succeeded and value else None


def _package_root(source_path: Path) -> Path:
    return source_path.parent if source_path.name == "SKILL.md" else source_path


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(root.resolve(strict=False))
    except ValueError:
        return False
    return True


def _is_dirty(owner_root: Path, package_root: Path) -> bool | None:
    try:
        relative = package_root.resolve(strict=False).relative_to(
            owner_root.resolve(strict=False)
        )
    except ValueError:
        return None
    succeeded, status = _git_result(
        owner_root,
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
        "--ignored=matching",
        "--",
        relative.as_posix(),
    )
    if not succeeded:
        return None
    return bool(status)


def resolve_portable_source(
    source_path: Path,
    *,
    expected_owner_root: Path | None = None,
) -> PortableSource | PortableAdapterBlocker:
    """Resolve truthful Git provenance for a package without mutating it."""

    package_root = _package_root(source_path).absolute()
    owner_value = _git_output(package_root, "rev-parse", "--show-toplevel")
    if owner_value is None:
        return PortableAdapterBlocker(
            "source_not_git", "package source is not in a Git worktree"
        )
    owner_root = Path(owner_value).resolve(strict=False)
    if not _is_within(package_root, owner_root):
        return PortableAdapterBlocker(
            "source_owner_mismatch", "package source is outside its resolved Git owner"
        )
    if expected_owner_root is not None and owner_root != expected_owner_root.resolve(
        strict=False
    ):
        return PortableAdapterBlocker(
            "source_owner_mismatch",
            "package source does not belong to the expected Git owner",
        )
    revision = _git_output(owner_root, "rev-parse", "HEAD")
    if revision is None or _GIT_REVISION_RE.fullmatch(revision) is None:
        return PortableAdapterBlocker(
            "source_revision_unavailable", "package source has no valid Git revision"
        )
    dirty = _is_dirty(owner_root, package_root)
    if dirty is None:
        return PortableAdapterBlocker(
            "source_status_unavailable",
            "package source status could not be determined",
        )
    return PortableSource(package_root, owner_root, revision, dirty)


def _package_state_changed(
    before: SkillPackageValidation,
    after: SkillPackageValidation,
) -> bool:
    """Compare two SDK-owned filesystem captures without host traversal."""

    return (
        before.status != after.status
        or before.candidate != after.candidate
        or before.identity != after.identity
        or before.files != after.files
        or before.findings != after.findings
    )


def _delegate_operation(
    source: PortableSource,
    operation: PortableOperation,
    captured: SkillPackageValidation,
    policy: SkillValidationPolicy | None,
) -> SkillPackageValidation | PackageReceipt:
    if operation == "validate":
        return captured
    return build_skill_package(
        source.package_root,
        source_revision=source.source_revision,
        policy=policy,
    )


def _delegation_change_blocker(
    source: PortableSource,
    operation: PortableOperation,
    captured: SkillPackageValidation,
    payload: SkillPackageValidation | PackageReceipt,
    policy: SkillValidationPolicy | None,
) -> PortableAdapterBlocker | None:
    current_revision = _git_output(source.owner_root, "rev-parse", "HEAD")
    if current_revision != source.source_revision:
        return PortableAdapterBlocker(
            "source_changed_during_validation",
            "package source revision changed during SDK delegation",
        )
    current = validate_skill_package(
        source.package_root,
        source_revision=source.source_revision,
        policy=policy,
    )
    content_changed = _package_state_changed(captured, current)
    build_candidate_changed = (
        operation == "build"
        and payload.candidate is not None
        and payload.candidate != captured.candidate
    )
    if content_changed or build_candidate_changed:
        return PortableAdapterBlocker(
            "source_changed_during_validation",
            "package source content changed during SDK delegation",
        )
    return None


def run_portable_validation(
    source_path: Path,
    *,
    operation: PortableOperation,
    expected_owner_root: Path | None = None,
    policy: SkillValidationPolicy | None = None,
) -> PortableResult:
    """Delegate to Skills SDK only after host provenance is resolved."""

    if operation not in {"validate", "build"}:
        raise ValueError(f"unsupported portable operation: {operation}")
    source = resolve_portable_source(
        source_path, expected_owner_root=expected_owner_root
    )
    if isinstance(source, PortableAdapterBlocker):
        return source
    if operation == "build" and source.dirty:
        return PortableAdapterBlocker(
            "source_not_immutable", "package build requires a clean Git-owned source"
        )
    captured = validate_skill_package(
        source.package_root,
        source_revision=source.source_revision,
        policy=policy,
    )
    payload = _delegate_operation(source, operation, captured, policy)
    blocker = _delegation_change_blocker(
        source,
        operation,
        captured,
        payload,
        policy,
    )
    if blocker is not None:
        return blocker
    return PortableAdapterSuccess(operation, source, payload)


__all__ = [
    "PortableAdapterBlocker",
    "PortableAdapterSuccess",
    "PortableOperation",
    "PortableResult",
    "PortableSource",
    "resolve_portable_source",
    "run_portable_validation",
]
