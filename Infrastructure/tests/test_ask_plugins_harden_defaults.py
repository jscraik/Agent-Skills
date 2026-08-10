"""Regression coverage for the canonical plugin hardening marketplace path."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.commands.plugins import harden_plugin


class TestPluginHardenDefaults(unittest.TestCase):
    def test_harden_uses_canonical_plugins_marketplace(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo_root = Path(directory)
            builder = repo_root / "Plugins/plugin-factory/scripts/plugin-builder/plugin_builder.py"
            builder.parent.mkdir(parents=True)
            builder.write_text("#!/usr/bin/env python3\n", encoding="utf-8")
            plugin_root = repo_root / "Plugins/example"
            plugin_root.mkdir(parents=True)

            with patch("ask.commands.plugins.subprocess.run") as run:
                run.return_value.returncode = 0
                run.return_value.stdout = "PASS\n"
                run.return_value.stderr = ""
                result = harden_plugin(repo_root, "Plugins/example")

        self.assertEqual(result.status, "success")
        self.assertIn(str(repo_root / "Plugins/marketplace.json"), run.call_args_list[0].args[0])


if __name__ == "__main__":
    unittest.main()
