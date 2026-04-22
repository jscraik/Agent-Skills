#!/usr/bin/env python3
"""Smoke checks for plugin-creator script wrappers."""

from pathlib import Path


def _find_repo_root(current: Path) -> Path:
    for parent in current.parents:
        if (parent / "AGENTS.md").exists() and (parent / "Plugins").exists():
            return parent
    raise AssertionError(f"could not locate repo root from {current}")


def test_creator_wrappers_point_to_impls() -> None:
    """
    Verify wrapper scripts in `scripts/` have matching `.pyw` implementations.

    This asserts each listed wrapper exists in the sibling `scripts` directory
    and that a same-named `.pyw` file exists beside it.
    """
    current = Path(__file__).resolve()
    repo_root = _find_repo_root(current)
    scripts_dir = (
        repo_root
        / "Plugins"
        / "plugin-factory"
        / "skills"
        / "scaffolding_templates"
        / "plugin-creator"
        / "scripts"
    )
    script_names = (
        "create_basic_plugin.py",
        "check_plugin_creator_template_drift.py",
    )

    for script_name in script_names:
        script_path = scripts_dir / script_name
        impl_path = script_path.with_suffix(".pyw")
        assert script_path.exists()
        assert impl_path.exists()
