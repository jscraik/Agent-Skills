"""
Structural validation tests for changes introduced in this PR:

  - Most .skillsets/*/manifest.jsonl and .skillsets/command-surface.json entries
    now use source_revision "bc58ae8d1" (bumped from "5b5889499").
    harness-engineering uses its own independent revision "085d548bf".
  - The "he-refine" entry in command-surface.json was updated:
      command_visibility: "target" -> "orchestrator"
      description: updated to reflect artifact refinement (not browser-first polish)
      level: "molecule" -> "compound"
      invoke_via: removed (no longer present)
      source_sha256: updated to reflect new SKILL.md content
"""
import json
import re
import unittest
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]

SKILLSET_DIR = REPO_ROOT / ".skillsets"
COMMAND_SURFACE_PATH = SKILLSET_DIR / "command-surface.json"

_NEW_REVISION = "bc58ae8d1"
_OLD_REVISION = "5b5889499"

# Git short-hash: 7+ hex chars
_REVISION_PATTERN = re.compile(r"^[0-9a-f]{7,}", re.IGNORECASE)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    """
    Load a JSON Lines (JSONL) file and return its parsed records.
    
    Blank or whitespace-only lines are skipped. Each non-empty line is parsed as JSON and appended to the returned list.
    
    Parameters:
        path (Path): Path to the JSONL file to load.
    
    Returns:
        list[dict[str, Any]]: A list of parsed JSON objects, one per non-empty line.
    
    Raises:
        AssertionError: If a line contains invalid JSON; the error message includes the file path and line number.
    """
    records = []
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


def _load_command_surface() -> dict[str, Any]:
    """
    Load and return the parsed JSON contents of the repository's command-surface file.
    
    Reads JSON from the path specified by the module-level COMMAND_SURFACE_PATH and returns the decoded object.
    
    Returns:
        dict[str, Any]: The parsed JSON root object from command-surface.json.
    """
    with open(COMMAND_SURFACE_PATH, encoding="utf-8") as fh:
        return json.load(fh)


# ---------------------------------------------------------------------------
# Manifest JSONL: source_revision bump
# ---------------------------------------------------------------------------

