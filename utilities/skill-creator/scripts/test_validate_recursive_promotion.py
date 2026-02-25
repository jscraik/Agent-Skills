#!/usr/bin/env python3
"""Tests for uplift/match-quality validation contracts."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
VALIDATOR = REPO_ROOT / "utilities" / "skill-creator" / "scripts" / "validate_recursive_promotion.py"


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class ValidateRecursivePromotionTests(unittest.TestCase):
    def _build_run(self, *, promotion_decision_state: str = "pass") -> tuple[Path, Path]:
        run_dir = Path(tempfile.mkdtemp(prefix="validate-promotion-", dir=REPO_ROOT / "artifacts"))
        self.addCleanup(lambda: shutil.rmtree(run_dir, ignore_errors=True))
        run_id = "run_test_counterfactual"
        lesson_file = run_dir / "lesson.md"
        lesson_file.write_text("Safe lesson body.\n", encoding="utf-8")

        run_obj = {
            "schema_version": "1.0",
            "run_id": run_id,
            "profile_id": "ui-ux-creative-coding",
            "terminal_status": "passed",
            "stop_reason": "pass",
            "prompt_hash": "hash-123",
            "versions": {
                "rubric_version": "2026-02-19",
                "evaluator_version": "v1",
            },
            "counters": {"iterations_completed": 1},
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
        (run_dir / "iteration_journal.jsonl").write_text(
            json.dumps(journal_row) + "\n",
            encoding="utf-8",
        )

        event_row = {
            "event_type": "promotion_approved",
            "run_id": run_id,
        }
        (run_dir / "events.jsonl").write_text(json.dumps(event_row) + "\n", encoding="utf-8")

        counterfactual = {
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
            "promotion_decision": promotion_decision_state,
            "auto_apply_decision": "hold",
        }
        decision = {
            "schema_version": "1.1",
            "run_id": run_id,
            "lesson_id": "lesson_ui_001",
            "decision": "approved",
            "reviewer_ids": ["jamie"],
            "expected_version": "v1",
            "lesson_status": "active",
            "canonical_version": "v1",
            "lesson_source_path": "lesson.md",
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
            "counterfactual_uplift": counterfactual,
        }
        decision_path = run_dir / "promotion_decision.json"
        decision_path.write_text(json.dumps(decision, indent=2), encoding="utf-8")
        return run_dir, decision_path

    def _run_validator(self, run_dir: Path, decision_path: Path) -> dict:
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
        return json.loads(proc.stdout.strip().splitlines()[-1])

    def test_approved_decision_passes_with_valid_counterfactual_contract(self) -> None:
        run_dir, decision_path = self._build_run(promotion_decision_state="pass")
        report = self._run_validator(run_dir, decision_path)
        self.assertEqual(report["status"], "ok")

    def test_approved_decision_fails_when_counterfactual_not_passed(self) -> None:
        run_dir, decision_path = self._build_run(promotion_decision_state="hold")
        report = self._run_validator(run_dir, decision_path)
        self.assertEqual(report["status"], "fail")
        self.assertTrue(
            any("counterfactual_uplift.promotion_decision=pass" in err for err in report["errors"])
        )


if __name__ == "__main__":
    unittest.main()
