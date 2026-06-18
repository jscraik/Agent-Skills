"""
Structural and content validation tests for files changed in this PR.

Covers:
  - All .skillsets/*/manifest.jsonl files: source_revision bumped to "635638fb0",
    old revision "83f7ab9ed" must not be present.
  - .skillsets/command-surface.json: source_revision updated to "0e372d956",
    handle_count updated to 111; generated wrapper counts are no longer emitted.
  - .skillsets/agent-ops/manifest.jsonl: goal-governor entry has revised
    description and triggers; session-workflow-miner is a new skill entry.
  - Docs/goals/jsc-351-agent-skills-codex-abi-conformance/state.yaml: new file
    with required top-level keys, version 2, and in_progress status.
  - .harness/memory/LEARNINGS.md: new 2026-05-24 entries appended without
    removing existing content.
"""
import json
import re
import unittest
from pathlib import Path
from typing import Any, ClassVar

import yaml  # PyYAML is available in the repo CI environment

REPO_ROOT = Path(__file__).resolve().parents[2]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SKILLSET_MANIFEST_PATHS = sorted(REPO_ROOT.glob(".skillsets/*/manifest.jsonl"))

COMMAND_SURFACE_PATH = REPO_ROOT / ".skillsets" / "command-surface.json"

STATE_YAML_PATH = (
    REPO_ROOT
    / "Docs"
    / "goals"
    / "jsc-351-agent-skills-codex-abi-conformance"
    / "state.yaml"
)

LEARNINGS_MD_PATH = REPO_ROOT / ".harness" / "memory" / "LEARNINGS.md"

# The source_revision bumped to this value for all manifest.jsonl files in
# this PR.
NEW_MANIFEST_REVISION = "635638fb0"

# The old source_revision that must no longer appear in any manifest.
OLD_MANIFEST_REVISION = "83f7ab9ed"

# The source_revision used inside command-surface.json (different from manifests).
NEW_COMMAND_SURFACE_REVISION = "0e372d956"

# Expected counts in command-surface.json after the new session-workflow-miner
# skill was added.
EXPECTED_HANDLE_COUNT = 111
EXPECTED_GENERATED_HANDLE_COUNT = 105

# Git short-hash pattern (7+ hex chars).
_REVISION_PATTERN = re.compile(r"^[0-9a-f]{7,}", re.IGNORECASE)


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    """
    Load and parse a JSON Lines (JSONL) file into a list of JSON objects.
    
    Empty or whitespace-only lines are ignored; each non-empty line is parsed as a separate JSON object.
    
    Parameters:
        path (Path): Path to the JSONL file to read (UTF-8 encoded).
    
    Returns:
        list[dict[str, Any]]: List of parsed JSON objects, in file order.
    
    Raises:
        AssertionError: If a non-empty line contains invalid JSON; the message includes the offending line number and file path.
    """
    records: list[dict[str, Any]] = []
    with open(path, encoding="utf-8") as fh:
        for lineno, raw in enumerate(fh, start=1):
            raw = raw.strip()
            if not raw:
                continue
            try:
                records.append(json.loads(raw))
            except json.JSONDecodeError as exc:
                raise AssertionError(
                    f"Invalid JSON on line {lineno} of {path}: {exc}"
                ) from exc
    return records


# ---------------------------------------------------------------------------
# Manifest source_revision bump: "83f7ab9ed" -> "635638fb0"
# ---------------------------------------------------------------------------


