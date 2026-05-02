from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "validation-and-linting"
    / "check_he_active_archive_links.py"
)
SPEC = importlib.util.spec_from_file_location("check_he_active_archive_links", SCRIPT_PATH)
assert SPEC is not None
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules["check_he_active_archive_links"] = MODULE
SPEC.loader.exec_module(MODULE)


def test_active_budget_archive_link_is_violation(tmp_path, monkeypatch) -> None:
    plugin_root = tmp_path / "Plugins" / "harness-engineering"
    archive = plugin_root / "fixtures" / "budget-archive" / "2026-04-21"
    archive.mkdir(parents=True)
    source = archive / "README.md"
    source.write_text("archived\n", encoding="utf-8")
    active = plugin_root / "README.md"
    active.symlink_to("fixtures/budget-archive/2026-04-21/README.md")
    monkeypatch.setattr(MODULE, "PLUGIN_ROOT", plugin_root)

    assert MODULE.iter_violations() == [active]


def test_budget_archive_link_inside_fixtures_is_ignored(tmp_path, monkeypatch) -> None:
    plugin_root = tmp_path / "Plugins" / "harness-engineering"
    archive = plugin_root / "fixtures" / "budget-archive" / "2026-04-21"
    archive.mkdir(parents=True)
    source = archive / "README.md"
    source.write_text("archived\n", encoding="utf-8")
    fixture_link = plugin_root / "fixtures" / "snapshot.md"
    fixture_link.symlink_to("budget-archive/2026-04-21/README.md")
    monkeypatch.setattr(MODULE, "PLUGIN_ROOT", plugin_root)

    assert MODULE.iter_violations() == []


def test_repair_materializes_active_link(tmp_path, monkeypatch) -> None:
    plugin_root = tmp_path / "Plugins" / "harness-engineering"
    archive = plugin_root / "fixtures" / "budget-archive" / "2026-04-21"
    archive.mkdir(parents=True)
    source = archive / "README.md"
    source.write_text("archived\n", encoding="utf-8")
    active = plugin_root / "README.md"
    active.symlink_to("fixtures/budget-archive/2026-04-21/README.md")
    monkeypatch.setattr(MODULE, "PLUGIN_ROOT", plugin_root)

    MODULE.repair_link(active)

    assert not active.is_symlink()
    assert active.read_text(encoding="utf-8") == "archived\n"
    assert MODULE.iter_violations() == []


def test_active_plugin_tests_are_disallowed_payload(tmp_path, monkeypatch) -> None:
    plugin_root = tmp_path / "Plugins" / "harness-engineering"
    tests_dir = plugin_root / "tests"
    tests_dir.mkdir(parents=True)
    monkeypatch.setattr(MODULE, "PLUGIN_ROOT", plugin_root)

    assert MODULE.iter_disallowed_active_payload() == [tests_dir]


def test_active_template_helper_is_disallowed_payload(tmp_path, monkeypatch) -> None:
    plugin_root = tmp_path / "Plugins" / "harness-engineering"
    helper = plugin_root / "skills" / "_template_utils.py"
    helper.parent.mkdir(parents=True)
    helper.write_text("# helper\n", encoding="utf-8")
    monkeypatch.setattr(MODULE, "PLUGIN_ROOT", plugin_root)

    assert MODULE.iter_disallowed_active_payload() == [helper]
