import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from ask.commands.plugins import doctor_plugins_state, list_plugins_state, status_plugin_state  # noqa: E402


class TestAskPluginsState(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="ask-plugins-state-"))
        self.repo_root = self.temp_dir / "repo"
        self.repo_root.mkdir(parents=True)
        self.fake_home = self.temp_dir / "home"
        self.fake_home.mkdir(parents=True)
        self.home_patcher = patch("ask.plugin_state.Path.home", return_value=self.fake_home)
        self.home_patcher.start()

        plugin_manifest = self.repo_root / "plugins" / "example-plugin" / ".codex-plugin" / "plugin.json"
        plugin_manifest.parent.mkdir(parents=True, exist_ok=True)
        (self.repo_root / "plugins" / "example-plugin" / "README.md").write_text(
            "# Example Plugin\n\nTest fixture plugin.\n",
            encoding="utf-8",
        )
        assets_dir = self.repo_root / "plugins" / "example-plugin" / "assets"
        assets_dir.mkdir(parents=True, exist_ok=True)
        (assets_dir / "icon.png").write_bytes(b"fixture-icon")
        (assets_dir / "logo.png").write_bytes(b"fixture-logo")
        skill = self.repo_root / "plugins" / "example-plugin" / "skills" / "example-skill" / "SKILL.md"
        skill.parent.mkdir(parents=True, exist_ok=True)
        skill.write_text(
            "---\nname: example-skill\ndescription: Example skill.\n---\n# Example Skill\n",
            encoding="utf-8",
        )
        plugin_manifest.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "name": "example-plugin",
                    "version": "0.1.0",
                    "description": "Example plugin",
                    "skills": "./skills/",
                    "governance": {"owner": "Agent Skills Team"},
                    "interface": {
                        "displayName": "Example Plugin",
                        "shortDescription": "Example short description",
                        "longDescription": "Example long description",
                        "developerName": "Agent Skills Team",
                        "category": "Productivity",
                        "capabilities": ["Interactive", "Read"],
                        "websiteURL": "https://example.com",
                        "defaultPrompt": "Help with example workflows.",
                        "composerIcon": "./assets/icon.png",
                        "logo": "./assets/logo.png",
                    },
                }
            )
            + "\n",
            encoding="utf-8",
        )

        marketplace = self.repo_root / ".agents" / "plugins" / "marketplace.json"
        marketplace.parent.mkdir(parents=True, exist_ok=True)
        marketplace.write_text(
            json.dumps(
                {
                    "name": "agent-skills-local",
                    "plugins": [
                        {
                            "name": "example-plugin",
                            "source": {"source": "local", "path": "./Plugins/example-plugin"},
                        }
                    ],
                }
            )
            + "\n",
            encoding="utf-8",
        )
        self._write_runtime_cache_plugin()

    def _write_profile_plugin(
        self,
        *,
        enabled: bool = True,
        stale_enabled: bool = False,
        source_path: str = "./.agents/plugins/example-plugin",
        copy_plugin: bool = True,
        compatibility_symlink: bool = True,
        personal_marketplace: bool = True,
    ) -> Path:
        profile_home = self.fake_home / ".codex"
        profile_home.mkdir(parents=True, exist_ok=True)
        config = profile_home / "config.toml"
        enabled_value = "true" if enabled else "false"
        config.write_text(
            f'[plugins."example-plugin@agent-skills-local"]\n'
            f"enabled = {enabled_value}\n",
            encoding="utf-8",
        )
        if stale_enabled:
            with config.open("a", encoding="utf-8") as handle:
                handle.write('\n[plugins."missing-plugin@agent-skills-local"]\nenabled = true\n')
        marketplace = profile_home / ".agents" / "plugins" / "marketplace.json"
        marketplace.parent.mkdir(parents=True, exist_ok=True)
        marketplace.write_text(
            json.dumps(
                {
                    "name": "agent-skills-local",
                    "plugins": [
                        {
                            "name": "example-plugin",
                            "source": {"source": "local", "path": source_path},
                        }
                    ],
                }
            )
            + "\n",
            encoding="utf-8",
        )
        if copy_plugin:
            source = self.repo_root / "plugins" / "example-plugin"
            official_target = self.fake_home / ".codex" / "plugins" / "example-plugin"
            shutil.rmtree(official_target, ignore_errors=True)
            shutil.copytree(source, official_target)
            target = profile_home / ".agents" / "plugins" / "example-plugin"
            shutil.rmtree(target, ignore_errors=True)
            if compatibility_symlink:
                target.symlink_to(official_target, target_is_directory=True)
            else:
                shutil.copytree(source, target)
        if personal_marketplace:
            personal_marketplace_path = self.fake_home / ".agents" / "plugins" / "marketplace.json"
            personal_marketplace_path.parent.mkdir(parents=True, exist_ok=True)
            personal_marketplace_path.write_text(
                json.dumps(
                    {
                        "name": "agent-skills-local",
                        "plugins": [
                            {
                                "name": "example-plugin",
                                "source": {"source": "local", "path": "./.codex/plugins/example-plugin"},
                            }
                        ],
                    }
                )
                + "\n",
                encoding="utf-8",
            )
        return profile_home

    def _write_runtime_cache_plugin(
        self,
        marketplace_name: str = "agent-skills-local",
        *,
        version: str | None = None,
        with_manifest: bool = True,
        with_skill: bool = True,
    ) -> Path:
        plugin_root = (
            self.repo_root
            / ".agents"
            / "plugins-runtime"
            / "cache"
            / marketplace_name
            / "example-plugin"
        )
        shutil.rmtree(plugin_root, ignore_errors=True)
        if version is not None:
            plugin_root = plugin_root / version
        if with_manifest:
            manifest = plugin_root / ".codex-plugin" / "plugin.json"
            manifest.parent.mkdir(parents=True, exist_ok=True)
            manifest.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "name": "example-plugin",
                        "version": "0.1.0",
                        "description": "Example plugin",
                        "skills": "./skills/",
                    }
                )
                + "\n",
                encoding="utf-8",
            )
        else:
            plugin_root.mkdir(parents=True, exist_ok=True)
        if with_skill:
            skill = plugin_root / "skills" / "example-skill" / "SKILL.md"
            skill.parent.mkdir(parents=True, exist_ok=True)
            skill.write_text(
                "---\nname: example-skill\ndescription: Example skill.\n---\n# Example Skill\n",
                encoding="utf-8",
            )
        marketplace_root = self.repo_root / ".agents" / "plugins-runtime" / "cache" / marketplace_name
        marketplace_manifest = marketplace_root / ".agents" / "plugins" / "marketplace.json"
        marketplace_manifest.parent.mkdir(parents=True, exist_ok=True)
        source_path = "./example-plugin" if version is None else f"./example-plugin/{version}"
        marketplace_manifest.write_text(
            json.dumps(
                {
                    "name": marketplace_name,
                    "plugins": [
                        {
                            "name": "example-plugin",
                            "source": {"source": "local", "path": source_path},
                        }
                    ],
                }
            )
            + "\n",
            encoding="utf-8",
        )
        return plugin_root

    def tearDown(self) -> None:
        self.home_patcher.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_list_plugins_state_returns_grouped_snapshot(self) -> None:
        self._write_runtime_cache_plugin()
        result = list_plugins_state(self.repo_root)
        self.assertEqual(result.status, "success")
        self.assertIn("installed_state", result.data)
        self.assertIn("activation_state", result.data)
        self.assertIn("health_state", result.data)
        self.assertEqual(result.data["installed_state"]["plugin_count"], 1)
        self.assertEqual(result.data["activation_state"]["plugin_count"], 1)
        self.assertEqual(result.data["health_state"]["status"], "healthy")
        self.assertFalse(result.data["desktop_readiness_state"]["desktop_loadable"])

    def test_status_reports_desktop_loadable_when_profile_config_and_mirror_are_ready(self) -> None:
        self._write_profile_plugin()

        result = status_plugin_state(self.repo_root, "example-plugin")

        self.assertEqual(result.status, "success")
        readiness = result.data["desktop_readiness_state"]
        self.assertTrue(readiness["desktop_loadable"])
        plugin_row = readiness["plugins"][0]
        self.assertTrue(plugin_row["active_config_ready"])
        self.assertTrue(plugin_row["personal_marketplace_ready"])
        self.assertTrue(plugin_row["profile_mirror_ready"])
        self.assertTrue(plugin_row["profile_checks"][0]["is_symlink"])
        self.assertEqual(
            plugin_row["profile_checks"][0]["resolved_realpath"],
            (self.fake_home / ".codex" / "plugins" / "example-plugin").resolve().as_posix(),
        )
        self.assertEqual(plugin_row["blockers"], [])

    def test_status_blocks_when_compatibility_mirror_is_copied_directory(self) -> None:
        self._write_profile_plugin(compatibility_symlink=False)

        result = status_plugin_state(self.repo_root, "example-plugin")

        self.assertEqual(result.status, "success")
        readiness = result.data["desktop_readiness_state"]
        self.assertFalse(readiness["desktop_loadable"])
        self.assertIn("PLUGIN_PROFILE_MIRROR_NOT_READY", readiness["blockers"])
        profile_issues = readiness["plugins"][0]["profile_checks"][0]["issues"]
        self.assertTrue(any("must be a symlink alias" in issue for issue in profile_issues))

    def test_status_blocks_when_official_personal_marketplace_is_missing(self) -> None:
        self._write_profile_plugin(personal_marketplace=False)

        result = status_plugin_state(self.repo_root, "example-plugin")

        self.assertEqual(result.status, "success")
        readiness = result.data["desktop_readiness_state"]
        self.assertFalse(readiness["desktop_loadable"])
        self.assertIn("PLUGIN_PERSONAL_MARKETPLACE_NOT_READY", readiness["blockers"])
        plugin_row = readiness["plugins"][0]
        self.assertFalse(plugin_row["personal_marketplace_ready"])
        self.assertEqual(
            plugin_row["personal_marketplace_check"]["marketplace_path"],
            (self.fake_home / ".agents" / "plugins" / "marketplace.json").as_posix(),
        )

    def test_status_uses_toml_parser_for_active_config_truth(self) -> None:
        profile_home = self._write_profile_plugin(enabled=False)
        (profile_home / "config.toml").write_text(
            'plugins."example-plugin@agent-skills-local".enabled = true\n',
            encoding="utf-8",
        )

        result = status_plugin_state(self.repo_root, "example-plugin")

        self.assertEqual(result.status, "success")
        readiness = result.data["desktop_readiness_state"]
        self.assertTrue(readiness["desktop_loadable"])
        self.assertEqual(readiness["enabled_plugin_ids"], ["example-plugin@agent-skills-local"])

    def test_status_ignores_broken_secondary_profile_for_default_desktop_loadability(self) -> None:
        self._write_profile_plugin()
        secondary_profile = self.fake_home / ".codex-preview"
        secondary_profile.mkdir(parents=True, exist_ok=True)

        result = status_plugin_state(self.repo_root, "example-plugin")

        self.assertEqual(result.status, "success")
        readiness = result.data["desktop_readiness_state"]
        self.assertTrue(readiness["desktop_loadable"])
        plugin_row = readiness["plugins"][0]
        self.assertTrue(plugin_row["profile_mirror_ready"])
        self.assertTrue(plugin_row["personal_marketplace_ready"])
        self.assertIn(secondary_profile.as_posix(), plugin_row["profile_homes"])
        secondary_rows = [
            row
            for row in plugin_row["profile_checks"]
            if row["profile_home"] == secondary_profile.as_posix()
        ]
        self.assertEqual(secondary_rows[0]["issues"], ["profile has no plugin marketplace manifest"])

    def test_status_reports_desktop_blocker_when_profile_path_is_missing(self) -> None:
        self._write_profile_plugin(copy_plugin=False)

        result = status_plugin_state(self.repo_root, "example-plugin")

        self.assertEqual(result.status, "success")
        readiness = result.data["desktop_readiness_state"]
        self.assertFalse(readiness["desktop_loadable"])
        self.assertIn("PLUGIN_PROFILE_MIRROR_NOT_READY", readiness["blockers"])
        profile_issues = readiness["plugins"][0]["profile_checks"][0]["issues"]
        self.assertTrue(any("marketplace local source path is not a directory" in issue for issue in profile_issues))

    def test_status_reports_desktop_blocker_for_stale_enabled_config_id(self) -> None:
        self._write_profile_plugin(stale_enabled=True)

        result = status_plugin_state(self.repo_root, "example-plugin")

        self.assertEqual(result.status, "success")
        readiness = result.data["desktop_readiness_state"]
        self.assertFalse(readiness["desktop_loadable"])
        self.assertIn("PLUGIN_ACTIVE_CONFIG_STALE_IDS", readiness["blockers"])
        self.assertEqual(readiness["stale_enabled_plugin_ids"], ["missing-plugin@agent-skills-local"])

    def test_list_plugins_state_detects_openai_curated_cache(self) -> None:
        marketplace = self.repo_root / ".agents" / "plugins" / "marketplace.json"
        payload = json.loads(marketplace.read_text(encoding="utf-8"))
        payload["name"] = "openai-curated"
        marketplace.write_text(json.dumps(payload) + "\n", encoding="utf-8")

        self._write_runtime_cache_plugin("openai-curated")

        result = list_plugins_state(self.repo_root)
        self.assertEqual(result.status, "success")
        activation_plugins = result.data["activation_state"]["plugins"]
        self.assertEqual(len(activation_plugins), 1)
        self.assertEqual(activation_plugins[0]["name"], "example-plugin")
        self.assertTrue(activation_plugins[0]["cache_present"])
        self.assertTrue(activation_plugins[0]["cache_content_ready"])

    def test_list_plugins_state_accepts_legacy_local_cache_family(self) -> None:
        marketplace = self.repo_root / ".agents" / "plugins" / "marketplace.json"
        payload = json.loads(marketplace.read_text(encoding="utf-8"))
        payload["name"] = "local"
        marketplace.write_text(json.dumps(payload) + "\n", encoding="utf-8")

        self._write_runtime_cache_plugin()

        result = list_plugins_state(self.repo_root)
        self.assertEqual(result.status, "success")
        self.assertEqual(result.data["health_state"]["status"], "healthy")
        activation_plugin = result.data["activation_state"]["plugins"][0]
        self.assertEqual(activation_plugin["marketplace_name"], "local")
        self.assertTrue(activation_plugin["cache_present"])
        self.assertTrue(activation_plugin["cache_content_ready"])

    def test_list_plugins_state_accepts_versioned_cache_content(self) -> None:
        self._write_runtime_cache_plugin(version="0.1.0")

        result = list_plugins_state(self.repo_root)
        self.assertEqual(result.status, "success")
        self.assertEqual(result.data["health_state"]["status"], "healthy")
        activation_plugin = result.data["activation_state"]["plugins"][0]
        self.assertTrue(activation_plugin["cache_present"])
        self.assertTrue(activation_plugin["cache_content_ready"])
        self.assertTrue(activation_plugin["cache_active_root"].endswith("/example-plugin/0.1.0"))

    def test_list_plugins_state_rejects_cache_without_manifest_declared_skills(self) -> None:
        shutil.rmtree(
            self.repo_root / ".agents" / "plugins-runtime" / "cache" / "agent-skills-local" / "example-plugin",
            ignore_errors=True,
        )
        self._write_runtime_cache_plugin(with_skill=False)

        result = list_plugins_state(self.repo_root)
        self.assertEqual(result.status, "success")
        self.assertEqual(result.data["health_state"]["status"], "degraded")
        activation_plugin = result.data["activation_state"]["plugins"][0]
        self.assertTrue(activation_plugin["cache_present"])
        self.assertFalse(activation_plugin["cache_content_ready"])
        self.assertTrue(activation_plugin["cache_issues"])
        blockers = result.data["health_state"]["blockers"]
        self.assertTrue(any("PLUGIN_RUNTIME_CONTENT_MISSING" in blocker for blocker in blockers))

    def test_list_plugins_state_rejects_cache_without_codex_marketplace_manifest(self) -> None:
        marketplace_manifest = (
            self.repo_root
            / ".agents"
            / "plugins-runtime"
            / "cache"
            / "agent-skills-local"
            / ".agents"
            / "plugins"
            / "marketplace.json"
        )
        marketplace_manifest.unlink()

        result = list_plugins_state(self.repo_root)

        self.assertEqual(result.status, "success")
        self.assertEqual(result.data["health_state"]["status"], "degraded")
        activation_plugin = result.data["activation_state"]["plugins"][0]
        self.assertTrue(activation_plugin["cache_present"])
        self.assertFalse(activation_plugin["cache_content_ready"])
        self.assertTrue(
            any("missing Codex marketplace manifest" in issue for issue in activation_plugin["cache_issues"]),
            activation_plugin["cache_issues"],
        )

    def test_list_plugins_state_rejects_broken_sibling_codex_marketplace_root(self) -> None:
        sibling_root = self.repo_root / "Plugins" / "cache" / "agent-skills-local" / "example-plugin" / "0.1.0"
        manifest = sibling_root / ".codex-plugin" / "plugin.json"
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "name": "example-plugin",
                    "version": "0.1.0",
                    "description": "Example plugin",
                    "skills": "./skills/",
                }
            )
            + "\n",
            encoding="utf-8",
        )
        skill = sibling_root / "skills" / "example-skill" / "SKILL.md"
        skill.parent.mkdir(parents=True, exist_ok=True)
        skill.write_text("---\nname: example-skill\ndescription: Example skill.\n---\n", encoding="utf-8")

        result = list_plugins_state(self.repo_root)

        self.assertEqual(result.status, "success")
        self.assertEqual(result.data["health_state"]["status"], "degraded")
        activation_plugin = result.data["activation_state"]["plugins"][0]
        self.assertTrue(activation_plugin["cache_present"])
        self.assertFalse(activation_plugin["cache_content_ready"])
        self.assertTrue(
            any("Plugins/cache/agent-skills-local" in issue for issue in activation_plugin["cache_issues"]),
            activation_plugin["cache_issues"],
        )

    def test_doctor_treats_missing_cache_as_blocker(self) -> None:
        cache_root = self.repo_root / ".agents" / "plugins-runtime" / "cache"
        shutil.rmtree(cache_root, ignore_errors=True)

        with patch(
            "ask.plugin_state.subprocess.run",
            return_value=subprocess.CompletedProcess(
                args=[],
                returncode=0,
                stdout="Plugin-shadowing check passed",
                stderr="",
            ),
        ):
            result = doctor_plugins_state(self.repo_root)

        self.assertEqual(result.status, "error")
        self.assertEqual(result.data["health_state"]["status"], "degraded")
        activation = result.data["health_state"]["checks"]["activation"]
        self.assertTrue(activation["missing_cache_plugins"])
        self.assertTrue(activation["cache_content_blockers"])
        self.assertTrue(activation["warnings"])

    def test_status_plugin_state_errors_when_missing(self) -> None:
        result = status_plugin_state(self.repo_root, "missing-plugin")
        self.assertEqual(result.status, "error")
        self.assertTrue(result.errors)
        self.assertEqual(result.errors[0].code, "ERR_VALIDATION")

    def test_doctor_reports_shadowing_failure(self) -> None:
        with patch(
            "ask.plugin_state.subprocess.run",
            return_value=subprocess.CompletedProcess(
                args=[],
                returncode=1,
                stdout="",
                stderr="Plugin-shadowing check failed",
            ),
        ):
            result = doctor_plugins_state(self.repo_root)

        self.assertEqual(result.status, "error")
        self.assertIn("health_state", result.data)
        self.assertEqual(result.data["health_state"]["status"], "degraded")
        blockers = result.data["health_state"]["blockers"]
        self.assertTrue(any("PLUGIN_SKILL_SHADOWING" in blocker for blocker in blockers))

    def test_doctor_reports_empty_readme_warning(self) -> None:
        (self.repo_root / "plugins" / "example-plugin" / "README.md").write_text("", encoding="utf-8")

        with patch(
            "ask.plugin_state.subprocess.run",
            return_value=subprocess.CompletedProcess(
                args=[],
                returncode=0,
                stdout="Plugin-shadowing check passed",
                stderr="",
            ),
        ):
            result = doctor_plugins_state(self.repo_root)

        self.assertEqual(result.status, "success")
        quality = result.data["health_state"]["checks"]["plugin_package_quality"]
        plugin_row = quality["plugins"][0]
        self.assertEqual(plugin_row["issues"], [])
        self.assertIn("README missing or empty", plugin_row["warnings"])

    def test_doctor_accepts_hooks_only_manifest(self) -> None:
        manifest_path = self.repo_root / "plugins" / "example-plugin" / ".codex-plugin" / "plugin.json"
        manifest_payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest_payload.pop("skills", None)
        manifest_payload["hooks"] = "./hooks.json"
        manifest_path.write_text(json.dumps(manifest_payload) + "\n", encoding="utf-8")

        with patch(
            "ask.plugin_state.subprocess.run",
            return_value=subprocess.CompletedProcess(
                args=[],
                returncode=0,
                stdout="Plugin-shadowing check passed",
                stderr="",
            ),
        ):
            result = doctor_plugins_state(self.repo_root)

        self.assertEqual(result.status, "success")
        quality = result.data["health_state"]["checks"]["plugin_package_quality"]
        plugin_row = quality["plugins"][0]
        self.assertEqual(plugin_row["issues"], [])

    def test_doctor_reports_missing_asset_warning(self) -> None:
        (self.repo_root / "plugins" / "example-plugin" / "assets" / "icon.png").unlink()

        with patch(
            "ask.plugin_state.subprocess.run",
            return_value=subprocess.CompletedProcess(
                args=[],
                returncode=0,
                stdout="Plugin-shadowing check passed",
                stderr="",
            ),
        ):
            result = doctor_plugins_state(self.repo_root)

        self.assertEqual(result.status, "success")
        quality = result.data["health_state"]["checks"]["plugin_package_quality"]
        plugin_row = quality["plugins"][0]
        self.assertEqual(plugin_row["issues"], [])
        self.assertTrue(any("interface.composerIcon" in warning for warning in plugin_row["warnings"]))

    def test_doctor_reports_asset_path_escape_warning(self) -> None:
        manifest_path = self.repo_root / "plugins" / "example-plugin" / ".codex-plugin" / "plugin.json"
        manifest_payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest_payload["interface"]["logo"] = "../../outside/logo.png"
        manifest_path.write_text(json.dumps(manifest_payload) + "\n", encoding="utf-8")

        with patch(
            "ask.plugin_state.subprocess.run",
            return_value=subprocess.CompletedProcess(
                args=[],
                returncode=0,
                stdout="Plugin-shadowing check passed",
                stderr="",
            ),
        ):
            result = doctor_plugins_state(self.repo_root)

        self.assertEqual(result.status, "success")
        quality = result.data["health_state"]["checks"]["plugin_package_quality"]
        plugin_row = quality["plugins"][0]
        self.assertEqual(plugin_row["issues"], [])
        self.assertTrue(any("escapes plugin root" in warning for warning in plugin_row["warnings"]))

    def test_list_plugins_state_includes_categorized_plugins(self) -> None:
        categorized_manifest = (
            self.repo_root / "Plugins" / "third-party" / "nested-plugin" / ".codex-plugin" / "plugin.json"
        )
        categorized_manifest.parent.mkdir(parents=True, exist_ok=True)
        (categorized_manifest.parent.parent / "README.md").write_text(
            "# Nested Plugin\n\nCategorized plugin fixture.\n",
            encoding="utf-8",
        )
        categorized_manifest.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "name": "nested-plugin",
                    "version": "0.1.0",
                    "description": "Nested fixture",
                    "interface": {
                        "displayName": "Nested Plugin",
                        "shortDescription": "Nested short description",
                        "longDescription": "Nested long description",
                        "developerName": "Agent Skills Team",
                        "category": "Productivity",
                        "capabilities": ["Read"],
                        "websiteURL": "https://example.com/nested",
                        "defaultPrompt": "Help with nested plugin workflows.",
                    },
                }
            )
            + "\n",
            encoding="utf-8",
        )

        result = list_plugins_state(self.repo_root)
        self.assertEqual(result.status, "success")
        names = sorted(plugin["name"] for plugin in result.data["installed_state"]["plugins"])
        self.assertEqual(names, ["example-plugin", "nested-plugin"])

    def test_list_plugins_state_handles_symlinked_plugins_outside_repo(self) -> None:
        external_root = self.temp_dir / "external-plugin-root"
        external_manifest = external_root / ".codex-plugin" / "plugin.json"
        external_manifest.parent.mkdir(parents=True, exist_ok=True)
        external_manifest.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "name": "external-plugin",
                    "version": "0.2.0",
                    "description": "External fixture",
                }
            )
            + "\n",
            encoding="utf-8",
        )

        linked_plugin = self.repo_root / "plugins" / "external-plugin"
        linked_plugin.parent.mkdir(parents=True, exist_ok=True)
        linked_plugin.symlink_to(external_root, target_is_directory=True)

        result = list_plugins_state(self.repo_root)
        self.assertEqual(result.status, "success")
        installed = {
            plugin["name"]: plugin for plugin in result.data["installed_state"]["plugins"]
        }
        self.assertIn("external-plugin", installed)
        self.assertEqual(installed["external-plugin"]["path"], external_root.resolve().as_posix())
        activation = {
            plugin["name"]: plugin for plugin in result.data["activation_state"]["plugins"]
        }
        self.assertFalse(activation["external-plugin"]["repo_managed"])
        self.assertEqual(result.data["health_state"]["status"], "healthy")


if __name__ == "__main__":
    unittest.main()
