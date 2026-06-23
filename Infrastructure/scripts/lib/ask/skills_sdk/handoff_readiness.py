from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


HANDOFF_READINESS_SCHEMA_VERSION = "skills-sdk.eval-handoff-readiness.v0"
HANDOFF_READINESS_SCHEMA_URI = "https://agent-skills.local/schemas/skills-sdk/eval-handoff-readiness.v0.schema.json"
HANDOFF_READINESS_INPUT_SCHEMA_VERSION = "skills-sdk.eval-handoff-readiness-input.v1"

REQUIRED_LANE_IDS = (
    "deterministic_local_gates",
    "oss-local",
    "oss-cloud",
    "tessl-live-dry-run",
)

REQUIRED_ORDER = (
    "deterministic_local_gates",
    "oss-local",
    "patch_oss_local_failures",
    "oss-cloud",
    "patch_oss_cloud_failures",
    "tessl-live-dry-run",
    "tessl-live",
    "patch_tessl_failures",
)


def _safe_slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip()).strip("-")
    return slug or "skill"


def _repo_relative(repo_root: Path, path: Path) -> str:
    try:
        return path.resolve(strict=False).relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _skill_md(source_path: Path) -> Path:
    return source_path if source_path.name == "SKILL.md" else source_path / "SKILL.md"


def _skill_dir(source_path: Path) -> Path:
    return source_path.parent if source_path.name == "SKILL.md" else source_path


def default_handoff_readiness_path(repo_root: Path, source_path: Path) -> Path:
    return repo_root / ".harness" / "evidence" / "handoff" / _safe_slug(_skill_dir(source_path).name) / "eval-handoff-readiness.json"


