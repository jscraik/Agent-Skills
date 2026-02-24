#!/usr/bin/env python3
"""Aggregate recursive loop run artifacts into Phase-2 shadow reports."""

from __future__ import annotations

import argparse
import json
import statistics
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PILOT_PROFILES = [
    "ui-ux-creative-coding",
    "interface-craft",
    "frontend-ui-design",
    "react-ui-patterns",
]

EVENT_TYPES = {
    "run_initialized",
    "run_state_changed",
    "promotion_approved",
    "failure_event",
    "run_blocked",
}


@dataclass(frozen=True)
class RunRecord:
    run_id: str
    profile_id: str
    terminal_status: str
    stop_reason: str
    finished_at: datetime
    iterations_completed: int
    tokens_used: int
    initial_overall: float
    final_overall: float
    quality_uplift: float
    critical_non_regression_passed: bool
    budget_compliant: bool
    first_pass_accepted: bool
    evaluator_flip_rate: float


@dataclass(frozen=True)
class WindowSummary:
    runs_total: int
    by_profile: Dict[str, int]
    repeat_failure_rate: float
    first_pass_acceptance_rate: float
    median_iterations: float
    p90_iterations: float
    quality_uplift_median: float
    quality_uplift_positive_rate: float
    critical_non_regression_compliance: float
    budget_compliance: float
    evaluator_flip_rate: float


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build recursive loop shadow dashboard + docs")
    p.add_argument("--runs-root", default="artifacts/skill-graphs/runs")
    p.add_argument("--window-days", type=int, default=7)
    p.add_argument("--min-runs-total", type=int, default=40)
    p.add_argument("--min-runs-per-profile", type=int, default=10)
    p.add_argument("--shadow-md", default="docs/skill-graphs/pilots/ui-skills-shadow-results.md")
    p.add_argument("--readout-md", default="docs/skill-graphs/pilots/ui-skills-pilot-readout.md")
    p.add_argument("--out-json", default="artifacts/skill-graphs/pilot/shadow-dashboard.json")
    p.add_argument("--daily-health-md", default="docs/skill-graphs/telemetry/daily-skill-health.md")
    p.add_argument("--failure-patterns-jsonl", default="artifacts/skill-graphs/telemetry/failure-pattern-candidates.jsonl")
    p.add_argument("--promotion-queue-md", default="artifacts/skill-graphs/telemetry/promotion-queue.md")
    p.add_argument("--max-run-lines", type=int, default=40)
    return p.parse_args()


