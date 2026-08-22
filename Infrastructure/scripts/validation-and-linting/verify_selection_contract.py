#!/usr/bin/env python3
"""Deterministic fixture verifier for selection contract behavior."""

from __future__ import annotations

import argparse
import fcntl
import importlib
import json
import logging
import os
import sys
from collections import Counter
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from tempfile import NamedTemporaryFile
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
rejected_history_path = catalog_parity_module._rejected_history_path

logger = logging.getLogger(__name__)
SERVICE_ID = "selection-contract-verifier"
MINIMUM_HISTORY_RUNS = 8


def resolve_fixture_path(filename: str) -> Path:
    """
    Resolve a selection-contract fixture path across supported repository layouts.

    Prefers `<repo>/tests/fixtures/selection-contract/<filename>` and falls back
    to `<repo>/Infrastructure/tests/fixtures/selection-contract/<filename>`.
    Returns the primary path when neither exists.
    """
    primary = REPO_ROOT / "tests" / "fixtures" / "selection-contract" / filename
    fallback = (
        REPO_ROOT
        / "Infrastructure"
        / "tests"
        / "fixtures"
        / "selection-contract"
        / filename
    )
    if primary.exists():
        return primary
    if fallback.exists():
        return fallback
    return primary


def parse_args() -> argparse.Namespace:
    """Parse selection-contract verifier arguments."""
    parser = argparse.ArgumentParser(
        description="Verify deterministic selection contract fixtures."
    )
    parser.add_argument(
        "--fixtures",
        type=Path,
        default=resolve_fixture_path("route-fixtures.json"),
        help="Path to route fixture file.",
    )
    parser.add_argument(
        "--artifact",
        type=Path,
        default=REPO_ROOT
        / "artifacts"
        / "validation"
        / "latest"
        / "routing-quality.json",
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
        type=_history_max_runs,
        default=200,
        help="Max schema-valid history rows to retain when --history-path is provided.",
    )
    return parser.parse_args()


def _history_max_runs(value: str) -> int:
    """Require enough retained rows for one complete trend window."""
    runs = int(value)
    if runs < MINIMUM_HISTORY_RUNS:
        raise argparse.ArgumentTypeError(
            f"history-max-runs must be at least {MINIMUM_HISTORY_RUNS}"
        )
    return runs


def _check_explainability(decision: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    for selected in decision.get("selected_candidates", []):
        if "confidence" not in selected:
            issues.append(
                f"selected candidate missing confidence: {selected.get('candidate_id')}"
            )
        if not selected.get("rationale"):
            issues.append(
                f"selected candidate missing rationale: {selected.get('candidate_id')}"
            )
    for excluded in decision.get("excluded_candidates", []):
        if not excluded.get("exclusion_reason"):
            issues.append(
                f"excluded candidate missing exclusion_reason: {excluded.get('candidate_id')}"
            )
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
    """Append one accepted row without rewriting invalid or deteriorating history."""
    history_path.parent.mkdir(parents=True, exist_ok=True)
    with _history_lock(history_path):
        return _append_history_locked(history_path, row, max_runs=max_runs)


@contextmanager
def _history_lock(history_path: Path):
    """Serialize history validation and replacement across verifier processes."""
    lock_path = history_path.with_suffix(f"{history_path.suffix}.lock")
    with lock_path.open("a", encoding="utf-8") as lock_file:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


def _append_history_locked(
    history_path: Path,
    row: dict[str, Any],
    *,
    max_runs: int,
) -> str | None:
    """Validate and replace history while the caller holds its writer lock."""
    issue = candidate_history_issue(history_path, row)
    if issue:
        _write_rejected_history(history_path, row, issue)
        return issue

    existing_rows: list[dict[str, Any]] = []
    if history_path.exists():
        for raw in history_path.read_text(
            encoding="utf-8", errors="ignore"
        ).splitlines():
            line = raw.strip()
            if not line:
                continue
            payload = json.loads(line)
            if not isinstance(payload, dict):
                return "schema_invalid_history"
            existing_rows.append(payload)

    existing_rows.append(row)

    bounded_rows = existing_rows[-max(MINIMUM_HISTORY_RUNS, int(max_runs)) :]

    _atomic_write_history(history_path, bounded_rows)
    rejected_history_path(history_path).unlink(missing_ok=True)
    return None


def _atomic_write_history(history_path: Path, rows: list[dict[str, Any]]) -> None:
    """Durably replace history through a temporary file in the same directory."""
    content = "".join(json.dumps(item, sort_keys=True) + "\n" for item in rows)
    with NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=history_path.parent,
        prefix=f".{history_path.name}.",
        delete=False,
    ) as temporary:
        temporary.write(content)
        temporary.flush()
        os.fsync(temporary.fileno())
        temporary_path = Path(temporary.name)
    try:
        os.replace(temporary_path, history_path)
    finally:
        temporary_path.unlink(missing_ok=True)


