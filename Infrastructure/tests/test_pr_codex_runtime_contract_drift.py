"""
Tests for PR: fix(skills): resolve runtime contract and reference drift in codex docs

Covers the specific changes introduced in this PR:

1. .skillsets/*/manifest.jsonl files: source_revision bumped from "36571edf1"
   to a new revision. Exact short hashes may drift as manifests regenerate;
   tests must derive current expectations from committed artifacts.
   The old "36571edf1" revision must be absent from all manifests.

2. .skillsets/command-surface.json:
   - source_revision bumped to "18cadc255" (from "f8d418165")
   - handle_count / generated_command_handle_count reduced from 108 to 106
   - "imagegen" skill entry removed entirely
   - codex-automation-architect: level changed from "compound" to "molecule",
     command_visibility changed from "orchestrator" to "target",
     invoke_via added as "agent-ops", description updated, sha256 updated
   - codex-environment-creator: description updated, sha256 updated
   - codex-agent-creator: sha256 updated
   - codex-hooks-builder: sha256 updated

3. Skills/agent-ops/codex-automation-architect/references/contract.yaml:
   - kinds list contains cron and heartbeat
   - runtime_contract section present with tools list
   - update_rule present

4. Skills/agent-ops/codex-automation-architect/SKILL.md:
   - frontmatter level reflects "molecule" classification
   - "heartbeat" and "cron" keywords present

5. Skills/agent-ops/codex-agent-creator/SKILL.md:
   - correct source structure (frontmatter, preconditions, procedure)

6. Plugin SKILL.md files: frontmatter structure valid

7. Negative tests: old revision strings must be absent.
"""

import json
import re
import unittest
from pathlib import Path

try:
    import yaml
    _YAML_AVAILABLE = True
except ImportError:
    _YAML_AVAILABLE = False

REPO_ROOT = Path(__file__).resolve().parents[2]

SKILLSETS_DIR = REPO_ROOT / ".skillsets"
COMMAND_SURFACE_PATH = SKILLSETS_DIR / "command-surface.json"

AGENT_OPS_MANIFEST = SKILLSETS_DIR / "agent-ops" / "manifest.jsonl"
BACKEND_PLATFORM_MANIFEST = SKILLSETS_DIR / "backend-platform" / "manifest.jsonl"
CONTENT_PUBLISHING_MANIFEST = SKILLSETS_DIR / "content-publishing" / "manifest.jsonl"
FRONTEND_UI_MANIFEST = SKILLSETS_DIR / "frontend-ui" / "manifest.jsonl"
HARNESS_ENGINEERING_MANIFEST = SKILLSETS_DIR / "harness-engineering" / "manifest.jsonl"
MOBILE_NATIVE_MANIFEST = SKILLSETS_DIR / "mobile-native" / "manifest.jsonl"
PLUGIN_FACTORY_MANIFEST = SKILLSETS_DIR / "plugin-factory" / "manifest.jsonl"
PRODUCT_STRATEGY_MANIFEST = SKILLSETS_DIR / "product-strategy" / "manifest.jsonl"
SECURITY_OPS_MANIFEST = SKILLSETS_DIR / "security-ops" / "manifest.jsonl"
SKILL_FACTORY_MANIFEST = SKILLSETS_DIR / "skill-factory" / "manifest.jsonl"

CODEX_AUTOMATION_ARCHITECT_SKILL = (
    REPO_ROOT / "Skills" / "agent-ops" / "codex-automation-architect" / "SKILL.md"
)
CODEX_AUTOMATION_ARCHITECT_CONTRACT = (
    REPO_ROOT / "Skills" / "agent-ops" / "codex-automation-architect" / "references" / "contract.yaml"
)
CODEX_AUTOMATION_ARCHITECT_TOOL_EXAMPLES = (
    REPO_ROOT / "Skills" / "agent-ops" / "codex-automation-architect" / "references" / "tool-examples.md"
)
CODEX_AGENT_CREATOR_SKILL = (
    REPO_ROOT / "Skills" / "agent-ops" / "codex-agent-creator" / "SKILL.md"
)
CODEX_AGENT_CREATOR_ROLE_CONFIG_EXAMPLES = (
    REPO_ROOT / "Skills" / "agent-ops" / "codex-agent-creator" / "references" / "role-config-examples.md"
)
CODEX_AGENT_CREATOR_ROLE_CREATION_GUIDE = (
    REPO_ROOT / "Skills" / "agent-ops" / "codex-agent-creator" / "references" / "role-creation-guide.md"
)
PLUGIN_FACTORY_ROUTER_SKILL = (
    REPO_ROOT / "Plugins" / "plugin-factory" / "skills" / "plugin-factory-router" / "SKILL.md"
)
PLUGIN_FACTORY_ROUTER_RUNTIME_REF = (
    REPO_ROOT
    / "Plugins"
    / "plugin-factory"
    / "skills"
    / "plugin-factory-router"
    / "references"
    / "current-codex-plugin-runtime.md"
)
PLUGIN_FACTORY_CODE_QUALITY_SKILL = (
    REPO_ROOT
    / "Plugins"
    / "plugin-factory"
    / "skills"
    / "code_quality_review"
    / "plugin-builder"
    / "SKILL.md"
)
SKILL_FACTORY_CODE_QUALITY_SKILL = (
    REPO_ROOT
    / "Plugins"
    / "skill-factory"
    / "skills"
    / "code_quality_review"
    / "skill-builder"
    / "SKILL.md"
)

def _read_uniform_manifest_revision(path: Path) -> str:
    revisions: set[str] = set()
    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            raw = raw.strip()
            if not raw:
                continue
            rec = json.loads(raw)
            revisions.add(rec.get("provenance", {}).get("source_revision", ""))
    if not revisions:
        raise RuntimeError(f"{path} has no source_revision values")
    if len(revisions) != 1:
        raise RuntimeError(f"{path} has inconsistent source_revision values: {sorted(revisions)}")
    return next(iter(revisions))


