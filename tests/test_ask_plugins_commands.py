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

from ask.commands.plugins import harden_plugin, init_plugin, install_plugin


class TestAskPluginsCommands(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="ask-plugins-cmds-"))
        self.repo_root = self.temp_dir / "repo"
        self.repo_root.mkdir(parents=True)

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_init_plugin_creates_manual_companion_folder(self) -> None:
        creator_script = self.repo_root / "skills-system" / "plugin-creator" / "scripts" / "create_basic_plugin.py"
        creator_script.parent.mkdir(parents=True, exist_ok=True)
        creator_script.write_text("#!/usr/bin/env python3\n", encoding="utf-8")

        plugin_root = self.repo_root / "plugins" / "my-plugin"
        plugin_root.mkdir(parents=True, exist_ok=True)
        completed = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout=f"Created plugin scaffold: {plugin_root}\n",
            stderr="",
        )
        with patch("ask.commands.plugins.subprocess.run", return_value=completed) as run_mock:
            result = init_plugin(
                self.repo_root,
                "My Plugin",
                with_marketplace=False,
                companion_folders=["references"],
            )

        self.assertEqual(result.status, "success")
        self.assertTrue((plugin_root / "references").is_dir())
        called_cmd = run_mock.call_args[0][0]
        self.assertNotIn("--with-references", called_cmd)

    def test_install_plugin_uses_packaged_installer_fallback(self) -> None:
        installer_script = (
            self.repo_root
            / "plugins"
            / "plugin-factory"
            / "skills"
            / "plugin-installer"
            / "scripts"
            / "install-plugin-from-github.py"
        )
        installer_script.parent.mkdir(parents=True, exist_ok=True)
        installer_script.write_text("#!/usr/bin/env python3\n", encoding="utf-8")

        completed = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="Installed demo-plugin to /tmp/demo-plugin\n",
            stderr="",
        )
        with patch("ask.commands.plugins.subprocess.run", return_value=completed) as run_mock:
            result = install_plugin(
                self.repo_root,
                url="https://github.com/example/repo",
                plugin_path="plugins/demo-plugin",
                name="demo-plugin",
            )

        self.assertEqual(result.status, "success")
        called_cmd = run_mock.call_args[0][0]
        self.assertEqual(called_cmd[0], "python3")
        self.assertEqual(called_cmd[1], str(installer_script))

    def test_harden_plugin_runs_validate_compat_and_marketplace_audit(self) -> None:
        builder_script = self.repo_root / "utilities" / "plugin-builder" / "scripts" / "plugin_builder.py"
        builder_script.parent.mkdir(parents=True, exist_ok=True)
        builder_script.write_text("#!/usr/bin/env python3\n", encoding="utf-8")

        plugin_root = self.repo_root / "plugins" / "demo-plugin"
        plugin_root.mkdir(parents=True, exist_ok=True)

        with patch(
            "ask.commands.plugins.subprocess.run",
            side_effect=[
                subprocess.CompletedProcess(args=[], returncode=0, stdout="PASS: validate\n", stderr=""),
                subprocess.CompletedProcess(args=[], returncode=0, stdout="PASS: compat\n", stderr=""),
                subprocess.CompletedProcess(args=[], returncode=0, stdout="PASS: marketplace\n", stderr=""),
            ],
        ):
            result = harden_plugin(self.repo_root, "plugins/demo-plugin")

        self.assertEqual(result.status, "success")
        runs = result.data.get("command_runs", [])
        self.assertEqual(len(runs), 3)
        self.assertEqual(runs[0]["step"], "validate")
        self.assertEqual(runs[1]["step"], "audit-compat")
        self.assertEqual(runs[2]["step"], "audit-marketplace")


if __name__ == "__main__":
    unittest.main()