class TestManifestRevisionBumpedToBc58ae8d1(unittest.TestCase):
    """
    Manifests explicitly changed in this PR should use updated source_revisions.

    Most skillsets were bumped to "bc58ae8d1".
    The harness-engineering skillset uses its own per-skillset revision "085d548bf".
    All manifests must no longer reference the previous shared revision "5b5889499".
    """

    # Skillsets bumped to bc58ae8d1 in this PR (all except harness-engineering)
    MANIFESTS_WITH_NEW_REVISION = [
        "agent-ops",
        "backend-platform",
        "content-publishing",
        "frontend-ui",
        "mobile-native",
        "plugin-factory",
        "product-strategy",
        "security-ops",
        "skill-factory",
    ]

    ALL_MANIFESTS = MANIFESTS_WITH_NEW_REVISION + ["harness-engineering"]

    # harness-engineering uses its own independent revision
    _HE_REVISION = "085d548bf"

    def _assert_revision_updated(self, skillset_name: str):
        """
        Assert that every record in the given skillset's manifest uses the expected new source revision.
        
        If the manifest file is missing the test is skipped. For each record in the manifest, the function asserts that `provenance.source_revision` equals the module-level `_NEW_REVISION`; each record is checked in a separate subTest keyed by the skillset name and the record `id`.
        """
        path = SKILLSET_DIR / skillset_name / "manifest.jsonl"
        if not path.exists():
            self.skipTest(f"Manifest not found: {path}")
        records = _load_jsonl(path)
        for rec in records:
            rev = rec.get("provenance", {}).get("source_revision", "")
            with self.subTest(skillset=skillset_name, skill_id=rec.get("id", "?")):
                self.assertEqual(
                    rev,
                    _NEW_REVISION,
                    f"Entry '{rec.get('id')}' in {skillset_name}/manifest.jsonl "
                    f"has revision '{rev}', expected '{_NEW_REVISION}'",
                )

    def _assert_old_revision_absent(self, skillset_name: str):
        """
        Assert that no records in the specified skillset's manifest use the old source revision.
        
        If the manifest file does not exist the check is skipped. For each record in
        <skillset>/manifest.jsonl this makes a subtest (keyed by skillset and record id)
        and asserts that `provenance.source_revision` is not equal to the module-level
        `_OLD_REVISION`.
        
        Parameters:
        	skillset_name (str): Name of the skillset directory containing `manifest.jsonl`.
        """
        path = SKILLSET_DIR / skillset_name / "manifest.jsonl"
        if not path.exists():
            return
        records = _load_jsonl(path)
        for rec in records:
            rev = rec.get("provenance", {}).get("source_revision", "")
            with self.subTest(skillset=skillset_name, skill_id=rec.get("id", "?")):
                self.assertNotEqual(
                    rev,
                    _OLD_REVISION,
                    f"Entry '{rec.get('id')}' in {skillset_name}/manifest.jsonl "
                    f"still has old revision '{_OLD_REVISION}'",
                )

    # Per-skillset revision checks for manifests bumped to bc58ae8d1
    def test_agent_ops_revision(self):
        self._assert_revision_updated("agent-ops")

    def test_backend_platform_revision(self):
        self._assert_revision_updated("backend-platform")

    def test_content_publishing_revision(self):
        self._assert_revision_updated("content-publishing")

    def test_frontend_ui_revision(self):
        self._assert_revision_updated("frontend-ui")

    def test_mobile_native_revision(self):
        self._assert_revision_updated("mobile-native")

    def test_plugin_factory_revision(self):
        self._assert_revision_updated("plugin-factory")

    def test_product_strategy_revision(self):
        self._assert_revision_updated("product-strategy")

    def test_security_ops_revision(self):
        self._assert_revision_updated("security-ops")

    def test_skill_factory_revision(self):
        self._assert_revision_updated("skill-factory")

    def test_harness_engineering_uses_its_own_revision(self):
        """harness-engineering manifest uses 085d548bf (its own independent revision)."""
        path = SKILLSET_DIR / "harness-engineering" / "manifest.jsonl"
        if not path.exists():
            self.skipTest("harness-engineering manifest not found")
        records = _load_jsonl(path)
        for rec in records:
            rev = rec.get("provenance", {}).get("source_revision", "")
            with self.subTest(skill_id=rec.get("id", "?")):
                self.assertEqual(
                    rev,
                    self._HE_REVISION,
                    f"Entry '{rec.get('id')}' in harness-engineering/manifest.jsonl "
                    f"has revision '{rev}', expected '{self._HE_REVISION}'",
                )

    def test_no_manifest_uses_old_revision(self):
        """
        Assert that no manifest record in any known skillset uses the old source_revision "5b5889499".
        """
        for skillset_name in self.ALL_MANIFESTS:
            self._assert_old_revision_absent(skillset_name)

    def test_all_revisions_are_valid_git_hash_format(self):
        """
        Assert that every manifest record's `provenance.source_revision` matches the expected git-hash pattern.
        
        Checks each manifest listed in `ALL_MANIFESTS` (skipping missing files) and uses a subtest per record to verify `provenance.source_revision` matches `_REVISION_PATTERN`; fails with a message identifying the invalid revision when a record does not conform.
        """
        for skillset_name in self.ALL_MANIFESTS:
            path = SKILLSET_DIR / skillset_name / "manifest.jsonl"
            if not path.exists():
                continue
            records = _load_jsonl(path)
            for rec in records:
                rev = rec.get("provenance", {}).get("source_revision", "")
                with self.subTest(skillset=skillset_name, skill_id=rec.get("id", "?")):
                    self.assertRegex(
                        rev,
                        _REVISION_PATTERN,
                        f"source_revision '{rev}' does not look like a git hash",
                    )