class TestManifestRevisionBump(unittest.TestCase):
    """All manifest.jsonl files must use the new source_revision "635638fb0"."""

    def _assert_all_revisions(self, path: Path, expected: str) -> None:
        """
        Assert every JSONL record in the given file has `provenance.source_revision` equal to the expected revision.
        
        Parameters:
            path (Path): Path to a JSONL file containing manifest records.
            expected (str): The expected `provenance.source_revision` value for each record.
        """
        records = _load_jsonl(path)
        for rec in records:
            rev = rec.get("provenance", {}).get("source_revision", "")
            with self.subTest(file=path.name, id=rec.get("id", "?")):
                self.assertEqual(
                    rev,
                    expected,
                    f"Entry '{rec.get('id')}' in {path.name} has revision "
                    f"'{rev}', expected '{expected}'",
                )

    def test_agent_ops_revision_is_new(self) -> None:
        self._assert_all_revisions(
            REPO_ROOT / ".skillsets" / "agent-ops" / "manifest.jsonl",
            NEW_MANIFEST_REVISION,
        )

    def test_backend_platform_revision_is_new(self) -> None:
        self._assert_all_revisions(
            REPO_ROOT / ".skillsets" / "backend-platform" / "manifest.jsonl",
            NEW_MANIFEST_REVISION,
        )

    def test_content_publishing_revision_is_new(self) -> None:
        """
        Assert every record in the content-publishing manifest uses the expected new manifest revision (`NEW_MANIFEST_REVISION`).
        """
        self._assert_all_revisions(
            REPO_ROOT / ".skillsets" / "content-publishing" / "manifest.jsonl",
            NEW_MANIFEST_REVISION,
        )

    def test_frontend_ui_revision_is_new(self) -> None:
        self._assert_all_revisions(
            REPO_ROOT / ".skillsets" / "frontend-ui" / "manifest.jsonl",
            NEW_MANIFEST_REVISION,
        )

    def test_harness_engineering_revision_is_new(self) -> None:
        """
        Assert that every entry in the harness-engineering manifest uses the expected new source_revision.
        """
        self._assert_all_revisions(
            REPO_ROOT / ".skillsets" / "harness-engineering" / "manifest.jsonl",
            NEW_MANIFEST_REVISION,
        )

    def test_mobile_native_revision_is_new(self) -> None:
        """
        Verify every record in .skillsets/mobile-native/manifest.jsonl has provenance.source_revision equal to NEW_MANIFEST_REVISION.
        
        This test fails if any record in the mobile-native manifest uses a different `provenance.source_revision`.
        """
        self._assert_all_revisions(
            REPO_ROOT / ".skillsets" / "mobile-native" / "manifest.jsonl",
            NEW_MANIFEST_REVISION,
        )

    def test_plugin_factory_revision_is_new(self) -> None:
        """
        Assert that every record in the plugin-factory manifest has the expected new provenance source_revision.
        
        Uses the test helper to load and check all JSONL records in .skillsets/plugin-factory/manifest.jsonl and verifies each record's `provenance.source_revision` equals NEW_MANIFEST_REVISION.
        """
        self._assert_all_revisions(
            REPO_ROOT / ".skillsets" / "plugin-factory" / "manifest.jsonl",
            NEW_MANIFEST_REVISION,
        )

    def test_product_strategy_revision_is_new(self) -> None:
        self._assert_all_revisions(
            REPO_ROOT / ".skillsets" / "product-strategy" / "manifest.jsonl",
            NEW_MANIFEST_REVISION,
        )

    def test_security_ops_revision_is_new(self) -> None:
        """
        Assert that every record in .skillsets/security-ops/manifest.jsonl has provenance.source_revision equal to NEW_MANIFEST_REVISION.
        """
        self._assert_all_revisions(
            REPO_ROOT / ".skillsets" / "security-ops" / "manifest.jsonl",
            NEW_MANIFEST_REVISION,
        )

    def test_skill_factory_revision_is_new(self) -> None:
        """
        Assert that every record in the .skillsets/skill-factory/manifest.jsonl file has the expected new manifest revision.
        """
        self._assert_all_revisions(
            REPO_ROOT / ".skillsets" / "skill-factory" / "manifest.jsonl",
            NEW_MANIFEST_REVISION,
        )

    def test_no_manifest_uses_old_revision(self) -> None:
        """No entry in any manifest should still reference the old revision."""
        for manifest_path in SKILLSET_MANIFEST_PATHS:
            records = _load_jsonl(manifest_path)
            for rec in records:
                rev = rec.get("provenance", {}).get("source_revision", "")
                with self.subTest(file=manifest_path.name, id=rec.get("id", "?")):
                    self.assertNotEqual(
                        rev,
                        OLD_MANIFEST_REVISION,
                        f"Entry '{rec.get('id')}' in {manifest_path.name} "
                        f"still uses old revision '{OLD_MANIFEST_REVISION}'",
                    )

    def test_all_manifests_use_consistent_single_revision(self) -> None:
        """Every manifest must use the same single source_revision value."""
        revisions: set[str] = set()
        for manifest_path in SKILLSET_MANIFEST_PATHS:
            records = _load_jsonl(manifest_path)
            for rec in records:
                rev = rec.get("provenance", {}).get("source_revision", "")
                if rev:
                    revisions.add(rev)
        self.assertEqual(
            revisions,
            {NEW_MANIFEST_REVISION},
            f"Expected only '{NEW_MANIFEST_REVISION}' across all manifests, "
            f"found: {sorted(revisions)}",
        )

    def test_new_revision_matches_git_hash_pattern(self) -> None:
        """The new revision string itself must look like a valid git short hash."""
        self.assertRegex(
            NEW_MANIFEST_REVISION,
            _REVISION_PATTERN,
            f"'{NEW_MANIFEST_REVISION}' does not match expected git-hash pattern",
        )


