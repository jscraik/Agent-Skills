"""
Tests for PR changes validation.

Covers static artifact integrity for:
- .skillsets/command-surface.json (new file)
- .skillsets/*/manifest.jsonl (policy_identity / source_revision bump)
- Infrastructure/GOVERNANCE/context-budget.yaml
- Infrastructure/GOVERNANCE/runtime-separation/current.json
- .codex/environments/environment.toml (codex_env_common.sh integration)
"""

import json
import sys
import tomllib
import unittest
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
LIFECYCLE_DIR = REPO_ROOT / "Infrastructure" / "scripts" / "lifecycle-and-sync"
sys.path.insert(0, str(LIFECYCLE_DIR))

from selection_policy import SYSTEM_BRIDGE_SKILL_NAMES, policy_identity  # noqa: E402

COMMAND_SURFACE_PATH = REPO_ROOT / ".skillsets" / "command-surface.json"
CONTEXT_BUDGET_PATH = REPO_ROOT / "Infrastructure" / "GOVERNANCE" / "context-budget.yaml"
RUNTIME_SEPARATION_PATH = (
    REPO_ROOT / "Infrastructure" / "GOVERNANCE" / "runtime-separation" / "current.json"
)
ENVIRONMENT_TOML_PATH = REPO_ROOT / ".codex" / "environments" / "environment.toml"
SKILLSETS_DIR = REPO_ROOT / ".skillsets"

EXPECTED_POLICY_IDENTITY = policy_identity()
SYSTEM_BRIDGE_HANDLES = set(SYSTEM_BRIDGE_SKILL_NAMES)

MANIFEST_REQUIRED_FIELDS = {
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
}
PROVENANCE_REQUIRED_FIELDS = {
    "generator",
    "policy_identity",
    "projection_mode",
    "source_revision",
    "source_sha256",
}
HANDLE_REQUIRED_FIELDS = {
    "command_visibility",
    "description",
    "handle",
    "kind",
    "level",
    "owner",
    "provenance",
    "runtime_visibility",
    "source_path",
}
VALID_COMMAND_VISIBILITY = {"target", "orchestrator", "reviewer", "direct"}
VALID_LEVELS = {"atom", "molecule", "compound", "reference", "router"}
VALID_RISK = {"low", "medium", "high"}


def _load_all_manifest_rows() -> list[dict]:
    """Load all rows from all manifest.jsonl files under .skillsets/."""
    rows = []
    for manifest_file in sorted(SKILLSETS_DIR.glob("*/manifest.jsonl")):
        for line_number, line in enumerate(
            manifest_file.read_text(encoding="utf-8").splitlines(), start=1
        ):
            line = line.strip()
            if not line:
                continue
            rows.append(
                {
                    "file": manifest_file,
                    "line_number": line_number,
                    "row": json.loads(line),
                }
            )
    return rows


