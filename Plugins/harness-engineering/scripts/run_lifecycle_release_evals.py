#!/usr/bin/env python3
"""Run HE lifecycle evals with explicit smoke, slice, and release lanes."""

from __future__ import annotations

import argparse
import json
import os
import re
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

SELECTION_SIGNAL_WARNING_MARKERS = (
    "selection signal was unavailable",
    "skill selection signal not found",
)

TOOL_PREFLIGHT_ERROR_CODES = {
    "ERR_ASK_UNAVAILABLE",
    "ERR_CODEX_AUTH_UNAVAILABLE",
    "ERR_UNSUPPORTED_FILTER",
}

CODEX_AUTH_ERROR_MARKERS = (
    "missing authenticated codex state",
    "selected codex home is not logged in",
    "codex login status reported",
)

CODEX_RUNNER_PREFLIGHT_MARKERS = (
    "failed to initialize in-process app-server client",
    "operation not permitted",
    "no events found in jsonl trace",
    "produced no final output",
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


def _skill_builder_runner_path(repo_root: Path) -> Path:
    return (
        repo_root
        / "Plugins"
        / "skill-factory"
        / "skills"
        / "code_quality_review"
        / "skill-builder"
        / "scripts"
        / "run_skill_evals.py"
    )


def _skill_path(skill_name: str) -> Path:
    return Path("Plugins") / "harness-engineering" / "skills" / skill_name


def _classify_case_failures(parsed: dict[str, object]) -> dict[str, object]:
    timeout_cases: list[dict[str, object]] = []
    content_failure_cases: list[dict[str, object]] = []
    tool_preflight_cases: list[dict[str, object]] = []
    other_failure_cases: list[dict[str, object]] = []

    for case in parsed.get("cases", []):
        if not isinstance(case, dict):
            continue
        if case.get("passed") is True and case.get("tier1_failed") is not True:
            continue

        failures = case.get("tier1_failures") or []
        failure_strings = [str(failure) for failure in failures]
        case_summary = {
            "id": case.get("id"),
            "name": case.get("name"),
            "category": case.get("category"),
            "tier1_failures": failures,
        }
        if any("exit code: 124" in failure or "returncode=124" in failure for failure in failure_strings):
            timeout_cases.append(case_summary)
        elif _case_has_tool_preflight_signal(case, failure_strings):
            tool_preflight_cases.append(case_summary)
        elif any("regex failed" in failure for failure in failure_strings):
            content_failure_cases.append(case_summary)
        else:
            other_failure_cases.append(case_summary)

    return {
        "timeout_cases": timeout_cases,
        "content_failure_cases": content_failure_cases,
        "tool_preflight_cases": tool_preflight_cases,
        "other_failure_cases": other_failure_cases,
    }


def _case_has_tool_preflight_signal(case: dict[str, object], failure_strings: list[str]) -> bool:
    warning_strings = [str(warning) for warning in (case.get("warnings") or [])]
    combined = "\n".join([*failure_strings, *warning_strings]).lower()
    if (
        "codex returned non-zero exit code" in combined
        and any(marker in combined for marker in CODEX_RUNNER_PREFLIGHT_MARKERS)
    ):
        return True

    runners = case.get("runners")
    if not isinstance(runners, dict):
        return False
    for runner_result in runners.values():
        if not isinstance(runner_result, dict):
            continue
        artifacts = runner_result.get("artifacts")
        if not isinstance(artifacts, dict):
            continue
        stderr_path = artifacts.get("stderr")
        if not isinstance(stderr_path, str):
            continue
        try:
            stderr_text = Path(stderr_path).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if any(marker in stderr_text.lower() for marker in CODEX_RUNNER_PREFLIGHT_MARKERS):
            return True
    return False


def _iter_case_warnings(parsed: dict[str, object]) -> list[dict[str, object]]:
    warning_cases: list[dict[str, object]] = []
    for case in parsed.get("cases", []):
        if not isinstance(case, dict):
            continue
        warnings = [str(warning) for warning in (case.get("warnings") or [])]
        if not warnings:
            continue
        warning_cases.append(
            {
                "id": case.get("id"),
                "name": case.get("name"),
                "category": case.get("category"),
                "warnings": warnings,
            }
        )
    return warning_cases


def _selection_signal_warnings(parsed: dict[str, object]) -> list[dict[str, object]]:
    selected: list[dict[str, object]] = []
    for case in _iter_case_warnings(parsed):
        warnings = [str(warning) for warning in (case.get("warnings") or [])]
        if any(
            marker in warning.lower()
            for warning in warnings
            for marker in SELECTION_SIGNAL_WARNING_MARKERS
        ):
            selected.append(case)
    return selected


def _tool_preflight_errors(result: dict[str, object]) -> list[dict[str, object]]:
    errors: list[dict[str, object]] = []
    for error in result.get("errors", []) or []:
        if not isinstance(error, dict):
            continue
        code = str(error.get("code") or "")
        if code in TOOL_PREFLIGHT_ERROR_CODES:
            errors.append(error)
    raw_error = str(result.get("raw_error") or "")
    if any(marker in raw_error.lower() for marker in CODEX_AUTH_ERROR_MARKERS):
        errors.append(
            {
                "code": "ERR_CODEX_AUTH_UNAVAILABLE",
                "message": "Codex live eval runner could not access authenticated Codex state.",
            }
        )
    return errors


def _merged_case_failure_classification(results: list[dict[str, object]]) -> dict[str, object]:
    merged: dict[str, list[dict[str, object]]] = {
        "timeout_cases": [],
        "content_failure_cases": [],
        "tool_preflight_cases": [],
        "other_failure_cases": [],
    }
    for result in results:
        classification = result.get("failure_classification")
        if isinstance(classification, dict):
            for key in merged:
                values = classification.get(key)
                if isinstance(values, list):
                    merged[key].extend(value for value in values if isinstance(value, dict))
            continue

        if result.get("status") == "timeout" or result.get("returncode") == 124:
            case_filters = result.get("case_filters")
            case_id = case_filters[0] if isinstance(case_filters, list) and case_filters else None
            merged["timeout_cases"].append(
                {
                    "id": case_id,
                    "name": case_id,
                    "category": None,
                    "tier1_failures": [
                        f"runner timed out after {result.get('timeout_seconds')} seconds"
                    ],
                }
            )
        elif _tool_preflight_errors(result):
            case_filters = result.get("case_filters")
            case_id = case_filters[0] if isinstance(case_filters, list) and case_filters else None
            merged["tool_preflight_cases"].append(
                {
                    "id": case_id,
                    "name": case_id,
                    "category": None,
                    "tier1_failures": result.get("errors") or [],
                }
            )
        elif result.get("returncode") != 0 or result.get("status") != "success":
            case_filters = result.get("case_filters")
            case_id = case_filters[0] if isinstance(case_filters, list) and case_filters else None
            merged["other_failure_cases"].append(
                {
                    "id": case_id,
                    "name": case_id,
                    "category": None,
                    "tier1_failures": result.get("tier1_failures") or result.get("errors") or [],
                }
            )
    return merged


def _result_failure_class(result: dict[str, object]) -> str | None:
    if result.get("returncode") == 0 and result.get("status") == "success":
        return None
    if result.get("status") == "timeout" or result.get("returncode") == 124:
        return "timeout"
    if _tool_preflight_errors(result):
        return "tool_preflight"

    classification = result.get("failure_classification")
    if isinstance(classification, dict):
        if classification.get("content_failure_cases"):
            return "content"
        if classification.get("tool_preflight_cases"):
            return "tool_preflight"
        if classification.get("timeout_cases"):
            return "timeout"
    return "other"


def _failure_breakdown(results: list[dict[str, object]]) -> dict[str, object]:
    breakdown: dict[str, object] = {
        "timeout_failures": [],
        "content_failures": [],
        "tool_preflight_failures": [],
        "selection_signal_warnings": [],
        "other_failures": [],
    }

    for result in results:
        skill = result.get("skill")
        failure_class = _result_failure_class(result)
        classification = result.get("failure_classification")
        timeout_cases = (
            classification.get("timeout_cases", [])
            if isinstance(classification, dict)
            else []
        )
        content_cases = (
            classification.get("content_failure_cases", [])
            if isinstance(classification, dict)
            else []
        )
        tool_preflight_cases = (
            classification.get("tool_preflight_cases", [])
            if isinstance(classification, dict)
            else []
        )
        if failure_class == "timeout" or timeout_cases:
            breakdown["timeout_failures"].append(
                {
                    "skill": skill,
                    "returncode": result.get("returncode"),
                    "timeout_seconds": result.get("timeout_seconds"),
                    "duration_seconds": result.get("duration_seconds"),
                    "case_classification": timeout_cases,
                }
            )
        if failure_class == "content" or content_cases:
            breakdown["content_failures"].append(
                {
                    "skill": skill,
                    "cases": content_cases,
                }
            )
        if failure_class == "tool_preflight" or tool_preflight_cases:
            breakdown["tool_preflight_failures"].append(
                {
                    "skill": skill,
                    "errors": _tool_preflight_errors(result),
                    "case_classification": tool_preflight_cases,
                }
            )
        if (
            failure_class == "other"
            and not timeout_cases
            and not content_cases
            and not tool_preflight_cases
            and not _tool_preflight_errors(result)
        ):
            breakdown["other_failures"].append(
                {
                    "skill": skill,
                    "returncode": result.get("returncode"),
                    "status": result.get("status"),
                    "errors": result.get("errors", []),
                }
            )

        raw_output = result.get("raw_output")
        if isinstance(raw_output, str) and raw_output.strip():
            parsed = parse_result(raw_output)
            warnings = _selection_signal_warnings(parsed)
            if warnings:
                breakdown["selection_signal_warnings"].append(
                    {
                        "skill": skill,
                        "cases": warnings,
                    }
                )

    return breakdown


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
    skill_path = _skill_path(skill_name)
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
    codex_home: Path | None,
) -> dict[str, object]:
    skill_path = _skill_path(skill_name)
    cmd = [
        sys.executable,
        str(_skill_builder_runner_path(repo_root)),
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
    if codex_home and runner == "codex":
        cmd.extend(["--codex-home", str(codex_home)])

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
            "case_filters": list(cases),
            "category_filters": list(categories),
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
        "failure_classification": _classify_case_failures(parsed),
        "case_filters": parsed.get("case_filters", list(cases)),
        "category_filters": parsed.get("category_filters", list(categories)),
        "artifacts": parsed.get("artifacts", {}),
        "errors": [] if status == "success" else [{"code": "ERR_VALIDATION", "message": "Evaluation run failed."}],
        "raw_output": process.stdout,
        "raw_error": process.stderr,
    }


