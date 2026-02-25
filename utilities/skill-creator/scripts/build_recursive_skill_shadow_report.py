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

DEFAULT_PILOT_PROFILES = [
    "ui-ux-creative-coding",
    "interface-craft",
    "frontend-ui-design",
    "react-ui-patterns",
]
PILOT_PROFILES = list(DEFAULT_PILOT_PROFILES)

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
    confidence_score: Optional[float]
    confidence_bucket: Optional[str]
    evidence_completeness_score: Optional[float]
    candidate_count: int
    capture_record_present: bool
    rollout_mode: str
    auto_capture_enabled: bool
    auto_apply_enabled: bool
    injected_lesson_count: int
    retrieved_lesson_count: int
    injection_suppressed: bool
    uplift_promotion_decision: Optional[str]
    uplift_auto_apply_decision: Optional[str]
    uplift_sample_size: Optional[int]


@dataclass(frozen=True)
class RunMeta:
    run_id: str
    profile_id: str
    finished_at: datetime
    run_dir: Path


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
    capture_records_written: int
    capture_coverage_rate: float
    auto_capture_enabled_rate: float
    auto_apply_enabled_rate: float
    confidence_bucket_counts: Dict[str, int]
    confidence_bucket_distribution: Dict[str, float]
    runs_with_injection: int
    runs_with_retrieved_lessons: int
    suppressed_injection_runs: int
    injection_usage_rate: float
    total_injected_lessons: int
    average_injected_lessons_per_run: float
    rollout_mode_counts: Dict[str, int]
    uplift_promotion_decision_counts: Dict[str, int]
    uplift_auto_apply_decision_counts: Dict[str, int]


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
    p.add_argument("--pilot-profiles-file", default="docs/skill-graphs/schemas/examples/pilot-profiles.json")
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


def load_pilot_profiles(path: Path) -> List[str]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("pilot profiles file must be a JSON array")
    profiles = [str(item).strip() for item in raw if str(item).strip()]
    if not profiles:
        raise ValueError("pilot profiles file must include at least one profile id")
    return profiles


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
    promotion_path = run_dir / "promotion_decision.json"
    confidence_score: Optional[float] = None
    confidence_bucket: Optional[str] = None
    evidence_completeness_score: Optional[float] = None
    candidate_count = 0
    capture_record_present = (run_dir / "capture_record.json").exists()
    runtime_controls = run.get("runtime_controls", {}) if isinstance(run.get("runtime_controls"), dict) else {}
    rollout_mode = str(runtime_controls.get("rollout_mode", "observe_only")).strip() or "observe_only"
    auto_capture_enabled = bool(runtime_controls.get("auto_capture_enabled", True))
    auto_apply_enabled = bool(runtime_controls.get("auto_apply_enabled", rollout_mode == "active"))
    injected_lesson_count = 0
    injected_lessons = run.get("injected_lessons")
    if isinstance(injected_lessons, list):
        injected_lesson_count = len(injected_lessons)
    retrieved_lesson_count = 0
    injection_summary = run.get("injection_summary", {}) if isinstance(run.get("injection_summary"), dict) else {}
    if "retrieved_count" in injection_summary:
        retrieved_lesson_count = safe_int(injection_summary.get("retrieved_count"), 0)
    else:
        retrieved_lessons = run.get("retrieved_lessons")
        if isinstance(retrieved_lessons, list):
            retrieved_lesson_count = len(retrieved_lessons)
    injection_suppressed = bool(injection_summary.get("suppressed_by_controls", False))
    uplift_obj_run = run.get("counterfactual_uplift", {}) if isinstance(run.get("counterfactual_uplift"), dict) else {}
    uplift_promotion_decision: Optional[str] = None
    uplift_auto_apply_decision: Optional[str] = None
    uplift_sample_size: Optional[int] = None
    if promotion_path.exists():
        promotion = load_json(promotion_path)
        conf = promotion.get("confidence", {}) if isinstance(promotion.get("confidence"), dict) else {}
        if "score" in conf:
            confidence_score = safe_float(conf.get("score"), 0.0)
        bucket_raw = str(conf.get("bucket", "")).strip()
        confidence_bucket = bucket_raw or None
        if "evidence_completeness" in conf:
            evidence_completeness_score = safe_float(conf.get("evidence_completeness"), 0.0)
        elif isinstance(promotion.get("evidence_packet"), dict):
            evidence_completeness_score = safe_float(
                promotion.get("evidence_packet", {}).get("completeness_score"), 0.0
            )
        candidates = promotion.get("lesson_candidates")
        if isinstance(candidates, list):
            candidate_count = len(candidates)
        uplift_obj = (
            promotion.get("counterfactual_uplift", {})
            if isinstance(promotion.get("counterfactual_uplift"), dict)
            else uplift_obj_run
        )
    else:
        uplift_obj = uplift_obj_run

    if isinstance(uplift_obj, dict):
        promotion_state = str(uplift_obj.get("promotion_decision", "")).strip().lower()
        auto_apply_state = str(uplift_obj.get("auto_apply_decision", "")).strip().lower()
        uplift_promotion_decision = promotion_state or None
        uplift_auto_apply_decision = auto_apply_state or None
        if "sample_size" in uplift_obj:
            uplift_sample_size = safe_int(uplift_obj.get("sample_size"), 0)

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
        confidence_score=confidence_score,
        confidence_bucket=confidence_bucket,
        evidence_completeness_score=evidence_completeness_score,
        candidate_count=candidate_count,
        capture_record_present=capture_record_present,
        rollout_mode=rollout_mode,
        auto_capture_enabled=auto_capture_enabled,
        auto_apply_enabled=auto_apply_enabled,
        injected_lesson_count=injected_lesson_count,
        retrieved_lesson_count=retrieved_lesson_count,
        injection_suppressed=injection_suppressed,
        uplift_promotion_decision=uplift_promotion_decision,
        uplift_auto_apply_decision=uplift_auto_apply_decision,
        uplift_sample_size=uplift_sample_size,
    )


