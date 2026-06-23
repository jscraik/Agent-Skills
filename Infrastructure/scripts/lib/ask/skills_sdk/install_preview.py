from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


INSTALL_PREVIEW_SCHEMA_VERSION = "skills-sdk.install-preview.v1"
INSTALL_PREVIEW_SCHEMA_URI = (
    "https://agent-skills.local/schemas/skills-sdk/install-preview.v1.schema.json"
)
LOCKFILE_PREVIEW_SCHEMA_VERSION = "skills-sdk.lockfile-preview.v1"
LOCKFILE_PREVIEW_SCHEMA_URI = (
    "https://agent-skills.local/schemas/skills-sdk/lockfile-preview.v1.schema.json"
)
DEFAULT_LOCKFILE_PATH = "skills.lock.json"
INSTALL_PREVIEW_ACCEPTANCE_TRACE = ["FR-006", "FR-010", "SA-020", "SA-021", "VP-021"]
LOCKFILE_PREVIEW_ACCEPTANCE_TRACE = ["FR-006", "SA-020", "SA-021", "VP-021"]


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


def _sha256_json(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"


def _scope_target_path(scope: str, package_name: str) -> str:
    if scope == "project":
        return f".agents/skills/{package_name}"
    if scope == "workspace":
        return f".codex/skills/{package_name}"
    return f"~/.codex/skills/{package_name}"


def build_install_preview(
    repo_root: Path,
    *,
    query: str,
    scope: str,
    source_path: Path | None,
    target_info: dict[str, Any],
) -> dict[str, Any]:
    """Build a schema-shaped install preview without mutating install state."""
    source_exists = bool(source_path and source_path.is_file())
    handle = target_info.get("handle")
    source_label = str(target_info.get("source_path") or query).strip()
    package_name = str(handle or Path(source_label).parent.name or Path(query).name).lstrip("$")
    target_path = _scope_target_path(scope, package_name)
    lockfile_path = repo_root / DEFAULT_LOCKFILE_PATH
    before_digest = _sha256_file(lockfile_path) if lockfile_path.is_file() else None
    source_digest = _sha256_file(source_path) if source_exists and source_path else "sha256:missing-source"
    lockfile_after_model = {
        "lockfile_path": DEFAULT_LOCKFILE_PATH,
        "operation": "add" if source_exists else "none",
        "target_path": target_path,
        "source_digest": source_digest,
    }
    conflicts: list[str] = []
    resolved_target = repo_root / target_path if not target_path.startswith("~") else None
    if resolved_target and resolved_target.exists():
        conflicts.append(f"target_exists:{target_path}")

    lockfile_delta_preview = {
        "schema_version": LOCKFILE_PREVIEW_SCHEMA_VERSION,
        "schema_uri": LOCKFILE_PREVIEW_SCHEMA_URI,
        "lockfile_path": DEFAULT_LOCKFILE_PATH,
        "operation": "add" if source_exists else "none",
        "before_digest": before_digest,
        "after_digest": _sha256_json(lockfile_after_model) if source_exists else before_digest,
        "would_write": False,
        "acceptance_trace": LOCKFILE_PREVIEW_ACCEPTANCE_TRACE,
    }
    receipt_ref = (
        ".harness/receipts/skills-sdk/install-preview/"
        f"{package_name.replace('/', '-') or 'unknown'}.json"
    )
    return {
        "schema_version": INSTALL_PREVIEW_SCHEMA_VERSION,
        "schema_uri": INSTALL_PREVIEW_SCHEMA_URI,
        "scope": scope,
        "target_paths": [target_path, DEFAULT_LOCKFILE_PATH],
        "digest": source_digest,
        "permission_summary": ["filesystem_read"],
        "trust_state": "requires_approval" if source_exists else "blocked",
        "conflicts": conflicts,
        "lockfile_delta_preview": lockfile_delta_preview,
        "rollback_note": "Preview only; no rollback journal is needed because no write occurred.",
        "mutation_performed": False,
        "receipt_ref": receipt_ref,
        "acceptance_trace": INSTALL_PREVIEW_ACCEPTANCE_TRACE,
    }
