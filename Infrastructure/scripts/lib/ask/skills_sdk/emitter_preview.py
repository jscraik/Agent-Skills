from __future__ import annotations

from pathlib import Path
from typing import Any


EMITTER_PREVIEW_SCHEMA_VERSION = "skills-sdk.emitter-preview-receipt.v0"
EMITTER_PREVIEW_SCHEMA_URI = (
    "https://agent-skills.local/schemas/skills-sdk/emitter-preview-receipt.v0.schema.json"
)
EMITTER_ACCEPTANCE_TRACE = ["PU-027", "FR-003", "FR-008", "SA-003", "VP-027"]
SUPPORTED_PROJECTIONS = frozenset({"runtime-skill"})
DEFAULT_TARGET_ROOT = ".agents/skills"
BLOCKED_SUMMARY = "emitter preview is blocked by contract validation."
PREVIEW_SUMMARY = "emitter preview produced a local projection write plan without writing files."


class EmitterPreviewError(ValueError):
    def __init__(self, receipt: dict[str, Any]) -> None:
        super().__init__(receipt["agent_summary"])
        self.receipt = receipt


def _repo_relative(repo_root: Path, path: Path) -> str:
    try:
        return path.resolve(strict=False).relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _check(check_id: str, status: str, message: str, evidence: list[str] | None = None) -> dict[str, Any]:
    return {
        "id": check_id,
        "status": status,
        "severity": "blocker",
        "message": message,
        "evidence": evidence or [],
    }


def _target_root_check(target_root: str) -> dict[str, Any]:
    normalized = _normalize_target_root(target_root)
    blocked_markers = ("://", "\\")
    allowed = (
        normalized == DEFAULT_TARGET_ROOT
        and not target_root.strip().startswith("/")
        and not any(marker in target_root for marker in blocked_markers)
    )
    return _check(
        "target_root_local_projection",
        "pass" if allowed else "blocker",
        "Emitter preview is limited to the local .agents/skills projection root.",
        [target_root],
    )


def _normalize_target_root(target_root: str) -> str:
    return target_root.strip().rstrip("/")


def _projection_check(projection: str) -> dict[str, Any]:
    return _check(
        "projection_supported",
        "pass" if projection in SUPPORTED_PROJECTIONS else "blocker",
        "Emitter preview currently supports only the runtime-skill projection contract.",
        [projection],
    )


def _hardening_check(hardening_receipt: dict[str, Any]) -> dict[str, Any]:
    status = str(hardening_receipt.get("status") or "")
    return _check(
        "package_hardened_before_emit",
        "pass" if status == "pass" else "blocker",
        "Emitter preview requires a passing package hardening receipt before write planning.",
        [f"hardening_status:{status}"],
    )


def _write_plan(repo_root: Path, package_receipt: dict[str, Any], target_root: str) -> list[dict[str, Any]]:
    manifest = package_receipt.get("manifest")
    source = manifest.get("source") if isinstance(manifest, dict) else {}
    source_root = str(source.get("root") or "").strip() if isinstance(source, dict) else ""
    package_id = str(package_receipt["package_id"])
    actions: list[dict[str, Any]] = []
    for file_record in package_receipt.get("manifest", {}).get("files", []):
        if not isinstance(file_record, dict):
            continue
        source_path = str(file_record.get("path") or "").strip()
        if not source_path:
            continue
        relative_source = Path(source_path).name
        if source_root and source_path.startswith(f"{source_root}/"):
            relative_source = source_path[len(source_root) + 1 :]
        target_path = Path(target_root) / package_id / relative_source
        actions.append(
            {
                "action": "write",
                "source_path": source_path,
                "target_path": target_path.as_posix(),
                "source_digest": str(file_record.get("sha256") or ""),
                "reason": "project runtime projection would mirror packaged skill source",
            }
        )
    if not actions:
        actions.append(
            {
                "action": "skip",
                "source_path": _repo_relative(repo_root, repo_root),
                "target_path": f"{target_root}/{package_id}",
                "source_digest": None,
                "reason": "package manifest has no files to project",
            }
        )
    return actions


def _receipt_target_root(checks: list[dict[str, Any]], normalized_target_root: str) -> str:
    target_root_status = next(check["status"] for check in checks if check["id"] == "target_root_local_projection")
    return normalized_target_root if target_root_status == "pass" else DEFAULT_TARGET_ROOT


def build_emitter_preview_receipt(
    repo_root: Path,
    *,
    package_receipt: dict[str, Any],
    hardening_receipt: dict[str, Any],
    projection: str = "runtime-skill",
    target_root: str = DEFAULT_TARGET_ROOT,
) -> dict[str, Any]:
    normalized_target_root = _normalize_target_root(target_root)
    checks = [
        _projection_check(projection),
        _target_root_check(target_root),
        _hardening_check(hardening_receipt),
    ]
    blockers = [check for check in checks if check["status"] == "blocker"]
    receipt_target_root = _receipt_target_root(checks, normalized_target_root)
    receipt = {
        "schema_version": EMITTER_PREVIEW_SCHEMA_VERSION,
        "schema_uri": EMITTER_PREVIEW_SCHEMA_URI,
        "status": "blocked" if blockers else "preview",
        "operation": "emitter_write_plan_preview",
        "projection": projection,
        "package_id": package_receipt["package_id"],
        "version": package_receipt["version"],
        "package_digest": package_receipt["package_digest"],
        "target_root": receipt_target_root,
        "write_plan": [] if blockers else _write_plan(repo_root, package_receipt, receipt_target_root),
        "required_receipts": ["package_digest_receipt", "package_hardening_receipt"],
        "emitter_checks": checks,
        "blockers": blockers,
        "mutation_performed": False,
        "artifact_emitted": False,
        "remote_publish_requested": False,
        "acceptance_trace": EMITTER_ACCEPTANCE_TRACE,
        "agent_summary": BLOCKED_SUMMARY if blockers else PREVIEW_SUMMARY,
    }
    if blockers:
        raise EmitterPreviewError(receipt)
    return receipt
