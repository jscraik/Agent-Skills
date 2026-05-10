"""
Structural validation tests for files changed in this PR.

Covers:
  - All .skillsets/*/manifest.jsonl files: source_revision format, required fields
  - .skillsets/command-surface.json: source_revision format, updated autofix description
  - .mise.toml: new pylint entry and uv version bump
  - .gitignore: new artifacts/policy/ entry
  - .codex/environments/environment.toml: new Pylint action block
"""
import json
import re
import unittest
from pathlib import Path
from typing import Any, ClassVar

REPO_ROOT = Path(__file__).resolve().parents[2]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SKILLSET_MANIFEST_PATHS = sorted(
    REPO_ROOT.glob(".skillsets/*/manifest.jsonl")
)

COMMAND_SURFACE_PATH = REPO_ROOT / ".skillsets" / "command-surface.json"

MISE_TOML_PATH = REPO_ROOT / ".mise.toml"

GITIGNORE_PATH = REPO_ROOT / ".gitignore"

ENVIRONMENT_TOML_PATH = REPO_ROOT / ".codex" / "environments" / "environment.toml"


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    """Return a list of parsed JSON objects from a JSONL file."""
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


# Git short-hash format used by the skillset generator (7-9 hex chars followed
# by optional trailing chars). The PR changed "7b1cf7a49" to "0ae8c3e6d".
_REVISION_PATTERN = re.compile(r"^[0-9a-f]{7,}", re.IGNORECASE)


# ---------------------------------------------------------------------------
# Manifest JSONL structure
# ---------------------------------------------------------------------------

class TestManifestJsonlStructure(unittest.TestCase):
    """Each manifest.jsonl entry must satisfy structural invariants."""

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

    def _check_manifest(self, path: Path):
        records = _load_jsonl(path)
        self.assertGreater(
            len(records), 0, f"Manifest {path} is unexpectedly empty"
        )
        for i, rec in enumerate(records):
            with self.subTest(file=path.name, index=i, id=rec.get("id", "?")):
                for field in self.REQUIRED_FIELDS:
                    self.assertIn(field, rec, f"Missing field '{field}'")
                # provenance sub-fields
                prov = rec["provenance"]
                self.assertIn("source_revision", prov)
                self.assertIn("source_sha256", prov)
                self.assertIn("generator", prov)
                # source_revision must look like a git hash
                revision = prov["source_revision"]
                self.assertRegex(
                    revision,
                    _REVISION_PATTERN,
                    f"source_revision '{revision}' does not look like a git hash",
                )
                # triggers must be a list
                self.assertIsInstance(rec["triggers"], list)
                self.assertGreater(len(rec["triggers"]), 0)

    def test_agent_ops_manifest(self):
        path = REPO_ROOT / ".skillsets" / "agent-ops" / "manifest.jsonl"
        self._check_manifest(path)

    def test_backend_platform_manifest(self):
        path = REPO_ROOT / ".skillsets" / "backend-platform" / "manifest.jsonl"
        self._check_manifest(path)

    def test_content_publishing_manifest(self):
        path = REPO_ROOT / ".skillsets" / "content-publishing" / "manifest.jsonl"
        self._check_manifest(path)

    def test_frontend_ui_manifest(self):
        path = REPO_ROOT / ".skillsets" / "frontend-ui" / "manifest.jsonl"
        self._check_manifest(path)

    def test_harness_engineering_manifest(self):
        path = REPO_ROOT / ".skillsets" / "harness-engineering" / "manifest.jsonl"
        self._check_manifest(path)

    def test_mobile_native_manifest(self):
        path = REPO_ROOT / ".skillsets" / "mobile-native" / "manifest.jsonl"
        self._check_manifest(path)

    def test_plugin_factory_manifest(self):
        path = REPO_ROOT / ".skillsets" / "plugin-factory" / "manifest.jsonl"
        self._check_manifest(path)

    def test_product_strategy_manifest(self):
        path = REPO_ROOT / ".skillsets" / "product-strategy" / "manifest.jsonl"
        self._check_manifest(path)

    def test_security_ops_manifest(self):
        path = REPO_ROOT / ".skillsets" / "security-ops" / "manifest.jsonl"
        self._check_manifest(path)

    def test_skill_factory_manifest(self):
        path = REPO_ROOT / ".skillsets" / "skill-factory" / "manifest.jsonl"
        self._check_manifest(path)


