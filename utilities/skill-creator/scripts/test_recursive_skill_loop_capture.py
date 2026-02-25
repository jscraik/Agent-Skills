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
        promotion = json.loads((run_dir / "promotion_decision.json").read_text(encoding="utf-8"))
        candidates = json.loads((run_dir / "lesson_candidates.json").read_text(encoding="utf-8"))

        self.assertEqual(capture["feedback"]["status"], "worked")
        self.assertEqual(capture["feedback"]["source"], "cli_one_tap")
        self.assertTrue(capture["capture_id"])
        self.assertEqual(capture["evidence"]["evidence_packet_id"], evidence["evidence_packet_id"])
        self.assertIn("confidence", capture)
        self.assertIn("score", capture["confidence"])
        self.assertIn(capture["confidence"]["bucket"], {"high", "medium", "low"})
        self.assertIn("confidence", promotion)
        self.assertIn("lesson_candidates", promotion)
        self.assertEqual(promotion.get("schema_version"), "1.1")
        self.assertIn("counterfactual_uplift", promotion)
        self.assertEqual(len(promotion["lesson_candidates"]), len(candidates["items"]))
        self.assertGreaterEqual(len(candidates["items"]), 1)
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
        candidates = json.loads((run_dir / "lesson_candidates.json").read_text(encoding="utf-8"))

        self.assertEqual(capture["feedback"]["status"], "missing")
        self.assertEqual(capture["output_summary"]["terminal_status"], run_obj["terminal_status"])
        self.assertEqual(evidence["run_id"], run_obj["run_id"])
        self.assertEqual(candidates["items"], [])

    def test_start_of_run_retrieval_ranking_and_injection_attribution(self) -> None:
        lessons_dir = Path(tempfile.mkdtemp(prefix="lessons-test-"))
        lessons_file = lessons_dir / "canonical-lessons.jsonl"
        rows = [
            {
                "schema_version": "1.0",
                "scope_skill": "ui-ux-creative-coding",
                "scope_profile": "ui",
                "status": "active",
                "effective_from": "2026-02-24T12:00:00Z",
                "confidence": 0.99,
            },
            {
                "schema_version": "1.0",
                "lesson_id": "lesson_ui_high",
                "scope_skill": "ui-ux-creative-coding",
                "scope_profile": "ui",
                "status": "active",
                "effective_from": "2026-02-24T10:00:00Z",
                "confidence": 0.9,
            },
            {
                "schema_version": "1.0",
                "lesson_id": "lesson_ui_low",
                "scope_skill": "ui-ux-creative-coding",
                "scope_profile": "ui",
                "status": "active",
                "effective_from": "2026-02-24T09:00:00Z",
                "confidence": 0.4,
            },
            {
                "schema_version": "1.0",
                "lesson_id": "lesson_other_scope",
                "scope_skill": "interface-craft",
                "scope_profile": "ui",
                "status": "active",
                "effective_from": "2026-02-24T11:00:00Z",
                "confidence": 0.95,
            },
        ]
        lessons_file.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")

        returncode, run_dir = self._run_loop(
            "--lessons-jsonl",
            str(lessons_file),
            "--max-injected-lessons",
            "2",
            "--low-confidence-threshold",
            "0.6",
            "--rollout-mode",
            "active",
            "--uplift-gate-mode",
            "observe",
        )
        self.assertIn(returncode, {0, 2, 3, 4, 5})

        run_obj = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
        capture = json.loads((run_dir / "capture_record.json").read_text(encoding="utf-8"))
        promotion = json.loads((run_dir / "promotion_decision.json").read_text(encoding="utf-8"))

        injected = run_obj.get("injected_lessons", [])
        self.assertEqual(len(injected), 2)
        self.assertEqual(injected[0]["lesson_id"], "lesson_ui_high")
        self.assertEqual(injected[1]["lesson_id"], "lesson_ui_low")
        self.assertNotIn("", [item["lesson_id"] for item in injected])
        self.assertFalse(bool(injected[0]["low_confidence_flag"]))
        self.assertTrue(bool(injected[1]["low_confidence_flag"]))
        self.assertEqual(injected[1]["warning"], "low_confidence_downranked")

        self.assertEqual(
            promotion.get("injected_lesson_ids", []),
            [item["lesson_id"] for item in injected],
        )
        self.assertEqual(capture.get("injected_lessons", {}).get("count"), 2)

    def test_observe_only_default_disables_auto_apply(self) -> None:
        lessons_dir = Path(tempfile.mkdtemp(prefix="lessons-observe-"))
        lessons_file = lessons_dir / "canonical-lessons.jsonl"
        rows = [
            {
                "schema_version": "1.0",
                "lesson_id": "lesson_ui_high",
                "scope_skill": "ui-ux-creative-coding",
                "scope_profile": "ui",
                "status": "active",
                "effective_from": "2026-02-24T10:00:00Z",
                "confidence": 0.9,
            }
        ]
        lessons_file.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")

        returncode, run_dir = self._run_loop("--lessons-jsonl", str(lessons_file))
        self.assertIn(returncode, {0, 2, 3, 4, 5})

        run_obj = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
        controls = run_obj.get("runtime_controls", {})
        self.assertEqual(controls.get("rollout_mode"), "observe_only")
        self.assertFalse(bool(controls.get("auto_apply_enabled")))
        self.assertEqual(run_obj.get("injected_lessons", []), [])
        self.assertEqual(run_obj.get("injection_summary", {}).get("retrieved_count"), 1)
        self.assertEqual(run_obj.get("injection_summary", {}).get("selected_count"), 0)

    def test_rollout_mode_off_blocks_run_and_disables_capture(self) -> None:
        returncode, run_dir = self._run_loop("--rollout-mode", "off")
        self.assertEqual(returncode, 5)

        run_obj = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
        blocker = json.loads((run_dir / "run_blocker.json").read_text(encoding="utf-8"))
        controls = run_obj.get("runtime_controls", {})

        self.assertEqual(controls.get("rollout_mode"), "off")
        self.assertFalse(bool(controls.get("auto_capture_enabled")))
        self.assertFalse(bool(controls.get("auto_apply_enabled")))
        self.assertEqual(blocker.get("code"), "run_rollforward_blocked")
        self.assertFalse((run_dir / "capture_record.json").exists())

    def test_global_and_per_skill_kill_switches_disable_auto_paths(self) -> None:
        controls_dir = Path(tempfile.mkdtemp(prefix="controls-test-"))
        (controls_dir / "auto_capture.disabled").write_text("1\n", encoding="utf-8")
        skill_switch = controls_dir / "skills" / "ui-ux-creative-coding" / "auto_apply.disabled"
        skill_switch.parent.mkdir(parents=True, exist_ok=True)
        skill_switch.write_text("1\n", encoding="utf-8")

        lessons_file = controls_dir / "canonical-lessons.jsonl"
        lessons_file.write_text(
            json.dumps(
                {
                    "schema_version": "1.0",
                    "lesson_id": "lesson_ui_high",
                    "scope_skill": "ui-ux-creative-coding",
                    "scope_profile": "ui",
                    "status": "active",
                    "effective_from": "2026-02-24T10:00:00Z",
                    "confidence": 0.9,
                }
            )
            + "\n",
            encoding="utf-8",
        )

        returncode, run_dir = self._run_loop(
            "--rollout-mode",
            "active",
            "--controls-dir",
            str(controls_dir),
            "--lessons-jsonl",
            str(lessons_file),
        )
        self.assertIn(returncode, {0, 2, 3, 4, 5})

        run_obj = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
        controls = run_obj.get("runtime_controls", {})
        reasons = set(controls.get("reasons", []))

        self.assertFalse(bool(controls.get("auto_capture_enabled")))
        self.assertFalse(bool(controls.get("auto_apply_enabled")))
        self.assertIn("global_auto_capture_kill_switch", reasons)
        self.assertIn("skill_auto_apply_kill_switch", reasons)
        self.assertEqual(run_obj.get("injected_lessons", []), [])
        self.assertFalse((run_dir / "capture_record.json").exists())

    def test_uplift_gate_enforce_allows_bootstrap_when_insufficient_pairs(self) -> None:
        lessons_file = Path(tempfile.mkdtemp(prefix="uplift-lessons-")) / "canonical-lessons.jsonl"
        lessons_file.write_text(
            json.dumps(
                {
                    "schema_version": "1.0",
                    "lesson_id": "lesson_ui_high",
                    "scope_skill": "ui-ux-creative-coding",
                    "scope_profile": "ui",
                    "status": "active",
                    "effective_from": "2026-02-24T10:00:00Z",
                    "confidence": 0.9,
                }
            )
            + "\n",
            encoding="utf-8",
        )

        returncode, run_dir = self._run_loop(
            "--rollout-mode",
            "active",
            "--lessons-jsonl",
            str(lessons_file),
        )
        self.assertIn(returncode, {0, 2, 3, 4, 5})

        run_obj = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
        promotion = json.loads((run_dir / "promotion_decision.json").read_text(encoding="utf-8"))
        controls = run_obj.get("runtime_controls", {})
        reasons = set(controls.get("reasons", []))
        uplift = promotion.get("counterfactual_uplift", {})

        self.assertTrue(bool(controls.get("auto_apply_enabled")))
        self.assertIn("uplift_auto_apply_gate_bootstrap_insufficient_data", reasons)
        self.assertEqual(promotion.get("schema_version"), "1.1")
        self.assertEqual(uplift.get("promotion_decision"), "insufficient_data")
        self.assertEqual(uplift.get("auto_apply_decision"), "insufficient_data")
        self.assertGreaterEqual(len(run_obj.get("injected_lessons", [])), 1)


if __name__ == "__main__":
    unittest.main()
