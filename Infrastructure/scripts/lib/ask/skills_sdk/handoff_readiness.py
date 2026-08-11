from __future__ import annotations

import json
import hashlib
import re
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from ask.skills_sdk.handoff_readiness_tessl import (
    agent_summary as _agent_summary,
    blocked_next_gates as _blocked_next_gates,
    next_actions as _next_actions,
    oss_release_scenario_coverage_checks as _oss_release_scenario_coverage_checks,
    tessl_score_checks as _tessl_score_checks,
    tessl_score_receipt as _tessl_score_receipt,
    tessl_score_summary as _tessl_score_summary,
)


HANDOFF_READINESS_SCHEMA_VERSION = "skills-sdk.eval-handoff-readiness.v1"
HANDOFF_READINESS_SCHEMA_URI = "https://agent-skills.local/schemas/skills-sdk/eval-handoff-readiness.v1.schema.json"
HANDOFF_READINESS_INPUT_SCHEMA_VERSION = "skills-sdk.eval-handoff-readiness-input.v2"
HANDOFF_READINESS_MAX_AGE = timedelta(hours=24)

REQUIRED_LANE_IDS = (
    "mechanical_validation",
    "security_risk_modes",
    "scenario_quality",
    "scorer_quality",
    "scorer_calibration",
    "deterministic_local_gates",
    "oss-local",
    "oss-cloud",
    "tessl-local-proof",
    "tessl-live-dry-run",
)

PRE_TESSL_DRY_RUN_LANE_IDS = REQUIRED_LANE_IDS[:-1]

REQUIRED_ORDER = (
    "mechanical_validation",
    "security_risk_modes",
    "scenario_quality",
    "scorer_quality",
    "scorer_calibration",
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


def default_tessl_score_path(repo_root: Path, source_path: Path) -> Path:
    return repo_root / ".harness" / "evidence" / "handoff" / _safe_slug(_skill_dir(source_path).name) / "tessl-score-preview.json"


def build_candidate_identity(repo_root: Path, source_path: Path) -> dict[str, str]:
    """Return deterministic source and scenario identities for a live handoff."""
    skill_dir = _skill_dir(source_path)
    source_digest = _tree_digest(skill_dir)
    scenario_digest = _scenario_digest(skill_dir)
    return {
        "source_path": _repo_relative(repo_root, _skill_md(source_path)),
        "candidate_digest": source_digest,
        "scenario_set_digest": scenario_digest,
    }


def _tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file() and not item.is_symlink()):
        relative = path.relative_to(root).as_posix()
        if relative.startswith(("__pycache__/", ".harness/", ".agents/", ".codex/")):
            continue
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _scenario_digest(skill_dir: Path) -> str:
    digest = hashlib.sha256()
    scenario_paths = [skill_dir / "references" / "evals.yaml"]
    evals_dir = skill_dir / "references" / "evals"
    if evals_dir.is_dir():
        scenario_paths.extend(sorted(path for path in evals_dir.rglob("*") if path.is_file() and not path.is_symlink()))
    for path in scenario_paths:
        if not path.is_file():
            continue
        relative = path.relative_to(skill_dir).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


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
    if lane_id == "mechanical_validation":
        return _mechanical_validation_semantics(lane, payload, profile)
    if lane_id == "security_risk_modes":
        return _security_risk_modes_semantics(lane, payload, profile)
    if lane_id in {"scenario_quality", "scorer_quality", "scorer_calibration"}:
        return _sdk_quality_gate_semantics(lane_id, lane, payload, profile)
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


def _mechanical_validation_semantics(lane: dict[str, Any], payload: dict[str, Any], profile: str | None) -> dict[str, Any]:
    command = str(lane.get("command") or "")
    command_ok = "skills audit" in command and "package verify" in command
    return {
        "ok": command_ok,
        "profile": profile,
        "expected": "command records both strict skills audit and package verify",
    }


def _security_risk_modes_semantics(lane: dict[str, Any], payload: dict[str, Any], profile: str | None) -> dict[str, Any]:
    command = str(lane.get("command") or "")
    command_ok = "sdk security risk-modes" in command and "--preview" in command
    return {
        "ok": command_ok,
        "profile": profile,
        "expected": "command records sdk security risk-modes --preview",
    }


