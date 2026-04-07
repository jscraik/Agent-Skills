#!/usr/bin/env python3
"""Security-focused regression tests for plugin-installer GitHub import script."""

from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "skills-system" / "plugin-installer" / "scripts" / "install-plugin-from-github.py"
SCRIPT_DIR = SCRIPT_PATH.parent


def _load_installer_module():
    if str(SCRIPT_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPT_DIR))
    spec = importlib.util.spec_from_file_location("plugin_installer_github", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)  # type: ignore[assignment]
    return module


installer = _load_installer_module()


def _write_min_plugin(plugin_dir: Path) -> None:
    manifest_dir = plugin_dir / ".codex-plugin"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    (manifest_dir / "plugin.json").write_text(
        '{"name":"sample-plugin","version":"0.1.0","description":"sample"}\n',
        encoding="utf-8",
    )


class PluginInstallerSecurityTests(unittest.TestCase):
    def test_validate_relative_path_rejects_option_like_path(self) -> None:
        with self.assertRaises(installer.InstallError):
            installer._validate_relative_path("--dangerous")

    def test_validate_ref_token_rejects_option_like_ref(self) -> None:
        with self.assertRaises(installer.InstallError):
            installer._validate_ref_token("--orphan")

    def test_validate_relative_path_rejects_dot_path(self) -> None:
        with self.assertRaises(installer.InstallError):
            installer._validate_relative_path(".")

    def test_validate_ref_token_rejects_empty(self) -> None:
        with self.assertRaises(installer.InstallError):
            installer._validate_ref_token("   ")

    def test_validate_plugin_root_rejects_symlink_payloads(self) -> None:
        if not hasattr(os, "symlink"):
            self.skipTest("symlink not supported on this platform")

        with tempfile.TemporaryDirectory() as tmpdir:
            plugin_dir = Path(tmpdir) / "sample-plugin"
            _write_min_plugin(plugin_dir)
            os.symlink("/etc/hosts", plugin_dir / "leak.txt")

            with self.assertRaises(installer.InstallError):
                installer._validate_plugin_root(str(plugin_dir))

    def test_validate_plugin_root_rejects_missing_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            plugin_dir = Path(tmpdir) / "sample-plugin"
            plugin_dir.mkdir(parents=True, exist_ok=True)
            with self.assertRaises(installer.InstallError):
                installer._validate_plugin_root(str(plugin_dir))


if __name__ == "__main__":
    unittest.main()
