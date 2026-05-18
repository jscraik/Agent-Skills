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
    "he-reframe",
    "he-linear-plan",
    "he-eval-report",
    "he-phase-work",
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
    "ERR_CODEX_RUNNER_PREFLIGHT",
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
    "usage limit for gpt-5.3-codex-spark",
)

SLOW_CASE_DIAGNOSTIC_THRESHOLD_SECONDS = 120
DEFAULT_EVAL_MODEL = "gpt-5.3-codex-spark"
DEFAULT_CODEX_ARGS = ("--ignore-user-config",)


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
    """
    Detects whether a case exhibits signs of a Codex runner "preflight" failure.

    Checks the provided failure_strings combined with any case["warnings"] for the phrase "codex returned non-zero exit code" together with any Codex runner preflight markers; if that combination is not found, inspects runner artifact files (when present and readable) for those markers.

    Parameters:
        case (dict): Case dictionary that may include:
            - "warnings": iterable of warning entries (will be stringified)
            - "runners": mapping of runner names to result dicts, each may contain an "artifacts" dict with stderr/stdout/final/jsonl file path strings.
        failure_strings (list[str]): List of failure messages (e.g., tier1 failures) to search.

    Returns:
        `true` if the combined failure/warning text contains both the non-zero Codex exit phrase and a preflight marker, or if any readable runner artifact contains a preflight marker; `false` otherwise.
    """
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
        if _artifacts_have_codex_runner_preflight_signal(artifacts):
            return True
    return False


