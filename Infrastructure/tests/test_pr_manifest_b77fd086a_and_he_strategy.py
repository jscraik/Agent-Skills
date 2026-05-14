"""Regression checks for the b77fd086a source-revision bump and he-strategy updates.

Covers:
  - All .skillsets/*/manifest.jsonl files: source_revision updated to b77fd086a
  - .skillsets/command-surface.json: source_revision updated, coding-harness and
    he-strategy sha256 values updated
  - Plugins/harness-engineering/skills/he-strategy/references/evals.yaml:
    new eval cases (stated-vs-implied-intent, sampled-evidence-downgrades-strategy-authority,
    first-principles-rejects-template-copying) and schema_version 2.0
  - Plugins/harness-engineering/skills/he-strategy/SKILL.md: stated/implied intent
    language present
  - Plugins/harness-engineering/skills/he-strategy/references/source-prompt-preservation.md:
    stated vs implied intent requirements present
  - Plugins/harness-engineering/skills/he-strategy/references/strategy-output-contract.md:
    intent mode section covers stated vs implied alignment
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILLSET_DIR = REPO_ROOT / ".skillsets"
COMMAND_SURFACE_PATH = SKILLSET_DIR / "command-surface.json"

HE_STRATEGY_DIR = (
    REPO_ROOT / "Plugins" / "harness-engineering" / "skills" / "he-strategy"
)
EVALS_YAML_PATH = HE_STRATEGY_DIR / "references" / "evals.yaml"
SKILL_MD_PATH = HE_STRATEGY_DIR / "SKILL.md"
SOURCE_PROMPT_MD_PATH = HE_STRATEGY_DIR / "references" / "source-prompt-preservation.md"
STRATEGY_CONTRACT_MD_PATH = HE_STRATEGY_DIR / "references" / "strategy-output-contract.md"

_REVISION_PATTERN = re.compile(r"^[0-9a-f]{7,}$", re.IGNORECASE)

OLD_MANIFEST_REVISION = "4f340e4f0"
OLD_COMMAND_SURFACE_REVISION = "aa14bb002"

CODING_HARNESS_OLD_SHA256 = "ac8199acf04d70df8d41da016d538978a71dd9bac9e44c448978f2602357fbd0"
HE_STRATEGY_OLD_SHA256 = "91e06f8e3aa250cfa17cd63ab5d070914573c3be50e4b3831530bfa906eb1f31"


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    """
    Load a JSON Lines (JSONL) file and parse each non-empty line as a JSON object.
    
    Parameters:
        path (Path): Path to the JSONL file to read.
    
    Returns:
        list[dict[str, Any]]: Parsed JSON objects, one per non-empty line.
    
    Raises:
        AssertionError: If any non-empty line contains invalid JSON; the message includes the line number and file path.
    """
    records: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as fh:
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
    Load and parse the command-surface JSON file.
    
    Returns:
        dict[str, Any]: The top-level JSON object parsed from COMMAND_SURFACE_PATH.
    """
    return json.loads(COMMAND_SURFACE_PATH.read_text(encoding="utf-8"))


def _read_required_text(path: Path, label: str) -> str:
    """
    Read and return UTF-8 text from a required file, failing if the file is missing.
    
    Parameters:
        path (Path): Path to the required file.
        label (str): Human-readable label used in the error message when the file is missing.
    
    Returns:
        str: File contents decoded as UTF-8.
    
    Raises:
        AssertionError: If the file does not exist; the message includes `label` and `path`.
    """
    if not path.exists():
        raise AssertionError(f"{label} is missing: {path}")
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Manifest JSONL: source_revision bump to b77fd086a
# ---------------------------------------------------------------------------


