from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk.observability_feedback import (  # noqa: E402
    ObservabilityFeedbackError,
    build_observability_feedback_receipt,
)
from ask.skills_sdk.observability_promotion import build_observability_promotion_receipt  # noqa: E402
from ask.skills_sdk.package_build import build_package_digest_receipt  # noqa: E402
from ask.skills_sdk.typed_contracts import (  # noqa: E402
    validate_observability_feedback_receipt,
    validate_observability_promotion_receipt,
    validate_robot_envelope,
)
from pydantic import ValidationError  # noqa: E402


FIXTURE_SKILL = REPO_ROOT / "Infrastructure/tests/fixtures/skills_sdk/valid_skill"
REDACTED_EVENTS = "Infrastructure/tests/fixtures/skills_sdk/observability/redacted-events.fixture"
RAW_EVENTS = "Infrastructure/tests/fixtures/skills_sdk/observability/raw-events.fixture"
EVAL_RUN_FIXTURE = REPO_ROOT / "Infrastructure/tests/fixtures/skills_sdk/schema_spine/valid/eval-run-receipt.json"


def _command_env() -> dict[str, str]:
    env = os.environ.copy()
    temp_base = Path(tempfile.gettempdir()) / "agent-skills-test"
    env.setdefault("XDG_CACHE_HOME", str(temp_base / "xdg-cache"))
    env.setdefault("XDG_STATE_HOME", str(temp_base / "xdg-state"))
    env.setdefault("MISE_CACHE_DIR", str(temp_base / "mise-cache"))
    env.setdefault("UV_CACHE_DIR", str(temp_base / "uv-cache"))
    env.setdefault("MISE_TRUSTED_CONFIG_PATHS", str(REPO_ROOT / ".mise.toml"))
    return env


