#!/usr/bin/env python3
"""Build an Ars Contexta-style intervention queue for recursive skill pilots."""

from __future__ import annotations

import argparse
import json
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import build_recursive_skill_shadow_report as shadow_report

DEFAULT_OUTPUT_JSON = "Infrastructure/artifacts/skill-graphs/telemetry/arscontexta-intervention-queue.json"
DEFAULT_OUTPUT_MD = "docs/skill-graphs/pilots/arscontexta-intervention-queue.md"

METHODOLOGY_REFS = [
    "Plugins/arscontexta/methodology/retrieval verification loop tests description quality at scale.md",
    "Plugins/arscontexta/methodology/queries evolve during search so agents should checkpoint.md",
    "Plugins/arscontexta/methodology/schema enforcement via validation agents enables soft consistency.md",
    "Plugins/arscontexta/methodology/methodology development should follow the trajectory from documentation to skill to hook as understanding hardens.md",
]


@dataclass(frozen=True)
class ProfileEntry:
    profile_id: str
    profile_file: Optional[Path]
    objective: str
    scope_skill: Optional[str]
    scope_profile: Optional[str]
    criteria_labels: Dict[str, str]
    criteria_thresholds: Dict[str, float]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Ars Contexta intervention queue for pilot profiles")
    parser.add_argument("--runs-root", default="Infrastructure/artifacts/skill-graphs/runs")
    parser.add_argument("--pilot-profiles-file", default="docs/skill-graphs/schemas/examples/pilot-profiles.json")
    parser.add_argument("--dashboard-json", default="Infrastructure/artifacts/skill-graphs/pilot/shadow-dashboard.json")
    parser.add_argument("--failure-patterns-jsonl", default="Infrastructure/artifacts/skill-graphs/telemetry/failure-pattern-candidates.jsonl")
    parser.add_argument("--output-json", default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", default=DEFAULT_OUTPUT_MD)
    return parser.parse_args()


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_optional_json(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else None


def load_profile_entries(path: Path) -> List[ProfileEntry]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list) or not raw:
        raise ValueError("pilot profiles file must be a non-empty JSON array")

    entries: List[ProfileEntry] = []
    for item in raw:
        if isinstance(item, str):
            profile_id = item.strip()
            if profile_id:
                entries.append(
                    ProfileEntry(
                        profile_id=profile_id,
                        profile_file=None,
                        objective="",
                        scope_skill=None,
                        scope_profile=None,
                        criteria_labels={},
                        criteria_thresholds={},
                    )
                )
            continue

        if not isinstance(item, dict):
            raise ValueError("pilot profile entries must be strings or objects")

        profile_file_raw = str(item.get("profile_file") or item.get("profile_path") or "").strip()
        profile_file = resolve_profile_path(path, profile_file_raw) if profile_file_raw else None
        profile_data = load_optional_json(profile_file) if profile_file else None
        profile_id = str(item.get("profile_id") or (profile_data or {}).get("profile_id") or "").strip()
        if not profile_id:
            raise ValueError("pilot profile entries require profile_id or a readable profile_file")

        objective = str(item.get("objective") or "").strip()
        criteria_labels: Dict[str, str] = {}
        criteria_thresholds: Dict[str, float] = {}
        if profile_data:
            criteria = profile_data.get("criteria")
            if isinstance(criteria, list):
                for criterion in criteria:
                    if not isinstance(criterion, dict):
                        continue
                    criterion_id = str(criterion.get("id") or "").strip()
                    if not criterion_id:
                        continue
                    criteria_labels[criterion_id] = str(criterion.get("label") or criterion_id).strip()
                    criteria_thresholds[criterion_id] = float(criterion.get("threshold") or 0.0)

        entries.append(
            ProfileEntry(
                profile_id=profile_id,
                profile_file=profile_file,
                objective=objective,
                scope_skill=str((profile_data or {}).get("scope_skill") or "").strip() or None,
                scope_profile=str((profile_data or {}).get("scope_profile") or "").strip() or None,
                criteria_labels=criteria_labels,
                criteria_thresholds=criteria_thresholds,
            )
        )
    return entries


def resolve_profile_path(manifest_path: Path, profile_file_raw: str) -> Path:
    path = Path(profile_file_raw)
    if path.is_absolute():
        return path
    manifest_relative = (manifest_path.parent / path).resolve()
    if manifest_relative.exists():
        return manifest_relative
    return (Path.cwd() / path).resolve()


def parse_window(window: str) -> Tuple[date, date]:
    start_raw, end_raw = window.split("..", 1)
    return (date.fromisoformat(start_raw), date.fromisoformat(end_raw))


def iter_run_dirs(runs_root: Path) -> Iterable[Path]:
    return sorted((path for path in runs_root.glob("run_*") if path.is_dir()), key=lambda path: path.name)


def criterion_label(entry: ProfileEntry, criterion_id: str) -> str:
    fallback = criterion_id.replace("_", " ").strip()
    return entry.criteria_labels.get(criterion_id, fallback.title())


def render_objective(objective: str, profile_id: str) -> str:
    if not objective:
        return ""
    return objective.replace("{profile_id}", profile_id).replace("{n}", "N")


def top_counter(counter: Counter[str], entry: ProfileEntry, limit: int = 3) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for criterion_id, count in counter.most_common(limit):
        rows.append(
            {
                "criterion_id": criterion_id,
                "label": criterion_label(entry, criterion_id),
                "count": count,
                "threshold": entry.criteria_thresholds.get(criterion_id),
            }
        )
    return rows


def choose_stage(
    clean_rate: float,
    recovered_rate: float,
    conflict_count: int,
    low_confidence_rate: float,
    positive_signal_count: int,
) -> str:
    if clean_rate >= 1.0 and recovered_rate == 0.0 and conflict_count == 0 and low_confidence_rate <= 0.1:
        return "hook-candidate"
    if clean_rate >= 0.75 and conflict_count == 0 and low_confidence_rate <= 0.35 and positive_signal_count >= 3:
        return "skill"
    return "documentation"


def format_criteria_list(rows: List[Dict[str, Any]]) -> str:
    labels = [str(row["label"]) for row in rows if row.get("label")]
    if not labels:
        return "the current weak criteria"
    if len(labels) == 1:
        return labels[0]
    if len(labels) == 2:
        return f"{labels[0]} and {labels[1]}"
    return f"{', '.join(labels[:-1])}, and {labels[-1]}"


def build_recommendations(
    entry: ProfileEntry,
    stage: str,
    clean_rate: float,
    recovered_rate: float,
    conflict_runs: List[str],
    weak_rows: List[Dict[str, Any]],
    regression_rows: List[Dict[str, Any]],
    positive_rows: List[Dict[str, Any]],
) -> List[str]:
    weak_text = format_criteria_list(weak_rows or regression_rows)
    regression_text = format_criteria_list(regression_rows or weak_rows)
    positive_text = format_criteria_list(positive_rows)
    conflict_text = ", ".join(conflict_runs[:3]) if conflict_runs else "recent recovered runs"

    if stage == "hook-candidate":
        return [
            f"Promote the repeated win around {positive_text} from operator note into a reusable skill reference before considering hook-level automation.",
            f"Keep checkpoint reviews active for {entry.profile_id} until at least one additional window confirms {clean_rate:.0%} clean runs without recovery.",
            f"Reserve hook promotion for the subset of guidance that remains deterministic across runs and does not reopen regressions in {regression_text}.",
        ]

    if stage == "skill":
        return [
            f"Turn the repeated positive pattern around {positive_text} into a profile-scoped retrieval note that is injected before iteration 1.",
            f"Use a checkpoint after each reevaluation to ask whether the active search should pivot toward {regression_text} instead of continuing generic remediation.",
            f"Do not promote beyond skill-level guidance until recovered-run rate falls below {max(0.1, recovered_rate / 2):.0%} for {entry.profile_id}.",
        ]

    return [
        f"Capture an Ars Contexta note for {entry.profile_id} centered on {weak_text}, using {conflict_text} as the seed evidence set.",
        f"At each reevaluation checkpoint, explicitly reassess whether the objective should pivot toward {regression_text}; treat that as search refinement, not failure.",
        f"Keep these interventions at documentation level for now, and only promote a pattern upward once it repeats cleanly without reopening regressions.",
    ]


def build_queries(entry: ProfileEntry, weak_rows: List[Dict[str, Any]], positive_rows: List[Dict[str, Any]]) -> List[str]:
    weak_text = format_criteria_list(weak_rows)
    positive_text = format_criteria_list(positive_rows) if positive_rows else "the most stable positive deltas"
    return [
        f"What recurring evidence explains why {entry.profile_id} regresses on {weak_text} during reevaluation?",
        f"Which prompt clauses or rubric reminders improved {positive_text} without weakening safety or non-regression?",
        f"What should be retrieved before iteration 1 so {entry.profile_id} starts from the last stable intervention instead of rediscovering it?",
    ]


def render_markdown(
    generated_at: str,
    current_window: str,
    profiles: List[Dict[str, Any]],
    output_json_path: str,
) -> str:
    lines: List[str] = []
    lines.append("# Ars Contexta Intervention Queue")
    lines.append("")
    lines.append("Ars Contexta-backed synthesis layer for recursive skill pilot instability. This queue does not replace the shadow gate; it converts repeated failure and recovery patterns into retrieval-ready interventions.")
    lines.append("")
    lines.append("## Table of Contents")
    lines.append("- [Overview](#overview)")
    lines.append("- [Promotion Rule](#promotion-rule)")
    lines.append("- [Profile Queues](#profile-queues)")
    lines.append("- [Methodology References](#methodology-references)")
    lines.append("")
    lines.append("## Overview")
    lines.append(f"- Generated: `{generated_at}`")
    lines.append(f"- Window: `{current_window}`")
    lines.append(f"- Machine-readable queue: `/{output_json_path}`")
    lines.append("- Operator use: review the top unstable profile, capture the intervention as a note first, then promote only repeated wins into skill references or hooks.")
    lines.append("")
    lines.append("## Promotion Rule")
    lines.append("- `documentation`: pattern is still unstable; capture and retrieve, do not automate.")
    lines.append("- `skill`: repeated positive pattern is stable enough to encode in a reusable workflow or reference.")
    lines.append("- `hook-candidate`: only for deterministic patterns that remain clean across windows without recovery.")
    lines.append("")
    lines.append("## Profile Queues")
    for profile in profiles:
        profile_id = profile["profile_id"]
        lines.append(f"### `{profile_id}`")
        lines.append(f"- Stage: `{profile['arscontexta_stage']}`")
        lines.append(f"- Scope skill: `{profile['scope_skill']}`")
        lines.append(f"- Clean runs: `{profile['metrics']['clean_runs']}/{profile['metrics']['runs_total']}`")
        lines.append(f"- Recovered runs: `{profile['metrics']['recovered_runs']}`")
        lines.append(f"- Evaluator conflicts: `{profile['metrics']['evaluator_conflicts']}`")
        lines.append(f"- Low-confidence runs: `{profile['metrics']['low_confidence_runs']}`")
        if profile.get("objective"):
            lines.append(f"- Objective focus: {profile['objective']}")
        if profile["signals"]["weakest_criteria"]:
            lines.append("- Weakest criteria:")
            for row in profile["signals"]["weakest_criteria"]:
                lines.append(f"  - `{row['criterion_id']}` ({row['label']}) x{row['count']}")
        if profile["signals"]["regression_criteria"]:
            lines.append("- Regression criteria:")
            for row in profile["signals"]["regression_criteria"]:
                lines.append(f"  - `{row['criterion_id']}` ({row['label']}) x{row['count']}")
        if profile["signals"]["positive_criteria"]:
            lines.append("- Positive criteria:")
            for row in profile["signals"]["positive_criteria"]:
                lines.append(f"  - `{row['criterion_id']}` ({row['label']}) x{row['count']}")
        lines.append("- Recommendations:")
        for rec in profile["recommendations"]:
            lines.append(f"  - {rec}")
        lines.append("- Retrieval checkpoints:")
        for query in profile["retrieval_packet"]["checkpoint_queries"]:
            lines.append(f"  - {query}")
        lines.append("")
    lines.append("## Methodology References")
    for ref in METHODOLOGY_REFS:
        lines.append(f"- `/{ref}`")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    repo_root = Path.cwd()
    runs_root = (repo_root / args.runs_root).resolve()
    pilot_profiles_path = (repo_root / args.pilot_profiles_file).resolve()
    dashboard_path = (repo_root / args.dashboard_json).resolve()
    failure_patterns_path = (repo_root / args.failure_patterns_jsonl).resolve()
    output_json_path = (repo_root / args.output_json).resolve()
    output_md_path = (repo_root / args.output_md).resolve()

    entries = load_profile_entries(pilot_profiles_path)
    entry_by_id = {entry.profile_id: entry for entry in entries}
    shadow_report.PILOT_PROFILES = [entry.profile_id for entry in entries]

    dashboard = load_json(dashboard_path)
    current_window = str(dashboard.get("current_window") or "").strip()
    if not current_window:
        raise RuntimeError("dashboard JSON missing current_window")
    window_start, window_end = parse_window(current_window)

    failure_rows = shadow_report.load_jsonl(failure_patterns_path)
    failure_by_profile: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for row in failure_rows:
        profile_id = str(row.get("profile_id") or "").strip()
        run_id = str(row.get("run_id") or "").strip()
        if profile_id in entry_by_id and run_id:
            failure_by_profile[profile_id].append(row)

    records_by_profile: Dict[str, List[shadow_report.RunRecord]] = defaultdict(list)
    weakest_by_profile: Dict[str, Counter[str]] = defaultdict(Counter)
    regressions_by_profile: Dict[str, Counter[str]] = defaultdict(Counter)
    positives_by_profile: Dict[str, Counter[str]] = defaultdict(Counter)

    for run_dir in iter_run_dirs(runs_root):
        record = shadow_report.load_run_record(run_dir)
        if record is None or record.profile_id not in entry_by_id:
            continue
        finished_day = record.finished_at.date()
        if finished_day < window_start or finished_day > window_end:
            continue

        records_by_profile[record.profile_id].append(record)

        journal_path = run_dir / "iteration_journal.jsonl"
        if journal_path.exists():
            for row in shadow_report.load_jsonl(journal_path):
                diagnosis = row.get("diagnosis")
                if isinstance(diagnosis, dict):
                    for criterion_id in diagnosis.get("weakest_criteria") or []:
                        if isinstance(criterion_id, str) and criterion_id.strip():
                            weakest_by_profile[record.profile_id][criterion_id.strip()] += 1
                reevaluation = row.get("reevaluation_report")
                if isinstance(reevaluation, dict):
                    for criterion_id in reevaluation.get("regression_criteria") or []:
                        if isinstance(criterion_id, str) and criterion_id.strip():
                            regressions_by_profile[record.profile_id][criterion_id.strip()] += 1

        lesson_candidates_path = run_dir / "lesson_candidates.json"
        if lesson_candidates_path.exists():
            lesson_candidates = load_optional_json(lesson_candidates_path) or {}
            items = lesson_candidates.get("items")
            if isinstance(items, list):
                for item in items:
                    if not isinstance(item, dict):
                        continue
                    implementation = item.get("implementation")
                    if isinstance(implementation, dict):
                        deltas = implementation.get("positive_criterion_deltas")
                        if isinstance(deltas, dict):
                            for criterion_id in deltas:
                                if isinstance(criterion_id, str) and criterion_id.strip():
                                    positives_by_profile[record.profile_id][criterion_id.strip()] += 1

    queue_profiles: List[Dict[str, Any]] = []
    for entry in entries:
        records = sorted(records_by_profile.get(entry.profile_id, []), key=lambda record: record.finished_at, reverse=True)
        if not records:
            continue

        runs_total = len(records)
        clean_runs = sum(1 for record in records if record.critical_non_regression_passed)
        recovered_runs = sum(1 for record in records if record.non_regression_recovered)
        terminal_pass_runs = sum(1 for record in records if record.terminal_status == "passed")
        evaluator_conflicts = sum(1 for record in records if record.stop_reason == "evaluator_conflict")
        low_confidence_runs = sum(1 for record in records if record.confidence_bucket == "low")
        clean_rate = clean_runs / runs_total
        recovered_rate = recovered_runs / runs_total
        low_confidence_rate = low_confidence_runs / runs_total
        positive_rows = top_counter(positives_by_profile[entry.profile_id], entry)
        weakest_rows = top_counter(weakest_by_profile[entry.profile_id], entry)
        regression_rows = top_counter(regressions_by_profile[entry.profile_id], entry)
        conflict_runs = [record.run_id for record in records if record.stop_reason == "evaluator_conflict"]
        stage = choose_stage(
            clean_rate=clean_rate,
            recovered_rate=recovered_rate,
            conflict_count=evaluator_conflicts,
            low_confidence_rate=low_confidence_rate,
            positive_signal_count=sum(row["count"] for row in positive_rows),
        )

        profile_row = {
            "profile_id": entry.profile_id,
            "profile_file": str(entry.profile_file.relative_to(repo_root)) if entry.profile_file else None,
            "scope_skill": entry.scope_skill or records[0].profile_id,
            "scope_profile": entry.scope_profile or "unknown",
            "objective": render_objective(entry.objective, entry.profile_id),
            "arscontexta_stage": stage,
            "metrics": {
                "runs_total": runs_total,
                "clean_runs": clean_runs,
                "terminal_pass_runs": terminal_pass_runs,
                "recovered_runs": recovered_runs,
                "evaluator_conflicts": evaluator_conflicts,
                "low_confidence_runs": low_confidence_runs,
                "median_iterations": statistics.median(record.iterations_completed for record in records),
                "median_quality_uplift": round(statistics.median(record.quality_uplift for record in records), 3),
                "mean_flip_rate": round(statistics.mean(record.evaluator_flip_rate for record in records), 3),
            },
            "signals": {
                "weakest_criteria": weakest_rows,
                "regression_criteria": regression_rows,
                "positive_criteria": positive_rows,
                "failure_candidates": [
                    {
                        "run_id": row.get("run_id"),
                        "stop_reason": row.get("stop_reason"),
                        "terminal_status": row.get("terminal_status"),
                        "quality_uplift": row.get("quality_uplift"),
                    }
                    for row in failure_by_profile.get(entry.profile_id, [])[:5]
                ],
            },
            "recommendations": build_recommendations(
                entry=entry,
                stage=stage,
                clean_rate=clean_rate,
                recovered_rate=recovered_rate,
                conflict_runs=conflict_runs,
                weak_rows=weakest_rows,
                regression_rows=regression_rows,
                positive_rows=positive_rows,
            ),
            "retrieval_packet": {
                "checkpoint_queries": build_queries(entry, weakest_rows or regression_rows, positive_rows),
                "capture_fields": [
                    "run_id",
                    "profile_id",
                    "objective_hash",
                    "weakest_criteria",
                    "regression_criteria",
                    "positive_criterion_deltas",
                    "critical_non_regression_passed",
                    "terminal_non_regression_passed",
                ],
            },
            "unstable_score": round(
                (runs_total - clean_runs) + (recovered_runs * 1.5) + (evaluator_conflicts * 2.0) + low_confidence_runs,
                3,
            ),
        }
        queue_profiles.append(profile_row)

    queue_profiles.sort(key=lambda row: (-float(row["unstable_score"]), row["profile_id"]))

    payload = {
        "schema_version": "1.0",
        "generated_at": dashboard.get("generated_at"),
        "current_window": current_window,
        "source_artifacts": {
            "dashboard_json": args.dashboard_json,
            "failure_patterns_jsonl": args.failure_patterns_jsonl,
            "pilot_profiles_file": args.pilot_profiles_file,
            "runs_root": args.runs_root,
        },
        "methodology_refs": METHODOLOGY_REFS,
        "profiles": queue_profiles,
    }

    output_json_path.parent.mkdir(parents=True, exist_ok=True)
    output_md_path.parent.mkdir(parents=True, exist_ok=True)
    output_json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    output_md_path.write_text(
        render_markdown(
            generated_at=str(payload["generated_at"]),
            current_window=current_window,
            profiles=queue_profiles,
            output_json_path=args.output_json,
        ),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
