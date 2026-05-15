from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "validation-and-linting"
    / "check_plugin_active_archive_links.py"
)
SPEC = importlib.util.spec_from_file_location("check_plugin_active_archive_links", SCRIPT_PATH)
assert SPEC is not None
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules["check_plugin_active_archive_links"] = MODULE
SPEC.loader.exec_module(MODULE)


def test_active_budget_archive_link_is_violation(tmp_path) -> None:
    plugin_root = tmp_path / "Plugins" / "skill-factory"
    archive = plugin_root / "fixtures" / "budget-archive" / "2026-04-21"
    archive.mkdir(parents=True)
    source = archive / "README.md"
    source.write_text("archived\n", encoding="utf-8")
    active = plugin_root / "README.md"
    active.symlink_to("fixtures/budget-archive/2026-04-21/README.md")

    assert MODULE.iter_violations(plugin_root) == [active]


def test_budget_archive_link_inside_fixtures_is_ignored(tmp_path) -> None:
    plugin_root = tmp_path / "Plugins" / "skill-factory"
    archive = plugin_root / "fixtures" / "budget-archive" / "2026-04-21"
    archive.mkdir(parents=True)
    source = archive / "README.md"
    source.write_text("archived\n", encoding="utf-8")
    fixture_link = plugin_root / "fixtures" / "snapshot.md"
    fixture_link.symlink_to("budget-archive/2026-04-21/README.md")

    assert MODULE.iter_violations(plugin_root) == []


def test_active_alias_inside_plugin_is_allowed(tmp_path) -> None:
    plugin_root = tmp_path / "Plugins" / "skill-factory"
    target = plugin_root / "skills" / "code_quality_review" / "skill-builder"
    target.mkdir(parents=True)
    alias = plugin_root / "skills" / "skill-builder"
    alias.parent.mkdir(parents=True, exist_ok=True)
    alias.symlink_to("code_quality_review/skill-builder")

    assert MODULE.iter_violations(plugin_root) == []
