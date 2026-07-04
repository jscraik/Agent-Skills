#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from oss_minimum_io import file_sha256, load_json_object, stable_json_hash


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
    prompt_path: str | None
    prompt_bytes: int | None


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


def _prompt_path(scorecard_path: Path, raw_case: dict[str, Any], closeout_case: dict[str, Any] | None) -> Path | None:
    raw_result_path = raw_case.get("dir") or (closeout_case.get("result_path") if closeout_case else None)
    candidates: list[Path] = []
    if raw_result_path:
        candidates.append(Path(str(raw_result_path)) / "prompt.txt")
    candidates.append(scorecard_path.parent / "prompt.txt")
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def _file_size(path: Path | None) -> int | None:
    if path is None:
        return None
    try:
        return path.stat().st_size
    except OSError:
        return None


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


def _evidence_status(raw_status: str, workflow_validation_status: str | None) -> str:
    if raw_status != "pass":
        return raw_status
    return "pass" if workflow_validation_status == "pass" else "blocked"


def collect_case_evidence(artifacts_root: Path, case_id: str, bucket: str) -> CaseEvidence:
    latest: CaseEvidence | None = None
    for scorecard_path in sorted(artifacts_root.glob("*/scorecard.json")):
        latest = _latest_case_from_scorecard(scorecard_path, case_id, bucket) or latest
    return latest or _missing_case_evidence(case_id, bucket)


def _latest_case_from_scorecard(scorecard_path: Path, case_id: str, bucket: str) -> CaseEvidence | None:
    scorecard = load_json_object(scorecard_path)
    closeout_path = scorecard_path.with_name("workflow-closeout.json")
    closeout = load_json_object(closeout_path) if closeout_path.is_file() else {}
    closeout_case = _closeout_case(closeout, case_id)
    for raw_case in scorecard.get("cases") or []:
        if isinstance(raw_case, dict) and raw_case.get("id") == case_id:
            return _case_evidence_from_raw(
                scorecard_path=scorecard_path,
                scorecard=scorecard,
                closeout_path=closeout_path,
                closeout=closeout,
                closeout_case=closeout_case,
                raw_case=raw_case,
                case_id=case_id,
                bucket=bucket,
            )
    return None


def _case_evidence_from_raw(
    *,
    scorecard_path: Path,
    scorecard: dict[str, Any],
    closeout_path: Path,
    closeout: dict[str, Any],
    closeout_case: dict[str, Any] | None,
    raw_case: dict[str, Any],
    case_id: str,
    bucket: str,
) -> CaseEvidence:
    workflow_validation_status = _workflow_validation_status(closeout)
    prompt_path = _prompt_path(scorecard_path, raw_case, closeout_case)
    return CaseEvidence(
        case_id=case_id,
        bucket=bucket,
        status=_case_evidence_status(raw_case, closeout_case, workflow_validation_status),
        run_id=str(scorecard.get("run_id") or scorecard_path.parent.name),
        scorecard_path=str(scorecard_path),
        workflow_closeout_path=str(closeout_path) if closeout_path.is_file() else None,
        workflow_closeout_status=str(closeout.get("status")) if closeout.get("status") else None,
        workflow_closeout_validation_status=workflow_validation_status,
        result_path=_case_result_path(raw_case, closeout_case),
        blocker_class=str(raw_case.get("blocker_class")) if raw_case.get("blocker_class") else None,
        failures=[str(item) for item in raw_case.get("tier1_failures") or []],
        codex_exec_invoked=_runner_codex_exec(raw_case),
        trace_total_tokens=_runner_total_tokens(raw_case),
        prompt_path=str(prompt_path) if prompt_path else None,
        prompt_bytes=_file_size(prompt_path),
    )


def _case_evidence_status(
    raw_case: dict[str, Any],
    closeout_case: dict[str, Any] | None,
    workflow_validation_status: str | None,
) -> str:
    status = _case_status(raw_case)
    if closeout_case and closeout_case.get("status") in {"pass", "fail", "blocked"}:
        status = str(closeout_case["status"])
    return _evidence_status(status, workflow_validation_status)


def _case_result_path(raw_case: dict[str, Any], closeout_case: dict[str, Any] | None) -> str | None:
    return _optional_str(raw_case.get("dir") or (closeout_case.get("result_path") if closeout_case else None))


def _missing_case_evidence(case_id: str, bucket: str) -> CaseEvidence:
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
        prompt_path=None,
        prompt_bytes=None,
    )


def _runner_hash() -> str:
    script_path = Path(__file__)
    return file_sha256(script_path) or "unknown"


def _source_hash(skill: str) -> str | None:
    skill_path = Path(skill)
    if skill_path.is_dir():
        skill_path = skill_path / "SKILL.md"
    return file_sha256(skill_path)


