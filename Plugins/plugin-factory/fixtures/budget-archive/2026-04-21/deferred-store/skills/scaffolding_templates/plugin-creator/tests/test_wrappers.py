#!/usr/bin/env python3
"""Smoke checks for plugin-creator script wrappers."""

from pathlib import Path
import sys

HELPERS_ROOT = Path(__file__).resolve().parents[3]
if str(HELPERS_ROOT) not in sys.path:
    sys.path.insert(0, str(HELPERS_ROOT))

from tests_shared import find_repo_root


def test_creator_wrappers_point_to_impls() -> None:
    """
    Verify wrapper scripts in `scripts/` have matching `.pyw` implementations.

    This asserts each listed wrapper exists in the sibling `scripts` directory
    and that a same-named `.pyw` file exists beside it.
    """
    current = Path(__file__).resolve()
    repo_root = find_repo_root(current)
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