def load_run_meta(run_dir: Path) -> Optional[RunMeta]:
    run_path = run_dir / "run.json"
    if not run_path.exists():
        return None
    run = load_json(run_path)
    profile_id = str(run.get("profile_id", "")).strip()
    if profile_id not in PILOT_PROFILES:
        return None
    finished_raw = str(run.get("finished_at", "")).strip()
    if not finished_raw:
        raise ValueError("run.json missing finished_at")
    finished_at = parse_iso8601(finished_raw)
    run_id = str(run.get("run_id", run_dir.name))
    return RunMeta(run_id=run_id, profile_id=profile_id, finished_at=finished_at, run_dir=run_dir)


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
            capture_records_written=0,
            capture_coverage_rate=0.0,
            auto_capture_enabled_rate=0.0,
            auto_apply_enabled_rate=0.0,
            confidence_bucket_counts={"high": 0, "medium": 0, "low": 0, "unknown": 0},
            confidence_bucket_distribution={"high": 0.0, "medium": 0.0, "low": 0.0, "unknown": 0.0},
            runs_with_injection=0,
            runs_with_retrieved_lessons=0,
            suppressed_injection_runs=0,
            injection_usage_rate=0.0,
            total_injected_lessons=0,
            average_injected_lessons_per_run=0.0,
            rollout_mode_counts={"off": 0, "observe_only": 0, "active": 0, "other": 0},
            uplift_promotion_decision_counts={
                "pass": 0,
                "hold": 0,
                "regressed": 0,
                "insufficient_data": 0,
                "insufficient_match_quality": 0,
                "unknown": 0,
            },
            uplift_auto_apply_decision_counts={
                "pass": 0,
                "hold": 0,
                "regressed": 0,
                "insufficient_data": 0,
                "insufficient_match_quality": 0,
                "unknown": 0,
            },
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
    capture_records_written = sum(1 for r in records if r.capture_record_present)
    auto_capture_enabled_runs = sum(1 for r in records if r.auto_capture_enabled)
    auto_apply_enabled_runs = sum(1 for r in records if r.auto_apply_enabled)
    confidence_bucket_counts = {"high": 0, "medium": 0, "low": 0, "unknown": 0}
    for r in records:
        bucket = (r.confidence_bucket or "unknown").strip().lower()
        if bucket not in confidence_bucket_counts:
            bucket = "unknown"
        confidence_bucket_counts[bucket] += 1
    confidence_bucket_distribution = {
        k: round(v / total, 4)
        for k, v in confidence_bucket_counts.items()
    }
    runs_with_injection = sum(1 for r in records if r.injected_lesson_count > 0)
    runs_with_retrieved_lessons = sum(1 for r in records if r.retrieved_lesson_count > 0)
    suppressed_injection_runs = sum(1 for r in records if r.injection_suppressed)
    total_injected_lessons = sum(max(0, r.injected_lesson_count) for r in records)
    rollout_mode_counts = {"off": 0, "observe_only": 0, "active": 0, "other": 0}
    for r in records:
        mode = r.rollout_mode if r.rollout_mode in {"off", "observe_only", "active"} else "other"
        rollout_mode_counts[mode] += 1
    uplift_states = ["pass", "hold", "regressed", "insufficient_data", "insufficient_match_quality", "unknown"]
    uplift_promotion_decision_counts = {key: 0 for key in uplift_states}
    uplift_auto_apply_decision_counts = {key: 0 for key in uplift_states}
    for r in records:
        promotion_state = r.uplift_promotion_decision if r.uplift_promotion_decision in uplift_promotion_decision_counts else "unknown"
        auto_apply_state = r.uplift_auto_apply_decision if r.uplift_auto_apply_decision in uplift_auto_apply_decision_counts else "unknown"
        uplift_promotion_decision_counts[promotion_state] += 1
        uplift_auto_apply_decision_counts[auto_apply_state] += 1

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
        capture_records_written=capture_records_written,
        capture_coverage_rate=round(capture_records_written / total, 4),
        auto_capture_enabled_rate=round(auto_capture_enabled_runs / total, 4),
        auto_apply_enabled_rate=round(auto_apply_enabled_runs / total, 4),
        confidence_bucket_counts=confidence_bucket_counts,
        confidence_bucket_distribution=confidence_bucket_distribution,
        runs_with_injection=runs_with_injection,
        runs_with_retrieved_lessons=runs_with_retrieved_lessons,
        suppressed_injection_runs=suppressed_injection_runs,
        injection_usage_rate=round(runs_with_injection / total, 4),
        total_injected_lessons=total_injected_lessons,
        average_injected_lessons_per_run=round(total_injected_lessons / total, 3),
        rollout_mode_counts=rollout_mode_counts,
        uplift_promotion_decision_counts=uplift_promotion_decision_counts,
        uplift_auto_apply_decision_counts=uplift_auto_apply_decision_counts,
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
    lines.append(
        f"- Capture coverage: `{fmt_pct(current_summary.capture_coverage_rate)}` "
        f"(`{current_summary.capture_records_written}/{current_summary.runs_total}` runs with capture artifacts)"
    )
    lines.append(
        "- Confidence bucket distribution: "
        f"`high={current_summary.confidence_bucket_counts['high']}` "
        f"`medium={current_summary.confidence_bucket_counts['medium']}` "
        f"`low={current_summary.confidence_bucket_counts['low']}` "
        f"`unknown={current_summary.confidence_bucket_counts['unknown']}`"
    )
    lines.append(
        f"- Injection usage rate: `{fmt_pct(current_summary.injection_usage_rate)}` "
        f"(`{current_summary.runs_with_injection}/{current_summary.runs_total}` runs, "
        f"total lessons `{current_summary.total_injected_lessons}`, "
        f"suppressed-by-controls runs `{current_summary.suppressed_injection_runs}`)"
    )
    lines.append(
        "- Rollout mode distribution: "
        f"`active={current_summary.rollout_mode_counts['active']}` "
        f"`observe_only={current_summary.rollout_mode_counts['observe_only']}` "
        f"`off={current_summary.rollout_mode_counts['off']}` "
        f"`other={current_summary.rollout_mode_counts['other']}`"
    )
    lines.append(
        "- Uplift gate decisions (promotion/auto-apply): "
        f"`pass={current_summary.uplift_promotion_decision_counts['pass']}/{current_summary.uplift_auto_apply_decision_counts['pass']}` "
        f"`insufficient_data={current_summary.uplift_promotion_decision_counts['insufficient_data']}/{current_summary.uplift_auto_apply_decision_counts['insufficient_data']}` "
        f"`regressed={current_summary.uplift_promotion_decision_counts['regressed']}/{current_summary.uplift_auto_apply_decision_counts['regressed']}`"
    )
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
    lines.append(
        f"- Capture coverage: `{fmt_pct(current_summary.capture_coverage_rate)}` (target: `>=95.0%`)"
    )
    lines.append(
        f"- Injection usage rate: `{fmt_pct(current_summary.injection_usage_rate)}` (target: pilot-defined; monitor suppression count `{current_summary.suppressed_injection_runs}`)"
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
        "capture_records_written": summary.capture_records_written,
        "capture_coverage_rate": summary.capture_coverage_rate,
        "auto_capture_enabled_rate": summary.auto_capture_enabled_rate,
        "auto_apply_enabled_rate": summary.auto_apply_enabled_rate,
        "confidence_bucket_counts": summary.confidence_bucket_counts,
        "confidence_bucket_distribution": summary.confidence_bucket_distribution,
        "runs_with_injection": summary.runs_with_injection,
        "runs_with_retrieved_lessons": summary.runs_with_retrieved_lessons,
        "suppressed_injection_runs": summary.suppressed_injection_runs,
        "injection_usage_rate": summary.injection_usage_rate,
        "total_injected_lessons": summary.total_injected_lessons,
        "average_injected_lessons_per_run": summary.average_injected_lessons_per_run,
        "rollout_mode_counts": summary.rollout_mode_counts,
        "uplift_promotion_decision_counts": summary.uplift_promotion_decision_counts,
        "uplift_auto_apply_decision_counts": summary.uplift_auto_apply_decision_counts,
    }


