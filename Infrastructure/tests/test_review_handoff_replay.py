from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Infrastructure" / "scripts" / "validation-and-linting"))
sys.path.insert(0, str(ROOT / "Infrastructure" / "scripts" / "lib"))

from review_handoff_replay import (  # noqa: E402
    EXPECTED_HANDOFF_ARGV,
    EXPECTED_PLAN_ARGV,
    _adversarial_findings,
    _classify_handoff_payload,
    _cleanup,
)
import review_handoff_replay as replay  # noqa: E402
from ask.skills_sdk.review_plan import _target_digest as canonical_target_digest  # noqa: E402


def _positive_payload() -> dict[str, object]:
    return {
        "status": "success",
        "data": {
            "review_handoff": {
                "schema_version": "skills-sdk.review-handoff-receipt.v1",
                "status": "pass",
                "source_review_plan": {
                    "path": ".harness/artifacts/sdk-review-plan/simplify.json",
                    "schema_version": "skills-sdk.review-plan-receipt.v1",
                    "receipt_sha256": "a" * 64,
                    "receipt_instance_id": "rp_fixturereviewplan",
                },
                "mutation_performed": False,
                "receipt_written": False,
                "receipt_path": None,
                "not_proven": ["reviewers_completed", "ci_passed"],
            }
        },
    }


class TestReviewHandoffReplay(unittest.TestCase):
    def test_exact_setup_and_handoff_argv_are_stable(self) -> None:
        self.assertEqual(
            EXPECTED_PLAN_ARGV,
            (
                "./bin/ask",
                "sdk",
                "review",
                "plan",
                "--target",
                "Skills/agent-ops/simplify",
                "--intent",
                "validation_review",
                "--receipt-out",
                ".harness/artifacts/sdk-review-plan/simplify.json",
                "--json",
                "--robot",
            ),
        )
        self.assertEqual(
            EXPECTED_HANDOFF_ARGV,
            (
                "./bin/ask",
                "sdk",
                "review",
                "handoff",
                "--plan",
                ".harness/artifacts/sdk-review-plan/simplify.json",
                "--target",
                "Skills/agent-ops/simplify",
                "--intent",
                "validation_review",
                "--json",
                "--robot",
            ),
        )

    def test_positive_handoff_is_read_only_and_not_review_completion(self) -> None:
        findings = _classify_handoff_payload(_positive_payload())
        self.assertEqual(findings, [])

    def test_mutation_and_completion_claims_fail_closed(self) -> None:
        payload = _positive_payload()
        handoff = payload["data"]["review_handoff"]
        assert isinstance(handoff, dict)
        handoff["mutation_performed"] = True
        handoff["receipt_written"] = True
        handoff["receipt_path"] = ".harness/artifacts/sdk-review-handoff/simplify.json"
        handoff["not_proven"] = []
        messages = [finding["message"] for finding in _classify_handoff_payload(payload)]
        self.assertTrue(any("mutation_performed" in message for message in messages))
        self.assertTrue(any("receipt_written" in message for message in messages))
        self.assertTrue(any("not_proven" in message for message in messages))

    def test_wrong_status_or_schema_fails_closed(self) -> None:
        for key, value in (("status", "error"), ("schema_version", "wrong.schema")):
            payload = _positive_payload()
            handoff = payload["data"]["review_handoff"]
            assert isinstance(handoff, dict)
            handoff[key] = value
            self.assertTrue(_classify_handoff_payload(payload))

    def test_adversarial_review_requires_negative_contracts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "review_handoff_replay.py"
            test = Path(temp_dir) / "test_review_handoff_replay.py"
            source.write_text("EXPECTED_HANDOFF_ARGV = ()\n", encoding="utf-8")
            test.write_text("# no negative replay\n", encoding="utf-8")
            findings = _adversarial_findings(source, test)
        messages = [finding["message"] for finding in findings]
        self.assertTrue(any("exact handoff argv" in message for message in messages))
        self.assertTrue(any("negative replay" in message for message in messages))

    def test_adversarial_review_does_not_scan_boundary_prose_as_authority(self) -> None:
        findings = _adversarial_findings()
        messages = [finding["message"] for finding in findings]
        self.assertFalse(any("execution or external-access authority" in message for message in messages))

    def test_findings_are_json_serializable(self) -> None:
        json.dumps(_classify_handoff_payload(_positive_payload()))

    def test_target_digest_matches_the_canonical_review_plan_contract(self) -> None:
        status, digest, findings = canonical_target_digest(ROOT / "Skills/agent-ops/simplify")
        self.assertEqual(status, "available")
        self.assertIsNotNone(digest)
        self.assertEqual(findings, [])
        self.assertEqual(replay._target_digest(), digest)

    def test_cleanup_removes_only_empty_generated_trace_directories(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            plan_path = root / "artifacts" / "sdk-review-plan" / "simplify.json"
            trace_dir = root / "artifacts" / "sdk-review-plan" / "traces"
            trace_path = trace_dir / ("a" * 64 + ".trace.json")
            plan_path.parent.mkdir(parents=True)
            trace_dir.mkdir()
            plan_path.write_text("{}\n", encoding="utf-8")
            trace_path.write_text("{}\n", encoding="utf-8")
            with mock.patch.object(replay, "PLAN_PATH", plan_path), mock.patch.object(replay, "TRACE_DIR", trace_dir):
                _cleanup(False, set(), {trace_path})
            self.assertFalse(plan_path.exists())
            self.assertFalse(trace_path.exists())
            self.assertFalse(trace_dir.exists())


if __name__ == "__main__":
    unittest.main()
