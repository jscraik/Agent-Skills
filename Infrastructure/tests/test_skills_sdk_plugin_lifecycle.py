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

from ask.commands.skills_impl import (  # noqa: E402
    SkillsSdkPluginCreateRequest,
    SkillsSdkPluginReviewRequest,
    skills_sdk_plugin_install,
    skills_sdk_plugin_create,
    skills_sdk_plugin_save_registry,
)
from ask.commands.skills_impl_sdk_calibration import _sdk_plugin_review_command  # noqa: E402


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


def _write_skill(repo_root: Path) -> Path:
    skill_root = repo_root / "Skills" / "agent-ops" / "demo-skill"
    skill_root.mkdir(parents=True)
    (skill_root / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                "name: demo-skill",
                "description: Demo skill for SDK plugin lifecycle tests.",
                "---",
                "",
                "# Demo Skill",
                "",
                "Use this only in tests.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return skill_root


class TestSkillsSdkPluginLifecycle(unittest.TestCase):
    def test_sdk_plugin_help_exposes_lifecycle_actions(self) -> None:
        process = subprocess.run(
            ["./bin/ask", "sdk", "plugin", "--help"],
            cwd=REPO_ROOT,
            env=_command_env(),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=60,
        )

        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertIn("create", process.stdout)
        self.assertIn("review", process.stdout)
        self.assertIn("install", process.stdout)
        self.assertIn("save-registry", process.stdout)

    def test_create_preview_routes_single_skill_without_writing(self) -> None:
        result = skills_sdk_plugin_create(
            REPO_ROOT,
            SkillsSdkPluginCreateRequest(
                kind="skill", name="demo-skill", category="agent-ops", description="Demo skill",
                with_registry=True, companion_folders=[], apply=False,
            ),
        )

        payload = result.data["skills_sdk_plugin_create"]
        self.assertEqual(result.status, "success")
        self.assertEqual(payload["status"], "preview")
        self.assertEqual(payload["kind"], "skill")
        self.assertFalse(payload["mutation_performed"])
        self.assertEqual(payload["first_principles_gate"]["artifact_decision"], "IMPROVE_EXISTING")
        self.assertTrue(any("ask skills init" in command for command in payload["planned_commands"]))
        replay = payload["planned_commands"][-1]
        self.assertIn("--description", replay)
        self.assertIn("Demo skill", replay)
        self.assertIn("--with-registry", replay)

    def test_create_preview_routes_plugin_with_registry_without_writing(self) -> None:
        result = skills_sdk_plugin_create(
            REPO_ROOT,
            SkillsSdkPluginCreateRequest(
                kind="plugin", name="demo-plugin", category="third-party", description=None,
                with_registry=True, companion_folders=["references"], apply=False,
            ),
        )

        payload = result.data["skills_sdk_plugin_create"]
        self.assertEqual(result.status, "success")
        self.assertEqual(payload["status"], "preview")
        self.assertEqual(payload["kind"], "plugin")
        self.assertFalse(payload["mutation_performed"])
        self.assertTrue(any("ask plugins create" in command for command in payload["planned_commands"]))
        replay = payload["planned_commands"][-1]
        self.assertIn("--with-registry", replay)
        self.assertIn("--with-references", replay)

    def test_review_replay_retains_strict_mode(self) -> None:
        replay = _sdk_plugin_review_command(
            SkillsSdkPluginReviewRequest(
                kind="skill", target="Skills/agent-ops/demo-skill", strict=True, execute=True
            )
        )

        self.assertIn("--strict", replay)
        self.assertIn("--execute", replay)

    def test_save_registry_apply_writes_skill_registry(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_root = _write_skill(repo_root)

            result = skills_sdk_plugin_save_registry(
                repo_root,
                kind="skill",
                target=str(skill_root / "SKILL.md"),
                registry=".harness/skills/registry.json",
                apply=True,
            )

            payload = result.data["skills_sdk_plugin_save_registry"]
            registry = json.loads((repo_root / ".harness/skills/registry.json").read_text(encoding="utf-8"))
            self.assertEqual(result.status, "success")
            self.assertEqual(payload["status"], "applied")
            self.assertTrue(payload["mutation_performed"])
            self.assertEqual(registry["skills"][0]["handle"], "demo-skill")
            self.assertEqual(registry["skills"][0]["source"]["path"], "Skills/agent-ops/demo-skill/SKILL.md")

    def test_save_registry_apply_blocks_unresolved_skill_target_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)

            result = skills_sdk_plugin_save_registry(
                repo_root,
                kind="skill",
                target="typo",
                registry=".harness/skills/registry.json",
                apply=True,
            )

            payload = result.data["skills_sdk_plugin_save_registry"]
            self.assertEqual(result.status, "error")
            self.assertEqual(payload["status"], "blocked")
            self.assertFalse(payload["mutation_performed"])
            self.assertIsNone(payload["receipt"])
            self.assertFalse((repo_root / ".harness/skills/registry.json").exists())
            self.assertIn(
                "did not resolve to a canonical source",
                result.errors[0].message,
            )

    def test_save_registry_apply_writes_plugin_marketplace(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            plugin_root = repo_root / "Plugins" / "third-party" / "demo-plugin"
            (plugin_root / ".codex-plugin").mkdir(parents=True)
            (plugin_root / ".codex-plugin" / "plugin.json").write_text(
                '{"schema_version":1,"name":"demo-plugin","version":"0.1.0","skills":"./skills"}\n',
                encoding="utf-8",
            )

            result = skills_sdk_plugin_save_registry(
                repo_root,
                kind="plugin",
                target="Plugins/third-party/demo-plugin",
                registry="Plugins/marketplace.json",
                apply=True,
            )

            payload = result.data["skills_sdk_plugin_save_registry"]
            marketplace = json.loads((repo_root / "Plugins/marketplace.json").read_text(encoding="utf-8"))
            self.assertEqual(result.status, "success")
            self.assertEqual(payload["status"], "applied")
            self.assertFalse(payload["remote_publish_performed"])
            self.assertEqual(marketplace["plugins"][0]["name"], "demo-plugin")
            self.assertEqual(marketplace["plugins"][0]["source"]["path"], "./Plugins/third-party/demo-plugin")

    def test_save_registry_apply_blocks_missing_plugin_target_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)

            result = skills_sdk_plugin_save_registry(
                repo_root,
                kind="plugin",
                target="Plugins/third-party/typo",
                registry="Plugins/marketplace.json",
                apply=True,
            )

            payload = result.data["skills_sdk_plugin_save_registry"]
            self.assertEqual(result.status, "error")
            self.assertEqual(payload["status"], "blocked")
            self.assertFalse(payload["mutation_performed"])
            self.assertIsNone(payload["receipt"])
            self.assertFalse((repo_root / "Plugins/marketplace.json").exists())
            self.assertIn("does not exist", result.errors[0].message)

    def test_save_registry_apply_blocks_plugin_target_outside_repo(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir) / "repo"
            outside_root = Path(temp_dir) / "outside-plugin"
            repo_root.mkdir()
            outside_root.mkdir()

            result = skills_sdk_plugin_save_registry(
                repo_root,
                kind="plugin",
                target=str(outside_root),
                registry="Plugins/marketplace.json",
                apply=True,
            )

            payload = result.data["skills_sdk_plugin_save_registry"]
            self.assertEqual(result.status, "error")
            self.assertEqual(payload["status"], "blocked")
            self.assertFalse(payload["mutation_performed"])
            self.assertIn("must stay inside the repository", result.errors[0].message)

    def test_plugin_install_validation_command_records_full_plugin_inputs(self) -> None:
        result = skills_sdk_plugin_install(
            REPO_ROOT,
            kind="plugin",
            url="https://example.com/plugin.git",
            name="demo-plugin",
            ref="v1.2.3",
            dest="Plugins/vendor",
            validation_level="strict",
            allow_untrusted_source=True,
            allow_unpinned_ref=True,
            sync_profile=True,
            require_desktop_loadable=True,
            apply=False,
        )

        command = result.data["skills_sdk_plugin_install"]["validation_commands"][0]
        self.assertIn("--url https://example.com/plugin.git", command)
        self.assertIn("--name demo-plugin", command)
        self.assertIn("--ref v1.2.3", command)
        self.assertIn("--dest Plugins/vendor", command)
        self.assertIn("--validation-level strict", command)
        self.assertIn("--allow-untrusted-source", command)
        self.assertIn("--allow-unpinned-ref", command)
        self.assertIn("--sync-profile", command)
        self.assertIn("--require-desktop-loadable", command)

    def test_skill_install_validation_command_records_target_inputs(self) -> None:
        result = skills_sdk_plugin_install(
            REPO_ROOT,
            kind="skill",
            target="Skills/agent-ops/testing",
            project_root="/tmp/example-project",
            scope="user",
            apply=False,
        )

        command = result.data["skills_sdk_plugin_install"]["validation_commands"][0]
        self.assertIn("--target Skills/agent-ops/testing", command)
        self.assertIn("--project-root /tmp/example-project", command)
        self.assertIn("--scope user", command)
        self.assertIn("--preview", command)


if __name__ == "__main__":
    unittest.main()