# ---------------------------------------------------------------------------
# agent-ops manifest: goal-governor entry changes
# ---------------------------------------------------------------------------


class TestGoalGovernorEntryUpdated(unittest.TestCase):
    """The goal-governor skill in agent-ops/manifest.jsonl must reflect PR changes."""

    _MANIFEST_PATH = REPO_ROOT / ".skillsets" / "agent-ops" / "manifest.jsonl"

    def _get_goal_governor(self) -> dict[str, Any]:
        """
        Retrieve the 'goal-governor' entry from the agent-ops manifest.
        
        Searches the JSONL records loaded from the manifest path and returns the record whose `id` is "goal-governor".
        If no such entry is found the test fails via an assertion.
        
        Returns:
            dict[str, Any]: The manifest record for "goal-governor".
        """
        records = _load_jsonl(self._MANIFEST_PATH)
        entry = next((r for r in records if r.get("id") == "goal-governor"), None)
        self.assertIsNotNone(entry, "goal-governor entry not found in agent-ops manifest")
        return entry  # type: ignore[return-value]

    def test_goal_governor_exists(self) -> None:
        """
        Ensure the `goal-governor` entry is present in the agent-ops manifest.
        
        Raises:
            AssertionError: If the `goal-governor` record is not found.
        """
        self._get_goal_governor()

    def test_goal_governor_description_mentions_stuck(self) -> None:
        """New description should describe stuck/hanging/not-finishing scenarios."""
        entry = self._get_goal_governor()
        desc = entry["description"]
        self.assertIn(
            "stuck",
            desc.lower(),
            f"goal-governor description should mention 'stuck': {desc}",
        )

    def test_goal_governor_description_mentions_hanging(self) -> None:
        """
        Assert that the goal-governor entry's description contains the word "hanging" (case-insensitive).
        
        Raises:
        	AssertionError: If the description does not include "hanging".
        """
        entry = self._get_goal_governor()
        desc = entry["description"]
        self.assertIn(
            "hanging",
            desc.lower(),
            f"goal-governor description should mention 'hanging': {desc}",
        )

    def test_goal_governor_description_mentions_not_finishing(self) -> None:
        entry = self._get_goal_governor()
        desc = entry["description"]
        self.assertIn(
            "not finishing",
            desc.lower(),
            f"goal-governor description should mention 'not finishing': {desc}",
        )

    def test_goal_governor_triggers_include_stalled_goal_continuation(self) -> None:
        """New trigger 'stalled goal continuation' must be present."""
        entry = self._get_goal_governor()
        triggers = entry["triggers"]
        self.assertIn(
            "stalled goal continuation",
            triggers,
            f"'stalled goal continuation' not found in triggers: {triggers}",
        )

    def test_goal_governor_triggers_include_goal_governor(self) -> None:
        """Core trigger 'goal governor' must still be present."""
        entry = self._get_goal_governor()
        self.assertIn("goal governor", entry["triggers"])

    def test_goal_governor_triggers_do_not_include_old_goal_workflows(self) -> None:
        """Old trigger 'goal workflows' was removed; the slash-prefixed variant remains."""
        entry = self._get_goal_governor()
        triggers = entry["triggers"]
        # The plain "goal workflows" trigger was replaced by "stalled goal continuation".
        # The /goal workflows variant with a slash-prefix is kept.
        self.assertNotIn(
            "goal workflows",
            triggers,
            f"Plain 'goal workflows' trigger should have been removed; triggers: {triggers}",
        )

    def test_goal_governor_level_is_molecule(self) -> None:
        """
        Assert that the `goal-governor` manifest entry has its `level` set to "molecule".
        
        Fails the test if the entry's `level` field is not equal to "molecule".
        """
        entry = self._get_goal_governor()
        self.assertEqual(
            entry.get("level"),
            "molecule",
            f"goal-governor level should be 'molecule', got '{entry.get('level')}'",
        )

    def test_goal_governor_source_sha256_is_new(self) -> None:
        """source_sha256 must reflect the content change in SKILL.md."""
        entry = self._get_goal_governor()
        sha = entry.get("provenance", {}).get("source_sha256", "")
        # The old sha256 was 34cd2819a9932a0a27ded10f866fb3fdcd8d5cf85e111615aee5d1fcc6281697.
        old_sha = "34cd2819a9932a0a27ded10f866fb3fdcd8d5cf85e111615aee5d1fcc6281697"
        self.assertNotEqual(
            sha,
            old_sha,
            "goal-governor source_sha256 was not updated from the old value",
        )
        # New sha256 must be a valid 64-char hex string.
        self.assertRegex(
            sha,
            r"^[0-9a-f]{64}$",
            f"source_sha256 '{sha}' is not a valid 64-char hex sha256",
        )

    def test_goal_governor_source_revision_is_new(self) -> None:
        """
        Assert that the `goal-governor` entry's `provenance.source_revision` equals the expected new manifest revision.
        
        Loads the `goal-governor` record and fails the test if its `provenance.source_revision` is not exactly `NEW_MANIFEST_REVISION`.
        """
        entry = self._get_goal_governor()
        rev = entry.get("provenance", {}).get("source_revision", "")
        self.assertEqual(
            rev,
            NEW_MANIFEST_REVISION,
            f"goal-governor source_revision '{rev}' should be '{NEW_MANIFEST_REVISION}'",
        )

    def test_goal_governor_required_fields_present(self) -> None:
        """
        Verify the `goal-governor` entry in the agent-ops manifest contains all required top-level fields.
        
        Asserts that the entry returned by _get_goal_governor() includes the keys:
        "description", "id", "level", "provenance", "risk", "runtime_visibility",
        "scope", "skill_set", "source_path", and "triggers".
        """
        required: ClassVar[tuple[str, ...]] = (
            "description",
            "id",
            "level",
            "provenance",
            "risk",
            "runtime_visibility",
            "scope",
            "skill_set",
            "source_path",
            "triggers",
        )
        entry = self._get_goal_governor()
        for field in required:
            with self.subTest(field=field):
                self.assertIn(field, entry, f"goal-governor is missing field '{field}'")


