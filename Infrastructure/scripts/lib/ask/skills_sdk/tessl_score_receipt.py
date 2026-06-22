from __future__ import annotations

import json
from pathlib import Path
from typing import Any


TESSL_SCORE_RECEIPT_SCHEMA_VERSION = "skills-sdk.tessl-score-receipt.v0"
TESSL_SCORE_RECEIPT_SCHEMA_URI = "https://jscraik.local/agent-skills/schemas/skills-sdk/tessl-score-receipt.v0.schema.json"
TESSL_LIVE_HANDOFF_MIN_USAGE_PERCENT = 90.0


def _repo_relative(repo_root: Path, path: Path) -> str:
    try:
        return path.resolve(strict=False).relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _load_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, str(exc)
    if not isinstance(loaded, dict):
        return None, "json_root_not_object"
    return loaded, None


def _attributes(payload: dict[str, Any]) -> dict[str, Any]:
    data = payload.get("data")
    attributes = data.get("attributes") if isinstance(data, dict) else None
    return attributes if isinstance(attributes, dict) else {}


def _score_solution(solution: dict[str, Any]) -> tuple[float, float] | None:
    results = solution.get("assessmentResults")
    if not isinstance(results, list) or not results:
        return None
    score = 0.0
    max_score = 0.0
    for result in results:
        if not isinstance(result, dict):
            continue
        score += float(result.get("score") or 0)
        max_score += float(result.get("max_score") or result.get("maxScore") or 0)
    return score, max_score


def _run_id(payload: dict[str, Any], fallback: str | None) -> str:
    data = payload.get("data")
    if isinstance(data, dict):
        value = data.get("id") or data.get("evalRunId") or data.get("runId")
        if isinstance(value, str) and value.strip():
            return value.strip()
    return (fallback or "").strip()


def _score_summary(payload: dict[str, Any]) -> dict[str, Any]:
    attrs = _attributes(payload)
    scenarios = attrs.get("scenarios")
    if not isinstance(scenarios, list):
        return _empty_score_summary()
    totals, scored, missing = _score_scenarios(scenarios)
    return _score_summary_from_parts(scenarios, totals, scored, missing)


def _empty_score_summary() -> dict[str, Any]:
    return {
        "scenario_count": 0,
        "scored_scenario_count": 0,
        "missing_scenario_count": 0,
        "usage_points": 0.0,
        "baseline_points": 0.0,
        "max_points": 0.0,
        "usage_percent": None,
        "baseline_percent": None,
        "lift_points": None,
        "missing": [{"reason": "missing_scenarios"}],
        "regressions": [],
        "ties": [],
    }


def _score_scenarios(scenarios: list[Any]) -> tuple[dict[str, float], list[dict[str, Any]], list[dict[str, Any]]]:
    totals = {"usage_points": 0.0, "baseline_points": 0.0, "max_points": 0.0}
    scored: list[dict[str, Any]] = []
    missing: list[dict[str, Any]] = []
    for scenario in scenarios:
        score, missing_item = _score_scenario(scenario)
        if missing_item is not None:
            missing.append(missing_item)
            continue
        if score is None:
            continue
        scored.append(score)
        totals["usage_points"] += score["usage_score"]
        totals["baseline_points"] += score["baseline_score"]
        totals["max_points"] += score["max_score"]
    return totals, scored, missing


def _score_scenario(scenario: object) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    if not isinstance(scenario, dict):
        return None, None
    path = str(scenario.get("path") or scenario.get("id") or "unknown")
    by_variant, missing_item = _scenario_variants(scenario, path)
    if missing_item is not None:
        return None, missing_item
    usage_score = _score_solution(by_variant["usage-spec"])
    baseline_score = _score_solution(by_variant["baseline"])
    if usage_score is None or baseline_score is None:
        return None, {
            "path": path,
            "reason": "missing_assessment_results",
            "usage_has": usage_score is not None,
            "baseline_has": baseline_score is not None,
        }
    scenario_max = usage_score[1] or baseline_score[1]
    return {"path": path, "usage_score": usage_score[0], "baseline_score": baseline_score[0], "max_score": scenario_max}, None


def _scenario_variants(scenario: dict[str, Any], path: str) -> tuple[dict[str, dict[str, Any]], dict[str, Any] | None]:
    solutions = scenario.get("solutions")
    if not isinstance(solutions, list):
        return {}, {"path": path, "reason": "missing_solutions"}
    by_variant = {solution.get("variant"): solution for solution in solutions if isinstance(solution, dict)}
    usage = by_variant.get("usage-spec")
    baseline = by_variant.get("baseline")
    if not isinstance(usage, dict) or not isinstance(baseline, dict):
        return {}, {"path": path, "reason": "missing_variant", "variants": sorted(str(key) for key in by_variant)}
    return {"usage-spec": usage, "baseline": baseline}, None