def _write_rejected_history(
    history_path: Path, row: dict[str, Any], issue: str
) -> None:
    """Preserve rejected evidence separately from the accepted baseline."""
    path = rejected_history_path(history_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"issue": issue, "candidate": row}, sort_keys=True) + "\n",
        encoding="utf-8",
    )


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


def _record_history(
    args: argparse.Namespace, failed: list[dict[str, Any]], row: dict[str, Any]
) -> str | None:
    """Persist one accepted sample when the current fixture run passed."""
    if not args.history_path or failed:
        return None
    return _append_history(args.history_path, row, max_runs=args.history_max_runs)


def _route_issues(
    decision: dict[str, Any], expected: dict[str, Any], active_policy: str
) -> list[str]:
    """Return contract mismatches for one route decision."""
    issues: list[str] = []
    comparisons = (
        (
            "decision_status",
            decision.get("decision_status"),
            expected.get("decision_status"),
        ),
        ("failure_class", decision.get("failure_class"), expected.get("failure_class")),
        (
            "considered_total",
            int(decision.get("considered_total", -1)),
            int(expected.get("considered_total", -1)),
        ),
        (
            "considered_truncated",
            bool(decision.get("considered_truncated")),
            bool(expected.get("considered_truncated")),
        ),
    )
    issues.extend(_comparison_issues(comparisons))
    selected = [
        candidate.get("name") for candidate in decision.get("selected_candidates", [])
    ]
    expected_selected = list(expected.get("selected_names", []))
    if selected != expected_selected:
        issues.append(
            f"selected_names mismatch: expected={expected_selected} actual={selected}"
        )
    if decision.get("policy_identity") != active_policy:
        issues.append("policy_identity mismatch against active selection policy")
    if decision.get("decision_status") != "resolved" and not decision.get(
        "operator_action"
    ):
        issues.append("non-success decision missing operator_action")
    return issues


def _comparison_issues(comparisons: tuple[tuple[str, Any, Any], ...]) -> list[str]:
    """Render mismatched expected and actual values."""
    return [
        f"{label} mismatch: expected={wanted} actual={actual}"
        for label, actual, wanted in comparisons
        if actual != wanted
    ]


def _route_decision(fixture: dict[str, Any], active_policy: str) -> dict[str, Any]:
    """Build one route fixture decision."""
    return build_decision_payload(
        request=str(fixture.get("request", "")),
        policy_identity=active_policy,
        considered_limit=int(fixture.get("considered_limit", 20)),
        top_k=int(fixture.get("top_k", 3)),
        eligible_candidates=_fixture_to_eligible(fixture),
        ranked_candidates=list(fixture.get("ranked_candidates", [])),
        uncertainty_reasons=list(fixture.get("uncertainty_reasons", [])),
    )


def _evaluate_routes(
    fixtures: list[dict[str, Any]], active_policy: str
) -> tuple[Any, ...]:
    """Evaluate route fixtures and return results plus aggregate counters."""
    results: list[dict[str, Any]] = []
    status_counter: Counter[str] = Counter()
    failure_counter: Counter[str] = Counter()
    rejection_counter: Counter[str] = Counter()
    explainability_failures = failure_mapping_failures = 0
    for fixture in fixtures:
        decision = _route_decision(fixture, active_policy)
        issues = _route_issues(decision, fixture.get("expected", {}), active_policy)
        explainability_issues = _check_explainability(decision)
        explainability_failures += bool(explainability_issues)
        issues.extend(explainability_issues)
        for excluded in decision.get("excluded_candidates", []):
            rejection_counter[str(excluded.get("exclusion_reason") or "unknown")] += 1
        failure_mapping_failures += decision.get(
            "decision_status"
        ) != "resolved" and not decision.get("failure_class")
        status_counter[str(decision.get("decision_status"))] += 1
        failure_counter[str(decision.get("failure_class") or "none")] += 1
        results.append(_result(fixture.get("id", "unknown"), "route", decision, issues))
    return (
        results,
        status_counter,
        failure_counter,
        rejection_counter,
        explainability_failures,
        failure_mapping_failures,
    )