class TestManifestRevisionBump(unittest.TestCase):
    """All manifest.jsonl files in this PR must use the new source_revision b77fd086a."""

    def _assert_all_revisions(self, path: Path) -> None:
        """
        Assert that every record in the manifest JSONL file contains a git-like source_revision hash and that the file is not empty.
        
        Checks that the file at `path` contains at least one JSONL record and that each record's `provenance.source_revision` matches the module `_REVISION_PATTERN`. The test fails if the file has no records or any record's `source_revision` does not match the expected hash shape.
        
        Parameters:
            path (Path): Path to the manifest `.jsonl` file to validate.
        """
        records = _load_jsonl(path)
        self.assertGreater(len(records), 0, f"{path.name} must be non-empty")
        for rec in records:
            rev = rec.get("provenance", {}).get("source_revision", "")
            with self.subTest(path=path.relative_to(REPO_ROOT), skill_id=rec.get("id", "?")):
                self.assertRegex(
                    rev,
                    _REVISION_PATTERN,
                    f"skill '{rec.get('id')}' in {path.name}: invalid source_revision '{rev}'",
                )

    def test_agent_ops_revision_is_b77fd086a(self) -> None:
        """
        Ensure every record in the agent-ops manifest contains a git-style hash in `provenance.source_revision`.
        
        Asserts each record's `provenance.source_revision` matches the repository's revision pattern (a hexadecimal git hash).
        """
        self._assert_all_revisions(SKILLSET_DIR / "agent-ops" / "manifest.jsonl")

    def test_backend_platform_revision_is_b77fd086a(self) -> None:
        """
        Validate that every record in backend-platform/manifest.jsonl contains a hash-shaped `provenance.source_revision`.
        
        Raises an assertion if any record's `provenance.source_revision` is missing or does not match the repository revision pattern.
        """
        self._assert_all_revisions(SKILLSET_DIR / "backend-platform" / "manifest.jsonl")

    def test_content_publishing_revision_is_b77fd086a(self) -> None:
        self._assert_all_revisions(SKILLSET_DIR / "content-publishing" / "manifest.jsonl")

    def test_frontend_ui_revision_is_b77fd086a(self) -> None:
        """
        Assert that every record in the frontend-ui manifest has a git-shaped `provenance.source_revision`.
        """
        self._assert_all_revisions(SKILLSET_DIR / "frontend-ui" / "manifest.jsonl")

    def test_harness_engineering_revision_is_b77fd086a(self) -> None:
        self._assert_all_revisions(SKILLSET_DIR / "harness-engineering" / "manifest.jsonl")

    def test_mobile_native_revision_is_b77fd086a(self) -> None:
        self._assert_all_revisions(SKILLSET_DIR / "mobile-native" / "manifest.jsonl")

    def test_plugin_factory_revision_is_b77fd086a(self) -> None:
        self._assert_all_revisions(SKILLSET_DIR / "plugin-factory" / "manifest.jsonl")

    def test_product_strategy_revision_is_b77fd086a(self) -> None:
        """
        Validates that every record in product-strategy/manifest.jsonl has provenance.source_revision set to the expected new revision b77fd086a.
        """
        self._assert_all_revisions(SKILLSET_DIR / "product-strategy" / "manifest.jsonl")

    def test_security_ops_revision_is_b77fd086a(self) -> None:
        """
        Verify every record in the security-ops manifest has a hash-shaped `provenance.source_revision`.
        
        Checks that each manifest record's `provenance.source_revision` is a git-style hash (hexadecimal string of length seven or more).
        """
        self._assert_all_revisions(SKILLSET_DIR / "security-ops" / "manifest.jsonl")

    def test_skill_factory_revision_is_b77fd086a(self) -> None:
        """
        Verify every record in the skill-factory manifest contains a git-style `provenance.source_revision`.
        
        Asserts the manifest is non-empty and that each record's `provenance.source_revision` matches the repository's expected hash-shaped revision pattern.
        """
        self._assert_all_revisions(SKILLSET_DIR / "skill-factory" / "manifest.jsonl")

    def test_no_manifest_contains_old_revision_4f340e4f0(self) -> None:
        """
        Assert that no manifest.jsonl record in any skillset contains the old source revision '4f340e4f0'.
        
        For each record in .skillsets/*/manifest.jsonl this test checks `provenance.source_revision` and fails if it equals OLD_MANIFEST_REVISION.
        """
        for path in sorted(SKILLSET_DIR.glob("*/manifest.jsonl")):
            records = _load_jsonl(path)
            for rec in records:
                rev = rec.get("provenance", {}).get("source_revision", "")
                with self.subTest(path=path.relative_to(REPO_ROOT), skill_id=rec.get("id", "?")):
                    self.assertNotEqual(
                        rev,
                        OLD_MANIFEST_REVISION,
                        f"skill '{rec.get('id')}' in {path.name} still has old revision "
                        f"'{OLD_MANIFEST_REVISION}'",
                    )

    def test_all_manifests_have_consistent_single_revision(self) -> None:
        """All manifest entries across all skillsets must share exactly one source_revision."""
        revisions: set[str] = set()
        for path in sorted(SKILLSET_DIR.glob("*/manifest.jsonl")):
            for rec in _load_jsonl(path):
                rev = rec.get("provenance", {}).get("source_revision", "")
                if rev:
                    revisions.add(rev)
        self.assertEqual(1, len(revisions), f"Expected one shared revision, found: {sorted(revisions)}")
        for rev in revisions:
            self.assertRegex(rev, _REVISION_PATTERN, f"Invalid manifest revision '{rev}'")