class TestManifestSourceRevisionUpdated(unittest.TestCase):
    """All manifests in the PR should use the new source_revision 0ae8c3e6d."""

    _NEW_REVISION = "0ae8c3e6d"

    def _assert_revision(self, path: Path):
        records = _load_jsonl(path)
        for rec in records:
            rev = rec.get("provenance", {}).get("source_revision", "")
            self.assertEqual(
                rev,
                self._NEW_REVISION,
                f"Entry '{rec.get('id')}' in {path.name} still has old revision: {rev}",
            )

    def test_agent_ops_revision_updated(self):
        self._assert_revision(REPO_ROOT / ".skillsets" / "agent-ops" / "manifest.jsonl")

    def test_backend_platform_revision_updated(self):
        self._assert_revision(REPO_ROOT / ".skillsets" / "backend-platform" / "manifest.jsonl")

    def test_no_old_revision_in_any_manifest(self):
        """No manifest should still reference the old revision 7b1cf7a49."""
        old_revision = "7b1cf7a49"
        for manifest_path in SKILLSET_MANIFEST_PATHS:
            records = _load_jsonl(manifest_path)
            for rec in records:
                rev = rec.get("provenance", {}).get("source_revision", "")
                self.assertNotEqual(
                    rev,
                    old_revision,
                    f"Entry '{rec.get('id')}' in {manifest_path.name} still has old revision",
                )


class TestManifestAutofix(unittest.TestCase):
    """Validate the autofix skill entry in agent-ops manifest was updated."""

    def test_autofix_description_updated(self):
        path = REPO_ROOT / ".skillsets" / "agent-ops" / "manifest.jsonl"
        records = _load_jsonl(path)
        autofix = next((r for r in records if r.get("id") == "autofix"), None)
        self.assertIsNotNone(autofix, "autofix entry not found in agent-ops manifest")
        desc = autofix["description"]
        # New description must mention "fix every current unresolved"
        self.assertIn("fix every current unresolved", desc, f"Unexpected description: {desc}")

    def test_autofix_triggers_include_new_description_trigger(self):
        path = REPO_ROOT / ".skillsets" / "agent-ops" / "manifest.jsonl"
        records = _load_jsonl(path)
        autofix = next((r for r in records if r.get("id") == "autofix"), None)
        self.assertIsNotNone(autofix)
        triggers = autofix["triggers"]
        self.assertIn("autofix", triggers)


# ---------------------------------------------------------------------------
# command-surface.json
# ---------------------------------------------------------------------------

class TestCommandSurfaceJson(unittest.TestCase):
    def setUp(self):
        with open(COMMAND_SURFACE_PATH, encoding="utf-8") as fh:
            self._data = json.load(fh)

    def test_file_is_valid_json(self):
        """setUp already validated this; just assert the data is non-empty."""
        self.assertIsInstance(self._data, dict)

    def test_has_handles_list(self):
        # The command-surface.json schema uses "handles" (not "commands").
        self.assertIn("handles", self._data)
        self.assertIsInstance(self._data["handles"], list)

    def test_has_schema_version(self):
        self.assertIn("schema_version", self._data)
        self.assertEqual(self._data["schema_version"], "command-surface.v1")

    def test_all_source_revisions_use_new_hash(self):
        new_revision = "0ae8c3e6d"
        old_revision = "7b1cf7a49"
        for entry in self._data.get("handles", []):
            prov = entry.get("provenance", {})
            rev = prov.get("source_revision", "")
            if rev:
                self.assertNotEqual(
                    rev, old_revision,
                    f"Command '{entry.get('handle')}' still uses old revision {old_revision}"
                )
                self.assertEqual(
                    rev, new_revision,
                    f"Command '{entry.get('handle')}' has unexpected revision: {rev}"
                )

    def test_autofix_description_updated(self):
        handles = self._data.get("handles", [])
        autofix = next((c for c in handles if c.get("handle") == "autofix"), None)
        self.assertIsNotNone(autofix, "autofix entry not found in command-surface.json")
        desc = autofix.get("description", "")
        self.assertIn(
            "fix every current unresolved",
            desc,
            f"autofix description not updated: {desc}",
        )

    def test_autofix_source_sha256_updated(self):
        handles = self._data.get("handles", [])
        autofix = next((c for c in handles if c.get("handle") == "autofix"), None)
        self.assertIsNotNone(autofix)
        sha = autofix.get("provenance", {}).get("source_sha256", "")
        # The old sha256 for autofix was b618b921...
        self.assertNotEqual(
            sha,
            "b618b921fdfe5fc0b6a367101251c1fcae93bf87bbd4af6a195c23099223cc04",
            "autofix source_sha256 was not updated",
        )

    def test_all_handles_have_required_fields(self):
        required = ["handle", "description", "kind", "provenance"]
        for cmd in self._data.get("handles", []):
            for field in required:
                with self.subTest(handle=cmd.get("handle", "?"), field=field):
                    self.assertIn(field, cmd)

    def test_each_provenance_has_source_revision(self):
        for cmd in self._data.get("handles", []):
            prov = cmd.get("provenance", {})
            with self.subTest(handle=cmd.get("handle", "?")):
                self.assertIn("source_revision", prov)

    def test_handle_count_reflects_total_handles(self):
        """The declared handle_count must match the actual length of the handles list."""
        declared = self._data.get("handle_count", -1)
        actual = len(self._data.get("handles", []))
        self.assertEqual(declared, actual, "handle_count metadata does not match handles list length")