# ---------------------------------------------------------------------------
# Manifest JSONL: structural invariants
# ---------------------------------------------------------------------------

class TestManifestRequiredFields(unittest.TestCase):
    """Each manifest.jsonl entry must carry all required fields."""

    REQUIRED_FIELDS = (
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

    PROVENANCE_FIELDS = ("source_revision", "source_sha256", "generator")

    def _check_manifest(self, skillset_name: str):
        """
        Validate that the given skillset's manifest.jsonl exists and that each record contains required fields and valid structure.
        
        Loads <SKILLSET_DIR>/<skillset_name>/manifest.jsonl, asserts the file is present and contains at least one record, then for each record asserts:
        - every key listed in self.REQUIRED_FIELDS is present at the top level,
        - every key listed in self.PROVENANCE_FIELDS is present inside the record's `provenance` object,
        - `triggers` is a list with at least one element.
        
        Parameters:
            skillset_name (str): Name of the skillset directory under SKILLSET_DIR whose manifest should be checked.
        """
        path = SKILLSET_DIR / skillset_name / "manifest.jsonl"
        if not path.exists():
            self.skipTest(f"Manifest not found: {path}")
        records = _load_jsonl(path)
        self.assertGreater(len(records), 0, f"Manifest {path.name} is unexpectedly empty")
        for rec in records:
            with self.subTest(skillset=skillset_name, skill_id=rec.get("id", "?")):
                for field in self.REQUIRED_FIELDS:
                    self.assertIn(field, rec, f"Missing required field '{field}'")
                prov = rec["provenance"]
                for pf in self.PROVENANCE_FIELDS:
                    self.assertIn(pf, prov, f"Missing provenance field '{pf}'")
                self.assertIsInstance(rec["triggers"], list)
                self.assertGreater(len(rec["triggers"]), 0, "triggers list must be non-empty")

    def test_agent_ops_structure(self):
        self._check_manifest("agent-ops")

    def test_backend_platform_structure(self):
        self._check_manifest("backend-platform")

    def test_content_publishing_structure(self):
        self._check_manifest("content-publishing")

    def test_frontend_ui_structure(self):
        """
        Validate that the 'frontend-ui' manifest contains the required top-level fields, required provenance fields, and a non-empty `triggers` list; the test is skipped if the manifest file is missing.
        """
        self._check_manifest("frontend-ui")

    def test_harness_engineering_structure(self):
        self._check_manifest("harness-engineering")

    def test_mobile_native_structure(self):
        self._check_manifest("mobile-native")

    def test_plugin_factory_structure(self):
        self._check_manifest("plugin-factory")

    def test_product_strategy_structure(self):
        """
        Validate the product-strategy manifest contains required fields and minimal structure.
        
        Ensures the `.skillsets/product-strategy/manifest.jsonl` file exists (or skips if missing), contains at least one record, and that each record includes the top-level required fields, the required provenance fields, and a non-empty `triggers` list.
        """
        self._check_manifest("product-strategy")

    def test_security_ops_structure(self):
        self._check_manifest("security-ops")

    def test_skill_factory_structure(self):
        self._check_manifest("skill-factory")


# ---------------------------------------------------------------------------
# command-surface.json: source_revision bump
# ---------------------------------------------------------------------------

class TestCommandSurfaceRevisionBump(unittest.TestCase):
    def setUp(self):
        """
        Prepare the test fixture by loading the repository's command-surface.json into the test instance.
        
        Stores the parsed JSON object from command-surface.json on self._data for use by individual tests.
        """
        self._data = _load_command_surface()

    def test_all_handle_revisions_use_new_hash(self):
        """
        Verify that every handle in the loaded command-surface data that specifies a `provenance.source_revision` uses the expected new revision.
        
        This test iterates `self._data["handles"]` and for each entry with a non-empty `provenance.source_revision` asserts it equals `_NEW_REVISION`, using a subTest keyed by the handle name for clearer failure reporting.
        """
        for entry in self._data.get("handles", []):
            prov = entry.get("provenance", {})
            rev = prov.get("source_revision", "")
            if rev:
                with self.subTest(handle=entry.get("handle", "?")):
                    self.assertEqual(
                        rev,
                        _NEW_REVISION,
                        f"Handle '{entry.get('handle')}' has revision '{rev}', "
                        f"expected '{_NEW_REVISION}'",
                    )

    def test_no_handle_uses_old_revision(self):
        """
        Verifies no handle entry in the loaded command-surface data uses the deprecated source revision.
        
        For each handle in self._data["handles"], asserts that `provenance.source_revision` is not equal to the old revision constant (`_OLD_REVISION`). Each handle is checked inside a subTest keyed by the handle name to isolate failures.
        """
        for entry in self._data.get("handles", []):
            prov = entry.get("provenance", {})
            rev = prov.get("source_revision", "")
            with self.subTest(handle=entry.get("handle", "?")):
                self.assertNotEqual(
                    rev,
                    _OLD_REVISION,
                    f"Handle '{entry.get('handle')}' still uses old revision {_OLD_REVISION}",
                )

    def test_file_is_valid_json_with_handles_list(self):
        """
        Assert that the loaded command-surface data is a JSON object and contains a top-level "handles" key whose value is a list.
        
        This verifies the file parsed into a dict and that the required "handles" array is present and properly typed.
        """
        self.assertIsInstance(self._data, dict)
        self.assertIn("handles", self._data)
        self.assertIsInstance(self._data["handles"], list)

    def test_all_handles_have_required_fields(self):
        required = ("handle", "description", "kind", "provenance")
        for entry in self._data.get("handles", []):
            for field in required:
                with self.subTest(handle=entry.get("handle", "?"), field=field):
                    self.assertIn(field, entry)


# ---------------------------------------------------------------------------
# command-surface.json: he-refine entry structural changes
# ---------------------------------------------------------------------------

class TestCommandSurfaceHeRefineEntry(unittest.TestCase):
    """Validate the specific structural changes made to the he-refine entry in this PR."""

    def setUp(self):
        """
        Load command-surface data and set self._he_refine to the first handle entry whose `handle` is "he-refine", or `None` if not found.
        """
        data = _load_command_surface()
        self._he_refine = next(
            (h for h in data.get("handles", []) if h.get("handle") == "he-refine"),
            None,
        )

    def test_he_refine_entry_exists(self):
        """
        Asserts that the `he-refine` handle exists in the loaded command-surface data.
        
        Raises an assertion failure with a clear message if the `he-refine` entry is missing.
        """
        self.assertIsNotNone(
            self._he_refine,
            "he-refine entry not found in command-surface.json",
        )

    def test_he_refine_command_visibility_is_orchestrator(self):
        """
        Assert the he-refine handle's command_visibility equals "orchestrator".
        """
        self.assertEqual(self._he_refine.get("command_visibility"), "orchestrator")

    def test_he_refine_command_visibility_is_not_target(self):
        """
        Assert that the `he-refine` handle's `command_visibility` is not "target".
        """
        self.assertNotEqual(self._he_refine.get("command_visibility"), "target")

    def test_he_refine_level_is_compound(self):
        """level was changed from 'molecule' to 'compound' in this PR."""
        self.assertEqual(self._he_refine.get("level"), "compound")

    def test_he_refine_level_is_not_molecule(self):
        """
        Asserts the `he-refine` handle's `level` field is not "molecule".
        """
        self.assertNotEqual(self._he_refine.get("level"), "molecule")

    def test_he_refine_invoke_via_is_removed(self):
        """
        Asserts that the `he-refine` handle does not include the `invoke_via` key.
        
        This verifies the `invoke_via` field (previously set to "harness-engineering") has been removed from the `he-refine` entry.
        """
        self.assertNotIn("invoke_via", self._he_refine)

    def test_he_refine_description_reflects_artifact_refinement(self):
        """New description targets artifact/plan/spec refinement, not browser-first polish."""
        desc = self._he_refine.get("description", "")
        self.assertIn(
            "Refine Harness Engineering",
            desc,
            f"he-refine description should reference 'Refine Harness Engineering', got: {desc}",
        )

    def test_he_refine_description_does_not_mention_browser_first(self):
        """Old description referenced 'browser-first' - should not appear in new description."""
        desc = self._he_refine.get("description", "")
        self.assertNotIn(
            "browser-first",
            desc,
            f"he-refine description still contains old browser-first language: {desc}",
        )

    def test_he_refine_description_does_not_mention_dev_server(self):
        """
        Asserts the he-refine handle's description does not contain the substring "dev-server-backed".
        """
        desc = self._he_refine.get("description", "")
        self.assertNotIn(
            "dev-server-backed",
            desc,
            f"he-refine description still contains old dev-server language: {desc}",
        )

    def test_he_refine_source_revision_is_new(self):
        """
        Assert the he-refine handle's provenance `source_revision` equals the expected new revision.
        
        Fails the test if the handle's `provenance.source_revision` is not equal to `_NEW_REVISION`.
        """
        rev = self._he_refine.get("provenance", {}).get("source_revision", "")
        self.assertEqual(
            rev,
            _NEW_REVISION,
            f"he-refine source_revision should be {_NEW_REVISION}, got: {rev}",
        )

    def test_he_refine_source_sha256_updated(self):
        """
        Asserts the he-refine handle's provenance.source_sha256 was changed from the previous SHA-256.
        
        Checks that the `provenance.source_sha256` for the `he-refine` handle does not equal the prior SHA
        "9c8b00872f7b10d64d63a5df5652d3fb30731fdb506dddaa5aed5cb58ec897d9".
        """
        old_sha = "9c8b00872f7b10d64d63a5df5652d3fb30731fdb506dddaa5aed5cb58ec897d9"
        sha = self._he_refine.get("provenance", {}).get("source_sha256", "")
        self.assertNotEqual(
            sha,
            old_sha,
            "he-refine source_sha256 was not updated from old value",
        )

    def test_he_refine_new_source_sha256_is_non_empty(self):
        sha = self._he_refine.get("provenance", {}).get("source_sha256", "")
        self.assertTrue(len(sha) > 0, "he-refine source_sha256 must be non-empty")

    def test_he_refine_owner_is_harness_engineering(self):
        """Check that the he-refine handle's owner is "harness-engineering"."""
        self.assertEqual(self._he_refine.get("owner"), "harness-engineering")

    def test_he_refine_kind_is_skill(self):
        self.assertEqual(self._he_refine.get("kind"), "skill")

    def test_he_refine_has_required_provenance_fields(self):
        """
        Verify the `he-refine` handle's provenance contains required fields.
        
        Asserts that the provenance object includes `source_revision`, `source_sha256`, and `generator`.
        """
        prov = self._he_refine.get("provenance", {})
        for field in ("source_revision", "source_sha256", "generator"):
            with self.subTest(field=field):
                self.assertIn(field, prov)


# ---------------------------------------------------------------------------
# Regression: all manifests remain parseable JSONL
# ---------------------------------------------------------------------------

class TestAllManifestsParseable(unittest.TestCase):
    """Regression: every manifest.jsonl in the repo must be valid JSONL after this PR."""

    def test_all_manifest_jsonl_files_parse_without_error(self):
        manifest_paths = sorted(SKILLSET_DIR.glob("*/manifest.jsonl"))
        self.assertGreater(len(manifest_paths), 0, "No manifest.jsonl files found")
        for path in manifest_paths:
            with self.subTest(path=path.relative_to(REPO_ROOT)):
                records = _load_jsonl(path)
                self.assertGreater(len(records), 0, f"{path.name} must be non-empty")


if __name__ == "__main__":
    unittest.main()