def _sdk_quality_gate_semantics(
    lane_id: str,
    lane: dict[str, Any],
    payload: dict[str, Any],
    profile: str | None,
) -> dict[str, Any]:
    command = str(lane.get("command") or "")
    expected_command = lane_id.replace("_", "-")
    command_ok = f"sdk eval {expected_command}" in command and "--preview" in command
    return {
        "ok": command_ok,
        "profile": profile,
        "expected": f"command records sdk eval {expected_command} --preview",
    }


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


def _receipt_case_count(payload: dict[str, Any]) -> int | None:
    for key in ("case_count", "scenario_count", "scored_scenario_count"):
        value = payload.get(key)
        if isinstance(value, int):
            return value
    for nested_receipt in _nested_receipt_payloads(payload):
        nested = _receipt_case_count(nested_receipt)
        if nested is not None:
            return nested
    return None


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
    declared_status = lane.get("status") if isinstance(lane, dict) else None
    blockers = [check for check in checks if check["status"] == "blocker"]
    effective_status = _effective_lane_status(declared_status, blockers)
    blocker = _effective_lane_blocker(lane, blockers)
    return {
        "id": lane_id,
        "status": effective_status,
        "declared_status": declared_status if isinstance(declared_status, str) else None,
        "command": lane.get("command") if isinstance(lane, dict) else None,
        "receipt_path": receipt_path if isinstance(receipt_path, str) else None,
        "blocker": blocker,
        "checks": checks,
        "blockers": blockers,
    }


def _effective_lane_status(declared_status: Any, blockers: list[dict[str, Any]]) -> str | None:
    if blockers:
        if declared_status in {"blocked", "skip"}:
            return declared_status
        return "blocked"
    return declared_status if isinstance(declared_status, str) else None


def _effective_lane_blocker(lane: dict[str, Any] | None, blockers: list[dict[str, Any]]) -> str | None:
    declared_blocker = lane.get("blocker") if isinstance(lane, dict) else None
    if isinstance(declared_blocker, str) and declared_blocker.strip():
        return declared_blocker
    if not blockers:
        return None
    blocker_ids = ",".join(str(blocker.get("id") or "unknown") for blocker in blockers)
    return f"blocked_validation: {blocker_ids}"