# ---------------------------------------------------------------------------
# .mise.toml
# ---------------------------------------------------------------------------

class TestMiseToml(unittest.TestCase):
    def setUp(self):
        self._content = MISE_TOML_PATH.read_text(encoding="utf-8")

    def test_pylint_entry_present(self):
        self.assertIn("pylint", self._content)

    def test_pylint_version_is_4_0_5(self):
        self.assertIn("4.0.5", self._content)

    def test_uv_version_bumped_to_0_11_3(self):
        self.assertIn("0.11.3", self._content)

    def test_old_uv_version_not_present(self):
        self.assertNotIn('"uv" = "0.10.9"', self._content)

    def test_pylint_installed_via_pipx(self):
        # The new entry should use the pipx backend
        self.assertIn("pipx:pylint", self._content)


# ---------------------------------------------------------------------------
# .gitignore
# ---------------------------------------------------------------------------

class TestGitignore(unittest.TestCase):
    def setUp(self):
        """
        Prepare test fixture by loading the repository .gitignore file into self._lines as a list of lines.
        
        Each line is decoded as UTF-8 and split on line boundaries; the resulting list preserves original ordering and excludes trailing newline characters.
        """
        self._lines = GITIGNORE_PATH.read_text(encoding="utf-8").splitlines()

    def test_artifacts_policy_entry_present(self):
        """
        Ensure the repository .gitignore includes an artifacts/policy/ ignore entry in either relative or leading-slash form.
        
        Checks that either "artifacts/policy/" or "/artifacts/policy/" appears among the file's lines.
        """
        self.assertTrue(
            "artifacts/policy/" in self._lines or "/artifacts/policy/" in self._lines
        )

    def test_original_infrastructure_artifacts_policy_still_present(self):
        self.assertIn("Infrastructure/artifacts/policy/", self._lines)

    def test_harness_runtime_outputs_ignored(self):
        for entry in [
            ".harness/backups/",
            ".harness/*.db",
            ".harness/ci-migrate-snapshots/",
        ]:
            self.assertIn(entry, self._lines)

    def test_harness_curated_roots_are_trackable(self):
        """
        Asserts that specific curated `.harness/` root directories are marked as trackable in `.gitignore`.

        Checks for the presence of negated ignore patterns that ensure the following curated roots are tracked: `!.harness/core/`, `!.harness/linear/`, `!.harness/refactors/`, `!.harness/specs/`, and `!.harness/review/`.
        """
        for entry in [
            "!.harness/core/",
            "!.harness/linear/",
            "!.harness/refactors/",
            "!.harness/specs/",
            "!.harness/review/",
        ]:
            self.assertIn(entry, self._lines)

    def test_plugins_zip_is_ignored(self):
        """Plugins/*.zip archives must be ignored so built plugin zips are not tracked."""
        self.assertIn("Plugins/*.zip", self._lines)

    def test_harness_root_marker_is_trackable(self):
        """The top-level !.harness/ negation must be present so the directory itself is trackable."""
        self.assertIn(".harness/", self._lines)
        self.assertIn("!.harness/", self._lines)

    def test_harness_core_recursive_content_is_trackable(self):
        """!.harness/core/** must be present so nested core policy files are tracked."""
        self.assertIn("!.harness/core/**", self._lines)

    def test_harness_decisions_are_trackable(self):
        """ADR and decision files under .harness/decisions/ must be tracked."""
        self.assertIn("!.harness/decisions/", self._lines)
        self.assertIn("!.harness/decisions/**", self._lines)

    def test_harness_features_are_trackable(self):
        """Feature intent and moat files under .harness/features/ must be tracked."""
        self.assertIn("!.harness/features/", self._lines)
        self.assertIn("!.harness/features/**", self._lines)

    def test_harness_plan_is_trackable(self):
        """Plan artifacts under .harness/plan/ must be tracked."""
        self.assertIn("!.harness/plan/", self._lines)
        self.assertIn("!.harness/plan/**", self._lines)

    def test_harness_memory_is_trackable(self):
        """Memory learnings under .harness/memory/ must be tracked."""
        self.assertIn("!.harness/memory/", self._lines)
        self.assertIn("!.harness/memory/**", self._lines)

    def test_harness_quality_is_trackable(self):
        """Quality criteria under .harness/quality/ must be tracked."""
        self.assertIn("!.harness/quality/", self._lines)
        self.assertIn("!.harness/quality/**", self._lines)

    def test_harness_json_files_are_trackable(self):
        """Contract JSON files at .harness/*.json must be tracked."""
        self.assertIn("!.harness/*.json", self._lines)

    def test_harness_strategy_triage_ideate_brainstorm_are_trackable(self):
        """Secondary reference dirs (strategy, triage, ideate, brainstorm) must be tracked."""
        for entry in [
            "!.harness/strategy/",
            "!.harness/strategy/**",
            "!.harness/triage/",
            "!.harness/triage/**",
            "!.harness/ideate/",
            "!.harness/ideate/**",
            "!.harness/brainstorm/",
            "!.harness/brainstorm/**",
        ]:
            with self.subTest(entry=entry):
                self.assertIn(entry, self._lines)

    def test_harness_ignore_block_precedes_negation_block(self):
        """Runtime-ignored entries must appear before the negation block in .gitignore."""
        ignore_idx = next(
            (i for i, line in enumerate(self._lines) if line == ".harness/backups/"), -1
        )
        negation_idx = next(
            (i for i, line in enumerate(self._lines) if line == "!.harness/"), -1
        )
        self.assertGreaterEqual(ignore_idx, 0, ".harness/backups/ entry not found")
        self.assertGreaterEqual(negation_idx, 0, "!.harness/ entry not found")
        self.assertLess(
            ignore_idx,
            negation_idx,
            "Runtime-ignore entries should precede the negation block",
        )

    def test_harness_db_ignore_precedes_json_negation(self):
        """.harness/*.db must be ignored before !.harness/*.json is re-included."""
        db_idx = next(
            (i for i, line in enumerate(self._lines) if line == ".harness/*.db"), -1
        )
        json_neg_idx = next(
            (i for i, line in enumerate(self._lines) if line == "!.harness/*.json"), -1
        )
        self.assertGreaterEqual(db_idx, 0, ".harness/*.db entry not found")
        self.assertGreaterEqual(json_neg_idx, 0, "!.harness/*.json entry not found")
        self.assertLess(
            db_idx,
            json_neg_idx,
            ".harness/*.db should be ignored before .harness/*.json is re-included",
        )


