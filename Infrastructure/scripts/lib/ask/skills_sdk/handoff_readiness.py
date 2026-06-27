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
    "tessl-local-proof",
    "tessl-live-dry-run",
)

REQUIRED_ORDER = (
    "deterministic_local_gates",
    "oss-local",
    "patch_oss_local_failures",
    "oss-cloud",
    "patch_oss_cloud_failures",
    "tessl-local-proof",
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
        checks.append(_lane_receipt_semantics_check(repo_root, lane_id, lane))
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
    placeholder_free = command_ok and not _has_command_placeholder(command)
    return _check(
        "lane_command_recorded",
        "pass" if command_ok and placeholder_free else "blocker",
        "Each lane must record the exact executable command that produced or repairs its evidence.",
        [command] if command_ok else [lane_id],
    )


def _has_command_placeholder(command: str) -> bool:
    return bool(re.search(r"<[^>]+>", command))


def _lane_receipt_check(repo_root: Path, lane_id: str, receipt_value: Any) -> dict[str, Any]:
    receipt_path = _resolve_evidence_path(repo_root, receipt_value)
    receipt_ok = receipt_path is not None and receipt_path.exists()
    return _check(
        "lane_receipt_path_exists",
        "pass" if receipt_ok else "blocker",
        "Passed lanes must point at an existing receipt or durable evidence artifact.",
        [_repo_relative(repo_root, receipt_path)] if receipt_path is not None else [lane_id],
    )


def _receipt_status(payload: dict[str, Any]) -> str | None:
    for key in ("status", "receipt_status", "eval_status", "tessl_eval_status"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    for nested_receipt in _nested_receipt_payloads(payload):
        value = nested_receipt.get("status")
        if isinstance(value, str) and value.strip():
            return value.strip()
    tessl_eval = payload.get("tessl_eval")
    if isinstance(tessl_eval, dict):
        value = tessl_eval.get("status")
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _receipt_profile(payload: dict[str, Any]) -> str | None:
    for key in ("profile", "codex_profile", "judge_profile_id", "lane"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    judge_profile = payload.get("judge_profile")
    if isinstance(judge_profile, dict):
        value = judge_profile.get("id")
        if isinstance(value, str) and value.strip():
            return value.strip()
    for nested_receipt in _nested_receipt_payloads(payload):
        for key in ("profile", "codex_profile", "judge_profile_id", "lane"):
            value = nested_receipt.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return None


def _nested_receipt_payloads(payload: dict[str, Any]) -> list[dict[str, Any]]:
    receipts: list[dict[str, Any]] = []
    direct = payload.get("receipt")
    if isinstance(direct, dict):
        receipts.append(direct)
    data = payload.get("data")
    if isinstance(data, dict):
        for value in data.values():
            if isinstance(value, dict) and isinstance(value.get("receipt"), dict):
                receipts.append(value["receipt"])
    return receipts


def _lane_receipt_semantics_check(repo_root: Path, lane_id: str, lane: dict[str, Any]) -> dict[str, Any]:
    loaded = _load_lane_receipt(repo_root, lane_id, lane.get("receipt_path"))
    if loaded["check"] is not None:
        return loaded["check"]

    receipt_path = loaded["path"]
    payload = loaded["payload"]
    status = (_receipt_status(payload) or "missing_status").strip().lower()
    profile_check = _lane_profile_semantics(lane_id, lane, payload)
    evidence = _lane_semantics_evidence(repo_root, receipt_path, status, profile_check)
    passing_statuses = {"pass", "success", "scored"}
    return _check(
        "lane_receipt_semantics_valid",
        "pass" if status in passing_statuses and profile_check["ok"] else "blocker",
        "Passed lane receipts must prove the lane status and profile they are standing in for.",
        evidence,
    )


def _load_lane_receipt(repo_root: Path, lane_id: str, receipt_value: Any) -> dict[str, Any]:
    receipt_path = _resolve_evidence_path(repo_root, receipt_value)
    if receipt_path is None or not receipt_path.exists():
        check = _check(
            "lane_receipt_semantics_valid",
            "blocker",
            "Passed lanes must point at a readable receipt whose status and lane semantics can be checked.",
            [lane_id],
        )
        return {"path": None, "payload": {}, "check": check}
    payload, error = _load_json_object(receipt_path)
    if payload is None:
        check = _check(
            "lane_receipt_semantics_valid",
            "blocker",
            "Passed lanes must point at a JSON receipt, not an opaque or unreadable artifact.",
            [_repo_relative(repo_root, receipt_path), error or "invalid_json"],
        )
        return {"path": receipt_path, "payload": {}, "check": check}
    return {"path": receipt_path, "payload": payload, "check": None}


def _lane_profile_semantics(lane_id: str, lane: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    profile = _receipt_profile(payload)
    expected_profile = None
    if lane_id in {"oss-local", "oss-cloud"}:
        expected_profile = lane_id
        codex_exec_invoked = _receipt_codex_exec_invoked(payload)
        return {
            "ok": profile == expected_profile and codex_exec_invoked,
            "profile": profile,
            "expected": f"{expected_profile} with codex_exec_invoked=true",
            "codex_exec_invoked": codex_exec_invoked,
        }
    if lane_id == "tessl-live-dry-run":
        return _tessl_live_dry_run_semantics(lane, payload, profile)
    if lane_id == "tessl-local-proof":
        return _tessl_local_proof_semantics(lane, payload, profile)
    return {"ok": True, "profile": profile, "expected": expected_profile}


def _tessl_live_dry_run_semantics(lane: dict[str, Any], payload: dict[str, Any], profile: str | None) -> dict[str, Any]:
    command = str(lane.get("command") or "")
    command_ok = "--tessl-live-dry-run" in command
    receipt_ok = _receipt_has_tessl_live_dry_run(payload)
    return {
        "ok": command_ok and receipt_ok,
        "profile": profile,
        "expected": "command includes --tessl-live-dry-run and receipt records tessl_eval.dry_run=true",
        "tessl_live_dry_run": receipt_ok,
    }


def _receipt_has_tessl_live_dry_run(payload: dict[str, Any]) -> bool:
    for candidate in _tessl_eval_payloads(payload):
        if candidate.get("dry_run") is not True:
            continue
        status = str(candidate.get("status") or payload.get("status") or "").strip().lower()
        if status in {"pass", "success"}:
            return True
    return False


def _tessl_eval_payloads(payload: dict[str, Any]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    tessl_eval = payload.get("tessl_eval")
    if isinstance(tessl_eval, dict):
        candidates.append(tessl_eval)
    data = payload.get("data")
    if isinstance(data, dict):
        nested_tessl_eval = data.get("tessl_eval")
        if isinstance(nested_tessl_eval, dict):
            candidates.append(nested_tessl_eval)
        for value in data.values():
            if isinstance(value, dict):
                nested = value.get("tessl_eval")
                if isinstance(nested, dict):
                    candidates.append(nested)
    return candidates


def _tessl_local_proof_semantics(lane: dict[str, Any], payload: dict[str, Any], profile: str | None) -> dict[str, Any]:
    command = str(lane.get("command") or "")
    command_ok = "tessl-local-proof" in command and "--execute" in command
    receipt_ok = any(
        nested.get("schema_version") == "skills-sdk.tessl-local-proof.v1"
        and nested.get("execute") is True
        and nested.get("status") == "pass"
        for nested in _nested_receipt_payloads(payload)
    )
    return {
        "ok": command_ok and receipt_ok,
        "profile": profile,
        "expected": "command includes tessl-local-proof --execute",
    }


def _receipt_codex_exec_invoked(payload: dict[str, Any]) -> bool:
    if payload.get("codex_exec_invoked") is True:
        return True
    for nested_receipt in _nested_receipt_payloads(payload):
        if nested_receipt.get("codex_exec_invoked") is True:
            return True
    return False


def _lane_semantics_evidence(
    repo_root: Path,
    receipt_path: Path,
    status: str,
    profile_check: dict[str, Any],
) -> list[str]:
    evidence = [
        _repo_relative(repo_root, receipt_path),
        f"status={status}",
    ]
    expected = profile_check.get("expected")
    if expected is not None:
        evidence.append(f"profile={profile_check.get('profile') or 'missing'}")
        evidence.append(f"expected={expected}")
    if "codex_exec_invoked" in profile_check:
        evidence.append(f"codex_exec_invoked={profile_check.get('codex_exec_invoked')}")
    if "tessl_live_dry_run" in profile_check:
        evidence.append(f"tessl_live_dry_run={profile_check.get('tessl_live_dry_run')}")
    return evidence


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


def _next_actions(
    repo_root: Path,
    blockers: list[dict[str, Any]],
    readiness_path: Path,
    lanes: list[dict[str, Any]] | None = None,
) -> list[str]:
    blocker_ids = {str(blocker["id"]) for blocker in blockers}
    if "readiness_artifact_present" in blocker_ids:
        return [
            f"Create {_repo_relative(repo_root, readiness_path)} with deterministic, oss-local, oss-cloud, and Tessl dry-run lane receipts."
        ]
    command_actions = _lane_command_next_actions(blocker_ids)
    if command_actions:
        return command_actions
    if _lane_has_runtime_blocker(lanes or [], "oss-local"):
        return [_OSS_LOCAL_RUNTIME_BLOCKER_ACTION]
    return _lane_status_next_actions(blocker_ids)


_OSS_LOCAL_RUNTIME_BLOCKER_ACTION = (
    "Preserve the oss-local blocked_runtime receipt, run oss-cloud as a diagnostic continuation, "
    "and keep live Tessl blocked until oss-local is repaired or an explicit skip receipt is approved."
)


def _lane_command_next_actions(blocker_ids: set[str]) -> list[str]:
    if "lane_command_recorded" in blocker_ids:
        return [
            "Replace placeholder lane commands with exact replay commands and durable receipt_path values before rerunning handoff-readiness.",
            "For oss-local, first run ./bin/ask sdk eval run <skill> --runner internal --mode smoke --codex-profile oss-local --json --robot, then record its durable receipt_path.",
            "Use the A/B judge route only when a comparative baseline and fixture have already been materialized.",
        ]
    if "lane_present" in blocker_ids:
        return ["Add the missing required lane rows before running live Tessl."]
    return []


def _lane_status_next_actions(blocker_ids: set[str]) -> list[str]:
    if "lane_status_pass" in blocker_ids:
        return ["Rerun from oss-local after patching until deterministic gates, oss-local, oss-cloud, and Tessl dry-run all pass."]
    if "lane_receipt_path_exists" in blocker_ids:
        return ["Move lane evidence into durable .harness evidence paths and update receipt_path values."]
    return ["Run live Tessl; if it fails, owner-classify the failure and return to oss-local."]


def _lane_has_runtime_blocker(lanes: list[dict[str, Any]], lane_id: str) -> bool:
    for lane in lanes:
        if lane.get("id") != lane_id:
            continue
        blocker = lane.get("blocker")
        return isinstance(blocker, str) and "blocked_runtime" in blocker
    return False


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
        "required_next_actions": _next_actions(repo_root, blockers, actual_readiness_path, lanes),
        "mutation_performed": False,
        "promotion_performed": False,
        "agent_summary": _agent_summary(blockers, query),
    }