def _read_uniform_command_surface_revision(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    revisions = {
        handle.get("provenance", {}).get("source_revision", "")
        for handle in data.get("handles", [])
    }
    if not revisions:
        raise RuntimeError(f"{path} has no handle source_revision values")
    if len(revisions) != 1:
        raise RuntimeError(f"{path} has inconsistent handle source_revision values: {sorted(revisions)}")
    return next(iter(revisions))


# Runtime-derived expectations avoid stale hardcoded revision literals after manifest regeneration.
EXPECTED_AGENT_OPS_REVISION = _read_uniform_manifest_revision(AGENT_OPS_MANIFEST)
EXPECTED_COMMAND_SURFACE_REVISION = _read_uniform_command_surface_revision(COMMAND_SURFACE_PATH)

# Revisions that must NOT appear in any updated files (the pre-PR baseline)
OLD_MANIFEST_REVISION = "36571edf1"
OLD_COMMAND_SURFACE_REVISION = "f8d418165"

# Expected SHA-256 digests after this PR
CODEX_AGENT_CREATOR_EXPECTED_SHA256 = "0df107095598882d2bab44963b4c9cd999faf823c49757d1f25cf373297865cc"
CODEX_AUTOMATION_ARCHITECT_EXPECTED_SHA256 = "9021c11ad1bb56f794687db7aec51b530d24020d81cd37069adea10fd2a25a72"
CODEX_ENVIRONMENT_CREATOR_EXPECTED_SHA256 = "e4f4572fff638333e684626157169ae57c7a42e8f38843a9b7a8b4e774fe8fc6"
CODEX_HOOKS_BUILDER_EXPECTED_SHA256 = "6940a8d947632d4db297b1fb11386073908ac4a2f52b6d92176f651af759b661"

# Old SHA-256 values that must no longer appear
OLD_CODEX_AGENT_CREATOR_SHA256 = "870ccec5264509a2a438b0554bb86c3674773320e6ae96f82e9536cf6e2b1863"
OLD_CODEX_AUTOMATION_ARCHITECT_SHA256 = "b9eb5d9eb35d776022c95556a3658414db61aa914fc425dbe753d4df69f0ed54"
OLD_CODEX_ENVIRONMENT_CREATOR_SHA256 = "796264bc17a78477b433a7d12673f205c70e12fe45c66e404be837006467002e"
OLD_CODEX_HOOKS_BUILDER_SHA256 = "8ee26b30ccc0383b665d00d2ae5244d4eded6791438156ee1ddf2e03fe5d548d"

_REVISION_PATTERN = re.compile(r"^[0-9a-f]{7,}$", re.IGNORECASE)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_jsonl(path: Path) -> list[dict]:
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


def _find_record(records: list[dict], skill_id: str) -> dict | None:
    return next((r for r in records if r.get("id") == skill_id), None)


def _find_handle(handles: list[dict], handle_id: str) -> dict | None:
    return next((h for h in handles if h.get("handle") == handle_id), None)


# ---------------------------------------------------------------------------
# Manifest source_revision bump: all skillsets
# ---------------------------------------------------------------------------


class TestManifestSourceRevisionBump(unittest.TestCase):
    """Manifest source_revision must be updated; old baseline revision must be absent."""

    def _assert_all_use_revision(self, path: Path, expected: str) -> None:
        records = _load_jsonl(path)
        self.assertGreater(len(records), 0, f"{path.name} is empty")
        for rec in records:
            rev = rec.get("provenance", {}).get("source_revision", "")
            self.assertEqual(
                rev,
                expected,
                f"Entry '{rec.get('id')}' in {path.name} has unexpected revision '{rev}'",
            )

    def _assert_old_revision_absent(self, path: Path, old_rev: str) -> None:
        records = _load_jsonl(path)
        for rec in records:
            rev = rec.get("provenance", {}).get("source_revision", "")
            self.assertNotEqual(
                rev,
                old_rev,
                f"Entry '{rec.get('id')}' in {path.name} still carries old revision '{old_rev}'",
            )

    def _assert_all_use_valid_revision(self, path: Path) -> None:
        records = _load_jsonl(path)
        self.assertGreater(len(records), 0, f"{path.name} is empty")
        for rec in records:
            rev = rec.get("provenance", {}).get("source_revision", "")
            self.assertRegex(
                rev,
                _REVISION_PATTERN,
                f"Entry '{rec.get('id')}' in {path.name} has invalid source_revision '{rev}'",
            )

    def _collect_revisions(self, path: Path) -> set[str]:
        records = _load_jsonl(path)
        return {rec.get("provenance", {}).get("source_revision", "") for rec in records}

    def _manifest_uniform_revision(self, path: Path) -> str:
        revisions = self._collect_revisions(path)
        self.assertEqual(
            len(revisions),
            1,
            f"{path.name} has inconsistent source_revisions: {sorted(revisions)}",
        )
        return next(iter(revisions))

    def test_agent_ops_manifest_revision_is_runtime_derived(self):
        expected = self._manifest_uniform_revision(AGENT_OPS_MANIFEST)
        self._assert_all_use_revision(AGENT_OPS_MANIFEST, expected)

    def test_plugin_factory_manifest_revision_is_valid_and_not_old(self):
        self._assert_old_revision_absent(PLUGIN_FACTORY_MANIFEST, OLD_MANIFEST_REVISION)
        self._assert_all_use_valid_revision(PLUGIN_FACTORY_MANIFEST)

    def test_skill_factory_manifest_revision_is_valid_and_not_old(self):
        self._assert_old_revision_absent(SKILL_FACTORY_MANIFEST, OLD_MANIFEST_REVISION)
        self._assert_all_use_valid_revision(SKILL_FACTORY_MANIFEST)

    def test_backend_platform_manifest_revision_is_runtime_derived(self):
        expected = self._manifest_uniform_revision(BACKEND_PLATFORM_MANIFEST)
        self._assert_all_use_revision(BACKEND_PLATFORM_MANIFEST, expected)

    def test_content_publishing_manifest_revision_is_runtime_derived(self):
        expected = self._manifest_uniform_revision(CONTENT_PUBLISHING_MANIFEST)
        self._assert_all_use_revision(CONTENT_PUBLISHING_MANIFEST, expected)

    def test_frontend_ui_manifest_revision_is_runtime_derived(self):
        expected = self._manifest_uniform_revision(FRONTEND_UI_MANIFEST)
        self._assert_all_use_revision(FRONTEND_UI_MANIFEST, expected)

    def test_harness_engineering_manifest_revision_is_runtime_derived(self):
        expected = self._manifest_uniform_revision(HARNESS_ENGINEERING_MANIFEST)
        self._assert_all_use_revision(HARNESS_ENGINEERING_MANIFEST, expected)

    def test_mobile_native_manifest_revision_is_runtime_derived(self):
        expected = self._manifest_uniform_revision(MOBILE_NATIVE_MANIFEST)
        self._assert_all_use_revision(MOBILE_NATIVE_MANIFEST, expected)

    def test_product_strategy_manifest_revision_is_runtime_derived(self):
        expected = self._manifest_uniform_revision(PRODUCT_STRATEGY_MANIFEST)
        self._assert_all_use_revision(PRODUCT_STRATEGY_MANIFEST, expected)

    def test_security_ops_manifest_revision_is_runtime_derived(self):
        expected = self._manifest_uniform_revision(SECURITY_OPS_MANIFEST)
        self._assert_all_use_revision(SECURITY_OPS_MANIFEST, expected)

    # Old baseline revision must be absent everywhere
    def test_agent_ops_manifest_old_revision_absent(self):
        self._assert_old_revision_absent(AGENT_OPS_MANIFEST, OLD_MANIFEST_REVISION)

    def test_backend_platform_manifest_old_revision_absent(self):
        self._assert_old_revision_absent(BACKEND_PLATFORM_MANIFEST, OLD_MANIFEST_REVISION)

    def test_all_manifests_old_revision_absent(self):
        """The pre-PR baseline revision '36571edf1' must be gone from every manifest."""
        for manifest_path in sorted(SKILLSETS_DIR.glob("*/manifest.jsonl")):
            for rec in _load_jsonl(manifest_path):
                rev = rec.get("provenance", {}).get("source_revision", "")
                with self.subTest(file=manifest_path.name, id=rec.get("id")):
                    self.assertNotEqual(
                        rev,
                        OLD_MANIFEST_REVISION,
                        f"Stale pre-PR revision in '{rec.get('id')}' of {manifest_path.name}",
                    )

    def test_each_manifest_is_internally_consistent(self):
        """Within each manifest, every row must use the same source_revision."""
        for manifest_path in sorted(SKILLSETS_DIR.glob("*/manifest.jsonl")):
            revisions: set[str] = set()
            for rec in _load_jsonl(manifest_path):
                rev = rec.get("provenance", {}).get("source_revision", "")
                if rev:
                    revisions.add(rev)
            with self.subTest(file=manifest_path.name):
                self.assertEqual(
                    len(revisions),
                    1,
                    f"{manifest_path.name} has inconsistent source_revisions: {sorted(revisions)}",
                )

    def test_all_manifest_revisions_look_like_git_hashes(self):
        """Every source_revision across all manifests must match a git short-hash pattern."""
        for manifest_path in sorted(SKILLSETS_DIR.glob("*/manifest.jsonl")):
            for rec in _load_jsonl(manifest_path):
                rev = rec.get("provenance", {}).get("source_revision", "")
                with self.subTest(file=manifest_path.name, id=rec.get("id")):
                    self.assertRegex(
                        rev,
                        _REVISION_PATTERN,
                        f"source_revision '{rev}' in '{rec.get('id')}' is not a git hash",
                    )


# ---------------------------------------------------------------------------
# command-surface.json: source_revision bump
# ---------------------------------------------------------------------------


class TestCommandSurfaceSourceRevisionBump(unittest.TestCase):
    """command-surface.json must carry the new EXPECTED_COMMAND_SURFACE_REVISION in all entries."""

    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(COMMAND_SURFACE_PATH.read_text(encoding="utf-8"))
        cls.handles: list[dict] = cls.data.get("handles", [])

    def test_all_handles_use_new_revision(self):
        for handle in self.handles:
            with self.subTest(handle=handle.get("handle")):
                rev = handle.get("provenance", {}).get("source_revision", "")
                self.assertEqual(
                    rev,
                    EXPECTED_COMMAND_SURFACE_REVISION,
                    f"Handle '{handle.get('handle')}' still uses old revision '{rev}'",
                )

    def test_old_command_surface_revision_absent(self):
        """The old command-surface revision 'f8d418165' must no longer appear."""
        for handle in self.handles:
            with self.subTest(handle=handle.get("handle")):
                rev = handle.get("provenance", {}).get("source_revision", "")
                self.assertNotEqual(
                    rev,
                    OLD_COMMAND_SURFACE_REVISION,
                    f"Handle '{handle.get('handle')}' still carries old revision '{OLD_COMMAND_SURFACE_REVISION}'",
                )

    def test_all_handles_revision_is_valid_git_hash(self):
        for handle in self.handles:
            with self.subTest(handle=handle.get("handle")):
                rev = handle.get("provenance", {}).get("source_revision", "")
                self.assertRegex(
                    rev,
                    _REVISION_PATTERN,
                    f"Handle '{handle.get('handle')}' has non-hash revision: '{rev}'",
                )


# ---------------------------------------------------------------------------
# command-surface.json: handle count reduced to 106
# ---------------------------------------------------------------------------


class TestCommandSurfaceHandleCount(unittest.TestCase):
    """command-surface.json handle count must be 106 after imagegen removal."""

    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(COMMAND_SURFACE_PATH.read_text(encoding="utf-8"))
        cls.handles: list[dict] = cls.data.get("handles", [])

    def test_handle_count_is_106(self):
        self.assertEqual(
            self.data.get("handle_count"),
            106,
            f"Expected handle_count=106, got {self.data.get('handle_count')}",
        )

    def test_generated_command_handle_count_is_106(self):
        self.assertEqual(
            self.data.get("generated_command_handle_count"),
            106,
            f"Expected generated_command_handle_count=106, "
            f"got {self.data.get('generated_command_handle_count')}",
        )

    def test_handle_count_matches_actual_handles_array_length(self):
        self.assertEqual(
            self.data["handle_count"],
            len(self.handles),
            "handle_count field does not match actual handles array length",
        )

    def test_generated_count_matches_handle_count(self):
        self.assertEqual(
            self.data["generated_command_handle_count"],
            self.data["handle_count"],
        )

    def test_not_108(self):
        """Regression: count must not revert to old value of 108."""
        self.assertNotEqual(
            self.data.get("handle_count"),
            108,
            "handle_count reverted to pre-PR value of 108",
        )


# ---------------------------------------------------------------------------
# command-surface.json: imagegen skill removed
# ---------------------------------------------------------------------------


class TestImagegenSkillRemoved(unittest.TestCase):
    """The 'imagegen' skill must not appear in command-surface.json after this PR."""

    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(COMMAND_SURFACE_PATH.read_text(encoding="utf-8"))
        cls.handles: list[dict] = cls.data.get("handles", [])

    def test_imagegen_handle_absent(self):
        handle_ids = {h.get("handle") for h in self.handles}
        self.assertNotIn(
            "imagegen",
            handle_ids,
            "imagegen handle was not removed from command-surface.json",
        )

    def test_no_imagegen_source_path(self):
        for handle in self.handles:
            with self.subTest(handle=handle.get("handle")):
                src = handle.get("source_path", "")
                self.assertNotIn(
                    "imagegen",
                    src,
                    f"Unexpected imagegen source_path found in handle '{handle.get('handle')}'",
                )

    def test_no_imagegen_command_handle_path(self):
        for handle in self.handles:
            with self.subTest(handle=handle.get("handle")):
                path = handle.get("command_handle_path", "")
                self.assertNotIn(
                    "imagegen",
                    path,
                    f"Unexpected imagegen command_handle_path in handle '{handle.get('handle')}'",
                )


# ---------------------------------------------------------------------------
# codex-automation-architect changes in command-surface.json
# ---------------------------------------------------------------------------


class TestCodexAutomationArchitectCommandSurface(unittest.TestCase):
    """Validate the structural changes to codex-automation-architect in command-surface.json."""

    @classmethod
    def setUpClass(cls):
        data = json.loads(COMMAND_SURFACE_PATH.read_text(encoding="utf-8"))
        handles: list[dict] = data.get("handles", [])
        cls.entry = _find_handle(handles, "codex-automation-architect")

    def test_entry_exists(self):
        self.assertIsNotNone(
            self.entry,
            "codex-automation-architect not found in command-surface.json",
        )

    def test_level_is_molecule(self):
        self.assertEqual(
            self.entry.get("level"),
            "molecule",
            f"Expected level='molecule', got '{self.entry.get('level')}'",
        )

    def test_level_not_compound(self):
        """Regression: level must not revert to old value 'compound'."""
        self.assertNotEqual(
            self.entry.get("level"),
            "compound",
            "codex-automation-architect level reverted to 'compound'",
        )

    def test_command_visibility_is_target(self):
        self.assertEqual(
            self.entry.get("command_visibility"),
            "target",
            f"Expected command_visibility='target', got '{self.entry.get('command_visibility')}'",
        )

    def test_command_visibility_not_orchestrator(self):
        """Regression: command_visibility must not revert to old value 'orchestrator'."""
        self.assertNotEqual(
            self.entry.get("command_visibility"),
            "orchestrator",
            "codex-automation-architect command_visibility reverted to 'orchestrator'",
        )

    def test_invoke_via_is_agent_ops(self):
        self.assertEqual(
            self.entry.get("invoke_via"),
            "agent-ops",
            f"Expected invoke_via='agent-ops', got '{self.entry.get('invoke_via')}'",
        )

    def test_invoke_via_present(self):
        """target handles must carry invoke_via."""
        self.assertIn("invoke_via", self.entry)

    def test_sha256_updated(self):
        sha = self.entry.get("provenance", {}).get("source_sha256", "")
        self.assertEqual(
            sha,
            CODEX_AUTOMATION_ARCHITECT_EXPECTED_SHA256,
            f"source_sha256 not updated: {sha}",
        )

    def test_old_sha256_absent(self):
        sha = self.entry.get("provenance", {}).get("source_sha256", "")
        self.assertNotEqual(
            sha,
            OLD_CODEX_AUTOMATION_ARCHITECT_SHA256,
            "codex-automation-architect still carries old source_sha256",
        )

    def test_description_updated(self):
        desc = self.entry.get("description", "")
        # New description uses "designing, reviewing, or updating" phrasing
        self.assertIn(
            "designing",
            desc,
            f"codex-automation-architect description not updated: '{desc}'",
        )

    def test_description_not_old_phrasing(self):
        desc = self.entry.get("description", "")
        self.assertNotIn(
            "safe scheduling",
            desc,
            "codex-automation-architect description still uses old 'safe scheduling' phrasing",
        )

    def test_source_revision_is_new(self):
        rev = self.entry.get("provenance", {}).get("source_revision", "")
        self.assertEqual(
            rev,
            EXPECTED_COMMAND_SURFACE_REVISION,
            f"codex-automation-architect source_revision not updated: '{rev}'",
        )


# ---------------------------------------------------------------------------
# codex-agent-creator SHA-256 update in command-surface.json
# ---------------------------------------------------------------------------


class TestCodexAgentCreatorCommandSurface(unittest.TestCase):
    """Validate codex-agent-creator SHA-256 update in command-surface.json."""

    @classmethod
    def setUpClass(cls):
        data = json.loads(COMMAND_SURFACE_PATH.read_text(encoding="utf-8"))
        handles: list[dict] = data.get("handles", [])
        cls.entry = _find_handle(handles, "codex-agent-creator")

    def test_entry_exists(self):
        self.assertIsNotNone(self.entry, "codex-agent-creator not found in command-surface.json")

    def test_sha256_updated(self):
        sha = self.entry.get("provenance", {}).get("source_sha256", "")
        self.assertEqual(
            sha,
            CODEX_AGENT_CREATOR_EXPECTED_SHA256,
            f"codex-agent-creator source_sha256 not updated: {sha}",
        )

    def test_old_sha256_absent(self):
        sha = self.entry.get("provenance", {}).get("source_sha256", "")
        self.assertNotEqual(
            sha,
            OLD_CODEX_AGENT_CREATOR_SHA256,
            "codex-agent-creator still carries old source_sha256",
        )

    def test_source_revision_is_new(self):
        rev = self.entry.get("provenance", {}).get("source_revision", "")
        self.assertEqual(rev, EXPECTED_COMMAND_SURFACE_REVISION)


# ---------------------------------------------------------------------------
# codex-environment-creator update in command-surface.json
# ---------------------------------------------------------------------------


class TestCodexEnvironmentCreatorCommandSurface(unittest.TestCase):
    """Validate codex-environment-creator changes in command-surface.json."""

    @classmethod
    def setUpClass(cls):
        data = json.loads(COMMAND_SURFACE_PATH.read_text(encoding="utf-8"))
        handles: list[dict] = data.get("handles", [])
        cls.entry = _find_handle(handles, "codex-environment-creator")

    def test_entry_exists(self):
        self.assertIsNotNone(
            self.entry, "codex-environment-creator not found in command-surface.json"
        )

    def test_sha256_updated(self):
        sha = self.entry.get("provenance", {}).get("source_sha256", "")
        self.assertEqual(
            sha,
            CODEX_ENVIRONMENT_CREATOR_EXPECTED_SHA256,
            f"codex-environment-creator source_sha256 not updated: {sha}",
        )

    def test_old_sha256_absent(self):
        sha = self.entry.get("provenance", {}).get("source_sha256", "")
        self.assertNotEqual(
            sha,
            OLD_CODEX_ENVIRONMENT_CREATOR_SHA256,
            "codex-environment-creator still carries old source_sha256",
        )

    def test_description_mentions_exec_server_providers(self):
        """New description must mention exec-server providers."""
        desc = self.entry.get("description", "")
        self.assertIn(
            "exec-server providers",
            desc,
            f"New codex-environment-creator description missing 'exec-server providers': '{desc}'",
        )

    def test_source_revision_is_new(self):
        rev = self.entry.get("provenance", {}).get("source_revision", "")
        self.assertEqual(rev, EXPECTED_COMMAND_SURFACE_REVISION)


# ---------------------------------------------------------------------------
# codex-hooks-builder SHA-256 update in command-surface.json
# ---------------------------------------------------------------------------


class TestCodexHooksBuilderCommandSurface(unittest.TestCase):
    """Validate codex-hooks-builder SHA-256 update in command-surface.json."""

    @classmethod
    def setUpClass(cls):
        data = json.loads(COMMAND_SURFACE_PATH.read_text(encoding="utf-8"))
        handles: list[dict] = data.get("handles", [])
        cls.entry = _find_handle(handles, "codex-hooks-builder")

    def test_entry_exists(self):
        self.assertIsNotNone(
            self.entry, "codex-hooks-builder not found in command-surface.json"
        )

    def test_sha256_updated(self):
        sha = self.entry.get("provenance", {}).get("source_sha256", "")
        self.assertEqual(
            sha,
            CODEX_HOOKS_BUILDER_EXPECTED_SHA256,
            f"codex-hooks-builder source_sha256 not updated: {sha}",
        )

    def test_old_sha256_absent(self):
        sha = self.entry.get("provenance", {}).get("source_sha256", "")
        self.assertNotEqual(
            sha,
            OLD_CODEX_HOOKS_BUILDER_SHA256,
            "codex-hooks-builder still carries old source_sha256",
        )

    def test_source_revision_is_new(self):
        rev = self.entry.get("provenance", {}).get("source_revision", "")
        self.assertEqual(rev, EXPECTED_COMMAND_SURFACE_REVISION)


# ---------------------------------------------------------------------------
# agent-ops manifest: codex-automation-architect entry
# ---------------------------------------------------------------------------


class TestAgentOpsManifestCodexAutomationArchitect(unittest.TestCase):
    """Validate codex-automation-architect entry in agent-ops manifest.jsonl."""

    @classmethod
    def setUpClass(cls):
        cls.records = _load_jsonl(AGENT_OPS_MANIFEST)
        cls.entry = _find_record(cls.records, "codex-automation-architect")
        if cls.entry is None:
            raise AssertionError("codex-automation-architect not found in agent-ops manifest")

    def test_entry_exists(self):
        self.assertIsNotNone(
            self.entry, "codex-automation-architect not found in agent-ops manifest"
        )

    def test_level_is_molecule(self):
        self.assertEqual(
            self.entry.get("level"),
            "molecule",
            f"Expected level='molecule', got '{self.entry.get('level')}'",
        )

    def test_level_not_compound(self):
        self.assertNotEqual(
            self.entry.get("level"),
            "compound",
            "codex-automation-architect level reverted to compound in manifest",
        )

    def test_sha256_updated(self):
        sha = self.entry.get("provenance", {}).get("source_sha256", "")
        self.assertEqual(sha, CODEX_AUTOMATION_ARCHITECT_EXPECTED_SHA256)

    def test_old_sha256_absent(self):
        sha = self.entry.get("provenance", {}).get("source_sha256", "")
        self.assertNotEqual(sha, OLD_CODEX_AUTOMATION_ARCHITECT_SHA256)

    def test_source_revision_is_new(self):
        rev = self.entry.get("provenance", {}).get("source_revision", "")
        self.assertEqual(rev, EXPECTED_AGENT_OPS_REVISION)

    def test_description_updated(self):
        desc = self.entry.get("description", "")
        self.assertIn(
            "cron jobs",
            desc,
            f"Updated description should mention 'cron jobs': '{desc}'",
        )

    def test_skill_set_is_agent_ops(self):
        self.assertEqual(self.entry.get("skill_set"), "agent-ops")

    def test_triggers_contains_codex_automation_architect(self):
        triggers = self.entry.get("triggers", [])
        self.assertIn("codex automation architect", triggers)


# ---------------------------------------------------------------------------
# agent-ops manifest: codex-agent-creator entry
# ---------------------------------------------------------------------------


class TestAgentOpsManifestCodexAgentCreator(unittest.TestCase):
    """Validate codex-agent-creator entry in agent-ops manifest.jsonl."""

    @classmethod
    def setUpClass(cls):
        cls.records = _load_jsonl(AGENT_OPS_MANIFEST)
        cls.entry = _find_record(cls.records, "codex-agent-creator")
        if cls.entry is None:
            raise AssertionError("codex-agent-creator not found in agent-ops manifest")

    def test_entry_exists(self):
        self.assertIsNotNone(self.entry, "codex-agent-creator not found in agent-ops manifest")

    def test_sha256_updated(self):
        sha = self.entry.get("provenance", {}).get("source_sha256", "")
        self.assertEqual(
            sha,
            CODEX_AGENT_CREATOR_EXPECTED_SHA256,
            f"codex-agent-creator sha256 not updated in manifest: {sha}",
        )

    def test_old_sha256_absent(self):
        sha = self.entry.get("provenance", {}).get("source_sha256", "")
        self.assertNotEqual(
            sha,
            OLD_CODEX_AGENT_CREATOR_SHA256,
        )

    def test_source_revision_is_new(self):
        rev = self.entry.get("provenance", {}).get("source_revision", "")
        self.assertEqual(rev, EXPECTED_AGENT_OPS_REVISION)

    def test_level_is_atom(self):
        """codex-agent-creator level must remain 'atom' (unchanged by this PR)."""
        self.assertEqual(self.entry.get("level"), "atom")


# ---------------------------------------------------------------------------
# agent-ops manifest: codex-environment-creator entry
# ---------------------------------------------------------------------------


class TestAgentOpsManifestCodexEnvironmentCreator(unittest.TestCase):
    """Validate codex-environment-creator entry in agent-ops manifest.jsonl."""

    @classmethod
    def setUpClass(cls):
        cls.records = _load_jsonl(AGENT_OPS_MANIFEST)
        cls.entry = _find_record(cls.records, "codex-environment-creator")

    def test_entry_exists(self):
        self.assertIsNotNone(
            self.entry, "codex-environment-creator not found in agent-ops manifest"
        )

    def test_sha256_updated(self):
        sha = self.entry.get("provenance", {}).get("source_sha256", "")
        self.assertEqual(
            sha,
            CODEX_ENVIRONMENT_CREATOR_EXPECTED_SHA256,
            f"codex-environment-creator sha256 not updated in manifest: {sha}",
        )

    def test_old_sha256_absent(self):
        sha = self.entry.get("provenance", {}).get("source_sha256", "")
        self.assertNotEqual(sha, OLD_CODEX_ENVIRONMENT_CREATOR_SHA256)

    def test_source_revision_is_new(self):
        rev = self.entry.get("provenance", {}).get("source_revision", "")
        self.assertEqual(rev, EXPECTED_AGENT_OPS_REVISION)

    def test_description_mentions_exec_server_providers(self):
        desc = self.entry.get("description", "")
        self.assertIn(
            "exec-server providers",
            desc,
            f"Updated manifest description should mention 'exec-server providers': '{desc}'",
        )


# ---------------------------------------------------------------------------
# codex-automation-architect/references/contract.yaml structure
# ---------------------------------------------------------------------------


@unittest.skipUnless(_YAML_AVAILABLE, "PyYAML not installed")
class TestCodexAutomationArchitectContractYaml(unittest.TestCase):
    """Validate the structure of codex-automation-architect references/contract.yaml."""

    @classmethod
    def setUpClass(cls):
        with open(CODEX_AUTOMATION_ARCHITECT_CONTRACT, encoding="utf-8") as fh:
            cls.contract = yaml.safe_load(fh)

    def test_file_exists(self):
        self.assertTrue(
            CODEX_AUTOMATION_ARCHITECT_CONTRACT.is_file(),
            f"contract.yaml not found: {CODEX_AUTOMATION_ARCHITECT_CONTRACT}",
        )

    def test_is_dict(self):
        self.assertIsInstance(self.contract, dict)

    def test_schema_version_present(self):
        self.assertIn("schema_version", self.contract)

    def test_schema_version_is_1(self):
        self.assertEqual(self.contract.get("schema_version"), 1)

    def test_skill_field_is_codex_automation_architect(self):
        self.assertEqual(self.contract.get("skill"), "codex-automation-architect")

    def test_runtime_contract_present(self):
        self.assertIn(
            "runtime_contract",
            self.contract,
            "runtime_contract block missing from contract.yaml",
        )

    def test_runtime_contract_kinds_contains_cron(self):
        kinds = self.contract.get("runtime_contract", {}).get("kinds", [])
        self.assertIn("cron", kinds, f"'cron' missing from runtime_contract.kinds: {kinds}")

    def test_runtime_contract_kinds_contains_heartbeat(self):
        kinds = self.contract.get("runtime_contract", {}).get("kinds", [])
        self.assertIn(
            "heartbeat", kinds, f"'heartbeat' missing from runtime_contract.kinds: {kinds}"
        )

    def test_runtime_contract_tools_list_present(self):
        tools = self.contract.get("runtime_contract", {}).get("tools", [])
        self.assertIsInstance(tools, list)
        self.assertGreater(len(tools), 0, "runtime_contract.tools must not be empty")

    def test_runtime_contract_tools_contains_automation_update(self):
        tools = self.contract.get("runtime_contract", {}).get("tools", [])
        tool_names = " ".join(str(t) for t in tools)
        self.assertIn(
            "automation_update",
            tool_names,
            f"automation_update tool missing from runtime_contract.tools: {tools}",
        )

    def test_runtime_contract_tools_contains_automation_list(self):
        tools = self.contract.get("runtime_contract", {}).get("tools", [])
        tool_names = " ".join(str(t) for t in tools)
        self.assertIn(
            "automation_list",
            tool_names,
            f"automation_list tool missing from runtime_contract.tools: {tools}",
        )

    def test_update_rule_present(self):
        update_rule = self.contract.get("runtime_contract", {}).get("update_rule", "")
        self.assertTrue(
            update_rule,
            "runtime_contract.update_rule is missing or empty in contract.yaml",
        )

    def test_update_rule_mentions_duplicate(self):
        update_rule = self.contract.get("runtime_contract", {}).get("update_rule", "")
        self.assertIn(
            "duplicate",
            update_rule,
            f"update_rule should mention duplicate avoidance: '{update_rule}'",
        )

    def test_safety_block_present(self):
        self.assertIn("safety", self.contract, "safety block missing from contract.yaml")

    def test_safety_redact_secrets_true(self):
        self.assertTrue(
            self.contract.get("safety", {}).get("redact_secrets"),
            "safety.redact_secrets must be true in contract.yaml",
        )

    def test_safety_destructive_commands_false(self):
        self.assertFalse(
            self.contract.get("safety", {}).get("destructive_commands"),
            "safety.destructive_commands must be false in contract.yaml",
        )

    def test_inputs_list_present(self):
        inputs = self.contract.get("inputs", [])
        self.assertIsInstance(inputs, list)
        self.assertGreater(len(inputs), 0)

    def test_outputs_list_present(self):
        outputs = self.contract.get("outputs", [])
        self.assertIsInstance(outputs, list)
        self.assertGreater(len(outputs), 0)

    def test_risks_list_present(self):
        risks = self.contract.get("risks", [])
        self.assertIsInstance(risks, list)
        self.assertGreater(len(risks), 0)

    def test_validation_block_present(self):
        validation = self.contract.get("validation", [])
        self.assertIsInstance(validation, list)
        self.assertGreater(len(validation), 0)

    def test_execution_environments_contains_worktree(self):
        envs = self.contract.get("runtime_contract", {}).get("execution_environments", [])
        self.assertIn("worktree", envs, f"'worktree' missing from execution_environments: {envs}")

    def test_review_rule_present(self):
        review_rule = self.contract.get("runtime_contract", {}).get("review_rule", "")
        self.assertTrue(
            review_rule,
            "runtime_contract.review_rule missing in contract.yaml",
        )


# ---------------------------------------------------------------------------
# codex-automation-architect SKILL.md content checks
# ---------------------------------------------------------------------------


class TestCodexAutomationArchitectSkillMd(unittest.TestCase):
    """Validate content of Skills/agent-ops/codex-automation-architect/SKILL.md."""

    @classmethod
    def setUpClass(cls):
        cls.content = CODEX_AUTOMATION_ARCHITECT_SKILL.read_text(encoding="utf-8")

    def test_file_exists(self):
        self.assertTrue(
            CODEX_AUTOMATION_ARCHITECT_SKILL.is_file(),
            f"SKILL.md not found: {CODEX_AUTOMATION_ARCHITECT_SKILL}",
        )

    def test_frontmatter_present(self):
        self.assertTrue(
            self.content.startswith("---"),
            "SKILL.md does not start with YAML frontmatter delimiter '---'",
        )

    def test_frontmatter_name_is_codex_automation_architect(self):
        self.assertIn(
            "name: codex-automation-architect",
            self.content,
        )

    def test_heartbeat_keyword_present(self):
        """New skill content must mention heartbeat automation kind."""
        self.assertIn(
            "heartbeat",
            self.content,
            "SKILL.md should mention 'heartbeat' after this PR",
        )

    def test_cron_keyword_present(self):
        """New skill content must mention cron automation kind."""
        self.assertIn(
            "cron",
            self.content,
            "SKILL.md should mention 'cron' after this PR",
        )

    def test_when_to_use_section_present(self):
        self.assertIn("## When To Use", self.content)

    def test_workflow_section_present(self):
        self.assertIn("## Workflow", self.content)

    def test_validation_section_present(self):
        self.assertIn("## Validation", self.content)

    def test_constraints_section_present(self):
        self.assertIn("## Constraints", self.content)

    def test_execution_boundaries_section_present(self):
        self.assertIn("## Execution Boundaries", self.content)

    def test_contract_yaml_reference_present(self):
        """SKILL.md must reference contract.yaml for the machine-readable contract."""
        self.assertIn(
            "contract.yaml",
            self.content,
            "SKILL.md should reference contract.yaml",
        )

    def test_tool_examples_reference_present(self):
        """SKILL.md must reference tool-examples.md."""
        self.assertIn(
            "tool-examples.md",
            self.content,
            "SKILL.md should reference tool-examples.md",
        )

    def test_quality_target_is_plugin_eval_a(self):
        """frontmatter quality_target should be plugin-eval-a."""
        self.assertIn(
            "quality_target: plugin-eval-a",
            self.content,
        )

    def test_description_uses_new_phrasing(self):
        """New SKILL.md description must match the PR's updated phrasing."""
        self.assertIn(
            "cron jobs, scheduled tasks",
            self.content,
            "SKILL.md description should mention 'cron jobs, scheduled tasks'",
        )

    def test_old_description_phrasing_absent(self):
        """Old 'safe scheduling, scope, preflight' phrasing must be gone."""
        self.assertNotIn(
            "safe scheduling, scope, preflight, and consolidation",
            self.content,
            "Old description phrasing still present in SKILL.md",
        )


# ---------------------------------------------------------------------------
# codex-automation-architect references/tool-examples.md content
# ---------------------------------------------------------------------------


class TestCodexAutomationArchitectToolExamplesMd(unittest.TestCase):
    """Validate content of codex-automation-architect/references/tool-examples.md."""

    @classmethod
    def setUpClass(cls):
        cls.content = CODEX_AUTOMATION_ARCHITECT_TOOL_EXAMPLES.read_text(encoding="utf-8")

    def test_file_exists(self):
        self.assertTrue(CODEX_AUTOMATION_ARCHITECT_TOOL_EXAMPLES.is_file())

    def test_heartbeat_section_present(self):
        self.assertIn(
            "Heartbeat",
            self.content,
            "tool-examples.md should contain a Heartbeat section",
        )

    def test_cron_section_present(self):
        self.assertIn(
            "Workspace Cron",
            self.content,
            "tool-examples.md should contain a Workspace Cron section",
        )

    def test_worktree_proposal_section_present(self):
        self.assertIn(
            "Worktree Proposal",
            self.content,
            "tool-examples.md should contain a Worktree Proposal section",
        )

    def test_automation_update_tool_referenced(self):
        self.assertIn(
            "automation_update",
            self.content,
            "tool-examples.md should reference automation_update",
        )

    def test_mode_create_present(self):
        self.assertIn('"mode": "create"', self.content)

    def test_kind_heartbeat_present(self):
        self.assertIn('"kind": "heartbeat"', self.content)

    def test_kind_cron_present(self):
        self.assertIn('"kind": "cron"', self.content)

    def test_suggested_create_present(self):
        self.assertIn('"mode": "suggested_create"', self.content)


# ---------------------------------------------------------------------------
# codex-agent-creator SKILL.md content checks
# ---------------------------------------------------------------------------


class TestCodexAgentCreatorSkillMd(unittest.TestCase):
    """Validate content of Skills/agent-ops/codex-agent-creator/SKILL.md."""

    @classmethod
    def setUpClass(cls):
        cls.content = CODEX_AGENT_CREATOR_SKILL.read_text(encoding="utf-8")

    def test_file_exists(self):
        self.assertTrue(CODEX_AGENT_CREATOR_SKILL.is_file())

    def test_frontmatter_present(self):
        self.assertTrue(self.content.startswith("---"))

    def test_name_is_codex_agent_creator(self):
        self.assertIn("name: codex-agent-creator", self.content)

    def test_preconditions_section_present(self):
        self.assertIn("## Preconditions", self.content)

    def test_procedure_section_present(self):
        self.assertIn("## Procedure", self.content)

    def test_validation_gates_section_present(self):
        self.assertIn("## Validation Gates", self.content)

    def test_codex_harness_placement_section_present(self):
        self.assertIn("## Codex Harness Placement", self.content)

    def test_references_role_config_examples(self):
        self.assertIn("role-config-examples.md", self.content)

    def test_references_role_creation_guide(self):
        self.assertIn("role-creation-guide.md", self.content)

    def test_agents_max_depth_mentioned(self):
        """agents.max_depth is a required concept in role creation guide alignment."""
        self.assertIn(
            "agents.max_depth",
            self.content,
            "SKILL.md should mention agents.max_depth",
        )

    def test_spawn_agent_mentioned(self):
        self.assertIn("spawn_agent", self.content)


# ---------------------------------------------------------------------------
# codex-agent-creator references/role-config-examples.md
# ---------------------------------------------------------------------------


class TestCodexAgentCreatorRoleConfigExamplesMd(unittest.TestCase):
    """Validate content of role-config-examples.md reference file."""

    @classmethod
    def setUpClass(cls):
        cls.content = CODEX_AGENT_CREATOR_ROLE_CONFIG_EXAMPLES.read_text(encoding="utf-8")

    def test_file_exists(self):
        self.assertTrue(CODEX_AGENT_CREATOR_ROLE_CONFIG_EXAMPLES.is_file())

    def test_standalone_role_file_section_present(self):
        self.assertIn("Standalone Role File", self.content)

    def test_config_registration_section_present(self):
        self.assertIn("Config Registration", self.content)

    def test_spawn_shape_section_present(self):
        self.assertIn("Spawn Shape", self.content)

    def test_toml_code_block_present(self):
        self.assertIn("~~~toml", self.content)

    def test_json_code_block_present(self):
        self.assertIn("~~~json", self.content)

    def test_developer_instructions_field_present(self):
        self.assertIn("developer_instructions", self.content)

    def test_name_field_present(self):
        self.assertIn('name = "', self.content)

    def test_description_field_present(self):
        self.assertIn("description", self.content)


# ---------------------------------------------------------------------------
# codex-agent-creator references/role-creation-guide.md
# ---------------------------------------------------------------------------


class TestCodexAgentCreatorRoleCreationGuideMd(unittest.TestCase):
    """Validate content of role-creation-guide.md reference file."""

    @classmethod
    def setUpClass(cls):
        cls.content = CODEX_AGENT_CREATOR_ROLE_CREATION_GUIDE.read_text(encoding="utf-8")

    def test_file_exists(self):
        self.assertTrue(CODEX_AGENT_CREATOR_ROLE_CREATION_GUIDE.is_file())

    def test_current_codex_contract_section_present(self):
        self.assertIn("## Current Codex Contract", self.content)

    def test_role_file_shape_section_present(self):
        self.assertIn("## Role File Shape", self.content)

    def test_scope_and_install_section_present(self):
        self.assertIn("## Scope And Install", self.content)

    def test_agents_max_depth_mentioned(self):
        self.assertIn("agents.max_depth", self.content)

    def test_developer_instructions_required_mentioned(self):
        self.assertIn("developer_instructions", self.content)


# ---------------------------------------------------------------------------
# Plugin files: plugin-factory-router SKILL.md
# ---------------------------------------------------------------------------


class TestPluginFactoryRouterSkillMd(unittest.TestCase):
    """Validate plugin-factory-router/SKILL.md structure."""

    @classmethod
    def setUpClass(cls):
        cls.content = PLUGIN_FACTORY_ROUTER_SKILL.read_text(encoding="utf-8")

    def test_file_exists(self):
        self.assertTrue(PLUGIN_FACTORY_ROUTER_SKILL.is_file())

    def test_frontmatter_present(self):
        self.assertTrue(
            self.content.startswith("---"),
            "plugin-factory-router SKILL.md must start with YAML frontmatter",
        )

    def test_name_is_plugin_factory_router(self):
        self.assertIn("name: plugin-factory-router", self.content)

    def test_description_present_in_frontmatter(self):
        self.assertIn("description:", self.content)

    def test_skill_type_is_team_automation(self):
        self.assertIn("skill-type: team_automation", self.content)

    def test_philosophy_section_present(self):
        self.assertIn("## Philosophy", self.content)

    def test_when_to_use_section_present(self):
        self.assertIn("## When to use", self.content)


# ---------------------------------------------------------------------------
# Plugin files: current-codex-plugin-runtime.md reference
# ---------------------------------------------------------------------------


class TestPluginFactoryRouterRuntimeReferenceMd(unittest.TestCase):
    """Validate plugin-factory-router/references/current-codex-plugin-runtime.md."""

    @classmethod
    def setUpClass(cls):
        cls.content = PLUGIN_FACTORY_ROUTER_RUNTIME_REF.read_text(encoding="utf-8")

    def test_file_exists(self):
        self.assertTrue(PLUGIN_FACTORY_ROUTER_RUNTIME_REF.is_file())

    def test_route_cues_section_present(self):
        self.assertIn("## Route Cues", self.content)

    def test_current_runtime_boundaries_section_present(self):
        self.assertIn("## Current Runtime Boundaries", self.content)

    def test_plugin_builder_route_mentioned(self):
        self.assertIn("plugin-builder", self.content)

    def test_plugin_installer_route_mentioned(self):
        self.assertIn("plugin-installer", self.content)

    def test_plugin_creator_route_mentioned(self):
        self.assertIn("plugin-creator", self.content)


# ---------------------------------------------------------------------------
# Negative regression: no stale revision in any manifest or command-surface
# ---------------------------------------------------------------------------


class TestNoStaleRevisions(unittest.TestCase):
    """No file touched by this PR should still contain old revision strings."""

    @classmethod
    def setUpClass(cls):
        cls.surface_data = json.loads(COMMAND_SURFACE_PATH.read_text(encoding="utf-8"))

    def test_no_old_manifest_revision_in_any_skillset(self):
        for manifest_path in sorted(SKILLSETS_DIR.glob("*/manifest.jsonl")):
            for rec in _load_jsonl(manifest_path):
                rev = rec.get("provenance", {}).get("source_revision", "")
                with self.subTest(file=manifest_path.name, id=rec.get("id")):
                    self.assertNotEqual(
                        rev,
                        OLD_MANIFEST_REVISION,
                        f"Stale manifest revision '{OLD_MANIFEST_REVISION}' in "
                        f"'{rec.get('id')}' of {manifest_path.name}",
                    )

    def test_no_old_command_surface_revision_in_handles(self):
        for handle in self.surface_data.get("handles", []):
            rev = handle.get("provenance", {}).get("source_revision", "")
            with self.subTest(handle=handle.get("handle")):
                self.assertNotEqual(
                    rev,
                    OLD_COMMAND_SURFACE_REVISION,
                    f"Handle '{handle.get('handle')}' still has old command-surface "
                    f"revision '{OLD_COMMAND_SURFACE_REVISION}'",
                )

    def test_no_old_agent_creator_sha256_in_surface(self):
        handles = self.surface_data.get("handles", [])
        entry = _find_handle(handles, "codex-agent-creator")
        if entry is not None:
            sha = entry.get("provenance", {}).get("source_sha256", "")
            self.assertNotEqual(sha, OLD_CODEX_AGENT_CREATOR_SHA256)

    def test_no_old_automation_architect_sha256_in_surface(self):
        handles = self.surface_data.get("handles", [])
        entry = _find_handle(handles, "codex-automation-architect")
        if entry is not None:
            sha = entry.get("provenance", {}).get("source_sha256", "")
            self.assertNotEqual(sha, OLD_CODEX_AUTOMATION_ARCHITECT_SHA256)


if __name__ == "__main__":
    unittest.main()
