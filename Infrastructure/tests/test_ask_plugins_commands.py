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

from ask.commands.plugins import (  # noqa: E402
    harden_plugin,
    init_plugin,
    install_plugin,
    prune_stale_plugin_config,
    sync_local_runtime_plugins,
    uninstall_plugin,
)


class TestAskPluginsCommands(unittest.TestCase):
    def setUp(self) -> None:
        """
        Create an isolated temporary repository for each test.

        Initialises `self.temp_dir` to a new temporary directory and creates `self.repo_root`
        as a nested `repo` directory inside it for use by tests.
        """
        self.temp_dir = Path(tempfile.mkdtemp(prefix="ask-plugins-cmds-"))
        self.repo_root = self.temp_dir / "repo"
        self.repo_root.mkdir(parents=True)

    def tearDown(self) -> None:
        """
        Remove the temporary repository directory created for the test.

        This performs a recursive deletion of `self.temp_dir` and its contents, ignoring any filesystem errors that occur during removal.
        """
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _write_repo_cache(self, *, plugin_name: str = "example-plugin") -> None:
        plugin_root = self.repo_root / ".agents" / "plugins-runtime" / "cache" / "agent-skills-local" / plugin_name
        manifest = plugin_root / ".codex-plugin" / "plugin.json"
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "name": plugin_name,
                    "version": "0.1.0",
                    "description": "Example plugin",
                    "skills": "./skills/",
                }
            )
            + "\n",
            encoding="utf-8",
        )
        skill = plugin_root / "skills" / "example-skill" / "SKILL.md"
        skill.parent.mkdir(parents=True, exist_ok=True)
        skill.write_text("---\nname: example-skill\ndescription: Example skill.\n---\n", encoding="utf-8")
        marketplace = (
            self.repo_root
            / ".agents"
            / "plugins-runtime"
            / "cache"
            / "agent-skills-local"
            / ".agents"
            / "plugins"
            / "marketplace.json"
        )
        marketplace.parent.mkdir(parents=True, exist_ok=True)
        marketplace.write_text(
            json.dumps(
                {
                    "name": "agent-skills-local",
                    "plugins": [
                        {
                            "name": plugin_name,
                            "source": {"source": "local", "path": f"./{plugin_name}"},
                        }
                    ],
                }
            )
            + "\n",
            encoding="utf-8",
        )

    def _write_repo_marketplace(self, *, plugin_name: str = "example-plugin") -> None:
        marketplace = self.repo_root / "Plugins" / "marketplace.json"
        marketplace.parent.mkdir(parents=True, exist_ok=True)
        marketplace.write_text(
            json.dumps(
                {
                    "name": "agent-skills-local",
                    "plugins": [
                        {
                            "name": plugin_name,
                            "source": {"source": "local", "path": f"./Plugins/{plugin_name}"},
                        }
                    ],
                }
            )
            + "\n",
            encoding="utf-8",
        )

    def _write_profile_config(self, home: Path, content: str) -> Path:
        profile_home = home / ".codex"
        profile_home.mkdir(parents=True, exist_ok=True)
        config_path = profile_home / "config.toml"
        config_path.write_text(content, encoding="utf-8")
        return config_path

    def test_init_plugin_creates_manual_companion_folder(self) -> None:
        creator_script = (
            self.repo_root
            / "Plugins"
            / "plugin-factory"
            / "skills"
            / "scaffolding_templates"
            / "plugin-creator"
            / "scripts"
            / "create_basic_plugin.pyw"
        )
        creator_script.parent.mkdir(parents=True, exist_ok=True)
        creator_script.write_text("#!/usr/bin/env python3\n", encoding="utf-8")

        plugin_root = self.repo_root / "Plugins" / "third-party" / "my-plugin"
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
        self.assertEqual(called_cmd[1], str(creator_script))

    def test_init_plugin_missing_creator_exposes_validation_command(self) -> None:
        result = init_plugin(
            self.repo_root,
            "Demo Plugin",
            with_marketplace=True,
            companion_folders=["references"],
        )

        self.assertEqual(result.status, "error")
        self.assertEqual(result.errors[0].code, "ERR_RUNTIME")
        self.assertEqual(
            result.data["validation_commands"],
            [
                "./bin/ask plugins init 'Demo Plugin' --with-marketplace "
                "--with-references --json --robot"
            ],
        )

    def test_install_plugin_uses_packaged_installer_fallback(self) -> None:
        """
        Ensures the packaged installer script is used as a fallback when installing a plugin.

        Creates a packaged installer script under the repository, patches `subprocess.run` to simulate a successful install, calls `install_plugin(...)`, and asserts the call succeeds and that the invoked subprocess command runs `python3` with the path to the packaged installer script.
        """
        installer_script = (
            self.repo_root
            / "Plugins"
            / "plugin-factory"
            / "skills"
            / "infrastructure_ops"
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
                plugin_path="Plugins/demo-plugin",
                name="demo-plugin",
            )

        self.assertEqual(result.status, "success")
        called_cmd = run_mock.call_args[0][0]
        self.assertEqual(called_cmd[0], "python3")
        self.assertEqual(called_cmd[1], str(installer_script))

    def test_install_plugin_dry_run_exposes_validation_command(self) -> None:
        result = install_plugin(
            self.repo_root,
            url="https://github.com/example/repo",
            plugin_path="Plugins/demo-plugin",
            name="demo-plugin",
            ref="abc123",
            dry_run=True,
        )

        self.assertEqual(result.status, "success")
        self.assertEqual(
            result.data["validation_commands"],
            [
                "./bin/ask plugins install https://github.com/example/repo "
                "--path Plugins/demo-plugin --name demo-plugin --ref abc123 "
                "--dry-run --json --robot"
            ],
        )

    def test_install_plugin_dry_run_includes_desktop_readiness_flags(self) -> None:
        result = install_plugin(
            self.repo_root,
            url="https://github.com/example/repo",
            plugin_path="Plugins/demo-plugin",
            name="demo-plugin",
            sync_profile=True,
            require_desktop_loadable=True,
            dry_run=True,
        )

        self.assertEqual(result.status, "success")
        self.assertEqual(
            result.data["validation_commands"],
            [
                "./bin/ask plugins install https://github.com/example/repo "
                "--path Plugins/demo-plugin --name demo-plugin --sync-profile "
                "--require-desktop-loadable --dry-run --json --robot"
            ],
        )
        self.assertTrue(result.data["sync_profile"])
        self.assertTrue(result.data["require_desktop_loadable"])

    def test_prune_stale_plugin_config_dry_run_reports_without_writing(self) -> None:
        self._write_repo_marketplace(plugin_name="example-plugin")
        fake_home = self.temp_dir / "home"
        config_path = self._write_profile_config(
            fake_home,
            '[plugins."example-plugin@agent-skills-local"]\n'
            'enabled = true\n\n'
            '[plugins."demo-plugin@agent-skills-local"]\n'
            'enabled = true\n',
        )

        with (
            patch("ask.commands.plugins.Path.home", return_value=fake_home),
            patch("ask.plugin_state.Path.home", return_value=fake_home),
        ):
            result = prune_stale_plugin_config(self.repo_root, dry_run=True)

        self.assertEqual(result.status, "success")
        self.assertTrue(result.data["dry_run"])
        self.assertEqual(result.data["stale_enabled_plugin_ids"], ["demo-plugin@agent-skills-local"])
        self.assertEqual(result.data["removed_plugin_ids"], ["demo-plugin@agent-skills-local"])
        self.assertIn("demo-plugin@agent-skills-local", config_path.read_text(encoding="utf-8"))

    def test_prune_stale_plugin_config_removes_stale_enabled_block(self) -> None:
        self._write_repo_marketplace(plugin_name="example-plugin")
        self._write_repo_cache(plugin_name="example-plugin")
        fake_home = self.temp_dir / "home"
        config_path = self._write_profile_config(
            fake_home,
            '[plugins."example-plugin@agent-skills-local"]\n'
            'enabled = true\n\n'
            '[plugins."demo-plugin@agent-skills-local"]\n'
            'enabled = true\n\n'
            '[plugins."browser@openai-bundled"]\n'
            'enabled = true\n',
        )

        with (
            patch("ask.commands.plugins.Path.home", return_value=fake_home),
            patch("ask.plugin_state.Path.home", return_value=fake_home),
        ):
            result = prune_stale_plugin_config(self.repo_root, stability_seconds=0)

        self.assertEqual(result.status, "success")
        self.assertTrue(result.data["changed"])
        self.assertEqual(result.data["removed_plugin_ids"], ["demo-plugin@agent-skills-local"])
        content = config_path.read_text(encoding="utf-8")
        self.assertNotIn("demo-plugin@agent-skills-local", content)
        self.assertIn('plugins."example-plugin@agent-skills-local"', content)
        self.assertIn('plugins."browser@openai-bundled"', content)
        self.assertEqual(result.data["desktop_readiness_state"]["stale_enabled_plugin_ids"], [])

    def test_prune_stale_plugin_config_can_verify_clean_config_stability(self) -> None:
        self._write_repo_marketplace(plugin_name="example-plugin")
        self._write_repo_cache(plugin_name="example-plugin")
        fake_home = self.temp_dir / "home"
        self._write_profile_config(
            fake_home,
            '[plugins."example-plugin@agent-skills-local"]\n'
            "enabled = true\n",
        )

        with (
            patch("ask.commands.plugins.Path.home", return_value=fake_home),
            patch("ask.plugin_state.Path.home", return_value=fake_home),
        ):
            result = prune_stale_plugin_config(
                self.repo_root,
                stability_seconds=0,
                verify_stable_when_clean=True,
            )

        self.assertEqual(result.status, "success")
        self.assertFalse(result.data["changed"])
        self.assertEqual(result.data["stale_enabled_plugin_ids"], [])
        self.assertEqual(result.data["desktop_readiness_state"]["stale_enabled_plugin_ids"], [])
        self.assertEqual(result.data["stability_checks"][0]["stale_enabled_plugin_ids"], [])

    def test_install_plugin_missing_installer_exposes_validation_command(self) -> None:
        result = install_plugin(
            self.repo_root,
            url="https://github.com/example/repo",
            plugin_path="Plugins/demo-plugin",
            name="demo-plugin",
        )

        self.assertEqual(result.status, "error")
        self.assertEqual(result.errors[0].code, "ERR_RUNTIME")
        self.assertEqual(
            result.data["validation_commands"],
            [
                "./bin/ask plugins install https://github.com/example/repo "
                "--path Plugins/demo-plugin --name demo-plugin --json --robot"
            ],
        )

    def test_uninstall_plugin_dry_run_exposes_validation_command(self) -> None:
        plugin_root = self.repo_root / "Plugins" / "third-party" / "demo-plugin"
        plugin_root.mkdir(parents=True, exist_ok=True)

        result = uninstall_plugin(self.repo_root, "demo-plugin", dry_run=True)

        self.assertEqual(result.status, "success")
        self.assertTrue(result.data["dry_run"])
        self.assertEqual(result.data["plugin_name"], "demo-plugin")
        self.assertEqual(result.data["target_path"], "Plugins/third-party/demo-plugin")
        self.assertEqual(
            result.data["validation_commands"],
            ["./bin/ask plugins uninstall demo-plugin --dry-run --json --robot"],
        )

    def test_uninstall_plugin_dry_run_supports_direct_plugin_layout(self) -> None:
        plugin_root = self.repo_root / "Plugins" / "demo-plugin"
        plugin_root.mkdir(parents=True, exist_ok=True)

        result = uninstall_plugin(self.repo_root, "demo-plugin", dry_run=True)

        self.assertEqual(result.status, "success")
        self.assertEqual(result.data["target_path"], "Plugins/demo-plugin")
        self.assertEqual(
            result.data["validation_commands"],
            ["./bin/ask plugins uninstall demo-plugin --dry-run --json --robot"],
        )

    def test_sync_local_runtime_missing_marketplace_exposes_validation_command(self) -> None:
        result = sync_local_runtime_plugins(self.repo_root, dry_run=True)

        self.assertEqual(result.status, "error")
        self.assertEqual(result.errors[0].code, "ERR_RUNTIME")
        self.assertEqual(
            result.data["validation_commands"],
            ["./bin/ask plugins sync-local-runtime --dry-run --json --robot"],
        )

    def test_sync_local_runtime_empty_marketplace_exposes_validation_command(self) -> None:
        marketplace = self.repo_root / "Plugins" / "marketplace.json"
        marketplace.parent.mkdir(parents=True, exist_ok=True)
        marketplace.write_text('{"plugins": []}\n', encoding="utf-8")

        result = sync_local_runtime_plugins(self.repo_root, dry_run=True)

        self.assertEqual(result.status, "error")
        self.assertEqual(result.errors[0].code, "ERR_VALIDATION")
        self.assertEqual(
            result.data["validation_commands"],
            ["./bin/ask plugins sync-local-runtime --dry-run --json --robot"],
        )

    def test_sync_local_runtime_skips_samefile_marketplace_copy(self) -> None:
        plugin_root = self.repo_root / "Plugins" / "example-plugin"
        manifest_path = plugin_root / ".codex-plugin" / "plugin.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "name": "example-plugin",
                    "version": "0.1.0",
                    "description": "Example plugin",
                    "skills": "./skills/",
                    "interface": {
                        "displayName": "Example Plugin",
                        "shortDescription": "Example plugin",
                        "longDescription": "Example plugin",
                        "developerName": "Agent Skills Team",
                        "category": "Productivity",
                        "capabilities": ["Read"],
                        "websiteURL": "https://example.com",
                    },
                }
            )
            + "\n",
            encoding="utf-8",
        )
        (plugin_root / "skills" / "example-skill").mkdir(parents=True)
        (plugin_root / "skills" / "example-skill" / "SKILL.md").write_text(
            "---\nname: example-skill\ndescription: Example skill.\n---\n",
            encoding="utf-8",
        )
        marketplace = self.repo_root / "Plugins" / "marketplace.json"
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

        fake_home = self.temp_dir / "home"
        profile_plugins = fake_home / ".codex" / "Plugins"
        profile_plugins.mkdir(parents=True)
        (profile_plugins / "marketplace.json").symlink_to(marketplace)
        personal_plugins = fake_home / ".agents" / "plugins"
        personal_plugins.parent.mkdir(parents=True)
        personal_plugins.symlink_to(self.repo_root / "Plugins", target_is_directory=True)

        with patch("ask.commands.plugins.Path.home", return_value=fake_home):
            result = sync_local_runtime_plugins(self.repo_root)

        self.assertEqual(result.status, "success")
        self.assertTrue(
            (profile_plugins / "example-plugin").samefile(
                fake_home / ".codex" / "plugins" / "example-plugin"
            )
        )
        self.assertTrue((fake_home / ".codex" / ".agents" / "plugins" / "example-plugin").is_symlink())
        self.assertEqual(
            (fake_home / ".codex" / ".agents" / "plugins" / "example-plugin").resolve(),
            (fake_home / ".codex" / "plugins" / "example-plugin").resolve(),
        )
        self.assertTrue((fake_home / ".codex" / "plugins" / "example-plugin" / ".codex-plugin" / "plugin.json").is_file())
        personal_marketplace = fake_home / ".agents" / "plugins" / "marketplace.json"
        self.assertTrue(personal_marketplace.is_file())
        self.assertEqual(
            (fake_home / ".agents" / "plugins").resolve(),
            (self.repo_root / ".agents" / "personal-plugins").resolve(),
        )
        self.assertEqual(
            json.loads(marketplace.read_text(encoding="utf-8"))["plugins"][0]["source"]["path"],
            "./Plugins/example-plugin",
        )
        self.assertTrue((fake_home / ".agents" / "plugins" / "example-plugin").is_symlink())
        self.assertEqual(
            (fake_home / ".agents" / "plugins" / "example-plugin").resolve(),
            (fake_home / ".codex" / "plugins" / "example-plugin").resolve(),
        )
        personal_payload = json.loads(personal_marketplace.read_text(encoding="utf-8"))
        self.assertEqual(
            personal_payload["plugins"][0]["source"]["path"],
            "./.codex/plugins/example-plugin",
        )
        profile_marketplace = json.loads(
            (fake_home / ".codex" / ".agents" / "plugins" / "marketplace.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            profile_marketplace["plugins"][0]["source"]["path"],
            "./.agents/plugins/example-plugin",
        )
        readiness = result.data["desktop_readiness_state"]
        self.assertFalse(readiness["desktop_loadable"])
        self.assertIn("PLUGIN_NOT_ENABLED_IN_ACTIVE_CONFIG", readiness["blockers"])
        reports = {Path(report["runtime_root"]).as_posix(): report for report in result.data["runtime_reports"]}
        self.assertTrue(reports[(fake_home / ".codex" / "plugins").as_posix()]["materializes_payload"])
        self.assertTrue(reports[(fake_home / ".codex" / "Plugins").as_posix()]["skipped_samefile_runtime_root"])
        self.assertFalse(reports[(fake_home / ".codex" / ".agents" / "plugins").as_posix()]["materializes_payload"])
        self.assertTrue(reports[(fake_home / ".agents" / "plugins").as_posix()]["repointed_marketplace_root"])
        self.assertEqual(
            reports[(fake_home / ".codex" / ".agents" / "plugins").as_posix()]["symlinked_plugins"],
            ["example-plugin"],
        )

    def test_sync_local_runtime_reports_desktop_loadable_after_profile_sync_when_enabled(self) -> None:
        plugin_root = self.repo_root / "Plugins" / "example-plugin"
        manifest_path = plugin_root / ".codex-plugin" / "plugin.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "name": "example-plugin",
                    "version": "0.1.0",
                    "description": "Example plugin",
                    "skills": "./skills/",
                    "interface": {
                        "displayName": "Example Plugin",
                        "shortDescription": "Example plugin",
                        "longDescription": "Example plugin",
                        "developerName": "Agent Skills Team",
                        "category": "Productivity",
                        "capabilities": ["Read"],
                        "websiteURL": "https://example.com",
                    },
                }
            )
            + "\n",
            encoding="utf-8",
        )
        (plugin_root / "skills" / "example-skill").mkdir(parents=True)
        (plugin_root / "skills" / "example-skill" / "SKILL.md").write_text(
            "---\nname: example-skill\ndescription: Example skill.\n---\n",
            encoding="utf-8",
        )
        marketplace = self.repo_root / "Plugins" / "marketplace.json"
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
        self._write_repo_cache(plugin_name="example-plugin")

        fake_home = self.temp_dir / "home"
        profile_home = fake_home / ".codex"
        profile_home.mkdir(parents=True)
        (profile_home / "config.toml").write_text(
            '[plugins."example-plugin@agent-skills-local"]\nenabled = true\n',
            encoding="utf-8",
        )

        with patch("ask.commands.plugins.Path.home", return_value=fake_home):
            result = sync_local_runtime_plugins(self.repo_root)

        self.assertEqual(result.status, "success")
        readiness = result.data["desktop_readiness_state"]
        self.assertTrue(readiness["desktop_loadable"])
        self.assertEqual(readiness["blockers"], [])
        self.assertEqual(
            readiness["plugins"][0]["profile_checks"][0]["source_path"],
            "./.agents/plugins/example-plugin",
        )
        self.assertTrue(readiness["plugins"][0]["personal_marketplace_ready"])
        self.assertEqual(
            readiness["plugins"][0]["personal_marketplace_check"]["source_path"],
            "./.codex/plugins/example-plugin",
        )
        self.assertTrue(readiness["plugins"][0]["profile_checks"][0]["is_symlink"])
        self.assertEqual(
            readiness["plugins"][0]["profile_checks"][0]["resolved_realpath"],
            (fake_home / ".codex" / "plugins" / "example-plugin").resolve().as_posix(),
        )

    def test_harden_plugin_missing_builder_exposes_validation_command(self) -> None:
        plugin_root = self.repo_root / "Plugins" / "third-party" / "demo-plugin"
        plugin_root.mkdir(parents=True, exist_ok=True)

        result = harden_plugin(self.repo_root, "Plugins/third-party/demo-plugin")

        self.assertEqual(result.status, "error")
        self.assertEqual(result.errors[0].code, "ERR_RUNTIME")
        self.assertEqual(
            result.data["validation_commands"],
            ["./bin/ask plugins harden Plugins/third-party/demo-plugin --json --robot"],
        )

    def test_harden_plugin_runs_validate_compat_and_marketplace_audit(self) -> None:
        """
        Verify that harden_plugin executes the validation, compatibility audit and marketplace audit in sequence and records each step's result.

        Sets up a plugin-builder script and plugin directory, simulates three successful subprocess outputs (`PASS: validate`, `PASS: compat`, `PASS: marketplace`), and asserts that the returned result has status "success" with exactly three recorded command runs whose steps are, in order: "validate", "audit-compat", "audit-marketplace".
        """
        builder_script = (
            self.repo_root
            / "Plugins"
            / "plugin-factory"
            / "skills"
            / "code_quality_review"
            / "plugin-builder"
            / "scripts"
            / "plugin_builder.py"
        )
        builder_script.parent.mkdir(parents=True, exist_ok=True)
        builder_script.write_text("#!/usr/bin/env python3\n", encoding="utf-8")

        plugin_root = self.repo_root / "Plugins" / "third-party" / "demo-plugin"
        plugin_root.mkdir(parents=True, exist_ok=True)

        with patch(
            "ask.commands.plugins.subprocess.run",
            side_effect=[
                subprocess.CompletedProcess(args=[], returncode=0, stdout="PASS: validate\n", stderr=""),
                subprocess.CompletedProcess(args=[], returncode=0, stdout="PASS: compat\n", stderr=""),
                subprocess.CompletedProcess(args=[], returncode=0, stdout="PASS: marketplace\n", stderr=""),
            ],
        ):
            result = harden_plugin(self.repo_root, "Plugins/third-party/demo-plugin")

        self.assertEqual(result.status, "success")
        runs = result.data.get("command_runs", [])
        self.assertEqual(len(runs), 3)
        self.assertEqual(runs[0]["step"], "validate")
        self.assertEqual(runs[1]["step"], "audit-compat")
        self.assertEqual(runs[2]["step"], "audit-marketplace")
        for run in runs:
            self.assertIn(str(builder_script), run["command"])


if __name__ == "__main__":
    unittest.main()
