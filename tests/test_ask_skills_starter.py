import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "lib"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from ask.commands.skills import list_skills


class TestAskSkillsStarter(unittest.TestCase):
    def test_starter_mode_returns_deterministic_subset(self) -> None:
        """
        Verify that listing skills in starter mode yields a deterministic, limited subset.
        
        Patches the canonical entries to a fixed set and calls list_skills(REPO_ROOT, starter=True, archetype="delivery", limit=3). Asserts the call succeeds, starter mode and archetype are reported, and the returned skill names are exactly ["ce-plan", "ce-work", "gh-workflow"] in that order.
        """
        entries = [
            SimpleNamespace(name="ce-work", source_dir=REPO_ROOT / "plugins" / "harness-engineering" / "skills" / "ce-work", category="plugins/harness-engineering/skills", description="ce-work"),
            SimpleNamespace(name="ce-plan", source_dir=REPO_ROOT / "plugins" / "harness-engineering" / "skills" / "ce-plan", category="plugins/harness-engineering/skills", description="ce-plan"),
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


if __name__ == "__main__":
    unittest.main()