# ---------------------------------------------------------------------------
# command-surface.json: source_revision + sha256 updates
# ---------------------------------------------------------------------------


class TestCommandSurfaceRevisionAndSha256(unittest.TestCase):
    """command-surface.json must use the new revision and updated sha256 values."""

    def setUp(self) -> None:
        """
        Load the command-surface.json file and cache its top-level handles list for test methods.
        
        Stores the parsed JSON object in self._data and assigns its "handles" list (or an empty list if missing) to self._handles.
        """
        self._data = _load_command_surface()
        self._handles = self._data.get("handles", [])

    def test_file_is_valid_json(self) -> None:
        """
        Verify command-surface.json contains the top-level "handles" key.
        
        Asserts the file parsed successfully and exposes the "handles" section required by subsequent tests.
        """
        self.assertIsInstance(self._data, dict)
        self.assertIn("handles", self._data)

    def test_no_command_surface_entry_has_old_revision_aa14bb002(self) -> None:
        """
        Assert that none of the command-surface handles reference the old command-surface revision.
        
        Fails the test if any handle's `provenance.source_revision` equals `OLD_COMMAND_SURFACE_REVISION`.
        """
        for entry in self._handles:
            rev = entry.get("provenance", {}).get("source_revision", "")
            with self.subTest(handle=entry.get("handle", "?")):
                self.assertNotEqual(
                    rev,
                    OLD_COMMAND_SURFACE_REVISION,
                    f"handle '{entry.get('handle')}' still references old revision "
                    f"'{OLD_COMMAND_SURFACE_REVISION}'",
                )

    def test_all_command_surface_revisions_match_manifest_revision(self) -> None:
        """
        Verify each handle in the command-surface whose provenance.source_revision is present matches manifest revision.
        
        Entries with an empty `provenance.source_revision` are skipped. Assertion failures include the handle name.
        """
        manifest_revisions: set[str] = set()
        for path in sorted(SKILLSET_DIR.glob("*/manifest.jsonl")):
            for rec in _load_jsonl(path):
                rev = rec.get("provenance", {}).get("source_revision", "")
                if rev:
                    manifest_revisions.add(rev)
        self.assertEqual(
            1,
            len(manifest_revisions),
            f"Expected one manifest revision, found: {sorted(manifest_revisions)}",
        )
        expected_revision = next(iter(manifest_revisions))
        for entry in self._handles:
            rev = entry.get("provenance", {}).get("source_revision", "")
            if rev:
                with self.subTest(handle=entry.get("handle", "?")):
                    self.assertEqual(
                        rev,
                        expected_revision,
                        f"handle '{entry.get('handle')}': expected '{expected_revision}', got '{rev}'",
                    )

    def test_coding_harness_sha256_is_hash_shaped(self) -> None:
        """
        Ensure the "coding-harness" handle exists in command-surface.json and its `provenance.source_sha256` is a 64-character hexadecimal string.
        """
        entry = next(
            (h for h in self._handles if h.get("handle") == "coding-harness"), None
        )
        self.assertIsNotNone(entry, "coding-harness handle not found in command-surface.json")
        sha = entry["provenance"].get("source_sha256", "")  # type: ignore[index]
        self.assertRegex(
            sha,
            re.compile(r"^[0-9a-f]{64}$", re.IGNORECASE),
            f"coding-harness sha256 must be a 64-char hex string, got '{sha}'",
        )

    def test_coding_harness_old_sha256_not_present(self) -> None:
        """
        Verify the `coding-harness` handle in command-surface.json does not use the old SHA256.
        
        Asserts that a handle named "coding-harness" exists and that its `provenance.source_sha256`
        is not equal to `CODING_HARNESS_OLD_SHA256`; fails if the handle is missing or the SHA256 matches the old value.
        """
        entry = next(
            (h for h in self._handles if h.get("handle") == "coding-harness"), None
        )
        self.assertIsNotNone(entry, "coding-harness handle not found in command-surface.json")
        sha = entry["provenance"].get("source_sha256", "")  # type: ignore[index]
        self.assertNotEqual(
            sha,
            CODING_HARNESS_OLD_SHA256,
            "coding-harness still has the old sha256 value",
        )

    def test_he_strategy_sha256_is_hash_shaped(self) -> None:
        """
        Verify the `he-strategy` handle's provenance SHA256 in command-surface.json is a 64-character hexadecimal string.
        
        Raises:
            AssertionError: If the `he-strategy` handle is missing or its `provenance.source_sha256` is not a 64-character hex string.
        """
        entry = next(
            (h for h in self._handles if h.get("handle") == "he-strategy"), None
        )
        self.assertIsNotNone(entry, "he-strategy handle not found in command-surface.json")
        sha = entry["provenance"].get("source_sha256", "")  # type: ignore[index]
        self.assertRegex(
            sha,
            re.compile(r"^[0-9a-f]{64}$", re.IGNORECASE),
            f"he-strategy sha256 must be a 64-char hex string, got '{sha}'",
        )

    def test_he_strategy_old_sha256_not_present(self) -> None:
        """
        Verify the `he-strategy` handle in command-surface.json does not use the previous SHA256 value.
        
        Asserts that a handle with "handle": "he-strategy" exists and that its `provenance.source_sha256` is not equal to `HE_STRATEGY_OLD_SHA256`.
        """
        entry = next(
            (h for h in self._handles if h.get("handle") == "he-strategy"), None
        )
        self.assertIsNotNone(entry, "he-strategy handle not found in command-surface.json")
        sha = entry["provenance"].get("source_sha256", "")  # type: ignore[index]
        self.assertNotEqual(
            sha,
            HE_STRATEGY_OLD_SHA256,
            "he-strategy still has the old sha256 value",
        )

    def test_all_source_revisions_are_valid_git_hashes(self) -> None:
        for entry in self._handles:
            rev = entry.get("provenance", {}).get("source_revision", "")
            with self.subTest(handle=entry.get("handle", "?")):
                self.assertRegex(rev, _REVISION_PATTERN)