# ---------------------------------------------------------------------------
# agent-ops manifest: session-workflow-miner (NEW skill)
# ---------------------------------------------------------------------------


class TestSessionWorkflowMinerAdded(unittest.TestCase):
    """The session-workflow-miner skill must be present in agent-ops manifest."""

    _MANIFEST_PATH = REPO_ROOT / ".skillsets" / "agent-ops" / "manifest.jsonl"

    REQUIRED_FIELDS: ClassVar[tuple[str, ...]] = (
        "description",
        "id",
        "level",
        "provenance",
        "risk",
        "runtime_visibility",
        "scope",
        "skill_set",
        "source_path",
        "triggers",
    )

    def _get_session_workflow_miner(self) -> dict[str, Any]:
        """
        Retrieve the "session-workflow-miner" entry from the agent-ops manifest.
        
        Loads the manifest JSONL and asserts that an entry with id "session-workflow-miner" exists,
        failing the test if it is not found.
        
        Returns:
            dict[str, Any]: The manifest record for the "session-workflow-miner" entry.
        """
        records = _load_jsonl(self._MANIFEST_PATH)
        entry = next(
            (r for r in records if r.get("id") == "session-workflow-miner"), None
        )
        self.assertIsNotNone(
            entry,
            "session-workflow-miner entry not found in agent-ops manifest",
        )
        return entry  # type: ignore[return-value]

    def test_session_workflow_miner_exists(self) -> None:
        self._get_session_workflow_miner()

    def test_session_workflow_miner_has_required_fields(self) -> None:
        entry = self._get_session_workflow_miner()
        for field in self.REQUIRED_FIELDS:
            with self.subTest(field=field):
                self.assertIn(
                    field,
                    entry,
                    f"session-workflow-miner is missing required field '{field}'",
                )

    def test_session_workflow_miner_skill_set_is_agent_ops(self) -> None:
        entry = self._get_session_workflow_miner()
        self.assertEqual(
            entry.get("skill_set"),
            "agent-ops",
            f"session-workflow-miner skill_set should be 'agent-ops', "
            f"got '{entry.get('skill_set')}'",
        )

    def test_session_workflow_miner_scope_is_global(self) -> None:
        """
        Verify that the 'session-workflow-miner' manifest entry has its `scope` set to "global".
        """
        entry = self._get_session_workflow_miner()
        self.assertEqual(
            entry.get("scope"),
            "global",
            f"session-workflow-miner scope should be 'global', got '{entry.get('scope')}'",
        )

    def test_session_workflow_miner_description_mentions_sessions(self) -> None:
        entry = self._get_session_workflow_miner()
        desc = entry.get("description", "")
        self.assertIn(
            "session",
            desc.lower(),
            f"session-workflow-miner description should mention 'session': {desc}",
        )

    def test_session_workflow_miner_has_triggers_list(self) -> None:
        entry = self._get_session_workflow_miner()
        triggers = entry.get("triggers", [])
        self.assertIsInstance(triggers, list)
        self.assertGreater(
            len(triggers),
            0,
            "session-workflow-miner must have at least one trigger",
        )

    def test_session_workflow_miner_trigger_includes_self(self) -> None:
        entry = self._get_session_workflow_miner()
        triggers = entry.get("triggers", [])
        self.assertIn(
            "session workflow miner",
            triggers,
            f"Expected 'session workflow miner' in triggers; got: {triggers}",
        )

    def test_session_workflow_miner_provenance_source_revision_is_new(self) -> None:
        entry = self._get_session_workflow_miner()
        rev = entry.get("provenance", {}).get("source_revision", "")
        self.assertEqual(
            rev,
            NEW_MANIFEST_REVISION,
            f"session-workflow-miner source_revision '{rev}' "
            f"should be '{NEW_MANIFEST_REVISION}'",
        )

    def test_session_workflow_miner_provenance_source_sha256_is_valid(self) -> None:
        entry = self._get_session_workflow_miner()
        sha = entry.get("provenance", {}).get("source_sha256", "")
        self.assertRegex(
            sha,
            r"^[0-9a-f]{64}$",
            f"session-workflow-miner source_sha256 '{sha}' is not a valid sha256",
        )

    def test_session_workflow_miner_level_is_compound(self) -> None:
        """
        Assert that the 'session-workflow-miner' manifest entry has its 'level' set to 'compound'.
        """
        entry = self._get_session_workflow_miner()
        self.assertEqual(
            entry.get("level"),
            "compound",
            f"session-workflow-miner level should be 'compound', got '{entry.get('level')}'",
        )

    def test_session_workflow_miner_risk_is_low(self) -> None:
        entry = self._get_session_workflow_miner()
        self.assertEqual(
            entry.get("risk"),
            "low",
            f"session-workflow-miner risk should be 'low', got '{entry.get('risk')}'",
        )

    def test_session_workflow_miner_source_path_ends_with_skill_md(self) -> None:
        """
        Assert the session-workflow-miner entry's `source_path` ends with 'SKILL.md'.
        
        Raises an assertion failure if the `session-workflow-miner` record's `source_path` does not end with 'SKILL.md'; the failure message includes the actual `source_path` value.
        """
        entry = self._get_session_workflow_miner()
        source_path = entry.get("source_path", "")
        self.assertTrue(
            source_path.endswith("SKILL.md"),
            f"session-workflow-miner source_path should end with 'SKILL.md': {source_path}",
        )


