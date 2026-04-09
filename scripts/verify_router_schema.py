#!/usr/bin/env python3
"""Validate router JSON payloads for schema and telemetry safety."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_LIB = REPO_ROOT / 'utilities' / 'skill-builder' / 'scripts'
if str(SCHEMA_LIB) not in sys.path:
    sys.path.insert(0, str(SCHEMA_LIB))

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
    data = payload.get("data")
    if isinstance(data, dict):
        decision = data.get("decision")
        if isinstance(decision, dict):
            return decision
    return payload


def validate_selection_decision(payload: Dict[str, Any]) -> List[str]:
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
