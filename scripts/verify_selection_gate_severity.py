#!/usr/bin/env python3
"""Emit and validate selection gate severity artifact."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    """
    Build and return the command-line arguments for the selection-gate-severity script.
    
    Parameters:
        None
    
    Arguments:
        --check-results (Path): TSV file of check results produced by validate_all.
        --output (Path): Destination path for the JSON artifact.
        --schema (Path): Path to the schema file used for structural validation.
        --run-id (str): Identifier for this validation run to embed in the artifact.
        --required-check (list[str]): Repeatable option listing spec-critical check names that must be present and have mode equal to "required".
    
    Returns:
        argparse.Namespace: Parsed arguments with attributes corresponding to the options above.
    """
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
    """
    Parse a TSV check-results file into a list of row dictionaries.
    
    Parameters:
        path (Path): Path to a tab-separated values file where each non-empty line
            contains at least four columns: slug, mode, result, log_file.
    
    Returns:
        list[dict[str, str | None]]: A list of dictionaries for each row with keys
            `name`, `mode`, `result` and `log_file` (`None` when the field is empty).
    
    Raises:
        ValueError: If the file does not exist, if any non-empty line has fewer than
            four tab-separated fields, or if the file contains no valid rows.
    """
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
    """
    Validate that a payload conforms to the expected selection-gate-severity schema contract.
    
    Performs dependency-free structural checks: verifies the schema file exists, that top-level fields meet the contract (schema_version equals "selection-gate-severity.v1", non-empty `run_id` and `generated_at`, and `all_required_passed` is boolean), and that `checks` is a non-empty list of objects where each check has non-empty string `name`, `mode`, `result`, and `rationale`, with `mode` one of `required` or `warn` and `result` one of `pass`, `fail`, or `blocked`.
    
    Parameters:
        payload (dict[str, Any]): The JSON-serialisable payload to validate.
        schema_path (Path): Path to the schema file; used to confirm the schema file exists.
    
    Returns:
        list[str]: A list of validation issue messages; an empty list indicates the payload satisfies the contract.
    """
    issues: list[str] = []
    if not schema_path.exists():
        issues.append(f"schema file missing: {schema_path}")
        return issues

    if payload.get("schema_version") != "selection-gate-severity.v1":
        issues.append("schema_version must be selection-gate-severity.v1")
    if not isinstance(payload.get("run_id"), str) or not payload["run_id"].strip():
        issues.append("run_id must be a non-empty string")
    generated_at = payload.get("generated_at")
    if not isinstance(generated_at, str) or not generated_at.strip():
        issues.append("generated_at must be a non-empty string")
    else:
        try:
            datetime.fromisoformat(generated_at.replace("Z", "+00:00"))
        except ValueError:
            issues.append("generated_at must be a valid ISO 8601 date-time string")
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
        log_file = check.get("log_file")
        if log_file is not None and (not isinstance(log_file, str) or not log_file.strip()):
            issues.append(f"checks[{idx}].log_file must be null or a non-empty string")

    return issues


def main() -> int:
    """
    Run the CLI: read TSV check results, build a selection-gate-severity JSON artefact, validate it against the schema, write it to the output path and report any issues.
    
    The function:
    - Loads check rows from the provided TSV; prints the error and returns 1 if loading fails.
    - Ensures any specified required checks exist and have mode "required", collecting issues for missing or mismatched entries.
    - Constructs per-check entries with `rationale` derived from the check `result`, computes `all_required_passed`, and assembles the payload.
    - Performs structural validation against the provided schema path and aggregates any validation issues.
    - Writes the JSON artefact to the output path (creating parent directories as needed).
    - Prints the artefact path and either a summary of validation issues or a success message.
    
    Returns:
        int: `0` on successful validation and write; `1` on TSV parse errors or if any validation issues are detected.
    """
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

    if issues:
        print("Selection gate severity validation failed:")
        for issue in issues:
            print(f"- {issue}")
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"selection-gate-severity artifact: {args.output}")
    print("Selection gate severity validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
