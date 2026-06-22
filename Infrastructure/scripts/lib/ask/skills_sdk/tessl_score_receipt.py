from __future__ import annotations

import json
from pathlib import Path
from typing import Any


TESSL_SCORE_RECEIPT_SCHEMA_VERSION = "skills-sdk.tessl-score-receipt.v0"
TESSL_SCORE_RECEIPT_SCHEMA_URI = "https://jscraik.local/agent-skills/schemas/skills-sdk/tessl-score-receipt.v0.schema.json"


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
    status = str(attrs.get("status") or "unknown").strip().lower()
    failure_reason = attrs.get("failureReason") if isinstance(attrs.get("failureReason"), dict) else None
    receipt_status, blocker_class, blocker = _receipt_status(status, failure_reason, score_summary)
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
        "ready": receipt_status == "pass",
        "score_summary": score_summary,
        "mutation_performed": False,
        "agent_summary": (
            "Tessl score receipt is blocked; use partial scores only as historical evidence."
            if receipt_status == "blocked"
            else "Tessl score receipt has complete scored baseline and usage-spec evidence."
        ),
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
        "mutation_performed": False,
    }


def _receipt_status(
    tessl_status: str,
    failure_reason: dict[str, Any] | None,
    score_summary: dict[str, Any],
) -> tuple[str, str | None, str | None]:
    if tessl_status in {"failed", "error", "cancelled", "canceled"}:
        return "blocked", "blocked_validation", _failure_blocker(tessl_status, failure_reason)
    if score_summary["scenario_count"] > 0 and score_summary["max_points"] <= 0:
        return "blocked", "blocked_validation", "Tessl eval view does not contain positive max points for scored scenarios."
    complete = score_summary["scenario_count"] > 0 and score_summary["missing_scenario_count"] == 0
    if complete:
        return "pass", None, None
    return "blocked", "blocked_validation", "Tessl eval view does not contain complete scored baseline and usage-spec assessments."


def _failure_blocker(tessl_status: str, failure_reason: dict[str, Any] | None) -> str:
    code = failure_reason.get("code") if isinstance(failure_reason, dict) else tessl_status
    message = (
        failure_reason.get("message")
        if isinstance(failure_reason, dict)
        else "Tessl run did not complete successfully."
    )
    return f"Tessl eval view status is {tessl_status}: {code}: {message}"