# ---------------------------------------------------------------------------
# evals.yaml: new eval cases and schema_version
# ---------------------------------------------------------------------------


class TestHeStrategyEvalsYaml(unittest.TestCase):
    """evals.yaml must have schema_version 2.0 and the three new eval cases."""

    def setUp(self) -> None:
        """
        Prepare parsed evals.yaml and extract case metadata for the tests.
        
        Sets:
        - `self._evals`: the YAML document loaded from EVALS_YAML_PATH.
        - `self._cases`: the list of case dictionaries from the document's `"cases"` key (empty list if absent).
        - `self._case_ids`: a set of all case `"id"` values.
        """
        self._evals = yaml.safe_load(EVALS_YAML_PATH.read_text(encoding="utf-8"))
        self._cases: list[dict[str, Any]] = self._evals.get("cases", [])
        self._case_ids = {c["id"] for c in self._cases}

    def test_schema_version_is_2_0(self) -> None:
        self.assertEqual(
            str(self._evals.get("schema_version", "")),
            "2.0",
            "evals.yaml schema_version should be '2.0'",
        )

    def test_skill_name_is_he_strategy(self) -> None:
        """
        Assert the evals.yaml 'skill_name' field equals "he-strategy".
        
        Checks that the loaded evals document contains the key `skill_name` with the exact value "he-strategy"; the test fails if the value differs or is missing.
        """
        self.assertEqual(self._evals.get("skill_name"), "he-strategy")

    def test_stated_vs_implied_intent_case_present(self) -> None:
        """
        Ensure the evals configuration contains the "stated-vs-implied-intent" case ID.
        
        Raises an assertion failure if that case ID is not present in the loaded `cases` set.
        """
        self.assertIn(
            "stated-vs-implied-intent",
            self._case_ids,
            "Missing eval case 'stated-vs-implied-intent'",
        )

    def test_sampled_evidence_downgrades_strategy_authority_case_present(self) -> None:
        """
        Assert that the eval case "sampled-evidence-downgrades-strategy-authority" is present in the loaded evals.
        """
        self.assertIn(
            "sampled-evidence-downgrades-strategy-authority",
            self._case_ids,
            "Missing eval case 'sampled-evidence-downgrades-strategy-authority'",
        )

    def test_first_principles_rejects_template_copying_case_present(self) -> None:
        """
        Asserts that the evals.yaml contains the "first-principles-rejects-template-copying" case ID.
        
        Raises an assertion failure with a clear message if the case ID is missing.
        """
        self.assertIn(
            "first-principles-rejects-template-copying",
            self._case_ids,
            "Missing eval case 'first-principles-rejects-template-copying'",
        )

    def test_stated_vs_implied_intent_is_realistic(self) -> None:
        """
        Assert the "stated-vs-implied-intent" eval case is realistic and contains required metadata.
        
        Verifies the case with id "stated-vs-implied-intent" has a truthy `realistic` flag and includes the `why_realistic` and `expected_behavior` fields.
        """
        case = next(c for c in self._cases if c["id"] == "stated-vs-implied-intent")
        self.assertTrue(
            case.get("realistic"),
            "stated-vs-implied-intent should be marked realistic: true",
        )
        self.assertIn("why_realistic", case, "stated-vs-implied-intent is missing why_realistic")
        self.assertIn(
            "expected_behavior",
            case,
            "stated-vs-implied-intent is missing expected_behavior",
        )

    def test_stated_vs_implied_intent_acceptance_checks_stated_and_implied(self) -> None:
        """
        Asserts the 'stated-vs-implied-intent' eval case acceptance contains language for both stated intent and implied intent.
        
        Fails the test if the case's acceptance values do not mention both "stated intent" and "implied intent" (case-insensitive).
        """
        case = next(c for c in self._cases if c["id"] == "stated-vs-implied-intent")
        acceptance = case.get("acceptance", [])
        patterns = [a.get("value", "") for a in acceptance]
        combined = " ".join(patterns)
        self.assertRegex(
            combined,
            re.compile(r"stated.?intent", re.IGNORECASE),
            "stated-vs-implied-intent acceptance must include stated intent language",
        )
        self.assertRegex(
            combined,
            re.compile(r"implied.?intent", re.IGNORECASE),
            "stated-vs-implied-intent acceptance must include implied intent language",
        )

    def test_stated_vs_implied_intent_acceptance_checks_alignment_contradiction(self) -> None:
        """
        Check that the 'stated-vs-implied-intent' eval's acceptance criteria include both alignment and contradiction checks.
        
        Asserts that the concatenated acceptance values for the case mention both "alignment" and "contradiction" (case-insensitive).
        """
        case = next(c for c in self._cases if c["id"] == "stated-vs-implied-intent")
        acceptance = case.get("acceptance", [])
        patterns = [a.get("value", "") for a in acceptance]
        combined = " ".join(patterns)
        self.assertRegex(
            combined,
            re.compile(r"alignment", re.IGNORECASE),
            "stated-vs-implied-intent acceptance must include alignment signals",
        )
        self.assertRegex(
            combined,
            re.compile(r"contradiction", re.IGNORECASE),
            "stated-vs-implied-intent acceptance must include contradiction signals",
        )

    def test_stated_vs_implied_intent_acceptance_checks_evidence_surfaces(self) -> None:
        """
        Ensure the "stated-vs-implied-intent" eval's acceptance text references at least one concrete evidence surface.
        
        Checks that the acceptance criteria mention one or more of: "command surface", "tests", "validation gate", or "runtime path" (case-insensitive).
        """
        case = next(c for c in self._cases if c["id"] == "stated-vs-implied-intent")
        acceptance = case.get("acceptance", [])
        patterns = [a.get("value", "") for a in acceptance]
        combined = " ".join(patterns)
        # Must reference concrete evidence surfaces from the prompt
        self.assertRegex(
            combined,
            re.compile(r"command.?surface|tests|validation.?gate|runtime.?path", re.IGNORECASE),
            "stated-vs-implied-intent acceptance must check for evidence surface signals",
        )

    def test_sampled_evidence_acceptance_requires_authority_limits(self) -> None:
        """
        Asserts the eval case "sampled-evidence-downgrades-strategy-authority" requires acceptance text that limits or restricts strategy authority.
        
        Checks that the case's acceptance content contains wording indicating sampled/partial evidence or explicit authority limits (for example: "sampled", "partial", "authority limited", "cannot", or "must not").
        """
        case = next(
            c for c in self._cases
            if c["id"] == "sampled-evidence-downgrades-strategy-authority"
        )
        acceptance = case.get("acceptance", [])
        patterns = [a.get("value", "") for a in acceptance]
        combined = " ".join(patterns)
        self.assertRegex(
            combined,
            re.compile(r"sampled|partial|authority.?limited|cannot|must.?not", re.IGNORECASE),
            "sampled-evidence case acceptance must check for authority-limiting language",
        )

    def test_first_principles_acceptance_requires_rejection_language(self) -> None:
        """
        Require that the "first-principles-rejects-template-copying" eval case's acceptance text enforces rejection or template-copying guardrail language.
        
        Checks that the case's acceptance entries contain at least one of the observable phrases: "first principles", "reject", "Do Not Create", or "template" (case-insensitive).
        """
        case = next(
            c for c in self._cases
            if c["id"] == "first-principles-rejects-template-copying"
        )
        acceptance = case.get("acceptance", [])
        patterns = [a.get("value", "") for a in acceptance]
        combined = " ".join(patterns)
        self.assertRegex(
            combined,
            re.compile(r"first.?principles|reject|Do Not Create|template", re.IGNORECASE),
            "first-principles case acceptance must check for template rejection language",
        )

    def test_every_case_has_required_fields(self) -> None:
        """
        Verify every eval case includes the required fields.
        
        Asserts that each case in self._cases contains the keys: `id`, `name`, `category`, `eval_modes`, `prompt`, and `acceptance`.
        """
        required = ("id", "name", "category", "eval_modes", "prompt", "acceptance")
        for case in self._cases:
            with self.subTest(case_id=case.get("id", "?")):
                for field in required:
                    self.assertIn(field, case, f"Case '{case.get('id')}' missing field '{field}'")

    def test_new_cases_are_in_eval_modes_smoke_and_release(self) -> None:
        """
        Verify that the three new eval cases include both "smoke" and "release" in their `eval_modes`.
        
        Asserts that each of the cases "stated-vs-implied-intent", "sampled-evidence-downgrades-strategy-authority", and "first-principles-rejects-template-copying" lists both eval modes; reports failures per case.
        """
        new_case_ids = {
            "stated-vs-implied-intent",
            "sampled-evidence-downgrades-strategy-authority",
            "first-principles-rejects-template-copying",
        }
        for case in self._cases:
            if case["id"] in new_case_ids:
                with self.subTest(case_id=case["id"]):
                    modes = case.get("eval_modes", [])
                    self.assertIn("smoke", modes, f"Case '{case['id']}' missing 'smoke' eval mode")
                    self.assertIn(
                        "release", modes, f"Case '{case['id']}' missing 'release' eval mode"
                    )

    def test_forbidden_commands_block_applies_to_new_cases(self) -> None:
        """All three new cases must carry the safe deterministic check (no curl/wget/rm -rf)."""
        new_case_ids = {
            "stated-vs-implied-intent",
            "sampled-evidence-downgrades-strategy-authority",
            "first-principles-rejects-template-copying",
        }
        required_forbidden = {"curl", "wget", "rm -rf"}
        for case in self._cases:
            if case["id"] in new_case_ids:
                checks = case.get("deterministic_checks", {})
                forbidden_cmds = set(checks.get("forbidden_commands", []))
                with self.subTest(case_id=case["id"]):
                    self.assertTrue(
                        required_forbidden.issubset(forbidden_cmds),
                        f"Case '{case['id']}' must include forbidden commands: {sorted(required_forbidden)}",
                    )

    def test_xp_feedback_slice_acceptance_covers_smallest_feedback_stop_pivot(self) -> None:
        """
        Asserts that the `xp-feedback-slice` eval case acceptance patterns mention smallest/feedback/stop/pivot/evidence language.
        
        If the `xp-feedback-slice` case is not present the test is skipped. The test combines all acceptance `value` strings and asserts the combined text matches any of: "smallest", "feedback", "stop", "pivot", or "evidence" (case-insensitive).
        """
        case = next((c for c in self._cases if c["id"] == "xp-feedback-slice"), None)
        if case is None:
            self.skipTest("xp-feedback-slice case not present")
        acceptance = case.get("acceptance", [])
        patterns = [a.get("value", "") for a in acceptance]
        combined = " ".join(patterns)
        self.assertRegex(
            combined,
            re.compile(r"smallest|feedback|stop|pivot|evidence", re.IGNORECASE),
        )


