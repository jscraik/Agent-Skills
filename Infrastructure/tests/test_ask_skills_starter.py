import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Iterator
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from ask.commands.skills import STARTER_ARCHETYPES, _skill_install_intake_decision, list_skills


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
        """Verify visible-only mode excludes plugin lane skills from inventory."""
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
            result = list_skills(REPO_ROOT, visible_only=True)

        mocked_discover.assert_called_once_with(advanced=False)

        self.assertEqual(result.status, "success")
        names = [item["name"] for item in result.data["skills"]]
        self.assertEqual(names, ["coderabbit", "simplify"])
        self.assertNotIn("code-review", names)
        self.assertFalse(result.data.get("advanced_mode"))
        self.assertEqual(result.data.get("inventory_mode"), "visible")
        self.assertTrue(result.data.get("visible_only"))

    def test_visible_only_wins_over_advanced_compat_alias(self) -> None:
        """Verify visible-only mode takes precedence over the advanced alias."""
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

    def test_visible_only_wins_when_category_is_set(self) -> None:
        """Verify visible-only mode stays active when filtering by category."""
        entries = [
            SimpleNamespace(
                name="coderabbit",
                source_dir=REPO_ROOT / "plugins" / "coderabbit" / "skills" / "coderabbit",
                category="Plugins/coderabbit/skills",
                description="router",
            ),
        ]

        with patch("ask.commands.skills.discover_catalog_entries", return_value=entries) as mocked_discover:
            result = list_skills(REPO_ROOT, category="coderabbit", visible_only=True)

        mocked_discover.assert_called_once_with(advanced=False)
        self.assertEqual(result.status, "success")
        self.assertFalse(result.data.get("advanced_mode"))
        self.assertEqual(result.data.get("inventory_mode"), "visible")
        self.assertTrue(result.data.get("visible_only"))
        self.assertEqual(
            result.data["validation_commands"],
            ["./bin/ask skills list --category coderabbit --visible-only --json --robot"],
        )

    def test_install_intake_scans_plugin_owned_canonical_skills(self) -> None:
        """Verify intake detects conflicts with plugin-owned canonical skills."""
        entries = [
            SimpleNamespace(
                name="plugin-builder",
                source_dir=REPO_ROOT
                / "Plugins"
                / "plugin-factory"
                / "skills"
                / "code_quality_review"
                / "plugin-builder",
                category="Plugins/plugin-factory/skills",
                description="plugin builder",
            ),
        ]

        with patch("ask.commands.skills_impl.discover_catalog_entries", return_value=entries) as mocked_discover:
            decision = _skill_install_intake_decision(
                REPO_ROOT,
                "plugin-builder",
                REPO_ROOT / "Skills" / "agent-ops" / "plugin-builder",
            )

        mocked_discover.assert_called_once_with(advanced=True)
        self.assertEqual(decision["schema_version"], "skill-install-intake.v1")
        self.assertEqual(decision["outcome"], "needs_human_choice")
        self.assertEqual(
            decision["local_overlap_candidates"][0]["path"],
            "Plugins/plugin-factory/skills/code_quality_review/plugin-builder",
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

    def test_unknown_archetype_falls_back_to_general(self) -> None:
        """
        An unknown archetype key must resolve to "general" in the result payload.

        Verifies that list_skills with starter=True and an archetype key not present
        in STARTER_ARCHETYPES reports starter_archetype == "general".
        """
        general_names = list(STARTER_ARCHETYPES["general"])
        entries = [
            SimpleNamespace(
                name=name,
                source_dir=REPO_ROOT / "Skills" / "agent-ops" / name,
                category="Skills/agent-ops",
                description=name,
            )
            for name in general_names[:3]
        ]
        with patch("ask.commands.skills.discover_catalog_entries", return_value=entries):
            result = list_skills(REPO_ROOT, starter=True, archetype="nonexistent-archetype", limit=3)

        self.assertEqual(result.status, "success")
        self.assertEqual(result.data["starter_archetype"], "general")
        self.assertTrue(result.data["starter_mode"])

    def test_starter_limit_zero_coerced_to_one(self) -> None:
        """
        A limit of 0 must be coerced to 1, returning exactly one skill.
        """
        entries = [
            SimpleNamespace(
                name="he-plan",
                source_dir=REPO_ROOT / "plugins" / "harness-engineering" / "skills" / "he-plan",
                category="Plugins/harness-engineering/skills",
                description="he-plan",
            ),
            SimpleNamespace(
                name="he-work",
                source_dir=REPO_ROOT / "plugins" / "harness-engineering" / "skills" / "he-work",
                category="Plugins/harness-engineering/skills",
                description="he-work",
            ),
        ]
        with patch("ask.commands.skills.discover_catalog_entries", return_value=entries):
            result = list_skills(REPO_ROOT, starter=True, archetype="delivery", limit=0)

        self.assertEqual(result.status, "success")
        self.assertEqual(result.data["starter_limit"], 1)
        self.assertEqual(len(result.data["skills"]), 1)

    def test_starter_mode_fills_from_remaining_when_archetype_insufficient(self) -> None:
        """
        When fewer archetype-preferred skills are available than the limit, the result
        is padded with non-archetype entries from the catalog in input order.
        """
        entries = [
            SimpleNamespace(
                name="he-plan",
                source_dir=REPO_ROOT / "plugins" / "harness-engineering" / "skills" / "he-plan",
                category="Plugins/harness-engineering/skills",
                description="he-plan",
            ),
            SimpleNamespace(
                name="extra-skill-a",
                source_dir=REPO_ROOT / "Skills" / "agent-ops" / "extra-skill-a",
                category="Skills/agent-ops",
                description="extra-a",
            ),
            SimpleNamespace(
                name="extra-skill-b",
                source_dir=REPO_ROOT / "Skills" / "agent-ops" / "extra-skill-b",
                category="Skills/agent-ops",
                description="extra-b",
            ),
        ]
        # delivery archetype: he-plan, he-work, he-code-review, coding-harness, docs-expert
        # Only he-plan is present; limit=3 => he-plan + extra-skill-a + extra-skill-b
        with patch("ask.commands.skills.discover_catalog_entries", return_value=entries):
            result = list_skills(REPO_ROOT, starter=True, archetype="delivery", limit=3)

        self.assertEqual(result.status, "success")
        names = [item["name"] for item in result.data["skills"]]
        self.assertEqual(len(names), 3)
        self.assertEqual(names[0], "he-plan")
        self.assertIn("extra-skill-a", names)
        self.assertIn("extra-skill-b", names)

    def test_category_filter_forces_advanced_discovery(self) -> None:
        """
        Providing a category argument must call discover_catalog_entries(advanced=True)
        even when advanced=False is the default.
        """
        entries = [
            SimpleNamespace(
                name="docs-expert",
                source_dir=REPO_ROOT / "Skills" / "agent-ops" / "docs-expert",
                category="Skills/agent-ops",
                description="docs",
            ),
        ]
        with patch("ask.commands.skills.discover_catalog_entries", return_value=entries) as mock_discover, \
             patch("ask.commands.skills.handles_report", return_value={"handles": []}):
            result = list_skills(REPO_ROOT, category="agent-ops")

        mock_discover.assert_called_once_with(advanced=True)
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

    def test_visible_only_with_category_preserves_visible_only_mode(self) -> None:
        """
        When both visible_only and category are provided, visible-only mode
        remains active and the category filter narrows that inventory.
        """
        entries = [
            SimpleNamespace(
                name="docs-expert",
                source_dir=REPO_ROOT / "Skills" / "agent-ops" / "docs-expert",
                category="Skills/agent-ops",
                description="docs",
            ),
        ]
        with patch("ask.commands.skills.discover_catalog_entries", return_value=entries) as mock_discover, \
             patch("ask.commands.skills.handles_report", return_value={"handles": []}):
            result = list_skills(REPO_ROOT, category="agent-ops", visible_only=True)

        mock_discover.assert_called_once_with(advanced=False)
        self.assertEqual(result.status, "success")
        self.assertFalse(result.data.get("advanced_mode"))
        self.assertTrue(result.data.get("visible_only"))
        self.assertEqual(result.data.get("inventory_mode"), "visible")

    def test_starter_mode_validation_command_includes_archetype_and_limit(self) -> None:
        """
        Starter mode must emit a validation command containing --archetype and --limit flags.
        """
        entries = [
            SimpleNamespace(
                name="he-plan",
                source_dir=REPO_ROOT / "plugins" / "harness-engineering" / "skills" / "he-plan",
                category="Plugins/harness-engineering/skills",
                description="he-plan",
            ),
        ]
        with patch("ask.commands.skills.discover_catalog_entries", return_value=entries):
            result = list_skills(REPO_ROOT, starter=True, archetype="delivery", limit=5)

        self.assertEqual(result.status, "success")
        validation_cmd = result.data["validation_commands"][0]
        self.assertIn("--archetype", validation_cmd)
        self.assertIn("delivery", validation_cmd)
        self.assertIn("--limit", validation_cmd)
        self.assertIn("5", validation_cmd)
        self.assertIn("starter", validation_cmd)

    def test_all_starter_archetypes_are_non_empty(self) -> None:
        """Every archetype in STARTER_ARCHETYPES must contain at least one skill handle."""
        for name, handles in STARTER_ARCHETYPES.items():
            self.assertGreater(len(handles), 0, f"Archetype '{name}' is unexpectedly empty")

    def test_starter_archetypes_have_no_internal_duplicates(self) -> None:
        """No archetype should list the same skill handle more than once."""
        for name, handles in STARTER_ARCHETYPES.items():
            self.assertEqual(
                len(handles),
                len(set(handles)),
                f"Archetype '{name}' contains duplicate handles: {handles}",
            )

    def test_docs_archetype_present_and_contains_docs_expert(self) -> None:
        """The 'docs' archetype must exist and include docs-expert."""
        self.assertIn("docs", STARTER_ARCHETYPES)
        self.assertIn("docs-expert", STARTER_ARCHETYPES["docs"])

    def test_starter_mode_empty_entries_returns_empty_skills(self) -> None:
        """
        When the catalog is empty, starter mode must return an empty skills list
        with status == "success" (not raise).
        """
        with patch("ask.commands.skills.discover_catalog_entries", return_value=[]):
            result = list_skills(REPO_ROOT, starter=True, archetype="delivery", limit=5)

        self.assertEqual(result.status, "success")
        self.assertEqual(result.data["skills"], [])
        self.assertTrue(result.data["starter_mode"])

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
        # Falls back to the two entries in input order.
        self.assertEqual(names, ["totally-unknown-skill", "another-unknown"])


class TestManifestJsonlSchema(unittest.TestCase):
    """Validate the structure of manifest.jsonl files updated in this PR."""

    MANIFEST_DIR = REPO_ROOT / ".skillsets"
    REQUIRED_TOP_LEVEL_FIELDS: frozenset[str] = frozenset({
        "description",
        "exclusions",
        "id",
        "level",
        "metadata_status",
        "provenance",
        "risk",
        "runtime_visibility",
        "scope",
        "skill_set",
        "source_path",
        "triggers",
    })
    REQUIRED_PROVENANCE_FIELDS: frozenset[str] = frozenset({
        "generator",
        "policy_identity",
        "projection_mode",
        "source_revision",
        "source_sha256",
    })
    EXPECTED_SOURCE_REVISION = "635638fb0"

    def _iter_manifest_records(self) -> Iterator[tuple[Path, int, dict[str, Any]]]:
        """
        Yield parsed JSON records from manifest.jsonl files with location metadata.
        
        Yields:
            tuple: A tuple of (manifest_path, lineno, record) where:
                - manifest_path (Path): The file path to the manifest.jsonl file
                - lineno (int): The line number of the record (1-indexed)
                - record (dict): The parsed JSON record
        """
        import json

        for manifest_path in sorted(self.MANIFEST_DIR.glob("*/manifest.jsonl")):
            with manifest_path.open(encoding="utf-8") as fh:
                for lineno, raw_line in enumerate(fh, start=1):
                    line = raw_line.strip()
                    if not line:
                        continue
                    record = json.loads(line)
                    yield manifest_path, lineno, record

    def test_all_manifest_records_have_required_fields(self) -> None:
        """Every record in every manifest.jsonl must contain the standard top-level fields."""
        for manifest_path, lineno, record in self._iter_manifest_records():
            missing = self.REQUIRED_TOP_LEVEL_FIELDS - record.keys()
            self.assertFalse(
                missing,
                f"{manifest_path}:{lineno} is missing fields: {missing}",
            )

    def test_all_manifest_records_have_required_provenance_fields(self) -> None:
        """Every provenance block must contain the standard provenance sub-fields."""
        for manifest_path, lineno, record in self._iter_manifest_records():
            provenance = record.get("provenance", {})
            missing = self.REQUIRED_PROVENANCE_FIELDS - provenance.keys()
            self.assertFalse(
                missing,
                f"{manifest_path}:{lineno} provenance is missing fields: {missing}",
            )

    def test_all_manifest_records_have_updated_source_revision(self) -> None:
        """Every manifest record's provenance.source_revision must equal the new revision."""
        for manifest_path, lineno, record in self._iter_manifest_records():
            actual = record["provenance"]["source_revision"]
            self.assertEqual(
                actual,
                self.EXPECTED_SOURCE_REVISION,
                f"{manifest_path}:{lineno} has source_revision={actual!r}, "
                f"expected {self.EXPECTED_SOURCE_REVISION!r}",
            )

    def test_all_manifest_records_have_non_empty_id_and_description(self) -> None:
        """Every manifest record must have a non-empty id and description."""
        for manifest_path, lineno, record in self._iter_manifest_records():
            self.assertTrue(
                record.get("id", "").strip(),
                f"{manifest_path}:{lineno} has an empty or missing 'id'",
            )
            self.assertTrue(
                record.get("description", "").strip(),
                f"{manifest_path}:{lineno} has an empty or missing 'description'",
            )

    def test_all_manifest_records_have_non_empty_triggers(self) -> None:
        """
        Validate that every manifest record has a triggers field that is a list.
        """
        for manifest_path, lineno, record in self._iter_manifest_records():
            self.assertIsInstance(
                record.get("triggers"),
                list,
                f"{manifest_path}:{lineno} 'triggers' is not a list",
            )

    def test_manifest_ids_are_unique_within_each_skillset(self) -> None:
        """Within a single manifest.jsonl file, skill ids must be unique."""
        import json

        for manifest_path in sorted(self.MANIFEST_DIR.glob("*/manifest.jsonl")):
            seen_ids: list[str] = []
            with manifest_path.open(encoding="utf-8") as fh:
                for raw_line in fh:
                    line = raw_line.strip()
                    if not line:
                        continue
                    record = json.loads(line)
                    seen_ids.append(record["id"])
            self.assertEqual(
                len(seen_ids),
                len(set(seen_ids)),
                f"{manifest_path} contains duplicate skill ids",
            )

    def test_manifest_source_paths_are_non_empty_strings(self) -> None:
        """Every record's source_path must be a non-empty string."""
        for manifest_path, lineno, record in self._iter_manifest_records():
            source_path = record.get("source_path", "")
            self.assertIsInstance(
                source_path,
                str,
                f"{manifest_path}:{lineno} source_path is not a string",
            )
            self.assertTrue(
                source_path.strip(),
                f"{manifest_path}:{lineno} source_path is empty",
            )


if __name__ == "__main__":
    unittest.main()
