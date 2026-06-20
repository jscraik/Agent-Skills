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

from ask.skills_sdk.static_explorer import build_static_explorer_receipt  # noqa: E402


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


class TestSkillsSdkStaticExplorer(unittest.TestCase):
    def test_static_explorer_command_builds_json_only_preview(self) -> None:
        process = _run_ask("sdk", "explorer", "static", "--preview", "--json", "--robot")

        self.assertEqual(process.returncode, 0, process.stderr)
        envelope = json.loads(process.stdout)
        payload = envelope["data"]["skills_sdk_static_explorer_preview"]
        receipt = payload["receipt"]

        self.assertEqual(payload["status"], "preview")
        self.assertGreater(receipt["capability_count"], 0)
        self.assertGreater(receipt["skill_count"], 0)
        self.assertIn("Infrastructure/config/skills-sdk/capability-matrix.v1.json", receipt["projection_inputs"])
        self.assertIn(".skillsets/*/manifest.jsonl", receipt["projection_inputs"])
        self.assertFalse(receipt["html_rendered"])
        self.assertFalse(receipt["hosted_publish_requested"])
        self.assertFalse(receipt["mutation_performed"])

    def test_static_explorer_requires_preview_flag(self) -> None:
        process = _run_ask("sdk", "explorer", "static", "--json", "--robot")

        self.assertNotEqual(process.returncode, 0)
        envelope = json.loads(process.stdout)
        self.assertEqual(envelope["status"], "error")
        self.assertIn("requires --preview", envelope["errors"][0]["message"])

    def test_static_explorer_builder_indexes_rooted_skill_manifests(self) -> None:
        receipt = build_static_explorer_receipt(REPO_ROOT)
        skill_ids = {row["id"] for row in receipt["skill_index"]}

        self.assertIn("testing", skill_ids)
        self.assertEqual(receipt["status"], "preview")
        self.assertFalse(receipt["html_rendered"])


if __name__ == "__main__":
    unittest.main()
