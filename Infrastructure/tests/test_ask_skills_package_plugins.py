import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from ask.commands.skills_impl import skills_package_verify  # noqa: E402
from helpers.ask_skills_package_fixtures import (  # noqa: E402
    write_gold_quality_skill,
    write_plugin_hooks,
    write_plugin_manifest,
)


class TestAskSkillsPackagePlugins(unittest.TestCase):
    def test_package_verify_accepts_openai_platform_plugin_hook_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            plugin_root = repo_root / "Plugins" / "plugin-fixture"
            skill_dir = plugin_root / "skills" / "packaged-skill"
            write_gold_quality_skill(skill_dir)
            write_plugin_manifest(plugin_root)
            write_plugin_hooks(
                plugin_root,
                {
                    "type": "command",
                    "command": "python3 ${PLUGIN_ROOT}/hooks/session_start.py",
                    "timeout": 5,
                    "statusMessage": "Loading plugin fixture",
                },
            )

            result = skills_package_verify(
                repo_root,
                "Plugins/plugin-fixture/skills/packaged-skill",
            )

        self.assertEqual(result.status, "success", result.data)
        verification = result.data["skill_package_verification"]
        compat = verification["sdk_contract"]["values"]["openai_platform_compat"]
        self.assertEqual(compat["schema_version"], "skills-sdk.openai-platform-compat.v1")
        self.assertEqual(compat["status"], "pass")
        self.assertEqual(compat["target_kind"], "plugin_skill")
        self.assertEqual(compat["blockers"], [])
        self.assertIn("openai_platform_compat", [check["name"] for check in verification["checks"]])

    def test_package_verify_treats_absent_plugin_hooks_as_not_applicable(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            plugin_root = repo_root / "Plugins" / "plugin-fixture"
            skill_dir = plugin_root / "skills" / "packaged-skill"
            write_gold_quality_skill(skill_dir)
            write_plugin_manifest(plugin_root, hooks_value=None)

            result = skills_package_verify(
                repo_root,
                "Plugins/plugin-fixture/skills/packaged-skill",
            )

        self.assertEqual(result.status, "success", result.data)
        verification = result.data["skill_package_verification"]
        compat = verification["sdk_contract"]["values"]["openai_platform_compat"]
        self.assertEqual(compat["status"], "pass")
        self.assertEqual(compat["target_kind"], "plugin_skill")
        self.assertEqual(compat["blockers"], [])
        checks = {check["name"]: check for check in compat["checks"]}
        self.assertEqual(checks["plugin_hooks_manifest_declared"]["status"], "not_applicable")

    def test_package_verify_blocks_unsupported_openai_platform_plugin_hooks(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            plugin_root = repo_root / "Plugins" / "plugin-fixture"
            skill_dir = plugin_root / "skills" / "packaged-skill"
            write_gold_quality_skill(skill_dir)
            write_plugin_manifest(plugin_root, hooks_value="./hooks/wrong.json")
            write_plugin_hooks(
                plugin_root,
                {
                    "type": "prompt",
                    "command": "/Users/jamiecraik/dev/plugin/hooks/session_start.py",
                    "timeoutSec": 5,
                },
            )

            result = skills_package_verify(
                repo_root,
                "Plugins/plugin-fixture/skills/packaged-skill",
            )

        self.assertEqual(result.status, "error")
        verification = result.data["skill_package_verification"]
        self.assertEqual(verification["blockers"][0]["rule_id"], "openai_platform_compat_blocked")
        compat = verification["sdk_contract"]["values"]["openai_platform_compat"]
        rule_ids = {blocker["rule_id"] for blocker in compat["blockers"]}
        self.assertIn("plugin_hooks_manifest_path_invalid", rule_ids)
        self.assertIn("plugin_hooks_unsupported_type", rule_ids)
        self.assertIn("plugin_hooks_timeoutsec_unsupported", rule_ids)

    def test_package_verify_reports_invalid_utf8_plugin_hooks_as_blocker(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            plugin_root = repo_root / "Plugins" / "plugin-fixture"
            skill_dir = plugin_root / "skills" / "packaged-skill"
            write_gold_quality_skill(skill_dir)
            write_plugin_manifest(plugin_root, hooks_value="./hooks/hooks.json")
            hooks_dir = plugin_root / "hooks"
            hooks_dir.mkdir(parents=True, exist_ok=True)
            (hooks_dir / "hooks.json").write_bytes(bytes([123, 255]))

            result = skills_package_verify(
                repo_root,
                "Plugins/plugin-fixture/skills/packaged-skill",
            )

        self.assertEqual(result.status, "error")
        compat = result.data["skill_package_verification"]["sdk_contract"]["values"]["openai_platform_compat"]
        blocker = next(blocker for blocker in compat["blockers"] if blocker["rule_id"] == "plugin_hooks_file_unreadable")
        self.assertEqual(blocker["evidence"]["error"], "UnicodeDecodeError")

    def test_package_verify_rejects_placeholder_hooks_with_local_absolute_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            plugin_root = repo_root / "Plugins" / "plugin-fixture"
            skill_dir = plugin_root / "skills" / "packaged-skill"
            write_gold_quality_skill(skill_dir)
            write_plugin_manifest(plugin_root, hooks_value="./hooks/hooks.json")
            write_plugin_hooks(
                plugin_root,
                {
                    "type": "command",
                    "command": "python3 $" + "{PLUGIN_ROOT}/hooks/session_start.py /Users/jamie/local",
                    "timeout": True,
                },
            )

            result = skills_package_verify(
                repo_root,
                "Plugins/plugin-fixture/skills/packaged-skill",
            )

        self.assertEqual(result.status, "error")
        compat = result.data["skill_package_verification"]["sdk_contract"]["values"]["openai_platform_compat"]
        rule_ids = {blocker["rule_id"] for blocker in compat["blockers"]}
        self.assertIn("plugin_hooks_command_not_portable", rule_ids)
        self.assertIn("plugin_hooks_timeout_missing", rule_ids)


if __name__ == "__main__":
    unittest.main()
