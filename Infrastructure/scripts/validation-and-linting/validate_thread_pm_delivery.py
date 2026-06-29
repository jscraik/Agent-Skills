#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, SCRIPT_DIR.as_posix())

import validate_thread_report  # noqa: E402


SCHEMA_VERSION = "thread-report-delivery/v1"
VALID_DELIVERY_STATUSES = {"delivered", "blocked"}
VALID_DELIVERY_METHODS = {
    "codex_app__send_message_to_thread",
    "codex_app__handoff_thread",
    "manual_pm_update",
    "blocked_no_thread_tool",
}


def _finding(path: str, message: str) -> dict[str, str]:
    return {"path": path, "message": message}


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip()) and "<" not in value and ">" not in value


def _load_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, str(exc)
    if not isinstance(payload, dict):
        return None, "json root must be an object"
    return payload, None


def _default_delivery_path(report_path: Path) -> Path:
    return report_path.with_name("pm-delivery.json")


def _validate_report(report_path: Path) -> tuple[dict[str, Any] | None, list[dict[str, str]]]:
    report, error = _load_json(report_path)
    if report is None:
        return None, [_finding("report", error or "unable to read report")]
    findings = validate_thread_report.validate_thread_report(report)
    return report, [_finding(f"report.{item['path']}", item["message"]) for item in findings]


def _validate_required_delivery_keys(delivery: dict[str, Any]) -> list[dict[str, str]]:
    required_keys = (
        "thread_id",
        "pm_thread_id",
        "report_path",
        "delivery_method",
        "delivery_status",
        "delivery_evidence",
    )
    return [_finding(f"delivery.{key}", "missing required key") for key in required_keys if key not in delivery]


def _validate_delivery_report_path(
    delivery: dict[str, Any],
    delivery_path: Path,
    report_path: Path,
) -> list[dict[str, str]]:
    report_path_value = delivery.get("report_path")
    if not _non_empty_string(report_path_value):
        return [_finding("delivery.report_path", "must be a non-empty final string")]

    resolved = (delivery_path.parent / report_path_value).resolve()
    if resolved != report_path.resolve():
        return [_finding("delivery.report_path", "must point at the validated thread-report artifact")]
    return []


def _validate_delivered_state(delivery: dict[str, Any]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    if delivery.get("delivery_status") != "delivered":
        return findings

    for key in ("delivered_at", "message_summary"):
        if not _non_empty_string(delivery.get(key)):
            findings.append(_finding(f"delivery.{key}", "must be present for delivered status"))
    if delivery.get("delivery_method", "").startswith("blocked"):
        findings.append(_finding("delivery.delivery_method", "delivered status cannot use a blocked delivery method"))
    return findings


def _validate_delivery_fields(
    delivery: dict[str, Any],
    report: dict[str, Any],
    report_path: Path,
    delivery_path: Path,
    *,
    require_delivery: bool,
) -> list[dict[str, str]]:
    findings = _validate_required_delivery_keys(delivery)
    if delivery.get("schema_version") != SCHEMA_VERSION:
        findings.append(_finding("delivery.schema_version", f"must equal {SCHEMA_VERSION}"))
    if delivery.get("thread_id") != report.get("thread_id"):
        findings.append(_finding("delivery.thread_id", "must match thread-report thread_id"))
    findings.extend(_validate_delivery_report_path(delivery, delivery_path, report_path))
    if not _non_empty_string(delivery.get("pm_thread_id")):
        findings.append(_finding("delivery.pm_thread_id", "must name the PM/root thread id"))
    elif delivery.get("pm_thread_id") == report.get("thread_id"):
        findings.append(_finding("delivery.pm_thread_id", "must differ from the execution thread_id"))
    if delivery.get("delivery_method") not in VALID_DELIVERY_METHODS:
        findings.append(_finding("delivery.delivery_method", "must be a supported delivery method or explicit blocked method"))
    if delivery.get("delivery_status") not in VALID_DELIVERY_STATUSES:
        findings.append(_finding("delivery.delivery_status", "must be delivered or blocked"))
    if not _non_empty_string(delivery.get("delivery_evidence")):
        findings.append(_finding("delivery.delivery_evidence", "must record concrete PM delivery evidence or blocker"))
    findings.extend(_validate_delivered_state(delivery))
    if require_delivery and delivery.get("delivery_status") != "delivered":
        findings.append(_finding("delivery.delivery_status", "PM delivery is required and must be delivered"))
    return findings


def validate_delivery(
    report_path: Path,
    delivery_path: Path,
    *,
    require_delivery: bool,
) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    report, report_findings = _validate_report(report_path)
    findings.extend(report_findings)
    if report is None:
        return findings

    delivery, error = _load_json(delivery_path)
    if delivery is None:
        if require_delivery:
            findings.append(_finding("delivery", f"missing PM delivery receipt: {delivery_path.as_posix()}"))
        return findings

    return findings + _validate_delivery_fields(
        delivery,
        report,
        report_path,
        delivery_path,
        require_delivery=require_delivery,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate PM delivery for a thread-report/v1 artifact.")
    parser.add_argument("report", type=Path)
    parser.add_argument("--delivery", type=Path)
    parser.add_argument("--require-delivery", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    delivery_path = args.delivery or _default_delivery_path(args.report)
    findings = validate_delivery(
        args.report,
        delivery_path,
        require_delivery=args.require_delivery,
    )
    result = {
        "schema_version": "thread-report-delivery-validation/v1",
        "status": "pass" if not findings else "fail",
        "report_path": args.report.as_posix(),
        "delivery_path": delivery_path.as_posix(),
        "require_delivery": args.require_delivery,
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
