#!/usr/bin/env python3
"""Regression tests for Phase 4 capture/evidence artifacts."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
SCRIPT_PATH = Path(__file__).with_name("recursive_skill_loop.py")
PROFILE_PATH = (
    REPO_ROOT / "Docs" / "skill-graphs" / "schemas" / "examples" / "ui-skills-profile.example.json"
)
MODULE_SPEC = importlib.util.spec_from_file_location("recursive_skill_loop_module", SCRIPT_PATH)
assert MODULE_SPEC and MODULE_SPEC.loader
RECURSIVE_LOOP_MODULE = importlib.util.module_from_spec(MODULE_SPEC)
sys.modules[MODULE_SPEC.name] = RECURSIVE_LOOP_MODULE
MODULE_SPEC.loader.exec_module(RECURSIVE_LOOP_MODULE)


class RecursiveLoopCaptureTests(unittest.TestCase):
    def _run_loop(
        self,
        *extra_args: str,
        stdin_text: str | None = None,
    ) -> tuple[subprocess.CompletedProcess[str], Path]:
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
        proc = subprocess.run(cmd, cwd=REPO_ROOT, text=True, input=stdin_text, capture_output=True)
        run_dirs = sorted(out_root.glob("run_*"))
        self.assertTrue(run_dirs, msg=f"expected run_* dir, stderr={proc.stderr}")
        return proc, run_dirs[-1]

    def _make_profile(self) -> object:
        return RECURSIVE_LOOP_MODULE.Profile(
            schema_version="1.0",
            profile_id="frontend-ui-frontend-ui-design",
            scope_skill="frontend/ui/frontend-ui-design",
            scope_profile="frontend",
            rubric_version="2026-03-21",
            evaluator_version="v1-frontend-learning",
            persona_set_id="frontend-ui-design-v1",
            thresholds=RECURSIVE_LOOP_MODULE.Thresholds(
                stability_consecutive_passes=2,
                critical_non_regression=True,
                max_iterations=5,
                max_elapsed_ms=180000,
                max_tokens=16000,
                no_improvement_escalation_limit=2,
            ),
            criteria=[
                RECURSIVE_LOOP_MODULE.Criterion(
                    id="visual_distinction",
                    label="Visual distinction",
                    threshold=0.68,
                    weight=0.1,
                    critical=False,
                ),
                RECURSIVE_LOOP_MODULE.Criterion(
                    id="hierarchy_primary_action",
                    label="Hierarchy and primary action",
                    threshold=0.74,
                    weight=0.18,
                    critical=True,
                ),
            ],
            delegation=RECURSIVE_LOOP_MODULE.DelegationDecision(
                mode="co-pilot",
                human_baseline_minutes=75.0,
                ai_process_minutes=25.0,
                probability_of_success=0.78,
                rationale="Frontend UI design benefits from repeated human plus agent review.",
            ),
            learning_posture={
                "supported": ["learn", "guided", "execute"],
                "default": "guided",
                "feedback_capture": {
                    "prompt_on_terminal": True,
                    "interactive_only": True,
                },
            },
        )

    def test_capture_record_and_evidence_packet_written_on_normal_run(self) -> None:
        proc, run_dir = self._run_loop(
            "--feedback-outcome",
            "worked",
            "--feedback-note",
            "good output quality",
        )
        self.assertIn(proc.returncode, {0, 2, 3, 4, 5})

        capture = json.loads((run_dir / "capture_record.json").read_text(encoding="utf-8"))
        evidence = json.loads((run_dir / "evidence_packet.json").read_text(encoding="utf-8"))
        promotion = json.loads((run_dir / "promotion_decision.json").read_text(encoding="utf-8"))
        observations = json.loads((run_dir / "lesson_observations.json").read_text(encoding="utf-8"))
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
        self.assertGreaterEqual(len(observations["items"]), len(candidates["items"]))
        self.assertEqual(capture["lesson_observations"]["count"], len(observations["items"]))
        self.assertEqual(len(promotion["lesson_candidates"]), len(candidates["items"]))
        self.assertGreaterEqual(len(candidates["items"]), 1)
        self.assertIn("score", evidence["completeness"])
        for key in ("events", "logs", "traces", "session_signals", "checks"):
            self.assertIn(key, evidence["completeness"])

    def test_capture_artifacts_exist_when_run_is_blocked(self) -> None:
        with tempfile.NamedTemporaryFile("w", delete=False) as f:
            f.write("1\n")
            rollback_flag = f.name

        proc, run_dir = self._run_loop("--rollback-required-file", rollback_flag)
        self.assertEqual(proc.returncode, 5)

        capture = json.loads((run_dir / "capture_record.json").read_text(encoding="utf-8"))
        evidence = json.loads((run_dir / "evidence_packet.json").read_text(encoding="utf-8"))
        run_obj = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
        observations = json.loads((run_dir / "lesson_observations.json").read_text(encoding="utf-8"))
        candidates = json.loads((run_dir / "lesson_candidates.json").read_text(encoding="utf-8"))

        self.assertEqual(capture["feedback"]["status"], "missing")
        self.assertEqual(capture["output_summary"]["terminal_status"], run_obj["terminal_status"])
        self.assertEqual(evidence["run_id"], run_obj["run_id"])
        self.assertEqual(observations["items"], [])
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

        proc, run_dir = self._run_loop(
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
        self.assertIn(proc.returncode, {0, 2, 3, 4, 5})

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

    def test_retrieve_and_rank_lessons_includes_guidance_payload(self) -> None:
        lessons_dir = Path(tempfile.mkdtemp(prefix="lessons-guidance-"))
        lessons_file = lessons_dir / "canonical-lessons.jsonl"
        row = {
            "schema_version": "1.0",
            "lesson_id": "frontend-ui-design-accessibility-before-polish-v1",
            "scope_skill": "frontend/ui/frontend-ui-design",
            "scope_profile": "frontend",
            "status": "candidate",
            "effective_from": "2026-03-31T15:30:00Z",
            "confidence": 0.62,
            "title": "Frontend UI Design: stabilize accessibility before polish",
            "summary": "Front-load accessibility and state coverage before decorative polish.",
            "guidance": [
                "Restate default, loading, empty, error, and disabled states before proposing embellishment.",
                "Name keyboard focus order, contrast expectations, and reduced-motion behavior explicitly.",
            ],
            "checkpoints": [
                "Did the guidance restate a complete state matrix?",
                "Did the guidance define focus, contrast, and reduced-motion requirements?",
            ],
            "methodology_stage": "documentation",
            "source_note": "/docs/skill-graphs/pilots/interventions/frontend-ui-design-accessibility-before-polish.md",
        }
        lessons_file.write_text(json.dumps(row) + "\n", encoding="utf-8")

        injection = RECURSIVE_LOOP_MODULE.retrieve_and_rank_lessons(
            profile=self._make_profile(),
            lessons_file=lessons_file,
            max_lessons=1,
            low_confidence_threshold=0.6,
        )

        self.assertEqual(injection["selected_count"], 1)
        selected = injection["selected"][0]
        self.assertEqual(selected["lesson_id"], row["lesson_id"])
        self.assertEqual(selected["title"], row["title"])
        self.assertEqual(selected["summary"], row["summary"])
        self.assertEqual(selected["guidance"], row["guidance"])
        self.assertEqual(selected["checkpoints"], row["checkpoints"])
        self.assertEqual(selected["methodology_stage"], "documentation")
        self.assertIn("Summary: Front-load accessibility and state coverage before decorative polish.", injection["injection_text"])
        self.assertIn("Restate default, loading, empty, error, and disabled states before proposing embellishment.", injection["injection_text"])
        self.assertIn("Did the guidance define focus, contrast, and reduced-motion requirements?", injection["injection_text"])
        self.assertIn("Methodology stage: documentation", injection["injection_text"])
        self.assertIn(
            "Source note: /docs/skill-graphs/pilots/interventions/frontend-ui-design-accessibility-before-polish.md",
            injection["injection_text"],
        )

    def test_observe_only_default_disables_auto_apply(self) -> None:
        lessons_dir = Path(tempfile.mkdtemp(prefix="lessons-observe-"))
        lessons_file = lessons_dir / "canonical-lessons.jsonl"
        controls_dir = Path(tempfile.mkdtemp(prefix="controls-observe-"))
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

        proc, run_dir = self._run_loop(
            "--controls-dir",
            str(controls_dir),
            "--lessons-jsonl",
            str(lessons_file),
        )
        self.assertIn(proc.returncode, {0, 2, 3, 4, 5})

        run_obj = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
        controls = run_obj.get("runtime_controls", {})
        self.assertEqual(controls.get("rollout_mode"), "observe_only")
        self.assertFalse(bool(controls.get("auto_apply_enabled")))
        self.assertEqual(run_obj.get("injected_lessons", []), [])
        self.assertEqual(run_obj.get("injection_summary", {}).get("retrieved_count"), 1)
        self.assertEqual(run_obj.get("injection_summary", {}).get("selected_count"), 0)

    def test_rollout_mode_off_blocks_run_and_disables_capture(self) -> None:
        proc, run_dir = self._run_loop("--rollout-mode", "off")
        self.assertEqual(proc.returncode, 5)

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

        proc, run_dir = self._run_loop(
            "--rollout-mode",
            "active",
            "--controls-dir",
            str(controls_dir),
            "--lessons-jsonl",
            str(lessons_file),
        )
        self.assertIn(proc.returncode, {0, 2, 3, 4, 5})

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

        proc, run_dir = self._run_loop(
            "--rollout-mode",
            "active",
            "--lessons-jsonl",
            str(lessons_file),
        )
        self.assertIn(proc.returncode, {0, 2, 3, 4, 5})

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

    def test_prompt_for_feedback_records_terminal_phase_feedback_after_status_output(self) -> None:
        proc, run_dir = self._run_loop(
            "--prompt-for-feedback",
            stdin_text="worked\nStrong hierarchy and useful direction.\n",
        )
        self.assertIn(proc.returncode, {0, 2, 3, 4, 5})

        stdout = proc.stdout
        status_index = stdout.index("[recursive-loop] status=")
        question_index = stdout.index("[recursive-loop] feedback_question=")
        self.assertLess(status_index, question_index)

        capture = json.loads((run_dir / "capture_record.json").read_text(encoding="utf-8"))
        events = [
            json.loads(line)
            for line in (run_dir / "events.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

        self.assertEqual(capture["feedback"]["status"], "worked")
        self.assertEqual(capture["feedback"]["source"], "terminal_prompt")
        self.assertEqual(capture["feedback"]["note"], "Strong hierarchy and useful direction.")

        event_types = [event["event_type"] for event in events]
        self.assertIn("post_run_feedback_prompted", event_types)
        self.assertIn("post_run_feedback_recorded", event_types)

    def test_prompt_for_feedback_is_skippable_and_degrades_to_missing(self) -> None:
        proc, run_dir = self._run_loop(
            "--prompt-for-feedback",
            stdin_text="\n",
        )
        self.assertIn(proc.returncode, {0, 2, 3, 4, 5})

        capture = json.loads((run_dir / "capture_record.json").read_text(encoding="utf-8"))
        self.assertEqual(capture["feedback"]["status"], "missing")
        self.assertEqual(capture["feedback"]["source"], "terminal_prompt_skipped")

    def test_prompt_for_feedback_is_non_blocking_without_ready_terminal_input(self) -> None:
        proc, run_dir = self._run_loop("--prompt-for-feedback")
        self.assertIn(proc.returncode, {0, 2, 3, 4, 5})

        capture = json.loads((run_dir / "capture_record.json").read_text(encoding="utf-8"))
        events = [
            json.loads(line)
            for line in (run_dir / "events.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

        self.assertEqual(capture["feedback"]["status"], "missing")
        self.assertEqual(capture["feedback"]["source"], "terminal_prompt_unanswered")
        recorded = next(event for event in events if event["event_type"] == "post_run_feedback_recorded")
        self.assertEqual(recorded["question_outcome"], "missing")
        self.assertFalse(bool(recorded["blocking"]))

    def test_feedback_prompt_wait_seconds_gives_tty_grace_period(self) -> None:
        self.assertGreater(
            RECURSIVE_LOOP_MODULE.feedback_prompt_wait_seconds(stdin_is_tty=True),
            0.0,
        )
        self.assertEqual(
            RECURSIVE_LOOP_MODULE.feedback_prompt_wait_seconds(stdin_is_tty=False),
            0.0,
        )
        self.assertGreater(
            RECURSIVE_LOOP_MODULE.feedback_prompt_wait_seconds(stdin_is_tty=True, note_prompt=True),
            0.0,
        )

    def test_prompt_interrupt_still_flushes_run_artifacts_before_feedback_capture(self) -> None:
        out_root = Path(tempfile.mkdtemp(prefix="recursive-loop-interrupt-"))
        args = RECURSIVE_LOOP_MODULE.build_parser().parse_args(
            [
                "--profile-file",
                str(PROFILE_PATH),
                "--objective",
                "Test objective for prompt interrupt artifact flushing.",
                "--out-root",
                str(out_root),
                "--run-owner",
                "test-owner",
                "--prompt-for-feedback",
            ]
        )

        with self.assertRaises(KeyboardInterrupt):
            with unittest.mock.patch.object(
                RECURSIVE_LOOP_MODULE,
                "prompt_for_feedback",
                side_effect=KeyboardInterrupt(),
            ):
                RECURSIVE_LOOP_MODULE.run_loop(args)

        run_dirs = sorted(out_root.glob("run_*"))
        self.assertTrue(run_dirs)
        run_dir = run_dirs[-1]
        self.assertTrue((run_dir / "events.jsonl").exists())
        self.assertTrue((run_dir / "capture_record.json").exists())
        self.assertTrue((run_dir / "evidence_packet.json").exists())

    def test_worked_feedback_prioritizes_positive_pattern_candidates(self) -> None:
        profile = self._make_profile()
        observations = RECURSIVE_LOOP_MODULE.build_lesson_observations(
            run_id="run_test",
            profile=profile,
            iteration_rows=[
                {
                    "iteration_id": 2,
                    "diagnosis": {
                        "reason": "Tighten hierarchy and reinforce strong layout choices.",
                        "weakest_criteria": ["hierarchy_primary_action"],
                        "deficits": {"hierarchy_primary_action": 0.12},
                    },
                    "improvement_action": {
                        "summary": "Strengthened hero hierarchy and refined spacing rhythm.",
                    },
                    "criterion_deltas": {
                        "visual_distinction": 0.22,
                        "hierarchy_primary_action": 0.08,
                    },
                }
            ],
            run_obj={
                "terminal_status": "passed",
                "stop_reason": "pass",
                "delegation": {"mode": "co-pilot"},
            },
            feedback={
                "status": "worked",
                "note": "The stronger visual direction landed well.",
            },
            confidence={
                "score": 0.86,
                "bucket": "high",
                "calibration_bucket": "C1_high_confidence",
                "quality_uplift": 0.09,
            },
            evidence_packet={"completeness": {"score": 1.0}},
        )
        candidates = RECURSIVE_LOOP_MODULE.build_lesson_candidates(
            run_id="run_test",
            profile=profile,
            iteration_rows=[
                {
                    "iteration_id": 2,
                    "diagnosis": {
                        "reason": "Tighten hierarchy and reinforce strong layout choices.",
                        "weakest_criteria": ["hierarchy_primary_action"],
                        "deficits": {"hierarchy_primary_action": 0.12},
                    },
                    "improvement_action": {
                        "summary": "Strengthened hero hierarchy and refined spacing rhythm.",
                    },
                    "criterion_deltas": {
                        "visual_distinction": 0.22,
                        "hierarchy_primary_action": 0.08,
                    },
                }
            ],
            run_obj={
                "terminal_status": "passed",
                "stop_reason": "pass",
                "delegation": {"mode": "co-pilot"},
            },
            feedback={
                "status": "worked",
                "note": "The stronger visual direction landed well.",
            },
            confidence={
                "score": 0.86,
                "bucket": "high",
                "calibration_bucket": "C1_high_confidence",
                "quality_uplift": 0.09,
            },
            evidence_packet={"completeness": {"score": 1.0}},
        )

        self.assertGreaterEqual(len(observations), 1)
        self.assertEqual(observations[0]["observation_type"], "positive_pattern")
        self.assertGreaterEqual(len(candidates), 1)
        self.assertEqual(candidates[0]["observation_type"], "positive_pattern")
        self.assertEqual(candidates[0]["source_observation"]["feedback_status"], "worked")
        self.assertIn("selection", candidates[0])

    def test_didnt_work_feedback_prioritizes_remediation_candidates(self) -> None:
        profile = self._make_profile()
        candidates = RECURSIVE_LOOP_MODULE.build_lesson_candidates(
            run_id="run_test",
            profile=profile,
            iteration_rows=[
                {
                    "iteration_id": 2,
                    "diagnosis": {
                        "reason": "Hierarchy remained weak and needs clearer primary action.",
                        "weakest_criteria": ["hierarchy_primary_action"],
                        "deficits": {"hierarchy_primary_action": 0.18},
                    },
                    "improvement_action": {
                        "summary": "Attempted hierarchy fixes but the result still felt crowded.",
                    },
                    "criterion_deltas": {
                        "visual_distinction": 0.16,
                    },
                }
            ],
            run_obj={
                "terminal_status": "failed",
                "stop_reason": "budget_exhausted",
                "delegation": {"mode": "co-pilot"},
            },
            feedback={
                "status": "didnt_work",
                "note": "It still felt generic and the hierarchy was unclear.",
            },
            confidence={
                "score": 0.48,
                "bucket": "low",
                "calibration_bucket": "C3_low_confidence",
                "quality_uplift": -0.02,
            },
            evidence_packet={"completeness": {"score": 1.0}},
        )

        self.assertGreaterEqual(len(candidates), 1)
        self.assertEqual(candidates[0]["observation_type"], "remediation")
        self.assertEqual(candidates[0]["source_observation"]["feedback_status"], "didnt_work")
        self.assertIn("selection", candidates[0])

    def test_profile_learning_posture_can_auto_enable_terminal_feedback(self) -> None:
        profile = self._make_profile()

        self.assertTrue(
            RECURSIVE_LOOP_MODULE.should_prompt_for_feedback(
                profile=profile,
                explicit_prompt_requested=False,
                feedback_outcome_present=False,
                stdin_is_tty=True,
                stdout_is_tty=True,
            )
        )
        self.assertFalse(
            RECURSIVE_LOOP_MODULE.should_prompt_for_feedback(
                profile=profile,
                explicit_prompt_requested=False,
                feedback_outcome_present=False,
                stdin_is_tty=False,
                stdout_is_tty=False,
            )
        )

    def test_profile_id_rejects_path_traversal_values(self) -> None:
        profile = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
        profile["profile_id"] = "../../tmp/evil"

        with tempfile.TemporaryDirectory(prefix="profile-id-") as tmp_dir:
            tmp_path = Path(tmp_dir)
            profile_path = tmp_path / "bad-profile.json"
            out_root = tmp_path / "out"
            profile_path.write_text(json.dumps(profile), encoding="utf-8")

            cmd = [
                sys.executable,
                str(SCRIPT_PATH),
                "--profile-file",
                str(profile_path),
                "--objective",
                "Path traversal regression test.",
                "--out-root",
                str(out_root),
            ]
            proc = subprocess.run(cmd, cwd=REPO_ROOT, text=True, capture_output=True)

            self.assertEqual(proc.returncode, 1)
            self.assertIn("profile_id", proc.stderr)
            self.assertFalse((out_root / "escape.lock").exists())


if __name__ == "__main__":
    unittest.main()
