#!/usr/bin/env python3
"""Backfill missing events.jsonl files for historical runs.

This script creates minimal events.jsonl files for runs that are missing them,
based on the run.json metadata. This ensures all runs in the skill-graph
have complete event telemetry.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


def iso_now() -> str:
    """Return current UTC timestamp in ISO format."""
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")


def sha256_text(text: str) -> str:
    """Return SHA256 hash of text."""
    import hashlib

    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_events_from_run(run_obj: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Reconstruct minimal events from run.json metadata."""
    events: List[Dict[str, Any]] = []

    run_id = run_obj.get("run_id", "unknown")
    skill_name = run_obj.get("scope_skill", "unknown")
    task_profile = run_obj.get("profile_id", "unknown")
    terminal_status = run_obj.get("terminal_status", "unknown")
    stop_reason = run_obj.get("stop_reason", "unknown")
    started_at = run_obj.get("started_at", iso_now())
    finished_at = run_obj.get("finished_at", iso_now())
    prompt_hash = run_obj.get("prompt_hash", "")
    evaluator_version = run_obj.get("versions", {}).get("evaluator_version", "v1")
    rubric_version = run_obj.get("versions", {}).get("rubric_version", "unknown")
    actor_id = run_obj.get("created_by", "recursive-skill-loop")

    # Event 1: run_initialized
    seed1 = f"{run_id}:run_initialized:{started_at}"
    events.append(
        {
            "schema_version": "1.0",
            "event_id": sha256_text(seed1)[:16],
            "ts": started_at,
            "run_id": run_id,
            "skill_name": skill_name,
            "task_profile": task_profile,
            "event_type": "run_initialized",
            "severity": "info",
            "terminal_status": None,
            "stop_reason": None,
            "actor_id": actor_id,
            "evaluator_version": evaluator_version,
            "rubric_version": rubric_version,
            "prompt_hash": prompt_hash,
            "auto_capture_enabled": False,  # Unknown for historical runs
            "auto_apply_enabled": False,
            "rollout_mode": "observe_only",  # Safe default
            "retrieved_lesson_ids": [],
            "injected_lesson_ids": [],
        }
    )

    # Event 2: run_state_changed (terminal)
    seed2 = f"{run_id}:run_state_changed:{terminal_status}:{stop_reason}:{finished_at}"
    events.append(
        {
            "schema_version": "1.0",
            "event_id": sha256_text(seed2)[:16],
            "ts": finished_at,
            "run_id": run_id,
            "skill_name": skill_name,
            "task_profile": task_profile,
            "event_type": "run_state_changed",
            "severity": "warn" if terminal_status != "passed" else "info",
            "terminal_status": terminal_status,
            "stop_reason": stop_reason,
            "actor_id": actor_id,
            "evaluator_version": evaluator_version,
            "rubric_version": rubric_version,
            "prompt_hash": prompt_hash,
        }
    )

    # Event 3: failure_event (for non-passed terminal states)
    if terminal_status != "passed":
        seed3 = f"{run_id}:failure_event:{finished_at}"
        events.append(
            {
                "schema_version": "1.0",
                "event_id": sha256_text(seed3)[:16],
                "ts": finished_at,
                "run_id": run_id,
                "skill_name": skill_name,
                "task_profile": task_profile,
                "event_type": "failure_event",
                "severity": "fail",
                "terminal_status": terminal_status,
                "stop_reason": stop_reason,
                "actor_id": actor_id,
                "evaluator_version": evaluator_version,
                "rubric_version": rubric_version,
                "prompt_hash": prompt_hash,
            }
        )

    return events


