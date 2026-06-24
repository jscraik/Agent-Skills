from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


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
    def test_start_routes_global_skill_to_mechanical_validation(self) -> None:
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
        self.assertEqual(receipt["current_lane"], "mechanical_validation")
        self.assertEqual(receipt["next_action"]["lane"], "mechanical_validation")
        self.assertIn("skills audit Skills/agent-ops/testing --level strict", receipt["next_action"]["command"])
        self.assertIn("scenario_quality", receipt["blocked_downstream_lanes"])
        mechanical_lane = next(lane for lane in receipt["lanes"] if lane["id"] == "mechanical_validation")
        self.assertIn("skills package verify Skills/agent-ops/testing", mechanical_lane["commands"][1])

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
            self.assertEqual(receipt["project_context"]["project_root"], str(project_root))
            self.assertEqual(receipt["project_context"]["project_source_root"], ".codex/skills")
            self.assertIn(str(skill_md.parent), receipt["next_action"]["command"])
            self.assertIn("oss_cloud_eval", receipt["blocked_downstream_lanes"])
            self.assertIn("Format, layout, references", receipt["what_this_does_not_prove"])


if __name__ == "__main__":
    unittest.main()
