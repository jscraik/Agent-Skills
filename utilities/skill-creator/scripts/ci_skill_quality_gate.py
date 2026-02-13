#!/usr/bin/env python3
"""Evaluate one or more skill eval scorecards and enforce tiered CI policy."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Tiered gate over skill eval scorecard JSON files.")
    p.add_argument(
        "paths",
        nargs="+",
        help="Scorecard files or directories containing scorecard.json/summary.json",
    )
    p.add_argument("--tier2-mode", choices=["warn", "fail", "off"], default="warn")
    p.add_argument("--format", choices=["text", "json"], default="text")
    return p.parse_args()


def find_scorecards(paths: List[str]) -> List[Path]:
    out: List[Path] = []
    for raw in paths:
        p = Path(raw).expanduser().resolve()
        if p.is_file():
            out.append(p)
            continue
        if p.is_dir():
            for candidate in p.rglob("scorecard.json"):
                out.append(candidate)
            for candidate in p.rglob("summary.json"):
                out.append(candidate)
    uniq = sorted(set(out))
    return uniq


def load_json(path: Path) -> Dict[str, Any]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return obj


def main() -> int:
    args = parse_args()
    scorecards = find_scorecards(args.paths)
    if not scorecards:
        print("No scorecards found.")
        return 1

    payload: Dict[str, Any] = {
        "tier2_mode": args.tier2_mode,
        "scorecards": [],
        "totals": {
            "files": 0,
            "cases": 0,
            "tier1_failed_cases": 0,
            "tier2_cases": 0,
        },
        "passed": True,
    }

    for path in scorecards:
        obj = load_json(path)
        cases = obj.get("cases") if isinstance(obj.get("cases"), list) else []

        tier1 = 0
        tier2 = 0
        for case in cases:
            if not isinstance(case, dict):
                continue
            if case.get("tier1_failed") is True:
                tier1 += 1
            if case.get("tier2_failed") is True:
                tier2 += 1

        if not cases:
            tier1 = int(obj.get("tier1_failures", 0) or 0)
            tier2 = int(obj.get("tier2_findings", 0) or 0)

        record = {
            "path": str(path),
            "skill": obj.get("skill"),
            "cases": len(cases),
            "tier1_failed_cases": tier1,
            "tier2_cases": tier2,
            "passed": tier1 == 0 and (args.tier2_mode != "fail" or tier2 == 0),
        }
        payload["scorecards"].append(record)

        payload["totals"]["files"] += 1
        payload["totals"]["cases"] += len(cases)
        payload["totals"]["tier1_failed_cases"] += tier1
        payload["totals"]["tier2_cases"] += tier2

    payload["passed"] = payload["totals"]["tier1_failed_cases"] == 0 and (
        args.tier2_mode != "fail" or payload["totals"]["tier2_cases"] == 0
    )

    if args.format == "json":
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"Scorecards: {payload['totals']['files']}")
        print(f"Cases: {payload['totals']['cases']}")
        print(f"Tier1 failed cases: {payload['totals']['tier1_failed_cases']}")
        print(f"Tier2 cases: {payload['totals']['tier2_cases']} (mode={args.tier2_mode})")
        print(f"RESULT: {'PASS' if payload['passed'] else 'FAIL'}")

    return 0 if payload["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