def _list_skill_builder_cases(
    repo_root: Path,
    skill_name: str,
    mode: str,
    cases: tuple[str, ...],
    categories: tuple[str, ...],
) -> tuple[list[str], dict[str, object] | None]:
    skill_path = _skill_path(skill_name)
    cmd = [
        sys.executable,
        str(_skill_builder_runner_path(repo_root)),
        str(skill_path),
        "--eval-mode",
        mode,
        "--runner",
        "discovery-smoke",
        "--list-cases",
    ]
    _append_repeatable_filter(cmd, "--case", cases)
    _append_repeatable_filter(cmd, "--category", categories)
    started_at = time.time()
    try:
        process = subprocess.run(
            cmd,
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=60,
        )
    except subprocess.TimeoutExpired as error:
        return [], {
            "skill": skill_name,
            "mode": mode,
            "runner": "codex",
            "command": " ".join(cmd),
            "returncode": 124,
            "duration_seconds": round(time.time() - started_at, 3),
            "timeout_seconds": 60,
            "status": "timeout",
            "errors": [
                {
                    "code": "ERR_CASE_DISCOVERY_TIMEOUT",
                    "message": "Timed out while listing eval cases before split release execution.",
                }
            ],
            "raw_output": error.stdout or "",
            "raw_error": error.stderr or "",
        }
    if process.returncode != 0:
        return [], {
            "skill": skill_name,
            "mode": mode,
            "runner": "codex",
            "command": " ".join(cmd),
            "returncode": process.returncode,
            "duration_seconds": round(time.time() - started_at, 3),
            "status": "error",
            "errors": [
                {
                    "code": "ERR_CASE_DISCOVERY",
                    "message": "Could not list eval cases before split release execution.",
                }
            ],
            "raw_output": process.stdout,
            "raw_error": process.stderr,
        }

    case_ids: list[str] = []
    for line in process.stdout.splitlines():
        match = re.match(r"^-\s+([^\s\[]+)\s+\[", line.strip())
        if match:
            case_ids.append(match.group(1))
    if not case_ids:
        return [], {
            "skill": skill_name,
            "mode": mode,
            "runner": "codex",
            "command": " ".join(cmd),
            "returncode": 1,
            "duration_seconds": round(time.time() - started_at, 3),
            "status": "error",
            "errors": [
                {
                    "code": "ERR_CASE_DISCOVERY_EMPTY",
                    "message": "No eval case ids were discovered for split release execution.",
                }
            ],
            "raw_output": process.stdout,
            "raw_error": process.stderr,
        }
    return case_ids, None


