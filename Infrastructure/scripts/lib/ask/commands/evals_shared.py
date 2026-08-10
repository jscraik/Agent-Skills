from __future__ import annotations

import datetime as dt
import json
import re
from collections.abc import Callable
from pathlib import Path


class EvalArtifactReadError(ValueError):
    """Raised when an existing JSON evidence artifact cannot be read safely."""


def _portable_command_part(part: str) -> str:
    return Path(part).name if Path(part).is_absolute() else part


def _sanitize_tessl_live_private_payload(value: object) -> object:
    if isinstance(value, dict):
        return {
            key: "<redacted-actor>"
            if key in {"createdBy", "user", "userId", "firstName", "lastName"}
            else _sanitize_tessl_live_private_payload(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_sanitize_tessl_live_private_payload(item) for item in value]
    if isinstance(value, str):
        stripped = value.strip()
        if stripped.startswith(("{", "[")):
            try:
                parsed = json.loads(stripped)
            except json.JSONDecodeError:
                parsed = None
            if isinstance(parsed, (dict, list)):
                return json.dumps(_sanitize_tessl_live_private_payload(parsed), indent=2, sort_keys=True)
        redacted = re.sub(r"/(?:Users|home)/[^\s\"',]+|/root(?:/[^\s\"',]+)?", "<user-path>", value)
        redacted = re.sub(r"(?i)\b[A-Z]:\\Users\\[^\s\"']+", "<user-path>", redacted)
        return re.sub(r"[-A-Za-z0-9._%+]+@[-A-Za-z0-9.]+\.[A-Za-z]{2,}", "<redacted-email>", redacted)
    return value


def _tessl_archive_suffix() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def _load_json_file(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise EvalArtifactReadError(f"Could not read JSON evidence artifact: {path}") from exc
    try:
        loaded = json.loads(text)
    except json.JSONDecodeError as exc:
        raise EvalArtifactReadError(f"Could not parse JSON evidence artifact: {path}") from exc
    if not isinstance(loaded, dict):
        raise EvalArtifactReadError(f"JSON evidence artifact must be an object: {path}")
    return loaded


def _tessl_live_view_inputs(payload: dict[str, object]) -> tuple[dict[str, object], list[object]]:
    data = payload.get("data")
    attributes = data.get("attributes") if isinstance(data, dict) else None
    scenarios = attributes.get("scenarios") if isinstance(attributes, dict) else None
    if not isinstance(scenarios, list):
        raise ValueError("Tessl eval view JSON did not include data.attributes.scenarios.")
    return (attributes if isinstance(attributes, dict) else {}, scenarios)


def _tessl_live_view_case_summary(
    scenario: object,
    score_solution: Callable[[dict[str, object]], tuple[float, float]],
    failed_criteria: Callable[[dict[str, object]], list[dict[str, object]]],
    missing_observable_output: Callable[[dict[str, object]], bool],
) -> dict[str, object] | None:
    if not isinstance(scenario, dict) or not isinstance(scenario.get("solutions"), list):
        return None
    solutions = scenario["solutions"]
    usage = next((item for item in solutions if isinstance(item, dict) and item.get("variant") == "usage-spec"), None)
    baseline = next((item for item in solutions if isinstance(item, dict) and item.get("variant") == "baseline"), None)
    if not isinstance(usage, dict) or not isinstance(baseline, dict):
        return None
    usage_score, max_score = score_solution(usage)
    baseline_score, baseline_max = score_solution(baseline)
    if max_score <= 0:
        max_score = baseline_max
    return _tessl_live_view_case_payload(
        scenario, usage, baseline, usage_score, baseline_score, max_score,
        failed_criteria, missing_observable_output,
    )


def _tessl_live_view_case_payload(
    scenario: dict[object, object],
    usage: dict[str, object],
    baseline: dict[str, object],
    usage_score: float,
    baseline_score: float,
    max_score: float,
    failed_criteria: Callable[[dict[str, object]], list[dict[str, object]]],
    missing_observable_output: Callable[[dict[str, object]], bool],
) -> dict[str, object]:
    return {
        "id": scenario.get("id"), "path": scenario.get("path"), "description": scenario.get("shortDescription"),
        "usage_score": usage_score, "baseline_score": baseline_score, "max_score": max_score,
        "regression": usage_score < baseline_score,
        "usage_failed_criteria": failed_criteria(usage), "baseline_failed_criteria": failed_criteria(baseline),
        "usage_missing_observable_output": missing_observable_output(usage),
        "baseline_missing_observable_output": missing_observable_output(baseline),
    }


def _tessl_live_view_score_totals(summaries: list[dict[str, object]]) -> tuple[float, float, float]:
    usage = sum(float(summary["usage_score"]) for summary in summaries)
    baseline = sum(float(summary["baseline_score"]) for summary in summaries)
    maximum = sum(float(summary["max_score"]) for summary in summaries)
    if maximum <= 0:
        raise ValueError("Tessl eval view JSON did not include scored baseline and usage-spec solutions.")
    return usage, baseline, maximum


def _tessl_live_view_comparisons(summaries: list[dict[str, object]]) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    regressions = [summary for summary in summaries if summary.get("regression")]
    shape_regressions = [
        summary for summary in regressions
        if summary.get("usage_missing_observable_output") and not summary.get("baseline_missing_observable_output")
    ]
    ties = [summary for summary in summaries if summary.get("usage_score") == summary.get("baseline_score")]
    return regressions, shape_regressions, ties


def _tessl_live_view_metrics(attributes: dict[str, object], collect_metrics: Callable[..., dict[str, object]]) -> dict[str, dict[str, object]]:
    return {
        "turn": collect_metrics(attributes, tokens=("turn",)),
        "token": collect_metrics(attributes, tokens=("token",)),
        "cost": collect_metrics(attributes, tokens=("cost", "price", "spend")),
    }


def _tessl_live_view_result(
    attributes: dict[str, object], summaries: list[dict[str, object]], totals: tuple[float, float, float],
    comparisons: tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]],
    metrics: dict[str, dict[str, object]], minimum_score: float, target_score: float,
) -> dict[str, object]:
    usage, baseline, maximum = totals
    regressions, shape_regressions, ties = comparisons
    usage_rate, baseline_rate = usage / maximum, baseline / maximum
    improvement = None if baseline_rate == 0 else usage_rate / baseline_rate
    return _tessl_live_view_payload(
        attributes, summaries, metrics, usage, baseline, maximum, usage_rate, baseline_rate, improvement,
        regressions, shape_regressions, ties, minimum_score, target_score,
    )


