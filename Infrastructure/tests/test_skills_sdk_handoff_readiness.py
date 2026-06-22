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

from ask.skills_sdk.handoff_readiness import build_handoff_readiness_receipt  # noqa: E402
from ask.skills_sdk.handoff_readiness_contracts import validate_handoff_readiness_receipt  # noqa: E402


FIXTURE_SKILL = "Infrastructure/tests/fixtures/skills_sdk/scenario_quality_skill"
REQUIRED_LANES = ("deterministic_local_gates", "oss-local", "oss-cloud", "tessl-live-dry-run")


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


def _write_readiness_bundle(temp_dir: Path, *, status: str = "pass") -> Path:
    lanes = []
    for lane_id in REQUIRED_LANES:
        receipt_path = temp_dir / f"{lane_id}.json"
        receipt_path.write_text(json.dumps({"lane": lane_id}) + "\n", encoding="utf-8")
        lanes.append({
            "id": lane_id,
            "status": status,
            "command": f"./bin/ask proof {lane_id}",
            "receipt_path": str(receipt_path),
        })
    readiness_path = temp_dir / "eval-handoff-readiness.json"
    readiness_path.write_text(
        json.dumps({
            "schema_version": "skills-sdk.eval-handoff-readiness-input.v1",
            "candidate_id": "fixture-candidate",
            "lanes": lanes,
        }),
        encoding="utf-8",
    )
    return readiness_path


class TestSkillsSdkHandoffReadiness(unittest.TestCase):
    def test_missing_readiness_artifact_blocks_live_gate(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            receipt = build_handoff_readiness_receipt(
                REPO_ROOT,
                source_path=REPO_ROOT / FIXTURE_SKILL,
                query=FIXTURE_SKILL,
                readiness_path=Path(temp_dir) / "missing.json",
            )

        self.assertEqual(receipt["status"], "blocked")
        self.assertFalse(receipt["ready_for_live_tessl"])
        blocker_ids = {blocker["id"] for blocker in receipt["blockers"]}
        self.assertIn("readiness_artifact_present", blocker_ids)
        self.assertIn("lane_present", blocker_ids)

    def test_complete_readiness_artifact_allows_live_gate(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            readiness_path = _write_readiness_bundle(Path(temp_dir))
            receipt = build_handoff_readiness_receipt(
                REPO_ROOT,
                source_path=REPO_ROOT / FIXTURE_SKILL,
                query=FIXTURE_SKILL,
                readiness_path=readiness_path,
            )

        self.assertEqual(receipt["status"], "preview")
        self.assertTrue(receipt["ready_for_live_tessl"])
        self.assertEqual(receipt["blockers"], [])
        validate_handoff_readiness_receipt(receipt)

    def test_handoff_readiness_command_requires_preview(self) -> None:
        process = _run_ask(
            "sdk",
            "eval",
            "handoff-readiness",
            "--skill",
            FIXTURE_SKILL,
            "--json",
            "--robot",
        )

        self.assertNotEqual(process.returncode, 0)
        envelope = json.loads(process.stdout)
        self.assertEqual(envelope["status"], "error")
        self.assertIn("require --preview", envelope["errors"][0]["message"])

    def test_handoff_readiness_command_builds_preview(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            readiness_path = _write_readiness_bundle(Path(temp_dir))
            process = _run_ask(
                "sdk",
                "eval",
                "handoff-readiness",
                "--skill",
                FIXTURE_SKILL,
                "--receipt-json",
                str(readiness_path),
                "--preview",
                "--json",
                "--robot",
            )

        self.assertEqual(process.returncode, 0, process.stderr)
        envelope = json.loads(process.stdout)
        payload = envelope["data"]["skills_sdk_eval_handoff_readiness"]
        self.assertEqual(payload["status"], "preview")
        self.assertTrue(payload["ready_for_live_tessl"])


if __name__ == "__main__":
    unittest.main()