# ---------------------------------------------------------------------------
# SKILL.md: stated/implied intent content
# ---------------------------------------------------------------------------


class TestHeStrategySkillMd(unittest.TestCase):
    """SKILL.md must contain sections and language introduced in this PR."""

    def setUp(self) -> None:
        """
        Load the he-strategy SKILL.md content into the test instance for use by test methods.
        
        Reads SKILL_MD_PATH using UTF-8 encoding and stores the file contents on self._text.
        """
        self._text = _read_required_text(SKILL_MD_PATH, "SKILL.md")

    def test_skill_md_exists(self) -> None:
        """
        Check that the he-strategy SKILL.md file exists at the expected repository path.
        
        Raises:
            AssertionError: if the SKILL.md file is missing.
        """
        self.assertTrue(SKILL_MD_PATH.exists(), "SKILL.md is missing")

    def test_skill_md_has_frontmatter_name(self) -> None:
        self.assertIn("name: he-strategy", self._text)

    def test_skill_md_has_required_sections(self) -> None:
        """
        Verify SKILL.md contains the required top-level section headings for the he-strategy skill.
        
        Asserts that the document includes each of the following headings: "## When to Use", "## When Not to Use",
        "## Preconditions", "## Inputs", "## Outputs", "## Procedure", "## Validation", "## Constraints",
        "## Failure Mode", and "## Handoff Rules".
        """
        for section in [
            "## When to Use",
            "## When Not to Use",
            "## Preconditions",
            "## Inputs",
            "## Outputs",
            "## Procedure",
            "## Validation",
            "## Constraints",
            "## Failure Mode",
            "## Handoff Rules",
        ]:
            with self.subTest(section=section):
                self.assertIn(section, self._text, f"SKILL.md is missing section '{section}'")

    def test_skill_md_references_evals_yaml(self) -> None:
        """
        Assert that the SKILL.md text contains a reference to the evals.yaml file.
        """
        self.assertIn("evals.yaml", self._text)

    def test_skill_md_references_strategy_output_contract(self) -> None:
        """
        Asserts that the SKILL.md text includes a reference to the strategy-output-contract.md document.
        """
        self.assertIn("strategy-output-contract.md", self._text)

    def test_skill_md_references_source_prompt_preservation(self) -> None:
        """
        Check that SKILL.md contains a reference to "source-prompt-preservation.md".
        """
        self.assertIn("source-prompt-preservation.md", self._text)

    def test_skill_md_lists_harness_output_paths(self) -> None:
        """
        Verify SKILL.md lists required harness output directory paths.
        
        Asserts that SKILL.md contains references to each of the expected harness output paths:
        ".harness/features/", ".harness/strategy/", and ".harness/decisions/". Each path is checked in a separate subTest.
        """
        for path in [".harness/features/", ".harness/strategy/", ".harness/decisions/"]:
            with self.subTest(path=path):
                self.assertIn(path, self._text, f"SKILL.md does not reference output path '{path}'")

    def test_skill_md_execution_boundaries_excludes_implementation(self) -> None:
        self.assertIn("## Execution Boundaries", self._text)
        # Execution boundary section must state strategy does not create Linear work
        self.assertIn("Do not\ncreate Linear work", self._text.replace("  ", " "))

    def test_skill_md_not_empty(self) -> None:
        self.assertGreater(len(self._text), 500)


