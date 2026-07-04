#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from oss_minimum_io import load_json_object


DEFAULT_BLOCKED_NEXT_GATES = [
    "oss-local-full-release-expansion",
    "oss-cloud",
    "tessl-dry-run",
    "tessl-live",
]
DEFAULT_BLOCKED_NEXT_GATES_BY_PROFILE = {
    "oss-local": DEFAULT_BLOCKED_NEXT_GATES,
    "oss-cloud": [
        "oss-local-full-release-expansion",
        "tessl-dry-run",
        "tessl-live",
    ],
}


@dataclass(frozen=True)
class CaseEvidence:
    case_id: str
    bucket: str
    status: str
    run_id: str | None
    scorecard_path: str | None
    workflow_closeout_path: str | None
    workflow_closeout_status: str | None
    workflow_closeout_validation_status: str | None
    result_path: str | None
    blocker_class: str | None
    failures: list[str]
    codex_exec_invoked: bool | None
    trace_total_tokens: int | None


def _case_status(raw_case: dict[str, Any]) -> str:
    if raw_case.get("passed") is True or raw_case.get("status") == "pass":
        return "pass"
    if raw_case.get("blocked") is True or raw_case.get("status") == "blocked":
        return "blocked"
    return "fail"


def _runner_codex_exec(raw_case: dict[str, Any]) -> bool | None:
    runners = raw_case.get("runners")
    if not isinstance(runners, dict):
        return None
    codex = runners.get("codex")
    if not isinstance(codex, dict):
        return None
    return codex.get("exit_code") is not None


def _runner_total_tokens(raw_case: dict[str, Any]) -> int | None:
    runners = raw_case.get("runners")
    codex = runners.get("codex") if isinstance(runners, dict) else None
    metrics = codex.get("metrics") if isinstance(codex, dict) else None
    trace = metrics.get("trace") if isinstance(metrics, dict) else None
    usage = trace.get("token_usage") if isinstance(trace, dict) else None
    total = usage.get("total_tokens") if isinstance(usage, dict) else None
    return total if isinstance(total, int) and not isinstance(total, bool) else None


def _closeout_case(closeout: dict[str, Any], case_id: str) -> dict[str, Any] | None:
    cases = closeout.get("cases")
    if not isinstance(cases, list):
        return None
    for raw_case in cases:
        if isinstance(raw_case, dict) and raw_case.get("id") == case_id:
            return raw_case
    return None


def _workflow_validation_status(closeout: dict[str, Any]) -> str | None:
    validation = closeout.get("closeout_validation")
    status = validation.get("status") if isinstance(validation, dict) else None
    return status if isinstance(status, str) else None


def _blocked_by_closeout_validation(status: str | None) -> bool:
    return status != "pass"


def _case_satisfies_gate(case: CaseEvidence) -> bool:
    return case.status == "pass" and not _blocked_by_closeout_validation(
        case.workflow_closeout_validation_status
    )


def collect_case_evidence(artifacts_root: Path, case_id: str, bucket: str) -> CaseEvidence:
    latest: CaseEvidence | None = None
    for scorecard_path in sorted(artifacts_root.glob("*/scorecard.json")):
        scorecard = load_json_object(scorecard_path)
        run_id = str(scorecard.get("run_id") or scorecard_path.parent.name)
        closeout_path = scorecard_path.with_name("workflow-closeout.json")
        closeout = load_json_object(closeout_path) if closeout_path.is_file() else {}
        closeout_case = _closeout_case(closeout, case_id)
        for raw_case in scorecard.get("cases") or []:
            if not isinstance(raw_case, dict) or raw_case.get("id") != case_id:
                continue
            status = _case_status(raw_case)
            if closeout_case and closeout_case.get("status") in {"pass", "fail", "blocked"}:
                status = str(closeout_case["status"])
            workflow_validation_status = _workflow_validation_status(closeout)
            failures = [str(item) for item in raw_case.get("tier1_failures") or []]
            blocker_class = str(raw_case.get("blocker_class")) if raw_case.get("blocker_class") else None
            if _blocked_by_closeout_validation(workflow_validation_status):
                status = "blocked"
                blocker_class = blocker_class or (
                    "workflow_closeout_validation_missing"
                    if workflow_validation_status is None
                    else "workflow_closeout_validation_not_pass"
                )
                failures.append(
                    f"workflow-closeout validation status is {workflow_validation_status}; expected pass."
                )
            latest = CaseEvidence(
                case_id=case_id,
                bucket=bucket,
                status=status,
                run_id=run_id,
                scorecard_path=str(scorecard_path),
                workflow_closeout_path=str(closeout_path) if closeout_path.is_file() else None,
                workflow_closeout_status=str(closeout.get("status")) if closeout.get("status") else None,
                workflow_closeout_validation_status=workflow_validation_status,
                result_path=_optional_str(
                    raw_case.get("dir")
                    or (closeout_case.get("result_path") if closeout_case else None)
                ),
                blocker_class=blocker_class,
                failures=failures,
                codex_exec_invoked=_runner_codex_exec(raw_case),
                trace_total_tokens=_runner_total_tokens(raw_case),
            )
    if latest:
        return latest
    return CaseEvidence(
        case_id=case_id,
        bucket=bucket,
        status="missing",
        run_id=None,
        scorecard_path=None,
        workflow_closeout_path=None,
        workflow_closeout_status=None,
        workflow_closeout_validation_status=None,
        result_path=None,
        blocker_class="missing_case_evidence",
        failures=["No scorecard case evidence found for selected case."],
        codex_exec_invoked=None,
        trace_total_tokens=None,
    )


