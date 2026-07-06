from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk.local_score import (  # noqa: E402
    build_local_score_receipt_from_lane_payloads,
    write_local_score_receipts,
)
from ask.commands import sdk as sdk_commands  # noqa: E402


VALID_SKILL = REPO_ROOT / "Infrastructure/tests/fixtures/skills_sdk/valid_skill"


def _result(data: dict) -> SimpleNamespace:
    return SimpleNamespace(data=data)


def _quality_payload(status: str = "blocked") -> SimpleNamespace:
    return _result(
        {
            "skill_package_verification": {
                "status": status,
                "source_digest": "sha256:" + "a" * 64,
                "package_digest": "sha256:" + "b" * 64,
                "blockers": [{"rule_id": "example_blocker"}] if status == "blocked" else [],
                "agent_summary": f"Package verification {status}.",
            }
        }
    )


def _impact_payload(
    ready: int = 33,
    total: int = 71,
    blocked: int = 38,
    status: str | None = None,
    blockers: list[dict[str, str]] | None = None,
) -> SimpleNamespace:
    receipt_status = status if status is not None else ("blocked" if blocked else "preview")
    return _result(
        {
            "skills_sdk_eval_scenario_quality": {
                "receipt": {
                    "status": receipt_status,
                    "scenario_count": total,
                    "promotion_ready_count": ready,
                    "blocked_count": blocked,
                    "blockers": blockers or [],
                    "agent_summary": "Scenario quality emitted evidence.",
                }
            }
        }
    )


def _security_payload() -> SimpleNamespace:
    return _result(
        {
            "skills_sdk_risk_mode_taxonomy": {
                "receipt": {
                    "status": "pass",
                    "primary_mode": "malicious_supply_chain",
                    "detected_modes": [
                        "malicious_supply_chain",
                        "negligent_instruction",
                        "vulnerable_operation",
                    ],
                    "mode_results": [
                        {"mode": "malicious_supply_chain", "status": "detected", "severity": "critical"},
                        {"mode": "negligent_instruction", "status": "detected", "severity": "high"},
                        {"mode": "vulnerable_operation", "status": "detected", "severity": "high"},
                    ],
                    "agent_summary": "Risk-mode taxonomy emitted evidence.",
                }
            }
        }
    )


def _command_env() -> dict[str, str]:
    env = os.environ.copy()
    temp_base = Path(tempfile.gettempdir()) / "agent-skills-test"
    env.setdefault("XDG_CACHE_HOME", str(temp_base / "xdg-cache"))
    env.setdefault("XDG_STATE_HOME", str(temp_base / "xdg-state"))
    env.setdefault("MISE_CACHE_DIR", str(temp_base / "mise-cache"))
    env.setdefault("MISE_STATE_DIR", str(temp_base / "mise-state"))
    env.setdefault("UV_CACHE_DIR", str(temp_base / "uv-cache"))
    env.setdefault("MISE_TRUSTED_CONFIG_PATHS", str(REPO_ROOT / ".mise.toml"))
    return env


