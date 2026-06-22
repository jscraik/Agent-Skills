from __future__ import annotations

import json
import math
import re
from typing import Any

from ask.skills_sdk.eval_ab_rubric import AB_RUBRIC_DIMENSIONS

DECISION_SCHEMA_VERSION = "skills-sdk.ab-judge-decision.v0"
ALLOWED_WINNERS = ["skill_a", "skill_b", "inconclusive"]
_DIMENSION_IDS = {dimension["id"] for dimension in AB_RUBRIC_DIMENSIONS}
_DECISION_KEYS = frozenset((
    "schema_version", "experiment_id", "dimension_scores", "normalized_score_a",
    "normalized_score_b", "winner", "confidence", "reason", "evidence_refs",
))
_DIMENSION_SCORE_KEYS = frozenset({"dimension_id", "skill_a_score", "skill_b_score", "reason", "evidence_refs"})


def _parse_judge_decision(raw_output: str, comparison_payload: dict[str, Any]) -> tuple[dict[str, Any] | None, str | None]:
    candidate = _json_candidate_text(raw_output)
    try:
        decision = json.loads(candidate, parse_constant=_reject_json_constant)
    except (ValueError, json.JSONDecodeError):
        try:
            decision = json.loads(_repair_judge_json_candidate(candidate), parse_constant=_reject_json_constant)
        except (ValueError, json.JSONDecodeError):
            return None, "judge_output_invalid_json"
    if not isinstance(decision, dict):
        return None, "judge_output_not_object"
    _derive_decision_normalized_scores(decision, comparison_payload)
    blocker = _decision_contract_blocker(decision, comparison_payload)
    if blocker:
        return None, blocker
    return decision, None


def _json_candidate_text(raw_output: str) -> str:
    stripped = raw_output.strip()
    fence = chr(96) * 3
    if stripped.startswith(fence) and stripped.endswith(fence):
        body = stripped[3:-3].strip()
        if body.lower().startswith("json"):
            body = body[4:].strip()
        return body
    return stripped


def _repair_judge_json_candidate(candidate: str) -> str:
    repaired = re.sub(
        r"\]\]\}\s*,\s*\"normalized_score_",
        r']}],"normalized_score_',
        candidate,
        count=1,
    )
    return re.sub(
        r'("reason"\s*:\s*"[^"]*")\s+("evidence_refs"\s*:)',
        r"\1,\2",
        repaired,
    )


def _derive_decision_normalized_scores(decision: dict[str, Any], comparison_payload: dict[str, Any]) -> None:
    rows = decision.get("dimension_scores")
    if not isinstance(rows, list):
        return
    if not all(isinstance(row, dict) for row in rows):
        return
    if any(row.get("dimension_id") not in _DIMENSION_IDS for row in rows):
        return
    if any(not _number_in_range(row.get(key), minimum=0, maximum=5) for row in rows for key in ("skill_a_score", "skill_b_score")):
        return
    computed_scores = _computed_normalized_scores(rows, comparison_payload)
    decision["normalized_score_a"] = computed_scores["normalized_score_a"]
    decision["normalized_score_b"] = computed_scores["normalized_score_b"]


def _decision_contract_blocker(decision: dict[str, Any], comparison_payload: dict[str, Any]) -> str | None:
    if set(decision) != _DECISION_KEYS:
        return "judge_decision_keys_invalid"
    if decision.get("schema_version") != DECISION_SCHEMA_VERSION:
        return "judge_decision_schema_mismatch"
    if decision.get("experiment_id") != comparison_payload["experiment_id"]:
        return "judge_decision_experiment_mismatch"
    scalar_blocker = _decision_scalar_blocker(decision)
    if scalar_blocker:
        return scalar_blocker
    dimension_blocker = _dimension_scores_blocker(decision.get("dimension_scores"))
    if dimension_blocker:
        return dimension_blocker
    return _decision_score_consistency_blocker(decision, comparison_payload)


