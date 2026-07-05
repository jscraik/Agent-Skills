from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "tests"))
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from helpers.schema_validator import _validate_schema_subset  # noqa: E402
from ask.skills_sdk.security_lane import build_security_lane_receipt  # noqa: E402


SCHEMA_PATH = REPO_ROOT / "Infrastructure/config/schemas/skills-sdk/security-lane-receipt.v0.schema.json"


def _schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


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


def _run_ask(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "Infrastructure/bin/ask", *args],
        cwd=REPO_ROOT,
        env=_command_env(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


class TestSkillsSdkSecurityLane(unittest.TestCase):
    def assert_schema_valid(self, payload: dict) -> None:
        _validate_schema_subset(_schema(), payload, {"security-lane-receipt": _schema()})

    def test_builder_records_deterministic_security_commands(self) -> None:
        source_path = REPO_ROOT / "Infrastructure/tests/fixtures/skills_sdk/valid_skill/SKILL.md"

        receipt = build_security_lane_receipt(
            REPO_ROOT,
            source_path=source_path,
            query="Infrastructure/tests/fixtures/skills_sdk/valid_skill",
            profile="oss-security",
        )

        self.assert_schema_valid(receipt)
        self.assertEqual(receipt["status"], "pass")
        self.assertEqual(receipt["package_id"], "skills-sdk-valid-fixture")
        self.assertEqual(len(receipt["commands"]), 2)
        command_names = [record["command"] for record in receipt["commands"]]
        self.assertIn("package-signature", command_names[0])
        self.assertIn("risk-modes", command_names[1])
        self.assertEqual(receipt["profile_review"]["profile"], "oss-security")
        self.assertEqual(receipt["profile_review"]["status"], "not_run")
        self.assertFalse(receipt["execution_performed"])
        self.assertFalse(receipt["scanner_execution_performed"])
        self.assertFalse(receipt["network_accessed"])
        self.assertFalse(receipt["credentials_accessed"])
        self.assertFalse(receipt["mutation_performed"])

    def test_builder_blocks_when_profile_review_is_required_without_receipt(self) -> None:
        source_path = REPO_ROOT / "Infrastructure/tests/fixtures/skills_sdk/valid_skill/SKILL.md"

        receipt = build_security_lane_receipt(
            REPO_ROOT,
            source_path=source_path,
            query="Infrastructure/tests/fixtures/skills_sdk/valid_skill",
            profile="oss-security",
            require_review=True,
        )

        self.assert_schema_valid(receipt)
        self.assertEqual(receipt["status"], "blocked")
        self.assertEqual(receipt["profile_review"]["status"], "blocked")
        self.assertTrue(receipt["profile_review"]["required"])

    def test_command_emits_preview_receipt_for_fixture_skill(self) -> None:
        process = _run_ask(
            "sdk",
            "security",
            "run-lane",
            "Infrastructure/tests/fixtures/skills_sdk/valid_skill",
            "--preview",
            "--profile",
            "oss-security",
            "--json",
            "--robot",
        )

        self.assertEqual(process.returncode, 0, process.stderr)
        envelope = json.loads(process.stdout)
        payload = envelope["data"]["skills_sdk_security_lane"]
        receipt = payload["receipt"]

        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["package_id"], "skills-sdk-valid-fixture")
        self.assertEqual(payload["profile_review"]["status"], "not_run")
        self.assert_schema_valid(receipt)

    def test_command_requires_preview_flag(self) -> None:
        process = _run_ask(
            "sdk",
            "security",
            "run-lane",
            "Infrastructure/tests/fixtures/skills_sdk/valid_skill",
            "--json",
            "--robot",
        )

        self.assertNotEqual(process.returncode, 0)
        envelope = json.loads(process.stdout)
        self.assertEqual(envelope["status"], "error")
        self.assertIn("requires --preview", envelope["errors"][0]["message"])

    def test_command_blocks_when_required_profile_review_is_missing(self) -> None:
        process = _run_ask(
            "sdk",
            "security",
            "run-lane",
            "Infrastructure/tests/fixtures/skills_sdk/valid_skill",
            "--preview",
            "--profile",
            "oss-security",
            "--require-review",
            "--json",
            "--robot",
        )

        self.assertNotEqual(process.returncode, 0)
        envelope = json.loads(process.stdout)
        payload = envelope["data"]["skills_sdk_security_lane"]
        self.assertEqual(payload["status"], "blocked")
        self.assertEqual(payload["profile_review"]["status"], "blocked")
        self.assertIn("profile review status is blocked", payload["agent_summary"])


if __name__ == "__main__":
    unittest.main()