class TestSkillsSdkLocalScore(unittest.TestCase):
    def test_builder_scores_blocked_but_usable_lane_evidence(self) -> None:
        receipt = build_local_score_receipt_from_lane_payloads(
            REPO_ROOT,
            source_path=VALID_SKILL,
            query="Infrastructure/tests/fixtures/skills_sdk/valid_skill",
            gate="oss-local",
            quality_result=_quality_payload(status="pass"),
            impact_result=_impact_payload(),
            security_result=_security_payload(),
            generated_at="2026-07-04T12:00:00Z",
        )

        self.assertEqual(receipt["score"]["basis"], "Q100 I46 S35")
        self.assertEqual(receipt["score"]["value"], 60)
        self.assertEqual(receipt["score"]["status"], "partial")
        self.assertTrue(receipt["lanes"]["impact"]["evidence_usable"])
        self.assertEqual(receipt["lanes"]["impact"]["status"], "blocked")
        self.assertEqual(receipt["lanes"]["security"]["score"], 35)
        self.assertEqual(receipt["completeness"]["blocked_lanes"], ["impact", "security"])

    def test_builder_keeps_command_error_payload_usable_for_quality_lane(self) -> None:
        receipt = build_local_score_receipt_from_lane_payloads(
            REPO_ROOT,
            source_path=VALID_SKILL,
            query="Infrastructure/tests/fixtures/skills_sdk/valid_skill",
            gate="creation",
            quality_result=_quality_payload(status="blocked"),
            impact_result=_impact_payload(ready=1, total=1, blocked=0),
            security_result=_result({}),
            generated_at="2026-07-04T12:00:00Z",
        )

        self.assertEqual(receipt["lanes"]["quality"]["score"], 0)
        self.assertTrue(receipt["lanes"]["quality"]["evidence_usable"])
        self.assertEqual(receipt["lanes"]["security"]["status"], "missing")
        self.assertIn("security", receipt["completeness"]["missing_lanes"])
        self.assertEqual(receipt["score"]["status"], "partial")

    def test_builder_honors_suite_level_scenario_quality_blockers(self) -> None:
        receipt = build_local_score_receipt_from_lane_payloads(
            REPO_ROOT,
            source_path=VALID_SKILL,
            query="Infrastructure/tests/fixtures/skills_sdk/valid_skill",
            gate="oss-local",
            quality_result=_quality_payload(status="pass"),
            impact_result=_impact_payload(
                ready=3,
                total=3,
                blocked=0,
                status="blocked",
                blockers=[{"rule_id": "release_minimum_scenario_count"}],
            ),
            security_result=_result({}),
            generated_at="2026-07-04T12:00:00Z",
        )

        self.assertEqual(receipt["lanes"]["impact"]["status"], "blocked")
        self.assertEqual(receipt["lanes"]["impact"]["details"]["blocked_count"], 0)
        self.assertEqual(receipt["lanes"]["impact"]["details"]["suite_blocker_count"], 1)
        self.assertIn("impact", receipt["completeness"]["blocked_lanes"])

    def test_write_current_creates_skillsbar_feed_and_history_receipt(self) -> None:
        receipt = build_local_score_receipt_from_lane_payloads(
            REPO_ROOT,
            source_path=VALID_SKILL,
            query="Infrastructure/tests/fixtures/skills_sdk/valid_skill",
            gate="creation",
            quality_result=_quality_payload(status="pass"),
            impact_result=_impact_payload(ready=1, total=1, blocked=0),
            security_result=_result({}),
            generated_at="2026-07-04T12:00:00Z",
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            paths = write_local_score_receipts(Path(temp_dir), receipt)

            current = Path(temp_dir) / paths["current"]
            history = Path(temp_dir) / paths["history"]
            self.assertTrue(current.is_file())
            self.assertTrue(history.is_file())
            self.assertEqual(json.loads(current.read_text(encoding="utf-8"))["schema_version"], "skills-sdk.local-score.v1")

    def test_write_current_sanitizes_skill_name_path_segment(self) -> None:
        receipt = build_local_score_receipt_from_lane_payloads(
            REPO_ROOT,
            source_path=VALID_SKILL,
            query="Infrastructure/tests/fixtures/skills_sdk/valid_skill",
            gate="creation",
            quality_result=_quality_payload(status="pass"),
            impact_result=_impact_payload(ready=1, total=1, blocked=0),
            security_result=_result({}),
            generated_at="2026-07-04T12:00:00Z",
        )
        receipt["skill_name"] = "../../tmp/evil"

        with tempfile.TemporaryDirectory() as temp_dir:
            paths = write_local_score_receipts(Path(temp_dir), receipt)

            base = Path(temp_dir) / ".harness" / "evidence" / "skills-sdk" / "local-score"
            current = (Path(temp_dir) / paths["current"]).resolve()
            self.assertTrue(current.is_relative_to(base.resolve()))
            self.assertIn("tmp-evil", paths["current"])

    def test_command_emits_local_score_receipt_without_exit_code_scraping(self) -> None:
        process = subprocess.run(
            [
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "score",
                "local",
                "Infrastructure/tests/fixtures/skills_sdk/scenario_quality_skill",
                "--gate",
                "creation",
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

        self.assertEqual(process.returncode, 0, process.stderr)
        envelope = json.loads(process.stdout)
        payload = envelope["data"]["skills_sdk_local_score"]
        self.assertEqual(payload["receipt"]["schema_version"], "skills-sdk.local-score.v1")
        self.assertIn(payload["score"]["status"], {"complete", "partial"})
        self.assertIn("quality", payload["lanes"])
        self.assertIn("impact", payload["lanes"])
        self.assertIn("security", payload["lanes"])

    def test_dispatch_local_score_resolves_skill_handle_before_reading_source(self) -> None:
        args = SimpleNamespace(
            score_action="local",
            target="skills-sdk-valid-fixture",
            gate="creation",
            ttl_seconds=3600,
            write_current=False,
        )

        with (
            mock.patch.object(
                sdk_commands.skills_commands,
                "_resolve_doctor_target",
                return_value=(
                    {"source_path": "Infrastructure/tests/fixtures/skills_sdk/valid_skill"},
                    "Infrastructure/tests/fixtures/skills_sdk/valid_skill",
                ),
            ) as resolve_mock,
            mock.patch.object(sdk_commands.skills_commands, "skills_package_verify", return_value=_quality_payload(status="pass")),
            mock.patch.object(sdk_commands.skills_commands, "skills_sdk_eval_scenario_quality", return_value=_impact_payload()),
            mock.patch.object(sdk_commands.skills_commands, "skills_sdk_security_risk_modes_preview", return_value=_security_payload()),
        ):
            result = sdk_commands._dispatch_sdk_score(REPO_ROOT, args)

        self.assertEqual(result.status, "success")
        resolve_mock.assert_called_once_with(REPO_ROOT, "skills-sdk-valid-fixture")
        payload = result.data["skills_sdk_local_score"]
        self.assertEqual(payload["query"], "skills-sdk-valid-fixture")
        self.assertEqual(payload["receipt"]["skill_path"], "Infrastructure/tests/fixtures/skills_sdk/valid_skill")


if __name__ == "__main__":
    unittest.main()
