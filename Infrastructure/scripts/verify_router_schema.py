#!/usr/bin/env python3
"""Validate selection/router JSON payloads for schema and telemetry safety."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parents[2]
schema_lib_candidates = [
    REPO_ROOT / "utilities" / "skill-builder" / "scripts",
    REPO_ROOT / "Skills" / "skill-builder" / "scripts",
    REPO_ROOT / "plugins" / "skill-factory" / "skills" / "code_quality_review" / "skill-builder" / "scripts",
    REPO_ROOT / "Plugins" / "skill-factory" / "skills" / "code_quality_review" / "skill-builder" / "scripts",
    REPO_ROOT / "plugins" / "skill-factory" / "skills" / "skill-builder" / "scripts",
    REPO_ROOT / "Plugins" / "skill-factory" / "skills" / "skill-builder" / "scripts",
]
for schema_lib in schema_lib_candidates:
    if schema_lib.exists() and str(schema_lib) not in sys.path:
        sys.path.insert(0, str(schema_lib))

from skill_router_schema import validate_router_result  # noqa: E402


def load_payload(path: Path | None) -> Dict[str, Any]:
    if path is None:
        data = sys.stdin.read().strip()
    else:
        data = path.read_text(encoding='utf-8')

    if not data:
        return {}

    obj = json.loads(data)
    if not isinstance(obj, dict):
        raise ValueError('Expected JSON object payload')
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


def validate_selection_decision(payload: Dict[str, Any]) -> List[str]:
    """
    Validate a "selection decision" payload for required fields, types and consistency.
    
    Checks presence of required keys, that `decision_status` corresponds to the expected `failure_class`
    (mapping includes: `resolved`→None, `unresolved_ambiguity`→`AMBIGUITY_UNRESOLVED`,
    `blocked_policy_drift`→`DISCOVERY_POLICY_DRIFT`, `degraded_no_candidates`→`NO_ELIGIBLE_CANDIDATES`,
    `blocked_catalog_parity`→`CATALOG_PARITY_DRIFT`), and that specific fields have the expected types
    (e.g. candidate lists, integer counters, boolean flag). For any `decision_status` other than
    `resolved`, requires a non-empty `operator_action`.
    
    Parameters:
        payload (Dict[str, Any]): The selection decision JSON object to validate.
    
    Returns:
        List[str]: Validation issue messages found; empty list if the payload passes all checks.
    """
    issues: List[str] = []
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

    missing = sorted(required - set(payload.keys()))
    if missing:
        issues.append(f"missing required fields: {', '.join(missing)}")

    decision_status = payload.get("decision_status")
    valid_statuses = {
        "resolved": None,
        "unresolved_ambiguity": "AMBIGUITY_UNRESOLVED",
        "blocked_policy_drift": "DISCOVERY_POLICY_DRIFT",
        "degraded_no_candidates": "NO_ELIGIBLE_CANDIDATES",
        "blocked_catalog_parity": "CATALOG_PARITY_DRIFT",
    }
    if decision_status not in valid_statuses:
        issues.append("invalid decision_status")
    else:
        expected_failure = valid_statuses[decision_status]
        if payload.get("failure_class") != expected_failure:
            issues.append(
                "failure_class must match decision_status mapping "
                f"(status={decision_status}, expected={expected_failure}, actual={payload.get('failure_class')})"
            )

    if not isinstance(payload.get("selected_candidates"), list):
        issues.append("selected_candidates must be a list")
    if not isinstance(payload.get("considered_candidates"), list):
        issues.append("considered_candidates must be a list")
    if not isinstance(payload.get("excluded_candidates"), list):
        issues.append("excluded_candidates must be a list")
    if not isinstance(payload.get("considered_limit"), int):
        issues.append("considered_limit must be an integer")
    if not isinstance(payload.get("considered_total"), int):
        issues.append("considered_total must be an integer")
    if not isinstance(payload.get("considered_truncated"), bool):
        issues.append("considered_truncated must be boolean")
    if not isinstance(payload.get("truncated_count"), int):
        issues.append("truncated_count must be an integer")
    if decision_status != "resolved" and not str(payload.get("operator_action") or "").strip():
        issues.append("non-success selection decisions must include operator_action")

    return issues


def validate_goal_decision(payload: Dict[str, Any]) -> List[str]:
    """
    Validate a "goal decision" payload for required fields, value constraints and type expectations.
    
    Checks that required keys are present, that `decision_status` is either "resolved" or "intent_unresolved" and that associated fields satisfy the conditional rules for each status (e.g. `failure_class` and `operator_action` expectations), and that `alternative_candidates` and `disambiguation_prompts` are lists.
    
    Parameters:
        payload (Dict[str, Any]): The goal-decision JSON object to validate.
    
    Returns:
        List[str]: A list of validation issue messages; empty if the payload conforms to the expected schema and constraints.
    """
    issues: List[str] = []
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
    missing = sorted(required - set(payload.keys()))
    if missing:
        issues.append(f"missing required fields: {', '.join(missing)}")

    decision_status = payload.get("decision_status")
    if decision_status not in {"resolved", "intent_unresolved"}:
        issues.append("invalid decision_status")
    elif decision_status == "resolved":
        if payload.get("failure_class") is not None:
            issues.append("resolved goal decision must set failure_class=null")
        if payload.get("operator_action") is not None:
            issues.append("resolved goal decision must set operator_action=null")
    else:
        if payload.get("failure_class") != "INTENT_UNRESOLVED":
            issues.append("intent_unresolved goal decision must set failure_class=INTENT_UNRESOLVED")
        if not str(payload.get("operator_action") or "").strip():
            issues.append("intent_unresolved goal decision must include operator_action")

    if not isinstance(payload.get("alternative_candidates"), list):
        issues.append("alternative_candidates must be a list")
    if not isinstance(payload.get("disambiguation_prompts"), list):
        issues.append("disambiguation_prompts must be a list")

    return issues


def validate_catalog_parity(payload: Dict[str, Any]) -> List[str]:
    """
    Validate a catalog-parity payload and collect schema or semantic issues.
    
    Checks for required fields and validates types and conditional constraints specific to catalog-parity payloads. In particular it enforces allowed `decision_status` values and, when `decision_status` is `blocked_catalog_parity`, requires `drift_detected` to be `True` and a non-empty `operator_action`.
    
    Parameters:
        payload (Dict[str, Any]): Parsed JSON object representing a catalog-parity payload.
    
    Returns:
        List[str]: A list of human-readable issue messages; empty when the payload satisfies all checks.
    """
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

    decision_status = payload.get("decision_status")
    if decision_status not in {"resolved", "blocked_catalog_parity"}:
        issues.append("invalid decision_status")
    if decision_status == "blocked_catalog_parity":
        if payload.get("drift_detected") is not True:
            issues.append("blocked_catalog_parity must set drift_detected=true")
        if not str(payload.get("operator_action") or "").strip():
            issues.append("blocked_catalog_parity must include operator_action")

    return issues


def validate_routing_quality(payload: Dict[str, Any]) -> List[str]:
    """
    Validate a routing-quality metrics payload for required fields, types and value constraints.
    
    Checks:
    - Presence of required top-level fields expected for a routing-quality payload.
    - `decision_status_counts` is an object and `top_rejection_reasons` is an array.
    - `unresolved_ambiguity_rate`, `no_candidate_rate` and `explainability_completeness_ratio` are numeric and within 0 to 1 inclusive.
    - `parity_status` is either `"pass"` or `"fail"`.
    
    Parameters:
        payload (dict): Parsed JSON object representing routing-quality metrics.
    
    Returns:
        list[str]: A list of human-readable issue messages describing validation failures; empty if the payload passes validation.
    """
    issues: List[str] = []
    if payload.get("schema_version") != "routing-quality.v1":
        issues.append("invalid schema_version: expected 'routing-quality.v1'")
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
    }
    missing = sorted(required - set(payload.keys()))
    if missing:
        issues.append(f"missing required fields: {', '.join(missing)}")

    if not isinstance(payload.get("decision_status_counts"), dict):
        issues.append("decision_status_counts must be an object")
    if not isinstance(payload.get("top_rejection_reasons"), list):
        issues.append("top_rejection_reasons must be an array")
    for field in ("unresolved_ambiguity_rate", "no_candidate_rate", "explainability_completeness_ratio"):
        value = payload.get(field)
        if not isinstance(value, (int, float)):
            issues.append(f"{field} must be numeric")
            continue
        if value < 0 or value > 1:
            issues.append(f"{field} must be within [0,1]")
    if payload.get("parity_status") not in {"pass", "fail"}:
        issues.append("parity_status must be 'pass' or 'fail'")

    return issues


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Verify router schema payload')
    parser.add_argument('--input', type=Path, help='Path to router JSON payload (defaults to stdin)')
    parser.add_argument(
        '--fail-on-sensitive-fields',
        action='store_true',
        help='Fail if sensitive patterns are present in payload values',
    )
    return parser.parse_args()


def main() -> int:
    """
    Determine the payload type, run the corresponding schema validations, print results and return an exit code.
    
    The function reads a pre-loaded payload (already obtained via CLI args), infers its validation mode from content or schema version, invokes the appropriate validator, prints a short summary and any validation issues to stdout, and yields a conventional CLI exit code.
    
    Returns:
        int: `0` if validation passed or no payload was provided, `1` if validation failed.
    """
    args = parse_args()
    payload = load_payload(args.input)

    if not payload:
        print('No payload provided; schema verification skipped.')
        return 0

    normalized = _selection_payload_from_envelope(payload)
    issues: List[str]
    mode: str
    if "top_candidates" in normalized:
        mode = "router"
        issues = validate_router_result(
            normalized,
            fail_on_sensitive_fields=args.fail_on_sensitive_fields,
        )
    elif normalized.get("schema_version") == "routing-quality.v1" or "decision_status_counts" in normalized:
        mode = "routing-quality"
        issues = validate_routing_quality(normalized)
    elif normalized.get("schema_version") == "goal-decision.v1" or "recommended_candidate" in normalized:
        mode = "goal"
        issues = validate_goal_decision(normalized)
    elif normalized.get("schema_version") == "catalog-parity.v1" or "drift_detected" in normalized:
        mode = "catalog"
        issues = validate_catalog_parity(normalized)
    elif "decision_status" in normalized or normalized.get("schema_version") == "selection-decision.v1":
        mode = "selection"
        issues = validate_selection_decision(normalized)
    else:
        mode = "unknown"
        issues = ["payload is neither a router result nor a selection decision payload"]

    if issues:
        print(f'{mode.title()} schema validation failed:')
        for issue in issues:
            print(f'- {issue}')
        return 1

    print(f'{mode.title()} schema validation passed.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
