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
            SimpleNamespace(name="ce-work", source_dir=REPO_ROOT / "plugins" / "harness-engineering" / "skills" / "ce-work", category="Plugins/harness-engineering/skills", description="ce-work"),
            SimpleNamespace(name="ce-plan", source_dir=REPO_ROOT / "plugins" / "harness-engineering" / "skills" / "ce-plan", category="Plugins/harness-engineering/skills", description="ce-plan"),
            SimpleNamespace(name="gh-workflow", source_dir=REPO_ROOT / "github" / "gh-workflow", category="github", description="gh"),
            SimpleNamespace(name="docs-expert", source_dir=REPO_ROOT / "product" / "docs" / "docs-expert", category="product/docs", description="docs"),
            SimpleNamespace(name="other-skill", source_dir=REPO_ROOT / "utilities" / "other", category="utilities", description="other"),
        ]

        with patch("ask.commands.skills._canonical_entries", return_value=entries):
            result = list_skills(REPO_ROOT, starter=True, archetype="delivery", limit=3)

        self.assertEqual(result.status, "success")
        self.assertTrue(result.data["starter_mode"])
        self.assertEqual(result.data["starter_archetype"], "delivery")
        names = [item["name"] for item in result.data["skills"]]
        self.assertEqual(names, ["ce-plan", "ce-work", "gh-workflow"])

    def test_default_list_hides_coderabbit_lane_skills(self) -> None:
        """
        Verify default skill listing hides 'lane' skills from coderabbit and does not enable advanced mode.
        
        Mocks canonical entries that include one router skill and several 'lane' skills under Plugins/coderabbit/skills, calls list_skills with default options, and asserts the result contains only the router skill ("coderabbit") and that `advanced_mode` is falsy or absent.
        """
        entries = [
            SimpleNamespace(
                name="coderabbit",
                source_dir=REPO_ROOT / "plugins" / "coderabbit" / "skills" / "coderabbit",
                category="Plugins/coderabbit/skills",
                description="router",
            ),
            SimpleNamespace(
                name="autofix",
                source_dir=REPO_ROOT / "plugins" / "coderabbit" / "skills" / "autofix",
                category="Plugins/coderabbit/skills",
                description="lane",
            ),
            SimpleNamespace(
                name="code-review",
                source_dir=REPO_ROOT / "plugins" / "coderabbit" / "skills" / "code-review",
                category="Plugins/coderabbit/skills",
                description="lane",
            ),
            SimpleNamespace(
                name="simplify",
                source_dir=REPO_ROOT / "plugins" / "coderabbit" / "skills" / "simplify",
                category="Plugins/coderabbit/skills",
                description="lane",
            ),
        ]

        def _discover_with_visibility(*, source: str = "auto", visibility: str = "default"):
            self.assertEqual(source, "auto")
            if visibility == "advanced":
                return entries
            return [entries[0]]

        with patch("ask.commands.skills.discover_skill_entries", side_effect=_discover_with_visibility) as mocked_discover:
            result = list_skills(REPO_ROOT)

        mocked_discover.assert_called_once_with(source="auto", visibility="default")

        self.assertEqual(result.status, "success")
        names = [item["name"] for item in result.data["skills"]]
        self.assertEqual(names, ["coderabbit"])
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
                name="autofix",
                source_dir=REPO_ROOT / "plugins" / "coderabbit" / "skills" / "autofix",
                category="Plugins/coderabbit/skills",
                description="lane",
            ),
        ]

        with patch("ask.commands.skills._canonical_entries", return_value=entries):
            result = list_skills(REPO_ROOT, advanced=True)

        self.assertEqual(result.status, "success")
        names = [item["name"] for item in result.data["skills"]]
        self.assertEqual(names, ["coderabbit", "autofix"])
        self.assertTrue(result.data.get("advanced_mode"))


if __name__ == "__main__":
    unittest.main()
