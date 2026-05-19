#!/usr/bin/env python3
"""Build a baseline/regression dashboard from skill eval scorecards."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from eval_signal_contract import (
    EXPECTED_SIGNAL_COMPOSITE_KEY,
    EXPECTED_SIGNAL_FORBIDDEN_FOUND_KEY,
    EXPECTED_SIGNAL_METRIC_KEY,
    EXPECTED_SIGNAL_MISSING_KEY,
    EXPECTED_SIGNAL_RISK_FACTORS_KEY,
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Aggregate skill eval scorecards into dashboard JSON/Markdown.")
    p.add_argument("--reports-root", default="Infrastructure/artifacts/skills", help="Base directory containing <skill>/<run_id>/scorecard.json")
    p.add_argument("--out-json", default="Infrastructure/artifacts/skills/dashboard.json")
    p.add_argument("--out-md", default="Infrastructure/artifacts/skills/dashboard.md")
    return p.parse_args()


def _to_int(value: Any) -> int:
    if isinstance(value, bool):
        return 0
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        try:
            return int(value.strip())
        except Exception:
            return 0
    return 0


def _as_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def load_scorecard(path: Path) -> Dict[str, Any]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise ValueError(f"Invalid scorecard object: {path}")
    obj["_path"] = str(path)
    return obj


def collect_scorecards(root: Path) -> Dict[str, List[Tuple[str, Dict[str, Any]]]]:
    by_skill: Dict[str, List[Tuple[str, Dict[str, Any]]]] = {}
    for scorecard_path in sorted([*root.rglob("scorecard.json"), *root.rglob("latest-scorecard.json")]):
        # expected path: <root>/<skill>/<run_id>/scorecard.json
        # or <root>/<skill>/latest-scorecard.json from ask eval-baseline.
        parts = scorecard_path.parts
        try:
            idx = parts.index("skills")
            skill = parts[idx + 1]
            run_id = "latest" if scorecard_path.name == "latest-scorecard.json" else parts[idx + 2]
        except Exception:
            if scorecard_path.name == "latest-scorecard.json":
                skill = scorecard_path.parent.name
                run_id = "latest"
            else:
                skill = scorecard_path.parent.parent.name
                run_id = scorecard_path.parent.name

        obj = load_scorecard(scorecard_path)
        by_skill.setdefault(skill, []).append((run_id, obj))

    for skill, runs in by_skill.items():
        runs.sort(key=lambda x: x[0])

    return by_skill


def summarize_expected_signals(cases: List[Any]) -> Dict[str, Any]:
    scores: List[int] = []
    risky_cases: List[Dict[str, Any]] = []
    missing_count = 0
    forbidden_count = 0

    for case in cases:
        if not isinstance(case, dict):
            continue
        case_risks: List[str] = []
        for runner in _as_dict(case.get("runners")).values():
            if not isinstance(runner, dict):
                continue
            expected = _as_dict(_as_dict(runner.get("metrics")).get(EXPECTED_SIGNAL_METRIC_KEY))
            score = expected.get(EXPECTED_SIGNAL_COMPOSITE_KEY)
            if isinstance(score, int):
                scores.append(score)
            risks = [str(item) for item in _as_list(expected.get(EXPECTED_SIGNAL_RISK_FACTORS_KEY))]
            missing = _as_list(expected.get(EXPECTED_SIGNAL_MISSING_KEY))
            forbidden = _as_list(expected.get(EXPECTED_SIGNAL_FORBIDDEN_FOUND_KEY))
            missing_count += len(missing)
            forbidden_count += len(forbidden)
            case_risks.extend(risks)
            if missing:
                case_risks.append(f"missing signals: {len(missing)}")
            if forbidden:
                case_risks.append(f"forbidden signals: {len(forbidden)}")
        if case_risks:
            risky_cases.append({
                "case": case.get("id") or case.get("name") or "case",
                EXPECTED_SIGNAL_RISK_FACTORS_KEY: case_risks[:4],
            })

    return {
        "runs": len(scores),
        "average": round(sum(scores) / len(scores)) if scores else None,
        "minimum": min(scores) if scores else None,
        "missing_signal_count": missing_count,
        "forbidden_signal_count": forbidden_count,
        "risky_cases": risky_cases,
    }


def summarize_run(obj: Dict[str, Any]) -> Dict[str, Any]:
    cases = obj.get("cases") if isinstance(obj.get("cases"), list) else []
    tier1 = 0
    tier2 = 0
    passed = 0
    for case in cases:
        if not isinstance(case, dict):
            continue
        if case.get("passed") is True:
            passed += 1
        if case.get("tier1_failed") is True:
            tier1 += 1
        if case.get("tier2_failed") is True:
            tier2 += 1

    if not cases:
        tier1 = _to_int(obj.get("tier1_failures", 0))
        tier2 = _to_int(obj.get("tier2_findings", 0))

    expected_signal_summary = _as_dict(obj.get("expected_signal_summary")) or summarize_expected_signals(cases)

    return {
        "runner_mode": obj.get("runner_mode"),
        "tier2_mode": obj.get("tier2_mode"),
        "cases": len(cases),
        "passed_cases": passed,
        "tier1_failed_cases": tier1,
        "tier2_cases": tier2,
        "passed": bool(obj.get("passed", tier1 == 0)),
        "path": obj.get("_path"),
        "expected_signal_summary": expected_signal_summary,
    }


def build_dashboard(by_skill: Dict[str, List[Tuple[str, Dict[str, Any]]]]) -> Dict[str, Any]:
    dashboard: Dict[str, Any] = {
        "skills": {},
        "totals": {
            "skills": 0,
            "runs": 0,
            "latest_tier1_failed_skills": 0,
            "latest_tier2_skills": 0,
        },
    }

    for skill, runs in sorted(by_skill.items()):
        entries = [{"run_id": run_id, **summarize_run(obj)} for run_id, obj in runs]
        latest = entries[-1] if entries else None
        previous = entries[-2] if len(entries) >= 2 else None

        trend = None
        if latest and previous:
            trend = {
                "tier1_delta": latest["tier1_failed_cases"] - previous["tier1_failed_cases"],
                "tier2_delta": latest["tier2_cases"] - previous["tier2_cases"],
                "pass_delta": int(latest["passed"]) - int(previous["passed"]),
            }

        dashboard["skills"][skill] = {
            "latest": latest,
            "previous": previous,
            "trend": trend,
            "runs": entries,
        }

        dashboard["totals"]["skills"] += 1
        dashboard["totals"]["runs"] += len(entries)
        if latest and latest["tier1_failed_cases"] > 0:
            dashboard["totals"]["latest_tier1_failed_skills"] += 1
        if latest and latest["tier2_cases"] > 0:
            dashboard["totals"]["latest_tier2_skills"] += 1

    return dashboard


def to_markdown(dashboard: Dict[str, Any]) -> str:
    lines: List[str] = []
    totals = dashboard["totals"]

    lines.append("# Skill Quality Dashboard")
    lines.append("")
    lines.append(f"- Skills: {totals['skills']}")
    lines.append(f"- Runs: {totals['runs']}")
    lines.append(f"- Latest tier1-failing skills: {totals['latest_tier1_failed_skills']}")
    lines.append(f"- Latest tier2-findings skills: {totals['latest_tier2_skills']}")
    lines.append("")
    lines.append("## Latest by skill")
    lines.append("")
    lines.append("| Skill | Cases | Tier1 failed | Tier2 | Expected signals | Passed | Trend (tier1/tier2) |")
    lines.append("|---|---:|---:|---:|---:|:---:|---:|")

    for skill, record in sorted(dashboard["skills"].items()):
        latest = record.get("latest") or {}
        trend = record.get("trend") or {}
        trend_text = "-"
        if trend:
            trend_text = f"{trend.get('tier1_delta', 0)}/{trend.get('tier2_delta', 0)}"
        signal_summary = latest.get("expected_signal_summary") if isinstance(latest, dict) else {}
        signal_average = _as_dict(signal_summary).get("average")
        signal_text = f"{signal_average}%" if isinstance(signal_average, int) else "-"

        lines.append(
            "| "
            + f"{skill} | {latest.get('cases', 0)} | {latest.get('tier1_failed_cases', 0)} | {latest.get('tier2_cases', 0)} | {signal_text} | "
            + ("✅" if latest.get("passed") else "❌")
            + f" | {trend_text} |"
        )

    lines.append("")
    lines.append("## Promotion policy reminder")
    lines.append("")
    lines.append("- Week 0: report-only baseline")
    lines.append("- Weeks 1-2: tier1 hard fail, tier2 warn")
    lines.append("- Week 3+: promote stable tier2 checks to fail")
    lines.append("")

    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    reports_root = Path(args.reports_root).expanduser().resolve()

    by_skill = collect_scorecards(reports_root)
    dashboard = build_dashboard(by_skill)

    out_json = Path(args.out_json).expanduser().resolve()
    out_md = Path(args.out_md).expanduser().resolve()
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)

    out_json.write_text(json.dumps(dashboard, indent=2, ensure_ascii=False), encoding="utf-8")
    out_md.write_text(to_markdown(dashboard), encoding="utf-8")

    print(f"Dashboard JSON: {out_json}")
    print(f"Dashboard MD: {out_md}")
    print(f"Skills: {dashboard['totals']['skills']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
