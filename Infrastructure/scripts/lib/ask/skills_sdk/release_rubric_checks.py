from __future__ import annotations

from typing import Any


SEMANTIC_ACCEPTANCE_TYPES = {
    "discovery_question",
    "expected_signal",
    "text_field_equals",
    "text_field_in",
    "text_field_present",
}
BEHAVIOR_VERBS = {
    "asks",
    "avoids",
    "blocks",
    "cites",
    "classifies",
    "compares",
    "distinguishes",
    "explains",
    "identifies",
    "includes",
    "maps",
    "names",
    "preserves",
    "records",
    "refuses",
    "reports",
    "returns",
    "separates",
    "states",
    "uses",
}


NEGATED_BOUNDARY_PRONE_PHRASES = {
    "ci passed",
    "commands were executed",
    "hosted ci passed",
    "remote checks passed",
    "validation passed",
}


def release_rubric_regex_checks(acceptance: list[Any], scenario_id: str) -> list[dict[str, Any]]:
    positive_regex_items = _acceptance_items_of_type(acceptance, scenario_id, {"regex"})
    semantic_items = _acceptance_items_of_type(acceptance, scenario_id, SEMANTIC_ACCEPTANCE_TYPES)
    brittle_negative_items = _negated_boundary_prone_items(acceptance, scenario_id)
    keyword_list_items = _keyword_list_expected_signal_items(acceptance, scenario_id)
    return [
        {
            "id": "release_rubric_regex_not_primary",
            "status": "blocker" if positive_regex_items else "pass",
            "severity": "blocker",
            "message": "Release rubrics must not use positive regex checks as scorer-facing proof; use behavioral expected_signal or typed assertions.",
            "evidence": positive_regex_items,
        },
        {
            "id": "release_rubric_semantic_coverage",
            "status": "pass" if len(semantic_items) >= 2 else "blocker",
            "severity": "blocker",
            "message": "Release rubrics must include at least two semantic or typed checks so wording variation does not dominate Tessl impact.",
            "evidence": [f"{scenario_id}:semantic_acceptance_count:{len(semantic_items)}"] if len(semantic_items) < 2 else [],
        },
        {
            "id": "release_rubric_negated_boundary_safe",
            "status": "blocker" if brittle_negative_items else "pass",
            "severity": "blocker",
            "message": "Release rubrics must not use phrase-only negative checks for readiness boundary claims because negated safe statements can contain the same phrase.",
            "evidence": brittle_negative_items,
        },
        {
            "id": "release_rubric_expected_signal_behavioral_sentence",
            "status": "blocker" if keyword_list_items else "pass",
            "severity": "blocker",
            "message": "Release expected_signal checks must describe observable behavior, not comma-separated keyword lists that overfit house phrasing.",
            "evidence": keyword_list_items,
        },
    ]


def _acceptance_items_of_type(acceptance: list[Any], scenario_id: str, accepted_types: set[str]) -> list[str]:
    return [
        f"{scenario_id}:acceptance[{index}]"
        for index, item in enumerate(acceptance, start=1)
        if isinstance(item, dict)
        and str(item.get("type") or "").strip().lower()
        in accepted_types
    ]


def _negated_boundary_prone_items(acceptance: list[Any], scenario_id: str) -> list[str]:
    evidence: list[str] = []
    for index, item in enumerate(acceptance, start=1):
        if not isinstance(item, dict):
            continue
        item_type = str(item.get("type") or "").strip().lower()
        if item_type != "not_contains":
            continue
        value = str(item.get("value") or "").replace("\\ ", " ").lower()
        if "encourages or permits this failure mode" in value:
            continue
        if any(phrase in value for phrase in NEGATED_BOUNDARY_PRONE_PHRASES):
            evidence.append(f"{scenario_id}:acceptance[{index}]")
    return evidence


def _keyword_list_expected_signal_items(acceptance: list[Any], scenario_id: str) -> list[str]:
    evidence: list[str] = []
    for index, item in enumerate(acceptance, start=1):
        if not isinstance(item, dict):
            continue
        item_type = str(item.get("type") or "").strip().lower()
        if item_type != "expected_signal":
            continue
        value = str(item.get("value") or "").strip()
        words = [word for word in value.replace(".", " ").replace(",", " ").split() if word]
        if (value.count(",") >= 2 and len(words) <= 8) or _looks_like_keyword_fragment(value, words):
            evidence.append(f"{scenario_id}:acceptance[{index}]")
    return evidence


def _looks_like_keyword_fragment(value: str, words: list[str]) -> bool:
    if not 2 <= len(words) <= 8:
        return False
    if any(separator in value for separator in [",", ";", ":", ".", "?", "!"]):
        return False
    normalized_words = [word.strip("()[]{}").lower() for word in words]
    if any(word in BEHAVIOR_VERBS for word in normalized_words):
        return False
    return value[:1].islower()