# ---------------------------------------------------------------------------
# command-surface.json: count and revision changes
# ---------------------------------------------------------------------------


class TestCommandSurfaceCountsAndRevision(unittest.TestCase):
    """command-surface.json must reflect the new counts and source_revision."""

    def setUp(self) -> None:
        """
        Load the command-surface JSON file into self._data for use by the test methods.
        
        Reads COMMAND_SURFACE_PATH using UTF-8 encoding and parses its contents with json.load,
        assigning the resulting Python object to self._data.
        """
        with open(COMMAND_SURFACE_PATH, encoding="utf-8") as fh:
            self._data = json.load(fh)

    def test_handle_count_is_111(self) -> None:
        """
        Verify the command-surface JSON's top-level "handle_count" equals the expected value.
        
        Asserts that the parsed command-surface data's "handle_count" field is equal to EXPECTED_HANDLE_COUNT.
        """
        self.assertEqual(
            self._data.get("handle_count"),
            EXPECTED_HANDLE_COUNT,
            f"handle_count should be {EXPECTED_HANDLE_COUNT}, "
            f"got {self._data.get('handle_count')}",
        )

    def test_generated_command_handle_count_is_absent(self) -> None:
        """
        Verify that command-surface metadata no longer reports generated wrapper counts.
        """
        self.assertNotIn("generated_command_handle_count", self._data)

    def test_handle_count_matches_actual_handles_length(self) -> None:
        """Declared handle_count must exactly match the length of the handles list."""
        actual = len(self._data.get("handles", []))
        self.assertEqual(
            self._data.get("handle_count"),
            actual,
            f"handle_count {self._data.get('handle_count')} "
            f"does not match actual list length {actual}",
        )

    def test_all_source_revisions_are_new_command_surface_revision(self) -> None:
        """Every handle's provenance.source_revision must use the new revision."""
        revisions: set[str] = {
            entry.get("provenance", {}).get("source_revision", "")
            for entry in self._data.get("handles", [])
            if entry.get("provenance", {}).get("source_revision", "")
        }
        self.assertGreater(len(revisions), 0, "No source_revision values found")
        self.assertEqual(
            revisions,
            {NEW_COMMAND_SURFACE_REVISION},
            f"Expected only '{NEW_COMMAND_SURFACE_REVISION}' in command-surface, "
            f"found: {sorted(revisions)}",
        )

    def test_no_source_revision_uses_old_manifest_revision(self) -> None:
        """
        Ensure no command-surface handle references the old manifest revision.
        
        Asserts that none of the entries in the command-surface `handles` list have
        `provenance.source_revision` equal to the known old revision.
        """
        for entry in self._data.get("handles", []):
            rev = entry.get("provenance", {}).get("source_revision", "")
            with self.subTest(handle=entry.get("handle", "?")):
                self.assertNotEqual(
                    rev,
                    OLD_MANIFEST_REVISION,
                    f"Handle '{entry.get('handle')}' still uses old revision "
                    f"'{OLD_MANIFEST_REVISION}'",
                )

    def test_command_surface_new_revision_matches_git_hash_pattern(self) -> None:
        """
        Assert that NEW_COMMAND_SURFACE_REVISION matches the expected short git-hash pattern.
        """
        self.assertRegex(
            NEW_COMMAND_SURFACE_REVISION,
            _REVISION_PATTERN,
            f"'{NEW_COMMAND_SURFACE_REVISION}' does not look like a git hash",
        )

    def test_generated_from_is_rooted_manifests(self) -> None:
        """
        Asserts that the command-surface metadata indicates it was generated from "rooted_manifests".
        """
        self.assertEqual(
            self._data.get("generated_from"),
            "rooted_manifests",
        )


