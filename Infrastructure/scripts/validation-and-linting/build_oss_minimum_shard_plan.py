#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from oss_minimum_io import load_json_object


def _selected_policy(policy_file: Path, proof_set_id: str | None) -> dict[str, Any]:
    payload = load_json_object(policy_file)
    proof_sets = payload.get("proof_sets")
    if not isinstance(proof_sets, dict):
        return {}
    selected_id = proof_set_id or next(iter(proof_sets), None)
    selected = proof_sets.get(selected_id) if isinstance(selected_id, str) else None
    return selected if isinstance(selected, dict) else {}


def _case_ids(policy: dict[str, Any]) -> list[str]:
    case_ids: list[str] = []
    for key in ("core_cases", "regression_cases"):
        raw_cases = policy.get(key)
        if not isinstance(raw_cases, list):
            continue
        for raw_case in raw_cases:
            case_id = str(raw_case).strip()
            if case_id and case_id not in case_ids:
                case_ids.append(case_id)
    return case_ids


def _case_statuses(proof_set: dict[str, Any] | None) -> dict[str, str]:
    if not isinstance(proof_set, dict):
        return {}
    statuses: dict[str, str] = {}
    cases = proof_set.get("cases")
    if not isinstance(cases, list):
        return statuses
    for case in cases:
        if not isinstance(case, dict):
            continue
        case_id = case.get("case_id")
        evidence = case.get("latest_evidence")
        status = evidence.get("status") if isinstance(evidence, dict) else None
        closeout_status = evidence.get("workflow_closeout_validation_status") if isinstance(evidence, dict) else None
        if isinstance(case_id, str) and case_id:
            statuses[case_id] = "pass" if status == "pass" and closeout_status == "pass" else str(status or "missing")
    return statuses


def _select_cases(case_ids: list[str], statuses: dict[str, str], selection: str) -> tuple[list[str], list[str]]:
    if selection == "all" or not statuses:
        return case_ids, []
    selected = [case_id for case_id in case_ids if statuses.get(case_id, "missing") != "pass"]
    skipped = [case_id for case_id in case_ids if statuses.get(case_id) == "pass"]
    return selected, skipped


def _chunks(items: list[str], size: int) -> list[list[str]]:
    return [items[index : index + size] for index in range(0, len(items), size)]


def _command_for_shard(skill: str, *, mode: str, codex_profile: str, timeout_seconds: int, cases: list[str]) -> str:
    args = [
        "./bin/ask",
        "sdk",
        "eval",
        "run",
        skill,
        "--runner",
        "internal",
        "--mode",
        mode,
        "--codex-profile",
        codex_profile,
        "--timeout-seconds",
        str(timeout_seconds),
    ]
    for case_id in cases:
        args.extend(["--case", case_id])
    args.extend(["--json", "--robot"])
    return " ".join(args)


def build_shard_plan(
    *,
    policy_file: Path,
    proof_set_id: str | None,
    codex_profile: str,
    mode: str,
    timeout_seconds: int,
    proof_set_receipt: Path | None = None,
    run_selection: str = "missing-or-blocked",
) -> dict[str, Any]:
    policy = _selected_policy(policy_file, proof_set_id)
    all_case_ids = _case_ids(policy)
    case_statuses = _case_statuses(load_json_object(proof_set_receipt) if proof_set_receipt else None)
    case_ids, skipped_case_ids = _select_cases(all_case_ids, case_statuses, run_selection)
    plan_context = _plan_context(policy, codex_profile=codex_profile, mode=mode)
    shards = _shards(case_ids=case_ids, timeout_seconds=timeout_seconds, **plan_context)
    return _plan_receipt(
        policy_file=policy_file,
        proof_set_id=proof_set_id,
        policy=policy,
        codex_profile=codex_profile,
        mode=mode,
        timeout_seconds=timeout_seconds,
        case_ids=case_ids,
        all_case_ids=all_case_ids,
        skipped_case_ids=skipped_case_ids,
        shards=shards,
        plan_context=plan_context,
        run_selection=run_selection,
    )


def _plan_context(policy: dict[str, Any], *, codex_profile: str, mode: str) -> dict[str, Any]:
    return {
        "skill": str(policy.get("skill") or ""),
        "shard_size": _shard_size(policy),
        "mode": mode,
        "codex_profile": codex_profile,
        "timeout_profile": _timeout_profile(policy, codex_profile=codex_profile, mode=mode),
    }


