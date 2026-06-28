from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "validation-and-linting"
    / "validate_skill_handoff_freshness.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("validate_skill_handoff_freshness", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _write_artifacts(root: Path, *, status_head: str, tracker_head: str, atlas_head: str) -> tuple[Path, Path, Path]:
    status_json = root / "status.json"
    tracker_json = root / "tracker.json"
    atlas_html = root / "atlas.html"
    status_json.write_text(json.dumps({"repo": {"head": status_head}}), encoding="utf-8")
    tracker_json.write_text(json.dumps({"repo": {"head": tracker_head}}), encoding="utf-8")
    atlas_html.write_text(f'<html data-generated-head="{atlas_head}"></html>', encoding="utf-8")
    return status_json, tracker_json, atlas_html


def test_freshness_accepts_matching_heads(tmp_path: Path) -> None:
    module = _load_module()
    status_json, tracker_json, atlas_html = _write_artifacts(
        tmp_path,
        status_head="abc1234",
        tracker_head="abc1234",
        atlas_head="abc1234",
    )

    findings = module.validate_freshness(
        "abc1234",
        status_json=status_json,
        tracker_json=tracker_json,
        atlas_html=atlas_html,
    )

    assert findings == []


def test_freshness_blocks_stale_status_json(tmp_path: Path) -> None:
    module = _load_module()
    status_json, tracker_json, atlas_html = _write_artifacts(
        tmp_path,
        status_head="stale",
        tracker_head="abc1234",
        atlas_head="abc1234",
    )

    findings = module.validate_freshness(
        "abc1234",
        status_json=status_json,
        tracker_json=tracker_json,
        atlas_html=atlas_html,
    )

    assert [finding.code for finding in findings] == ["status_json_head_stale"]


def test_freshness_blocks_stale_tracker_json(tmp_path: Path) -> None:
    module = _load_module()
    status_json, tracker_json, atlas_html = _write_artifacts(
        tmp_path,
        status_head="abc1234",
        tracker_head="stale",
        atlas_head="abc1234",
    )

    findings = module.validate_freshness(
        "abc1234",
        status_json=status_json,
        tracker_json=tracker_json,
        atlas_html=atlas_html,
    )

    assert [finding.code for finding in findings] == ["tracker_json_head_stale"]


def test_freshness_blocks_stale_atlas_head(tmp_path: Path) -> None:
    module = _load_module()
    status_json, tracker_json, atlas_html = _write_artifacts(
        tmp_path,
        status_head="abc1234",
        tracker_head="abc1234",
        atlas_head="stale",
    )

    findings = module.validate_freshness(
        "abc1234",
        status_json=status_json,
        tracker_json=tracker_json,
        atlas_html=atlas_html,
    )

    assert [finding.code for finding in findings] == ["atlas_generated_head_stale"]