def _load_json_object(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, str(exc)
    if not isinstance(payload, dict):
        return None, "json_root_not_object"
    return payload, None


def _check(check_id: str, status: str, message: str, evidence: list[str] | None = None) -> dict[str, Any]:
    return {"id": check_id, "status": status, "severity": "blocker", "message": message, "evidence": evidence or []}


def _resolve_evidence_path(repo_root: Path, value: object) -> Path | None:
    if not isinstance(value, str) or not value.strip():
        return None
    path = Path(value)
    return path if path.is_absolute() else repo_root / path


def _lane_index(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    lanes = payload.get("lanes")
    if not isinstance(lanes, list):
        return {}
    indexed: dict[str, dict[str, Any]] = {}
    for lane in lanes:
        if not isinstance(lane, dict):
            continue
        lane_id = lane.get("id")
        if isinstance(lane_id, str) and lane_id.strip():
            indexed[lane_id.strip()] = lane
    return indexed


def _lane_checks(repo_root: Path, lane_id: str, lane: dict[str, Any] | None) -> list[dict[str, Any]]:
    if lane is None:
        return [_missing_lane_check(lane_id)]

    status = lane.get("status")
    command = lane.get("command")
    checks = [
        _lane_status_check(status),
        _lane_command_check(lane_id, command),
    ]
    if status == "pass":
        checks.append(_lane_receipt_check(repo_root, lane_id, lane.get("receipt_path")))
        return checks
    checks.append(_blocked_lane_check(lane_id, lane.get("blocker")))
    return checks


def _missing_lane_check(lane_id: str) -> dict[str, Any]:
    return _check(
        "lane_present",
        "blocker",
        "Every live handoff lane must be represented by current evidence.",
        [lane_id],
    )


def _lane_status_check(status: Any) -> dict[str, Any]:
    return _check(
        "lane_status_pass",
        "pass" if status == "pass" else "blocker",
        "Required live handoff lanes must pass before live Tessl.",
        [str(status or "missing_status")],
    )


def _lane_command_check(lane_id: str, command: Any) -> dict[str, Any]:
    command_ok = isinstance(command, str) and command.strip()
    return _check(
        "lane_command_recorded",
        "pass" if command_ok else "blocker",
        "Each lane must record the exact command that produced its evidence.",
        [command] if command_ok else [lane_id],
    )


def _lane_receipt_check(repo_root: Path, lane_id: str, receipt_value: Any) -> dict[str, Any]:
    receipt_path = _resolve_evidence_path(repo_root, receipt_value)
    receipt_ok = receipt_path is not None and receipt_path.exists()
    return _check(
        "lane_receipt_path_exists",
        "pass" if receipt_ok else "blocker",
        "Passed lanes must point at an existing receipt or durable evidence artifact.",
        [_repo_relative(repo_root, receipt_path)] if receipt_path is not None else [lane_id],
    )


def _blocked_lane_check(lane_id: str, blocker: Any) -> dict[str, Any]:
    blocker_ok = isinstance(blocker, str) and blocker.strip()
    return _check(
        "blocked_lane_reason_recorded",
        "pass" if blocker_ok else "blocker",
        "Blocked or skipped lanes must record the blocker before live Tessl can proceed.",
        [blocker] if blocker_ok else [lane_id],
    )


def _lane_row(repo_root: Path, lane_id: str, lane: dict[str, Any] | None) -> dict[str, Any]:
    checks = _lane_checks(repo_root, lane_id, lane)
    receipt_path = lane.get("receipt_path") if isinstance(lane, dict) else None
    return {
        "id": lane_id,
        "status": lane.get("status") if isinstance(lane, dict) else None,
        "command": lane.get("command") if isinstance(lane, dict) else None,
        "receipt_path": receipt_path if isinstance(receipt_path, str) else None,
        "blocker": lane.get("blocker") if isinstance(lane, dict) else None,
        "checks": checks,
        "blockers": [check for check in checks if check["status"] == "blocker"],
    }


def _readiness_checks(repo_root: Path, path: Path, payload: dict[str, Any] | None, error: str | None) -> list[dict[str, Any]]:
    return [
        _check(
            "readiness_artifact_present",
            "pass" if payload is not None and error is None else "blocker",
            "Live Tessl requires a current handoff readiness artifact under .harness/evidence.",
            [_repo_relative(repo_root, path)] if payload is not None else [error or "missing_readiness_artifact"],
        ),
        _check(
            "readiness_schema_supported",
            "pass" if payload and payload.get("schema_version") == HANDOFF_READINESS_INPUT_SCHEMA_VERSION else "blocker",
            "The handoff readiness input schema_version must match the SDK contract.",
            [str(payload.get("schema_version"))] if payload else [HANDOFF_READINESS_INPUT_SCHEMA_VERSION],
        ),
    ]


def _next_actions(repo_root: Path, blockers: list[dict[str, Any]], readiness_path: Path) -> list[str]:
    if any(blocker["id"] == "readiness_artifact_present" for blocker in blockers):
        return [
            f"Create {_repo_relative(repo_root, readiness_path)} with deterministic, oss-local, oss-cloud, and Tessl dry-run lane receipts."
        ]
    if any(blocker["id"] == "lane_present" for blocker in blockers):
        return ["Add the missing required lane rows before running live Tessl."]
    if any(blocker["id"] == "lane_status_pass" for blocker in blockers):
        return ["Rerun from oss-local after patching until deterministic gates, oss-local, oss-cloud, and Tessl dry-run all pass."]
    if any(blocker["id"] == "lane_receipt_path_exists" for blocker in blockers):
        return ["Move lane evidence into durable .harness evidence paths and update receipt_path values."]
    return ["Run live Tessl; if it fails, owner-classify the failure and return to oss-local."]


def _agent_summary(blockers: list[dict[str, Any]], query: str) -> str:
    if blockers:
        return f"Handoff readiness for {query} is blocked: live Tessl requires current deterministic, oss-local, oss-cloud, and Tessl dry-run evidence."
    return f"Handoff readiness for {query} is complete for live Tessl."


def build_handoff_readiness_receipt(
    repo_root: Path,
    *,
    source_path: Path,
    query: str,
    readiness_path: Path | None = None,
) -> dict[str, Any]:
    skill_path = _skill_md(source_path)
    actual_readiness_path = readiness_path or default_handoff_readiness_path(repo_root, source_path)
    payload, error = _load_json_object(actual_readiness_path) if actual_readiness_path.is_file() else (None, "missing_readiness_artifact")
    lane_map = _lane_index(payload or {})
    lanes = [_lane_row(repo_root, lane_id, lane_map.get(lane_id)) for lane_id in REQUIRED_LANE_IDS]
    checks = _readiness_checks(repo_root, actual_readiness_path, payload, error)
    blockers = [check for check in checks if check["status"] == "blocker"] + [
        blocker for lane in lanes for blocker in lane["blockers"]
    ]
    return {
        "schema_version": HANDOFF_READINESS_SCHEMA_VERSION,
        "schema_uri": HANDOFF_READINESS_SCHEMA_URI,
        "status": "blocked" if blockers else "preview",
        "operation": "eval_handoff_readiness_preview",
        "query": query,
        "skill_path": _repo_relative(repo_root, skill_path),
        "readiness_path": _repo_relative(repo_root, actual_readiness_path),
        "required_lanes": list(REQUIRED_LANE_IDS),
        "required_order": list(REQUIRED_ORDER),
        "lanes": lanes,
        "quality_checks": checks,
        "blockers": blockers,
        "ready_for_live_tessl": not blockers,
        "required_next_actions": _next_actions(repo_root, blockers, actual_readiness_path),
        "mutation_performed": False,
        "promotion_performed": False,
        "agent_summary": _agent_summary(blockers, query),
    }