# ---------------------------------------------------------------------------
# Docs/goals/jsc-351-agent-skills-codex-abi-conformance/state.yaml (new file)
# ---------------------------------------------------------------------------


class TestJsc351StateYamlExists(unittest.TestCase):
    """state.yaml must exist and be parseable YAML."""

    def test_state_yaml_file_exists(self) -> None:
        self.assertTrue(
            STATE_YAML_PATH.exists(),
            f"state.yaml not found at {STATE_YAML_PATH}",
        )

    def test_state_yaml_is_parseable(self) -> None:
        content = STATE_YAML_PATH.read_text(encoding="utf-8")
        # Should not raise
        data = yaml.safe_load(content)
        self.assertIsInstance(data, dict, "state.yaml should parse to a dict")

    def test_state_yaml_is_non_empty(self) -> None:
        content = STATE_YAML_PATH.read_text(encoding="utf-8").strip()
        self.assertGreater(len(content), 0, "state.yaml must not be empty")


class TestJsc351StateYamlStructure(unittest.TestCase):
    """state.yaml must contain the required top-level keys and values."""

    def setUp(self) -> None:
        """
        Prepare test fixture by loading and parsing the state YAML file into self._data.
        
        Reads STATE_YAML_PATH using UTF-8 and parses it with yaml.safe_load, storing the resulting dictionary in self._data for use by the test methods.
        """
        self._data: dict[str, Any] = yaml.safe_load(
            STATE_YAML_PATH.read_text(encoding="utf-8")
        )

    REQUIRED_TOP_LEVEL_KEYS: ClassVar[tuple[str, ...]] = (
        "version",
        "goal",
        "governance_evidence",
        "completion_contract",
        "rules",
        "checks",
        "tasks",
    )

    def test_required_top_level_keys_present(self) -> None:
        """
        Assert that the state YAML contains all required top-level keys.
        
        Each key in self.REQUIRED_TOP_LEVEL_KEYS is checked in a subtest; the test fails with a clear message if a key is missing from self._data.
        """
        for key in self.REQUIRED_TOP_LEVEL_KEYS:
            with self.subTest(key=key):
                self.assertIn(key, self._data, f"state.yaml is missing key '{key}'")

    def test_version_is_2(self) -> None:
        """
        Verify the top-level `version` field in the loaded state YAML equals 2.
        
        Checks that `self._data["version"]` is exactly 2 and fails the test with a message showing the actual value if it does not match.
        """
        self.assertEqual(
            self._data.get("version"),
            2,
            f"state.yaml version should be 2, got {self._data.get('version')}",
        )

    def test_goal_slug_is_jsc_351(self) -> None:
        """
        Verify that the goal slug contains "jsc-351".
        
        Asserts that the loaded YAML's `goal.slug` includes the substring "jsc-351"; on failure the assertion message shows the actual slug.
        """
        goal = self._data.get("goal", {})
        slug = goal.get("slug", "")
        self.assertIn(
            "jsc-351",
            slug,
            f"goal.slug should contain 'jsc-351', got '{slug}'",
        )

    def test_goal_status_is_in_progress(self) -> None:
        """
        Assert that the loaded goal's status equals "in_progress".
        
        If the status differs or the goal is missing, the test fails and reports the actual value.
        """
        goal = self._data.get("goal", {})
        self.assertEqual(
            goal.get("status"),
            "in_progress",
            f"goal.status should be 'in_progress', got '{goal.get('status')}'",
        )

    def test_goal_has_objective(self) -> None:
        """
        Verify that the loaded goal contains a non-empty objective.
        
        Asserts that `goal.objective` exists and has length greater than zero.
        """
        goal = self._data.get("goal", {})
        objective = goal.get("objective", "")
        self.assertGreater(len(objective), 0, "goal.objective must not be empty")

    def test_tasks_is_non_empty_list(self) -> None:
        """
        Assert that the YAML state's "tasks" field exists and contains at least one task.
        
        This test verifies that `self._data["tasks"]` is a list and that its length is greater than zero; it fails the test if the key is missing, not a list, or empty.
        """
        tasks = self._data.get("tasks", [])
        self.assertIsInstance(tasks, list)
        self.assertGreater(len(tasks), 0, "state.yaml must have at least one task")

    def test_each_task_has_id_and_status(self) -> None:
        """
        Assert that every task in the loaded state YAML contains both the `id` and `status` keys.
        
        Each task in `self._data["tasks"]` is checked and will cause the test to fail if either key is missing.
        """
        tasks = self._data.get("tasks", [])
        for task in tasks:
            task_id = task.get("id", "?")
            with self.subTest(task_id=task_id):
                self.assertIn("id", task, f"Task is missing 'id' field")
                self.assertIn("status", task, f"Task '{task_id}' is missing 'status'")

    def test_governance_evidence_has_outstanding_gates(self) -> None:
        """
        Verify that `governance_evidence` defines an `outstanding_gates` list and that the list contains at least one entry.
        
        Asserts that `governance_evidence.outstanding_gates` is a list and its length is greater than zero.
        """
        evidence = self._data.get("governance_evidence", {})
        gates = evidence.get("outstanding_gates", [])
        self.assertIsInstance(gates, list)
        self.assertGreater(
            len(gates), 0, "governance_evidence.outstanding_gates must not be empty"
        )

    def test_each_outstanding_gate_has_id_kind_status(self) -> None:
        """
        Assert that each outstanding governance gate entry includes the required keys.
        
        Loads the top-level `governance_evidence.outstanding_gates` list and, for every gate in that list, asserts the presence of the keys `"id"`, `"kind"`, and `"status"`. Each gate is tested in a subTest keyed by the gate's `id` (or `"?"` if missing).
        """
        evidence = self._data.get("governance_evidence", {})
        gates = evidence.get("outstanding_gates", [])
        for gate in gates:
            gate_id = gate.get("id", "?")
            with self.subTest(gate_id=gate_id):
                self.assertIn("id", gate)
                self.assertIn("kind", gate)
                self.assertIn("status", gate)

    def test_rules_require_one_active_task(self) -> None:
        rules = self._data.get("rules", {})
        self.assertTrue(
            rules.get("one_active_task"),
            "rules.one_active_task must be true",
        )

    def test_completion_contract_has_outcome(self) -> None:
        """
        Assert that the state's completion contract contains a non-empty 'outcome' value.
        
        Checks that the top-level `completion_contract` mapping has a non-empty `outcome` string; fails the test if `outcome` is missing or empty.
        """
        contract = self._data.get("completion_contract", {})
        outcome = contract.get("outcome", "")
        self.assertGreater(len(outcome), 0, "completion_contract.outcome must not be empty")

    def test_continuation_gate_auto_continue_is_no(self) -> None:
        """
        Assert that the loaded state's continuation_gate has "auto_continue_allowed" set to "no".
        
        Raises:
            AssertionError: if the key is missing or its value is not "no".
        """
        gate = self._data.get("continuation_gate", {})
        self.assertEqual(
            gate.get("auto_continue_allowed"),
            "no",
            "continuation_gate.auto_continue_allowed should be 'no'",
        )

    def test_checks_has_last_verification(self) -> None:
        """
        Assert that the loaded YAML `checks` mapping includes a `last_verification` key.
        
        This test fails if the `checks` section is missing the required `last_verification` entry.
        """
        checks = self._data.get("checks", {})
        self.assertIn("last_verification", checks, "checks must contain last_verification")

    def test_last_verification_outcome_is_pass(self) -> None:
        """
        Assert that the checks.last_verification outcome is "pass".
        
        Raises an assertion failure if the `checks.last_verification.outcome` value is not the string "pass".
        """
        checks = self._data.get("checks", {})
        lv = checks.get("last_verification", {})
        self.assertEqual(
            lv.get("outcome"),
            "pass",
            f"last_verification.outcome should be 'pass', got '{lv.get('outcome')}'",
        )