def _decision_scalar_blocker(decision: dict[str, Any]) -> str | None:
    if decision.get("winner") not in ALLOWED_WINNERS:
        return "judge_decision_winner_invalid"
    if decision.get("confidence") not in {"low", "medium", "high"}:
        return "judge_decision_confidence_invalid"
    if not isinstance(decision.get("reason"), str) or not decision["reason"].strip():
        return "judge_decision_reason_missing"
    if not _evidence_refs_valid(decision.get("evidence_refs")):
        return "judge_decision_evidence_refs_invalid"
    return None


def _decision_score_consistency_blocker(decision: dict[str, Any], comparison_payload: dict[str, Any]) -> str | None:
    if not _normalized_scores_valid(decision):
        return "judge_decision_normalized_scores_invalid"
    computed_scores = _computed_normalized_scores(decision["dimension_scores"], comparison_payload)
    if not _normalized_scores_match(decision, computed_scores):
        return "judge_decision_normalized_scores_mismatch"
    if decision["winner"] != _expected_winner(computed_scores, decision, comparison_payload):
        return "judge_decision_winner_mismatch"
    return None


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON constant is not allowed: {value}")


def _normalized_scores_valid(decision: dict[str, Any]) -> bool:
    for key in ("normalized_score_a", "normalized_score_b"):
        value = decision.get(key)
        if not _number_in_range(value, minimum=0, maximum=1):
            return False
    return True


def _computed_normalized_scores(rows: list[dict[str, Any]], comparison_payload: dict[str, Any]) -> dict[str, float]:
    weights = {dimension["id"]: dimension["weight"] for dimension in comparison_payload["rubric"]["dimensions"]}
    score_a = sum(row["skill_a_score"] * weights[row["dimension_id"]] for row in rows) / 5
    score_b = sum(row["skill_b_score"] * weights[row["dimension_id"]] for row in rows) / 5
    return {"normalized_score_a": score_a, "normalized_score_b": score_b}


def _normalized_scores_match(decision: dict[str, Any], computed_scores: dict[str, float]) -> bool:
    return all(math.isclose(decision[key], computed_scores[key], rel_tol=0, abs_tol=1e-9) for key in computed_scores)


def _expected_winner(computed_scores: dict[str, float], decision: dict[str, Any], comparison_payload: dict[str, Any]) -> str:
    winner_policy = comparison_payload["rubric"]["winner_policy"]
    delta = computed_scores["normalized_score_b"] - computed_scores["normalized_score_a"]
    minimum_delta = winner_policy["minimum_normalized_delta"]
    if abs(delta) < minimum_delta:
        return winner_policy["tie_result"]
    if not _confidence_meets_minimum(decision["confidence"], winner_policy["minimum_confidence"]):
        return winner_policy["tie_result"]
    return "skill_b" if delta > 0 else "skill_a"


def _confidence_meets_minimum(value: str, minimum: str) -> bool:
    confidence_rank = {"low": 0, "medium": 1, "high": 2}
    return confidence_rank[value] >= confidence_rank[minimum]


def _dimension_scores_blocker(rows: object) -> str | None:
    if not isinstance(rows, list) or len(rows) != len(_DIMENSION_IDS):
        return "judge_dimension_scores_invalid"
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            return "judge_dimension_scores_invalid"
        if set(row) != _DIMENSION_SCORE_KEYS:
            return "judge_dimension_scores_invalid"
        dimension_id = row.get("dimension_id")
        if dimension_id not in _DIMENSION_IDS or dimension_id in seen:
            return "judge_dimension_scores_invalid"
        seen.add(dimension_id)
        if not _dimension_score_row_valid(row):
            return "judge_dimension_scores_invalid"
    return None if seen == _DIMENSION_IDS else "judge_dimension_scores_invalid"


def _dimension_score_row_valid(row: dict[str, Any]) -> bool:
    if not isinstance(row.get("reason"), str) or not row["reason"].strip():
        return False
    if not _evidence_refs_valid(row.get("evidence_refs")):
        return False
    for key in ("skill_a_score", "skill_b_score"):
        if not _number_in_range(row.get(key), minimum=0, maximum=5):
            return False
    return True


def _number_in_range(value: object, *, minimum: float, maximum: float) -> bool:
    return isinstance(value, int | float) and not isinstance(value, bool) and math.isfinite(value) and minimum <= value <= maximum


def _evidence_refs_valid(value: object) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(item, str) and item for item in value)
