#!/usr/bin/env python3
"""Smoke checks for plugin-builder script wrappers."""

from pathlib import Path


def _find_repo_root(current: Path) -> Path:
    for parent in current.parents:
        if (parent / "AGENTS.md").exists() and (parent / "Plugins").exists():
            return parent
    raise AssertionError(f"could not locate repo root from {current}")


def test_plugin_builder_wrapper_points_to_impl() -> None:
    current = Path(__file__).resolve()
    repo_root = _find_repo_root(current)
    script_path = current.parent.parent / "scripts" / "plugin_builder.py"
    impl_path = repo_root / "Plugins" / "plugin-factory" / "skills" / "code_quality_review" / "plugin-builder" / "scripts" / "plugin_builder.pyw"

    assert script_path.exists()
    assert impl_path.exists()
    wrapper_source = script_path.read_text(encoding="utf-8")
    assert "runpy.run_path" in wrapper_source
    assert ".pyw" in wrapper_source
