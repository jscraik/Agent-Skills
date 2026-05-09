#!/usr/bin/env python3
"""Run HE lifecycle evals with explicit smoke, slice, and release lanes."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path


DEFAULT_SKILLS = (
    "he-router",
    "he-spec",
    "he-code-review",
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


def _append_repeatable_filter(cmd: list[str], flag: str, values: tuple[str, ...]) -> None:
    for value in values:
        cmd.extend([flag, value])


def _ask_unavailable_reason(repo_root: Path) -> str | None:
    ask_path = repo_root / "bin" / "ask"
    if not ask_path.exists():
        return "./bin/ask is missing"
    if not ask_path.is_file():
        return "./bin/ask is not a file"
    if not os.access(ask_path, os.X_OK):
        return "./bin/ask is not executable"
    return None


def _blocked_result(
    *,
    skill_name: str,
    mode: str,
    runner: str,
    command: list[str],
    message: str,
    started_at: float,
) -> dict[str, object]:
    return {
        "skill": skill_name,
        "mode": mode,
        "runner": runner,
        "command": " ".join(command),
        "returncode": 126,
        "duration_seconds": round(time.time() - started_at, 3),
        "status": "blocked",
        "decision": "blocked",
        "errors": [{"code": "ERR_ASK_UNAVAILABLE", "message": message}],
        "raw_output": "",
        "raw_error": "",
    }


def _run_ask_eval(
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
    unavailable_reason = _ask_unavailable_reason(repo_root)
    if unavailable_reason:
        return _blocked_result(
            skill_name=skill_name,
            mode=mode,
            runner="ask",
            command=cmd,
            message=unavailable_reason,
            started_at=started_at,
        )
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
    except FileNotFoundError as error:
        return _blocked_result(
            skill_name=skill_name,
            mode=mode,
            runner="ask",
            command=cmd,
            message=f"./bin/ask could not be executed: {error}",
            started_at=started_at,
        )
    except PermissionError as error:
        return _blocked_result(
            skill_name=skill_name,
            mode=mode,
            runner="ask",
            command=cmd,
            message=f"./bin/ask could not be executed: {error}",
            started_at=started_at,
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
            "runner": "ask",
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
        "runner": "ask",
        "command": " ".join(cmd),
        "returncode": process.returncode,
        "duration_seconds": duration_seconds,
        "status": parsed.get("status"),
        "errors": parsed.get("errors", []),
        "raw_output": process.stdout,
        "raw_error": process.stderr,
    }


def _run_skill_builder_eval(
    repo_root: Path,
    skill_name: str,
    mode: str,
    runner: str,
    cases: tuple[str, ...],
    categories: tuple[str, ...],
    per_skill_timeout_sec: int | None,
    model: str | None,
    timeout_profile: str | None,
) -> dict[str, object]:
    skill_path = Path("Plugins") / "harness-engineering" / "skills" / skill_name
    cmd = [
        sys.executable,
        str(
            repo_root
            / "Plugins"
            / "skill-factory"
            / "skills"
            / "code_quality_review"
            / "skill-builder"
            / "scripts"
            / "run_skill_evals.py"
        ),
        str(skill_path),
        "--eval-mode",
        mode,
        "--runner",
        runner,
        "--format",
        "json",
    ]
    _append_repeatable_filter(cmd, "--case", cases)
    _append_repeatable_filter(cmd, "--category", categories)
    if per_skill_timeout_sec:
        cmd.extend(["--timeout-sec", str(per_skill_timeout_sec)])
    if model:
        cmd.extend(["--model", model])
    if timeout_profile:
        cmd.extend(["--timeout-profile", timeout_profile])

    started_at = time.time()
    print(
        f"RUNNING {skill_name} {mode} runner={runner} "
        f"cases={','.join(cases) or '*'} categories={','.join(categories) or '*'}",
        file=sys.stderr,
        flush=True,
    )
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
            f"TIMEOUT {skill_name} {mode} runner={runner} "
            f"timeout_seconds={timeout} duration_seconds={duration_seconds}",
            file=sys.stderr,
            flush=True,
        )
        return {
            "skill": skill_name,
            "mode": mode,
            "runner": runner,
            "command": " ".join(cmd),
            "returncode": 124,
            "duration_seconds": duration_seconds,
            "timeout_seconds": timeout,
            "status": "timeout",
            "decision": "timeout",
            "errors": [{"code": "ERR_TIMEOUT", "message": f"timed out after {timeout} seconds"}],
            "raw_output": error.stdout or "",
            "raw_error": error.stderr or "",
        }

    parsed = parse_result(process.stdout)
    duration_seconds = round(time.time() - started_at, 3)
    decision = parsed.get("decision")
    status = "success" if process.returncode == 0 and decision == "pass" else "error"
    print(
        f"DONE {skill_name} {mode} runner={runner} decision={decision} "
        f"returncode={process.returncode} duration_seconds={duration_seconds}",
        file=sys.stderr,
        flush=True,
    )
    return {
        "skill": skill_name,
        "mode": mode,
        "runner": runner,
        "command": " ".join(cmd),
        "returncode": process.returncode,
        "duration_seconds": duration_seconds,
        "status": status,
        "decision": decision,
        "tier1_failures": parsed.get("tier1_failures"),
        "tier2_findings": parsed.get("tier2_findings"),
        "case_filters": parsed.get("case_filters", []),
        "category_filters": parsed.get("category_filters", []),
        "artifacts": parsed.get("artifacts", {}),
        "errors": [] if status == "success" else [{"code": "ERR_VALIDATION", "message": "Evaluation run failed."}],
        "raw_output": process.stdout,
        "raw_error": process.stderr,
    }


def run_skill(
    repo_root: Path,
    skill_name: str,
    mode: str,
    eval_runner: str,
    cases: tuple[str, ...],
    categories: tuple[str, ...],
    per_skill_timeout_sec: int | None,
    model: str | None,
    timeout_profile: str | None,
) -> dict[str, object]:
    if eval_runner == "ask":
        if cases or categories or model or timeout_profile:
            return {
                "skill": skill_name,
                "mode": mode,
                "runner": "ask",
                "returncode": 2,
                "duration_seconds": 0,
                "status": "error",
                "errors": [
                    {
                        "code": "ERR_UNSUPPORTED_FILTER",
                        "message": "Use --eval-runner codex when case, category, model, or timeout-profile filters are required.",
                    }
                ],
                "raw_output": "",
                "raw_error": "",
            }
        return _run_ask_eval(repo_root, skill_name, mode, per_skill_timeout_sec)
    return _run_skill_builder_eval(
        repo_root,
        skill_name,
        mode,
        eval_runner,
        cases,
        categories,
        per_skill_timeout_sec,
        model,
        timeout_profile,
    )


def run_router_sample_gate(repo_root: Path, timeout_sec: int = 300) -> dict[str, object]:
    cmd = [
        sys.executable,
        str(
            repo_root
            / "Plugins"
            / "harness-engineering"
            / "scripts"
            / "validate_routing_map.py"
        ),
        "--run-router-samples",
        "--json",
    ]
    started_at = time.time()
    try:
        process = subprocess.run(
            cmd,
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
        )
    except subprocess.TimeoutExpired as error:
        return {
            "required": True,
            "gate": "router_samples",
            "command": " ".join(cmd),
            "returncode": 124,
            "duration_seconds": round(time.time() - started_at, 3),
            "timeout_seconds": timeout_sec,
            "status": "timeout",
            "errors": [{"code": "ERR_TIMEOUT", "message": f"timed out after {timeout_sec} seconds"}],
            "raw_output": error.stdout or "",
            "raw_error": error.stderr or "",
        }

    parsed = parse_result(process.stdout)
    return {
        "required": True,
        "gate": "router_samples",
        "command": " ".join(cmd),
        "returncode": process.returncode,
        "duration_seconds": round(time.time() - started_at, 3),
        "status": "pass" if process.returncode == 0 and parsed.get("status") == "pass" else "fail",
        "errors": parsed.get("errors", []),
        "warnings": parsed.get("warnings", []),
        "raw_output": process.stdout,
        "raw_error": process.stderr,
    }


def summarize(
    results: list[dict[str, object]],
    *,
    router_sample_gate: dict[str, object] | None = None,
) -> dict[str, object]:
    failing = [
        result
        for result in results
        if result.get("returncode") != 0 or result.get("status") != "success"
    ]
    failing_gates: list[str] = []
    if router_sample_gate is not None and (
        router_sample_gate.get("returncode") != 0 or router_sample_gate.get("status") != "pass"
    ):
        failing_gates.append("router_samples")
    return {
        "schema_version": 1,
        "gate": "harness-engineering-lifecycle-evals",
        "status": "pass" if not failing and not failing_gates else "fail",
        "skills": [result["skill"] for result in results],
        "results": results,
        "failing_skills": [result["skill"] for result in failing],
        "failing_gates": failing_gates,
        "router_sample_gate": router_sample_gate,
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
    parser.add_argument(
        "--eval-runner",
        choices=("ask", "codex"),
        default="ask",
        help=(
            "Runner surface. `ask` preserves the legacy wrapper and runs every case. "
            "`codex` calls the skill-builder runner directly and supports case/category slicing."
        ),
    )
    parser.add_argument(
        "--case",
        action="append",
        help="Run matching eval case ids/names. Repeat or pass comma-separated values.",
    )
    parser.add_argument(
        "--category",
        action="append",
        choices=("happy", "edge", "negative", "pressure"),
        help="Run matching eval categories. Repeat for multiple categories.",
    )
    parser.add_argument("--model", help="Model override for direct Codex eval runner.")
    parser.add_argument(
        "--timeout-profile",
        choices=("default", "codex-heavy", "discovery-heavy"),
        help="Timeout profile for direct Codex eval runner.",
    )
    parser.add_argument(
        "--require-router-samples",
        action="store_true",
        help="Fail release confidence unless router sample execution passes.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON only.")
    args = parser.parse_args()

    repo_root = repo_root_from_script()
    selected_skills = tuple(args.skill) if args.skill else DEFAULT_SKILLS
    cases = tuple(
        item.strip()
        for value in (args.case or [])
        for item in value.split(",")
        if item.strip()
    )
    categories = tuple(args.category or ())
    results = [
        run_skill(
            repo_root,
            skill,
            args.mode,
            args.eval_runner,
            cases,
            categories,
            args.per_skill_timeout_sec,
            args.model,
            args.timeout_profile,
        )
        for skill in selected_skills
    ]
    router_sample_gate = run_router_sample_gate(repo_root) if args.require_router_samples else None
    summary = summarize(results, router_sample_gate=router_sample_gate)

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
