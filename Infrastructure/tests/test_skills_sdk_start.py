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
        lane_ids = [lane["id"] for lane in receipt["lanes"]]
        self.assertIn("security_risk_modes", lane_ids)
        self.assertIn("scorer_quality", lane_ids)
        self.assertIn("scorer_calibration", lane_ids)
        self.assertIn("tessl_local_proof_execute", lane_ids)
        self.assertIn("tessl_live_dry_run", lane_ids)
        self.assertIn("handoff_readiness", lane_ids)
        self.assertIn("tessl_live_confirmation", lane_ids)
        self.assertIn("registry_or_private_workspace_decision", lane_ids)
        self.assertEqual(receipt["score_policy"]["oss_local_target"], "70-75 success rate after mechanical checks, gold scenarios, and initial rubric hardening")
        self.assertIn(">=90 internal success rate", receipt["score_policy"]["oss_cloud_target"])
        self.assertIn("external confirmation only", receipt["score_policy"]["tessl_live_target"])

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
            self.assertIn("security posture", receipt["what_this_does_not_prove"])
            self.assertIn("skills-sdk-lab", receipt["score_policy"]["workspace_policy"])

    def test_start_records_single_pipeline_for_all_lifecycle_entrypoints(self) -> None:
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
        lanes = {lane["id"]: lane for lane in receipt["lanes"]}

        self.assertIn("create, update, install, refactor, skillify, and skill-builder", receipt["what_this_proves"])
        self.assertEqual(lanes["oss_local_repair_loop"]["target_success_rate"], "70-75 internal success after mechanical and scenario gates")
        self.assertEqual(lanes["oss_cloud_repair_loop"]["target_success_rate"], ">=90 internal success before Tessl spend")
        self.assertEqual(lanes["tessl_live_confirmation"]["target_success_rate"], ">=90 and >= baseline; Tessl is confirmational, not the discovery loop")
        self.assertIn("--workspace skills-sdk-lab", lanes["tessl_local_proof_execute"]["command"])
        self.assertIn("--tessl-live-dry-run", lanes["tessl_live_dry_run"]["command"])
        self.assertIn("private workspace retention or public registry publication", lanes["registry_or_private_workspace_decision"]["command"])

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
