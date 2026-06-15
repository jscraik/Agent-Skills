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

        with patch("ask.commands.skills.discover_catalog_entries", return_value=entries) as mocked_discover:
            result = list_skills(REPO_ROOT, starter=True, archetype="delivery", limit=3)

        mocked_discover.assert_called_once_with(advanced=False)

        self.assertEqual(result.status, "success")
        self.assertTrue(result.data["starter_mode"])
        self.assertEqual(result.data["starter_archetype"], "delivery")
        names = [item["name"] for item in result.data["skills"]]
        self.assertEqual(names, ["he-plan", "he-work", "coding-harness"])

    def test_default_list_uses_full_repo_inventory(self) -> None:
        """
        Verify default skill listing uses full repo inventory.
        
        Mocks canonical entries that include one router skill, one coderabbit lane skill under
        Plugins/coderabbit/skills, and a standalone simplify skill under Skills/agent-ops. Calls
        list_skills with default options and asserts the result includes router, lane, and
        standalone skills from the repo catalog.
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

        with patch("ask.commands.skills.discover_catalog_entries", return_value=entries) as mocked_discover:
            result = list_skills(REPO_ROOT)

        mocked_discover.assert_called_once_with(advanced=True)

        self.assertEqual(result.status, "success")
        names = [item["name"] for item in result.data["skills"]]
        self.assertEqual(names, ["coderabbit", "code-review", "simplify"])
        self.assertTrue(result.data.get("advanced_mode"))
        self.assertEqual(result.data.get("inventory_mode"), "repo")

    def test_visible_only_list_hides_coderabbit_lane_skills(self) -> None:
        entries = [
            SimpleNamespace(
                name="coderabbit",
                source_dir=REPO_ROOT / "plugins" / "coderabbit" / "skills" / "coderabbit",
                category="Plugins/coderabbit/skills",
                description="router",
            ),
            SimpleNamespace(
                name="simplify",
                source_dir=REPO_ROOT / "Skills" / "agent-ops" / "simplify",
                category="Skills/agent-ops",
                description="standalone",
            ),
        ]

        with patch("ask.commands.skills.discover_catalog_entries", return_value=entries) as mocked_discover:
            result = list_skills(REPO_ROOT, visible_only=True)

        mocked_discover.assert_called_once_with(advanced=False)

        self.assertEqual(result.status, "success")
        names = [item["name"] for item in result.data["skills"]]
        self.assertEqual(names, ["coderabbit", "simplify"])
        self.assertFalse(result.data.get("advanced_mode"))
        self.assertEqual(result.data.get("inventory_mode"), "visible")
        self.assertTrue(result.data.get("visible_only"))

    def test_visible_only_wins_over_advanced_compat_alias(self) -> None:
        entries = [
            SimpleNamespace(
                name="coderabbit",
                source_dir=REPO_ROOT / "plugins" / "coderabbit" / "skills" / "coderabbit",
                category="Plugins/coderabbit/skills",
                description="router",
            ),
        ]

        with patch("ask.commands.skills.discover_catalog_entries", return_value=entries) as mocked_discover:
            result = list_skills(REPO_ROOT, advanced=True, visible_only=True)

        mocked_discover.assert_called_once_with(advanced=False)
        self.assertEqual(result.status, "success")
        self.assertFalse(result.data.get("advanced_mode"))
        self.assertEqual(result.data.get("inventory_mode"), "visible")
        self.assertTrue(result.data.get("visible_only"))
        self.assertEqual(
            result.data["validation_commands"],
            ["./bin/ask skills list --visible-only --json --robot"],
        )

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

    def test_starter_archetypes_has_all_expected_keys(self) -> None:
        """STARTER_ARCHETYPES must expose the four documented archetype keys."""
        for key in ("general", "delivery", "review", "docs"):
            with self.subTest(key=key):
                self.assertIn(key, STARTER_ARCHETYPES)
                self.assertIsInstance(STARTER_ARCHETYPES[key], tuple)
                self.assertGreater(len(STARTER_ARCHETYPES[key]), 0)

    def test_starter_archetypes_docs_contains_expected_skills(self) -> None:
        """The 'docs' archetype must list known documentation-oriented handles."""
        docs = STARTER_ARCHETYPES["docs"]
        self.assertIn("docs-expert", docs)
        self.assertIn("agents-md", docs)

    def test_starter_mode_unknown_archetype_falls_back_to_general(self) -> None:
        """
        An unknown archetype key falls back to 'general' for selection and
        is recorded as 'general' in the result data.
        """
        general_handles = list(STARTER_ARCHETYPES["general"])
        entries = [
            SimpleNamespace(
                name=name,
                source_dir=REPO_ROOT / "Skills" / "agent-ops" / name,
                category="Skills/agent-ops",
                description=name,
            )
            for name in general_handles
        ]

        with patch("ask.commands.skills.discover_catalog_entries", return_value=entries):
            result = list_skills(REPO_ROOT, starter=True, archetype="nonexistent-archetype", limit=3)

        self.assertEqual(result.status, "success")
        self.assertTrue(result.data["starter_mode"])
        self.assertEqual(result.data["starter_archetype"], "general")

    def test_starter_mode_limit_zero_coerces_to_one(self) -> None:
        """
        A limit of 0 must be silently promoted to 1 so the result always
        contains at least one skill.
        """
        entries = [
            SimpleNamespace(
                name="he-plan",
                source_dir=REPO_ROOT / "Skills" / "agent-ops" / "he-plan",
                category="Skills/agent-ops",
                description="he-plan",
            ),
            SimpleNamespace(
                name="he-work",
                source_dir=REPO_ROOT / "Skills" / "agent-ops" / "he-work",
                category="Skills/agent-ops",
                description="he-work",
            ),
        ]

        with patch("ask.commands.skills.discover_catalog_entries", return_value=entries):
            result = list_skills(REPO_ROOT, starter=True, archetype="delivery", limit=0)

        self.assertEqual(result.status, "success")
        self.assertEqual(result.data["starter_limit"], 1)
        self.assertLessEqual(len(result.data["skills"]), 1)

    def test_starter_mode_records_starter_limit_in_result(self) -> None:
        """starter_limit in result.data must match the effective clamped limit."""
        entries = [
            SimpleNamespace(
                name=name,
                source_dir=REPO_ROOT / "Skills" / "agent-ops" / name,
                category="Skills/agent-ops",
                description=name,
            )
            for name in ("he-plan", "he-work", "he-code-review")
        ]

        with patch("ask.commands.skills.discover_catalog_entries", return_value=entries):
            result = list_skills(REPO_ROOT, starter=True, archetype="delivery", limit=2)

        self.assertEqual(result.status, "success")
        self.assertEqual(result.data["starter_limit"], 2)
        self.assertLessEqual(len(result.data["skills"]), 2)

    def test_starter_mode_validation_commands_include_archetype_and_limit(self) -> None:
        """validation_commands for starter mode must embed --archetype and --limit."""
        entries = [
            SimpleNamespace(
                name="he-plan",
                source_dir=REPO_ROOT / "Skills" / "agent-ops" / "he-plan",
                category="Skills/agent-ops",
                description="he-plan",
            ),
        ]

        with patch("ask.commands.skills.discover_catalog_entries", return_value=entries):
            result = list_skills(REPO_ROOT, starter=True, archetype="delivery", limit=5)

        cmds = result.data.get("validation_commands", [])
        self.assertTrue(len(cmds) >= 1)
        cmd = cmds[0]
        self.assertIn("--archetype", cmd)
        self.assertIn("delivery", cmd)
        self.assertIn("--limit", cmd)
        self.assertIn("5", cmd)

    def test_category_filter_sets_advanced_discovery_mode(self) -> None:
        """
        Supplying a category token must force advanced (full-repo) discovery
        regardless of other flags, because category search needs the full catalog.
        """
        entries = [
            SimpleNamespace(
                name="docs-expert",
                source_dir=REPO_ROOT / "Skills" / "agent-ops" / "docs-expert",
                category="Skills/agent-ops",
                description="docs",
            ),
        ]

        with patch("ask.commands.skills.discover_catalog_entries", return_value=entries) as mock_disc, \
             patch("ask.commands.skills.handles_report", return_value={"handles": []}):
            result = list_skills(REPO_ROOT, category="agent-ops")

        # Category presence forces advanced=True for discovery
        mock_disc.assert_called_once_with(advanced=True)
        self.assertEqual(result.status, "success")
        self.assertTrue(result.data.get("advanced_mode"))

    def test_category_filter_excludes_non_matching_entries(self) -> None:
        """Entries whose category/name/description do not match the token are excluded."""
        entries = [
            SimpleNamespace(
                name="docs-expert",
                source_dir=REPO_ROOT / "Skills" / "agent-ops" / "docs-expert",
                category="Skills/agent-ops",
                description="docs",
            ),
            SimpleNamespace(
                name="mobile-ui",
                source_dir=REPO_ROOT / "Skills" / "frontend-ui" / "mobile-ui",
                category="Skills/frontend-ui",
                description="mobile",
            ),
        ]

        with patch("ask.commands.skills.discover_catalog_entries", return_value=entries), \
             patch("ask.commands.skills.handles_report", return_value={"handles": []}):
            result = list_skills(REPO_ROOT, category="agent-ops")

        self.assertEqual(result.status, "success")
        names = [item["name"] for item in result.data["skills"]]
        self.assertIn("docs-expert", names)
        self.assertNotIn("mobile-ui", names)

    def test_visible_only_with_category_does_not_apply_visible_filter(self) -> None:
        """
        When both visible_only=True and a category are given, visible_only must be
        ignored because category-scoped searches need the full catalog.
        """
        entries = [
            SimpleNamespace(
                name="docs-expert",
                source_dir=REPO_ROOT / "Skills" / "agent-ops" / "docs-expert",
                category="Skills/agent-ops",
                description="docs",
            ),
        ]

        with patch("ask.commands.skills.discover_catalog_entries", return_value=entries) as mock_disc, \
             patch("ask.commands.skills.handles_report", return_value={"handles": []}):
            result = list_skills(REPO_ROOT, category="agent-ops", visible_only=True)

        # A category token overrides visible_only, so advanced discovery is used
        mock_disc.assert_called_once_with(advanced=True)
        self.assertFalse(result.data.get("visible_only"))

    def test_result_always_contains_policy_identity_string(self) -> None:
        """Every list_skills call must include a non-empty policy_identity string."""
        entries = []

        with patch("ask.commands.skills.discover_catalog_entries", return_value=entries):
            result = list_skills(REPO_ROOT)

        self.assertIn("policy_identity", result.data)
        self.assertIsInstance(result.data["policy_identity"], str)
        self.assertTrue(result.data["policy_identity"].strip())

    def test_skill_path_is_repo_relative_when_inside_repo(self) -> None:
        """Skills whose source_dir is inside repo_root must use a repo-relative path."""
        source_dir = REPO_ROOT / "Skills" / "agent-ops" / "docs-expert"
        entries = [
            SimpleNamespace(
                name="docs-expert",
                source_dir=source_dir,
                category="Skills/agent-ops",
                description="docs",
            ),
        ]

        with patch("ask.commands.skills.discover_catalog_entries", return_value=entries):
            result = list_skills(REPO_ROOT)

        self.assertEqual(result.status, "success")
        self.assertEqual(len(result.data["skills"]), 1)
        path_value = result.data["skills"][0]["path"]
        # Must be relative, not absolute
        self.assertFalse(path_value.startswith("/"), f"Expected relative path, got: {path_value}")
        self.assertIn("docs-expert", path_value)

    def test_empty_entry_list_returns_success_with_empty_skills(self) -> None:
        """An empty catalog produces a success result with an empty skills list."""
        with patch("ask.commands.skills.discover_catalog_entries", return_value=[]):
            result = list_skills(REPO_ROOT)

        self.assertEqual(result.status, "success")
        self.assertEqual(result.data["skills"], [])

    def test_starter_mode_with_no_archetype_matches_fills_from_remaining(self) -> None:
        """
        When none of the archetype-preferred names appear in entries, _starter_entries
        must still fill up to limit from the remaining entries in input order.
        """
        entries = [
            SimpleNamespace(
                name="totally-unknown-skill",
                source_dir=REPO_ROOT / "Skills" / "agent-ops" / "totally-unknown-skill",
                category="Skills/agent-ops",
                description="unknown",
            ),
            SimpleNamespace(
                name="another-unknown",
                source_dir=REPO_ROOT / "Skills" / "agent-ops" / "another-unknown",
                category="Skills/agent-ops",
                description="unknown2",
            ),
        ]

        with patch("ask.commands.skills.discover_catalog_entries", return_value=entries):
            result = list_skills(REPO_ROOT, starter=True, archetype="delivery", limit=2)

        self.assertEqual(result.status, "success")
        names = [item["name"] for item in result.data["skills"]]
        # Falls back to the two entries in input order
        self.assertEqual(names, ["totally-unknown-skill", "another-unknown"])


if __name__ == "__main__":
    unittest.main()
