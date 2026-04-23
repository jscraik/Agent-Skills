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

from ask.commands.plugins import doctor_plugins_state, list_plugins_state, status_plugin_state


class TestAskPluginsState(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="ask-plugins-state-"))
        self.repo_root = self.temp_dir / "repo"
        self.repo_root.mkdir(parents=True)

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
        (
            self.repo_root
            / ".agents"
            / "plugins-runtime"
            / "cache"
            / "agent-skills-local"
            / "example-plugin"
        ).mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_list_plugins_state_returns_grouped_snapshot(self) -> None:
        result = list_plugins_state(self.repo_root)
        self.assertEqual(result.status, "success")
        self.assertIn("installed_state", result.data)
        self.assertIn("activation_state", result.data)
        self.assertIn("health_state", result.data)
        self.assertEqual(result.data["installed_state"]["plugin_count"], 1)
        self.assertEqual(result.data["activation_state"]["plugin_count"], 1)
        self.assertEqual(result.data["health_state"]["status"], "healthy")

    def test_list_plugins_state_detects_openai_curated_cache(self) -> None:
        marketplace = self.repo_root / ".agents" / "plugins" / "marketplace.json"
        payload = json.loads(marketplace.read_text(encoding="utf-8"))
        payload["name"] = "openai-curated"
        marketplace.write_text(json.dumps(payload) + "\n", encoding="utf-8")

        cache_dir = (
            self.repo_root
            / ".agents"
            / "plugins-runtime"
            / "cache"
            / "openai-curated"
            / "example-plugin"
        )
        cache_dir.mkdir(parents=True, exist_ok=True)

        result = list_plugins_state(self.repo_root)
        self.assertEqual(result.status, "success")
        activation_plugins = result.data["activation_state"]["plugins"]
        self.assertEqual(len(activation_plugins), 1)
        self.assertEqual(activation_plugins[0]["name"], "example-plugin")
        self.assertTrue(activation_plugins[0]["cache_present"])

    def test_list_plugins_state_accepts_legacy_local_cache_family(self) -> None:
        marketplace = self.repo_root / ".agents" / "plugins" / "marketplace.json"
        payload = json.loads(marketplace.read_text(encoding="utf-8"))
        payload["name"] = "local"
        marketplace.write_text(json.dumps(payload) + "\n", encoding="utf-8")

        legacy_cache_dir = (
            self.repo_root
            / ".agents"
            / "plugins-runtime"
            / "cache"
            / "agent-skills-local"
            / "example-plugin"
        )
        legacy_cache_dir.mkdir(parents=True, exist_ok=True)

        result = list_plugins_state(self.repo_root)
        self.assertEqual(result.status, "success")
        self.assertEqual(result.data["health_state"]["status"], "healthy")
        activation_plugin = result.data["activation_state"]["plugins"][0]
        self.assertEqual(activation_plugin["marketplace_name"], "local")
        self.assertTrue(activation_plugin["cache_present"])

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