def backfill_run(run_dir: Path, dry_run: bool = False, verbose: bool = False) -> bool:
    """Backfill events.jsonl for a single run if missing.

    Returns True if backfill was needed and successful, False otherwise.
    """
    events_path = run_dir / "events.jsonl"
    run_json_path = run_dir / "run.json"

    # Never operate on symlinked run directories.
    if run_dir.is_symlink():
        print(f"✗ {run_dir.name}: run directory is a symlink (skipping)", file=sys.stderr)
        return False

    # Refuse to write to symlinked events files (including dangling symlinks).
    if events_path.is_symlink():
        print(f"✗ {run_dir.name}: events.jsonl is a symlink (skipping)", file=sys.stderr)
        return False

    # Skip if events.jsonl already exists
    if events_path.exists():
        if verbose:
            print(f"✓ {run_dir.name}: events.jsonl exists")
        return False

    # Skip if run.json is missing (can't reconstruct)
    if not run_json_path.exists():
        if verbose:
            print(f"⚠ {run_dir.name}: missing run.json (skipping)")
        return False

    # Load run.json
    try:
        run_obj = json.loads(run_json_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"✗ {run_dir.name}: failed to load run.json: {e}", file=sys.stderr)
        return False

    # Reconstruct events
    events = build_events_from_run(run_obj)

    if dry_run:
        print(f"[DRY-RUN] Would write {len(events)} events to {events_path}")
        if verbose:
            for event in events:
                print(f"  - {event['event_type']}: {event['ts']}")
        return True

    # Write events.jsonl
    try:
        with events_path.open("w", encoding="utf-8") as f:
            for event in events:
                f.write(json.dumps(event, sort_keys=True))
                f.write("\n")
        print(f"✓ {run_dir.name}: wrote {len(events)} events")
        return True
    except Exception as e:
        print(f"✗ {run_dir.name}: failed to write events.jsonl: {e}", file=sys.stderr)
        return False


def find_runs_missing_events(runs_root: Path) -> List[Path]:
    """Find all run directories missing events.jsonl."""
    missing: List[Path] = []

    for run_dir in runs_root.iterdir():
        if run_dir.is_symlink():
            continue
        if not run_dir.is_dir():
            continue
        if not (run_dir / "run.json").exists():
            continue  # Not a valid run

        events_path = run_dir / "events.jsonl"
        if not events_path.exists():
            missing.append(run_dir)

    return sorted(missing)


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(
        description="Backfill missing events.jsonl files for historical runs"
    )
    p.add_argument(
        "--runs-root",
        type=Path,
        default=Path("Infrastructure/artifacts/skill-graphs/runs"),
        help="Root directory containing run directories",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    p.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed progress",
    )
    p.add_argument(
        "--runs-smoke-root",
        type=Path,
        default=Path("Infrastructure/artifacts/skill-graphs/runs-smoke"),
        help="Root directory containing smoke test runs",
    )

    args = p.parse_args(argv)

    all_missing: List[Path] = []

    # Check primary runs directory
    if args.runs_root.exists():
        missing = find_runs_missing_events(args.runs_root)
        if missing:
            all_missing.extend(missing)
            print(f"Found {len(missing)} runs missing events.jsonl in {args.runs_root}")

    # Check smoke test runs directory
    if args.runs_smoke_root.exists():
        missing_smoke = find_runs_missing_events(args.runs_smoke_root)
        if missing_smoke:
            all_missing.extend(missing_smoke)
            print(f"Found {len(missing_smoke)} smoke runs missing events.jsonl in {args.runs_smoke_root}")

    if not all_missing:
        print("All runs have events.jsonl ✓")
        return 0

    print(f"\nTotal runs needing backfill: {len(all_missing)}")
    if args.dry_run:
        print("[DRY-RUN] Would backfill the following runs:")
        for run_dir in all_missing:
            print(f"  - {run_dir.name}")

    print()

    # Backfill each run
    backfilled = 0
    for run_dir in all_missing:
        if backfill_run(run_dir, dry_run=args.dry_run, verbose=args.verbose):
            backfilled += 1

    print(f"\nBackfilled {backfilled}/{len(all_missing)} runs")
    return 0 if backfilled == len(all_missing) else 1


if __name__ == "__main__":
    sys.exit(main())
