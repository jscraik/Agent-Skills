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
from ask.skills_sdk.package_build import build_package_digest_receipt  # noqa: E402
from ask.skills_sdk.typed_contracts import (  # noqa: E402
    validate_observability_feedback_receipt,
    validate_robot_envelope,
)
from pydantic import ValidationError  # noqa: E402


FIXTURE_SKILL = REPO_ROOT / "Infrastructure/tests/fixtures/skills_sdk/valid_skill"
REDACTED_EVENTS = "Infrastructure/tests/fixtures/skills_sdk/observability/redacted-events.fixture"
RAW_EVENTS = "Infrastructure/tests/fixtures/skills_sdk/observability/raw-events.fixture"


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


if __name__ == "__main__":
    unittest.main()