def _readiness_checks(repo_root: Path, path: Path, payload: dict[str, Any] | None, error: str | None) -> list[dict[str, Any]]:
    checks = [
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
    if payload is None:
        return checks

    candidate = payload.get("candidate")
    checks.append(
        _check(
            "candidate_identity_present",
            "pass" if isinstance(candidate, dict) else "blocker",
            "A handoff artifact must bind every live lane to one candidate identity.",
            ["candidate"] if isinstance(candidate, dict) else ["missing_candidate"],
        )
    )
    issued_at = payload.get("issued_at")
    checks.append(_candidate_timestamp_check(issued_at))
    return checks


def _candidate_timestamp_check(value: Any) -> dict[str, Any]:
    if not isinstance(value, str):
        return _check(
            "candidate_identity_fresh",
            "blocker",
            "A handoff artifact must record an RFC3339 issued_at timestamp no older than 24 hours.",
            ["missing_issued_at"],
        )
    try:
        issued_at = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if issued_at.tzinfo is None:
            raise ValueError("timestamp_has_no_timezone")
    except ValueError:
        return _check(
            "candidate_identity_fresh",
            "blocker",
            "A handoff artifact must record an RFC3339 issued_at timestamp no older than 24 hours.",
            [value],
        )
    fresh = datetime.now(UTC) - issued_at.astimezone(UTC) <= HANDOFF_READINESS_MAX_AGE
    return _check(
        "candidate_identity_fresh",
        "pass" if fresh else "blocker",
        "A handoff artifact must record an RFC3339 issued_at timestamp no older than 24 hours.",
        [value],
    )


def _candidate_binding_checks(
    repo_root: Path,
    source_path: Path,
    readiness_path: Path,
    payload: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    if payload is None:
        return []
    expected = build_candidate_identity(repo_root, source_path)
    observed = payload.get("candidate")
    candidate_matches = isinstance(observed, dict) and all(observed.get(key) == value for key, value in expected.items())
    checks = [
        _check(
            "candidate_identity_matches_source",
            "pass" if candidate_matches else "blocker",
            "Live handoff evidence must match the current canonical skill source and scenario set.",
            [json.dumps(observed, sort_keys=True) if isinstance(observed, dict) else "missing_candidate"],
        )
    ]
    if not candidate_matches:
        return checks

    evidence_root = readiness_path.parent.resolve(strict=False)
    for lane in payload.get("lanes", []):
        if not isinstance(lane, dict) or lane.get("status") != "pass":
            continue
        lane_id = str(lane.get("id") or "unknown")
        receipt_path = _resolve_evidence_path(repo_root, lane.get("receipt_path"))
        path_ok = receipt_path is not None and receipt_path.is_file() and not receipt_path.is_symlink()
        if path_ok:
            try:
                receipt_path.resolve(strict=True).relative_to(evidence_root)
            except ValueError:
                path_ok = False
        checks.append(
            _check(
                "lane_receipt_confined_to_handoff_bundle",
                "pass" if path_ok else "blocker",
                "Passed lane receipts must be regular files within the handoff evidence bundle.",
                [lane_id, _repo_relative(repo_root, receipt_path)] if receipt_path is not None else [lane_id],
            )
        )
        if not path_ok or receipt_path is None:
            continue
        receipt, receipt_error = _load_json_object(receipt_path)
        receipt_candidate = receipt.get("candidate") if receipt else None
        receipt_matches = receipt_error is None and isinstance(receipt_candidate, dict) and all(
            receipt_candidate.get(key) == value for key, value in expected.items()
        )
        checks.append(
            _check(
                "lane_receipt_candidate_matches_source",
                "pass" if receipt_matches else "blocker",
                "Passed lane receipts must carry the same candidate identity as their handoff artifact.",
                [lane_id],
            )
        )
    return checks


def _actual_tessl_score_path(repo_root: Path, source_path: Path, tessl_score_path: Path | None) -> Path | None:
    actual_path = tessl_score_path or default_tessl_score_path(repo_root, source_path)
    if tessl_score_path is None and not actual_path.exists():
        return None
    return actual_path


def _readiness_payload(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    return _load_json_object(path) if path.is_file() else (None, "missing_readiness_artifact")


def _load_tessl_score_receipt(path: Path | None) -> dict[str, Any] | None:
    payload, _error = _load_json_object(path) if path else (None, None)
    return _tessl_score_receipt(payload)


def _handoff_checks(
    repo_root: Path,
    readiness_path: Path,
    payload: dict[str, Any] | None,
    error: str | None,
    lane_map: dict[str, dict[str, Any]],
    tessl_score_path: Path | None,
    tessl_score_receipt: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    checks = _readiness_checks(repo_root, readiness_path, payload, error)
    checks.extend(_tessl_score_checks(repo_root, tessl_score_path))
    checks.extend(_oss_release_scenario_coverage_checks(repo_root, lane_map, tessl_score_receipt))
    return checks


def _handoff_blockers(checks: list[dict[str, Any]], lanes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [check for check in checks if check["status"] == "blocker"] + [
        blocker for lane in lanes for blocker in lane["blockers"]
    ]


def _handoff_receipt(
    repo_root: Path,
    *,
    query: str,
    skill_path: Path,
    readiness_path: Path,
    tessl_score_path: Path | None,
    tessl_score_receipt: dict[str, Any] | None,
    lanes: list[dict[str, Any]],
    checks: list[dict[str, Any]],
    blockers: list[dict[str, Any]],
) -> dict[str, Any]:
    blocked_next_gates = _blocked_next_gates(lanes, blockers)
    return {
        "schema_version": HANDOFF_READINESS_SCHEMA_VERSION,
        "schema_uri": HANDOFF_READINESS_SCHEMA_URI,
        "status": "blocked" if blockers else "preview",
        "operation": "eval_handoff_readiness_preview",
        "query": query,
        "skill_path": _repo_relative(repo_root, skill_path),
        "candidate": build_candidate_identity(repo_root, skill_path),
        "readiness_path": _repo_relative(repo_root, readiness_path),
        "tessl_score_path": _repo_relative(repo_root, tessl_score_path) if tessl_score_path else None,
        "tessl_score_summary": _tessl_score_summary(tessl_score_receipt),
        "required_lanes": list(REQUIRED_LANE_IDS),
        "required_order": list(REQUIRED_ORDER),
        "lanes": lanes,
        "quality_checks": checks,
        "blockers": blockers,
        "next_gate_allowed": not blockers and not blocked_next_gates,
        "blocked_next_gates": blocked_next_gates,
        "ready_for_live_tessl": not blockers and not blocked_next_gates,
        "required_next_actions": _next_actions(repo_root, blockers, readiness_path, lanes),
        "mutation_performed": False,
        "promotion_performed": False,
        "agent_summary": _agent_summary(blockers, query),
    }


def build_handoff_readiness_receipt(
    repo_root: Path,
    *,
    source_path: Path,
    query: str,
    readiness_path: Path | None = None,
    tessl_score_path: Path | None = None,
) -> dict[str, Any]:
    skill_path = _skill_md(source_path)
    actual_readiness_path = readiness_path or default_handoff_readiness_path(repo_root, source_path)
    actual_tessl_score_path = _actual_tessl_score_path(repo_root, source_path, tessl_score_path)
    payload, error = _readiness_payload(actual_readiness_path)
    lane_map = _lane_index(payload or {})
    lanes = [_lane_row(repo_root, lane_id, lane_map.get(lane_id)) for lane_id in REQUIRED_LANE_IDS]
    tessl_score_receipt = _load_tessl_score_receipt(actual_tessl_score_path)
    checks = _handoff_checks(repo_root, actual_readiness_path, payload, error, lane_map, actual_tessl_score_path, tessl_score_receipt)
    checks.extend(_candidate_binding_checks(repo_root, skill_path, actual_readiness_path, payload))
    blockers = _handoff_blockers(checks, lanes)
    return _handoff_receipt(
        repo_root,
        query=query,
        skill_path=skill_path,
        readiness_path=actual_readiness_path,
        tessl_score_path=actual_tessl_score_path,
        tessl_score_receipt=tessl_score_receipt,
        lanes=lanes,
        checks=checks,
        blockers=blockers,
    )


def build_tessl_dry_run_admission(
    repo_root: Path,
    *,
    source_path: Path,
    query: str,
    readiness_path: Path | None = None,
) -> dict[str, Any]:
    """Check the preconditions for a non-scoring private Tessl dry-run.

    The dry-run itself creates the final lane needed by live Tessl. It cannot
    require that evidence recursively, but it must require every prior SDK
    proof lane from the same handoff artifact.
    """
    actual_readiness_path = readiness_path or default_handoff_readiness_path(repo_root, source_path)
    payload, error = _readiness_payload(actual_readiness_path)
    lane_map = _lane_index(payload or {})
    lanes = [
        _lane_row(repo_root, lane_id, lane_map.get(lane_id))
        for lane_id in PRE_TESSL_DRY_RUN_LANE_IDS
    ]
    checks = _readiness_checks(repo_root, actual_readiness_path, payload, error)
    checks.extend(_candidate_binding_checks(repo_root, _skill_md(source_path), actual_readiness_path, payload))
    blockers = _handoff_blockers(checks, lanes)
    ready = not blockers
    return {
        "schema_version": HANDOFF_READINESS_SCHEMA_VERSION,
        "operation": "eval_tessl_dry_run_admission",
        "query": query,
        "readiness_path": _repo_relative(repo_root, actual_readiness_path),
        "required_lanes": list(PRE_TESSL_DRY_RUN_LANE_IDS),
        "lanes": lanes,
        "checks": checks,
        "blockers": blockers,
        "ready_for_tessl_dry_run": ready,
        "required_next_actions": _next_actions(repo_root, blockers, actual_readiness_path, lanes),
        "mutation_performed": False,
        "agent_summary": (
            f"Tessl dry-run admission for {query} is ready."
            if ready
            else f"Tessl dry-run admission for {query} is blocked: complete the mechanical, security, scenario/scorer, deterministic, OSS, and Tessl-local lanes first."
        ),
    }
