from __future__ import annotations

from typing import Any


SEMANTIC_ACCEPTANCE_TYPES = {
    "discovery_question",
    "expected_signal",
    "text_field_equals",
    "text_field_in",
    "text_field_present",
}


def release_rubric_regex_checks(acceptance: list[Any], scenario_id: str) -> list[dict[str, Any]]:
    positive_regex_items = _acceptance_items_of_type(acceptance, scenario_id, {"regex"})
    semantic_items = _acceptance_items_of_type(acceptance, scenario_id, SEMANTIC_ACCEPTANCE_TYPES)
    needs_semantic_coverage = len(positive_regex_items) > 1
    return [
        {
            "id": "release_rubric_regex_not_primary",
            "status": "blocker" if len(positive_regex_items) > 1 else "pass",
            "severity": "blocker",
            "message": "Release rubrics must not use multiple positive regex checks as primary scoring; use behavioral expected_signal or typed assertions.",
            "evidence": positive_regex_items[1:],
        },
        {
            "id": "release_rubric_semantic_coverage",
            "status": "pass" if not needs_semantic_coverage or len(semantic_items) >= 2 else "blocker",
            "severity": "blocker",
            "message": "Release rubrics must include at least two semantic or typed checks so wording variation does not dominate Tessl impact.",
            "evidence": [f"{scenario_id}:semantic_acceptance_count:{len(semantic_items)}"] if len(semantic_items) < 2 else [],
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
