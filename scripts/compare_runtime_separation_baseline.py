#!/usr/bin/env python3
"""Compare runtime-separation current artifact against baseline and fail on regressions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", required=True, help="Baseline artifact path")
    parser.add_argument("--current", required=True, help="Current artifact path")
    return parser.parse_args()


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON root must be object: {path}")
    return payload


def _flatten_checks(checks: dict[str, Any], prefix: str = "") -> dict[str, dict[str, Any]]:
    flattened: dict[str, dict[str, Any]] = {}
    for key, value in checks.items():
        ref = f"{prefix}{key}" if not prefix else f"{prefix}.{key}"
        if isinstance(value, dict) and {"returncode", "drift_class", "blocker_id"}.issubset(value.keys()):
            flattened[ref] = value
        elif isinstance(value, dict):
            flattened.update(_flatten_checks(value, ref))
    return flattened


def _severity(check: dict[str, Any]) -> int:
    return 0 if check.get("returncode") in (0, None) else 2


def main() -> int:
    args = parse_args()
    baseline_path = Path(args.baseline).resolve()
    current_path = Path(args.current).resolve()

    baseline = _load(baseline_path)
    current = _load(current_path)

    baseline_summary = baseline.get("summary") if isinstance(baseline.get("summary"), dict) else {}
    current_summary = current.get("summary") if isinstance(current.get("summary"), dict) else {}

    baseline_checks = baseline_summary.get("command_checks") if isinstance(baseline_summary.get("command_checks"), dict) else {}
    current_checks = current_summary.get("command_checks") if isinstance(current_summary.get("command_checks"), dict) else {}

    flat_baseline = _flatten_checks(baseline_checks)
    flat_current = _flatten_checks(current_checks)

    blockers: list[dict[str, Any]] = []

    for key, baseline_check in flat_baseline.items():
        if key not in flat_current:
            blockers.append(
                {
                    "id": f"missing_check:{key}",
                    "severity": 2,
                    "reason": f"current artifact missing check {key}",
                }
            )
            continue

        current_check = flat_current[key]
        baseline_severity = _severity(baseline_check)
        current_severity = _severity(current_check)

        if current_severity > baseline_severity:
            blockers.append(
                {
                    "id": f"severity_regression:{key}",
                    "severity": current_severity,
                    "reason": (
                        f"check {key} severity regressed "
                        f"(baseline={baseline_severity}, current={current_severity})"
                    ),
                }
            )

        baseline_blocker = baseline_check.get("blocker_id")
        current_blocker = current_check.get("blocker_id")
        if baseline_blocker in (None, "") and current_blocker not in (None, ""):
            blockers.append(
                {
                    "id": f"new_blocker:{key}",
                    "severity": current_severity,
                    "reason": f"check {key} introduced blocker_id={current_blocker}",
                }
            )

    decision_status = "pass" if not blockers else "blocked_regression"
    output = {
        "schema_version": "runtime-separation-compare.v1",
        "decision_status": decision_status,
        "baseline": str(baseline_path),
        "current": str(current_path),
        "blockers": blockers,
        "summary": {
            "baseline_check_count": len(flat_baseline),
            "current_check_count": len(flat_current),
            "regression_count": len(blockers),
        },
    }
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0 if not blockers else 1


if __name__ == "__main__":
    raise SystemExit(main())