def build_proof_set(
    *,
    skill: str,
    artifacts_root: Path,
    core_cases: list[str],
    regression_cases: list[str],
    codex_profile: str,
    model: str | None,
    policy: str | None = None,
    blocked_next_gates: list[str],
    shard_size_limit: int | None = None,
) -> dict[str, Any]:
    cases = [
        collect_case_evidence(artifacts_root, case_id, "core") for case_id in core_cases
    ] + [
        collect_case_evidence(artifacts_root, case_id, "regression") for case_id in regression_cases
    ]
    summary = {
        "case_count": len(cases),
        "pass_count": sum(1 for case in cases if case.status == "pass"),
        "blocked_count": sum(1 for case in cases if case.status == "blocked"),
        "fail_count": sum(1 for case in cases if case.status == "fail"),
        "missing_count": sum(1 for case in cases if case.status == "missing"),
    }
    gate_status = (
        "pass"
        if summary["case_count"] > 0 and all(_case_satisfies_gate(case) for case in cases)
        else "blocked"
    )
    later_lane_notes = {
        "oss-local": "It does not prove the full release lane, oss-cloud, Tessl dry-run, Tessl live, CI, merge, publish, or release readiness.",
        "oss-cloud": "It does not prove the full release lane, Tessl dry-run, Tessl live, CI, merge, publish, or release readiness.",
    }
    return {
        "schema_version": "oss-minimum-proof-set/v1",
        "gate_status": gate_status,
        "skill": skill,
        "codex_profile": codex_profile,
        "model": model,
        "policy": policy or "unspecified",
        "shard_size_limit": shard_size_limit,
        "summary": summary,
        "blocked_next_gates": blocked_next_gates,
        "cases": [
            {
                "case_id": case.case_id,
                "bucket": case.bucket,
                "required": True,
                "latest_evidence": {
                    "status": case.status,
                    "run_id": case.run_id,
                    "scorecard_path": case.scorecard_path,
                    "workflow_closeout_path": case.workflow_closeout_path,
                    "workflow_closeout_status": case.workflow_closeout_status,
                    "workflow_closeout_validation_status": case.workflow_closeout_validation_status,
                    "result_path": case.result_path,
                    "blocker_class": case.blocker_class,
                    "failures": case.failures,
                    "codex_exec_invoked": case.codex_exec_invoked,
                    "trace_total_tokens": case.trace_total_tokens,
                },
            }
            for case in cases
        ],
        "notes": [
            f"This artifact scopes Jamie's immediate OSS start gate to {len(core_cases)} core plus {len(regression_cases)} regression cases.",
            later_lane_notes.get(
                codex_profile,
                "It does not prove the full release lane, later OSS lanes, Tessl dry-run, Tessl live, CI, merge, publish, or release readiness.",
            ),
            "Evidence is populated from scorecard.json and workflow-closeout.json receipts under the selected artifacts root.",
        ],
    }


def default_blocked_next_gates(codex_profile: str) -> list[str]:
    return list(DEFAULT_BLOCKED_NEXT_GATES_BY_PROFILE.get(codex_profile, DEFAULT_BLOCKED_NEXT_GATES))


def _optional_str(value: object) -> str | None:
    return str(value) if value is not None else None


def _load_policy_cases(policy_file: Path | None, proof_set_id: str | None) -> tuple[str | None, str | None, list[str], list[str], int | None]:
    if not policy_file:
        return None, None, [], [], None
    payload = load_json_object(policy_file)
    proof_sets = payload.get("proof_sets")
    if not isinstance(proof_sets, dict):
        return None, None, [], [], None
    selected_id = proof_set_id or next(iter(proof_sets), None)
    selected = proof_sets.get(selected_id) if isinstance(selected_id, str) else None
    if not isinstance(selected, dict):
        return None, None, [], [], None
    skill = selected.get("skill")
    policy = selected.get("policy")
    core_cases = selected.get("core_cases")
    regression_cases = selected.get("regression_cases")
    shard_size_limit = selected.get("shard_size_limit")
    return (
        skill if isinstance(skill, str) else None,
        policy if isinstance(policy, str) else None,
        [str(case_id) for case_id in core_cases or [] if str(case_id).strip()],
        [str(case_id) for case_id in regression_cases or [] if str(case_id).strip()],
        shard_size_limit if isinstance(shard_size_limit, int) and not isinstance(shard_size_limit, bool) else None,
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build an OSS minimum proof-set receipt from eval artifacts.")
    parser.add_argument("skill")
    parser.add_argument("--artifacts-root", required=True, type=Path)
    parser.add_argument("--policy-file", type=Path)
    parser.add_argument("--proof-set-id")
    parser.add_argument("--core-case", action="append", default=[])
    parser.add_argument("--regression-case", action="append", default=[])
    parser.add_argument("--codex-profile", default="oss-local")
    parser.add_argument("--model")
    parser.add_argument("--blocked-next-gate", action="append")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    policy_skill, policy_label, policy_core_cases, policy_regression_cases, shard_size_limit = _load_policy_cases(
        args.policy_file,
        args.proof_set_id,
    )
    core_cases = args.core_case or policy_core_cases
    regression_cases = args.regression_case or policy_regression_cases
    skill = policy_skill or args.skill
    receipt = build_proof_set(
        skill=skill,
        artifacts_root=args.artifacts_root,
        core_cases=core_cases,
        regression_cases=regression_cases,
        codex_profile=args.codex_profile,
        model=args.model,
        policy=policy_label,
        blocked_next_gates=args.blocked_next_gate or default_blocked_next_gates(args.codex_profile),
        shard_size_limit=shard_size_limit,
    )
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.json or not args.output:
        print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if receipt["gate_status"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
