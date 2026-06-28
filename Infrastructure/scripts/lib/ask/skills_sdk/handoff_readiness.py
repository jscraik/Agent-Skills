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


def default_tessl_score_path(repo_root: Path, source_path: Path) -> Path:
    return repo_root / ".harness" / "evidence" / "handoff" / _safe_slug(_skill_dir(source_path).name) / "tessl-score-preview.json"


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
    if "lane_receipt_semantics_valid" in blocker_ids and _lane_receipt_semantics_blocked(lanes or [], "oss-local"):
        return [_OSS_LOCAL_RECEIPT_SEMANTICS_BLOCKER_ACTION]
    if _lane_has_runtime_blocker(lanes or [], "oss-local"):
        return [_OSS_LOCAL_RUNTIME_BLOCKER_ACTION]
    return _lane_status_next_actions(blocker_ids)


_OSS_LOCAL_RUNTIME_BLOCKER_ACTION = (
    "Preserve the oss-local blocked_runtime receipt, run oss-cloud as a diagnostic continuation, "
    "and keep live Tessl blocked until oss-local is repaired or an explicit skip receipt is approved."
)

_OSS_LOCAL_RECEIPT_SEMANTICS_BLOCKER_ACTION = (
    "Repair the oss-local release-lane failures and rerun oss-local before oss-cloud; "
    "do not run live Tessl while the oss-local receipt status, profile proof, or release scenario evidence is blocked."
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
    return [
        "Run live Tessl and classify the live-lane result; return to oss-local only when "
        "the Tessl failure is evidence of a local skill regression."
    ]


def _tessl_score_receipt(payload: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(payload, dict):
        return None
    data = payload.get("data")
    if isinstance(data, dict):
        score = data.get("skills_sdk_eval_tessl_score")
        if isinstance(score, dict) and isinstance(score.get("receipt"), dict):
            return score["receipt"]
    if isinstance(payload.get("receipt"), dict):
        return payload["receipt"]
    return None


def _tessl_score_summary(receipt: dict[str, Any] | None) -> dict[str, Any] | None:
    if receipt is None:
        return None
    score_summary = _score_summary(receipt)
    feedback_loop = _feedback_loop(receipt)
    regressions = _regressions(score_summary)
    return {
        "status": receipt.get("status"),
        "blocker_class": receipt.get("blocker_class"),
        "feedback_loop_status": feedback_loop.get("status"),
        "regression_count": feedback_loop.get("regression_count") if feedback_loop.get("regression_count") is not None else len(regressions),
        "usage_percent": score_summary.get("usage_percent"),
        "baseline_percent": score_summary.get("baseline_percent"),
        "scenario_count": score_summary.get("scenario_count"),
    }


def _score_summary(receipt: dict[str, Any]) -> dict[str, Any]:
    value = receipt.get("score_summary")
    return value if isinstance(value, dict) else {}


def _feedback_loop(receipt: dict[str, Any]) -> dict[str, Any]:
    value = receipt.get("feedback_loop")
    return value if isinstance(value, dict) else {}


def _regressions(score_summary: dict[str, Any]) -> list[Any]:
    value = score_summary.get("regressions")
    return value if isinstance(value, list) else []


def _tessl_score_checks(repo_root: Path, tessl_score_path: Path | None) -> list[dict[str, Any]]:
    if tessl_score_path is None:
        return []
    payload, error = _load_json_object(tessl_score_path) if tessl_score_path.is_file() else (None, "missing_tessl_score")
    if payload is None:
        return [
            _check(
                "tessl_score_receipt_readable",
                "blocker",
                "Live handoff must consume the latest SDK Tessl score receipt when one is declared or present.",
                [_repo_relative(repo_root, tessl_score_path), error or "invalid_json"],
            )
        ]
    receipt = _tessl_score_receipt(payload)
    if receipt is None:
        return [
            _check(
                "tessl_score_receipt_readable",
                "blocker",
                "Tessl score evidence must include a skills-sdk Tessl score receipt.",
                [_repo_relative(repo_root, tessl_score_path)],
            )
        ]
    return _tessl_score_gate_checks(repo_root, tessl_score_path, receipt)


def _tessl_score_gate_checks(repo_root: Path, tessl_score_path: Path, receipt: dict[str, Any]) -> list[dict[str, Any]]:
    score_summary = _score_summary(receipt)
    feedback_loop = _feedback_loop(receipt)
    regressions = _regressions(score_summary)
    usage_percent = score_summary.get("usage_percent")
    usage_ok = isinstance(usage_percent, (int, float)) and float(usage_percent) >= 90.0
    feedback_open = feedback_loop.get("status") == "open"
    baseline_wins = bool(regressions) or int(feedback_loop.get("regression_count") or 0) > 0
    evidence = [_repo_relative(repo_root, tessl_score_path)]
    return [
        _tessl_gate_check(
            "tessl_feedback_loop_closed",
            not feedback_open,
            "Live Tessl handoff is blocked while the Tessl-to-internal feedback loop is open.",
            evidence,
            f"feedback_loop.status={feedback_loop.get('status')}",
        ),
        _tessl_gate_check(
            "tessl_baseline_wins_absent",
            not baseline_wins,
            "Live Tessl handoff is blocked when baseline beats usage on any scenario.",
            evidence,
            f"regression_count={feedback_loop.get('regression_count') or len(regressions)}",
        ),
        _tessl_gate_check(
            "tessl_usage_threshold_met",
            usage_ok,
            "Live Tessl handoff requires usage score >= 90%.",
            evidence,
            f"usage_percent={usage_percent}",
        ),
    ]


def _tessl_gate_check(check_id: str, ok: bool, message: str, evidence: list[str], failure_evidence: str) -> dict[str, Any]:
    return _check(check_id, "pass" if ok else "blocker", message, evidence if ok else evidence + [failure_evidence])


def _oss_release_scenario_coverage_checks(
    repo_root: Path,
    lane_map: dict[str, dict[str, Any]],
    tessl_score_receipt: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    if tessl_score_receipt is None:
        return []
    score_summary = _score_summary(tessl_score_receipt)
    expected_count = score_summary.get("scenario_count")
    if not isinstance(expected_count, int) or expected_count <= 0:
        return []
    return [
        _oss_lane_release_scenario_check(repo_root, lane_id, lane_map.get(lane_id) or {}, expected_count)
        for lane_id in ("oss-local", "oss-cloud")
    ]


def _oss_lane_release_scenario_check(repo_root: Path, lane_id: str, lane: dict[str, Any], expected_count: int) -> dict[str, Any]:
    receipt_path = _resolve_evidence_path(repo_root, lane.get("receipt_path"))
    payload, error = _load_json_object(receipt_path) if receipt_path and receipt_path.is_file() else (None, "missing_oss_receipt")
    observed_count = _receipt_case_count(payload) if payload is not None else None
    return _check(
        f"{lane_id}_release_scenario_count_matches_tessl",
        "pass" if observed_count == expected_count else "blocker",
        "OSS release proof must run the same scenario count as the final Tessl assessment before live handoff.",
        _oss_release_scenario_evidence(repo_root, receipt_path, error, expected_count, observed_count),
    )


def _oss_release_scenario_evidence(
    repo_root: Path,
    receipt_path: Path | None,
    error: str | None,
    expected_count: int,
    observed_count: int | None,
) -> list[str]:
    evidence_path = _repo_relative(repo_root, receipt_path) if receipt_path is not None else error or "missing_oss_receipt"
    return [f"expected:{expected_count}", f"observed:{observed_count if observed_count is not None else 'missing'}", evidence_path]


def _lane_has_runtime_blocker(lanes: list[dict[str, Any]], lane_id: str) -> bool:
    for lane in lanes:
        if lane.get("id") != lane_id:
            continue
        blocker = lane.get("blocker")
        return isinstance(blocker, str) and "blocked_runtime" in blocker
    return False


def _lane_receipt_semantics_blocked(lanes: list[dict[str, Any]], lane_id: str) -> bool:
    for lane in lanes:
        if lane.get("id") != lane_id:
            continue
        blockers = lane.get("blockers")
        if not isinstance(blockers, list):
            return False
        return any(isinstance(blocker, dict) and blocker.get("id") == "lane_receipt_semantics_valid" for blocker in blockers)
    return False


def _lane_effective_status(lanes: list[dict[str, Any]], lane_id: str) -> str | None:
    for lane in lanes:
        if lane.get("id") == lane_id:
            status = lane.get("status")
            return status if isinstance(status, str) else None
    return None


def _blocked_next_gates(lanes: list[dict[str, Any]], blockers: list[dict[str, Any]]) -> list[str]:
    oss_local_status = _lane_effective_status(lanes, "oss-local")
    if oss_local_status != "pass" or _lane_receipt_semantics_blocked(lanes, "oss-local"):
        return ["oss-cloud", "tessl-dry-run", "tessl-live"]

    oss_cloud_status = _lane_effective_status(lanes, "oss-cloud")
    if oss_cloud_status != "pass":
        return ["tessl-dry-run", "tessl-live"]

    tessl_dry_run_status = _lane_effective_status(lanes, "tessl-live-dry-run")
    if tessl_dry_run_status != "pass" or blockers:
        return ["tessl-live"]

    return []


def _agent_summary(blockers: list[dict[str, Any]], query: str) -> str:
    if blockers:
        return f"Handoff readiness for {query} is blocked: live Tessl requires current deterministic, oss-local, oss-cloud, and Tessl dry-run evidence."
    return f"Handoff readiness for {query} is complete for live Tessl."


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
