#!/usr/bin/env python3
"""Tests for recursive promotion validation contracts."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict

import unittest


REPO_ROOT = Path(__file__).resolve().parents[3]
VALIDATOR = REPO_ROOT / "utilities" / "skill-builder" / "scripts" / "validate_recursive_promotion.py"


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _to_row_error_codes(report: Dict[str, Any]) -> set[str]:
    codes = set()
    for item in report.get("errors", []):
        if isinstance(item, dict):
            code = item.get("code")
            if isinstance(code, str):
                codes.add(code)
    return codes


class ValidateRecursivePromotionTests(unittest.TestCase):
    def _run_script(self, run_dir: Path, decision_path: Path) -> Dict[str, Any]:
        proc = subprocess.run(
            [
                sys.executable,
                str(VALIDATOR),
                "--run-dir",
                str(run_dir),
                "--decision-file",
                str(decision_path),
            ],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(proc.stdout.strip(), "", msg=proc.stderr)
        return json.loads(proc.stdout.strip())

    def _build_run(
        self,
        run_dir: Path,
        decision_state: str,
        decision_promotion: str,
        *,
        terminal_status: str = "passed",
        stop_reason: str = "pass",
        auto_capture_enabled: bool = True,
        include_capture_artifacts: bool = True,
    ) -> Dict[str, Any]:
        run_id = run_dir.name
        lesson_file = run_dir / "lesson.md"
        lesson_file.write_text("Safe lesson body.\n", encoding="utf-8")

        run_obj = {
            "schema_version": "1.0",
            "run_id": run_id,
            "profile_id": "ui-ux-creative-coding",
            "terminal_status": terminal_status,
            "stop_reason": stop_reason,
            "prompt_hash": "hash-123",
            "scope_skill": "ui-ux-creative-coding",
            "scope_profile": "ui",
            "versions": {
                "rubric_version": "2026-02-19",
                "evaluator_version": "v1",
            },
            "counters": {"iterations_completed": 1},
            "runtime_controls": {
                "auto_capture_enabled": auto_capture_enabled,
            },
            "finished_at": "2026-02-26T12:00:00Z",
        }
        (run_dir / "run.json").write_text(json.dumps(run_obj, indent=2), encoding="utf-8")

        journal_row = {
            "run_id": run_id,
            "iteration_id": 1,
            "reevaluation_report": {
                "gate_decision": "pass",
                "non_regression_passed": True,
            },
        }
        (run_dir / "iteration_journal.jsonl").write_text(json.dumps(journal_row) + "\n", encoding="utf-8")

        if include_capture_artifacts:
            (run_dir / "capture_record.json").write_text(
                json.dumps({"schema_version": "1.0"}, indent=2),
                encoding="utf-8",
            )
            (run_dir / "evidence_packet.json").write_text(
                json.dumps({"schema_version": "1.0", "completeness_score": 1.0}, indent=2),
                encoding="utf-8",
            )
            (run_dir / "lesson_candidates.json").write_text(
                json.dumps({"schema_version": "1.0", "items": []}, indent=2),
                encoding="utf-8",
            )

        event_row = {
            "schema_version": "1.0",
            "event_id": f"evt-{run_id}",
            "ts": "2026-02-26T12:00:00Z",
            "run_id": run_id,
            "skill_name": "ui-ux-creative-coding",
            "task_profile": "ui",
            "event_type": "promotion_approved",
            "severity": "info",
            "terminal_status": terminal_status,
            "stop_reason": stop_reason,
            "actor_id": "test-suite",
            "evaluator_version": "v1",
            "rubric_version": "2026-02-19",
            "prompt_hash": "hash-123",
        }
        (run_dir / "events.jsonl").write_text(json.dumps(event_row) + "\n", encoding="utf-8")

        decision = {
            "schema_version": "1.1",
            "run_id": run_id,
            "lesson_id": f"lesson_{run_id}",
            "decision": decision_state,
            "reviewer_ids": ["jamie"],
            "expected_version": "v1",
            "lesson_status": "active",
            "lesson_source_path": str(lesson_file),
            "lesson_content_sha256": sha256_text(lesson_file.read_text(encoding="utf-8")),
            "gate_decision": {
                "runtime_gates_passed": True,
                "provenance_complete": True,
                "security_checklist_passed": True,
            },
            "provenance": {
                "prompt_hash": "hash-123",
                "rubric_version": "2026-02-19",
                "evaluator_version": "v1",
                "iteration_ids": [1],
            },
            "counterfactual_uplift": {
                "analysis_method_version": "counterfactual_uplift_v1",
                "sample_size": 50,
                "match_quality_metrics": {
                    "treated_unmatched_rate": 0.0,
                    "max_allowed_unmatched_rate": 0.15,
                    "valid": True,
                },
                "promotion_thresholds": {
                    "min_pairs_total": 40,
                    "ci_lower_min": 0.0,
                },
                "uplift_confidence_band": {
                    "method": "normal_approx_95",
                    "level": 0.95,
                    "lower": 0.01,
                    "upper": 0.09,
                },
                "promotion_decision": decision_promotion,
                "auto_apply_decision": "hold",
            },
        }
        decision_path = run_dir / "promotion_decision.json"
        decision_path.write_text(json.dumps(decision, indent=2), encoding="utf-8")
        return decision

    def test_approved_decision_passes_with_valid_counterfactual_contract(self) -> None:
        with tempfile.TemporaryDirectory(prefix="validate-promotion-") as tmpdir:
            run_dir = Path(tmpdir) / "run-approved-valid"
            run_dir.mkdir()
            self._build_run(
                run_dir=run_dir,
                decision_state="approved",
                decision_promotion="pass",
            )
            report = self._run_script(run_dir, run_dir / "promotion_decision.json")
            self.assertEqual(report["status"], "ok")

    def test_approved_decision_rejects_nonpass_counterfactual(self) -> None:
        with tempfile.TemporaryDirectory(prefix="validate-promotion-") as tmpdir:
            run_dir = Path(tmpdir) / "run-approved-hold"
            run_dir.mkdir()
            self._build_run(
                run_dir=run_dir,
                decision_state="approved",
                decision_promotion="hold",
            )
            report = self._run_script(run_dir, run_dir / "promotion_decision.json")
            self.assertEqual(report["status"], "fail")
            self.assertIn("E_APPROVED_COUNTERFACTUAL_NOT_PASS", _to_row_error_codes(report))

    def test_validator_catches_non_integer_iteration_ids(self) -> None:
        with tempfile.TemporaryDirectory(prefix="validate-promotion-") as tmpdir:
            run_dir = Path(tmpdir) / "run-invalid-journal"
            run_dir.mkdir()
            self._build_run(
                run_dir=run_dir,
                decision_state="approved",
                decision_promotion="pass",
            )
            (run_dir / "iteration_journal.jsonl").write_text(
                json.dumps(
                    {
                        "run_id": "run-invalid-journal",
                        "iteration_id": None,
                        "reevaluation_report": {
                            "gate_decision": "pass",
                            "non_regression_passed": True,
                        },
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            report = self._run_script(run_dir, run_dir / "promotion_decision.json")
            self.assertEqual(report["status"], "fail")
            self.assertIn("E_JOURNAL_ITERATION_ID_INVALID", _to_row_error_codes(report))

    def test_validator_rejects_blocked_terminal_without_required_blocker_artifacts(self) -> None:
        with tempfile.TemporaryDirectory(prefix="validate-promotion-") as tmpdir:
            run_dir = Path(tmpdir) / "run-blocker-missing"
            run_dir.mkdir()
            self._build_run(
                run_dir=run_dir,
                decision_state="candidate",
                decision_promotion="hold",
                terminal_status="failed",
                stop_reason="dependency_missing",
            )

            # Do not write run_blocker.json or rollback_recommendation.json.
            report = self._run_script(run_dir, run_dir / "promotion_decision.json")
            error_codes = _to_row_error_codes(report)
            self.assertEqual(report["status"], "fail")
            self.assertIn("E_BLOCKER_ARTIFACT_MISSING", error_codes)
            self.assertIn("E_BLOCKER_EVENT_MISMATCH", error_codes)

    def test_validator_tolerates_legacy_candidate_layout_without_events_or_capture(self) -> None:
        with tempfile.TemporaryDirectory(prefix="validate-promotion-") as tmpdir:
            run_dir = Path(tmpdir) / "run-legacy-candidate"
            run_dir.mkdir()

            lesson_file = run_dir / "lesson.md"
            lesson_file.write_text("Safe legacy lesson body.\n", encoding="utf-8")

            (run_dir / "run.json").write_text(
                json.dumps(
                    {
                        "schema_version": "1.0",
                        "run_id": run_dir.name,
                        "profile_id": "ui-ux-creative-coding",
                        "terminal_status": "passed",
                        "stop_reason": "pass",
                        "prompt_hash": "hash-legacy",
                        "scope_skill": "ui-ux-creative-coding",
                        "scope_profile": "ui",
                        "versions": {
                            "rubric_version": "2026-02-19",
                            "evaluator_version": "v1",
                        },
                        "counters": {"iterations_completed": 1},
                        "finished_at": "2026-02-26T12:00:00Z",
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
            (run_dir / "iteration_journal.jsonl").write_text(
                json.dumps(
                    {
                        "run_id": run_dir.name,
                        "iteration_id": 1,
                        "reevaluation_report": {
                            "gate_decision": "pass",
                            "non_regression_passed": True,
                        },
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            (run_dir / "promotion_decision.json").write_text(
                json.dumps(
                    {
                        "schema_version": "1.0",
                        "run_id": run_dir.name,
                        "lesson_id": f"lesson_{run_dir.name}",
                        "decision": "candidate",
                        "reviewer_ids": ["jamie"],
                        "expected_version": "v1",
                        "lesson_source_path": str(lesson_file),
                        "lesson_content_sha256": sha256_text(lesson_file.read_text(encoding="utf-8")),
                        "gate_decision": {
                            "runtime_gates_passed": True,
                            "provenance_complete": True,
                            "security_checklist_passed": True,
                        },
                        "provenance": {
                            "prompt_hash": "hash-legacy",
                            "rubric_version": "2026-02-19",
                            "evaluator_version": "v1",
                            "iteration_ids": [1],
                        },
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )

            report = self._run_script(run_dir, run_dir / "promotion_decision.json")
            self.assertEqual(report["status"], "ok")
            warning_codes = {item.get("code") for item in report.get("warnings", []) if isinstance(item, dict)}
            self.assertIn("W_LEGACY_EVENTS_FILE_MISSING", warning_codes)
            self.assertIn("W_COUNTERFACTUAL_MISSING", warning_codes)

    def test_validator_requires_events_for_legacy_approved_decisions(self) -> None:
        """Legacy mode must NOT suppress events.jsonl requirement for approved decisions."""
        with tempfile.TemporaryDirectory(prefix="validate-promotion-") as tmpdir:
            run_dir = Path(tmpdir) / "run-legacy-approved-missing-events"
            run_dir.mkdir()

            lesson_file = run_dir / "lesson.md"
            lesson_file.write_text("Safe legacy lesson body.\n", encoding="utf-8")

            (run_dir / "run.json").write_text(
                json.dumps(
                    {
                        "schema_version": "1.0",
                        "run_id": run_dir.name,
                        "profile_id": "ui-ux-creative-coding",
                        "terminal_status": "passed",
                        "stop_reason": "pass",
                        "prompt_hash": "hash-legacy",
                        "scope_skill": "ui-ux-creative-coding",
                        "scope_profile": "ui",
                        "versions": {
                            "rubric_version": "2026-02-19",
                            "evaluator_version": "v1",
                        },
                        "counters": {"iterations_completed": 1},
                        "finished_at": "2026-02-26T12:00:00Z",
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
            (run_dir / "iteration_journal.jsonl").write_text(
                json.dumps(
                    {
                        "run_id": run_dir.name,
                        "iteration_id": 1,
                        "reevaluation_report": {
                            "gate_decision": "pass",
                            "non_regression_passed": True,
                        },
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            (run_dir / "promotion_decision.json").write_text(
                json.dumps(
                    {
                        "schema_version": "1.0",
                        "run_id": run_dir.name,
                        "lesson_id": f"lesson_{run_dir.name}",
                        "decision": "approved",
                        "reviewer_ids": ["jamie"],
                        "expected_version": "v1",
                        "lesson_source_path": str(lesson_file),
                        "lesson_content_sha256": sha256_text(lesson_file.read_text(encoding="utf-8")),
                        "gate_decision": {
                            "runtime_gates_passed": True,
                            "provenance_complete": True,
                            "security_checklist_passed": True,
                        },
                        "provenance": {
                            "prompt_hash": "hash-legacy",
                            "rubric_version": "2026-02-19",
                            "evaluator_version": "v1",
                            "iteration_ids": [1],
                        },
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
            # events.jsonl intentionally absent — must be caught even in legacy mode.
            report = self._run_script(run_dir, run_dir / "promotion_decision.json")
            self.assertEqual(report["status"], "fail")
            self.assertIn("E_REQUIRED_ARTIFACT_MISSING", _to_row_error_codes(report))


if __name__ == "__main__":
    unittest.main()