def _artifact_file_has_codex_runner_preflight_signal(path: object) -> bool:
    """
    Detects whether an artifact file contains markers that indicate a Codex runner preflight failure.

    Parameters:
        path: Path to an artifact file (expected as a string). If not a string or the file cannot be read, the function reports no preflight signal.

    Returns:
        True if any Codex runner preflight marker is found in the file contents, False otherwise.
    """
    if not isinstance(path, str):
        return False
    try:
        text = Path(path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    return any(marker in text.lower() for marker in CODEX_RUNNER_PREFLIGHT_MARKERS)


def _artifacts_have_codex_runner_preflight_signal(artifacts: dict[str, object]) -> bool:
    for name in ("stderr", "stdout", "final", "jsonl"):
        if _artifact_file_has_codex_runner_preflight_signal(artifacts.get(name)):
            return True
    return False


def _artifact_tool_preflight_case(parsed: dict[str, object]) -> dict[str, object] | None:
    """
    Constructs a synthetic case entry when parsed artifacts indicate a Codex runner preflight failure.

    Parameters:
        parsed (dict): Parsed JSON output from an evaluation run; expected to contain an "artifacts" mapping and optionally "case_filters" and "tier1_failures".

    Returns:
        dict | None: A synthetic case dictionary with keys `id`, `name`, `category`, and `tier1_failures` when an artifact `stderr` contains a Codex runner preflight signal; `None` otherwise.
    """
    artifacts = parsed.get("artifacts")
    if not isinstance(artifacts, dict):
        return None
    if not _artifacts_have_codex_runner_preflight_signal(artifacts):
        return None

    case_filters = parsed.get("case_filters")
    case_id = case_filters[0] if isinstance(case_filters, list) and case_filters else None
    return {
        "id": case_id,
        "name": case_id,
        "category": None,
        "tier1_failures": parsed.get("tier1_failures") or [
            "[codex] Codex runner preflight failed before producing final output."
        ],
    }


def _classify_eval_failures(parsed: dict[str, object]) -> dict[str, object]:
    """
    Augments a case-level failure classification with a synthetic tool-preflight case derived from top-level artifacts when present.

    If the parsed evaluation output contains an artifact-derived Codex runner preflight signal, this function appends a corresponding case entry to the `tool_preflight_cases` list (creating the list if necessary) and removes any matching case entry from `other_failure_cases`. If no artifact-derived preflight case is found, the original classification is returned unchanged.

    Parameters:
        parsed (dict): Parsed evaluation output (JSON decoded) describing the run and its cases.

    Returns:
        dict: A failure classification mapping that includes (when applicable) the keys `timeout_cases`, `content_failure_cases`, `tool_preflight_cases`, and `other_failure_cases`.
    """
    classification = _classify_case_failures(parsed)
    artifact_case = _artifact_tool_preflight_case(parsed)
    if artifact_case is None:
        return classification

    classification.setdefault("tool_preflight_cases", [])
    tool_cases = classification.get("tool_preflight_cases")
    if isinstance(tool_cases, list):
        tool_cases.append(artifact_case)

    other_cases = classification.get("other_failure_cases")
    if isinstance(other_cases, list):
        artifact_id = artifact_case.get("id")
        classification["other_failure_cases"] = [
            case
            for case in other_cases
            if not isinstance(case, dict) or case.get("id") != artifact_id
        ]
    return classification


def _iter_case_warnings(parsed: dict[str, object]) -> list[dict[str, object]]:
    """
    Collects cases that contain warnings from a parsed evaluation result.

    Parameters:
        parsed (dict): Parsed evaluation output expected to contain a "cases" iterable where each case may include "id", "name", "category", and "warnings".

    Returns:
        list[dict]: A list of dictionaries for each case that had warnings. Each dictionary contains:
            - "id": case id (or None if missing)
            - "name": case name (or None if missing)
            - "category": case category (or None if missing)
            - "warnings": list of warning strings
    """
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
        "slow_pass_cases": [],
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
        slow_cases = result.get("slow_cases")
        if isinstance(slow_cases, list) and slow_cases:
            breakdown["slow_pass_cases"].append(
                {
                    "skill": skill,
                    "threshold_seconds": result.get(
                        "slow_case_threshold_seconds",
                        SLOW_CASE_DIAGNOSTIC_THRESHOLD_SECONDS,
                    ),
                    "cases": slow_cases,
                }
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
    """
    Run the skill-builder evaluation runner for a single skill and return a structured result.

    Parameters:
        repo_root (Path): Repository root used as working directory for the runner.
        skill_name (str): Name of the skill to evaluate.
        mode (str): Evaluation mode, e.g., "smoke" or "release".
        runner (str): Eval runner identifier (e.g., "codex" or "ask"); affects available flags.
        cases (tuple[str, ...]): Specific case IDs to filter the run; empty means run all cases.
        categories (tuple[str, ...]): Category filters (e.g., "happy", "edge"); empty means all categories.
        per_skill_timeout_sec (int | None): Per-skill timeout override in seconds; when None a mode-based default is used.
        model (str | None): Optional model identifier forwarded to the runner.
        timeout_profile (str | None): Optional timeout profile forwarded to the runner.
        codex_home (Path | None): Path to Codex home; used only when `runner == "codex"`.

    Returns:
        dict[str, object]: Structured evaluation result containing keys including:
            - "skill", "mode", "runner", "command"
            - "returncode" (int), "duration_seconds" (float)
            - "status" ("success" or "error" or "timeout"), "decision" (from parsed output)
            - "tier1_failures", "tier2_findings" (from runner output)
            - "failure_classification" (classification dict produced from parsed output)
            - "case_filters", "category_filters" (echoed or derived)
            - "artifacts" (dict), "errors" (list of error dicts)
            - "raw_output" (stdout string), "raw_error" (stderr string)
    """
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
    cmd.extend(["--model", DEFAULT_EVAL_MODEL])
    _append_repeatable_filter(cmd, "--codex-arg", DEFAULT_CODEX_ARGS)
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
        "failure_classification": _classify_eval_failures(parsed),
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
    max_cases: int | None = None,
    max_tool_preflight_failures: int = 1,
) -> dict[str, object]:
    """
    Run the skill-builder eval runner in split-per-case mode, execute each discovered case individually, and aggregate per-case results and failure classification.

    Parameters:
        repo_root (Path): Repository root path used to locate the skill-builder runner.
        skill_name (str): Name of the skill to evaluate.
        mode (str): Evaluation mode, e.g., "smoke" or "release".
        runner (str): Eval runner name passed to the skill-builder (e.g., "codex").
        cases (tuple[str, ...]): Case filters passed to discovery; used to limit listed cases.
        categories (tuple[str, ...]): Category filters passed to discovery.
        per_skill_timeout_sec (int | None): Optional per-skill timeout (seconds) applied to each per-case invocation.
        model (str | None): Optional model identifier forwarded to the skill-builder runner.
        timeout_profile (str | None): Optional timeout profile forwarded to the skill-builder runner.
        codex_home (Path | None): Optional Codex home directory used when the runner requires a Codex installation.

    Returns:
        dict[str, object]: Aggregated evaluation result containing (among other keys):
            - "skill", "mode", "runner", "command": metadata about this split run.
            - "returncode": 0 when all cases passed, 2 when any case failed.
            - "status": "success" when no failures, "timeout" if all failures timed out, otherwise "error".
            - "decision": "pass" when no failures, otherwise "fail".
            - "split_cases": True.
            - "case_filters", "category_filters": lists of the input filters.
            - "case_results": list of per-case result dicts as returned by the underlying runner.
            - "slow_case_threshold_seconds", "slow_cases": slow-case diagnostics.
            - "failure_classification": merged classification of case-level failures (timeout/content/tool_preflight/other).
            - "errors": empty list when no failures, otherwise a single error dict whose code is
                "ERR_CODEX_RUNNER_PREFLIGHT" if all failures are codex runner preflight failures, else "ERR_VALIDATION".
            - "raw_output": JSON string summarizing per-case statuses and slow cases.
            - "raw_error": empty string (no top-level stderr output for split runs).
    """
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

    discovered_case_count = len(case_ids)
    selected_case_ids = case_ids[:max_cases] if max_cases is not None else case_ids
    case_results: list[dict[str, object]] = []
    early_stop_reason: str | None = None
    tool_preflight_failures = 0
    for case_id in selected_case_ids:
        result = _run_skill_builder_eval(
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
        case_results.append(result)
        if _result_failure_class(result) != "tool_preflight":
            continue
        tool_preflight_failures += 1
        if max_tool_preflight_failures and tool_preflight_failures >= max_tool_preflight_failures:
            early_stop_reason = "tool_preflight_failure_limit"
            break

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
    failure_classification = _merged_case_failure_classification(case_results)
    tool_preflight_cases = failure_classification.get("tool_preflight_cases")
    non_tool_preflight_failures = (
        failure_classification.get("content_failure_cases")
        or failure_classification.get("timeout_cases")
        or failure_classification.get("other_failure_cases")
    )
    all_failures_are_tool_preflight = (
        bool(failed)
        and isinstance(tool_preflight_cases, list)
        and len(tool_preflight_cases) == len(failed)
        and not non_tool_preflight_failures
    )
    slow_cases = [
        {
            "id": (result.get("case_filters") or [None])[0]
            if isinstance(result.get("case_filters"), list)
            else None,
            "duration_seconds": result.get("duration_seconds"),
        }
        for result in case_results
        if result.get("returncode") == 0
        and result.get("status") == "success"
        and isinstance(result.get("duration_seconds"), (int, float))
        and result["duration_seconds"] >= SLOW_CASE_DIAGNOSTIC_THRESHOLD_SECONDS
    ]
    return {
        "skill": skill_name,
        "mode": mode,
        "runner": runner,
        "command": (
            f"split release cases via {_skill_builder_runner_path(repo_root)} "
            f"cases={','.join(selected_case_ids) or '<none>'}"
        ),
        "returncode": 0 if not failed else 2,
        "duration_seconds": round(time.time() - started_at, 3),
        "timeout_seconds": per_skill_timeout_sec,
        "status": "success" if not failed else ("timeout" if len(timed_out) == len(failed) else "error"),
        "decision": "pass" if not failed else "fail",
        "split_cases": True,
        "bounded_run": max_cases is not None or early_stop_reason is not None,
        "max_cases": max_cases,
        "max_tool_preflight_failures": max_tool_preflight_failures,
        "discovered_case_count": discovered_case_count,
        "executed_case_count": len(case_results),
        "skipped_case_count": max(discovered_case_count - len(case_results), 0),
        "early_stop_reason": early_stop_reason,
        "case_filters": list(cases),
        "category_filters": list(categories),
        "case_results": case_results,
        "slow_case_threshold_seconds": SLOW_CASE_DIAGNOSTIC_THRESHOLD_SECONDS,
        "slow_cases": slow_cases,
        "failure_classification": failure_classification,
        "errors": []
        if not failed
        else [
            {
                "code": "ERR_CODEX_RUNNER_PREFLIGHT"
                if all_failures_are_tool_preflight
                else "ERR_VALIDATION",
                "message": "Codex live eval runner failed before producing final output."
                if all_failures_are_tool_preflight
                else "One or more split eval cases failed.",
            }
        ],
        "raw_output": json.dumps(
            {
                "split_cases": True,
                "bounded_run": max_cases is not None or early_stop_reason is not None,
                "max_cases": max_cases,
                "max_tool_preflight_failures": max_tool_preflight_failures,
                "discovered_case_count": discovered_case_count,
                "executed_case_count": len(case_results),
                "skipped_case_count": max(discovered_case_count - len(case_results), 0),
                "early_stop_reason": early_stop_reason,
                "case_count": len(case_results),
                "slow_case_threshold_seconds": SLOW_CASE_DIAGNOSTIC_THRESHOLD_SECONDS,
                "slow_cases": slow_cases,
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
    max_cases: int | None = None,
    max_tool_preflight_failures: int = 1,
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
            max_cases,
            max_tool_preflight_failures,
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
        "eval_runtime": {
            "codex_model": DEFAULT_EVAL_MODEL,
            "codex_args": list(DEFAULT_CODEX_ARGS),
            "reasoning_flags": [],
        },
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
    parser.add_argument(
        "--model",
        help=(
            "Compatibility option. HE evals always run with "
            f"{DEFAULT_EVAL_MODEL}; any other value is rejected."
        ),
    )
    parser.add_argument(
        "--codex-home",
        help=(
            "Codex home for direct Codex eval runner. When omitted, the shared "
            "skill eval runner creates an isolated writable CODEX_HOME for the "
            "live eval process."
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
    parser.add_argument(
        "--max-cases",
        type=int,
        help=(
            "Bound split Codex release execution to the first N discovered cases. "
            "Use for diagnostic loops; omit for full release coverage."
        ),
    )
    parser.add_argument(
        "--max-tool-preflight-failures",
        type=int,
        default=1,
        help=(
            "Stop split Codex release execution after N runner preflight failures. "
            "Use 0 to run every selected case even when the live runner is unhealthy."
        ),
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON only.")
    args = parser.parse_args()
    if args.max_cases is not None and args.max_cases < 1:
        parser.error("--max-cases must be greater than or equal to 1")
    if args.max_tool_preflight_failures < 0:
        parser.error("--max-tool-preflight-failures must be greater than or equal to 0")
    if args.model and args.model != DEFAULT_EVAL_MODEL:
        parser.error(f"--model is fixed to {DEFAULT_EVAL_MODEL} for HE evals")

    repo_root = repo_root_from_script()
    selected_skills = tuple(args.skill) if args.skill else DEFAULT_SKILLS
    cases = tuple(
        item.strip()
        for value in (args.case or [])
        for item in value.split(",")
        if item.strip()
    )
    categories = tuple(args.category or ())
    codex_home = Path(args.codex_home).expanduser().resolve() if args.codex_home else None
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
            args.max_cases,
            args.max_tool_preflight_failures,
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
