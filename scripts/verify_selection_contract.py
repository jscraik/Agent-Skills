#!/usr/bin/env python3
"""Deterministic fixture verifier for selection contract behavior."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

import sys

sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "scripts" / "lib"))

from selection_policy import policy_identity
from ask.selection_contract import EligibleCandidate, build_decision_payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify deterministic selection contract fixtures.")
    parser.add_argument(
        "--fixtures",
        type=Path,
        default=REPO_ROOT / "tests" / "fixtures" / "selection-contract" / "route-fixtures.json",
        help="Path to route fixture file.",
    )
    parser.add_argument(
        "--artifact",
        type=Path,
        default=REPO_ROOT / "artifacts" / "validation" / "latest" / "routing-quality.json",
        help="Path to write routing quality artifact.",
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


def main() -> int:
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
    explainability_failures = 0
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

        explainability_issues = _check_explainability(decision)
        if explainability_issues:
            explainability_failures += 1
            issues.extend(explainability_issues)

        status_counter[str(decision["decision_status"])] += 1
        failure_key = decision.get("failure_class") or "none"
        failure_counter[str(failure_key)] += 1

        results.append(
            {
                "id": fixture_id,
                "decision_status": decision["decision_status"],
                "failure_class": decision.get("failure_class"),
                "passed": not issues,
                "issues": issues,
            }
        )

    failed = [item for item in results if not item["passed"]]
    artifact = {
        "schema_version": "routing-quality.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "policy_identity": active_policy_identity,
        "fixture_path": str(args.fixtures.relative_to(REPO_ROOT)) if args.fixtures.is_relative_to(REPO_ROOT) else str(args.fixtures),
        "totals": {
            "fixtures": len(results),
            "passed": len(results) - len(failed),
            "failed": len(failed),
            "explainability_failures": explainability_failures,
        },
        "status_counts": dict(status_counter),
        "failure_class_counts": dict(failure_counter),
        "explainability_complete": explainability_failures == 0,
        "fixtures": results,
    }

    args.artifact.parent.mkdir(parents=True, exist_ok=True)
    args.artifact.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"Selection contract fixtures: total={len(results)} failed={len(failed)}")
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
