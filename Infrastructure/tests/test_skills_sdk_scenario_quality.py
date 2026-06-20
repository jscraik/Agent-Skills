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

from ask.skills_sdk.scenario_quality import (  # noqa: E402
    ScenarioQualityError,
    build_scenario_quality_receipt,
)


FIXTURE_SKILL = "Infrastructure/tests/fixtures/skills_sdk/scenario_quality_skill"
INVALID_SKILL = "Infrastructure/tests/fixtures/skills_sdk/valid_skill"


def _command_env() -> dict[str, str]:
    env = os.environ.copy()
    temp_base = Path(tempfile.gettempdir()) / "agent-skills-test"
    env.setdefault("XDG_CACHE_HOME", str(temp_base / "xdg-cache"))
    env.setdefault("XDG_STATE_HOME", str(temp_base / "xdg-state"))
    env.setdefault("MISE_CACHE_DIR", str(temp_base / "mise-cache"))
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


class TestSkillsSdkScenarioQuality(unittest.TestCase):
    def test_scenario_quality_command_builds_preview(self) -> None:
        process = _run_ask("sdk", "eval", "scenario-quality", FIXTURE_SKILL, "--preview", "--json", "--robot")

        self.assertEqual(process.returncode, 0, process.stderr)
        envelope = json.loads(process.stdout)
        payload = envelope["data"]["skills_sdk_eval_scenario_quality"]
        receipt = payload["receipt"]

        self.assertEqual(payload["status"], "preview")
        self.assertEqual(receipt["scenario_count"], 1)
        self.assertEqual(receipt["promotion_ready_count"], 1)
        self.assertFalse(receipt["mutation_performed"])
        self.assertFalse(receipt["promotion_performed"])

    def test_scenario_quality_requires_preview_flag(self) -> None:
        process = _run_ask("sdk", "eval", "scenario-quality", FIXTURE_SKILL, "--json", "--robot")

        self.assertNotEqual(process.returncode, 0)
        envelope = json.loads(process.stdout)
        self.assertEqual(envelope["status"], "error")
        self.assertIn("requires --preview", envelope["errors"][0]["message"])

    def test_builder_blocks_missing_evals_yaml(self) -> None:
        with self.assertRaises(ScenarioQualityError) as raised:
            build_scenario_quality_receipt(
                REPO_ROOT,
                source_path=REPO_ROOT / INVALID_SKILL / "SKILL.md",
                query=INVALID_SKILL,
            )

        receipt = raised.exception.receipt
        self.assertEqual(receipt["status"], "blocked")
        self.assertEqual(receipt["scenario_count"], 0)
        self.assertTrue(any(check["id"] == "evals_yaml_present" for check in receipt["blockers"]))


if __name__ == "__main__":
    unittest.main()
