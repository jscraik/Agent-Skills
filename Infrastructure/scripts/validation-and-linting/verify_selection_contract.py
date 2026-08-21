#!/usr/bin/env python3
"""Deterministic fixture verifier for selection contract behavior."""

from __future__ import annotations

import argparse
import importlib
import json
import logging
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]

sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lifecycle-and-sync"))

selection_policy_module = importlib.import_module("selection_policy")
selection_contract_module = importlib.import_module("ask.selection_contract")
catalog_parity_module = importlib.import_module("ask.catalog_parity")
policy_identity = selection_policy_module.policy_identity
EligibleCandidate = selection_contract_module.EligibleCandidate
build_decision_payload = selection_contract_module.build_decision_payload
build_goal_decision = selection_contract_module.build_goal_decision
candidate_history_issue = catalog_parity_module._candidate_history_issue

logger = logging.getLogger(__name__)
def resolve_fixture_path(filename: str) -> Path:
    """
    Resolve a selection-contract fixture path across supported repository layouts.

    Prefers `<repo>/tests/fixtures/selection-contract/<filename>` and falls back
    to `<repo>/Infrastructure/tests/fixtures/selection-contract/<filename>`.
    Returns the primary path when neither exists.
    """
    primary = REPO_ROOT / "tests" / "fixtures" / "selection-contract" / filename
    fallback = REPO_ROOT / "Infrastructure" / "tests" / "fixtures" / "selection-contract" / filename
    if primary.exists():
        return primary
    if fallback.exists():
        return fallback
    return primary


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments for the selection contract verification tool.
    
    Returns:
        argparse.Namespace: Parsed arguments with attributes:
            - fixtures (Path): Path to the route fixture JSON.
            - artifact (Path): Path to write the routing quality JSON artifact.
            - goal_fixtures (Path): Path to the goal fixture JSON.
            - history_path (Path|None): Optional JSONL history file path for append-only trend records.
            - history_max_runs (int): Maximum number of schema-valid history rows to retain.
    """
    parser = argparse.ArgumentParser(description="Verify deterministic selection contract fixtures.")
    parser.add_argument(
        "--fixtures",
        type=Path,
        default=resolve_fixture_path("route-fixtures.json"),
        help="Path to route fixture file.",
    )
    parser.add_argument(
        "--artifact",
        type=Path,
        default=REPO_ROOT / "artifacts" / "validation" / "latest" / "routing-quality.json",
        help="Path to write routing quality artifact.",
    )
    parser.add_argument(
        "--goal-fixtures",
        type=Path,
        default=resolve_fixture_path("goal-fixtures.json"),
        help="Path to goal fixture file.",
    )
    parser.add_argument(
        "--history-path",
        type=Path,
        default=None,
        help="Optional JSONL history path for append-only routing quality trend records.",
    )
    parser.add_argument(
        "--history-max-runs",
        type=int,
        default=200,
        help="Max schema-valid history rows to retain when --history-path is provided.",
    )
    return parser.parse_args()


def _check_explainability(decision: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    for selected in decision.get("selected_candidates", []):
        if "confidence" not in selected:
            issues.append(f"selected candidate missing confidence: {selected.get('candidate_id')}")
        if not selected.get("rationale"):
            issues.append(f"selected candidate missing rationale: {selected.get('candidate_id')}")
    for excluded in decision.get("excluded_candidates", []):
        if not excluded.get("exclusion_reason"):
            issues.append(f"excluded candidate missing exclusion_reason: {excluded.get('candidate_id')}")
    return issues


def _fixture_to_eligible(fixture: dict[str, Any]) -> list[EligibleCandidate]:
    """
    Convert a route fixture's `eligible_candidates` entries into a list of `EligibleCandidate` objects.
    
    Parameters:
        fixture (dict): Fixture object expected to contain an `eligible_candidates` list of candidate mappings.
            Each candidate mapping should include:
            - `name` (required): candidate name
            - `path` (required): candidate path
            - `description` (optional): candidate description (defaults to empty string)
            - `scope_rank` (optional): numeric rank (defaults to 999)
    
    Returns:
        list[EligibleCandidate]: A list of `EligibleCandidate` instances built from the fixture entries.
    """
    items = []
    for candidate in fixture.get("eligible_candidates", []):
        items.append(
            EligibleCandidate(
                name=str(candidate["name"]),
                path=str(candidate["path"]),
                description=str(candidate.get("description", "")),
                scope_rank=int(candidate.get("scope_rank", 999)),
            )
        )
    return items


def _append_history(
    history_path: Path,
    row: dict[str, Any],
    *,
    max_runs: int,
) -> str | None:
    """
    Append one accepted metrics row without rewriting invalid or deteriorating history.
    
    Parameters:
    	history_path (Path): Path to the JSONL history file to read and overwrite.
    	row (dict[str, Any]): Metrics row to append (no schema enforcement is performed here).
    	max_runs (int): Maximum number of history rows to retain; values less than 1 are treated as 1.
    """
    issue = candidate_history_issue(history_path, row)
    if issue:
        return issue

    existing_rows: list[dict[str, Any]] = []
    if history_path.exists():
        for raw in history_path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = raw.strip()
            if not line:
                continue
            payload = json.loads(line)
            if not isinstance(payload, dict):
                return "schema_invalid_history"
            existing_rows.append(payload)

    existing_rows.append(row)

    bounded_rows = existing_rows[-max(1, int(max_runs)) :]

    history_path.parent.mkdir(parents=True, exist_ok=True)
    history_path.write_text(
        "".join(json.dumps(item, sort_keys=True) + "\n" for item in bounded_rows),
        encoding="utf-8",
    )
    return None


def _routing_history_row(
    artifact: dict[str, Any],
    active_policy_identity: str,
    unresolved_ambiguity_rate: float,
    no_candidate_rate: float,
) -> dict[str, Any]:
    """Build the accepted routing-quality sample persisted after validation."""
    return {
        "schema_version": "routing-quality-history.v1",
        "run_id": artifact["run_id"],
        "generated_at": artifact["generated_at"],
        "policy_identity": active_policy_identity,
        "decision_status_counts": artifact["decision_status_counts"],
        "unresolved_ambiguity_rate": unresolved_ambiguity_rate,
        "no_candidate_rate": no_candidate_rate,
        "parity_status": artifact["parity_status"],
    }


def _record_history(args: argparse.Namespace, failed: list[dict[str, Any]], row: dict[str, Any]) -> str | None:
    """Persist one accepted sample when the current fixture run passed."""
    if not args.history_path or failed:
        return None
    return _append_history(args.history_path, row, max_runs=args.history_max_runs)


def main() -> int:
    """
    Run verification of selection contract fixtures, produce a routing-quality artifact and optional history entry.
    
    Loads route fixtures (and optionally goal fixtures), builds and validates decisions against expected outputs, aggregates per-fixture results and summary metrics (including explainability and failure-mapping checks), writes a JSON artifact describing outcomes and gates, optionally appends a bounded JSONL history row when provided and there are no failures, prints a concise summary to stdout, and exits with a status indicating success or failure.
    
    Returns:
        int: 0 on successful verification (no failing fixtures), 1 on failure or input/validation errors.
    """
    args = parse_args()
    if not args.fixtures.exists():
        print(f"Fixture file not found: {args.fixtures}")
        return 1

    fixture_payload = json.loads(args.fixtures.read_text(encoding="utf-8"))
    fixtures = fixture_payload.get("fixtures", [])
    if not isinstance(fixtures, list) or not fixtures:
        print(f"No fixtures found in {args.fixtures}")
        return 1

    active_policy_identity = policy_identity()
    status_counter: Counter[str] = Counter()
    failure_counter: Counter[str] = Counter()
    rejection_counter: Counter[str] = Counter()
    explainability_failures = 0
    failure_mapping_failures = 0
    results: list[dict[str, Any]] = []

    for fixture in fixtures:
        fixture_id = fixture.get("id", "unknown")
        expected = fixture.get("expected", {})
        eligible = _fixture_to_eligible(fixture)
        decision = build_decision_payload(
            request=str(fixture.get("request", "")),
            policy_identity=active_policy_identity,
            considered_limit=int(fixture.get("considered_limit", 20)),
            top_k=int(fixture.get("top_k", 3)),
            eligible_candidates=eligible,
            ranked_candidates=list(fixture.get("ranked_candidates", [])),
            uncertainty_reasons=list(fixture.get("uncertainty_reasons", [])),
        )

        issues: list[str] = []
        if decision["decision_status"] != expected.get("decision_status"):
            issues.append(
                f"decision_status mismatch: expected={expected.get('decision_status')} actual={decision['decision_status']}"
            )
        if decision.get("failure_class") != expected.get("failure_class"):
            issues.append(
                f"failure_class mismatch: expected={expected.get('failure_class')} actual={decision.get('failure_class')}"
            )

        selected_names = [candidate.get("name") for candidate in decision.get("selected_candidates", [])]
        if selected_names != list(expected.get("selected_names", [])):
            issues.append(
                f"selected_names mismatch: expected={expected.get('selected_names', [])} actual={selected_names}"
            )

        if int(decision.get("considered_total", -1)) != int(expected.get("considered_total", -1)):
            issues.append(
                f"considered_total mismatch: expected={expected.get('considered_total')} actual={decision.get('considered_total')}"
            )
        if bool(decision.get("considered_truncated")) != bool(expected.get("considered_truncated")):
            issues.append(
                f"considered_truncated mismatch: expected={expected.get('considered_truncated')} actual={decision.get('considered_truncated')}"
            )
        if decision.get("policy_identity") != active_policy_identity:
            issues.append("policy_identity mismatch against active selection policy")
        if decision["decision_status"] != "resolved" and not decision.get("operator_action"):
            issues.append("non-success decision missing operator_action")

        explainability_issues = _check_explainability(decision)
        if explainability_issues:
            explainability_failures += 1
            issues.extend(explainability_issues)
        for excluded in decision.get("excluded_candidates", []):
            reason = str(excluded.get("exclusion_reason") or "unknown")
            rejection_counter[reason] += 1
        if decision["decision_status"] != "resolved" and not decision.get("failure_class"):
            failure_mapping_failures += 1

        status_counter[str(decision["decision_status"])] += 1
        failure_key = decision.get("failure_class") or "none"
        failure_counter[str(failure_key)] += 1

        results.append(
            {
                "id": fixture_id,
                "surface": "route",
                "decision_status": decision["decision_status"],
                "failure_class": decision.get("failure_class"),
                "passed": not issues,
                "issues": issues,
            }
        )

    goal_results: list[dict[str, Any]] = []
    if args.goal_fixtures.exists():
        goal_payload = json.loads(args.goal_fixtures.read_text(encoding="utf-8"))
        goal_fixtures = goal_payload.get("fixtures", [])
        if isinstance(goal_fixtures, list):
            for fixture in goal_fixtures:
                fixture_id = fixture.get("id", "goal-unknown")
                route_decision = fixture.get("route_decision", {})
                expected = fixture.get("expected", {})
                issues: list[str] = []

                if not isinstance(route_decision, dict):
                    issues.append("route_decision fixture must be an object")
                    goal_decision = {}
                else:
                    # Goal must always reflect the active route/policy identity.
                    route_decision["policy_identity"] = active_policy_identity
                    goal_decision = build_goal_decision(route_decision)

                if goal_decision.get("decision_status") != expected.get("decision_status"):
                    issues.append(
                        "goal decision_status mismatch: "
                        f"expected={expected.get('decision_status')} actual={goal_decision.get('decision_status')}"
                    )
                if goal_decision.get("failure_class") != expected.get("failure_class"):
                    issues.append(
                        "goal failure_class mismatch: "
                        f"expected={expected.get('failure_class')} actual={goal_decision.get('failure_class')}"
                    )

                recommended = goal_decision.get("recommended_candidate") or {}
                if recommended.get("name") != expected.get("recommended_name"):
                    issues.append(
                        "recommended candidate mismatch: "
                        f"expected={expected.get('recommended_name')} actual={recommended.get('name')}"
                    )
                alt_names = [item.get("name") for item in goal_decision.get("alternative_candidates", [])]
                if alt_names != list(expected.get("alternative_names", [])):
                    issues.append(
                        f"alternative_names mismatch: expected={expected.get('alternative_names', [])} actual={alt_names}"
                    )

                if goal_decision.get("policy_identity") != active_policy_identity:
                    issues.append("goal policy_identity mismatch against active selection policy")
                if goal_decision.get("decision_status") != "resolved" and not goal_decision.get("operator_action"):
                    issues.append("goal non-success decision missing operator_action")
                if goal_decision.get("decision_status") != "resolved" and not goal_decision.get("failure_class"):
                    failure_mapping_failures += 1

                status_key = goal_decision.get("decision_status") or "none"
                status_counter[str(status_key)] += 1
                failure_key = goal_decision.get("failure_class") or "none"
                failure_counter[str(failure_key)] += 1
                goal_results.append(
                    {
                        "id": fixture_id,
                        "surface": "goal",
                        "decision_status": goal_decision.get("decision_status"),
                        "failure_class": goal_decision.get("failure_class"),
                        "passed": not issues,
                        "issues": issues,
                    }
                )

    all_results = results + goal_results

    failed = [item for item in all_results if not item["passed"]]
    unresolved_ambiguity_rate = (
        status_counter.get("unresolved_ambiguity", 0) / len(all_results) if all_results else 0.0
    )
    no_candidate_rate = (
        status_counter.get("degraded_no_candidates", 0) / len(all_results) if all_results else 0.0
    )
    explainability_completeness_ratio = (
        1.0 - (explainability_failures / max(1, len(all_results)))
    )
    gate_outcomes = {
        "hard": {
            "catalog_parity": "fail" if status_counter.get("blocked_catalog_parity", 0) > 0 else "pass",
            "explainability_completeness": "pass" if explainability_failures == 0 else "fail",
            "failure_mapping_completeness": "pass" if failure_mapping_failures == 0 else "fail",
        },
        "soft": {
            "unresolved_ambiguity_rate": unresolved_ambiguity_rate,
            "no_candidate_rate": no_candidate_rate,
        },
    }
    artifact = {
        "schema_version": "routing-quality.v1",
        "run_id": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "policy_identity": active_policy_identity,
        "fixture_path": str(args.fixtures.relative_to(REPO_ROOT)) if args.fixtures.is_relative_to(REPO_ROOT) else str(args.fixtures),
        "goal_fixture_path": str(args.goal_fixtures.relative_to(REPO_ROOT))
        if args.goal_fixtures.is_relative_to(REPO_ROOT)
        else str(args.goal_fixtures),
        "totals": {
            "fixtures": len(all_results),
            "passed": len(all_results) - len(failed),
            "failed": len(failed),
            "explainability_failures": explainability_failures,
        },
        # Backward compatibility: both keys intentionally mirror status_counter.
        "decision_status_counts": dict(status_counter),
        "status_counts": dict(status_counter),
        "failure_class_counts": dict(failure_counter),
        "top_rejection_reasons": [
            {"reason": reason, "count": count}
            for reason, count in rejection_counter.most_common(5)
        ],
        "explainability_completeness_ratio": explainability_completeness_ratio,
        "parity_status": "pass" if status_counter.get("blocked_catalog_parity", 0) == 0 else "fail",
        "gate_outcomes": gate_outcomes,
        "explainability_complete": explainability_failures == 0,
        "fixtures": all_results,
        "unresolved_ambiguity_rate": unresolved_ambiguity_rate,
        "no_candidate_rate": no_candidate_rate,
    }

    args.artifact.parent.mkdir(parents=True, exist_ok=True)
    args.artifact.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    history_issue = _record_history(
        args,
        failed,
        _routing_history_row(artifact, active_policy_identity, unresolved_ambiguity_rate, no_candidate_rate),
    )
    if history_issue:
        print(f"Selection history rejected: {history_issue}")
        return 1

    print(f"Selection contract fixtures: total={len(all_results)} failed={len(failed)}")
    print(f"Policy identity: {active_policy_identity}")
    print(f"Artifact: {args.artifact}")

    if failed:
        print("Selection contract verification failed:")
        for item in failed:
            print(f"- {item['id']}")
            for issue in item["issues"]:
                print(f"    * {issue}")
        return 1

    print("Selection contract verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
