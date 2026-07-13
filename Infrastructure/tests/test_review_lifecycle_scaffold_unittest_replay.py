from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Infrastructure" / "scripts" / "validation-and-linting"))

from review_lifecycle_scaffold_unittest_replay import (  # noqa: E402
    EXPECTED_ARGV,
    _adversarial_findings,
    _build_report,
    _observe_transcript,
)
import review_lifecycle_scaffold_unittest_replay as replay  # noqa: E402


class TestReviewLifecycleScaffoldUnittestReplay(unittest.TestCase):
    def test_exact_command_and_positive_marker_are_stable(self) -> None:
        self.assertEqual(
            EXPECTED_ARGV,
            (
                "python3",
                "-m",
                "unittest",
                "Infrastructure.scripts.testing.test_skill_creator_lifecycle_scaffold",
                "-v",
            ),
        )
        status, evidence = _observe_transcript("Ran 4 tests in 0.135s\nOK\n")
        self.assertEqual(status, "pass")
        self.assertIn("lifecycle_scaffold_unittest_test_count:4", evidence)

    def test_malformed_and_ambiguous_markers_fail_closed(self) -> None:
        for transcript in (
            "Ran 3 tests in 0.135s\nOK\n",
            "Ran 4 tests in .135s\nOK\n",
            "Ran 4 tests in 0.135s\nFAILED (failures=1)\nOK\n",
            "Ran 4 tests in 0.135s\nOK\ntrailing\n",
        ):
            status, evidence = _observe_transcript(transcript)
            self.assertEqual(status, "fail")
            self.assertEqual(evidence, ["lifecycle_scaffold_unittest_receipt:invalid_marker"])

    def test_adversarial_findings_reject_unsafe_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "stabilization_replay.py"
            test = Path(temp_dir) / "test_replay.py"
            source.write_text("ALLOWLIST = set()\n", encoding="utf-8")
            test.write_text("# no replay coverage\n", encoding="utf-8")
            findings = _adversarial_findings(source, test)
        messages = [finding["message"] for finding in findings]
        self.assertTrue(any("exact lifecycle unittest argv" in message for message in messages))
        self.assertTrue(any("negative replay" in message for message in messages))

    def test_build_report_is_machine_readable_and_fails_closed(self) -> None:
        report = _build_report("adversarial", [{"severity": "blocker", "message": "x"}], [])
        self.assertEqual(report["schema_version"], "skills-sdk.lifecycle-scaffold-unittest-review.v1")
        self.assertEqual(report["status"], "blocked_validation")
        json.dumps(report)

    def test_worker_review_requires_the_bounded_transcript_marker(self) -> None:
        with (
            mock.patch.object(replay, "_candidate_findings", return_value=[]),
            mock.patch.object(replay, "_status_snapshot", side_effect=("", "")),
            mock.patch.object(replay, "_run", return_value=(0, "Ran 3 tests in 0.135s\nOK\n", "")),
        ):
            findings, evidence = replay._worker_findings()
        self.assertTrue(any("transcript did not contain" in finding["message"] for finding in findings))
        self.assertEqual(evidence[0]["transcript_status"], "fail")


if __name__ == "__main__":
    unittest.main()
