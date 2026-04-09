import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "lib"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from ask.commands.plugins import doctor_plugins_state, list_plugins_state, status_plugin_state


class TestAskPluginsState(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="ask-plugins-state-"))
        self.repo_root = self.temp_dir / "repo"
        self.repo_root.mkdir(parents=True)

        plugin_manifest = self.repo_root / "plugins" / "example-plugin" / ".codex-plugin" / "plugin.json"
        plugin_manifest.parent.mkdir(parents=True, exist_ok=True)
        plugin_manifest.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "name": "example-plugin",
                    "version": "0.1.0",
                    "description": "Example plugin",
                    "governance": {"owner": "Agent Skills Team"},
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
                            "source": {"source": "local", "path": "./plugins/example-plugin"},
                        }
                    ],
                }
            )
            + "\n",
            encoding="utf-8",
        )

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


if __name__ == "__main__":
    unittest.main()