def _goal_issues(
    decision: dict[str, Any], expected: dict[str, Any], active_policy: str
) -> list[str]:
    """Return contract mismatches for one goal decision."""
    issues: list[str] = []
    comparisons = (
        (
            "goal decision_status",
            decision.get("decision_status"),
            expected.get("decision_status"),
        ),
        (
            "goal failure_class",
            decision.get("failure_class"),
            expected.get("failure_class"),
        ),
        (
            "recommended candidate",
            (decision.get("recommended_candidate") or {}).get("name"),
            expected.get("recommended_name"),
        ),
        (
            "alternative_names",
            [item.get("name") for item in decision.get("alternative_candidates", [])],
            list(expected.get("alternative_names", [])),
        ),
    )
    for label, actual, wanted in comparisons:
        if actual != wanted:
            issues.append(f"{label} mismatch: expected={wanted} actual={actual}")
    if decision.get("policy_identity") != active_policy:
        issues.append("goal policy_identity mismatch against active selection policy")
    if decision.get("decision_status") != "resolved" and not decision.get(
        "operator_action"
    ):
        issues.append("goal non-success decision missing operator_action")
    return issues


def _goal_decision(
    fixture: dict[str, Any], active_policy: str
) -> tuple[dict[str, Any], list[str]]:
    """Build one goal fixture decision and input-shape errors."""
    route_decision = fixture.get("route_decision", {})
    if not isinstance(route_decision, dict):
        return {}, ["route_decision fixture must be an object"]
    route_decision["policy_identity"] = active_policy
    return build_goal_decision(route_decision), []


def _evaluate_goals(path: Path, active_policy: str) -> tuple[Any, ...]:
    """Evaluate optional goal fixtures and return results plus counters."""
    results: list[dict[str, Any]] = []
    status_counter: Counter[str] = Counter()
    failure_counter: Counter[str] = Counter()
    failure_mapping_failures = 0
    if not path.exists():
        return results, status_counter, failure_counter, failure_mapping_failures
    fixtures, issue = _read_fixture_objects(path)
    if issue:
        results.append(_result("goal-fixtures", "goal", {}, [issue]))
        return results, status_counter, failure_counter, failure_mapping_failures
    assert fixtures is not None
    for fixture in fixtures:
        decision, issues = _goal_decision(fixture, active_policy)
        issues.extend(
            _goal_issues(decision, fixture.get("expected", {}), active_policy)
        )
        failure_mapping_failures += decision.get(
            "decision_status"
        ) != "resolved" and not decision.get("failure_class")
        status_counter[str(decision.get("decision_status") or "none")] += 1
        failure_counter[str(decision.get("failure_class") or "none")] += 1
        results.append(
            _result(fixture.get("id", "goal-unknown"), "goal", decision, issues)
        )
    return results, status_counter, failure_counter, failure_mapping_failures


def _result(
    fixture_id: str, surface: str, decision: dict[str, Any], issues: list[str]
) -> dict[str, Any]:
    """Build one stable fixture result record."""
    return {
        "id": fixture_id,
        "surface": surface,
        "decision_status": decision.get("decision_status"),
        "failure_class": decision.get("failure_class"),
        "passed": not issues,
        "issues": issues,
    }


def _artifact_path(path: Path) -> str:
    """Render a repository-relative path when possible."""
    return (
        str(path.relative_to(REPO_ROOT))
        if path.is_relative_to(REPO_ROOT)
        else str(path)
    )


def _rates(
    results: list[dict[str, Any]],
    status_counter: Counter[str],
    explainability_failures: int,
) -> tuple[float, ...]:
    """Calculate routing quality rates."""
    count = len(results)
    ambiguity = status_counter.get("unresolved_ambiguity", 0) / count if count else 0.0
    no_candidate = (
        status_counter.get("degraded_no_candidates", 0) / count if count else 0.0
    )
    explainability = 1.0 - (explainability_failures / max(1, count))
    return ambiguity, no_candidate, explainability


def _gate_outcomes(
    statuses: Counter[str],
    explainability_failures: int,
    mapping_failures: int,
    rates: tuple[float, ...],
) -> dict[str, Any]:
    """Build hard and soft gate outcomes."""
    return {
        "hard": {
            "catalog_parity": "fail"
            if statuses.get("blocked_catalog_parity", 0)
            else "pass",
            "explainability_completeness": "pass"
            if not explainability_failures
            else "fail",
            "failure_mapping_completeness": "pass" if not mapping_failures else "fail",
        },
        "soft": {"unresolved_ambiguity_rate": rates[0], "no_candidate_rate": rates[1]},
    }


def _artifact(
    args: argparse.Namespace,
    active_policy: str,
    results: list[dict[str, Any]],
    counters: tuple[Any, ...],
) -> dict[str, Any]:
    """Build the routing-quality artifact."""
    statuses, failures, rejections, explainability_failures, mapping_failures = counters
    failed = [item for item in results if not item["passed"]]
    rates = _rates(results, statuses, explainability_failures)
    return {
        "schema_version": "routing-quality.v1",
        "run_id": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "policy_identity": active_policy,
        "fixture_path": _artifact_path(args.fixtures),
        "goal_fixture_path": _artifact_path(args.goal_fixtures),
        "totals": _artifact_totals(results, failed, explainability_failures),
        "decision_status_counts": dict(statuses),
        "status_counts": dict(statuses),
        "failure_class_counts": dict(failures),
        "top_rejection_reasons": _top_rejections(rejections),
        "explainability_completeness_ratio": rates[2],
        "parity_status": "fail"
        if statuses.get("blocked_catalog_parity", 0)
        else "pass",
        "gate_outcomes": _gate_outcomes(
            statuses, explainability_failures, mapping_failures, rates
        ),
        "explainability_complete": not explainability_failures,
        "fixtures": results,
        "unresolved_ambiguity_rate": rates[0],
        "no_candidate_rate": rates[1],
    }