def _criteria_hash(core_cases: list[str], regression_cases: list[str], policy: str | None) -> str:
    return stable_json_hash({
        "policy": policy or "unspecified",
        "core_cases": core_cases,
        "regression_cases": regression_cases,
    })


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
    cases = _collect_selected_cases(artifacts_root, core_cases, regression_cases)
    source_hash = _source_hash(skill)
    criteria_hash = _criteria_hash(core_cases, regression_cases, policy)
    runner_hash = _runner_hash()
    summary = _proof_summary(cases)
    gate_status = _proof_gate_status(summary)
    return _proof_receipt(
        skill=skill,
        codex_profile=codex_profile,
        model=model,
        policy=policy,
        shard_size_limit=shard_size_limit,
        blocked_next_gates=blocked_next_gates,
        cases=cases,
        summary=summary,
        hashes={"source": source_hash, "criteria": criteria_hash, "runner": runner_hash},
        case_counts={"core": len(core_cases), "regression": len(regression_cases)},
        gate_status=gate_status,
    )


def _collect_selected_cases(artifacts_root: Path, core_cases: list[str], regression_cases: list[str]) -> list[CaseEvidence]:
    return [
        collect_case_evidence(artifacts_root, case_id, "core") for case_id in core_cases
    ] + [
        collect_case_evidence(artifacts_root, case_id, "regression") for case_id in regression_cases
    ]


def _proof_summary(cases: list[CaseEvidence]) -> dict[str, int]:
    return {
        "case_count": len(cases),
        "pass_count": sum(1 for case in cases if case.status == "pass"),
        "blocked_count": sum(1 for case in cases if case.status == "blocked"),
        "fail_count": sum(1 for case in cases if case.status == "fail"),
        "missing_count": sum(1 for case in cases if case.status == "missing"),
    }


def _proof_gate_status(summary: dict[str, int]) -> str:
    return "pass" if summary["case_count"] > 0 and summary["pass_count"] == summary["case_count"] else "blocked"


def _proof_receipt(
    *,
    skill: str,
    codex_profile: str,
    model: str | None,
    policy: str | None,
    shard_size_limit: int | None,
    blocked_next_gates: list[str],
    cases: list[CaseEvidence],
    summary: dict[str, int],
    hashes: dict[str, str | None],
    case_counts: dict[str, int],
    gate_status: str,
) -> dict[str, Any]:
    return {
        "schema_version": "oss-minimum-proof-set/v1",
        "gate_status": gate_status,
        "skill": skill,
        "codex_profile": codex_profile,
        "model": model,
        "policy": policy or "unspecified",
        "shard_size_limit": shard_size_limit,
        "cache_contract": _cache_contract(hashes=hashes, model=model, codex_profile=codex_profile),
        "summary": summary,
        "blocked_next_gates": blocked_next_gates,
        "cases": [_case_receipt(case, hashes=hashes, model=model, codex_profile=codex_profile) for case in cases],
        "notes": _receipt_notes(codex_profile=codex_profile, case_counts=case_counts),
    }


def _cache_contract(*, hashes: dict[str, str | None], model: str | None, codex_profile: str) -> dict[str, Any]:
    return {
        "schema_version": "skills-sdk.eval-cache-index.v1",
        "source_hash": hashes["source"],
        "criteria_hash": hashes["criteria"],
        "runner_hash": hashes["runner"],
        "model": model,
        "codex_profile": codex_profile,
        "reuse_rule": "A case may reuse pass evidence only when source_hash, criteria_hash, runner_hash, model, codex_profile, case status, and closeout validation all match.",
    }


def _receipt_notes(*, codex_profile: str, case_counts: dict[str, int]) -> list[str]:
    return [
        f"This artifact scopes Jamie's immediate OSS start gate to {case_counts['core']} core plus {case_counts['regression']} regression cases.",
        _lane_boundary_note(codex_profile),
        "Evidence is populated from scorecard.json and workflow-closeout.json receipts under the selected artifacts root.",
        "Passing case evidence requires workflow-closeout closeout_validation.status=pass; missing, blocked, or failed closeout validation blocks promotion.",
    ]


def _lane_boundary_note(codex_profile: str) -> str:
    notes = {
        "oss-local": "It does not prove the full release lane, oss-cloud, Tessl dry-run, Tessl live, CI, merge, publish, or release readiness.",
        "oss-cloud": "It does not prove the full release lane, Tessl dry-run, Tessl live, CI, merge, publish, or release readiness.",
    }
    return notes.get(
        codex_profile,
        "It does not prove the full release lane, later OSS lanes, Tessl dry-run, Tessl live, CI, merge, publish, or release readiness.",
    )


def _case_receipt(
    case: CaseEvidence,
    *,
    hashes: dict[str, str | None],
    model: str | None,
    codex_profile: str,
) -> dict[str, Any]:
    return {
        "case_id": case.case_id,
        "bucket": case.bucket,
        "required": True,
        "latest_evidence": _case_latest_evidence(case),
        "cache_key": {
            "source_hash": hashes["source"],
            "criteria_hash": hashes["criteria"],
            "runner_hash": hashes["runner"],
            "model": model,
            "codex_profile": codex_profile,
            "case_id": case.case_id,
        },
    }


def _case_latest_evidence(case: CaseEvidence) -> dict[str, Any]:
    return {
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
        "prompt_path": case.prompt_path,
        "prompt_bytes": case.prompt_bytes,
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
