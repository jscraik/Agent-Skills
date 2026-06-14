#!/usr/bin/env python3
"""Smoke checks for plugin-installer script wrappers."""

import importlib.util
from contextlib import contextmanager
from importlib.machinery import SourceFileLoader
from pathlib import Path
import sys
import tempfile


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / ".git").exists() and (candidate / "Plugins").is_dir():
            return candidate
    raise AssertionError(f"Unable to find repository root from {start}")


@contextmanager
def temp_sys_path(path: Path):
    path_str = str(path)
    inserted = False
    if path_str not in sys.path:
        sys.path.insert(0, path_str)
        inserted = True
    try:
        yield
    finally:
        if inserted:
            try:
                sys.path.remove(path_str)
            except ValueError:
                pass


def load_installer_impl(module_name: str, impl_path: Path):
    with temp_sys_path(impl_path.parent):
        loader = SourceFileLoader(module_name, str(impl_path))
        spec = importlib.util.spec_from_file_location(module_name, impl_path, loader=loader)
        assert spec is not None
        assert spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    return module


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
    module = load_installer_impl("plugin_installer_impl_test", impl_path)

    assert module._plugin_builder_script() == expected_builder


def test_strict_installer_resolves_installed_plugin_mirror_builder() -> None:
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
    module = load_installer_impl("plugin_installer_impl_mirror_test", impl_path)

    with tempfile.TemporaryDirectory(prefix="plugin-installer-mirror-") as temp_dir:
        mirror_root = Path(temp_dir) / ".codex" / "plugins" / "plugin-factory"
        mirror_impl = (
            mirror_root
            / "skills"
            / "infrastructure_ops"
            / "plugin-installer"
            / "scripts"
            / "install-plugin-from-github.pyw"
        )
        mirror_builder = mirror_root / "scripts" / "plugin-builder" / "plugin_builder.py"
        mirror_impl.parent.mkdir(parents=True)
        mirror_builder.parent.mkdir(parents=True)
        mirror_impl.write_text("# installed mirror wrapper\n", encoding="utf-8")
        mirror_builder.write_text("# installed mirror builder\n", encoding="utf-8")

        module.__file__ = str(mirror_impl)

        assert module._plugin_builder_script() == mirror_builder.resolve()