class TestCommandSurfaceJsonStructure(unittest.TestCase):
    """Validate the committed .skillsets/command-surface.json file."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.data = json.loads(COMMAND_SURFACE_PATH.read_text(encoding="utf-8"))
        cls.handles: list[dict] = cls.data.get("handles", [])

    def test_file_is_valid_json(self) -> None:
        """command-surface.json must be parseable JSON (regression guard)."""
        # Already guaranteed by setUpClass; this test makes the assertion explicit.
        self.assertIsInstance(self.data, dict)

    def test_generated_from_is_rooted_manifests(self) -> None:
        """PR switched projection mode to rooted; generated_from must reflect that."""
        self.assertEqual(self.data.get("generated_from"), "rooted_manifests")

    def test_handle_count_field_matches_handles_array_length(self) -> None:
        """handle_count must equal the actual number of entries in the handles array."""
        self.assertEqual(self.data["handle_count"], len(self.handles))

    def test_generated_command_handle_count_is_absent(self) -> None:
        """Command-surface metadata must not advertise generated wrapper files."""
        self.assertNotIn("generated_command_handle_count", self.data)

    def test_handle_count_is_not_empty(self) -> None:
        """The rooted command surface must expose generated handles without hard-coding churn."""
        self.assertGreater(self.data["handle_count"], 0)

    def test_each_handle_has_required_fields(self) -> None:
        """Every handle object must contain all required fields."""
        for handle in self.handles:
            with self.subTest(handle=handle.get("handle")):
                missing = HANDLE_REQUIRED_FIELDS - handle.keys()
                self.assertFalse(
                    missing,
                    f"Handle '{handle.get('handle')}' is missing fields: {missing}",
                )

    def test_target_handles_have_invoke_via(self) -> None:
        """Handles with command_visibility='target' must carry an invoke_via field."""
        for handle in self.handles:
            if handle.get("command_visibility") == "target":
                with self.subTest(handle=handle.get("handle")):
                    self.assertIn(
                        "invoke_via",
                        handle,
                        f"target handle '{handle['handle']}' missing invoke_via",
                    )
                    self.assertIsNotNone(handle["invoke_via"])

    def test_orchestrator_handles_do_not_have_invoke_via(self) -> None:
        """Handles with command_visibility='orchestrator' must not have invoke_via."""
        for handle in self.handles:
            if handle.get("command_visibility") == "orchestrator":
                with self.subTest(handle=handle.get("handle")):
                    self.assertNotIn(
                        "invoke_via",
                        handle,
                        f"orchestrator handle '{handle['handle']}' should not have invoke_via",
                    )

    def test_no_duplicate_handles(self) -> None:
        """All handle identifiers must be unique within the command surface."""
        seen: list[str] = [h["handle"] for h in self.handles]
        self.assertEqual(len(seen), len(set(seen)), "Duplicate handle identifiers found")

    def test_all_handles_use_new_policy_identity(self) -> None:
        """Every handle must carry the updated policy_identity from this PR."""
        for handle in self.handles:
            with self.subTest(handle=handle.get("handle")):
                prov = handle.get("provenance", {})
                self.assertEqual(
                    prov.get("policy_identity"),
                    EXPECTED_POLICY_IDENTITY,
                    f"Handle '{handle.get('handle')}' has wrong policy_identity",
                )

    def test_all_handles_runtime_visibility_is_supported(self) -> None:
        """Every handle must use a supported runtime_visibility policy."""
        for handle in self.handles:
            with self.subTest(handle=handle.get("handle")):
                self.assertIn(
                    handle.get("runtime_visibility"),
                    {"latent", "flat", "root", "hidden"},
                    f"Handle '{handle.get('handle')}' has wrong runtime_visibility",
                )

    def test_all_handles_kind_is_skill(self) -> None:
        """All handles in this surface are skill handles."""
        for handle in self.handles:
            with self.subTest(handle=handle.get("handle")):
                self.assertEqual(
                    handle.get("kind"),
                    "skill",
                    f"Handle '{handle.get('handle')}' has unexpected kind",
                )

    def test_all_command_visibility_values_are_valid(self) -> None:
        """command_visibility must be one of the enumerated valid values."""
        for handle in self.handles:
            with self.subTest(handle=handle.get("handle")):
                self.assertIn(
                    handle.get("command_visibility"),
                    VALID_COMMAND_VISIBILITY,
                    f"Handle '{handle.get('handle')}' has invalid command_visibility",
                )

    def test_all_levels_are_valid(self) -> None:
        """level must be one of the enumerated valid taxonomy values."""
        for handle in self.handles:
            with self.subTest(handle=handle.get("handle")):
                self.assertIn(
                    handle.get("level"),
                    VALID_LEVELS,
                    f"Handle '{handle.get('handle')}' has invalid level",
                )

    def test_all_provenance_blocks_have_rooted_projection_mode(self) -> None:
        """The PR enforces rooted projection; all provenance blocks must reflect it."""
        for handle in self.handles:
            with self.subTest(handle=handle.get("handle")):
                prov = handle.get("provenance", {})
                self.assertEqual(
                    prov.get("projection_mode"),
                    "rooted",
                    f"Handle '{handle.get('handle')}' has wrong projection_mode",
                )

    def test_provenance_source_sha256_is_non_empty(self) -> None:
        """Every provenance block must carry a non-empty source_sha256 digest."""
        for handle in self.handles:
            with self.subTest(handle=handle.get("handle")):
                prov = handle.get("provenance", {})
                self.assertTrue(
                    prov.get("source_sha256"),
                    f"Handle '{handle.get('handle')}' missing source_sha256",
                )

    def test_handles_do_not_include_command_handle_path(self) -> None:
        """Command-surface rows are metadata only and do not point to wrapper files."""
        for handle in self.handles:
            with self.subTest(handle=handle.get("handle")):
                self.assertNotIn("command_handle_path", handle)

    def test_source_paths_start_with_skills_or_plugins(self) -> None:
        """source_path must point into canonical source trees or system bridges."""
        for handle in self.handles:
            with self.subTest(handle=handle.get("handle")):
                src = handle.get("source_path", "")
                allowed_source = src.startswith("Skills/") or src.startswith("Plugins/")
                if handle.get("handle") in SYSTEM_BRIDGE_HANDLES:
                    allowed_source = allowed_source or src.startswith("skills-system/")
                self.assertTrue(
                    allowed_source,
                    f"Handle '{handle.get('handle')}' has non-canonical source_path: {src}",
                )

    def test_descriptions_are_non_empty_strings(self) -> None:
        """Every handle must carry a non-empty description string."""
        for handle in self.handles:
            with self.subTest(handle=handle.get("handle")):
                desc = handle.get("description", "")
                self.assertIsInstance(desc, str)
                self.assertTrue(desc.strip(), f"Handle '{handle.get('handle')}' has empty description")


class TestManifestJsonlStructure(unittest.TestCase):
    """Validate the committed .skillsets/*/manifest.jsonl files from this PR."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest_rows = _load_all_manifest_rows()

    def test_manifest_files_exist_for_each_skillset_directory(self) -> None:
        """Every skillset subdirectory must contain a manifest.jsonl file."""
        for subdir in sorted(SKILLSETS_DIR.iterdir()):
            if subdir.is_dir():
                manifest = subdir / "manifest.jsonl"
                self.assertTrue(
                    manifest.is_file(),
                    f"Missing manifest.jsonl in {subdir.name}",
                )

    def test_all_manifest_lines_are_valid_json_objects(self) -> None:
        """Each line in every manifest.jsonl must parse as a JSON object."""
        self.assertGreater(len(self.manifest_rows), 0, "No manifest rows found")
        for entry in self.manifest_rows:
            with self.subTest(file=entry["file"].name, line=entry["line_number"]):
                self.assertIsInstance(
                    entry["row"],
                    dict,
                    f"{entry['file']}:{entry['line_number']} is not a JSON object",
                )

    def test_all_manifests_use_new_policy_identity(self) -> None:
        """All manifests must match the active selection-policy identity."""
        for entry in self.manifest_rows:
            with self.subTest(id=entry["row"].get("id"), file=entry["file"].name):
                prov = entry["row"].get("provenance", {})
                self.assertEqual(
                    prov.get("policy_identity"),
                    EXPECTED_POLICY_IDENTITY,
                    f"Row '{entry['row'].get('id')}' in {entry['file'].name} has stale policy_identity",
                )

    def test_all_manifests_use_new_source_revision(self) -> None:
        """All manifests must carry a concrete short git source revision."""
        for entry in self.manifest_rows:
            with self.subTest(id=entry["row"].get("id"), file=entry["file"].name):
                prov = entry["row"].get("provenance", {})
                self.assertRegex(
                    prov.get("source_revision", ""),
                    r"^[0-9A-Fa-f]{7,}$",
                    f"Row '{entry['row'].get('id')}' in {entry['file'].name} has stale source_revision",
                )

    def test_all_manifests_use_rooted_projection_mode(self) -> None:
        """All manifests must use the rooted projection mode."""
        for entry in self.manifest_rows:
            with self.subTest(id=entry["row"].get("id"), file=entry["file"].name):
                prov = entry["row"].get("provenance", {})
                self.assertEqual(
                    prov.get("projection_mode"),
                    "rooted",
                    f"Row '{entry['row'].get('id')}' in {entry['file'].name} uses wrong projection_mode",
                )

    def test_all_manifest_rows_have_required_fields(self) -> None:
        """Each manifest row must contain all required fields."""
        for entry in self.manifest_rows:
            with self.subTest(id=entry["row"].get("id"), file=entry["file"].name):
                missing = MANIFEST_REQUIRED_FIELDS - entry["row"].keys()
                self.assertFalse(
                    missing,
                    f"Row '{entry['row'].get('id')}' in {entry['file'].name} missing: {missing}",
                )

    def test_all_manifest_provenance_blocks_have_required_fields(self) -> None:
        """Each provenance block must contain all required sub-fields."""
        for entry in self.manifest_rows:
            with self.subTest(id=entry["row"].get("id"), file=entry["file"].name):
                prov = entry["row"].get("provenance", {})
                missing = PROVENANCE_REQUIRED_FIELDS - prov.keys()
                self.assertFalse(
                    missing,
                    f"Provenance for '{entry['row'].get('id')}' in {entry['file'].name} missing: {missing}",
                )

    def test_triggers_are_lists_of_strings(self) -> None:
        """Each manifest row's triggers field must be a non-empty list of strings."""
        for entry in self.manifest_rows:
            with self.subTest(id=entry["row"].get("id"), file=entry["file"].name):
                triggers = entry["row"].get("triggers")
                self.assertIsInstance(
                    triggers,
                    list,
                    f"triggers for '{entry['row'].get('id')}' is not a list",
                )
                self.assertGreater(
                    len(triggers),
                    0,
                    f"triggers for '{entry['row'].get('id')}' is empty",
                )
                for t in triggers:
                    self.assertIsInstance(
                        t,
                        str,
                        f"Non-string trigger in '{entry['row'].get('id')}': {t!r}",
                    )

    def test_risk_values_are_valid(self) -> None:
        """risk field must be one of the valid enumerated values."""
        for entry in self.manifest_rows:
            with self.subTest(id=entry["row"].get("id"), file=entry["file"].name):
                self.assertIn(
                    entry["row"].get("risk"),
                    VALID_RISK,
                    f"Row '{entry['row'].get('id')}' has invalid risk value",
                )

    def test_levels_are_valid(self) -> None:
        """level field must be one of the enumerated taxonomy values."""
        for entry in self.manifest_rows:
            with self.subTest(id=entry["row"].get("id"), file=entry["file"].name):
                self.assertIn(
                    entry["row"].get("level"),
                    VALID_LEVELS,
                    f"Row '{entry['row'].get('id')}' has invalid level",
                )

    def test_runtime_visibility_is_supported(self) -> None:
        """All manifest rows must use a supported runtime_visibility policy."""
        for entry in self.manifest_rows:
            with self.subTest(id=entry["row"].get("id"), file=entry["file"].name):
                self.assertIn(
                    entry["row"].get("runtime_visibility"),
                    {"latent", "flat", "root", "hidden"},
                    f"Row '{entry['row'].get('id')}' has unexpected runtime_visibility",
                )

    def test_source_paths_use_canonical_prefix(self) -> None:
        """source_path in manifests must start with Skills/ or Plugins/."""
        for entry in self.manifest_rows:
            with self.subTest(id=entry["row"].get("id"), file=entry["file"].name):
                src = entry["row"].get("source_path", "")
                self.assertTrue(
                    src.startswith("Skills/") or src.startswith("Plugins/"),
                    f"Row '{entry['row'].get('id')}' has non-canonical source_path: {src}",
                )

    def test_provenance_source_sha256_is_non_empty(self) -> None:
        """provenance.source_sha256 must be a non-empty hex digest string."""
        for entry in self.manifest_rows:
            with self.subTest(id=entry["row"].get("id"), file=entry["file"].name):
                sha = entry["row"].get("provenance", {}).get("source_sha256", "")
                self.assertTrue(
                    sha,
                    f"Row '{entry['row'].get('id')}' has empty source_sha256",
                )

    def test_generator_is_context_budgeted_skillsets(self) -> None:
        """All provenance blocks must identify the canonical generator."""
        for entry in self.manifest_rows:
            with self.subTest(id=entry["row"].get("id"), file=entry["file"].name):
                gen = entry["row"].get("provenance", {}).get("generator", "")
                self.assertEqual(
                    gen,
                    "context-budgeted-skillsets.v1",
                    f"Row '{entry['row'].get('id')}' has unexpected generator: {gen}",
                )

    def test_skill_set_matches_parent_directory(self) -> None:
        """skill_set in each row must match the name of its containing directory."""
        for entry in self.manifest_rows:
            parent_name = entry["file"].parent.name
            with self.subTest(id=entry["row"].get("id"), file=entry["file"].name):
                self.assertEqual(
                    entry["row"].get("skill_set"),
                    parent_name,
                    f"skill_set mismatch in {entry['file']}: expected '{parent_name}'",
                )

    def test_no_duplicate_ids_within_a_skillset(self) -> None:
        """Within a single skillset manifest, all skill IDs must be unique."""
        by_file: dict[Path, list[str]] = {}
        for entry in self.manifest_rows:
            by_file.setdefault(entry["file"], []).append(entry["row"].get("id", ""))
        for manifest_file, ids in by_file.items():
            with self.subTest(file=manifest_file.name):
                self.assertEqual(
                    len(ids),
                    len(set(ids)),
                    f"Duplicate IDs in {manifest_file}: {ids}",
                )

    def test_descriptions_are_non_empty_strings(self) -> None:
        """Every manifest row must have a non-empty description."""
        for entry in self.manifest_rows:
            with self.subTest(id=entry["row"].get("id"), file=entry["file"].name):
                desc = entry["row"].get("description", "")
                self.assertIsInstance(desc, str)
                self.assertTrue(
                    desc.strip(),
                    f"Row '{entry['row'].get('id')}' has empty description",
                )


class TestRuntimeSeparationCurrentJson(unittest.TestCase):
    """Validate Infrastructure/GOVERNANCE/runtime-separation/current.json."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.data = json.loads(RUNTIME_SEPARATION_PATH.read_text(encoding="utf-8"))

    def test_file_is_valid_json(self) -> None:
        """current.json must be parseable JSON."""
        self.assertIsInstance(self.data, dict)

    def test_schema_version_is_correct(self) -> None:
        """schema_version must match the expected runtime-separation schema identifier."""
        self.assertEqual(
            self.data.get("schema_version"),
            "runtime-separation-current.v1",
        )

    def test_status_matches_recorded_issues(self) -> None:
        """The committed baseline status must honestly reflect recorded issues."""
        expected = "healthy" if not self.data.get("issues") else "degraded"
        self.assertEqual(self.data.get("status"), expected)

    def test_plugin_package_root_parity_failures_are_issues(self) -> None:
        """Failed plugin package root parity rows must be visible as issues."""
        summary = self.data.get("summary", {})
        parity_rows = summary.get("plugin_package_root_parity", [])
        failed_plugins = {
            row.get("plugin_id")
            for row in parity_rows
            if isinstance(row, dict) and row.get("parity_result") == "fail"
        }
        issue_checks = {
            issue.get("check")
            for issue in self.data.get("issues", [])
            if isinstance(issue, dict)
        }
        missing = {
            f"plugin_package_root_parity.{plugin_id}"
            for plugin_id in failed_plugins
            if plugin_id
        } - issue_checks
        self.assertFalse(missing, f"Missing parity issues: {sorted(missing)}")

    def test_required_top_level_fields_present(self) -> None:
        """All mandatory top-level fields must be present."""
        required = {"schema_version", "status", "issues", "summary"}
        missing = required - self.data.keys()
        self.assertFalse(missing, f"Missing top-level fields: {missing}")

    def test_summary_policy_identity_matches_pr_policy(self) -> None:
        """summary.policy_identity must match the new policy_identity from this PR."""
        policy = self.data.get("summary", {}).get("policy_identity", "")
        self.assertEqual(
            policy,
            EXPECTED_POLICY_IDENTITY,
            "runtime-separation/current.json has stale policy_identity in summary",
        )

    def test_canonical_root_digest_starts_with_policy_identity(self) -> None:
        """canonical_root_digest must be anchored to the current policy_identity prefix."""
        digest = self.data.get("summary", {}).get("canonical_root_digest", "")
        self.assertTrue(
            digest.startswith(EXPECTED_POLICY_IDENTITY),
            f"canonical_root_digest does not start with expected policy prefix: {digest!r}",
        )

    def test_summary_has_command_checks(self) -> None:
        """summary must contain command_checks mapping."""
        self.assertIn("command_checks", self.data.get("summary", {}))
        self.assertIsInstance(self.data["summary"]["command_checks"], dict)

    def test_command_checks_contain_required_entries(self) -> None:
        """The standard set of baseline command checks must all be present."""
        checks = self.data.get("summary", {}).get("command_checks", {})
        required_checks = {
            "plugins_doctor",
            "plugins_status",
            "repo_doctor_catalog",
            "repo_status",
            "repo_validate",
            "skills_list",
        }
        missing = required_checks - checks.keys()
        self.assertFalse(missing, f"Missing command checks: {missing}")

    def test_each_command_check_has_returncode(self) -> None:
        """Every individual command check must record its returncode.

        plugins_status is a nested dict of plugin_id -> command check; each
        sub-check must also carry a returncode.
        """
        checks = self.data.get("summary", {}).get("command_checks", {})
        for check_name, check_value in checks.items():
            if not isinstance(check_value, dict):
                continue
            # Detect leaf command check (has "command" or "returncode" directly).
            # plugins_status is a nested mapping whose values are the leaf checks.
            if "returncode" in check_value:
                with self.subTest(check=check_name):
                    self.assertIn(
                        "returncode",
                        check_value,
                        f"Command check '{check_name}' missing returncode",
                    )
            else:
                # Treat as nested mapping; validate each inner leaf check.
                for plugin_id, plugin_check in check_value.items():
                    if isinstance(plugin_check, dict):
                        with self.subTest(check=check_name, plugin=plugin_id):
                            self.assertIn(
                                "returncode",
                                plugin_check,
                                f"Plugin check '{check_name}.{plugin_id}' missing returncode",
                            )

    def test_reader_root_set_present(self) -> None:
        """summary.reader_root_set must be a non-empty list."""
        reader_root = self.data.get("summary", {}).get("reader_root_set")
        self.assertIsNotNone(reader_root)
        self.assertIsInstance(reader_root, list)
        self.assertGreater(len(reader_root), 0)


class TestContextBudgetYaml(unittest.TestCase):
    """Validate Infrastructure/GOVERNANCE/context-budget.yaml."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.data = yaml.safe_load(CONTEXT_BUDGET_PATH.read_text(encoding="utf-8"))

    def test_file_is_valid_yaml(self) -> None:
        """context-budget.yaml must parse as a YAML mapping."""
        self.assertIsInstance(self.data, dict)

    def test_required_top_level_sections_present(self) -> None:
        """context-budget.yaml must contain its three canonical top-level sections."""
        required = {"runtime_projection", "routing", "workouts"}
        missing = required - self.data.keys()
        self.assertFalse(missing, f"Missing sections: {missing}")

    def test_runtime_projection_has_required_fields(self) -> None:
        """runtime_projection section must carry all mandatory constraint keys."""
        section = self.data.get("runtime_projection", {})
        required = {
            "max_root_skill_sets",
            "max_root_description_words_total",
            "max_root_body_words_each",
        }
        missing = required - section.keys()
        self.assertFalse(missing, f"runtime_projection missing fields: {missing}")

    def test_routing_has_required_fields(self) -> None:
        """routing section must carry the max_candidates_returned constraint."""
        section = self.data.get("routing", {})
        self.assertIn("max_candidates_returned", section)

    def test_workouts_has_required_fields(self) -> None:
        """workouts section must carry the max_skill_context_tokens constraint."""
        section = self.data.get("workouts", {})
        self.assertIn("max_skill_context_tokens", section)

    def test_all_numeric_limits_are_positive_integers(self) -> None:
        """Every numeric budget limit must be a positive integer."""
        checks = [
            ("runtime_projection", "max_root_skill_sets"),
            ("runtime_projection", "max_root_description_words_total"),
            ("runtime_projection", "max_root_body_words_each"),
            ("routing", "max_candidates_returned"),
            ("workouts", "max_skill_context_tokens"),
        ]
        for section_name, field_name in checks:
            with self.subTest(section=section_name, field=field_name):
                value = self.data.get(section_name, {}).get(field_name)
                self.assertIsNotNone(
                    value, f"{section_name}.{field_name} is missing"
                )
                self.assertIsInstance(
                    value,
                    int,
                    f"{section_name}.{field_name} must be an integer, got {type(value).__name__}",
                )
                self.assertGreater(
                    value, 0, f"{section_name}.{field_name} must be positive"
                )

    def test_max_root_skill_sets_is_reasonable_upper_bound(self) -> None:
        """max_root_skill_sets should be a small, bounded number (not unbounded)."""
        value = self.data.get("runtime_projection", {}).get("max_root_skill_sets", 0)
        self.assertGreater(value, 0)
        self.assertLessEqual(value, 50, "max_root_skill_sets seems unreasonably large")

    def test_max_candidates_returned_is_bounded(self) -> None:
        """max_candidates_returned should be a small number suitable for routing."""
        value = self.data.get("routing", {}).get("max_candidates_returned", 0)
        self.assertGreater(value, 0)
        self.assertLessEqual(value, 20, "max_candidates_returned seems unreasonably large")


class TestEnvironmentTomlCodexEnvCommon(unittest.TestCase):
    """Validate .codex/environments/environment.toml codex_env_common.sh integration."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.raw = ENVIRONMENT_TOML_PATH.read_text(encoding="utf-8")
        with open(ENVIRONMENT_TOML_PATH, "rb") as f:
            cls.parsed = tomllib.load(f)

    def test_file_is_valid_toml(self) -> None:
        """environment.toml must parse as valid TOML."""
        self.assertIsInstance(self.parsed, dict)

    def test_setup_script_sources_codex_env_common(self) -> None:
        """[setup].script must source Infrastructure/scripts/codex-preflight/codex_env_common.sh."""
        setup_script: str = self.parsed.get("setup", {}).get("script", "")
        self.assertIn(
            "Infrastructure/scripts/codex-preflight/codex_env_common.sh",
            setup_script,
            "[setup].script does not source codex_env_common.sh",
        )

    def test_setup_script_calls_codex_apply_env(self) -> None:
        """[setup].script must call codex_apply_env after sourcing."""
        setup_script: str = self.parsed.get("setup", {}).get("script", "")
        self.assertIn(
            "codex_apply_env",
            setup_script,
            "[setup].script does not call codex_apply_env",
        )

    def test_setup_script_has_shellcheck_comment_for_codex_env_common(self) -> None:
        """[setup].script must include the shellcheck source annotation for codex_env_common.sh."""
        setup_script: str = self.parsed.get("setup", {}).get("script", "")
        self.assertIn(
            "# shellcheck source=Infrastructure/scripts/codex-preflight/codex_env_common.sh",
            setup_script,
            "[setup].script missing shellcheck annotation for codex_env_common.sh",
        )

    def _get_action_script(self, action_name: str) -> str:
        """Return the command script for a named [[actions]] entry, or empty string."""
        for action in self.parsed.get("actions", []):
            if action.get("name") == action_name:
                return action.get("command", "")
        return ""

    def test_tools_action_sources_codex_env_common(self) -> None:
        """The 'Tools' [[actions]] entry must source codex_env_common.sh."""
        script = self._get_action_script("Tools")
        self.assertTrue(script, "Could not find 'Tools' action in environment.toml")
        self.assertIn(
            "Infrastructure/scripts/codex-preflight/codex_env_common.sh",
            script,
            "Tools action does not source codex_env_common.sh",
        )

    def test_tools_action_calls_codex_apply_env(self) -> None:
        """The 'Tools' [[actions]] entry must call codex_apply_env."""
        script = self._get_action_script("Tools")
        self.assertIn(
            "codex_apply_env",
            script,
            "Tools action does not call codex_apply_env",
        )

    def test_tools_action_has_shellcheck_comment_for_codex_env_common(self) -> None:
        """The 'Tools' [[actions]] entry must include the shellcheck annotation."""
        script = self._get_action_script("Tools")
        self.assertIn(
            "# shellcheck source=Infrastructure/scripts/codex-preflight/codex_env_common.sh",
            script,
            "Tools action missing shellcheck annotation for codex_env_common.sh",
        )

    def test_mise_action_sources_codex_env_common(self) -> None:
        """The 'Mise' [[actions]] entry must source codex_env_common.sh."""
        script = self._get_action_script("Mise")
        self.assertTrue(script, "Could not find 'Mise' action in environment.toml")
        self.assertIn(
            "Infrastructure/scripts/codex-preflight/codex_env_common.sh",
            script,
            "Mise action does not source codex_env_common.sh",
        )

    def test_mise_action_calls_codex_apply_env(self) -> None:
        """The 'Mise' [[actions]] entry must call codex_apply_env."""
        script = self._get_action_script("Mise")
        self.assertIn(
            "codex_apply_env",
            script,
            "Mise action does not call codex_apply_env",
        )

    def test_mise_action_has_shellcheck_comment_for_codex_env_common(self) -> None:
        """The 'Mise' [[actions]] entry must include the shellcheck annotation."""
        script = self._get_action_script("Mise")
        self.assertIn(
            "# shellcheck source=Infrastructure/scripts/codex-preflight/codex_env_common.sh",
            script,
            "Mise action missing shellcheck annotation for codex_env_common.sh",
        )

    def test_codex_apply_env_always_follows_source_in_each_block(self) -> None:
        """
        In every block that sources codex_env_common.sh, codex_apply_env must
        appear on the very next non-empty line after the source statement.

        This guards against accidentally adding the source without the call.
        """
        scripts_to_check = [
            ("setup", self.parsed.get("setup", {}).get("script", "")),
        ]
        for action in self.parsed.get("actions", []):
            scripts_to_check.append((action.get("name", "?"), action.get("command", "")))

        for block_name, script in scripts_to_check:
            if "codex_env_common.sh" not in script:
                continue
            lines = script.splitlines()
            for idx, line in enumerate(lines):
                if "codex_env_common.sh" in line and line.strip().startswith("source"):
                    # Find the next non-empty line
                    next_lines = [candidate.strip() for candidate in lines[idx + 1:] if candidate.strip()]
                    with self.subTest(block=block_name):
                        self.assertTrue(
                            next_lines,
                            f"No line after source in '{block_name}'",
                        )
                        self.assertEqual(
                            next_lines[0],
                            "codex_apply_env",
                            f"codex_apply_env not immediately after source in '{block_name}'",
                        )

    def test_no_action_sources_codex_env_common_without_codex_apply_env(self) -> None:
        """
        If any action script sources codex_env_common.sh, it must also call
        codex_apply_env (guards against half-applied sourcing blocks).
        """
        for action in self.parsed.get("actions", []):
            script: str = action.get("command", "")
            if "codex_env_common.sh" in script:
                with self.subTest(action=action.get("name")):
                    self.assertIn(
                        "codex_apply_env",
                        script,
                        f"Action '{action.get('name')}' sources codex_env_common.sh but does not call codex_apply_env",
                    )


if __name__ == "__main__":
    unittest.main()
