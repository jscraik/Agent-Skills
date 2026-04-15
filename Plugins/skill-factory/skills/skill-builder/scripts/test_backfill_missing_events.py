#!/usr/bin/env python3
"""Security-focused tests for backfill_missing_events.py."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from backfill_missing_events import backfill_run, find_runs_missing_events


class BackfillMissingEventsSecurityTests(unittest.TestCase):
    def test_find_runs_missing_events_skips_symlinked_run_dirs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as outside_tmp:
            root = Path(tmp)
            safe_run = root / "safe-run"
            safe_run.mkdir()
            (safe_run / "run.json").write_text("{}", encoding="utf-8")

            outside = Path(outside_tmp) / "outside"
            outside.mkdir()
            (outside / "run.json").write_text("{}", encoding="utf-8")
            (root / "symlink-run").symlink_to(outside, target_is_directory=True)

            missing = find_runs_missing_events(root)

            self.assertEqual(missing, [safe_run])

    def test_backfill_run_rejects_symlinked_run_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "target"
            target.mkdir()
            (target / "run.json").write_text("{}", encoding="utf-8")
            symlink_run = root / "symlink-run"
            symlink_run.symlink_to(target, target_is_directory=True)

            written = backfill_run(symlink_run)

            self.assertFalse(written)
            self.assertFalse((target / "events.jsonl").exists())

    def test_backfill_run_rejects_symlinked_events_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "run"
            run_dir.mkdir()
            (run_dir / "run.json").write_text("{}", encoding="utf-8")
            (run_dir / "events.jsonl").symlink_to(root / "outside-events.jsonl")

            written = backfill_run(run_dir)

            self.assertFalse(written)
            self.assertFalse((root / "outside-events.jsonl").exists())


if __name__ == "__main__":
    unittest.main()