def _score_summary_from_parts(
    scenarios: list[Any],
    totals: dict[str, float],
    scored: list[dict[str, Any]],
    missing: list[dict[str, Any]],
) -> dict[str, Any]:
    max_points = totals["max_points"]
    return {
        "scenario_count": len(scenarios),
        "scored_scenario_count": len(scored),
        "missing_scenario_count": len(missing),
        "usage_points": totals["usage_points"],
        "baseline_points": totals["baseline_points"],
        "max_points": totals["max_points"],
        "usage_percent": _percent(totals["usage_points"], max_points),
        "baseline_percent": _percent(totals["baseline_points"], max_points),
        "lift_points": _lift_percent(totals, max_points),
        "missing": missing,
        "regressions": [item for item in scored if item["usage_score"] < item["baseline_score"]],
        "ties": [item["path"] for item in scored if item["usage_score"] == item["baseline_score"]],
    }


def _percent(points: float, max_points: float) -> float | None:
    return None if max_points <= 0 else round((points / max_points) * 100, 4)


def _lift_percent(totals: dict[str, float], max_points: float) -> float | None:
    if max_points <= 0:
        return None
    return round(((totals["usage_points"] - totals["baseline_points"]) / max_points) * 100, 4)


def build_tessl_score_receipt(
    repo_root: Path,
    *,
    view_json: Path,
    skill: str,
    run_id: str | None = None,
) -> dict[str, Any]:
    payload, load_error = _load_json(view_json)
    if payload is None:
        return _blocked_load_receipt(repo_root, view_json, skill, run_id, load_error)
    attrs = _attributes(payload)
    score_summary = _score_summary(payload)
    feedback_loop = _feedback_loop(score_summary)
    status = str(attrs.get("status") or "unknown").strip().lower()
    failure_reason = attrs.get("failureReason") if isinstance(attrs.get("failureReason"), dict) else None
    receipt_status, blocker_class, blocker = _receipt_status(status, failure_reason, score_summary)
    ready = receipt_status == "pass"
    return {
        "schema_version": TESSL_SCORE_RECEIPT_SCHEMA_VERSION,
        "schema_uri": TESSL_SCORE_RECEIPT_SCHEMA_URI,
        "status": receipt_status,
        "blocker_class": blocker_class,
        "blocker": blocker,
        "skill": skill,
        "run_id": _run_id(payload, run_id),
        "view_json": _repo_relative(repo_root, view_json),
        "tessl_status": status,
        "failure_reason": failure_reason,
        "memory_derived": False,
        "ready": ready,
        "score_summary": score_summary,
        "readiness_thresholds": _readiness_thresholds(),
        "feedback_loop": feedback_loop,
        "mutation_performed": False,
        "agent_summary": _agent_summary(ready, blocker),
    }


def _blocked_load_receipt(
    repo_root: Path,
    view_json: Path,
    skill: str,
    run_id: str | None,
    load_error: str | None,
) -> dict[str, Any]:
    return {
        "schema_version": TESSL_SCORE_RECEIPT_SCHEMA_VERSION,
        "schema_uri": TESSL_SCORE_RECEIPT_SCHEMA_URI,
        "status": "blocked",
        "blocker_class": "blocked_missing_artifact",
        "blocker": f"Tessl view artifact could not be loaded: {load_error}",
        "skill": skill,
        "run_id": run_id or "",
        "view_json": _repo_relative(repo_root, view_json),
        "memory_derived": False,
        "ready": False,
        "score_summary": None,
        "readiness_thresholds": _readiness_thresholds(),
        "feedback_loop": {
            "status": "blocked",
            "required_next_actions": [
                "Preserve a valid tessl eval view --json artifact before scoring.",
            ],
        },
        "mutation_performed": False,
    }


def _readiness_thresholds() -> dict[str, Any]:
    return {
        "live_handoff_min_usage_percent": TESSL_LIVE_HANDOFF_MIN_USAGE_PERCENT,
        "usage_must_beat_baseline": True,
        "baseline_scenario_wins_allowed": 0,
    }


def _agent_summary(ready: bool, blocker: str | None) -> str:
    if ready:
        return "Tessl score receipt has closed the live-to-internal feedback loop for this run."
    return _blocked_agent_summary(blocker)


