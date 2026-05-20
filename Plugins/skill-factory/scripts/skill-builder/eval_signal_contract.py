#!/usr/bin/env python3
"""Shared contract for local expected-signal eval grading."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

EXPECTED_SIGNAL_REQUIRED_DIMENSIONS: Dict[str, str] = {
    "required_terms": "required term",
    "required_output_fields": "required output field",
    "required_source_reads": "required source read",
}

EXPECTED_SIGNAL_FORBIDDEN_DIMENSIONS: Dict[str, str] = {
    "forbidden_terms": "forbidden term",
    "forbidden_actions": "forbidden action",
}

EXPECTED_SIGNAL_FLOW_KEY = "flow_steps"
EXPECTED_SIGNAL_BUDGET_KEY = "min_expected_signal_score"
EXPECTED_SIGNAL_METRIC_KEY = "expected_signals"
EXPECTED_SIGNAL_COMPOSITE_KEY = "composite"
EXPECTED_SIGNAL_RISK_FACTORS_KEY = "risk_factors"
EXPECTED_SIGNAL_MISSING_KEY = "missing_signals"
EXPECTED_SIGNAL_FORBIDDEN_FOUND_KEY = "forbidden_signals_found"
EXPECTED_SIGNAL_KEYS = frozenset(
    [
        *EXPECTED_SIGNAL_REQUIRED_DIMENSIONS.keys(),
        *EXPECTED_SIGNAL_FORBIDDEN_DIMENSIONS.keys(),
        EXPECTED_SIGNAL_FLOW_KEY,
    ]
)


def expected_signal_items(raw: Dict[str, Any], key: str) -> List[str]:
    value = raw.get(key)
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"`expected_signals.{key}` must be a list when provided.")
    items: List[str] = []
    for item in value:
        text = str(item).strip()
        if text:
            items.append(text)
    return items


def parse_min_expected_signal_score(budgets: Optional[Dict[str, Any]]) -> Optional[float]:
    if not budgets:
        return None
    value = budgets.get(EXPECTED_SIGNAL_BUDGET_KEY)
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            return None
    return None
