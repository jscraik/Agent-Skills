#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from oss_minimum_io import load_json_object


BLOCKED_NEXT_GATES_WHEN_BLOCKED = ["oss-cloud-eval-run", "tessl-dry-run", "tessl-live"]
BLOCKED_NEXT_GATES_AFTER_PASS = ["tessl-dry-run", "tessl-live"]
DEFAULT_STAGE_MATURITY_EXPECTATIONS = {
    "oss-local": "repair loop",
    "oss-cloud": "uplift loop",
    "tessl": "confirmation loop",
}
DELTA_OWNERS = {
    "skill",
    "scenario",
    "rubric",
    "scorer",
    "runner",
    "runtime",
    "environment",
    "none",
}
MISSING_CLOUD_EVIDENCE_OWNER = "missing_cloud_evidence"
UNCLASSIFIED_DELTA_OWNER = "unclassified_delta"


def _case_status(case: dict[str, Any]) -> str:
    evidence = case.get("latest_evidence")
    if isinstance(evidence, dict):
        status = evidence.get("status")
        if isinstance(status, str) and status:
            return status
    return "missing"


def _cases_by_id(proof_set: dict[str, Any]) -> dict[str, dict[str, Any]]:
    cases = proof_set.get("cases")
    if not isinstance(cases, list):
        return {}
    mapped: dict[str, dict[str, Any]] = {}
    for case in cases:
        if not isinstance(case, dict):
            continue
        case_id = case.get("case_id")
        if isinstance(case_id, str) and case_id:
            mapped[case_id] = case
    return mapped


def _proof_set_gate_status(proof_set: dict[str, Any] | None) -> str:
    if not isinstance(proof_set, dict):
        return "missing"
    status = proof_set.get("gate_status")
    return status if isinstance(status, str) and status else "missing"


def _lane_score(proof_set: dict[str, Any] | None, *, lane: str) -> dict[str, Any]:
    cases = list(_cases_by_id(proof_set or {}).values())
    case_count = len(cases)
    status_counts = {
        "pass": sum(1 for case in cases if _case_status(case) == "pass"),
        "blocked": sum(1 for case in cases if _case_status(case) == "blocked"),
        "fail": sum(1 for case in cases if _case_status(case) == "fail"),
        "missing": sum(1 for case in cases if _case_status(case) == "missing"),
    }
    pass_rate = status_counts["pass"] / case_count if case_count else 0.0
    return {
        "schema_version": "oss-lane-score/v1",
        "lane": lane,
        "case_count": case_count,
        "pass_count": status_counts["pass"],
        "blocked_count": status_counts["blocked"],
        "fail_count": status_counts["fail"],
        "missing_count": status_counts["missing"],
        "pass_rate": round(pass_rate, 4),
        "gate_status": _proof_set_gate_status(proof_set),
    }


def _owner_for_delta(case_id: str, delta_owners: dict[str, str], *, has_cloud: bool, local_status: str, cloud_status: str) -> str:
    if not has_cloud:
        return MISSING_CLOUD_EVIDENCE_OWNER
    if local_status == cloud_status:
        return "none"
    owner = delta_owners.get(case_id)
    if owner in DELTA_OWNERS:
        return owner
    return UNCLASSIFIED_DELTA_OWNER


def _evidence_path(case: dict[str, Any] | None) -> Any:
    if not case:
        return None
    evidence = case.get("latest_evidence")
    return evidence.get("scorecard_path") if isinstance(evidence, dict) else None


def _comparison_row(
    *,
    case_id: str,
    local_case: dict[str, Any],
    cloud_case: dict[str, Any] | None,
    delta_owners: dict[str, str],
) -> dict[str, Any]:
    local_status = _case_status(local_case)
    cloud_status = _case_status(cloud_case) if cloud_case else "missing"
    owner = _owner_for_delta(
        case_id,
        delta_owners,
        has_cloud=cloud_case is not None,
        local_status=local_status,
        cloud_status=cloud_status,
    )
    return {
        "case_id": case_id,
        "bucket": local_case.get("bucket"),
        "oss_local_status": local_status,
        "oss_cloud_status": cloud_status,
        "delta": local_status != cloud_status,
        "owner_if_delta": owner,
        "local_evidence_path": _evidence_path(local_case),
        "cloud_evidence_path": _evidence_path(cloud_case),
    }


def _comparison_summary(comparisons: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "case_count": len(comparisons),
        "parity_count": sum(1 for item in comparisons if not item["delta"]),
        "delta_count": sum(1 for item in comparisons if item["delta"]),
        "missing_cloud_count": sum(1 for item in comparisons if item["oss_cloud_status"] == "missing"),
        "missing_delta_owner_count": _missing_owner_count(comparisons),
    }


def _missing_owner_count(comparisons: list[dict[str, Any]]) -> int:
    return sum(1 for item in comparisons if item["delta"] and item["owner_if_delta"] == UNCLASSIFIED_DELTA_OWNER)


def _input_gate_status(local_proof_set: dict[str, Any], cloud_proof_set: dict[str, Any] | None) -> tuple[str, str, str]:
    local_gate_status = _proof_set_gate_status(local_proof_set)
    cloud_gate_status = _proof_set_gate_status(cloud_proof_set)
    input_gate_status = "pass" if local_gate_status == "pass" and cloud_gate_status == "pass" else "blocked"
    return input_gate_status, local_gate_status, cloud_gate_status


