"""Tessl and release-lane decisions for Skills SDK handoff readiness.

This module owns receipt reuse checks and next-stage routing.  The parent
handoff module owns source identity and lane receipt validation.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ask.skills_sdk.tessl_acceptance_policy import TESSL_ACCEPTANCE_SCORE


_OSS_LOCAL_RUNTIME_BLOCKER_ACTION = (
    "Preserve the oss-local blocked_runtime receipt, run oss-cloud as a diagnostic continuation, "
    "and keep live Tessl blocked until oss-local is repaired or an explicit skip receipt is approved."
)

_OSS_LOCAL_RECEIPT_SEMANTICS_BLOCKER_ACTION = (
    "Repair the oss-local release-lane failures and rerun oss-local before oss-cloud; "
    "do not run live Tessl while the oss-local receipt status, profile proof, or release scenario evidence is blocked."
)


def next_actions(
    repo_root: Path,
    blockers: list[dict[str, Any]],
    readiness_path: Path,
    lanes: list[dict[str, Any]] | None = None,
) -> list[str]:
    blocker_ids = {str(blocker["id"]) for blocker in blockers}
    if "readiness_artifact_present" in blocker_ids:
        path = _repo_relative(repo_root, readiness_path)
        return [f"Create {path} with deterministic, oss-local, oss-cloud, and Tessl dry-run lane receipts."]
    command_actions = _lane_command_next_actions(blocker_ids)
    if command_actions:
        return command_actions
    if _tessl_score_blocked(blocker_ids):
        return [_TESSL_SCORE_REPAIR_ACTION]
    if _oss_local_semantics_blocked(blocker_ids, lanes or []):
        return [_OSS_LOCAL_RECEIPT_SEMANTICS_BLOCKER_ACTION]
    if _lane_has_runtime_blocker(lanes or [], "oss-local"):
        return [_OSS_LOCAL_RUNTIME_BLOCKER_ACTION]
    return _lane_status_next_actions(blocker_ids)


_TESSL_SCORE_REPAIR_ACTION = (
    "Repair the Tessl score feedback loop by classifying baseline wins, low usage, or incomplete score "
    "evidence in the internal SDK lanes; rerun the Tessl score receipt before any live Tessl run."
)


def _tessl_score_blocked(blocker_ids: set[str]) -> bool:
    return not blocker_ids.isdisjoint(
        {
            "tessl_score_receipt_complete",
            "tessl_feedback_loop_closed",
            "tessl_baseline_wins_absent",
            "tessl_usage_threshold_met",
        }
    )


def _oss_local_semantics_blocked(blocker_ids: set[str], lanes: list[dict[str, Any]]) -> bool:
    return "lane_receipt_semantics_valid" in blocker_ids and _lane_receipt_semantics_blocked(lanes, "oss-local")


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


def tessl_score_receipt(payload: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(payload, dict):
        return None
    if payload.get("schema_version") == "skills-sdk.tessl-score-receipt.v0":
        return payload
    if isinstance(payload.get("score_summary"), dict) and isinstance(payload.get("feedback_loop"), dict):
        return payload
    data = payload.get("data")
    if isinstance(data, dict):
        score = data.get("skills_sdk_eval_tessl_score")
        if isinstance(score, dict) and isinstance(score.get("receipt"), dict):
            return score["receipt"]
    receipt = payload.get("receipt")
    return receipt if isinstance(receipt, dict) else None


def tessl_score_summary(receipt: dict[str, Any] | None) -> dict[str, Any] | None:
    if receipt is None:
        return None
    score_summary = _score_summary(receipt)
    feedback_loop = _feedback_loop(receipt)
    regressions = _regressions(score_summary)
    regression_count = feedback_loop.get("regression_count")
    return {
        "status": receipt.get("status"),
        "blocker_class": receipt.get("blocker_class"),
        "feedback_loop_status": feedback_loop.get("status"),
        "regression_count": regression_count if regression_count is not None else len(regressions),
        "usage_percent": score_summary.get("usage_percent"),
        "baseline_percent": score_summary.get("baseline_percent"),
        "scenario_count": score_summary.get("scenario_count"),
    }


def tessl_score_checks(repo_root: Path, tessl_score_path: Path | None) -> list[dict[str, Any]]:
    if tessl_score_path is None:
        return []
    payload, error = _read_tessl_score_payload(tessl_score_path)
    if payload is None:
        return [_unreadable_tessl_score_check(repo_root, tessl_score_path, error)]
    receipt = tessl_score_receipt(payload)
    if receipt is None:
        return [_missing_tessl_receipt_check(repo_root, tessl_score_path)]
    return _tessl_score_gate_checks(repo_root, tessl_score_path, receipt)


def _read_tessl_score_payload(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    return _load_json_object(path) if path.is_file() else (None, "missing_tessl_score")


def _unreadable_tessl_score_check(repo_root: Path, path: Path, error: str | None) -> dict[str, Any]:
    return _check(
        "tessl_score_receipt_readable",
        "blocker",
        "Live handoff must consume the latest SDK Tessl score receipt when one is declared or present.",
        [_repo_relative(repo_root, path), error or "invalid_json"],
    )


def _missing_tessl_receipt_check(repo_root: Path, path: Path) -> dict[str, Any]:
    return _check(
        "tessl_score_receipt_readable",
        "blocker",
        "Tessl score evidence must include a skills-sdk Tessl score receipt.",
        [_repo_relative(repo_root, path)],
    )


def _tessl_score_gate_checks(
    repo_root: Path,
    tessl_score_path: Path,
    receipt: dict[str, Any],
) -> list[dict[str, Any]]:
    score_summary = _score_summary(receipt)
    feedback_loop = _feedback_loop(receipt)
    regressions = _regressions(score_summary)
    usage_percent = score_summary.get("usage_percent")
    usage_ok = isinstance(usage_percent, (int, float)) and float(usage_percent) >= TESSL_ACCEPTANCE_SCORE
    evidence = [_repo_relative(repo_root, tessl_score_path)]
    return _tessl_gate_checks(score_summary, feedback_loop, regressions, usage_percent, usage_ok, evidence)


def _tessl_gate_checks(
    score_summary: dict[str, Any],
    feedback_loop: dict[str, Any],
    regressions: list[Any],
    usage_percent: object,
    usage_ok: bool,
    evidence: list[str],
) -> list[dict[str, Any]]:
    feedback_open = feedback_loop.get("status") == "open"
    baseline_wins = bool(regressions) or int(feedback_loop.get("regression_count") or 0) > 0
    return [
        _tessl_gate_check(
            "tessl_score_receipt_complete",
            bool(feedback_loop) and _positive_scenario_count(score_summary),
            "Tessl score evidence must include feedback_loop and score_summary.scenario_count.",
            evidence,
            f"feedback_loop={bool(feedback_loop)}:scenario_count={score_summary.get('scenario_count')}",
        ),
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
            f"Live Tessl handoff requires usage score >= {TESSL_ACCEPTANCE_SCORE}%.",
            evidence,
            f"usage_percent={usage_percent}",
        ),
    ]


def _positive_scenario_count(score_summary: dict[str, Any]) -> bool:
    scenario_count = score_summary.get("scenario_count")
    return isinstance(scenario_count, int) and scenario_count > 0


def _tessl_gate_check(
    check_id: str,
    ok: bool,
    message: str,
    evidence: list[str],
    failure_evidence: str,
) -> dict[str, Any]:
    return _check(check_id, "pass" if ok else "blocker", message, evidence if ok else evidence + [failure_evidence])


def oss_release_scenario_coverage_checks(
    repo_root: Path,
    lane_map: dict[str, dict[str, Any]],
    score_receipt: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    if score_receipt is None:
        return []
    score_summary = _score_summary(score_receipt)
    return [
        _oss_lane_release_scenario_check(repo_root, lane_id, lane_map.get(lane_id) or {}, score_summary)
        for lane_id in ("oss-local", "oss-cloud")
    ]


def _oss_lane_release_scenario_check(
    repo_root: Path,
    lane_id: str,
    lane: dict[str, Any],
    score_summary: dict[str, Any],
) -> dict[str, Any]:
    receipt_path = _resolve_evidence_path(repo_root, lane.get("receipt_path"))
    payload, error = _read_oss_receipt(receipt_path)
    observed_count = _receipt_case_count(payload) if payload is not None else None
    expected_count = _oss_release_expected_count(payload, score_summary)
    return _check(
        f"{lane_id}_release_scenario_count_matches_tessl",
        "pass" if isinstance(expected_count, int) and observed_count == expected_count else "blocker",
        "OSS release proof must run the declared release-set universe before live handoff.",
        _oss_release_scenario_evidence(repo_root, receipt_path, error, expected_count, observed_count),
    )


def _read_oss_receipt(path: Path | None) -> tuple[dict[str, Any] | None, str | None]:
    if path is None or not path.is_file():
        return None, "missing_oss_receipt"
    return _load_json_object(path)


def _oss_release_expected_count(payload: dict[str, Any] | None, score_summary: dict[str, Any]) -> int | None:
    receipt = payload.get("receipt") if isinstance(payload, dict) else None
    receipt = receipt if isinstance(receipt, dict) else payload
    if not isinstance(receipt, dict):
        receipt = {}
    case_ids = receipt.get("scenario_set_case_ids")
    if isinstance(case_ids, list) and case_ids:
        return len(case_ids)
    minimum = receipt.get("release_set_minimum")
    if isinstance(minimum, int) and minimum > 0:
        return minimum
    scenario_count = score_summary.get("scenario_count")
    return scenario_count if isinstance(scenario_count, int) and scenario_count > 0 else None


def _oss_release_scenario_evidence(
    repo_root: Path,
    receipt_path: Path | None,
    error: str | None,
    expected_count: int | None,
    observed_count: int | None,
) -> list[str]:
    evidence_path = _repo_relative(repo_root, receipt_path) if receipt_path is not None else error or "missing_oss_receipt"
    observed = observed_count if observed_count is not None else "missing"
    return [f"expected:{expected_count}", f"observed:{observed}", evidence_path]


def blocked_next_gates(lanes: list[dict[str, Any]], blockers: list[dict[str, Any]]) -> list[str]:
    if _foundation_lane_blocked(lanes):
        return ["oss-local", "oss-cloud", "tessl-dry-run", "tessl-live"]
    if _oss_local_blocked(lanes):
        return ["oss-cloud", "tessl-dry-run", "tessl-live"]
    if _lane_effective_status(lanes, "oss-cloud") != "pass":
        return ["tessl-dry-run", "tessl-live"]
    if _lane_effective_status(lanes, "tessl-live-dry-run") != "pass" or blockers:
        return ["tessl-live"]
    return []


def _foundation_lane_blocked(lanes: list[dict[str, Any]]) -> bool:
    lane_ids = (
        "mechanical_validation",
        "security_risk_modes",
        "scenario_quality",
        "scorer_quality",
        "scorer_calibration",
        "deterministic_local_gates",
    )
    return any(
        _lane_effective_status(lanes, lane_id) != "pass" or _lane_receipt_semantics_blocked(lanes, lane_id)
        for lane_id in lane_ids
    )


def _oss_local_blocked(lanes: list[dict[str, Any]]) -> bool:
    return _lane_effective_status(lanes, "oss-local") != "pass" or _lane_receipt_semantics_blocked(lanes, "oss-local")


def _lane_has_runtime_blocker(lanes: list[dict[str, Any]], lane_id: str) -> bool:
    for lane in lanes:
        if lane.get("id") == lane_id:
            blocker = lane.get("blocker")
            return isinstance(blocker, str) and "blocked_runtime" in blocker
    return False


def _lane_receipt_semantics_blocked(lanes: list[dict[str, Any]], lane_id: str) -> bool:
    for lane in lanes:
        if lane.get("id") == lane_id:
            blockers = lane.get("blockers")
            return isinstance(blockers, list) and any(
                isinstance(blocker, dict) and blocker.get("id") == "lane_receipt_semantics_valid"
                for blocker in blockers
            )
    return False


def _lane_effective_status(lanes: list[dict[str, Any]], lane_id: str) -> str | None:
    for lane in lanes:
        if lane.get("id") == lane_id:
            status = lane.get("status")
            return status if isinstance(status, str) else None
    return None


def agent_summary(blockers: list[dict[str, Any]], query: str) -> str:
    if blockers:
        return (
            f"Handoff readiness for {query} is blocked: live Tessl requires current mechanical, security, "
            "scenario/scorer, deterministic, oss-local, oss-cloud, Tessl-local, and Tessl dry-run evidence."
        )
    return f"Handoff readiness for {query} is complete for live Tessl."


def _repo_relative(repo_root: Path, path: Path) -> str:
    try:
        return path.resolve(strict=False).relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


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


def _score_summary(receipt: dict[str, Any]) -> dict[str, Any]:
    value = receipt.get("score_summary")
    return value if isinstance(value, dict) else {}


def _feedback_loop(receipt: dict[str, Any]) -> dict[str, Any]:
    value = receipt.get("feedback_loop")
    return value if isinstance(value, dict) else {}


def _regressions(score_summary: dict[str, Any]) -> list[Any]:
    value = score_summary.get("regressions")
    return value if isinstance(value, list) else []


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