def _receipt_status(
    tessl_status: str,
    failure_reason: dict[str, Any] | None,
    score_summary: dict[str, Any],
) -> tuple[str, str | None, str | None]:
    blocker = _receipt_blocker(tessl_status, failure_reason, score_summary)
    if blocker is not None:
        return "blocked", "blocked_validation", blocker
    return "pass", None, None


def _receipt_blocker(
    tessl_status: str,
    failure_reason: dict[str, Any] | None,
    score_summary: dict[str, Any],
) -> str | None:
    if tessl_status in {"failed", "error", "cancelled", "canceled"}:
        return _failure_blocker(tessl_status, failure_reason)
    if score_summary["scenario_count"] > 0 and score_summary["max_points"] <= 0:
        return "Tessl eval view does not contain positive max points for scored scenarios."
    complete = score_summary["scenario_count"] > 0 and score_summary["missing_scenario_count"] == 0
    if not complete:
        return "Tessl eval view does not contain complete scored baseline and usage-spec assessments."
    if score_summary["regressions"]:
        return _regression_blocker(score_summary["regressions"])
    return _handoff_blocker(score_summary)


def _regression_blocker(regressions: list[dict[str, Any]]) -> str:
    regression_paths = ", ".join(str(item["path"]) for item in regressions[:5])
    suffix = "" if len(regressions) <= 5 else f" and {len(regressions) - 5} more"
    return (
        "Tessl feedback loop is open: baseline beat usage-spec on "
        f"{len(regressions)} scenario(s): {regression_paths}{suffix}. "
        "Import or retain equivalent internal regression cases, fix the owner, and rerun before live handoff."
    )


def _handoff_blocker(score_summary: dict[str, Any]) -> str | None:
    usage_percent = score_summary["usage_percent"]
    if usage_percent is None or usage_percent < TESSL_LIVE_HANDOFF_MIN_USAGE_PERCENT:
        return _usage_threshold_blocker(usage_percent)
    lift_points = score_summary["lift_points"]
    if lift_points is None or lift_points <= 0:
        return "Tessl usage-spec did not beat baseline in aggregate; the skill is not providing measurable lift."
    return None


def _usage_threshold_blocker(usage_percent: float | None) -> str:
    return (
        "Tessl usage score is below the live handoff threshold: "
        f"{usage_percent}% < {TESSL_LIVE_HANDOFF_MIN_USAGE_PERCENT}%. "
        "Strengthen the skill or scenario owner path internally before another handoff."
    )


def _failure_blocker(tessl_status: str, failure_reason: dict[str, Any] | None) -> str:
    code = failure_reason.get("code") if isinstance(failure_reason, dict) else tessl_status
    message = (
        failure_reason.get("message")
        if isinstance(failure_reason, dict)
        else "Tessl run did not complete successfully."
    )
    return f"Tessl eval view status is {tessl_status}: {code}: {message}"


def _feedback_loop(score_summary: dict[str, Any]) -> dict[str, Any]:
    regressions = score_summary.get("regressions")
    regression_paths = [
        str(item.get("path"))
        for item in regressions
        if isinstance(item, dict) and item.get("path")
    ] if isinstance(regressions, list) else []
    usage_percent = score_summary.get("usage_percent")
    lift_points = score_summary.get("lift_points")
    missing_count = int(score_summary.get("missing_scenario_count") or 0)
    required_next_actions: list[str] = []
    if missing_count:
        required_next_actions.append("Rerun or preserve a Tessl view with complete baseline and usage-spec assessments.")
    if regression_paths:
        required_next_actions.append("Import or retain equivalent internal regression cases for every baseline-win Tessl scenario.")
        required_next_actions.append("Classify each regression owner as skill, task, criteria, or scorer before rerunning live Tessl.")
    if usage_percent is None or usage_percent < TESSL_LIVE_HANDOFF_MIN_USAGE_PERCENT:
        required_next_actions.append("Raise usage-spec performance above the live handoff threshold in internal release evidence.")
    if lift_points is None or lift_points <= 0:
        required_next_actions.append("Prove usage-spec beats baseline before claiming handoff readiness.")
    return {
        "status": "closed" if not required_next_actions else "open",
        "source": "tessl_score_receipt",
        "regression_count": len(regression_paths),
        "regression_paths": regression_paths,
        "missing_scenario_count": missing_count,
        "required_next_actions": required_next_actions,
    }


def _blocked_agent_summary(blocker: str | None) -> str:
    if blocker and "feedback loop is open" in blocker:
        return "Tessl score receipt is blocked because the live-to-internal regression feedback loop is still open."
    return "Tessl score receipt is blocked; use scores only as historical evidence until the blocker is closed."
