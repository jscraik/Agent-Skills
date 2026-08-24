"""Contract tests for repository-owned CodeRabbit review routing."""

from __future__ import annotations

from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = REPO_ROOT / ".coderabbit.yaml"


def _path_filters() -> list[str]:
    payload = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    return payload["reviews"]["path_filters"]


def test_coderabbit_reviews_every_tracked_path_by_default() -> None:
    filters = _path_filters()
    assert filters[0] == "**"
    assert "!artifacts/**" not in filters


def test_coderabbit_keeps_build_output_exclusions() -> None:
    filters = _path_filters()
    assert "!**/coverage/**" in filters
    assert "!**/dist/**" in filters
    assert "!**/node_modules/**" in filters