def parse_iso8601(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def validate_event_envelope(events: List[Dict[str, Any]], run_id: str) -> List[str]:
    errors: List[str] = []
    required = [
        "schema_version",
        "event_id",
        "ts",
        "run_id",
        "skill_name",
        "task_profile",
        "event_type",
        "severity",
        "terminal_status",
        "stop_reason",
    ]
    for idx, row in enumerate(events, start=1):
        for key in required:
            if key not in row:
                errors.append(f"{run_id}:event#{idx} missing field {key}")
        et = str(row.get("event_type", ""))
        if et not in EVENT_TYPES:
            errors.append(f"{run_id}:event#{idx} unknown event_type {et}")
        if et == "run_blocked" and not str(row.get("blocker_code", "")).strip():
            errors.append(f"{run_id}:event#{idx} run_blocked missing blocker_code")
    return errors


def has_fail_finding(report: Dict[str, Any]) -> bool:
    findings = report.get("findings")
    if not isinstance(findings, list):
        return False
    for finding in findings:
        if isinstance(finding, dict) and str(finding.get("severity", "")).lower() == "fail":
            return True
    return False


def load_run_record(run_dir: Path) -> Optional[RunRecord]:
    run_path = run_dir / "run.json"
    journal_path = run_dir / "iteration_journal.jsonl"
    if not run_path.exists() or not journal_path.exists():
        return None

    run = load_json(run_path)
    profile_id = str(run.get("profile_id", "")).strip()
    if profile_id not in PILOT_PROFILES:
        return None

    journals = load_jsonl(journal_path)
    if not journals:
        return None

    first = journals[0]
    last = journals[-1]
    initial_overall = safe_float(first.get("evaluation_report", {}).get("overall_score"), 0.0)
    final_overall = safe_float(last.get("reevaluation_report", {}).get("overall_score"), initial_overall)

    flip_count = 0
    for row in journals:
        before = has_fail_finding(row.get("evaluation_report", {}))
        after = has_fail_finding(row.get("reevaluation_report", {}))
        if before != after:
            flip_count += 1

    iter_count = max(1, safe_int(run.get("counters", {}).get("iterations_completed"), len(journals)))
    non_regression_all = all(
        bool(row.get("reevaluation_report", {}).get("non_regression_passed", False)) for row in journals
    )

    terminal_status = str(run.get("terminal_status", "failed"))
    stop_reason = str(run.get("stop_reason", "policy_failed"))

    return RunRecord(
        run_id=str(run.get("run_id", run_dir.name)),
        profile_id=profile_id,
        terminal_status=terminal_status,
        stop_reason=stop_reason,
        finished_at=parse_iso8601(str(run.get("finished_at"))),
        iterations_completed=iter_count,
        tokens_used=safe_int(run.get("counters", {}).get("tokens_used"), 0),
        initial_overall=initial_overall,
        final_overall=final_overall,
        quality_uplift=round(final_overall - initial_overall, 3),
        critical_non_regression_passed=non_regression_all,
        budget_compliant=stop_reason != "budget_exhausted",
        first_pass_accepted=terminal_status == "passed" and iter_count == 1,
        evaluator_flip_rate=round(flip_count / len(journals), 3),
    )


def percentile(values: List[float], p: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return float(ordered[0])
    idx = (len(ordered) - 1) * p
    lo = int(idx)
    hi = min(lo + 1, len(ordered) - 1)
    frac = idx - lo
    return ordered[lo] * (1 - frac) + ordered[hi] * frac


def summarize(records: List[RunRecord]) -> WindowSummary:
    if not records:
        return WindowSummary(
            runs_total=0,
            by_profile={p: 0 for p in PILOT_PROFILES},
            repeat_failure_rate=0.0,
            first_pass_acceptance_rate=0.0,
            median_iterations=0.0,
            p90_iterations=0.0,
            quality_uplift_median=0.0,
            quality_uplift_positive_rate=0.0,
            critical_non_regression_compliance=0.0,
            budget_compliance=0.0,
            evaluator_flip_rate=0.0,
        )

    by_profile = {p: 0 for p in PILOT_PROFILES}
    for r in records:
        by_profile[r.profile_id] = by_profile.get(r.profile_id, 0) + 1

    total = len(records)
    failures = sum(1 for r in records if r.terminal_status != "passed")
    first_pass = sum(1 for r in records if r.first_pass_accepted)
    positive_uplift = sum(1 for r in records if r.quality_uplift > 0)
    non_reg_ok = sum(1 for r in records if r.critical_non_regression_passed)
    budget_ok = sum(1 for r in records if r.budget_compliant)

    iteration_values = [float(r.iterations_completed) for r in records]
    uplift_values = [r.quality_uplift for r in records]
    flip_values = [r.evaluator_flip_rate for r in records]

    return WindowSummary(
        runs_total=total,
        by_profile=by_profile,
        repeat_failure_rate=round(failures / total, 4),
        first_pass_acceptance_rate=round(first_pass / total, 4),
        median_iterations=round(statistics.median(iteration_values), 3),
        p90_iterations=round(percentile(iteration_values, 0.9), 3),
        quality_uplift_median=round(statistics.median(uplift_values), 4),
        quality_uplift_positive_rate=round(positive_uplift / total, 4),
        critical_non_regression_compliance=round(non_reg_ok / total, 4),
        budget_compliance=round(budget_ok / total, 4),
        evaluator_flip_rate=round(sum(flip_values) / total, 4),
    )



def fmt_pct(v: Optional[float]) -> str:
    if v is None:
        return "n/a"
    return f"{v * 100:.1f}%"


def fmt_pp(v: Optional[float]) -> str:
    if v is None:
        return "n/a"
    return f"{v * 100:+.1f}pp"


def fmt_float(v: Optional[float], digits: int = 2) -> str:
    if v is None:
        return "n/a"
    return f"{v:.{digits}f}"


def gate_decision(
    *,
    current: WindowSummary,
    baseline: Optional[WindowSummary],
    min_runs_total: int,
    min_runs_per_profile: int,
) -> Tuple[str, List[str]]:
    reasons: List[str] = []

    if current.runs_total < min_runs_total:
        reasons.append(f"insufficient sample size ({current.runs_total}/{min_runs_total})")

    for profile, count in current.by_profile.items():
        if count < min_runs_per_profile:
            reasons.append(f"{profile} below required run count ({count}/{min_runs_per_profile})")

    if current.critical_non_regression_compliance < 1.0:
        reasons.append("critical non-regression compliance below 100%")

    if current.budget_compliance < 0.95:
        reasons.append("budget compliance below 95%")

    if current.quality_uplift_median < 0.12:
        reasons.append("quality uplift median below +0.12")

    if baseline is None or baseline.runs_total == 0:
        reasons.append("baseline window unavailable for delta KPIs")
    else:
        first_pass_delta = current.first_pass_acceptance_rate - baseline.first_pass_acceptance_rate
        failure_delta = current.repeat_failure_rate - baseline.repeat_failure_rate
        if first_pass_delta < 0.20:
            reasons.append("first-pass acceptance delta below +20pp")
        if failure_delta > -0.35:
            reasons.append("repeat failure pattern reduction below 35%")

    return ("GO" if not reasons else "HOLD", reasons)


def render_shadow_md(
    *,
    current_records: List[RunRecord],
    current_summary: WindowSummary,
    baseline_summary: Optional[WindowSummary],
    current_window: str,
    max_run_lines: int,
) -> str:
    lines: List[str] = []
    lines.append("# UI Skills Shadow Results (Phase 2)")
    lines.append("")
    lines.append("Shadow mode runs evaluator + checkpoint adversarial checks without automatic improvement writes.")
    lines.append("")
    lines.append("## Table of Contents")
    lines.append("")
    lines.append("- [Pilot scope](#pilot-scope)")
    lines.append("- [Window summary](#window-summary)")
    lines.append("- [Run log](#run-log)")
    lines.append("- [Exit gate checks](#exit-gate-checks)")
    lines.append("")
    lines.append("## Pilot scope")
    lines.append("")
    for profile in PILOT_PROFILES:
        lines.append(f"- `{profile}`")
    lines.append("")
    lines.append("## Window summary")
    lines.append("")
    lines.append(f"- Window: `{current_window}`")
    lines.append(f"- Runs total: `{current_summary.runs_total}`")
    lines.append("- Runs by profile:")
    for profile, count in current_summary.by_profile.items():
        lines.append(f"  - `{profile}`: `{count}`")
    lines.append("")

    first_pass_delta = None
    failure_delta = None
    if baseline_summary is not None and baseline_summary.runs_total > 0:
        first_pass_delta = current_summary.first_pass_acceptance_rate - baseline_summary.first_pass_acceptance_rate
        failure_delta = current_summary.repeat_failure_rate - baseline_summary.repeat_failure_rate

    lines.append("### KPI snapshot")
    lines.append("")
    lines.append(f"- Repeat failure pattern rate: `{fmt_pct(current_summary.repeat_failure_rate)}` (delta vs baseline: `{fmt_pp(failure_delta)}`)")
    lines.append(f"- First-pass acceptance: `{fmt_pct(current_summary.first_pass_acceptance_rate)}` (delta vs baseline: `{fmt_pp(first_pass_delta)}`)")
    lines.append(
        f"- Iterations median / p90: `{fmt_float(current_summary.median_iterations, 2)}` / `{fmt_float(current_summary.p90_iterations, 2)}`"
    )
    lines.append(
        f"- Quality uplift median: `{fmt_float(current_summary.quality_uplift_median, 3)}`; positive uplift rate: `{fmt_pct(current_summary.quality_uplift_positive_rate)}`"
    )
    lines.append(f"- Critical non-regression compliance: `{fmt_pct(current_summary.critical_non_regression_compliance)}`")
    lines.append(f"- Budget compliance: `{fmt_pct(current_summary.budget_compliance)}`")
    lines.append(f"- Evaluator flip rate: `{fmt_pct(current_summary.evaluator_flip_rate)}`")
    lines.append("")

    lines.append("## Run log")
    lines.append("")
    lines.append("| Run | Profile | Status | Stop reason | Iterations | Uplift | Non-regression | Tokens |")
    lines.append("|---|---|---|---|---:|---:|:---:|---:|")
    for record in current_records[:max_run_lines]:
        lines.append(
            "| "
            f"{record.run_id} | {record.profile_id} | {record.terminal_status} | {record.stop_reason} | "
            f"{record.iterations_completed} | {record.quality_uplift:+.3f} | "
            f"{'✅' if record.critical_non_regression_passed else '❌'} | {record.tokens_used} |"
        )
    if not current_records:
        lines.append("| _none_ | - | - | - | 0 | 0.000 | - | 0 |")
    lines.append("")

    lines.append("## Exit gate checks")
    lines.append("")
    lines.append("- Scoring variance + evaluator consistency observed in this window.")
    lines.append("- Failure taxonomy and stop reasons captured per run.")
    lines.append("- Governance/security controls remain required before promotions.")
    lines.append("")
    lines.append("Related:")
    lines.append("- [UI skills pilot readout](/docs/skill-graphs/pilots/ui-skills-pilot-readout.md)")

    return "\n".join(lines) + "\n"


def render_readout_md(
    *,
    current_summary: WindowSummary,
    baseline_summary: Optional[WindowSummary],
    current_window: str,
    decision: str,
    reasons: List[str],
) -> str:
    first_pass_delta = None
    failure_delta = None
    if baseline_summary is not None and baseline_summary.runs_total > 0:
        first_pass_delta = current_summary.first_pass_acceptance_rate - baseline_summary.first_pass_acceptance_rate
        failure_delta = current_summary.repeat_failure_rate - baseline_summary.repeat_failure_rate

    lines: List[str] = []
    lines.append("# UI Skills Pilot Readout")
    lines.append("")
    lines.append("Use this page to record expansion-gate evidence after pilot runs.")
    lines.append("")
    lines.append("## Table of Contents")
    lines.append("")
    lines.append("- [Readout metadata](#readout-metadata)")
    lines.append("- [Scorecard](#scorecard)")
    lines.append("- [Gate decision](#gate-decision)")
    lines.append("- [Follow-ups](#follow-ups)")
    lines.append("")

    lines.append("## Readout metadata")
    lines.append("")
    lines.append(f"- Window: `{current_window}`")
    lines.append(f"- Total runs: `{current_summary.runs_total}`")
    lines.append("- Runs per profile:")
    for profile, count in current_summary.by_profile.items():
        lines.append(f"  - `{profile}`: `{count}`")
    lines.append("- Reviewer(s): `_pending_`")
    lines.append("")

    lines.append("## Scorecard")
    lines.append("")
    lines.append(
        f"- Repeat failure pattern rate delta: `{fmt_pp(failure_delta)}` (target: `<= -35.0pp` reduction)"
    )
    lines.append(
        f"- First-pass acceptance delta: `{fmt_pp(first_pass_delta)}` (target: `>= +20.0pp`)"
    )
    lines.append(
        f"- Iterations median / p90: `{fmt_float(current_summary.median_iterations, 2)}` / `{fmt_float(current_summary.p90_iterations, 2)}` (target: `<=2 / <=4`)"
    )
    lines.append(
        f"- Quality uplift median: `{fmt_float(current_summary.quality_uplift_median, 3)}` (target: `>= +0.120`)"
    )
    lines.append(
        f"- Critical non-regression compliance: `{fmt_pct(current_summary.critical_non_regression_compliance)}` (target: `100.0%`)"
    )
    lines.append(
        f"- Budget compliance: `{fmt_pct(current_summary.budget_compliance)}` (target: `>=95.0%`)"
    )
    lines.append("- Reviewer overhead median / p90: `n/a / n/a` (not captured in MVP telemetry yet)")
    lines.append("")

    lines.append("## Gate decision")
    lines.append("")
    lines.append(f"- Decision: `{decision}`")
    lines.append("- Reason:")
    if reasons:
        for reason in reasons:
            lines.append(f"  - {reason}")
    else:
        lines.append("  - all gate conditions passed")
    lines.append("")

    lines.append("## Follow-ups")
    lines.append("")
    lines.append("- Owner: `_pending_`")
    lines.append("- Due date: `_pending_`")
    lines.append("- Tracking issue/doc: `_pending_`")

    return "\n".join(lines) + "\n"


def to_dict(summary: WindowSummary) -> Dict[str, Any]:
    return {
        "runs_total": summary.runs_total,
        "by_profile": summary.by_profile,
        "repeat_failure_rate": summary.repeat_failure_rate,
        "first_pass_acceptance_rate": summary.first_pass_acceptance_rate,
        "median_iterations": summary.median_iterations,
        "p90_iterations": summary.p90_iterations,
        "quality_uplift_median": summary.quality_uplift_median,
        "quality_uplift_positive_rate": summary.quality_uplift_positive_rate,
        "critical_non_regression_compliance": summary.critical_non_regression_compliance,
        "budget_compliance": summary.budget_compliance,
        "evaluator_flip_rate": summary.evaluator_flip_rate,
    }


def main() -> int:
    args = parse_args()

    runs_root = Path(args.runs_root).expanduser().resolve()
    repo_root = Path.cwd().resolve()
    run_records: List[RunRecord] = []
    skipped_runs: List[Dict[str, str]] = []
    event_errors: List[str] = []
    promotion_approved_by_run: Dict[str, bool] = {}

    for run_dir in sorted(runs_root.glob("run_*")):
        if not run_dir.is_dir():
            continue
        try:
            record = load_run_record(run_dir)
        except Exception as exc:
            run_dir_out = (
                str(run_dir.relative_to(repo_root))
                if run_dir.is_relative_to(repo_root)
                else str(run_dir)
            )
            skipped_runs.append({"run_dir": run_dir_out, "reason": str(exc)})
            continue
        if record is not None:
            run_records.append(record)
            events_path = run_dir / "events.jsonl"
            if not events_path.exists():
                event_errors.append(f"{record.run_id}: missing events.jsonl")
                promotion_approved_by_run[record.run_id] = False
            else:
                try:
                    events = load_jsonl(events_path)
                    event_errors.extend(validate_event_envelope(events, record.run_id))
                    promotion_approved_by_run[record.run_id] = any(
                        e.get("event_type") == "promotion_approved" for e in events
                    )
                except Exception as exc:
                    event_errors.append(f"{record.run_id}: invalid events.jsonl ({exc})")
                    promotion_approved_by_run[record.run_id] = False

    run_records.sort(key=lambda r: r.finished_at, reverse=True)

    if run_records:
        latest = max(r.finished_at for r in run_records)
    else:
        latest = datetime.now(timezone.utc)

    window_days = max(1, args.window_days)
    current_start = latest - timedelta(days=window_days - 1)
    baseline_start = current_start - timedelta(days=window_days)

    current_records = [r for r in run_records if r.finished_at >= current_start]
    baseline_records = [r for r in run_records if baseline_start <= r.finished_at < current_start]

    current_summary = summarize(current_records)
    baseline_summary = summarize(baseline_records) if baseline_records else None

    decision, reasons = gate_decision(
        current=current_summary,
        baseline=baseline_summary,
        min_runs_total=args.min_runs_total,
        min_runs_per_profile=args.min_runs_per_profile,
    )

    current_window = f"{current_start.date().isoformat()}..{latest.date().isoformat()}"

    shadow_md_text = render_shadow_md(
        current_records=current_records,
        current_summary=current_summary,
        baseline_summary=baseline_summary,
        current_window=current_window,
        max_run_lines=args.max_run_lines,
    )

    readout_md_text = render_readout_md(
        current_summary=current_summary,
        baseline_summary=baseline_summary,
        current_window=current_window,
        decision=decision,
        reasons=reasons,
    )

    shadow_md_path = Path(args.shadow_md).expanduser().resolve()
    readout_md_path = Path(args.readout_md).expanduser().resolve()
    out_json_path = Path(args.out_json).expanduser().resolve()
    daily_health_path = Path(args.daily_health_md).expanduser().resolve()
    failure_patterns_path = Path(args.failure_patterns_jsonl).expanduser().resolve()
    promotion_queue_path = Path(args.promotion_queue_md).expanduser().resolve()

    shadow_md_path.parent.mkdir(parents=True, exist_ok=True)
    readout_md_path.parent.mkdir(parents=True, exist_ok=True)
    out_json_path.parent.mkdir(parents=True, exist_ok=True)
    daily_health_path.parent.mkdir(parents=True, exist_ok=True)
    failure_patterns_path.parent.mkdir(parents=True, exist_ok=True)
    promotion_queue_path.parent.mkdir(parents=True, exist_ok=True)

    shadow_md_path.write_text(shadow_md_text, encoding="utf-8")
    readout_md_path.write_text(readout_md_text, encoding="utf-8")

    dashboard = {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "runs_root": (
            str(runs_root.relative_to(repo_root))
            if runs_root.is_relative_to(repo_root)
            else str(runs_root)
        ),
        "pilot_profiles": PILOT_PROFILES,
        "window_days": window_days,
        "current_window": current_window,
        "current": to_dict(current_summary),
        "baseline": to_dict(baseline_summary) if baseline_summary else None,
        "decision": {
            "state": decision,
            "reasons": reasons,
        },
        "event_envelope_errors": event_errors,
        "recent_runs": [
            {
                "run_id": r.run_id,
                "profile_id": r.profile_id,
                "terminal_status": r.terminal_status,
                "stop_reason": r.stop_reason,
                "iterations_completed": r.iterations_completed,
                "quality_uplift": r.quality_uplift,
                "critical_non_regression_passed": r.critical_non_regression_passed,
                "tokens_used": r.tokens_used,
                "finished_at": r.finished_at.isoformat().replace("+00:00", "Z"),
            }
            for r in current_records
        ],
        "skipped_runs": skipped_runs,
    }

    out_json_path.write_text(json.dumps(dashboard, indent=2), encoding="utf-8")

    daily_lines: List[str] = [
        "# Daily Skill Health",
        "",
        f"- Generated at: `{dashboard['generated_at']}`",
        f"- Window: `{current_window}`",
        f"- Runs total: `{current_summary.runs_total}`",
        f"- Decision: `{decision}`",
        f"- Critical non-regression compliance: `{fmt_pct(current_summary.critical_non_regression_compliance)}`",
        f"- Budget compliance: `{fmt_pct(current_summary.budget_compliance)}`",
        f"- Event envelope errors: `{len(event_errors)}`",
        "",
    ]
    if event_errors:
        daily_lines.append("## Event envelope errors")
        daily_lines.append("")
        for err in event_errors[:50]:
            daily_lines.append(f"- {err}")
        daily_lines.append("")
    daily_health_path.write_text("\n".join(daily_lines) + "\n", encoding="utf-8")

    failure_rows: List[Dict[str, Any]] = []
    for r in current_records:
        if r.terminal_status != "passed" or r.stop_reason != "pass":
            failure_rows.append(
                {
                    "schema_version": "1.0",
                    "run_id": r.run_id,
                    "profile_id": r.profile_id,
                    "terminal_status": r.terminal_status,
                    "stop_reason": r.stop_reason,
                    "iterations_completed": r.iterations_completed,
                    "quality_uplift": r.quality_uplift,
                    "finished_at": r.finished_at.isoformat().replace("+00:00", "Z"),
                }
            )
    failure_patterns_path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in failure_rows),
        encoding="utf-8",
    )

    queue_lines = ["# Promotion Queue", ""]
    queue_items = [
        r for r in current_records
        if r.terminal_status == "passed" and not promotion_approved_by_run.get(r.run_id, False)
    ]
    if not queue_items:
        queue_lines.append("- No pending promotions in window.")
    else:
        for r in queue_items:
            queue_lines.append(
                f"- `{r.run_id}` | profile `{r.profile_id}` | finished `{r.finished_at.isoformat().replace('+00:00', 'Z')}`"
            )
    queue_lines.append("")
    promotion_queue_path.write_text("\n".join(queue_lines), encoding="utf-8")

    print(f"[shadow-report] runs={len(run_records)} current_runs={len(current_records)}")
    print(f"[shadow-report] decision={decision}")
    print(f"[shadow-report] shadow_md={shadow_md_path}")
    print(f"[shadow-report] readout_md={readout_md_path}")
    print(f"[shadow-report] out_json={out_json_path}")
    print(f"[shadow-report] daily_health={daily_health_path}")
    print(f"[shadow-report] failure_patterns={failure_patterns_path}")
    print(f"[shadow-report] promotion_queue={promotion_queue_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
