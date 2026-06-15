"""
Structural validation tests for files changed in this PR.

Covers:
  - All .skillsets/*/manifest.jsonl files: source_revision updated to "5983ceeb",
    old revision "6cda095d5" not present anywhere.
  - Plugins/plugin-factory/.codex-plugin/plugin.json: required fields present.
  - plugin-builder fixture files: arscontexta-codex .codex-plugin/plugin.json,
    .app.json, and .mcp.json all satisfy their structural contracts.
"""
import json
import re
import unittest
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]

SKILLSET_MANIFEST_PATHS = sorted(REPO_ROOT.glob(".skillsets/*/manifest.jsonl"))

_NEW_REVISION = "5983ceeb"
_OLD_REVISION = "6cda095d5"

PLUGIN_FACTORY_PLUGIN_JSON = (
    REPO_ROOT / "Plugins" / "plugin-factory" / ".codex-plugin" / "plugin.json"
)

FIXTURE_DIR = (
    REPO_ROOT
    / "Plugins"
    / "plugin-factory"
    / "skills"
    / "code_quality_review"
    / "plugin-builder"
    / "fixtures"
    / "arscontexta-codex"
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Manifest source_revision: new value present, old value absent
# ---------------------------------------------------------------------------


class TestManifestSourceRevisionIs5983ceeb(unittest.TestCase):
    """Every manifest entry must carry the new source_revision '5983ceeb'."""

    MANIFEST_NAMES = (
        "agent-ops",
        "backend-platform",
        "content-publishing",
        "frontend-ui",
        "harness-engineering",
        "mobile-native",
        "plugin-factory",
        "product-strategy",
        "security-ops",
        "skill-factory",
    )

    def _assert_revision(self, skill_set: str) -> None:
        path = REPO_ROOT / ".skillsets" / skill_set / "manifest.jsonl"
        if not path.exists():
            self.skipTest(f"{path} not present in this environment")
        records = _load_jsonl(path)
        self.assertGreater(len(records), 0, f"Manifest {path} is unexpectedly empty")
        for rec in records:
            rev = rec.get("provenance", {}).get("source_revision", "")
            self.assertEqual(
                rev,
                _NEW_REVISION,
                f"Entry '{rec.get('id')}' in {skill_set}/manifest.jsonl "
                f"has unexpected revision: {rev!r}",
            )

    def test_agent_ops_uses_new_revision(self):
        self._assert_revision("agent-ops")

    def test_backend_platform_uses_new_revision(self):
        self._assert_revision("backend-platform")

    def test_content_publishing_uses_new_revision(self):
        self._assert_revision("content-publishing")

    def test_frontend_ui_uses_new_revision(self):
        self._assert_revision("frontend-ui")

    def test_harness_engineering_uses_new_revision(self):
        self._assert_revision("harness-engineering")

    def test_mobile_native_uses_new_revision(self):
        self._assert_revision("mobile-native")

    def test_plugin_factory_uses_new_revision(self):
        self._assert_revision("plugin-factory")

    def test_product_strategy_uses_new_revision(self):
        self._assert_revision("product-strategy")

    def test_security_ops_uses_new_revision(self):
        self._assert_revision("security-ops")

    def test_skill_factory_uses_new_revision(self):
        self._assert_revision("skill-factory")


class TestManifestOldRevisionAbsent(unittest.TestCase):
    """The old source_revision '6cda095d5' must not appear in any manifest."""

    def test_no_manifest_uses_old_revision(self):
        for path in SKILLSET_MANIFEST_PATHS:
            records = _load_jsonl(path)
            for rec in records:
                rev = rec.get("provenance", {}).get("source_revision", "")
                with self.subTest(file=path.name, id=rec.get("id", "?")):
                    self.assertNotEqual(
                        rev,
                        _OLD_REVISION,
                        f"Entry '{rec.get('id')}' in {path.name} still has old revision {_OLD_REVISION!r}",
                    )

    def test_all_manifests_use_single_consistent_revision(self):
        """All manifest entries across all skillsets share one common source_revision."""
        revisions = set()
        for path in SKILLSET_MANIFEST_PATHS:
            records = _load_jsonl(path)
            for rec in records:
                rev = rec.get("provenance", {}).get("source_revision", "")
                if rev:
                    revisions.add(rev)
        if not revisions:
            self.skipTest("No source_revision values found; manifests may be absent")
        self.assertEqual(
            len(revisions),
            1,
            f"Expected one consistent source_revision across all manifests, got: {sorted(revisions)}",
        )


# ---------------------------------------------------------------------------
# Plugin-factory top-level plugin.json
# ---------------------------------------------------------------------------


class TestPluginFactoryPluginJson(unittest.TestCase):
    """Validate the plugin-factory .codex-plugin/plugin.json structure."""

    def setUp(self):
        if not PLUGIN_FACTORY_PLUGIN_JSON.exists():
            self.skipTest("plugin-factory plugin.json not present")
        with open(PLUGIN_FACTORY_PLUGIN_JSON, encoding="utf-8") as fh:
            self._data = json.load(fh)

    def test_file_parses_as_valid_json(self):
        self.assertIsInstance(self._data, dict)

    def test_has_schema_version_1(self):
        self.assertEqual(self._data.get("schema_version"), 1)

    def test_has_name(self):
        self.assertIn("name", self._data)
        self.assertIsInstance(self._data["name"], str)
        self.assertTrue(self._data["name"].strip())

    def test_has_version(self):
        self.assertIn("version", self._data)

    def test_has_description(self):
        self.assertIn("description", self._data)
        self.assertIsInstance(self._data["description"], str)

    def test_has_interface(self):
        self.assertIn("interface", self._data)
        iface = self._data["interface"]
        self.assertIsInstance(iface, dict)

    def test_interface_has_display_name(self):
        iface = self._data["interface"]
        self.assertIn("displayName", iface)
        self.assertIsInstance(iface["displayName"], str)

    def test_interface_has_short_description(self):
        iface = self._data["interface"]
        self.assertIn("shortDescription", iface)

    def test_has_skills_path(self):
        self.assertIn("skills", self._data)

    def test_interface_capabilities_is_list(self):
        iface = self._data["interface"]
        self.assertIn("capabilities", iface)
        self.assertIsInstance(iface["capabilities"], list)
        self.assertGreater(len(iface["capabilities"]), 0)

    def test_governance_lifecycle_state_is_active(self):
        gov = self._data.get("governance", {})
        self.assertEqual(gov.get("lifecycle_state"), "active")

    def test_governance_maturity_is_canonical(self):
        gov = self._data.get("governance", {})
        self.assertEqual(gov.get("maturity"), "canonical")


# ---------------------------------------------------------------------------
# plugin-builder fixture: arscontexta-codex
# ---------------------------------------------------------------------------


class TestArscontextaCodexPluginJson(unittest.TestCase):
    """Validate the arscontexta-codex .codex-plugin/plugin.json fixture."""

    def setUp(self):
        path = FIXTURE_DIR / ".codex-plugin" / "plugin.json"
        if not path.exists():
            self.skipTest(f"fixture plugin.json not present at {path}")
        with open(path, encoding="utf-8") as fh:
            self._data = json.load(fh)

    def test_file_parses_as_valid_json(self):
        self.assertIsInstance(self._data, dict)

    def test_has_name(self):
        self.assertIn("name", self._data)
        self.assertEqual(self._data["name"], "arscontexta-codex")

    def test_has_version(self):
        self.assertIn("version", self._data)
        self.assertRegex(
            self._data["version"],
            r"^\d+\.\d+\.\d+",
            "version should follow semver pattern",
        )

    def test_has_description(self):
        self.assertIn("description", self._data)
        desc = self._data["description"]
        self.assertIsInstance(desc, str)
        self.assertIn("fixture", desc.lower())

    def test_has_license(self):
        self.assertIn("license", self._data)

    def test_has_keywords_list(self):
        self.assertIn("keywords", self._data)
        self.assertIsInstance(self._data["keywords"], list)
        self.assertIn("fixture", self._data["keywords"])
        self.assertIn("plugin-builder", self._data["keywords"])

    def test_has_skills_path(self):
        self.assertIn("skills", self._data)

    def test_references_mcp_servers(self):
        self.assertIn("mcpServers", self._data)

    def test_references_apps(self):
        self.assertIn("apps", self._data)

    def test_has_interface(self):
        self.assertIn("interface", self._data)
        iface = self._data["interface"]
        self.assertIsInstance(iface, dict)

    def test_interface_required_fields(self):
        iface = self._data["interface"]
        for field in ("displayName", "shortDescription", "longDescription", "developerName"):
            with self.subTest(field=field):
                self.assertIn(field, iface)

    def test_interface_category_is_productivity(self):
        iface = self._data["interface"]
        self.assertEqual(iface.get("category"), "Productivity")

    def test_interface_capabilities_is_list(self):
        iface = self._data["interface"]
        self.assertIn("capabilities", iface)
        self.assertIsInstance(iface["capabilities"], list)

    def test_interface_has_website_url(self):
        iface = self._data["interface"]
        self.assertIn("websiteURL", iface)
        self.assertTrue(iface["websiteURL"].startswith("https://"))

    def test_brand_color_is_hex(self):
        iface = self._data["interface"]
        self.assertIn("brandColor", iface)
        self.assertRegex(iface["brandColor"], r"^#[0-9A-Fa-f]{6}$")

    def test_author_has_required_fields(self):
        author = self._data.get("author", {})
        self.assertIn("name", author)
        self.assertIn("url", author)


class TestArscontextaCodexAppJson(unittest.TestCase):
    """Validate the arscontexta-codex .app.json fixture."""

    def setUp(self):
        path = FIXTURE_DIR / ".app.json"
        if not path.exists():
            self.skipTest(f"fixture .app.json not present at {path}")
        with open(path, encoding="utf-8") as fh:
            self._data = json.load(fh)

    def test_file_parses_as_valid_json(self):
        self.assertIsInstance(self._data, dict)

    def test_has_schema_version_1(self):
        self.assertEqual(self._data.get("schema_version"), 1)

    def test_has_name(self):
        self.assertIn("name", self._data)
        self.assertEqual(self._data["name"], "arscontexta-codex")

    def test_has_description(self):
        self.assertIn("description", self._data)

    def test_has_surfaces_list(self):
        self.assertIn("surfaces", self._data)
        surfaces = self._data["surfaces"]
        self.assertIsInstance(surfaces, list)
        self.assertGreater(len(surfaces), 0)
        self.assertIn("skills", surfaces)

    def test_has_source_with_repo(self):
        self.assertIn("source", self._data)
        source = self._data["source"]
        self.assertIn("repo", source)
        self.assertTrue(source["repo"].startswith("https://"))

    def test_source_has_commit(self):
        source = self._data.get("source", {})
        self.assertIn("commit", source)
        commit = source["commit"]
        self.assertRegex(commit, r"^[0-9a-f]{7,}", "commit should look like a git hash")


class TestArscontextaCodexMcpJson(unittest.TestCase):
    """Validate the arscontexta-codex .mcp.json fixture."""

    def setUp(self):
        path = FIXTURE_DIR / ".mcp.json"
        if not path.exists():
            self.skipTest(f"fixture .mcp.json not present at {path}")
        with open(path, encoding="utf-8") as fh:
            self._data = json.load(fh)

    def test_file_parses_as_valid_json(self):
        self.assertIsInstance(self._data, dict)

    def test_has_schema_version_1(self):
        self.assertEqual(self._data.get("schema_version"), 1)

    def test_has_mcp_servers(self):
        self.assertIn("mcpServers", self._data)
        self.assertIsInstance(self._data["mcpServers"], dict)

    def test_each_server_has_command(self):
        for server_name, server_config in self._data.get("mcpServers", {}).items():
            with self.subTest(server=server_name):
                self.assertIn("command", server_config)
                self.assertIsInstance(server_config["command"], str)

    def test_each_server_has_args_list(self):
        for server_name, server_config in self._data.get("mcpServers", {}).items():
            with self.subTest(server=server_name):
                self.assertIn("args", server_config)
                self.assertIsInstance(server_config["args"], list)

    def test_placeholder_server_notes_present(self):
        """Placeholder MCP entries must have a notes field explaining their purpose."""
        for server_name, server_config in self._data.get("mcpServers", {}).items():
            with self.subTest(server=server_name):
                if "placeholder" in server_name.lower():
                    self.assertIn(
                        "notes",
                        server_config,
                        f"Placeholder server '{server_name}' should include a 'notes' field",
                    )


# ---------------------------------------------------------------------------
# Regression: manifests with known-good source_sha256 values
# ---------------------------------------------------------------------------


class TestManifestSourceSha256Format(unittest.TestCase):
    """source_sha256 values must be 64-char hex strings."""

    _SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$", re.IGNORECASE)

    def test_all_manifest_entries_have_valid_sha256(self):
        for path in SKILLSET_MANIFEST_PATHS:
            records = _load_jsonl(path)
            for rec in records:
                sha = rec.get("provenance", {}).get("source_sha256", "")
                with self.subTest(file=path.name, id=rec.get("id", "?")):
                    self.assertRegex(
                        sha,
                        self._SHA256_PATTERN,
                        f"source_sha256 '{sha}' is not a valid 64-char hex string",
                    )


if __name__ == "__main__":
    unittest.main()
