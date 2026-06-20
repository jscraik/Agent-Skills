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

from ask.skills_sdk.ci_policy_preview import build_ci_policy_preview_receipt  # noqa: E402


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


class TestSkillsSdkCiPolicyPreview(unittest.TestCase):
    def test_ci_policy_command_builds_preview_from_high_risk_tier(self) -> None:
        process = _run_ask(
            "sdk",
            "ci",
            "policy",
            "--risk-tier",
            "high",
            "--preview",
            "--json",
            "--robot",
        )

        self.assertEqual(process.returncode, 0, process.stderr)
        envelope = json.loads(process.stdout)
        payload = envelope["data"]["skills_sdk_ci_policy_preview"]
        receipt = payload["receipt"]
        required_names = {check["name"] for check in receipt["required_checks"]}

        self.assertEqual(payload["status"], "preview")
        self.assertIn("risk-policy-gate", required_names)
        self.assertIn("Semgrep (SAST)", required_names)
        self.assertIn("Trivy (dependency CVE scan)", required_names)
        self.assertFalse(receipt["live_ci_evidence_attached"])
        self.assertFalse(receipt["branch_protection_mutated"])
        self.assertFalse(receipt["mutation_performed"])

    def test_ci_policy_requires_preview_flag(self) -> None:
        process = _run_ask(
            "sdk",
            "ci",
            "policy",
            "--risk-tier",
            "high",
            "--json",
            "--robot",
        )

        self.assertNotEqual(process.returncode, 0)
        envelope = json.loads(process.stdout)
        self.assertEqual(envelope["status"], "error")
        self.assertIn("requires --preview", envelope["errors"][0]["message"])

    def test_builder_blocks_unknown_risk_tier(self) -> None:
        with self.assertRaisesRegex(ValueError, "blocked"):
            build_ci_policy_preview_receipt(risk_tier="surprise")


if __name__ == "__main__":
    unittest.main()