def _run_skill_builder_eval_split_cases(
    repo_root: Path,
    skill_name: str,
    mode: str,
    runner: str,
    cases: tuple[str, ...],
    categories: tuple[str, ...],
    per_skill_timeout_sec: int | None,
    model: str | None,
    timeout_profile: str | None,
    codex_home: Path | None,
) -> dict[str, object]:
    started_at = time.time()
    case_ids, discovery_error = _list_skill_builder_cases(
        repo_root,
        skill_name,
        mode,
        cases,
        categories,
    )
    if discovery_error is not None:
        return discovery_error

    case_results: list[dict[str, object]] = []
    for case_id in case_ids:
        case_results.append(
            _run_skill_builder_eval(
                repo_root,
                skill_name,
                mode,
                runner,
                (case_id,),
                (),
                per_skill_timeout_sec,
                model,
                timeout_profile,
                codex_home,
            )
        )

    failed = [
        result
        for result in case_results
        if result.get("returncode") != 0 or result.get("status") != "success"
    ]
    timed_out = [
        result
        for result in case_results
        if result.get("returncode") == 124 or result.get("status") == "timeout"
    ]
    return {
        "skill": skill_name,
        "mode": mode,
        "runner": runner,
        "command": (
            f"split release cases via {_skill_builder_runner_path(repo_root)} "
            f"cases={','.join(case_ids) or '<none>'}"
        ),
        "returncode": 0 if not failed else 2,
        "duration_seconds": round(time.time() - started_at, 3),
        "timeout_seconds": per_skill_timeout_sec,
        "status": "success" if not failed else ("timeout" if len(timed_out) == len(failed) else "error"),
        "decision": "pass" if not failed else "fail",
        "split_cases": True,
        "case_filters": list(cases),
        "category_filters": list(categories),
        "case_results": case_results,
        "failure_classification": _merged_case_failure_classification(case_results),
        "errors": [] if not failed else [{"code": "ERR_VALIDATION", "message": "One or more split eval cases failed."}],
        "raw_output": json.dumps(
            {
                "split_cases": True,
                "case_count": len(case_results),
                "cases": [
                    {
                        "id": (result.get("case_filters") or [None])[0]
                        if isinstance(result.get("case_filters"), list)
                        else None,
                        "status": result.get("status"),
                        "returncode": result.get("returncode"),
                        "duration_seconds": result.get("duration_seconds"),
                    }
                    for result in case_results
                ],
            }
        ),
        "raw_error": "",
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
    split_release_cases: bool,
    codex_home: Path | None,
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
    if split_release_cases and mode == "release":
        return _run_skill_builder_eval_split_cases(
            repo_root,
            skill_name,
            mode,
            eval_runner,
            cases,
            categories,
            per_skill_timeout_sec,
            model,
            timeout_profile,
            codex_home,
        )
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
        codex_home,
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
    failure_breakdown = _failure_breakdown(results)
    return {
        "schema_version": 1,
        "gate": "harness-engineering-lifecycle-evals",
        "status": "pass" if not failing and not failing_gates else "fail",
        "skills": [result["skill"] for result in results],
        "results": results,
        "failing_skills": [result["skill"] for result in failing],
        "failing_gates": failing_gates,
        "failure_breakdown": failure_breakdown,
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
        "--codex-home",
        help=(
            "Codex home for direct Codex eval runner. Defaults to CODEX_HOME or ~/.codex "
            "so split release lanes use authenticated state instead of unauthenticated "
            "temporary homes."
        ),
    )
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
    parser.add_argument(
        "--split-release-cases",
        dest="split_release_cases",
        action="store_true",
        default=True,
        help=(
            "For --eval-runner codex release lanes, run each selected eval case separately "
            "and aggregate results so timeouts do not hide content failures. Default: enabled."
        ),
    )
    parser.add_argument(
        "--no-split-release-cases",
        dest="split_release_cases",
        action="store_false",
        help="Run release cases in one skill-level process for legacy debugging.",
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
    codex_home = (
        Path(args.codex_home).expanduser().resolve()
        if args.codex_home
        else Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex").expanduser().resolve()
    )
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
            args.split_release_cases,
            codex_home if args.eval_runner == "codex" else None,
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
