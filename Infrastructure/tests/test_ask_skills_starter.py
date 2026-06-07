import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from ask.commands.skills import STARTER_ARCHETYPES, list_skills


class TestAskSkillsStarter(unittest.TestCase):
    def test_starter_mode_returns_deterministic_subset(self) -> None:
        """
        Verify starter-mode skill listing returns a deterministic, archetype-filtered subset.
        
        Patches `discover_catalog_entries` to a fixed set of catalog entries, calls `list_skills(REPO_ROOT, starter=True, archetype="delivery", limit=3)`, and asserts the result indicates starter mode with `starter_archetype == "delivery"` and that the returned skill names are exactly ["he-plan", "he-work", "coding-harness"] in that order.
        """
        entries = [
            SimpleNamespace(name="he-work", source_dir=REPO_ROOT / "plugins" / "harness-engineering" / "skills" / "he-work", category="Plugins/harness-engineering/skills", description="he-work"),
            SimpleNamespace(name="he-plan", source_dir=REPO_ROOT / "plugins" / "harness-engineering" / "skills" / "he-plan", category="Plugins/harness-engineering/skills", description="he-plan"),
            SimpleNamespace(name="coding-harness", source_dir=REPO_ROOT / "Skills" / "agent-ops" / "coding-harness", category="Skills/agent-ops", description="harness"),
            SimpleNamespace(name="docs-expert", source_dir=REPO_ROOT / "product" / "docs" / "docs-expert", category="product/docs", description="docs"),
            SimpleNamespace(name="other-skill", source_dir=REPO_ROOT / "utilities" / "other", category="utilities", description="other"),
        ]

        with patch("ask.commands.skills.discover_catalog_entries", return_value=entries):
            result = list_skills(REPO_ROOT, starter=True, archetype="delivery", limit=3)

        self.assertEqual(result.status, "success")
        self.assertTrue(result.data["starter_mode"])
        self.assertEqual(result.data["starter_archetype"], "delivery")
        names = [item["name"] for item in result.data["skills"]]
        self.assertEqual(names, ["he-plan", "he-work", "coding-harness"])

    def test_default_list_hides_coderabbit_lane_skills(self) -> None:
        """
        Verify default skill listing hides plugin lane skills while preserving standalone simplify.
        
        Mocks canonical entries that include one router skill, one coderabbit lane skill under
        Plugins/coderabbit/skills, and a standalone simplify skill under Skills/agent-ops. Calls
        list_skills with default options and asserts the result includes router + standalone simplify
        (while hidden plugin lanes are excluded).
        """
        entries = [
            SimpleNamespace(
                name="coderabbit",
                source_dir=REPO_ROOT / "plugins" / "coderabbit" / "skills" / "coderabbit",
                category="Plugins/coderabbit/skills",
                description="router",
            ),
            SimpleNamespace(
                name="code-review",
                source_dir=REPO_ROOT / "plugins" / "coderabbit" / "skills" / "code-review",
                category="Plugins/coderabbit/skills",
                description="lane",
            ),
            SimpleNamespace(
                name="simplify",
                source_dir=REPO_ROOT / "Skills" / "agent-ops" / "simplify",
                category="Skills/agent-ops",
                description="standalone",
            ),
        ]

        filtered = [entries[0], entries[2]]

        with patch("ask.commands.skills.discover_catalog_entries", return_value=filtered) as mocked_discover:
            result = list_skills(REPO_ROOT)

        mocked_discover.assert_called_once_with(advanced=False)

        self.assertEqual(result.status, "success")
        names = [item["name"] for item in result.data["skills"]]
        self.assertEqual(names, ["coderabbit", "simplify"])
        self.assertFalse(result.data.get("advanced_mode"))

    def test_advanced_list_includes_coderabbit_lane_skills(self) -> None:
        entries = [
            SimpleNamespace(
                name="coderabbit",
                source_dir=REPO_ROOT / "plugins" / "coderabbit" / "skills" / "coderabbit",
                category="Plugins/coderabbit/skills",
                description="router",
            ),
            SimpleNamespace(
                name="code-review",
                source_dir=REPO_ROOT / "plugins" / "coderabbit" / "skills" / "code-review",
                category="Plugins/coderabbit/skills",
                description="lane",
            ),
        ]

        with patch("ask.commands.skills.discover_catalog_entries", return_value=entries):
            result = list_skills(REPO_ROOT, advanced=True)

        self.assertEqual(result.status, "success")
        names = [item["name"] for item in result.data["skills"]]
        self.assertEqual(names, ["coderabbit", "code-review"])
        self.assertTrue(result.data.get("advanced_mode"))

    def test_harness_engineering_category_includes_owned_command_handles(self) -> None:
        entries = [
            SimpleNamespace(
                name="harness-engineering",
                source_dir=REPO_ROOT / ".agents" / "skills" / "harness-engineering",
                category=".agents/skills",
                description="Route Harness Engineering work",
            ),
            SimpleNamespace(
                name="he-work",
                source_dir=REPO_ROOT / ".agents" / "skills" / "he-work",
                category=".agents/skills",
                description="Command-surface handle",
            ),
            SimpleNamespace(
                name="docs-expert",
                source_dir=REPO_ROOT / "Skills" / "agent-ops" / "docs-expert",
                category="Skills/agent-ops",
                description="Docs skill",
            ),
        ]
        handles_report = {
            "handles": [
                {"handle": "harness-engineering", "owner": "harness-engineering"},
                {"handle": "he-work", "owner": "harness-engineering"},
            ]
        }

        with patch("ask.commands.skills.discover_catalog_entries", return_value=entries), patch(
            "ask.commands.skills.handles_report",
            return_value=handles_report,
        ):
            result = list_skills(REPO_ROOT, category="harness-engineering")

        self.assertEqual(result.status, "success")
        names = [item["name"] for item in result.data["skills"]]
        self.assertEqual(names, ["harness-engineering", "he-work"])

    def test_starter_archetypes_do_not_reference_retired_he_review_handle(self) -> None:
        all_starter_handles = {handle for handles in STARTER_ARCHETYPES.values() for handle in handles}
        self.assertNotIn("he-review", all_starter_handles)
        self.assertIn("he-code-review", STARTER_ARCHETYPES["delivery"])
        self.assertIn("he-code-review", STARTER_ARCHETYPES["review"])


if __name__ == "__main__":
    unittest.main()
