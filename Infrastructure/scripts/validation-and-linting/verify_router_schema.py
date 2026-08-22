#!/usr/bin/env python3
"""Validate selection/router JSON payloads for schema and telemetry safety."""

from __future__ import annotations

import argparse
import json
import logging
import math
import sys
from pathlib import Path
from typing import Any, Dict, List


def _discover_repo_root() -> Path:
    resolved = Path(__file__).resolve()
    for candidate in resolved.parents:
        if (candidate / ".git").exists():
            return candidate
    for candidate in resolved.parents:
        if (candidate / "Infrastructure").is_dir() and (candidate / "scripts").is_dir():
            return candidate
    return resolved.parents[2]


REPO_ROOT = _discover_repo_root()
schema_lib_candidates = [
    REPO_ROOT / "plugins" / "skill-factory" / "scripts" / "skill-builder",
    REPO_ROOT / "Plugins" / "skill-factory" / "scripts" / "skill-builder",
]
for schema_lib in schema_lib_candidates:
    if schema_lib.exists() and str(schema_lib) not in sys.path:
        sys.path.insert(0, str(schema_lib))

from skill_router_schema import validate_router_result  # noqa: E402


SERVICE_ID = "router-schema-verifier"
logger = logging.getLogger(SERVICE_ID)


def load_payload(path: Path | None) -> Dict[str, Any]:
    if path is None:
        data = sys.stdin.read().strip()
    else:
        data = path.read_text(encoding="utf-8")

    if not data:
        return {}

    obj = json.loads(data)
    if not isinstance(obj, dict):
        raise ValueError("Expected JSON object payload")
    return obj