def _artifact_totals(
    results: list[dict[str, Any]],
    failed: list[dict[str, Any]],
    explainability_failures: int,
) -> dict[str, int]:
    """Build artifact total counts."""
    return {
        "fixtures": len(results),
        "passed": len(results) - len(failed),
        "failed": len(failed),
        "explainability_failures": explainability_failures,
    }


def _top_rejections(rejections: Counter[str]) -> list[dict[str, Any]]:
    """Build the bounded rejection-reason summary."""
    return [
        {"reason": reason, "count": count}
        for reason, count in rejections.most_common(5)
    ]


def _load_routes(path: Path) -> list[dict[str, Any]] | None:
    """Load required route fixtures with existing user diagnostics."""
    if not path.exists():
        print(f"Fixture file not found: {path}")
        return None
    fixtures, issue = _read_fixture_objects(path)
    if issue:
        print(f"Invalid fixtures in {path}: {issue}")
        return None
    if not fixtures:
        print(f"No fixtures found in {path}")
        return None
    return fixtures


def _read_fixture_objects(
    path: Path,
) -> tuple[list[dict[str, Any]] | None, str | None]:
    """Read one fixture document and validate its external input shape."""
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        issue = f"fixture_read_error:{type(exc).__name__}"
        logger.error("service=%s event=fixture_rejected code=%s", SERVICE_ID, issue)
        return None, issue
    if not isinstance(document, dict):
        issue = "fixture_root_must_be_object"
    elif not isinstance(document.get("fixtures", []), list):
        issue = "fixtures_must_be_array"
    elif not all(isinstance(item, dict) for item in document.get("fixtures", [])):
        issue = "fixture_entries_must_be_objects"
    else:
        return document.get("fixtures", []), None
    logger.error("service=%s event=fixture_rejected code=%s", SERVICE_ID, issue)
    return None, issue


def _report(
    args: argparse.Namespace,
    active_policy: str,
    results: list[dict[str, Any]],
    artifact: dict[str, Any],
    history_issue: str | None,
) -> int:
    """Persist history and print the stable command result."""
    failed = [item for item in results if not item["passed"]]
    if history_issue:
        logger.error(
            "service=%s event=history_rejected code=%s", SERVICE_ID, history_issue
        )
        print(f"Selection history rejected: {history_issue}")
        return 1
    print(f"Selection contract fixtures: total={len(results)} failed={len(failed)}")
    print(f"Policy identity: {active_policy}")
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


def _apply_history_outcome(
    args: argparse.Namespace,
    results: list[dict[str, Any]],
    artifact: dict[str, Any],
    active_policy: str,
) -> str | None:
    """Persist accepted history and bind its outcome into the artifact."""
    failed = [item for item in results if not item["passed"]]
    row = _routing_history_row(
        artifact,
        active_policy,
        artifact["unresolved_ambiguity_rate"],
        artifact["no_candidate_rate"],
    )
    issue = _record_history(args, failed, row)
    status = issue or (
        "accepted" if args.history_path and not failed else "not_recorded"
    )
    artifact["history_status"] = status
    artifact["gate_outcomes"]["hard"]["history_persistence"] = (
        "fail" if issue else "pass"
    )
    return issue


def main() -> int:
    """Verify fixtures and emit the routing-quality artifact."""
    args = parse_args()
    fixtures = _load_routes(args.fixtures)
    if fixtures is None:
        return 1
    active_policy = policy_identity()
    route = _evaluate_routes(fixtures, active_policy)
    goal = _evaluate_goals(args.goal_fixtures, active_policy)
    results = route[0] + goal[0]
    statuses, failures = route[1] + goal[1], route[2] + goal[2]
    counters = statuses, failures, route[3], route[4], route[5] + goal[3]
    artifact = _artifact(args, active_policy, results, counters)
    history_issue = _apply_history_outcome(args, results, artifact, active_policy)
    args.artifact.parent.mkdir(parents=True, exist_ok=True)
    args.artifact.write_text(
        json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return _report(args, active_policy, results, artifact, history_issue)


if __name__ == "__main__":
    raise SystemExit(main())