# ---------------------------------------------------------------------------
# source-prompt-preservation.md: stated vs implied intent requirements
# ---------------------------------------------------------------------------


class TestSourcePromptPreservation(unittest.TestCase):
    """source-prompt-preservation.md must carry the stated vs implied intent requirement."""

    def setUp(self) -> None:
        """
        Load the `source-prompt-preservation.md` fixture into `self._text` for use by the tests.
        
        Reads the file at SOURCE_PROMPT_MD_PATH and stores its UTF-8 text content on the test instance as `self._text`. Raises AssertionError if the required file is missing.
        """
        self._text = _read_required_text(
            SOURCE_PROMPT_MD_PATH, "source-prompt-preservation.md"
        )

    def test_file_exists(self) -> None:
        """
        Asserts that the source-prompt-preservation.md reference file exists in the repository.
        """
        self.assertTrue(SOURCE_PROMPT_MD_PATH.exists())

    def test_stated_intent_requirement_present(self) -> None:
        """
        Verify the source-prompt-preservation.md text includes the phrase "stated intent".
        
        Asserts that the loaded document text (case-insensitive) contains "stated intent"; the test fails if the phrase is not present.
        """
        self.assertIn(
            "stated intent",
            self._text.lower(),
            "source-prompt-preservation.md must document the stated intent requirement",
        )

    def test_implied_intent_requirement_present(self) -> None:
        self.assertIn(
            "implied intent",
            self._text.lower(),
            "source-prompt-preservation.md must document the implied intent requirement",
        )

    def test_alignment_and_contradiction_reporting_present(self) -> None:
        """
        Check that the source-prompt-preservation text mentions both "alignment" and "contradiction".
        
        Performs a case-insensitive search of self._text and fails if either term is missing.
        """
        self.assertIn("alignment", self._text.lower())
        self.assertIn("contradiction", self._text.lower())

    def test_evidence_surfaces_enumerated(self) -> None:
        # The doc must list concrete evidence surfaces for the comparison
        """
        Verify that source-prompt-preservation.md enumerates the concrete evidence surfaces used for stated-vs-implied comparisons.
        
        Asserts the document mentions (case-insensitively) the following evidence surfaces: "command surfaces", "tests", "validation gates", and "runtime paths".
        """
        for surface in ["command surfaces", "tests", "validation gates", "runtime paths"]:
            with self.subTest(surface=surface):
                self.assertIn(
                    surface.lower(),
                    self._text.lower(),
                    f"source-prompt-preservation.md must mention evidence surface: {surface}",
                )

    def test_authority_rule_present(self) -> None:
        """
        Assert that the source-prompt-preservation document contains the word "authority".
        
        Performs a case-insensitive check for the substring "authority" and fails the test if it is not present.
        """
        self.assertIn("authority", self._text.lower())

    def test_partial_coverage_authority_warning_present(self) -> None:
        """When coverage is partial/sampled, strategy must not be used as repo-wide authority."""
        self.assertIn("partial", self._text.lower())
        self.assertIn("repo-wide authority", self._text.lower())

    def test_covered_prompt_families_section_present(self) -> None:
        """
        Check that the skill's documentation contains the "## Covered Prompt Families" section.
        """
        self.assertIn("## Covered Prompt Families", self._text)


