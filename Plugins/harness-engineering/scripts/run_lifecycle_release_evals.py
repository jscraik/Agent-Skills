#!/usr/bin/env python3
"""Run HE lifecycle release evals as one confidence gate."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path


DEFAULT_SKILLS = (
    "he-router",
    "he-strategy",
    "he-refactor",
    "he-linear-plan",
    "he-eval-report",
    "he-phase-heartbeat",
    "he-plan",
    "he-work",
)


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[3]


def parse_result(stdout: str) -> dict[str, object]:
    try:
        parsed = json.loads(stdout)
    except json.JSONDecodeError:
        return {"status": "unknown", "raw_json_parse_error": True}
    if isinstance(parsed, dict):
        return parsed
    return {"status": "unknown", "raw_json_type": type(parsed).__name__}


def run_skill(
    repo_root: Path,
    skill_name: str,
    mode: str,
    per_skill_timeout_sec: int | None,
) -> dict[str, object]:
    skill_path = Path("Plugins") / "harness-engineering" / "skills" / skill_name
    cmd = [
        str(repo_root / "bin" / "ask"),
        "evals",
        "run",
        str(skill_path),
        "--mode",
        mode,
        "--json",
    ]
    started_at = time.time()
    print(f"RUNNING {skill_name} {mode}", file=sys.stderr, flush=True)
    timeout = per_skill_timeout_sec or (21600 if mode == "release" else 10800)
    try:
        process = subprocess.run(
            cmd,
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as error:
        duration_seconds = round(time.time() - started_at, 3)
        print(
            f"TIMEOUT {skill_name} {mode} timeout_seconds={timeout} duration_seconds={duration_seconds}",
            file=sys.stderr,
            flush=True,
        )
        return {
            "skill": skill_name,
            "mode": mode,
            "command": " ".join(cmd),
            "returncode": 124,
            "duration_seconds": duration_seconds,
            "timeout_seconds": timeout,
            "status": "timeout",
            "errors": [{"code": "ERR_TIMEOUT", "message": f"timed out after {timeout} seconds"}],
            "raw_output": error.stdout or "",
            "raw_error": error.stderr or "",
        }
    parsed = parse_result(process.stdout)
    duration_seconds = round(time.time() - started_at, 3)
    status = parsed.get("status")
    print(
        f"DONE {skill_name} {mode} status={status} "
        f"returncode={process.returncode} duration_seconds={duration_seconds}",
        file=sys.stderr,
        flush=True,
    )
    return {
        "skill": skill_name,
        "mode": mode,
        "command": " ".join(cmd),
        "returncode": process.returncode,
        "duration_seconds": duration_seconds,
        "status": parsed.get("status"),
        "errors": parsed.get("errors", []),
        "raw_output": process.stdout,
        "raw_error": process.stderr,
    }


def summarize(results: list[dict[str, object]]) -> dict[str, object]:
    failing = [
        result
        for result in results
        if result.get("returncode") != 0 or result.get("status") != "success"
    ]
    return {
        "schema_version": 1,
        "gate": "harness-engineering-lifecycle-release-evals",
        "status": "pass" if not failing else "fail",
        "skills": [result["skill"] for result in results],
        "results": results,
        "failing_skills": [result["skill"] for result in failing],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        choices=("smoke", "release"),
        default="release",
        help="Eval mode to run for every selected lifecycle skill.",
    )
    parser.add_argument(
        "--skill",
        action="append",
        choices=DEFAULT_SKILLS,
        help="Run one selected lifecycle skill. Repeat for multiple skills.",
    )
    parser.add_argument(
        "--per-skill-timeout-sec",
        type=int,
        help="Override the default per-skill timeout. Useful for diagnosing hangs.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON only.")
    args = parser.parse_args()

    repo_root = repo_root_from_script()
    selected_skills = tuple(args.skill) if args.skill else DEFAULT_SKILLS
    results = [
        run_skill(repo_root, skill, args.mode, args.per_skill_timeout_sec)
        for skill in selected_skills
    ]
    summary = summarize(results)

    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(f"status: {summary['status']}")
        print(f"mode: {args.mode}")
        for result in results:
            print(f"{result['skill']}: {result['status']} ({result['returncode']})")
        if summary["failing_skills"]:
            print("failing_skills: " + ", ".join(summary["failing_skills"]))

    return 0 if summary["status"] == "pass" else 2


if __name__ == "__main__":
    sys.exit(main())