class TestSkillsSdkObservabilityFeedback(unittest.TestCase):
    def _package_receipt(self) -> dict:
        return build_package_digest_receipt(
            REPO_ROOT,
            source_path=FIXTURE_SKILL / "SKILL.md",
            query=FIXTURE_SKILL.as_posix(),
        )

    def _passing_eval_receipt(self, package_receipt: dict) -> dict:
        payload = json.loads(EVAL_RUN_FIXTURE.read_text(encoding="utf-8"))
        payload["package_id"] = package_receipt["package_id"]
        payload["package_digest"] = package_receipt["package_digest"]
        payload["target_path"] = "Infrastructure/tests/fixtures/skills_sdk/valid_skill/SKILL.md"
        return payload

    def _write_receipt(self, directory: Path, name: str, receipt_fixture: dict) -> str:
        path = directory / name
        with path.open("w", encoding="utf-8") as handle:
            json.dump(receipt_fixture, handle, indent=2, sort_keys=True)
            handle.write("\n")
        return path.as_posix()

    def _promotion_cli(
        self,
        *,
        feedback_path: str,
        package_path: str,
        eval_path: str,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "observability",
                "promote",
                "--feedback-receipt",
                feedback_path,
                "--package-receipt",
                package_path,
                "--eval-run-receipt",
                eval_path,
                "--preview",
                "--json",
                "--robot",
            ],
            cwd=REPO_ROOT,
            env=_command_env(),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_builder_mines_redacted_events_into_blocked_candidates(self) -> None:
        payload = build_observability_feedback_receipt(
            REPO_ROOT,
            package_receipt=self._package_receipt(),
            events_path=REDACTED_EVENTS,
        )
        receipt = validate_observability_feedback_receipt(payload)

        self.assertEqual(receipt.status, "preview")
        self.assertEqual(receipt.event_count, 1)
        self.assertEqual(len(receipt.scenario_candidates), 1)
        self.assertEqual(len(receipt.skill_gap_candidates), 1)
        self.assertEqual(receipt.scenario_candidates[0].promotion_status, "blocked_pending_package_eval")
        self.assertFalse(receipt.mutation_performed)

    def test_builder_blocks_raw_prompt_events(self) -> None:
        with self.assertRaises(ObservabilityFeedbackError) as raised:
            build_observability_feedback_receipt(
                REPO_ROOT,
                package_receipt=self._package_receipt(),
                events_path=RAW_EVENTS,
            )

        receipt = validate_observability_feedback_receipt(raised.exception.receipt)

        self.assertEqual(receipt.status, "blocked")
        self.assertFalse(receipt.mutation_performed)
        all_evidence = [item for blocker in receipt.blockers for item in blocker.evidence]
        self.assertIn("event:0:raw_keys:raw_prompt", all_evidence)

    def test_contract_rejects_duplicate_required_receipts(self) -> None:
        payload = build_observability_feedback_receipt(
            REPO_ROOT,
            package_receipt=self._package_receipt(),
            events_path=REDACTED_EVENTS,
        )
        payload["scenario_candidates"][0]["required_receipts"] = [
            "package_digest_receipt",
            "package_digest_receipt",
        ]

        with self.assertRaises(ValidationError):
            validate_observability_feedback_receipt(payload)

    def test_builder_blocks_events_for_wrong_skill_package(self) -> None:
        with tempfile.NamedTemporaryFile("w", suffix=".events", encoding="utf-8") as events:
            events.write(
                json.dumps(
                    {
                        "event_type": "skill_run",
                        "skill_id": "other-skill",
                        "outcome": "failure",
                        "redacted": True,
                        "prompt_digest": "sha256:" + "5" * 64,
                        "failure_summary": "Wrong package event must not become a candidate.",
                    }
                )
                + "\n"
            )
            events.flush()

            with self.assertRaises(ObservabilityFeedbackError) as raised:
                build_observability_feedback_receipt(
                    REPO_ROOT,
                    package_receipt=self._package_receipt(),
                    events_path=events.name,
                )

        receipt = validate_observability_feedback_receipt(raised.exception.receipt)
        all_evidence = [item for blocker in receipt.blockers for item in blocker.evidence]

        self.assertEqual(receipt.status, "blocked")
        self.assertIn("event:0:skill_id:other-skill:expected:skills-sdk-valid-fixture", all_evidence)
        self.assertEqual(receipt.scenario_candidates, [])

    def test_builder_blocks_malformed_prompt_digest(self) -> None:
        with tempfile.NamedTemporaryFile("w", suffix=".events", encoding="utf-8") as events:
            events.write(
                json.dumps(
                    {
                        "event_type": "skill_run",
                        "skill_id": "skills-sdk-valid-fixture",
                        "outcome": "failure",
                        "redacted": True,
                        "prompt_digest": "x",
                        "failure_summary": "Malformed digest must not become a candidate.",
                    }
                )
                + "\n"
            )
            events.flush()

            with self.assertRaises(ObservabilityFeedbackError) as raised:
                build_observability_feedback_receipt(
                    REPO_ROOT,
                    package_receipt=self._package_receipt(),
                    events_path=events.name,
                )

        receipt = validate_observability_feedback_receipt(raised.exception.receipt)
        all_evidence = [item for blocker in receipt.blockers for item in blocker.evidence]

        self.assertEqual(receipt.status, "blocked")
        self.assertIn("event:0:prompt_digest_malformed", all_evidence)
        self.assertEqual(receipt.scenario_candidates, [])

    def test_builder_blocks_external_event_path_without_reading_it(self) -> None:
        with self.assertRaises(ObservabilityFeedbackError) as raised:
            build_observability_feedback_receipt(
                REPO_ROOT,
                package_receipt=self._package_receipt(),
                events_path="/etc/passwd",
            )

        receipt = validate_observability_feedback_receipt(raised.exception.receipt)

        self.assertEqual(receipt.status, "blocked")
        self.assertEqual(receipt.event_count, 0)
        self.assertEqual(receipt.scenario_candidates, [])
        self.assertEqual(receipt.blockers[0].id, "events_path_allowed")

    def test_public_cli_previews_observability_feedback(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "observability",
                "feedback",
                "--skill",
                "Infrastructure/tests/fixtures/skills_sdk/valid_skill",
                "--events",
                REDACTED_EVENTS,
                "--preview",
                "--json",
                "--robot",
            ],
            cwd=REPO_ROOT,
            env=_command_env(),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        envelope = validate_robot_envelope(json.loads(completed.stdout))
        payload = envelope.data["skills_sdk_observability_feedback"]
        self.assertIsInstance(payload, dict)
        receipt = validate_observability_feedback_receipt(payload["receipt"])
        self.assertEqual(receipt.status, "preview")
        self.assertEqual(receipt.package_id, "skills-sdk-valid-fixture")

    def test_promotion_preview_marks_candidates_ready_after_package_and_eval_receipts(self) -> None:
        package_receipt = self._package_receipt()
        feedback_receipt = build_observability_feedback_receipt(
            REPO_ROOT,
            package_receipt=package_receipt,
            events_path=REDACTED_EVENTS,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            payload = build_observability_promotion_receipt(
                REPO_ROOT,
                feedback_receipt_path=self._write_receipt(tmp_path, "feedback.json", feedback_receipt),
                package_receipt_path=self._write_receipt(tmp_path, "package.json", package_receipt),
                eval_run_receipt_path=self._write_receipt(tmp_path, "eval.json", self._passing_eval_receipt(package_receipt)),
            )

        receipt = validate_observability_promotion_receipt(payload)

        self.assertEqual(receipt.status, "preview")
        self.assertEqual(receipt.candidate_count, 2)
        self.assertEqual(receipt.promotion_ready_count, 2)
        self.assertTrue(all(decision.decision == "promotion_ready" for decision in receipt.candidate_decisions))
        self.assertFalse(receipt.mutation_performed)

    def test_promotion_preview_blocks_mismatched_eval_receipt(self) -> None:
        package_receipt = self._package_receipt()
        feedback_receipt = build_observability_feedback_receipt(
            REPO_ROOT,
            package_receipt=package_receipt,
            events_path=REDACTED_EVENTS,
        )
        eval_receipt = self._passing_eval_receipt(package_receipt)
        eval_receipt["package_digest"] = "sha256:" + "9" * 64
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            payload = build_observability_promotion_receipt(
                REPO_ROOT,
                feedback_receipt_path=self._write_receipt(tmp_path, "feedback.json", feedback_receipt),
                package_receipt_path=self._write_receipt(tmp_path, "package.json", package_receipt),
                eval_run_receipt_path=self._write_receipt(tmp_path, "eval.json", eval_receipt),
            )

        receipt = validate_observability_promotion_receipt(payload)

        self.assertEqual(receipt.status, "blocked")
        self.assertEqual(receipt.promotion_ready_count, 0)
        all_blockers = [blocker for decision in receipt.candidate_decisions for blocker in decision.blockers]
        self.assertIn("eval_receipt_package_digest_mismatch", all_blockers)

    def test_promotion_preview_rejects_schema_invalid_eval_receipt(self) -> None:
        package_receipt = self._package_receipt()
        feedback_receipt = build_observability_feedback_receipt(
            REPO_ROOT,
            package_receipt=package_receipt,
            events_path=REDACTED_EVENTS,
        )
        invalid_eval_receipt = {
            "schema_version": "skills-sdk.eval-run-receipt.v0",
            "status": "pass",
            "package_id": package_receipt["package_id"],
            "package_digest": package_receipt["package_digest"],
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            payload = build_observability_promotion_receipt(
                REPO_ROOT,
                feedback_receipt_path=self._write_receipt(tmp_path, "feedback.json", feedback_receipt),
                package_receipt_path=self._write_receipt(tmp_path, "package.json", package_receipt),
                eval_run_receipt_path=self._write_receipt(tmp_path, "eval.json", invalid_eval_receipt),
            )

        receipt = validate_observability_promotion_receipt(payload)

        self.assertEqual(receipt.status, "blocked")
        self.assertEqual(receipt.promotion_ready_count, 0)
        all_candidate_blockers = [blocker for decision in receipt.candidate_decisions for blocker in decision.blockers]
        self.assertIn("eval_receipt_contract_invalid", all_candidate_blockers)
        all_check_evidence = [item for blocker in receipt.blockers for item in blocker.evidence]
        self.assertIn("eval_receipt_contract_invalid", all_check_evidence)

    def test_promotion_preview_rejects_schema_invalid_package_receipt(self) -> None:
        package_receipt = self._package_receipt()
        feedback_receipt = build_observability_feedback_receipt(
            REPO_ROOT,
            package_receipt=package_receipt,
            events_path=REDACTED_EVENTS,
        )
        invalid_package_receipt = {
            "schema_version": "skills-sdk.package-digest-receipt.v0",
            "status": "built",
            "package_id": package_receipt["package_id"],
            "package_digest": package_receipt["package_digest"],
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            payload = build_observability_promotion_receipt(
                REPO_ROOT,
                feedback_receipt_path=self._write_receipt(tmp_path, "feedback.json", feedback_receipt),
                package_receipt_path=self._write_receipt(tmp_path, "package.json", invalid_package_receipt),
                eval_run_receipt_path=self._write_receipt(tmp_path, "eval.json", self._passing_eval_receipt(package_receipt)),
            )

        receipt = validate_observability_promotion_receipt(payload)

        self.assertEqual(receipt.status, "blocked")
        self.assertEqual(receipt.promotion_ready_count, 0)
        all_candidate_blockers = [blocker for decision in receipt.candidate_decisions for blocker in decision.blockers]
        self.assertIn("package_receipt_contract_invalid", all_candidate_blockers)
        all_check_evidence = [item for blocker in receipt.blockers for item in blocker.evidence]
        self.assertIn("package_receipt_contract_invalid", all_check_evidence)

    def test_promotion_preview_accepts_required_receipts_in_any_order(self) -> None:
        package_receipt = self._package_receipt()
        feedback_receipt = build_observability_feedback_receipt(
            REPO_ROOT,
            package_receipt=package_receipt,
            events_path=REDACTED_EVENTS,
        )
        for candidate in feedback_receipt["scenario_candidates"] + feedback_receipt["skill_gap_candidates"]:
            candidate["required_receipts"] = ["eval_run_receipt", "package_digest_receipt"]
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            payload = build_observability_promotion_receipt(
                REPO_ROOT,
                feedback_receipt_path=self._write_receipt(tmp_path, "feedback.json", feedback_receipt),
                package_receipt_path=self._write_receipt(tmp_path, "package.json", package_receipt),
                eval_run_receipt_path=self._write_receipt(tmp_path, "eval.json", self._passing_eval_receipt(package_receipt)),
            )

        receipt = validate_observability_promotion_receipt(payload)

        self.assertEqual(receipt.status, "preview")
        self.assertEqual(receipt.promotion_ready_count, 2)
        self.assertTrue(all(decision.decision == "promotion_ready" for decision in receipt.candidate_decisions))

    def test_promotion_preview_surfaces_contract_blockers(self) -> None:
        package_receipt = self._package_receipt()
        feedback_receipt = build_observability_feedback_receipt(
            REPO_ROOT,
            package_receipt=package_receipt,
            events_path=REDACTED_EVENTS,
        )
        feedback_receipt["status"] = "blocked"
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            payload = build_observability_promotion_receipt(
                REPO_ROOT,
                feedback_receipt_path=self._write_receipt(tmp_path, "feedback.json", feedback_receipt),
                package_receipt_path=self._write_receipt(tmp_path, "package.json", package_receipt),
                eval_run_receipt_path=self._write_receipt(tmp_path, "eval.json", self._passing_eval_receipt(package_receipt)),
            )

        receipt = validate_observability_promotion_receipt(payload)

        self.assertEqual(receipt.status, "blocked")
        self.assertEqual(receipt.promotion_ready_count, 0)
        all_check_evidence = [item for blocker in receipt.blockers for item in blocker.evidence]
        self.assertIn("feedback_receipt_not_preview", all_check_evidence)

    def test_promotion_preview_preserves_non_check_blockers(self) -> None:
        package_receipt = self._package_receipt()
        feedback_receipt = build_observability_feedback_receipt(
            REPO_ROOT,
            package_receipt=package_receipt,
            events_path=REDACTED_EVENTS,
        )
        feedback_receipt["scenario_candidates"] = []
        feedback_receipt["skill_gap_candidates"] = []
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            payload = build_observability_promotion_receipt(
                REPO_ROOT,
                feedback_receipt_path=self._write_receipt(tmp_path, "feedback.json", feedback_receipt),
                package_receipt_path=self._write_receipt(tmp_path, "package.json", package_receipt),
                eval_run_receipt_path=self._write_receipt(tmp_path, "eval.json", self._passing_eval_receipt(package_receipt)),
            )

        receipt = validate_observability_promotion_receipt(payload)

        self.assertEqual(receipt.status, "blocked")
        self.assertEqual(receipt.candidate_count, 0)
        all_check_evidence = [item for blocker in receipt.blockers for item in blocker.evidence]
        self.assertIn("feedback_receipt_has_no_candidates", all_check_evidence)

    def test_public_cli_previews_observability_promotion(self) -> None:
        package_receipt = self._package_receipt()
        feedback_receipt = build_observability_feedback_receipt(
            REPO_ROOT,
            package_receipt=package_receipt,
            events_path=REDACTED_EVENTS,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            feedback_path = self._write_receipt(tmp_path, "feedback.json", feedback_receipt)
            package_path = self._write_receipt(tmp_path, "package.json", package_receipt)
            eval_path = self._write_receipt(tmp_path, "eval.json", self._passing_eval_receipt(package_receipt))
            completed = self._promotion_cli(
                feedback_path=feedback_path,
                package_path=package_path,
                eval_path=eval_path,
            )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        envelope = validate_robot_envelope(json.loads(completed.stdout))
        payload = envelope.data["skills_sdk_observability_promote"]
        receipt = validate_observability_promotion_receipt(payload["receipt"])
        self.assertEqual(receipt.status, "preview")
        self.assertEqual(receipt.promotion_ready_count, 2)


if __name__ == "__main__":
    unittest.main()