def main() -> int:
    global PILOT_PROFILES
    args = parse_args()
    pilot_profiles_path = Path(args.pilot_profiles_file).expanduser().resolve()
    PILOT_PROFILES = load_pilot_profiles(pilot_profiles_path)

    runs_root = Path(args.runs_root).expanduser().resolve()
    repo_root = Path.cwd().resolve()
    run_records: List[RunRecord] = []
    run_meta: List[RunMeta] = []
    skipped_runs: List[Dict[str, str]] = []
    event_errors: List[str] = []
    promotion_approved_by_run: Dict[str, bool] = {}

    for run_dir in sorted(runs_root.glob("run_*")):
        if not run_dir.is_dir():
            continue
        try:
            meta = load_run_meta(run_dir)
        except Exception as exc:
            run_dir_out = (
                str(run_dir.relative_to(repo_root))
                if run_dir.is_relative_to(repo_root)
                else str(run_dir)
            )
            skipped_runs.append({"run_dir": run_dir_out, "reason": str(exc)})
            continue
        if meta is not None:
            run_meta.append(meta)

    run_meta.sort(key=lambda r: r.finished_at, reverse=True)

    if run_meta:
        latest = run_meta[0].finished_at
    else:
        latest = datetime.now(timezone.utc)

    window_days = max(1, args.window_days)
    current_start = latest - timedelta(days=window_days - 1)
    baseline_start = current_start - timedelta(days=window_days)

    selected_run_meta = [m for m in run_meta if m.finished_at >= baseline_start]
    for meta in selected_run_meta:
        run_dir = meta.run_dir
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
        if record is None:
            continue
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
        "pilot_profiles_file": str(pilot_profiles_path),
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
                "confidence_score": r.confidence_score,
                "confidence_bucket": r.confidence_bucket,
                "evidence_completeness_score": r.evidence_completeness_score,
                "candidate_count": r.candidate_count,
                "capture_record_present": r.capture_record_present,
                "rollout_mode": r.rollout_mode,
                "auto_capture_enabled": r.auto_capture_enabled,
                "auto_apply_enabled": r.auto_apply_enabled,
                "injected_lesson_count": r.injected_lesson_count,
                "retrieved_lesson_count": r.retrieved_lesson_count,
                "injection_suppressed": r.injection_suppressed,
                "uplift_promotion_decision": r.uplift_promotion_decision,
                "uplift_auto_apply_decision": r.uplift_auto_apply_decision,
                "uplift_sample_size": r.uplift_sample_size,
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
        f"- Capture coverage: `{fmt_pct(current_summary.capture_coverage_rate)}` ({current_summary.capture_records_written}/{current_summary.runs_total})",
        f"- Confidence buckets: `high={current_summary.confidence_bucket_counts['high']}` `medium={current_summary.confidence_bucket_counts['medium']}` `low={current_summary.confidence_bucket_counts['low']}` `unknown={current_summary.confidence_bucket_counts['unknown']}`",
        f"- Injection usage: `{fmt_pct(current_summary.injection_usage_rate)}` ({current_summary.runs_with_injection}/{current_summary.runs_total})",
        f"- Injection suppressed by controls: `{current_summary.suppressed_injection_runs}`",
        f"- Uplift promotion decisions: `pass={current_summary.uplift_promotion_decision_counts['pass']}` `hold={current_summary.uplift_promotion_decision_counts['hold']}` `insufficient_data={current_summary.uplift_promotion_decision_counts['insufficient_data']}`",
        f"- Uplift auto-apply decisions: `pass={current_summary.uplift_auto_apply_decision_counts['pass']}` `hold={current_summary.uplift_auto_apply_decision_counts['hold']}` `insufficient_data={current_summary.uplift_auto_apply_decision_counts['insufficient_data']}`",
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
            confidence_str = "n/a" if r.confidence_score is None else f"{r.confidence_score:.3f}"
            bucket_str = r.confidence_bucket or "n/a"
            completeness_str = (
                "n/a" if r.evidence_completeness_score is None else f"{r.evidence_completeness_score:.3f}"
            )
            queue_lines.append(
                f"- `{r.run_id}` | profile `{r.profile_id}` | confidence `{confidence_str}` (`{bucket_str}`)"
                f" | evidence completeness `{completeness_str}` | candidates `{r.candidate_count}`"
                f" | rollout `{r.rollout_mode}` | injected `{r.injected_lesson_count}`"
                f" | uplift `{r.uplift_promotion_decision or 'unknown'}/{r.uplift_auto_apply_decision or 'unknown'}`"
                f" | finished `{r.finished_at.isoformat().replace('+00:00', 'Z')}`"
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
