#!/usr/bin/env python3
"""Regression tests for Codex plugin-builder marketplace path handling."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "utilities" / "codex-plugin-builder" / "scripts" / "plugin_builder.py"
SPEC = importlib.util.spec_from_file_location("plugin_builder", MODULE_PATH)
assert SPEC and SPEC.loader
plugin_builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(plugin_builder)


class PluginBuilderMarketplacePathTests(unittest.TestCase):
    def test_repo_root_relative_path_for_plugins_marketplace(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            plugin_root = repo_root / "plugins" / "example-plugin"
            plugin_root.mkdir(parents=True)
            marketplace_path = repo_root / "plugins" / "marketplace.json"

            path = plugin_builder._relative_repo_source_path(plugin_root, marketplace_path)

            self.assertEqual(path, "./plugins/example-plugin")

    def test_repo_root_relative_path_for_agents_marketplace(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            plugin_root = repo_root / "plugins" / "example-plugin"
            plugin_root.mkdir(parents=True)
            agents_plugins = repo_root / ".agents" / "plugins"
            agents_plugins.mkdir(parents=True)
            marketplace_path = agents_plugins / "marketplace.json"

            path = plugin_builder._relative_repo_source_path(plugin_root, marketplace_path)

            self.assertEqual(path, "./plugins/example-plugin")

    def test_marketplace_entry_rejects_plugins_dir_relative_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            plugin_root = repo_root / "plugins" / "example-plugin"
            plugin_root.mkdir(parents=True)
            marketplace_path = repo_root / "plugins" / "marketplace.json"
            payload = {
                "name": "local-marketplace",
                "interface": {"displayName": "Local Marketplace"},
                "plugins": [
                    {
                        "name": "example-plugin",
                        "source": {
                            "source": "local",
                            "path": "./example-plugin",
                        },
                        "policy": {
                            "installation": "AVAILABLE",
                            "authentication": "ON_INSTALL",
                        },
                        "category": "Productivity",
                    }
                ],
            }

            failures = plugin_builder._check_marketplace_entry(
                payload,
                "example-plugin",
                plugin_root,
                marketplace_path,
            )

            self.assertTrue(
                any("./plugins/example-plugin" in failure for failure in failures),
                failures,
            )


if __name__ == "__main__":
    unittest.main()
