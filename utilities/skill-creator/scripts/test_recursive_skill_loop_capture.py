#!/usr/bin/env python3
"""Regression tests for Phase 4 capture/evidence artifacts."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPO_ROOT / "utilities" / "skill-creator" / "scripts" / "recursive_skill_loop.py"
PROFILE_PATH = (
    REPO_ROOT / "docs" / "skill-graphs" / "schemas" / "examples" / "ui-skills-profile.example.json"
)


class RecursiveLoopCaptureTests(unittest.TestCase):
    def _run_loop(self, *extra_args: str) -> tuple[int, Path]:
        out_root = Path(tempfile.mkdtemp(prefix="recursive-loop-test-"))
        cmd = [
            sys.executable,
            str(SCRIPT_PATH),
            "--profile-file",
            str(PROFILE_PATH),
            "--objective",
            "Test objective for capture/evidence artifact validation.",
            "--out-root",
            str(out_root),
            "--run-owner",
            "test-owner",
            *extra_args,
        ]
        proc = subprocess.run(cmd, cwd=REPO_ROOT, text=True, capture_output=True)
        run_dirs = sorted(out_root.glob("run_*"))
        self.assertTrue(run_dirs, msg=f"expected run_* dir, stderr={proc.stderr}")
        return proc.returncode, run_dirs[-1]

    def test_capture_record_and_evidence_packet_written_on_normal_run(self) -> None:
        returncode, run_dir = self._run_loop(
            "--feedback-outcome",
            "worked",
            "--feedback-note",
            "good output quality",
        )
        self.assertIn(returncode, {0, 2, 3, 4, 5})

        capture = json.loads((run_dir / "capture_record.json").read_text(encoding="utf-8"))
        evidence = json.loads((run_dir / "evidence_packet.json").read_text(encoding="utf-8"))

        self.assertEqual(capture["feedback"]["status"], "worked")
        self.assertEqual(capture["feedback"]["source"], "cli_one_tap")
        self.assertTrue(capture["capture_id"])
        self.assertEqual(capture["evidence"]["evidence_packet_id"], evidence["evidence_packet_id"])
        self.assertIn("score", evidence["completeness"])
        for key in ("events", "logs", "traces", "session_signals", "checks"):
            self.assertIn(key, evidence["completeness"])

    def test_capture_artifacts_exist_when_run_is_blocked(self) -> None:
        with tempfile.NamedTemporaryFile("w", delete=False) as f:
            f.write("1\n")
            rollback_flag = f.name

        returncode, run_dir = self._run_loop("--rollback-required-file", rollback_flag)
        self.assertEqual(returncode, 5)

        capture = json.loads((run_dir / "capture_record.json").read_text(encoding="utf-8"))
        evidence = json.loads((run_dir / "evidence_packet.json").read_text(encoding="utf-8"))
        run_obj = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))

        self.assertEqual(capture["feedback"]["status"], "missing")
        self.assertEqual(capture["output_summary"]["terminal_status"], run_obj["terminal_status"])
        self.assertEqual(evidence["run_id"], run_obj["run_id"])


if __name__ == "__main__":
    unittest.main()
