import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

EXPECTED_PLUGIN_SKILLS = {
    "harness-engineering": {
        "he-brainstorm",
        "he-code-review",
        "he-compound",
        "he-compound-refresh",
        "he-deepen-plan",
        "he-deepen-spec",
        "he-fix-bugs",
        "he-ideate",
        "he-improve",
        "he-plan",
        "he-prune-branches",
        "he-refine",
        "he-reliability-review",
        "he-router",
        "he-spec",
        "he-tdd",
        "he-technical-review",
        "he-work",
    },
    "plugin-factory": {
        "plugin-builder",
        "plugin-creator",
        "plugin-factory-router",
        "plugin-installer",
        "plugin-router",
    },
    "skill-factory": {
        "skill-builder",
        "skill-creator",
        "skill-factory-router",
        "skill-installer",
    },
}

EXPECTED_MARKETPLACE_SOURCE_PATHS = {
    "harness-engineering": "./Plugins/harness-engineering",
    "plugin-factory": "./Plugins/plugin-factory",
    "skill-factory": "./Plugins/skill-factory",
}

EXPECTED_PLUGIN_KEYWORDS = {
    "plugin-factory": {
        "plugin-factory-router",
        "plugin-router",
        "plugin-builder",
        "plugin-creator",
        "plugin-installer",
    },
    "skill-factory": {
        "skill-factory-router",
        "skill-builder",
        "skill-creator",
        "skill-installer",
    },
}


class LocalPluginPickerSurfaceTests(unittest.TestCase):
    def test_local_marketplace_lists_only_expected_local_plugins(self) -> None:
        marketplace_path = REPO_ROOT / "Plugins" / "marketplace.json"
        payload = json.loads(marketplace_path.read_text(encoding="utf-8"))
        names = {
            item["name"]
            for item in payload.get("plugins", [])
            if isinstance(item, dict) and isinstance(item.get("name"), str)
        }
        self.assertEqual(names, set(EXPECTED_PLUGIN_SKILLS))

    def test_local_plugins_use_canonical_marketplace_source_paths(self) -> None:
        marketplace_path = REPO_ROOT / "Plugins" / "marketplace.json"
        payload = json.loads(marketplace_path.read_text(encoding="utf-8"))
        by_name = {
            item["name"]: item
            for item in payload.get("plugins", [])
            if isinstance(item, dict) and isinstance(item.get("name"), str)
        }

        for plugin_name, expected_path in EXPECTED_MARKETPLACE_SOURCE_PATHS.items():
            plugin = by_name[plugin_name]
            self.assertEqual(
                plugin.get("source", {}).get("path"),
                expected_path,
                f"{plugin_name} should use the canonical ./Plugins/<name> marketplace source path",
            )

    def test_local_plugins_use_first_level_skills_root(self) -> None:
        for plugin_name in EXPECTED_PLUGIN_SKILLS:
            manifest_path = REPO_ROOT / "Plugins" / plugin_name / ".codex-plugin" / "plugin.json"
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(
                payload.get("skills"),
                "./skills/",
                f"{plugin_name} should expose plugin skills from ./skills/",
            )

    def test_local_plugins_expose_all_expected_skills_at_first_level(self) -> None:
        for plugin_name, expected_skill_names in EXPECTED_PLUGIN_SKILLS.items():
            skills_root = REPO_ROOT / "Plugins" / plugin_name / "skills"
            direct_skill_names = {
                child.name
                for child in skills_root.iterdir()
                if child.is_dir() and (child / "SKILL.md").exists()
            }
            self.assertEqual(
                direct_skill_names,
                expected_skill_names,
                f"{plugin_name} first-level plugin picker surface drifted",
            )

    def test_local_plugins_expose_openai_metadata_for_first_level_skills(self) -> None:
        for plugin_name, expected_skill_names in EXPECTED_PLUGIN_SKILLS.items():
            skills_root = REPO_ROOT / "Plugins" / plugin_name / "skills"
            missing = []
            for skill_name in sorted(expected_skill_names):
                skill_dir = skills_root / skill_name
                metadata_path = skill_dir / "agents" / "openai.yaml"
                if not metadata_path.exists():
                    missing.append(str(metadata_path.relative_to(REPO_ROOT)))
            self.assertEqual([], missing, f"{plugin_name} is missing skill-level OpenAI metadata")

    def test_local_plugin_manifests_describe_visible_skill_surface(self) -> None:
        for plugin_name, expected_keywords in EXPECTED_PLUGIN_KEYWORDS.items():
            manifest_path = REPO_ROOT / "Plugins" / plugin_name / ".codex-plugin" / "plugin.json"
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            keywords = set(payload.get("keywords", []))
            self.assertTrue(
                expected_keywords.issubset(keywords),
                f"{plugin_name} manifest keywords should include the visible skill surface",
            )
            self.assertFalse(
                {"skill-refactor", "skillify"} & keywords,
                f"{plugin_name} manifest should not advertise removed or non-visible skills",
            )


if __name__ == "__main__":
    unittest.main()
