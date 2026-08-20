from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "validation-and-linting"
    / "prepare_repo_surface_cleanup.py"
)
SPEC = importlib.util.spec_from_file_location("prepare_repo_surface_cleanup", SCRIPT_PATH)
assert SPEC is not None
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules["prepare_repo_surface_cleanup"] = MODULE
SPEC.loader.exec_module(MODULE)


def _inventory() -> dict:
    return {
        "schema_version": 1,
        "status": "success",
        "summary": {"total_paths": 4, "blocking_findings": 3},
        "findings": [
            {
                "path": "artifacts/run/events.jsonl",
                "classification": "historical_artifact",
                "status": "violation",
                "code": "tracked_historical_artifact",
            },
            {
                "path": "Infrastructure/Infrastructure/artifacts/out.json",
                "classification": "unknown",
                "status": "violation",
                "code": "duplicated_infrastructure_path",
            },
            {
                "path": ".skillsets/codex.json",
                "classification": "unknown",
                "status": "unknown",
                "code": "ownership_decision_required",
            },
        ],
    }


def test_cleanup_report_has_required_groups_and_no_deletions(tmp_path) -> None:
    (tmp_path / "Docs").mkdir()
    (tmp_path / "Docs" / "note.md").write_text("playwright-interactive\n", encoding="utf-8")

    report = MODULE.build_cleanup_report(
        _inventory(),
        repo_root=tmp_path,
        retired_skill_names=["playwright-interactive"],
    )

    assert report["schema_version"] == 1
    assert report["metadata"]["mode"] == "preparation_only"
    assert report["metadata"]["deletions_performed"] is False
    group_names = {group["name"] for group in report["groups"]}
    assert group_names == {
        "historical_generated_artifacts",
        "retired_skill_debris",
        "suspicious_nested_infra_paths",
        "unresolved_generated_runtime_ownership",
    }
    assert report["summary"]["safe_to_delete_total"] == 0
    for group in report["groups"]:
        assert group["state"] in {"candidate", "blocked"}
        assert {"candidate", "blocked", "safe_to_delete"} <= group["state_buckets"].keys()
        assert "safe_to_delete" in group
        assert group["safe_to_delete"] == []
        assert group["reference_scan"]["command"]


def test_retired_skill_reference_hits_block_group(tmp_path) -> None:
    (tmp_path / "Docs").mkdir()
    (tmp_path / "Docs" / "route.md").write_text("Use gh-workflow for GitHub work.\n", encoding="utf-8")

    report = MODULE.build_cleanup_report(
        _inventory(),
        repo_root=tmp_path,
        retired_skill_names=["gh-workflow"],
    )
    retired_group = next(group for group in report["groups"] if group["name"] == "retired_skill_debris")

    assert retired_group["state"] == "blocked"
    assert retired_group["reference_scan"]["total_hits"] == 1
    assert retired_group["blockers"] == ["reference_scan_found_hits"]


def test_candidate_requires_owner_disposition_and_falsification(tmp_path) -> None:
    report = MODULE.build_cleanup_report(_inventory(), repo_root=tmp_path, retired_skill_names=[])
    historical_group = next(
        group for group in report["groups"] if group["name"] == "historical_generated_artifacts"
    )

    assert historical_group["state"] == "candidate"
    assert historical_group["blockers"] == [
        "future_cleanup_pr_must_confirm_owner_disposition_and_falsification"
    ]


def test_write_reports_creates_json_and_markdown(tmp_path) -> None:
    report = MODULE.build_cleanup_report(_inventory(), repo_root=tmp_path, retired_skill_names=[])
    retired_group = next(group for group in report["groups"] if group["name"] == "retired_skill_debris")

    json_path, md_path = MODULE.write_reports(report, tmp_path / "reports")

    assert retired_group["candidate_summary"]["total"] == 0
    assert json.loads(json_path.read_text(encoding="utf-8"))["schema_version"] == 1
    markdown = md_path.read_text(encoding="utf-8")
    assert "Repo Surface Cleanup Preparation" in markdown
    assert "Safe to delete total: `0`" in markdown
