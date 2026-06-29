#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]

SCHEMA_VERSION = "thread-report/v1"
VALID_STATUSES = {"pass", "blocked", "failed"}
VALID_OUTCOMES = {"pass", "fail", "blocked"}
BLOCKED_OSS_LOCAL_GATES = {"oss-cloud", "tessl-dry-run", "tessl-live"}
LEARNING_LEDGER_PATH = ".harness/memory/LEARNINGS.md"
REPO_ROOT = Path(__file__).resolve().parents[3]


def _finding(path: str, message: str) -> dict[str, str]:
    return {"path": path, "message": message}


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip()) and not _has_placeholder(value)


def _has_placeholder(value: str) -> bool:
    return bool(re.search(r"<[^<>\s][^<>]*>", value))


def _validate_items(
    payload: dict[str, Any],
    key: str,
    required_keys: set[str],
    outcome_key: str | None = None,
) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    value = payload.get(key)
    if not isinstance(value, list) or not value:
        return [_finding(key, "must be a non-empty list")]
    for index, item in enumerate(value):
        item_path = f"{key}.{index}"
        if not isinstance(item, dict):
            findings.append(_finding(item_path, "must be an object"))
            continue
        missing = sorted(required_keys - set(item))
        if missing:
            findings.append(_finding(item_path, f"missing required keys: {','.join(missing)}"))
        for required_key in required_keys:
            if required_key not in item:
                continue
            if required_key == outcome_key:
                if item.get(required_key) not in VALID_OUTCOMES:
                    findings.append(_finding(f"{item_path}.{required_key}", "must be pass, fail, or blocked"))
            elif not _non_empty_string(item.get(required_key)):
                findings.append(_finding(f"{item_path}.{required_key}", "must be a non-empty final string"))
    return findings


def _repo_path_exists(value: str) -> bool:
    if value.startswith(("https://", "http://")):
        return True
    path = Path(value)
    if path.is_absolute():
        try:
            path.relative_to(ROOT)
        except ValueError:
            return False
        return path.exists()
    if value.startswith("../"):
        return False
    return (ROOT / path).exists()


def _validate_repo_path(value: Any, finding_path: str) -> list[dict[str, str]]:
    if not _non_empty_string(value):
        return []
    return [] if _repo_path_exists(str(value)) else [_finding(finding_path, "must reference an existing repo path")]


def _validate_required_top(payload: dict[str, Any]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    required_top = {
        "schema_version",
        "thread_id",
        "repo_head",
        "task_id",
        "status",
        "current_gate",
        "next_gate_allowed",
        "blocked_next_gates",
        "commands",
        "artifact_assertions",
        "contradictions",
        "files_changed",
        "lessons",
        "next_action",
    }
    missing = sorted(required_top - set(payload))
    if missing:
        findings.append(_finding("$", f"missing required keys: {','.join(missing)}"))
    return findings


def _validate_scalar_fields(payload: dict[str, Any]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    if payload.get("schema_version") != SCHEMA_VERSION:
        findings.append(_finding("schema_version", f"must equal {SCHEMA_VERSION}"))
    for key in ("thread_id", "repo_head", "task_id", "current_gate", "next_action"):
        if not _non_empty_string(payload.get(key)):
            findings.append(_finding(key, "must be a non-empty final string"))
    if payload.get("status") not in VALID_STATUSES:
        findings.append(_finding("status", "must be pass, blocked, or failed"))
    if not isinstance(payload.get("next_gate_allowed"), bool):
        findings.append(_finding("next_gate_allowed", "must be boolean"))
    return findings


def _validate_blocked_next_gates(payload: dict[str, Any]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    blocked_next_gates = payload.get("blocked_next_gates")
    if not isinstance(blocked_next_gates, list) or not all(isinstance(item, str) and item.strip() for item in blocked_next_gates):
        findings.append(_finding("blocked_next_gates", "must be a list of non-empty strings"))
    elif payload.get("current_gate") == "oss-local-repair" and not BLOCKED_OSS_LOCAL_GATES.issubset(set(blocked_next_gates)):
        findings.append(_finding("blocked_next_gates", "oss-local repair must block oss-cloud, tessl-dry-run, and tessl-live"))

    if payload.get("current_gate") == "oss-local-repair" and payload.get("next_gate_allowed") is not False:
        findings.append(_finding("next_gate_allowed", "oss-local repair must set next_gate_allowed false"))
    return findings


def _validate_files_changed(payload: dict[str, Any]) -> list[dict[str, str]]:
    files_changed = payload.get("files_changed")
    if not isinstance(files_changed, list) or not all(isinstance(item, str) and item.strip() for item in files_changed):
        return [_finding("files_changed", "must be a list of non-empty strings")]
    findings: list[dict[str, str]] = []
    for index, item in enumerate(files_changed):
        findings.extend(_validate_repo_path(item, f"files_changed.{index}"))
    return findings


def _validate_lessons(payload: dict[str, Any]) -> list[dict[str, str]]:
    findings = _validate_items(
        payload,
        "lessons",
        {
            "lesson",
            "failure_pattern",
            "carry_forward_target",
            "deterministic_guardrail",
            "recorded_in",
            "validation",
        },
    )
    lessons = payload.get("lessons")
    if not isinstance(lessons, list):
        return findings
    has_learning_ledger_record = False
    for index, item in enumerate(lessons):
        if not isinstance(item, dict):
            continue
        recorded_in = item.get("recorded_in")
        findings.extend(_validate_repo_path(recorded_in, f"lessons.{index}.recorded_in"))
        if isinstance(recorded_in, str) and LEARNING_LEDGER_PATH in recorded_in:
            has_learning_ledger_record = True
        if isinstance(recorded_in, str) and recorded_in.startswith(".harness/reports/thread-replies/"):
            findings.append(
                _finding(
                    f"lessons.{index}.recorded_in",
                    "must point at durable memory, docs, source, eval, or validator surface; not only the thread report",
                )
            )
    if not has_learning_ledger_record:
        findings.append(
            _finding(
                "lessons",
                f"must record at least one carry-forward lesson in {LEARNING_LEDGER_PATH}",
            )
        )
    return findings


def validate_thread_report(payload: dict[str, Any]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    findings.extend(_validate_required_top(payload))
    findings.extend(_validate_scalar_fields(payload))
    findings.extend(_validate_blocked_next_gates(payload))
    findings.extend(_validate_items(payload, "commands", {"command", "outcome", "evidence"}, "outcome"))
    findings.extend(_validate_items(payload, "artifact_assertions", {"artifact", "assertion", "outcome"}, "outcome"))
    for index, item in enumerate(payload.get("artifact_assertions") or []):
        if isinstance(item, dict):
            findings.extend(_validate_repo_path(item.get("artifact"), f"artifact_assertions.{index}.artifact"))
    findings.extend(_validate_items(payload, "contradictions", {"artifact", "problem", "owner"}))
    findings.extend(_validate_files_changed(payload))
    findings.extend(_validate_lessons(payload))
    return findings


def _load_report(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, str(exc)
    if not isinstance(payload, dict):
        return None, "json root must be an object"
    return payload, None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a thread-report/v1 artifact.")
    parser.add_argument("report", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    payload, error = _load_report(args.report)
    findings = [_finding("$", error)] if payload is None else validate_thread_report(payload)
    result = {
        "schema_version": "thread-report-validation/v1",
        "status": "pass" if not findings else "fail",
        "path": args.report.as_posix(),
        "findings": findings,
    }
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(result["status"])
        for finding in findings:
            print(f"{finding['path']}: {finding['message']}")
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