# ---------------------------------------------------------------------------
# .harness/memory/LEARNINGS.md: new 2026-05-24 entries appended
# ---------------------------------------------------------------------------


class TestLearningsMdNewEntries(unittest.TestCase):
    """LEARNINGS.md must contain the new 2026-05-24 log entries from this PR."""

    def setUp(self) -> None:
        """
        Prepare the test fixture by reading the repository LEARNINGS.md file into self._content.
        
        Reads the entire .harness/memory/LEARNINGS.md file using UTF-8 encoding and stores its text for use by subsequent tests.
        """
        self._content = LEARNINGS_MD_PATH.read_text(encoding="utf-8")

    def test_learnings_md_exists(self) -> None:
        """
        Check that the repository's LEARNINGS.md file exists at the expected path.
        """
        self.assertTrue(LEARNINGS_MD_PATH.exists(), "LEARNINGS.md file must exist")

    def test_learnings_md_is_non_empty(self) -> None:
        """
        Assert that the loaded LEARNINGS.md content is not empty after trimming whitespace.
        """
        self.assertGreater(len(self._content.strip()), 0, "LEARNINGS.md must not be empty")

    def test_learnings_md_contains_2026_05_24_entries(self) -> None:
        """New entries dated 2026-05-24 must be present."""
        self.assertIn(
            "2026-05-24",
            self._content,
            "LEARNINGS.md should contain new entries dated 2026-05-24",
        )

    def test_learnings_md_retains_older_entries(self) -> None:
        """Append-only: entries from before 2026-05-24 must still be present."""
        # An older entry we know should be present from the original file.
        self.assertIn(
            "2026-05-19",
            self._content,
            "LEARNINGS.md must retain previous entries (append-only policy)",
        )

    def test_new_entries_reference_bash_command_failures(self) -> None:
        """The new entries record 'Bash command' failures with exit code 2."""
        self.assertIn(
            "exit code 2",
            self._content,
            "New LEARNINGS.md entries should mention 'exit code 2' failures",
        )

    def test_new_entries_include_auto_keys(self) -> None:
        """The new entries include auto-key identifiers."""
        self.assertIn(
            "auto-key:",
            self._content,
            "New LEARNINGS.md entries should include 'auto-key:' identifiers",
        )

    def test_learnings_md_has_correct_section_header(self) -> None:
        """The file should begin with the repo-specific header."""
        self.assertIn(
            "Repo-specific agent knowledge base",
            self._content,
            "LEARNINGS.md must contain the standard section header",
        )

    def test_new_2026_05_24_entries_mention_jq_or_cat(self) -> None:
        """The 2026-05-24 entries specifically record 'cat' and 'jq' failures."""
        self.assertIn(
            "'jq'",
            self._content,
            "2026-05-24 entries should mention jq command failures",
        )
        self.assertIn(
            "'cat'",
            self._content,
            "2026-05-24 entries should mention cat command failures",
        )


if __name__ == "__main__":
    unittest.main()