def _tessl_live_view_payload(
    attributes: dict[str, object], summaries: list[dict[str, object]], metrics: dict[str, dict[str, object]],
    usage: float, baseline: float, maximum: float, usage_rate: float, baseline_rate: float, improvement: float | None,
    regressions: list[dict[str, object]], shape_regressions: list[dict[str, object]], ties: list[dict[str, object]],
    minimum_score: float, target_score: float,
) -> dict[str, object]:
    return {
        "score": usage_rate, "baseline_score": baseline_rate, "improvement": improvement,
        "comparative_quality": {"with_skill_score": usage_rate, "without_skill_score": baseline_rate, "improvement": improvement, "beats_baseline": usage_rate > baseline_rate, "baseline_ties_count": len(ties), "regressions_count": len(regressions)},
        "model_selection": {"agent": attributes.get("agent"), "model": attributes.get("model"), "scorer_agent": attributes.get("scorerAgent") or attributes.get("scorer_agent"), "scorer_model": attributes.get("scorerModel") or attributes.get("scorer_model"), "quality_floor_before_cost": True, "cost_is_secondary_to_score": True},
        "cost_observability": {"turn_metrics_available": bool(metrics["turn"]), "token_metrics_available": bool(metrics["token"]), "cost_metrics_available": bool(metrics["cost"]), "turn_metrics": metrics["turn"], "token_metrics": metrics["token"], "cost_metrics": metrics["cost"]},
        "usage_points": usage, "baseline_points": baseline, "max_points": maximum, "scenarios_count": len(summaries),
        "regressions_count": len(regressions), "regressions": regressions, "evidence_shape_regressions_count": len(shape_regressions),
        "evidence_shape_regressions": shape_regressions, "baseline_ties_count": len(ties), "baseline_ties": ties,
        "min_score_required": minimum_score, "target_score": target_score, "meets_min_score": usage_rate >= minimum_score,
        "beats_baseline": usage_rate > baseline_rate,
    }


def _summarize_tessl_live_eval_view(
    payload: dict[str, object], *, score_solution: Callable[[dict[str, object]], tuple[float, float]],
    failed_criteria: Callable[[dict[str, object]], list[dict[str, object]]], missing_observable_output: Callable[[dict[str, object]], bool],
    collect_metrics: Callable[..., dict[str, object]], minimum_score: float, target_score: float,
) -> dict[str, object]:
    attributes, scenarios = _tessl_live_view_inputs(payload)
    summaries = [summary for scenario in scenarios if (summary := _tessl_live_view_case_summary(scenario, score_solution, failed_criteria, missing_observable_output))]
    return _tessl_live_view_result(
        attributes, summaries, _tessl_live_view_score_totals(summaries), _tessl_live_view_comparisons(summaries),
        _tessl_live_view_metrics(attributes, collect_metrics), minimum_score, target_score,
    )