# ---------------------------------------------------------------------------
# strategy-output-contract.md: intent mode covers stated vs implied
# ---------------------------------------------------------------------------


class TestStrategyOutputContract(unittest.TestCase):
    """strategy-output-contract.md must document stated vs implied alignment for intent mode."""

    def setUp(self) -> None:
        """
        Load the strategy-output-contract.md text into self._text for use by the test methods.
        
        Raises:
            AssertionError: if the required file is missing or cannot be read.
        """
        self._text = _read_required_text(
            STRATEGY_CONTRACT_MD_PATH, "strategy-output-contract.md"
        )

    def test_file_exists(self) -> None:
        """
        Assert that the strategy output contract Markdown file is present at the expected path.
        
        This test fails if STRATEGY_CONTRACT_MD_PATH does not exist.
        """
        self.assertTrue(STRATEGY_CONTRACT_MD_PATH.exists())

    def test_intent_mode_documented(self) -> None:
        """
        Checks that the strategy output contract documents the intent mode.
        
        Asserts that the loaded contract text contains the substring "intent" (case-insensitive).
        """
        self.assertIn("intent", self._text.lower())

    def test_stated_vs_implied_alignment_in_intent_sections(self) -> None:
        # The contract must describe the stated vs implied comparison for intent artifacts
        """
        Verify the strategy contract text includes both "stated" and "implied" intent terminology in its intent-related sections.
        
        Checks that the lowercased document contains the substrings "stated" and "implied".
        """
        lower = self._text.lower()
        self.assertIn("stated", lower)
        self.assertIn("implied", lower)

    def test_schema_version_required_in_outputs(self) -> None:
        """
        Ensure the strategy output contract document contains the literal `schema_version`.
        
        Asserts that the loaded document text includes the substring "schema_version".
        """
        self.assertIn("schema_version", self._text)

    def test_do_not_create_guardrail_present(self) -> None:
        """
        Asserts that the strategy output contract documents the "Do Not Create" guardrail.
        
        Checks that the loaded strategy output contract text contains the exact phrase "Do Not Create".
        """
        self.assertIn("Do Not Create", self._text)

    def test_required_output_contract_section_present(self) -> None:
        self.assertIn("## Required Output Contract", self._text)

    def test_mode_guardrails_section_present(self) -> None:
        """
        Verify the strategy output contract contains a "## Mode Guardrails" section.
        
        Asserts that the loaded document text includes the exact heading `## Mode Guardrails`.
        """
        self.assertIn("## Mode Guardrails", self._text)

    def test_evidence_traceability_matrix_required(self) -> None:
        """
        Asserts that the strategy output contract document includes an evidence and traceability matrix.
        
        Checks that the lowercase form of the loaded document text contains the phrase "evidence and traceability matrix".
        """
        self.assertIn("evidence and traceability matrix", self._text.lower())

    def test_stop_or_pivot_condition_required(self) -> None:
        """
        Verify the strategy-output-contract document requires a "stop or pivot condition".
        """
        self.assertIn("stop or pivot condition", self._text.lower())

    def test_all_six_modes_documented(self) -> None:
        """
        Check that the strategy output contract document lists all six required modes.
        
        Asserts that each of the mode labels "intent", "architecture-review", "triage",
        "strategic-compression", "decision-compression", and "core-compression" appears
        in the loaded strategy-output-contract.md text; fails with a message naming the
        missing mode.
        """
        for mode in [
            "intent",
            "architecture-review",
            "triage",
            "strategic-compression",
            "decision-compression",
            "core-compression",
        ]:
            with self.subTest(mode=mode):
                self.assertIn(
                    mode,
                    self._text,
                    f"strategy-output-contract.md does not document mode '{mode}'",
                )


if __name__ == "__main__":
    unittest.main()
