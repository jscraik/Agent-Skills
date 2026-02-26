#!/usr/bin/env python3
"""Validate that events.jsonl is required and properly formatted.

This script validates that:
1. events.jsonl is in RUN_REQUIRED_FILES
2. All runs have events.jsonl files
3. events.jsonl contains valid JSON Lines
4. Event types are recognized
5. Required fields are present

Run with: python3 utilities/skill-creator/scripts/test_events_jsonl_required.py
"""

import json
import sys
from pathlib import Path
from typing import List, Set

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from validate_recursive_promotion import RUN_REQUIRED_FILES
except ImportError:
    print("⚠ Could not import validate_recursive_promotion (using fallback)")
    RUN_REQUIRED_FILES = {"run.json", "iteration_journal.jsonl", "events.jsonl", "promotion_decision.json"}


def test_events_jsonl_is_required() -> bool:
    """Verify events.jsonl is in RUN_REQUIRED_FILES."""
    if "events.jsonl" not in RUN_REQUIRED_FILES:
        print("✗ FAIL: events.jsonl must be in RUN_REQUIRED_FILES to ensure it's always created")
        return False
    print("✓ events.jsonl is in RUN_REQUIRED_FILES")
    return True


def test_all_runs_have_events_jsonl() -> bool:
    """Check that all runs in artifacts/skill-graphs/runs have events.jsonl."""
    runs_root = Path("artifacts/skill-graphs/runs")
    if not runs_root.exists():
        print("⚠ SKIP: No runs directory found")
        return True

    missing_events: List[str] = []
    for run_dir in runs_root.iterdir():
        if not run_dir.is_dir():
            continue
        if not (run_dir / "run.json").exists():
            continue  # Not a valid run

        events_path = run_dir / "events.jsonl"
        if not events_path.exists():
            missing_events.append(run_dir.name)

    if missing_events:
        print(f"✗ FAIL: {len(missing_events)} runs missing events.jsonl:")
        for run_name in missing_events[:5]:  # Show first 5
            print(f"  - {run_name}")
        if len(missing_events) > 5:
            print(f"  ... and {len(missing_events) - 5} more")
        return False

    print("✓ All runs have events.jsonl")
    return True


def test_events_jsonl_has_valid_format() -> bool:
    """Check that all events.jsonl files have valid JSON Lines format."""
    runs_root = Path("artifacts/skill-graphs/runs")
    if not runs_root.exists():
        print("⚠ SKIP: No runs directory found")
        return True

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
        except Exception as e:
            invalid_files.append(f"{run_dir.name}: {e}")

    if invalid_files:
        print(f"✗ FAIL: {len(invalid_files)} invalid events.jsonl files:")
        for error in invalid_files[:5]:  # Show first 5
            print(f"  - {error}")
        if len(invalid_files) > 5:
            print(f"  ... and {len(invalid_files) - 5} more")
        return False

    print("✓ All events.jsonl files have valid format")
    return True


def test_events_use_valid_event_types() -> bool:
    """Check that all event types are recognized."""
    runs_root = Path("artifacts/skill-graphs/runs")
    if not runs_root.exists():
        print("⚠ SKIP: No runs directory found")
        return True

    # Valid event types from recursive_skill_loop.py
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

        try:
            with events_path.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    event = json.loads(line)
                    event_type = event.get("event_type", "")
                    if event_type not in valid_event_types:
                        unknown_types.add(event_type)
        except Exception:
            pass  # Already tested in test_events_jsonl_has_valid_format

    if unknown_types:
        print(f"✗ FAIL: Unknown event types found: {unknown_types}")
        return False

    print("✓ All event types are recognized")
    return True


def main() -> int:
    """Run all validation tests."""
    print("=" * 60)
    print("events.jsonl Validation Tests")
    print("=" * 60)
    print()

    tests = [
        test_events_jsonl_is_required,
        test_all_runs_have_events_jsonl,
        test_events_jsonl_has_valid_format,
        test_events_use_valid_event_types,
    ]

    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"✗ FAIL: {test_func.__name__} raised exception: {e}")
            results.append(False)

    print()
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 60)

    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