def _plan_receipt(
    *,
    policy_file: Path,
    proof_set_id: str | None,
    policy: dict[str, Any],
    codex_profile: str,
    mode: str,
    timeout_seconds: int,
    case_ids: list[str],
    all_case_ids: list[str],
    skipped_case_ids: list[str],
    shards: list[dict[str, Any]],
    plan_context: dict[str, Any],
    run_selection: str,
) -> dict[str, Any]:
    return {
        "schema_version": "oss-minimum-shard-plan/v1",
        "policy_file": str(policy_file),
        "proof_set_id": proof_set_id,
        "policy": policy.get("policy"),
        "skill": str(policy.get("skill") or ""),
        "codex_profile": codex_profile,
        "mode": mode,
        "timeout_seconds": timeout_seconds,
        "timeout_profile": plan_context["timeout_profile"],
        "shard_size_limit": plan_context["shard_size"],
        "run_selection": run_selection,
        "case_count": len(case_ids),
        "policy_case_count": len(all_case_ids),
        "skipped_pass_case_count": len(skipped_case_ids),
        "skipped_pass_case_ids": skipped_case_ids,
        "shard_count": len(shards),
        "cost_projection": _cost_projection(case_ids, shards),
        "shards": shards,
        "notes": [
            "Shard commands are generated from the repo-owned OSS minimum proof-set policy.",
            "When proof_set_receipt is supplied, pass-valid cases are skipped unless run_selection=all.",
            "Run shards in order and rebuild the matching proof/comparison receipt after evidence exists.",
        ],
    }


def _shard_size(policy: dict[str, Any]) -> int:
    shard_size_limit = policy.get("shard_size_limit")
    if isinstance(shard_size_limit, int) and not isinstance(shard_size_limit, bool):
        return shard_size_limit
    return 1


def _timeout_profile(policy: dict[str, Any], *, codex_profile: str, mode: str) -> str | None:
    timeout_profiles = policy.get("timeout_profiles")
    if not isinstance(timeout_profiles, dict):
        return None
    raw_timeout_profile = timeout_profiles.get(codex_profile) or timeout_profiles.get(mode)
    return str(raw_timeout_profile) if raw_timeout_profile else None


def _shards(
    *,
    skill: str,
    case_ids: list[str],
    shard_size: int,
    mode: str,
    codex_profile: str,
    timeout_seconds: int,
    timeout_profile: str | None,
) -> list[dict[str, Any]]:
    return [
        _shard(
            index=index,
            skill=skill,
            cases=cases,
            mode=mode,
            codex_profile=codex_profile,
            timeout_seconds=timeout_seconds,
            timeout_profile=timeout_profile,
        )
        for index, cases in enumerate(_chunks(case_ids, shard_size), start=1)
    ]


def _shard(
    *,
    index: int,
    skill: str,
    cases: list[str],
    mode: str,
    codex_profile: str,
    timeout_seconds: int,
    timeout_profile: str | None,
) -> dict[str, Any]:
    return {
        "index": index,
        "case_count": len(cases),
        "case_ids": cases,
        "timeout_profile": timeout_profile,
        "command": _command_for_shard(
            skill,
            mode=mode,
            codex_profile=codex_profile,
            timeout_seconds=timeout_seconds,
            cases=cases,
        ),
    }


def _cost_projection(case_ids: list[str], shards: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": "skills-sdk.oss-run-budget-preflight.v1",
        "selected_case_count": len(case_ids),
        "expected_solution_runs": len(case_ids),
        "expected_score_runs": 0,
        "expected_model_tasks": len(case_ids),
        "shard_count": len(shards),
        "status": "pass",
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build shard commands for an OSS minimum proof-set policy.")
    parser.add_argument("--policy-file", required=True, type=Path)
    parser.add_argument("--proof-set-id")
    parser.add_argument("--codex-profile", required=True)
    parser.add_argument("--mode", default="release")
    parser.add_argument("--timeout-seconds", type=int, default=120)
    parser.add_argument("--proof-set-receipt", type=Path)
    parser.add_argument("--run-selection", choices=["missing-or-blocked", "all"], default="missing-or-blocked")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    receipt = build_shard_plan(
        policy_file=args.policy_file,
        proof_set_id=args.proof_set_id,
        codex_profile=args.codex_profile,
        mode=args.mode,
        timeout_seconds=args.timeout_seconds,
        proof_set_receipt=args.proof_set_receipt,
        run_selection=args.run_selection,
    )
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.json or not args.output:
        print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
