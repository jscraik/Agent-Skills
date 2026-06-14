#!/usr/bin/env python3
"""Smoke checks for plugin-installer script wrappers."""

import importlib.util
from importlib.machinery import SourceFileLoader
from pathlib import Path
import sys

def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / ".git").exists() and (candidate / "Plugins").is_dir():
            return candidate
    raise AssertionError(f"Unable to find repository root from {start}")


def test_installer_wrapper_points_to_impl() -> None:
    current = Path(__file__).resolve()
    repo_root = find_repo_root(current)
    script_path = (
        repo_root
        / "Plugins"
        / "plugin-factory"
        / "skills"
        / "infrastructure_ops"
        / "plugin-installer"
        / "scripts"
        / "install-plugin-from-github.py"
    )
    impl_path = script_path.with_suffix(".pyw")

    assert script_path.exists()
    assert impl_path.exists()


def test_strict_installer_resolves_relocated_plugin_builder() -> None:
    current = Path(__file__).resolve()
    repo_root = find_repo_root(current)
    impl_path = (
        repo_root
        / "Plugins"
        / "plugin-factory"
        / "skills"
        / "infrastructure_ops"
        / "plugin-installer"
        / "scripts"
        / "install-plugin-from-github.pyw"
    )
    expected_builder = repo_root / "Plugins" / "plugin-factory" / "scripts" / "plugin-builder" / "plugin_builder.py"
    script_dir = impl_path.parent
    if str(script_dir) not in sys.path:
        sys.path.insert(0, str(script_dir))
    loader = SourceFileLoader("plugin_installer_impl_test", str(impl_path))
    spec = importlib.util.spec_from_file_location("plugin_installer_impl_test", impl_path, loader=loader)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert module._plugin_builder_script() == expected_builder
