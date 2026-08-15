#!/usr/bin/env python3
"""Validate that events.jsonl is required and properly formatted."""

import json
import sys
from pathlib import Path
from typing import List, Set

sys.path.insert(0, str(Path(__file__).parent))

try:
    from validate_recursive_promotion import RUN_REQUIRED_FILES
except ImportError:
    print("⚠ Could not import validate_recursive_promotion (using fallback)")
    RUN_REQUIRED_FILES = {"run.json", "iteration_journal.jsonl", "events.jsonl", "promotion_decision.json"}


def test_events_jsonl_is_required() -> None:
    """Verify events.jsonl is in RUN_REQUIRED_FILES."""
    assert (
        "events.jsonl" in RUN_REQUIRED_FILES
    ), "events.jsonl must be in RUN_REQUIRED_FILES to ensure it's always created"
    print("✓ events.jsonl is in RUN_REQUIRED_FILES")


def test_all_runs_have_events_jsonl() -> None:
    """Check that all current recursive runs have events.jsonl."""
    runs_root = Path(".tmp/agent-skills-artifacts/skill-graphs/runs")
    if not runs_root.exists():
        print("⚠ SKIP: No runs directory found")
        return

    missing_events: List[str] = []
    for run_dir in runs_root.iterdir():
        if not run_dir.is_dir():
            continue
        if not (run_dir / "run.json").exists():
            continue
        if not (run_dir / "events.jsonl").exists():
            missing_events.append(run_dir.name)

    assert not missing_events, (
        f"{len(missing_events)} runs missing events.jsonl:\n"
        + "\n".join(f"  - {name}" for name in missing_events[:5])
        + (f"\n  ... and {len(missing_events) - 5} more" if len(missing_events) > 5 else "")
    )
    print("✓ All runs have events.jsonl")


def test_events_jsonl_has_valid_format() -> None:
    """Check that all events.jsonl files have valid JSON Lines format."""
    runs_root = Path(".tmp/agent-skills-artifacts/skill-graphs/runs")
    if not runs_root.exists():
        print("⚠ SKIP: No runs directory found")
        return

    invalid_files: List[str] = []
    for run_dir in runs_root.iterdir():
        if not run_dir.is_dir():
            continue

        events_path = run_dir / "events.jsonl"
        if not events_path.exists():
            continue

        try:
            with events_path.open("r", encoding="utf-8") as f:
                for idx, line in enumerate(f):
                    line = line.strip()
                    if not line:
                        continue
                    event = json.loads(line)
                    if not isinstance(event, dict):
                        raise ValueError(f"Event {idx} is not a dict")
                    if "event_type" not in event:
                        raise ValueError(f"Event {idx} missing event_type")
                    if "schema_version" not in event:
                        raise ValueError(f"Event {idx} missing schema_version")
                    if "run_id" not in event:
                        raise ValueError(f"Event {idx} missing run_id")
        except Exception as exc:
            invalid_files.append(f"{run_dir.name}: {exc}")

    assert not invalid_files, (
        f"{len(invalid_files)} invalid events.jsonl files:\n"
        + "\n".join(f"  - {error}" for error in invalid_files[:5])
        + (f"\n  ... and {len(invalid_files) - 5} more" if len(invalid_files) > 5 else "")
    )
    print("✓ All events.jsonl files have valid format")


def test_events_use_valid_event_types() -> None:
    """Check that all event types are recognized."""
    runs_root = Path(".tmp/agent-skills-artifacts/skill-graphs/runs")
    if not runs_root.exists():
        print("⚠ SKIP: No runs directory found")
        return

    valid_event_types = {
        "run_initialized",
        "run_state_changed",
        "run_blocked",
        "failure_event",
        "promotion_approved",
    }

    unknown_types: Set[str] = set()
    for run_dir in runs_root.iterdir():
        if not run_dir.is_dir():
            continue

        events_path = run_dir / "events.jsonl"
        if not events_path.exists():
            continue

        with events_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                event = json.loads(line)
                event_type = event.get("event_type", "")
                if event_type not in valid_event_types:
                    unknown_types.add(event_type)

    assert not unknown_types, f"Unknown event types found: {unknown_types}"
    print("✓ All event types are recognized")


def main() -> int:
    """Run all validation tests and exit with pytest-like status."""
    print("=" * 60)
    print("events.jsonl Validation Tests")
    print("=" * 60)
    print()

    tests = [
        ("events.jsonl required", test_events_jsonl_is_required),
        ("runs have events.jsonl", test_all_runs_have_events_jsonl),
        ("events.jsonl format", test_events_jsonl_has_valid_format),
        ("event types are recognized", test_events_use_valid_event_types),
    ]

    failures = 0
    for name, test_func in tests:
        try:
            test_func()
        except Exception as exc:
            failures += 1
            print(f"✗ FAIL: {name} -> {exc}")

    print()
    print("=" * 60)
    print(f"Results: {len(tests) - failures}/{len(tests)} tests passed")
    print("=" * 60)

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
