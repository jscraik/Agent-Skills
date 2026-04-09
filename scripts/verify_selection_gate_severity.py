#!/usr/bin/env python3
"""Emit and validate selection gate severity artifact."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Write selection gate severity artifact.")
    parser.add_argument("--check-results", type=Path, required=True, help="TSV check result file from validate_all.")
    parser.add_argument("--output", type=Path, required=True, help="Output JSON artifact path.")
    parser.add_argument("--schema", type=Path, required=True, help="Schema file path for structural validation.")
    parser.add_argument("--run-id", required=True, help="Validation run id.")
    parser.add_argument(
        "--required-check",
        action="append",
        default=[],
        help="Spec-critical check that must exist in check results and be mode=required.",
    )
    return parser.parse_args()


def _load_check_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise ValueError(f"check results file not found: {path}")

    rows: list[dict[str, str]] = []
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line:
            continue
        parts = line.split("\t")
        if len(parts) < 4:
            raise ValueError(f"invalid check result row: {line}")
        slug, mode, result, log_file = parts[:4]
        rows.append(
            {
                "name": slug,
                "mode": mode,
                "result": result,
                "log_file": log_file or None,
            }
        )
    if not rows:
        raise ValueError("check results file is empty")
    return rows


def _validate_against_schema(payload: dict[str, Any], schema_path: Path) -> list[str]:
    # Keep this validator dependency-free; enforce the fields from schema contract directly.
    issues: list[str] = []
    if not schema_path.exists():
        issues.append(f"schema file missing: {schema_path}")
        return issues

    if payload.get("schema_version") != "selection-gate-severity.v1":
        issues.append("schema_version must be selection-gate-severity.v1")
    if not isinstance(payload.get("run_id"), str) or not payload["run_id"].strip():
        issues.append("run_id must be a non-empty string")
    if not isinstance(payload.get("generated_at"), str) or not payload["generated_at"].strip():
        issues.append("generated_at must be a non-empty string")
    if not isinstance(payload.get("all_required_passed"), bool):
        issues.append("all_required_passed must be boolean")

    checks = payload.get("checks")
    if not isinstance(checks, list) or not checks:
        issues.append("checks must be a non-empty array")
        return issues

    for idx, check in enumerate(checks):
        if not isinstance(check, dict):
            issues.append(f"checks[{idx}] must be an object")
            continue
        for field in ("name", "mode", "result", "rationale"):
            value = check.get(field)
            if not isinstance(value, str) or not value.strip():
                issues.append(f"checks[{idx}].{field} must be a non-empty string")
        if check.get("mode") not in {"required", "warn"}:
            issues.append(f"checks[{idx}].mode must be required|warn")
        if check.get("result") not in {"pass", "fail", "blocked"}:
            issues.append(f"checks[{idx}].result must be pass|fail|blocked")

    return issues


def main() -> int:
    args = parse_args()

    try:
        rows = _load_check_rows(args.check_results)
    except ValueError as exc:
        print(str(exc))
        return 1

    required_checks = sorted(set(args.required_check))
    by_name = {row["name"]: row for row in rows}
    issues: list[str] = []

    for required_name in required_checks:
        row = by_name.get(required_name)
        if row is None:
            issues.append(f"required check missing from results: {required_name}")
            continue
        if row["mode"] != "required":
            issues.append(f"required check must be mode=required: {required_name} (actual={row['mode']})")

    checks: list[dict[str, Any]] = []
    for row in rows:
        result = row["result"]
        rationale = "check passed"
        if result == "fail":
            rationale = "check failed; inspect log"
        elif result == "blocked":
            rationale = "check blocked; inspect log"
        checks.append(
            {
                "name": row["name"],
                "mode": row["mode"],
                "result": result,
                "rationale": rationale,
                "log_file": row["log_file"],
            }
        )

    all_required_passed = True
    for check in checks:
        if check["mode"] == "required" and check["result"] != "pass":
            all_required_passed = False
            break

    payload = {
        "schema_version": "selection-gate-severity.v1",
        "run_id": args.run_id,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "all_required_passed": all_required_passed,
        "checks": checks,
    }

    structural_issues = _validate_against_schema(payload, args.schema)
    issues.extend(structural_issues)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"selection-gate-severity artifact: {args.output}")
    if issues:
        print("Selection gate severity validation failed:")
        for issue in issues:
            print(f"- {issue}")
        return 1

    print("Selection gate severity validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
