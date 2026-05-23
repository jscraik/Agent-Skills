from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.services.plugin_sources import copy_directory_contents


def test_copy_directory_contents_materializes_safe_nested_symlinks(tmp_path: Path) -> None:
    source = tmp_path / "source"
    target = tmp_path / "target"
    fixture_plugin = (
        source
        / "fixtures"
        / "archive"
        / "skills"
        / "plugin-builder"
        / "fixtures"
        / "demo"
        / ".codex-plugin"
    )
    copied_plugin = (
        source
        / "skills"
        / "code_quality_review"
        / "plugin-builder"
        / "fixtures"
        / "demo"
        / ".codex-plugin"
    )
    fixture_plugin.mkdir(parents=True)
    copied_plugin.mkdir(parents=True)
    (fixture_plugin / "plugin.json").write_text('{"name":"demo"}\n', encoding="utf-8")
    (copied_plugin / "plugin.json").symlink_to(
        "../../../../../../fixtures/archive/skills/plugin-builder/fixtures/demo/.codex-plugin/plugin.json"
    )

    copy_directory_contents(source, target)

    materialized = (
        target
        / "skills"
        / "code_quality_review"
        / "plugin-builder"
        / "fixtures"
        / "demo"
        / ".codex-plugin"
        / "plugin.json"
    )
    assert materialized.is_file()
    assert not materialized.is_symlink()
    assert materialized.read_text(encoding="utf-8") == '{"name":"demo"}\n'


def test_copy_directory_contents_rejects_escaping_symlink(tmp_path: Path) -> None:
    source = tmp_path / "source"
    target = tmp_path / "target"
    outside = tmp_path / "outside.json"
    source.mkdir()
    outside.write_text("secret\n", encoding="utf-8")
    (source / "plugin.json").symlink_to(os.path.relpath(outside, source))

    with pytest.raises(ValueError, match="Unsafe plugin cache symlink"):
        copy_directory_contents(source, target)
