#!/usr/bin/env python3
"""Aggregate skill feedback logs into subject-level scoreboards."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


def infer_subject_from_event(event: dict) -> str:
    subject = (event.get("subject") or "").strip()
    if subject:
        return subject

    action_key = (event.get("action_key") or "").strip()
    if action_key:
        if "graph" in action_key:
            return "graph"
        return "other"

    skill_path = (event.get("skill_path") or "").lower()
    if "/frontend/" in skill_path:
        return "ui"
    if "/github/" in skill_path or "review" in skill_path:
        return "code_review"
    if "/backend/" in skill_path:
        return "backend"
    if "/product/security/" in skill_path:
        return "security"
    if "/auth/" in skill_path:
        return "auth"
    return "general"


def load_events(log_paths: list[Path]) -> list[dict]:
    events: list[dict] = []
    for path in log_paths:
        if not path.exists() or not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            events.append(event)
    return events


def default_logs(workspace: Path) -> list[Path]:
    candidates = [
        workspace / "Infrastructure/ops/metrics/skill-feedback/decision-feedback.jsonl",
        workspace / "Infrastructure/ops/metrics/graph/feedback/decision-feedback.jsonl",
    ]
    return candidates


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build subject-level scoreboard from skill feedback logs."
    )
    parser.add_argument("--workspace", default=".", help="Workspace root for default log discovery.")
    parser.add_argument(
        "--log",
        action="append",
        default=[],
        help="Additional feedback log path(s). Can be repeated.",
    )
    parser.add_argument(
        "--format",
        choices=["table", "json"],
        default="table",
        help="Output format.",
    )
    parser.add_argument(
        "--write-report",
        action="store_true",
        help="Write markdown report to Infrastructure/ops/metrics/skill-feedback/Infrastructure/reports/subject-scoreboard-latest.md",
    )
    return parser.parse_args()


def render_table(subject_rows: list[dict], skill_rows: list[dict]) -> str:
    lines = []
    lines.append("skill-subject-scoreboard: PASS")
    lines.append("")
    lines.append("By subject")
    lines.append("subject\tevents\tgood\tneutral\tbad\tunknown\tgood_rate\tbad_rate")
    for row in subject_rows:
        lines.append(
            f"{row['subject']}\t{row['events']}\t{row['good']}\t{row['neutral']}\t"
            f"{row['bad']}\t{row['unknown']}\t{row['good_rate']:.2f}\t{row['bad_rate']:.2f}"
        )

    lines.append("")
    lines.append("Top skills by bad_rate (min 2 events)")
    lines.append("skill\tsubject\tevents\tgood\tbad\tbad_rate")
    for row in skill_rows:
        if row["events"] < 2:
            continue
        lines.append(
            f"{row['skill_name']}\t{row['subject']}\t{row['events']}\t{row['good']}\t"
            f"{row['bad']}\t{row['bad_rate']:.2f}"
        )
    return "\n".join(lines)


def build_rows(events: list[dict]) -> tuple[list[dict], list[dict]]:
    subject_counts: dict[str, Counter] = defaultdict(Counter)
    skill_counts: dict[tuple[str, str], Counter] = defaultdict(Counter)

    for e in events:
        subject = infer_subject_from_event(e)
        skill_name = (e.get("skill_name") or "unknown").strip() or "unknown"
        outcome = (e.get("outcome") or "unknown").strip() or "unknown"

        subject_counts[subject]["events"] += 1
        subject_counts[subject][outcome] += 1

        key = (subject, skill_name)
        skill_counts[key]["events"] += 1
        skill_counts[key][outcome] += 1

    subject_rows = []
    for subject, c in sorted(subject_counts.items(), key=lambda kv: (-kv[1]["events"], kv[0])):
        events_n = c["events"]
        good = c["good"]
        bad = c["bad"]
        subject_rows.append(
            {
                "subject": subject,
                "events": events_n,
                "good": good,
                "neutral": c["neutral"],
                "bad": bad,
                "unknown": c["unknown"],
                "good_rate": (good / events_n) if events_n else 0.0,
                "bad_rate": (bad / events_n) if events_n else 0.0,
            }
        )

    skill_rows = []
    for (subject, skill_name), c in skill_counts.items():
        events_n = c["events"]
        good = c["good"]
        bad = c["bad"]
        skill_rows.append(
            {
                "subject": subject,
                "skill_name": skill_name,
                "events": events_n,
                "good": good,
                "neutral": c["neutral"],
                "bad": bad,
                "unknown": c["unknown"],
                "good_rate": (good / events_n) if events_n else 0.0,
                "bad_rate": (bad / events_n) if events_n else 0.0,
            }
        )
    skill_rows.sort(key=lambda r: (-r["bad_rate"], -r["events"], r["skill_name"]))

    return subject_rows, skill_rows


def main() -> int:
    args = parse_args()
    workspace = Path(args.workspace).expanduser().resolve()
    log_paths = default_logs(workspace) + [Path(p).expanduser().resolve() for p in args.log]
    # dedupe while preserving order
    deduped = []
    seen = set()
    for p in log_paths:
        if p in seen:
            continue
        seen.add(p)
        deduped.append(p)

    events = load_events(deduped)
    if not events:
        print("skill-subject-scoreboard: no feedback events found")
        print("checked logs:")
        for p in deduped:
            print(f"- {p}")
        return 1

    subject_rows, skill_rows = build_rows(events)

    if args.format == "json":
        payload = {
            "schema_version": 1,
            "events": len(events),
            "logs": [str(p) for p in deduped if p.exists()],
            "subjects": subject_rows,
            "skills": skill_rows,
        }
        output = json.dumps(payload, indent=2)
    else:
        output = render_table(subject_rows, skill_rows)

    print(output)

    if args.write_report:
        report_dir = workspace / "Infrastructure/ops/metrics/skill-feedback/reports"
        report_dir.mkdir(parents=True, exist_ok=True)
        report_path = report_dir / "subject-scoreboard-latest.md"
        lines = ["# Skill Subject Scoreboard", "", "```", output, "```", ""]
        report_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"report: {report_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
