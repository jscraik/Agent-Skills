#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SOURCE = "Plugins/skill-factory/skills/code_quality_review/skill-builder"
HANDLE = "skill-builder"
WORKOUT = "skill-factory/skill-builder-sdk-pipeline"


def run_json(command: list[str]) -> dict:
    try:
        result = subprocess.run(
            command,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        print(f"command_timed_out: {' '.join(command)}", file=sys.stderr)
        raise SystemExit(1) from exc
    if result.returncode != 0:
        print(f"command_failed: {' '.join(command)}", file=sys.stderr)
        print(result.stdout, file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        raise SystemExit(1)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        print(f"invalid_json: {' '.join(command)}: {exc}", file=sys.stderr)
        print(result.stdout, file=sys.stderr)
        raise SystemExit(1) from exc


def data(payload: dict, *keys: str) -> object:
    current: object = payload
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            print(f"missing_json_key: {'.'.join(keys)}", file=sys.stderr)
            raise SystemExit(1)
        current = current[key]
    return current


def assert_strict_audit() -> None:
    audit = run_json([
        "./bin/ask",
        "skills",
        "audit",
        SOURCE,
        "--level",
        "strict",
        "--json",
        "--robot",
    ])
    if audit.get("status") != "success":
        print("strict_audit_not_success", file=sys.stderr)
        raise SystemExit(1)


def assert_package_pass() -> None:
    package = run_json([
        "./bin/ask",
        "skills",
        "package",
        SOURCE,
        "--checkout-test",
        "--strict",
        "--json",
        "--robot",
    ])
    package_data = data(package, "data", "skill_package")
    if not isinstance(package_data, dict) or package_data.get("status") != "pass":
        print("package_status_not_pass", file=sys.stderr)
        raise SystemExit(1)


def assert_runtime_proof_pass() -> None:
    proof = run_json(["./bin/ask", "skills", "proof", HANDLE, "--json", "--robot"])
    proof_data = data(proof, "data", "proof")
    if not isinstance(proof_data, dict) or proof_data.get("status") != "pass":
        print("runtime_proof_not_pass", file=sys.stderr)
        raise SystemExit(1)
    gates = proof_data.get("gates")
    if not isinstance(gates, dict) or not gates.get("user_runtime_ready"):
        print("user_runtime_not_ready", file=sys.stderr)
        raise SystemExit(1)


def assert_workout_candidate_available() -> None:
    scorecard = run_json(["./bin/ask", "skills", "prove", SOURCE, "--json", "--robot"])
    skill_proof = data(scorecard, "data", "skill_proof")
    if not isinstance(skill_proof, dict):
        print("skill_proof_not_mapping", file=sys.stderr)
        raise SystemExit(1)
    if skill_proof.get("proof_status") != "reachable_without_outcome_proof":
        print("unexpected_proof_status", file=sys.stderr)
        raise SystemExit(1)
    outcome = skill_proof.get("outcome_proof")
    if not isinstance(outcome, dict):
        print("outcome_proof_not_mapping", file=sys.stderr)
        raise SystemExit(1)
    if outcome.get("status") != "available_not_run":
        print("outcome_candidate_not_available", file=sys.stderr)
        raise SystemExit(1)
    if WORKOUT not in outcome.get("workout_candidates", []):
        print("workout_candidate_missing", file=sys.stderr)
        raise SystemExit(1)


def main() -> int:
    state_dir_value = os.environ.get("WORKOUT_STATE_DIR")
    if not state_dir_value:
        print("WORKOUT_STATE_DIR environment variable is required", file=sys.stderr)
        return 1
    state_file = Path(state_dir_value) / "sdk_pipeline.env"
    if not state_file.is_file():
        print("sdk_pipeline_state_missing", file=sys.stderr)
        return 1

    assert_strict_audit()
    assert_package_pass()
    assert_runtime_proof_pass()
    assert_workout_candidate_available()

    print("skill_builder_sdk_pipeline_workout_pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