def _selection_payload_from_envelope(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract the nested selection-like payload from an envelope when present.

    If `payload` is an envelope containing a `data` mapping with a nested `decision`,
    `goal_decision` or `catalog_parity` mapping, return that nested mapping;
    otherwise return the original `payload`.

    Parameters:
        payload (Dict[str, Any]): Top-level JSON object parsed from the envelope.

    Returns:
        Dict[str, Any]: The extracted nested payload if found, otherwise the original payload.
    """
    data = payload.get("data")
    if isinstance(data, dict):
        decision = data.get("decision")
        if isinstance(decision, dict):
            return decision
        goal = data.get("goal_decision")
        if isinstance(goal, dict):
            return goal
        catalog = data.get("catalog_parity")
        if isinstance(catalog, dict):
            return catalog
    return payload


def _missing_required(payload: Dict[str, Any], required: set[str]) -> List[str]:
    """Return one stable diagnostic for absent required fields."""
    missing = sorted(required - set(payload))
    return [f"missing required fields: {', '.join(missing)}"] if missing else []


def _selection_status_issues(payload: Dict[str, Any]) -> List[str]:
    """Validate the selection status and failure-class mapping."""
    status = payload.get("decision_status")
    status_failures = {
        "resolved": None,
        "unresolved_ambiguity": "AMBIGUITY_UNRESOLVED",
        "blocked_policy_drift": "DISCOVERY_POLICY_DRIFT",
        "degraded_no_candidates": "NO_ELIGIBLE_CANDIDATES",
        "blocked_catalog_parity": "CATALOG_PARITY_DRIFT",
    }
    if not isinstance(status, str) or status not in status_failures:
        return ["invalid decision_status"]
    expected = status_failures[status]
    actual = payload.get("failure_class")
    issues = []
    if actual != expected:
        issues.append(
            "failure_class must match decision_status mapping "
            f"(status={status}, expected={expected}, actual={actual})"
        )
    if status != "resolved" and not str(payload.get("operator_action") or "").strip():
        issues.append("non-success selection decisions must include operator_action")
    return issues


def _selection_type_issues(payload: Dict[str, Any]) -> List[str]:
    """Validate selection collection and counter types."""
    issues = []
    expected_types = {
        "selected_candidates": (list, "a list"),
        "considered_candidates": (list, "a list"),
        "excluded_candidates": (list, "a list"),
        "considered_limit": (int, "an integer"),
        "considered_total": (int, "an integer"),
        "considered_truncated": (bool, "boolean"),
        "truncated_count": (int, "an integer"),
    }
    for field, (expected, label) in expected_types.items():
        value = payload.get(field)
        if expected is int and type(value) is not int:
            issues.append(f"{field} must be {label}")
        elif expected is not int and not isinstance(value, expected):
            issues.append(f"{field} must be {label}")
    return issues


def validate_selection_decision(payload: Dict[str, Any]) -> List[str]:
    """Validate one selection-decision receipt."""
    required = {
        "schema_version",
        "request_id",
        "policy_identity",
        "decision_status",
        "selected_candidates",
        "considered_candidates",
        "excluded_candidates",
        "considered_limit",
        "considered_total",
        "considered_truncated",
        "truncated_count",
    }

    return (
        _missing_required(payload, required)
        + _selection_status_issues(payload)
        + _selection_type_issues(payload)
    )


def _goal_status_issues(payload: Dict[str, Any]) -> List[str]:
    """Validate conditional goal-decision status fields."""
    status = payload.get("decision_status")
    if not isinstance(status, str) or status not in {"resolved", "intent_unresolved"}:
        return ["invalid decision_status"]
    if status == "resolved":
        issues = []
        if payload.get("failure_class") is not None:
            issues.append("resolved goal decision must set failure_class=null")
        if payload.get("operator_action") is not None:
            issues.append("resolved goal decision must set operator_action=null")
        return issues
    issues = []
    if payload.get("failure_class") != "INTENT_UNRESOLVED":
        issues.append(
            "intent_unresolved goal decision must set failure_class=INTENT_UNRESOLVED"
        )
    if not str(payload.get("operator_action") or "").strip():
        issues.append("intent_unresolved goal decision must include operator_action")
    return issues


def validate_goal_decision(payload: Dict[str, Any]) -> List[str]:
    """Validate one goal-decision receipt."""
    issues = []
    if payload.get("schema_version") != "goal-decision.v1":
        issues.append("invalid schema_version: expected 'goal-decision.v1'")
    required = {
        "schema_version",
        "policy_identity",
        "decision_status",
        "failure_class",
        "operator_action",
        "recommended_candidate",
        "alternative_candidates",
        "disambiguation_prompts",
    }
    issues.extend(_missing_required(payload, required))
    issues.extend(_goal_status_issues(payload))
    if not isinstance(payload.get("alternative_candidates"), list):
        issues.append("alternative_candidates must be a list")
    if not isinstance(payload.get("disambiguation_prompts"), list):
        issues.append("disambiguation_prompts must be a list")

    return issues


def _catalog_history_status_issues(payload: Dict[str, Any]) -> List[str]:
    """Validate catalog history state emitted by every diagnostic mode."""
    allowed = {
        "available",
        "insufficient_history",
        "not_checked",
        "not_collected",
        "schema_invalid_history",
        "trend_deterioration",
    }
    status = payload.get("history_status")
    return (
        []
        if isinstance(status, str) and status in allowed
        else ["invalid history_status"]
    )


def _catalog_blocking_state_issues(payload: Dict[str, Any]) -> List[str]:
    """Require complete blocked-state evidence for blocking history outcomes."""
    decision = payload.get("decision_status")
    status = payload.get("history_status")
    history_blocking = isinstance(status, str) and status in {
        "schema_invalid_history", "trend_deterioration"
    }
    if decision != "blocked_catalog_parity" and not history_blocking:
        return []
    issues = []
    if decision != "blocked_catalog_parity":
        issues.append("blocking history_status must block catalog parity")
    if payload.get("drift_detected") is not True:
        issues.append("blocked catalog parity must set drift_detected=true")
    for field in ("drift_class", "blocking_reason", "operator_action"):
        value = payload.get(field)
        if not isinstance(value, str) or not value.strip():
            issues.append(f"blocked catalog parity must include {field}")
    return issues


def validate_catalog_parity(payload: Dict[str, Any]) -> List[str]:
    """Validate catalog-parity schema and blocked-state semantics."""
    issues: List[str] = []
    if payload.get("schema_version") != "catalog-parity.v1":
        issues.append("invalid schema_version: expected 'catalog-parity.v1'")
    required = {
        "schema_version",
        "policy_identity",
        "canonical_count",
        "surfaces",
        "drift_detected",
        "drift_class",
        "blocking_reason",
        "operator_action",
        "decision_status",
        "history_status",
    }
    missing = sorted(required - set(payload.keys()))
    if missing:
        issues.append(f"missing required fields: {', '.join(missing)}")

    if not isinstance(payload.get("canonical_count"), int):
        issues.append("canonical_count must be an integer")
    if not isinstance(payload.get("surfaces"), list):
        issues.append("surfaces must be a list")
    if not isinstance(payload.get("drift_detected"), bool):
        issues.append("drift_detected must be boolean")

    issues.extend(_catalog_history_status_issues(payload))

    decision_status = payload.get("decision_status")
    if decision_status not in {"resolved", "blocked_catalog_parity"}:
        issues.append("invalid decision_status")
    issues.extend(_catalog_blocking_state_issues(payload))

    return issues


def _routing_rate_issues(payload: Dict[str, Any]) -> List[str]:
    """Validate normalized routing-quality rates."""
    issues = []
    fields = (
        "unresolved_ambiguity_rate",
        "no_candidate_rate",
        "explainability_completeness_ratio",
    )
    for field in fields:
        value = payload.get(field)
        if type(value) not in (int, float) or (
            isinstance(value, float) and not math.isfinite(value)
        ):
            issues.append(f"{field} must be numeric")
        elif value < 0 or value > 1:
            issues.append(f"{field} must be within [0,1]")
    return issues


def _history_evidence_issues(payload: Dict[str, Any]) -> List[str]:
    """Validate history status and persistence-gate coherence."""
    status = payload.get("history_status")
    expected_gates = {
        "accepted": "pass",
        "not_recorded": "not_applicable",
        "schema_invalid_history": "fail",
        "trend_deterioration": "fail",
    }
    issues = []
    if not isinstance(status, str) or status not in expected_gates:
        issues.append("invalid history_status")
    outcomes = payload.get("gate_outcomes")
    hard = outcomes.get("hard") if isinstance(outcomes, dict) else None
    gate = hard.get("history_persistence") if isinstance(hard, dict) else None
    if not isinstance(gate, str) or gate not in {"pass", "fail", "not_applicable"}:
        issues.append("invalid history_persistence gate")
    elif (
        isinstance(status, str)
        and status in expected_gates
        and gate != expected_gates[status]
    ):
        issues.append("history_status contradicts history_persistence gate")
    return issues


def validate_routing_quality(payload: Dict[str, Any]) -> List[str]:
    """Validate one routing-quality metrics receipt."""
    required = {
        "schema_version",
        "run_id",
        "policy_identity",
        "decision_status_counts",
        "unresolved_ambiguity_rate",
        "no_candidate_rate",
        "top_rejection_reasons",
        "explainability_completeness_ratio",
        "parity_status",
        "history_status",
        "gate_outcomes",
    }
    issues = _missing_required(payload, required)
    if payload.get("schema_version") != "routing-quality.v1":
        issues.append("invalid schema_version: expected 'routing-quality.v1'")
    if not isinstance(payload.get("decision_status_counts"), dict):
        issues.append("decision_status_counts must be an object")
    if not isinstance(payload.get("top_rejection_reasons"), list):
        issues.append("top_rejection_reasons must be an array")
    issues.extend(_routing_rate_issues(payload))
    if payload.get("parity_status") not in {"pass", "fail"}:
        issues.append("parity_status must be 'pass' or 'fail'")

    issues.extend(_history_evidence_issues(payload))
    return issues


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify router schema payload")
    parser.add_argument(
        "--input", type=Path, help="Path to router JSON payload (defaults to stdin)"
    )
    parser.add_argument(
        "--fail-on-sensitive-fields",
        action="store_true",
        help="Fail if sensitive patterns are present in payload values",
    )
    return parser.parse_args()


def _validation_result(
    payload: Dict[str, Any], *, fail_on_sensitive_fields: bool
) -> tuple[str, List[str]]:
    """Route one payload to its owning validator."""
    normalized = _selection_payload_from_envelope(payload)
    if "top_candidates" in normalized:
        return "router", validate_router_result(
            normalized,
            fail_on_sensitive_fields=fail_on_sensitive_fields,
        )
    if (
        normalized.get("schema_version") == "routing-quality.v1"
        or "decision_status_counts" in normalized
    ):
        return "routing-quality", validate_routing_quality(normalized)
    if (
        normalized.get("schema_version") == "goal-decision.v1"
        or "recommended_candidate" in normalized
    ):
        return "goal", validate_goal_decision(normalized)
    if (
        normalized.get("schema_version") == "catalog-parity.v1"
        or "drift_detected" in normalized
    ):
        return "catalog", validate_catalog_parity(normalized)
    if (
        "decision_status" in normalized
        or normalized.get("schema_version") == "selection-decision.v1"
    ):
        return "selection", validate_selection_decision(normalized)
    return "unknown", [
        "payload is neither a router result nor a selection decision payload"
    ]


def _report_validation(mode: str, issues: List[str]) -> int:
    """Print one stable schema-validation result."""
    if not issues:
        print(f"service={SERVICE_ID} {mode.title()} schema validation passed.")
        return 0
    print(f"service={SERVICE_ID} {mode.title()} schema validation failed:")
    for issue in issues:
        print(f"- {issue}")
    return 1


def main() -> int:
    """Load, route, and report one router or selection payload."""
    args = parse_args()
    try:
        payload = load_payload(args.input)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        source = str(args.input) if args.input else "stdin"
        logger.exception(
            "service=%s event=input_rejected source=%s error=%s",
            SERVICE_ID,
            source,
            type(exc).__name__,
        )
        print(f"service={SERVICE_ID} Router schema input rejected: {source}")
        return 1
    if not payload:
        print(f"service={SERVICE_ID} No payload provided; schema verification skipped.")
        return 0
    mode, issues = _validation_result(
        payload,
        fail_on_sensitive_fields=args.fail_on_sensitive_fields,
    )
    return _report_validation(mode, issues)


if __name__ == "__main__":
    raise SystemExit(main())
