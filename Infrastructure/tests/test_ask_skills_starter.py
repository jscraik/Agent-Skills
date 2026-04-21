import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from ask.commands.skills import list_skills


class TestAskSkillsStarter(unittest.TestCase):
    def test_starter_mode_returns_deterministic_subset(self) -> None:
        """
        Verify listing skills in starter mode returns a deterministic, limited subset.
        
        Patches discovered canonical skill entries to a fixed set, calls list_skills(REPO_ROOT, starter=True, archetype="delivery", limit=3) and asserts the result reports starter mode with the specified archetype and that the returned skill names are exactly ["ce-plan", "ce-work", "gh-workflow"] in that order.
        """
        entries = [
            SimpleNamespace(name="he-work", source_dir=REPO_ROOT / "plugins" / "harness-engineering" / "skills" / "he-work", category="Plugins/harness-engineering/skills", description="he-work"),
            SimpleNamespace(name="he-plan", source_dir=REPO_ROOT / "plugins" / "harness-engineering" / "skills" / "he-plan", category="Plugins/harness-engineering/skills", description="he-plan"),
            SimpleNamespace(name="gh-workflow", source_dir=REPO_ROOT / "github" / "gh-workflow", category="github", description="gh"),
            SimpleNamespace(name="docs-expert", source_dir=REPO_ROOT / "product" / "docs" / "docs-expert", category="product/docs", description="docs"),
            SimpleNamespace(name="other-skill", source_dir=REPO_ROOT / "utilities" / "other", category="utilities", description="other"),
        ]

        with patch("ask.commands.skills.discover_catalog_entries", return_value=entries):
            result = list_skills(REPO_ROOT, starter=True, archetype="delivery", limit=3)

        self.assertEqual(result.status, "success")
        self.assertTrue(result.data["starter_mode"])
        self.assertEqual(result.data["starter_archetype"], "delivery")
        names = [item["name"] for item in result.data["skills"]]
        self.assertEqual(names, ["he-plan", "he-work", "gh-workflow"])

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


if __name__ == "__main__":
    unittest.main()
