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

from ask.commands.skills_impl import _sdk_improve_update_registry  # noqa: E402


def _command_env() -> dict[str, str]:
    env = os.environ.copy()
    temp_base = Path(tempfile.gettempdir()) / "agent-skills-test"
    env["XDG_CACHE_HOME"] = str(temp_base / "xdg-cache")
    env["XDG_STATE_HOME"] = str(temp_base / "xdg-state")
    env["MISE_CACHE_DIR"] = str(temp_base / "mise-cache")
    env["MISE_STATE_DIR"] = str(temp_base / "mise-state")
    env["UV_CACHE_DIR"] = str(temp_base / "uv-cache")
    env["MISE_TRUSTED_CONFIG_PATHS"] = str(REPO_ROOT / ".mise.toml")
    env["ASK_SKILLS_SDK_IMPROVE_TIMESTAMP"] = "2026-06-24T00:00:00Z"
    return env


def _run_json_command(*args: str) -> dict:
    process = _run_command(*args)
    if process.returncode != 0:
        raise AssertionError(
            f"{' '.join(args)} failed with {process.returncode}\nSTDOUT:\n{process.stdout}\nSTDERR:\n{process.stderr}"
        )
    return json.loads(process.stdout)


def _run_command(*args: str) -> subprocess.CompletedProcess[str]:
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
    return process


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


def _seed_registry_with_sensitive_summary(registry_path: Path) -> None:
    registry_path.parent.mkdir(parents=True)
    registry_path.write_text(
        json.dumps(
            {
                "schema_version": "skills-sdk.project-skill-registry.v1",
                "project": {"id": "x-writer-canary", "manifest": "skills-sdk.json"},
                "summary": {
                    "api_token": "do-not-store",
                    "nested": {"credential": "do-not-store-either"},
                },
                "skills": [],
            }
        ),
        encoding="utf-8",
    )


def _assert_apply_receipt_evidence(
    test_case: unittest.TestCase,
    *,
    payload: dict,
    project_root: Path,
    skill_md: Path,
    before_source: str,
    registry_path: Path,
) -> None:
    improve_payload = payload["data"]["skills_sdk_project_improve"]
    receipt = improve_payload["receipt"]
    events_path = project_root / ".harness/skills/events.jsonl"
    receipt_path = project_root / receipt["receipt_path"]
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    events = [json.loads(line) for line in events_path.read_text(encoding="utf-8").splitlines()]

    test_case.assertEqual(payload["status"], "success")
    test_case.assertEqual(receipt["status"], "pass")
    test_case.assertTrue(receipt["mutation_performed"])
    test_case.assertFalse(receipt["source_mutation_performed"])
    test_case.assertEqual(skill_md.read_text(encoding="utf-8"), before_source)
    test_case.assertTrue(receipt_path.is_file())
    test_case.assertEqual(registry["summary"]["last_improvement_receipt"], receipt["receipt_path"])
    test_case.assertEqual(registry["summary"]["api_token"], "[redacted]")
    test_case.assertEqual(registry["summary"]["nested"]["credential"], "[redacted]")
    test_case.assertEqual(registry["skills"][0]["handle"], "x-content-writer")
    test_case.assertEqual(registry["skills"][0]["evidence"]["last_improvement_receipt"], receipt["receipt_path"])
    test_case.assertEqual(events[-1]["event"], "project_skill_improvement_validated")
    test_case.assertEqual(events[-1]["source_edit_status"], "not_requested")
    test_case.assertFalse(improve_payload["source_mutation_performed"])


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
            registry_path = project_root / ".harness/skills/registry.json"
            _seed_registry_with_sensitive_summary(registry_path)

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
            _assert_apply_receipt_evidence(
                self,
                payload=payload,
                project_root=project_root,
                skill_md=skill_md,
                before_source=before_source,
                registry_path=registry_path,
            )

    def test_preview_blocks_project_evidence_paths_outside_project_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root, skill_md = _project_with_codex_skill(Path(tmp))
            manifest = _project_manifest()
            manifest["evidence"]["registry"] = "../outside-registry.json"
            (project_root / "skills-sdk.json").write_text(json.dumps(manifest), encoding="utf-8")

            process = _run_command(
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
            payload = json.loads(process.stdout)
            receipt = payload["data"]["skills_sdk_project_improve"]["receipt"]

            self.assertNotEqual(process.returncode, 0)
            self.assertEqual(payload["status"], "error")
            self.assertEqual(receipt["status"], "blocked")
            self.assertEqual(receipt["blockers"], ["invalid_project_evidence_paths"])
            self.assertFalse((project_root.parent / "outside-registry.json").exists())

    def test_apply_blocks_malformed_existing_registry_without_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root, skill_md = _project_with_codex_skill(Path(tmp))
            registry_path = project_root / ".harness" / "skills" / "registry.json"
            registry_path.parent.mkdir(parents=True)
            registry_path.write_text("{not-json", encoding="utf-8")

            process = _run_command(
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
            payload = json.loads(process.stdout)
            receipt = payload["data"]["skills_sdk_project_improve"]["receipt"]

            self.assertNotEqual(process.returncode, 0)
            self.assertEqual(payload["status"], "error")
            self.assertEqual(receipt["status"], "blocked")
            self.assertIn("invalid_project_registry", receipt["blockers"])
            self.assertEqual(registry_path.read_text(encoding="utf-8"), "{not-json")

    def test_registry_marks_eval_blocked_improvement_as_blocked(self) -> None:
        registry: dict = {"skills": []}

        _sdk_improve_update_registry(
            registry,
            project_id="x-writer-canary",
            handle="x-content-writer",
            source_path=".codex/skills/x-content-writer/SKILL.md",
            source_root=".codex/skills",
            hardening_receipt={"status": "pass", "package_digest": "sha256:" + "a" * 64, "file_count": 2},
            eval_receipt={"status": "blocked", "runner": "internal", "case_count": 1, "passed_count": 0, "failed_count": 1},
            improvement_status="blocked",
            receipt_path=".harness/skills/receipts/improvements/x-content-writer.json",
            timestamp="2026-06-24T00:00:00Z",
            source_edit_status="not_requested",
        )

        entry = registry["skills"][0]
        self.assertEqual(entry["lifecycle"]["state"], "blocked")
        self.assertEqual(entry["lifecycle"]["decision"], "improve_blocked")
        self.assertEqual(entry["package"]["hardening_status"], "pass")
        self.assertEqual(entry["evals"]["status"], "blocked")


if __name__ == "__main__":
    unittest.main()