def _comparison_status(summary: dict[str, int], input_gate_status: str) -> str:
    if summary["case_count"] <= 0 or summary["delta_count"] or summary["missing_delta_owner_count"]:
        return "blocked"
    return "pass" if input_gate_status == "pass" else "blocked"


def build_comparison(
    *,
    local_proof_set: dict[str, Any],
    cloud_proof_set: dict[str, Any] | None,
    delta_owners: dict[str, str],
    stage_maturity_expectations: dict[str, str] | None = None,
) -> dict[str, Any]:
    local_cases = _cases_by_id(local_proof_set)
    cloud_cases = _cases_by_id(cloud_proof_set or {})
    comparisons: list[dict[str, Any]] = []
    for case_id, local_case in local_cases.items():
        comparisons.append(_comparison_row(
            case_id=case_id,
            local_case=local_case,
            cloud_case=cloud_cases.get(case_id),
            delta_owners=delta_owners,
        ))
    summary = _comparison_summary(comparisons)
    input_gate_status, local_gate_status, cloud_gate_status = _input_gate_status(local_proof_set, cloud_proof_set)
    status = _comparison_status(summary, input_gate_status)
    return _comparison_receipt(
        local_proof_set=local_proof_set,
        cloud_proof_set=cloud_proof_set,
        comparisons=comparisons,
        summary=summary,
        status=status,
        input_gate_status=input_gate_status,
        local_gate_status=local_gate_status,
        cloud_gate_status=cloud_gate_status,
        stage_maturity_expectations=stage_maturity_expectations,
    )


def _comparison_receipt(
    *,
    local_proof_set: dict[str, Any],
    cloud_proof_set: dict[str, Any] | None,
    comparisons: list[dict[str, Any]],
    summary: dict[str, int],
    status: str,
    input_gate_status: str,
    local_gate_status: str,
    cloud_gate_status: str,
    stage_maturity_expectations: dict[str, str] | None,
) -> dict[str, Any]:
    return {
        "schema_version": "oss-minimum-comparison/v1",
        "status": status,
        "policy": local_proof_set.get("policy"),
        "skill": local_proof_set.get("skill"),
        "baseline_profile": local_proof_set.get("codex_profile"),
        "comparison_profile": (cloud_proof_set or {}).get("codex_profile", "oss-cloud"),
        "shard_size_limit": local_proof_set.get("shard_size_limit"),
        "summary": summary,
        "input_gate_status": input_gate_status,
        "input_gate_evidence": {
            "oss_local_gate_status": local_gate_status,
            "oss_cloud_gate_status": cloud_gate_status,
        },
        "lane_scores": {
            "oss-local": _lane_score(local_proof_set, lane="oss-local"),
            "oss-cloud": _lane_score(cloud_proof_set, lane="oss-cloud"),
        },
        "stage_maturity_expectations": stage_maturity_expectations or DEFAULT_STAGE_MATURITY_EXPECTATIONS,
        "comparisons": comparisons,
        "blocked_next_gates": BLOCKED_NEXT_GATES_AFTER_PASS if status == "pass" else BLOCKED_NEXT_GATES_WHEN_BLOCKED,
        "notes": [
            "This receipt compares the 15+5 oss-local minimum proof set against oss-cloud evidence.",
            "Missing cloud evidence blocks cloud eval promotion until the same selected cases have receipts.",
            "Comparison promotion requires both input proof-set gates to pass; parity alone is not sufficient.",
            "Every non-parity case must carry an owner before Tessl dry-run or live evaluation.",
        ],
    }


def _parse_owner_map(path: Path | None) -> dict[str, str]:
    if not path:
        return {}
    payload = load_json_object(path)
    raw = payload.get("delta_owners", payload)
    if not isinstance(raw, dict):
        return {}
    return {str(key): str(value) for key, value in raw.items()}


def _parse_stage_maturity_expectations(policy_file: Path | None, proof_set_id: str | None) -> dict[str, str]:
    if not policy_file:
        return DEFAULT_STAGE_MATURITY_EXPECTATIONS
    payload = load_json_object(policy_file)
    proof_sets = payload.get("proof_sets")
    if not isinstance(proof_sets, dict):
        return DEFAULT_STAGE_MATURITY_EXPECTATIONS
    selected_id = proof_set_id or next(iter(proof_sets), None)
    selected = proof_sets.get(selected_id) if isinstance(selected_id, str) else None
    if not isinstance(selected, dict):
        return DEFAULT_STAGE_MATURITY_EXPECTATIONS
    raw = selected.get("stage_maturity_expectations")
    if not isinstance(raw, dict):
        return DEFAULT_STAGE_MATURITY_EXPECTATIONS
    parsed = {str(key): str(value) for key, value in raw.items() if str(key).strip() and str(value).strip()}
    return parsed or DEFAULT_STAGE_MATURITY_EXPECTATIONS


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare oss-local and oss-cloud minimum proof-set receipts.")
    parser.add_argument("--oss-local-proof", required=True, type=Path)
    parser.add_argument("--oss-cloud-proof", type=Path)
    parser.add_argument("--policy-file", type=Path)
    parser.add_argument("--proof-set-id")
    parser.add_argument("--delta-owner-map", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    receipt = build_comparison(
        local_proof_set=load_json_object(args.oss_local_proof),
        cloud_proof_set=load_json_object(args.oss_cloud_proof) if args.oss_cloud_proof else None,
        delta_owners=_parse_owner_map(args.delta_owner_map),
        stage_maturity_expectations=_parse_stage_maturity_expectations(args.policy_file, args.proof_set_id),
    )
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.json or not args.output:
        print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if receipt["status"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
