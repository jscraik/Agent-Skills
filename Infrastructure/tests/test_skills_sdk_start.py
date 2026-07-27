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

from ask.commands.skills_impl import skills_sdk_start  # noqa: E402


def _command_env() -> dict[str, str]:
    env = os.environ.copy()
    temp_base = Path(tempfile.gettempdir()) / "agent-skills-test"
    env["XDG_CACHE_HOME"] = str(temp_base / "xdg-cache")
    env["XDG_STATE_HOME"] = str(temp_base / "xdg-state")
    env["MISE_CACHE_DIR"] = str(temp_base / "mise-cache")
    env["MISE_STATE_DIR"] = str(temp_base / "mise-state")
    env["UV_CACHE_DIR"] = str(temp_base / "uv-cache")
    env["MISE_TRUSTED_CONFIG_PATHS"] = str(REPO_ROOT / ".mise.toml")
    return env


def _run_json_command(*args: str) -> dict:
    process = subprocess.run(
        list(args),
        cwd=REPO_ROOT,
        env=_command_env(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=60,
    )
    if process.returncode != 0:
        raise AssertionError(
            f"{' '.join(args)} failed with {process.returncode}\nSTDOUT:\n{process.stdout}\nSTDERR:\n{process.stderr}"
        )
    return json.loads(process.stdout)


def _write_project_local_skill(project_root: Path) -> Path:
    skill_root = project_root / ".codex" / "skills" / "x-content-writer"
    skill_root.mkdir(parents=True)
    (project_root / "AGENTS.md").write_text("# X-writer Canary\n", encoding="utf-8")
    (project_root / "skills-sdk.json").write_text(
        json.dumps(
            {
                "schema_version": "skills-sdk.project.v1",
                "project_id": "x-writer-canary",
                "skill_roots": [
                    {
                        "path": ".codex/skills",
                        "classification": "canonical_project_source",
                        "default_for_update": True,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    skill_md = skill_root / "SKILL.md"
    skill_md.write_text(
        "---\n"
        "name: x-content-writer\n"
        "description: Project-local canary writer skill.\n"
        "---\n\n"
        "# X Content Writer\n\n"
        "Draft only from project-local evidence.\n",
        encoding="utf-8",
    )
    return skill_md


class TestSkillsSdkStart(unittest.TestCase):
    def test_start_returns_one_compact_local_next_action(self) -> None:
        payload = _run_json_command(
            sys.executable,
            "Infrastructure/bin/ask",
            "sdk",
            "start",
            "Skills/agent-ops/testing",
            "--json",
            "--robot",
        )
        receipt = payload["data"]["skills_sdk_start"]["receipt"]

        self.assertEqual(payload["status"], "success")
        self.assertEqual(receipt["schema_version"], "skills-sdk.pipeline-start.v1")
        self.assertEqual(receipt["target_class"], "global_skill")
        self.assertEqual(receipt["current_lane"], "local_check")
        self.assertEqual(receipt["next_action"]["command"], "./bin/ask sdk check Skills/agent-ops/testing --json --robot")
        self.assertEqual(receipt["blocked_downstream_lanes"], [])
        self.assertEqual(receipt["lanes"], [{"id": "local_check", "status": "required_not_run", "command": receipt["next_action"]["command"]}])
        self.assertNotIn("tessl", json.dumps(receipt).casefold())
        self.assertLess(len(json.dumps(payload)), 10_240)

    def test_start_classifies_manifest_declared_project_local_skill(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "x-writer"
            project_root.mkdir()
            skill_md = _write_project_local_skill(project_root)

            payload = _run_json_command(
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "start",
                str(skill_md),
                "--project-root",
                str(project_root),
                "--json",
                "--robot",
            )
            receipt = payload["data"]["skills_sdk_start"]["receipt"]

            self.assertEqual(payload["status"], "success")
            self.assertEqual(receipt["target_class"], "project_local_skill")
            self.assertIn(str(skill_md), receipt["source_path"])
            self.assertEqual(receipt["blocked_downstream_lanes"], [])
            self.assertIn("runtime reachability", receipt["what_this_does_not_prove"])

    def test_start_does_not_expose_future_lifecycle_detail(self) -> None:
        payload = _run_json_command(
            sys.executable,
            "Infrastructure/bin/ask",
            "sdk",
            "start",
            "Skills/agent-ops/testing",
            "--json",
            "--robot",
        )
        receipt = payload["data"]["skills_sdk_start"]["receipt"]
        self.assertEqual(len(receipt["lanes"]), 1)
        self.assertNotIn("score_policy", receipt)
        self.assertNotIn("provider", json.dumps(receipt).casefold())

    def test_start_blocks_runtime_projection_targets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp) / "repo"
            projection_skill = repo_root / ".agents" / "skills" / "demo-skill" / "SKILL.md"
            projection_skill.parent.mkdir(parents=True)
            projection_skill.write_text("---\nname: demo-skill\n---\n# Demo\n", encoding="utf-8")

            result = skills_sdk_start(repo_root, ".agents/skills/demo-skill/SKILL.md")

        payload = result.data["skills_sdk_start"]
        receipt = payload["receipt"]
        self.assertEqual(result.status, "error")
        self.assertEqual(receipt["status"], "blocked")
        self.assertEqual(receipt["target_class"], "runtime_projection")
        self.assertIn("runtime_projection_not_canonical_source", receipt["blockers"])


if __name__ == "__main__":
    unittest.main()