# ---------------------------------------------------------------------------
# .codex/environments/environment.toml


class TestEnvironmentToml(unittest.TestCase):
    def setUp(self):
        self._content = ENVIRONMENT_TOML_PATH.read_text(encoding="utf-8")

    def test_pylint_action_block_removed(self):
        """Pylint action must NOT be present after this PR removed it."""
        self.assertNotIn(
            'name = "Pylint"',
            self._content,
            "Pylint action was removed in this PR; 'name = \"Pylint\"' must not appear",
        )

    def test_pylint_version_command_removed(self):
        """'pylint --version' must not appear in any action after Pylint removal."""
        self.assertNotIn(
            "pylint --version",
            self._content,
            "Pylint action was removed; 'pylint --version' must not appear",
        )

    def test_pylint_existence_check_removed(self):
        """'command -v pylint' must not appear after Pylint action removal."""
        self.assertNotIn(
            "command -v pylint",
            self._content,
            "Pylint action was removed; 'command -v pylint' must not appear",
        )

    def test_strict_mode_present_in_remaining_actions(self):
        """'set -euo pipefail' must still be present in at least one remaining action."""
        self.assertIn("set -euo pipefail", self._content)

    def test_release_finalize_action_present(self):
        """'Release Finalize' action must be present (added in this PR)."""
        self.assertIn('name = "Release Finalize"', self._content)

    def test_setup_uses_path_candidate_loop(self):
        """setup script must use the new PATH candidate loop."""
        self.assertIn("for candidate in", self._content)
        self.assertIn('PATH="$candidate:$PATH"', self._content)

    def test_mise_now_conditional_in_setup(self):
        """mise execution must be conditional on 'command -v mise' in setup."""
        self.assertIn("if command -v mise >/dev/null 2>&1;", self._content)

    def test_mise_trust_allows_failure(self):
        """'mise trust' must allow failure with '|| true' in setup/Tools actions."""
        self.assertIn("mise trust --yes .mise.toml || true", self._content)

    def test_prepare_worktree_conditional_present(self):
        """setup must conditionally use scripts/prepare-worktree.sh if available."""
        self.assertIn("if [[ -f scripts/prepare-worktree.sh ]]", self._content)


if __name__ == "__main__":

