#!/usr/bin/env python3
"""Security regression tests for plugin-creator marketplace scaffolding."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = (
    REPO_ROOT / "skills-system" / "plugin-creator" / "scripts" / "create_basic_plugin.py"
)
SPEC = importlib.util.spec_from_file_location("plugin_creator", SCRIPT_PATH)
assert SPEC and SPEC.loader
plugin_creator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(plugin_creator)


class PluginCreatorMarketplaceSecurityTests(unittest.TestCase):
    def test_effective_policy_products_defaults_to_codex(self) -> None:
        self.assertEqual(plugin_creator._effective_policy_products(None), ["CODEX"])

    def test_relative_repo_source_path_resolves_from_agents_marketplace_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            plugin_root = root / "plugins" / "example-plugin"
            plugin_root.mkdir(parents=True, exist_ok=True)
            marketplace_path = root / ".agents" / "plugins" / "marketplace.json"
            marketplace_path.parent.mkdir(parents=True, exist_ok=True)

            source_path = plugin_creator._relative_repo_source_path(
                plugin_root,
                marketplace_path,
                allow_legacy_marketplace_path=False,
            )

            self.assertEqual(source_path, "./Plugins/example-plugin")

    def test_marketplace_repo_root_rejects_legacy_layout_without_override(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            marketplace_path = root / "plugins" / "marketplace.json"
            marketplace_path.parent.mkdir(parents=True, exist_ok=True)

            with self.assertRaisesRegex(ValueError, "OpenAI/Codex marketplace mode"):
                plugin_creator._marketplace_repo_root(
                    marketplace_path,
                    allow_legacy_marketplace_path=False,
                )

    def test_update_marketplace_json_writes_policy_products(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            plugin_name = "example-plugin"
            plugin_root = root / "plugins" / plugin_name
            plugin_root.mkdir(parents=True, exist_ok=True)
            marketplace_path = root / ".agents" / "plugins" / "marketplace.json"

            plugin_creator.update_marketplace_json(
                marketplace_path=marketplace_path,
                plugin_name=plugin_name,
                plugin_root=plugin_root,
                install_policy="AVAILABLE",
                auth_policy="ON_INSTALL",
                policy_products=["CODEX"],
                category="Productivity",
                force=False,
                allow_legacy_marketplace_path=False,
            )

            payload = json.loads(marketplace_path.read_text(encoding="utf-8"))
            entry = payload["plugins"][0]
            self.assertEqual(entry["source"]["path"], "./Plugins/example-plugin")
            self.assertEqual(entry["policy"]["products"], ["CODEX"])


if __name__ == "__main__":
    unittest.main()
