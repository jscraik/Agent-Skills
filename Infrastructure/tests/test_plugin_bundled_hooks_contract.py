import json
import runpy
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PLUGIN_BUILDER = (
    REPO_ROOT
    / "Plugins"
    / "plugin-factory"
    / "skills"
    / "code_quality_review"
    / "plugin-builder"
    / "scripts"
    / "plugin_builder.pyw"
)
PLUGIN_CREATOR = (
    REPO_ROOT
    / "Plugins"
    / "plugin-factory"
    / "skills"
    / "scaffolding_templates"
    / "plugin-creator"
    / "scripts"
    / "create_basic_plugin.pyw"
)
FACTORY_PLUGIN_ROOTS = (
    REPO_ROOT / "Plugins" / "plugin-factory",
    REPO_ROOT / "Plugins" / "skill-factory",
)


builder = runpy.run_path(str(PLUGIN_BUILDER))
creator = runpy.run_path(str(PLUGIN_CREATOR))


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def minimal_manifest(name: str = "demo-plugin") -> dict:
    return {
        "name": name,
        "version": "0.1.0",
        "description": "Demo plugin.",
        "interface": {
            "displayName": "Demo Plugin",
            "defaultPrompt": "Use demo plugin.",
        },
    }


def hooks_payload(command: str = "python3 ${PLUGIN_ROOT}/hooks/session_start.py") -> dict:
    return {
        "hooks": {
            "SessionStart": [
                {
                    "hooks": [
                        {
                            "type": "command",
                            "command": command,
                            "timeout": 10,
                        }
                    ]
                }
            ]
        }
    }


class PluginBundledHooksContractTests(unittest.TestCase):
    def test_creator_declares_default_hooks_path(self) -> None:
        payload = creator["build_plugin_json"](
            "demo-plugin",
            enabled_surfaces={"hooks": True},
        )
        self.assertEqual("./hooks/hooks.json", payload["hooks"])

    def test_builder_declares_default_hooks_path(self) -> None:
        payload = builder["build_plugin_json"](
            "demo-plugin",
            {"hooks": True},
        )
        self.assertEqual("./hooks/hooks.json", payload["hooks"])

    def test_default_hooks_file_validates_without_manifest_field(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            plugin_root = Path(tmp) / "demo-plugin"
            manifest = minimal_manifest()
            write_json(plugin_root / ".codex-plugin" / "plugin.json", manifest)
            write_json(plugin_root / "hooks" / "hooks.json", hooks_payload())

            failures = builder["_check_plugin_manifest"](
                plugin_root / ".codex-plugin" / "plugin.json"
            )

        self.assertEqual([], failures)

    def test_manifest_hook_path_array_validates_each_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            plugin_root = Path(tmp) / "demo-plugin"
            manifest = minimal_manifest()
            manifest["hooks"] = ["./hooks/session.json", "./hooks/stop.json"]
            write_json(plugin_root / ".codex-plugin" / "plugin.json", manifest)
            write_json(plugin_root / "hooks" / "session.json", hooks_payload())
            write_json(plugin_root / "hooks" / "stop.json", {"hooks": {"Stop": []}})

            failures = builder["_check_plugin_manifest"](
                plugin_root / ".codex-plugin" / "plugin.json"
            )

        self.assertEqual([], failures)

    def test_inline_manifest_hooks_validate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            plugin_root = Path(tmp) / "demo-plugin"
            manifest = minimal_manifest()
            manifest["hooks"] = hooks_payload()
            write_json(plugin_root / ".codex-plugin" / "plugin.json", manifest)

            failures = builder["_check_plugin_manifest"](
                plugin_root / ".codex-plugin" / "plugin.json"
            )

        self.assertEqual([], failures)

    def test_hook_command_rejects_local_absolute_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            plugin_root = Path(tmp) / "demo-plugin"
            manifest = minimal_manifest()
            manifest["hooks"] = "./hooks/hooks.json"
            write_json(plugin_root / ".codex-plugin" / "plugin.json", manifest)
            write_json(
                plugin_root / "hooks" / "hooks.json",
                hooks_payload("python3 /Users/jamie/dev/plugin/hooks/session_start.py"),
            )

            failures = builder["_check_plugin_manifest"](
                plugin_root / ".codex-plugin" / "plugin.json"
            )

        self.assertTrue(
            any("local absolute path" in failure for failure in failures),
            failures,
        )

    def test_hook_command_rejects_timeout_sec_field(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            plugin_root = Path(tmp) / "demo-plugin"
            manifest = minimal_manifest()
            manifest["hooks"] = "./hooks/hooks.json"
            write_json(plugin_root / ".codex-plugin" / "plugin.json", manifest)
            payload = hooks_payload()
            payload["hooks"]["SessionStart"][0]["hooks"][0].pop("timeout")
            payload["hooks"]["SessionStart"][0]["hooks"][0]["timeoutSec"] = 10
            write_json(plugin_root / "hooks" / "hooks.json", payload)

            failures = builder["_check_plugin_manifest"](
                plugin_root / ".codex-plugin" / "plugin.json"
            )

        self.assertTrue(
            any("timeoutSec is not a Codex hook field" in failure for failure in failures),
            failures,
        )

    def test_factory_plugins_declare_default_bundled_hooks(self) -> None:
        for plugin_root in FACTORY_PLUGIN_ROOTS:
            with self.subTest(plugin=plugin_root.name):
                manifest = json.loads(
                    (plugin_root / ".codex-plugin" / "plugin.json").read_text(
                        encoding="utf-8"
                    )
                )

                self.assertEqual("./hooks/hooks.json", manifest.get("hooks"))

    def test_factory_plugin_hooks_validate(self) -> None:
        for plugin_root in FACTORY_PLUGIN_ROOTS:
            with self.subTest(plugin=plugin_root.name):
                failures = builder["_check_plugin_manifest"](
                    plugin_root / ".codex-plugin" / "plugin.json"
                )

                self.assertEqual([], failures)

    def test_factory_plugin_hooks_use_scoped_command_paths(self) -> None:
        for plugin_root in FACTORY_PLUGIN_ROOTS:
            with self.subTest(plugin=plugin_root.name):
                payload = json.loads(
                    (plugin_root / "hooks" / "hooks.json").read_text(
                        encoding="utf-8"
                    )
                )
                command_hook = payload["hooks"]["SessionStart"][0]["hooks"][0]

                self.assertEqual("command", command_hook["type"])
                self.assertIn("${PLUGIN_ROOT}", command_hook["command"])
                self.assertIn("timeout", command_hook)
                self.assertNotIn("timeoutSec", command_hook)

    def test_factory_session_start_scripts_emit_context(self) -> None:
        scripts = (
            (
                REPO_ROOT
                / "Plugins"
                / "plugin-factory"
                / "hooks"
                / "session_start_contract.py",
                ("hooks/hooks.json", "timeout", "plugin_hooks"),
            ),
            (
                REPO_ROOT
                / "Plugins"
                / "skill-factory"
                / "hooks"
                / "session_start_routing.py",
                ("skill-creator", "skill-builder", "skill-refactor"),
            ),
        )
        for script, expected_fragments in scripts:
            with self.subTest(script=script.name):
                result = subprocess.run(
                    [sys.executable, str(script)],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                payload = json.loads(result.stdout)
                context = payload["hookSpecificOutput"]["additionalContext"]

                self.assertTrue(payload["continue"])
                self.assertTrue(payload["suppressOutput"])
                for expected_fragment in expected_fragments:
                    self.assertIn(expected_fragment, context)


if __name__ == "__main__":
    unittest.main()
