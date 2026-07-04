#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _selected_policy(policy_file: Path, proof_set_id: str | None) -> dict[str, Any]:
    payload = _load_json(policy_file)
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
) -> dict[str, Any]:
    policy = _selected_policy(policy_file, proof_set_id)
    skill = str(policy.get("skill") or "")
    shard_size_limit = policy.get("shard_size_limit")
    shard_size = shard_size_limit if isinstance(shard_size_limit, int) and not isinstance(shard_size_limit, bool) else 1
    case_ids = _case_ids(policy)
    shards = [
        {
            "index": index + 1,
            "case_count": len(cases),
            "case_ids": cases,
            "command": _command_for_shard(
                skill,
                mode=mode,
                codex_profile=codex_profile,
                timeout_seconds=timeout_seconds,
                cases=cases,
            ),
        }
        for index, cases in enumerate(_chunks(case_ids, shard_size))
    ]
    return {
        "schema_version": "oss-minimum-shard-plan/v1",
        "policy_file": str(policy_file),
        "proof_set_id": proof_set_id,
        "policy": policy.get("policy"),
        "skill": skill,
        "codex_profile": codex_profile,
        "mode": mode,
        "timeout_seconds": timeout_seconds,
        "shard_size_limit": shard_size,
        "case_count": len(case_ids),
        "shard_count": len(shards),
        "shards": shards,
        "notes": [
            "Shard commands are generated from the repo-owned OSS minimum proof-set policy.",
            "Run shards in order and rebuild the matching proof/comparison receipt after evidence exists.",
        ],
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build shard commands for an OSS minimum proof-set policy.")
    parser.add_argument("--policy-file", required=True, type=Path)
    parser.add_argument("--proof-set-id")
    parser.add_argument("--codex-profile", required=True)
    parser.add_argument("--mode", default="release")
    parser.add_argument("--timeout-seconds", type=int, default=120)
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
    )
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.json or not args.output:
        print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
