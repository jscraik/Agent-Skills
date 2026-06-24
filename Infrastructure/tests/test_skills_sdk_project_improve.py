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
    env.setdefault("XDG_CACHE_HOME", str(temp_base / "xdg-cache"))
    env.setdefault("XDG_STATE_HOME", str(temp_base / "xdg-state"))
    env.setdefault("MISE_CACHE_DIR", str(temp_base / "mise-cache"))
    env.setdefault("MISE_STATE_DIR", str(temp_base / "mise-state"))
    env.setdefault("UV_CACHE_DIR", str(temp_base / "uv-cache"))
    env.setdefault("MISE_TRUSTED_CONFIG_PATHS", str(REPO_ROOT / ".mise.toml"))
    env.setdefault("ASK_SKILLS_SDK_IMPROVE_TIMESTAMP", "2026-06-24T00:00:00Z")
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
    )
    if process.returncode != 0:
        raise AssertionError(
            f"{' '.join(args)} failed with {process.returncode}\nSTDOUT:\n{process.stdout}\nSTDERR:\n{process.stderr}"
        )
    return json.loads(process.stdout)


def _project_manifest() -> dict:
    return {
        "schema_version": "skills-sdk.project.v1",
        "project": {"id": "x-writer-canary", "name": "X-writer Canary"},
        "skill_sources": [
            {
                "root": ".codex/skills",
                "kind": "canonical_project_source",
                "standard": "agent-skills",
                "client": "codex",
                "write_policy": "sdk_managed",
            }
        ],
        "evidence": {
            "registry": ".harness/skills/registry.json",
            "events": ".harness/skills/events.jsonl",
            "receipts": ".harness/skills/receipts",
        },
    }


def _write_codex_skill(skill_root: Path) -> None:
    (skill_root / "README.md").write_text("# X Content Writer\n", encoding="utf-8")
    (skill_root / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                "name: x-content-writer",
                "description: Project-local canary writer skill.",
                "---",
                "",
                "# X Content Writer",
                "",
                "Draft only from project-local evidence and leave final publishing to the operator.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def _project_with_codex_skill(tmp_path: Path) -> tuple[Path, Path]:
    project_root = tmp_path / "x-writer-canary"
    skill_root = project_root / ".codex" / "skills" / "x-content-writer"
    skill_root.mkdir(parents=True)
    (project_root / "AGENTS.md").write_text("# X-writer Canary\n", encoding="utf-8")
    (project_root / "skills-sdk.json").write_text(
        json.dumps(_project_manifest()),
        encoding="utf-8",
    )
    _write_codex_skill(skill_root)
    return project_root, skill_root / "SKILL.md"


class TestSkillsSdkProjectImprove(unittest.TestCase):
    def test_preview_does_not_write_owner_repo_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root, skill_md = _project_with_codex_skill(Path(tmp))

            payload = _run_json_command(
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "improve",
                str(skill_md),
                "--project-root",
                str(project_root),
                "--preview",
                "--json",
                "--robot",
            )
            receipt = payload["data"]["skills_sdk_project_improve"]["receipt"]

            self.assertEqual(payload["status"], "success")
            self.assertEqual(receipt["status"], "pass")
            self.assertFalse(receipt["mutation_performed"])
            self.assertFalse(receipt["source_mutation_performed"])
            self.assertEqual(receipt["source_edit"]["status"], "not_requested")
            self.assertFalse((project_root / ".harness/skills/registry.json").exists())
            self.assertFalse((project_root / ".harness/skills/events.jsonl").exists())

    def test_apply_writes_registry_event_and_receipt_without_source_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root, skill_md = _project_with_codex_skill(Path(tmp))
            before_source = skill_md.read_text(encoding="utf-8")

            payload = _run_json_command(
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "improve",
                str(skill_md),
                "--project-root",
                str(project_root),
                "--apply",
                "--json",
                "--robot",
            )
            improve_payload = payload["data"]["skills_sdk_project_improve"]
            receipt = improve_payload["receipt"]
            registry_path = project_root / ".harness/skills/registry.json"
            events_path = project_root / ".harness/skills/events.jsonl"
            receipt_path = project_root / receipt["receipt_path"]
            registry = json.loads(registry_path.read_text(encoding="utf-8"))
            events = [json.loads(line) for line in events_path.read_text(encoding="utf-8").splitlines()]

            self.assertEqual(payload["status"], "success")
            self.assertEqual(receipt["status"], "pass")
            self.assertTrue(receipt["mutation_performed"])
            self.assertFalse(receipt["source_mutation_performed"])
            self.assertEqual(skill_md.read_text(encoding="utf-8"), before_source)
            self.assertTrue(receipt_path.is_file())
            self.assertEqual(registry["summary"]["last_improvement_receipt"], receipt["receipt_path"])
            self.assertEqual(registry["skills"][0]["handle"], "x-content-writer")
            self.assertEqual(registry["skills"][0]["evidence"]["last_improvement_receipt"], receipt["receipt_path"])
            self.assertEqual(events[-1]["event"], "project_skill_improvement_validated")
            self.assertEqual(events[-1]["source_edit_status"], "not_requested")
            self.assertFalse(improve_payload["source_mutation_performed"])


if __name__ == "__main__":
    unittest.main()
