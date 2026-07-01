from __future__ import annotations

import json
import os
import sys
from pathlib import Path


VALIDATOR_DIR = Path(__file__).resolve().parents[1] / "scripts" / "validation-and-linting"
if str(VALIDATOR_DIR) not in sys.path:
    sys.path.insert(0, str(VALIDATOR_DIR))

import validate_repo_layout  # noqa: E402


def _write_config(path: Path) -> None:
    source = Path(__file__).resolve().parents[1] / "config" / "repo-layout.v1.json"
    path.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")


def _minimal_repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    (root / "Infrastructure" / "config").mkdir(parents=True)
    _write_config(root / "Infrastructure" / "config" / "repo-layout.v1.json")
    for dirname in (".agents", ".harness", "Infrastructure", "Skills"):
        (root / dirname).mkdir(exist_ok=True)
    (root / "README.md").write_text("repo\n", encoding="utf-8")
    return root


def test_current_repository_layout_policy_passes_without_unknown_symlinks() -> None:
    root = Path(__file__).resolve().parents[2]
    report = validate_repo_layout.validate_repo_layout(
        root, root / "Infrastructure" / "config" / "repo-layout.v1.json"
    )

    assert report["status"] == "pass"
    assert report["summary"]["blocking_count"] == 0


def test_runtime_projection_symlink_is_allowed(tmp_path: Path) -> None:
    root = _minimal_repo(tmp_path)
    (root / ".agents" / "skills").mkdir(parents=True)
    os.symlink("../../Skills/agent-ops/testing", root / ".agents" / "skills" / "testing")

    report = validate_repo_layout.validate_repo_layout(
        root, root / "Infrastructure" / "config" / "repo-layout.v1.json"
    )

    assert report["status"] == "pass"
    symlink_findings = [
        finding for finding in report["findings"] if finding["path"] == ".agents/skills/testing"
    ]
    assert symlink_findings
    assert symlink_findings[0]["classification"] == "runtime_projection"


def test_unknown_symlink_blocks_layout_validation(tmp_path: Path) -> None:
    root = _minimal_repo(tmp_path)
    os.symlink("Infrastructure", root / "mystery-link")

    report = validate_repo_layout.validate_repo_layout(
        root, root / "Infrastructure" / "config" / "repo-layout.v1.json"
    )

    assert report["status"] == "fail"
    assert any(finding["code"] == "unknown_symlink" for finding in report["findings"])


def test_capitalized_plugin_internal_alias_is_allowed(tmp_path: Path) -> None:
    root = _minimal_repo(tmp_path)
    alias_dir = root / "Plugins" / "skill-factory" / "skills"
    alias_dir.mkdir(parents=True)
    os.symlink("../../../Skills/agent-ops/testing", alias_dir / "skill-refactor")

    report = validate_repo_layout.validate_repo_layout(
        root, root / "Infrastructure" / "config" / "repo-layout.v1.json"
    )

    assert report["status"] == "pass"
    alias_findings = [
        finding
        for finding in report["findings"]
        if finding["path"] == "Plugins/skill-factory/skills/skill-refactor"
    ]
    assert alias_findings
    assert alias_findings[0]["classification"] == "compatibility_alias"


def test_future_nested_foundry_paths_classify_top_level_root(tmp_path: Path) -> None:
    root = _minimal_repo(tmp_path)
    (root / "foundry" / "skills").mkdir(parents=True)

    report = validate_repo_layout.validate_repo_layout(
        root, root / "Infrastructure" / "config" / "repo-layout.v1.json"
    )

    assert report["status"] == "pass"
    assert not any(
        finding["code"] == "top_level_unclassified" and finding["path"] == "foundry"
        for finding in report["findings"]
    )


def test_root_infrastructure_alias_is_deprecated_warning(tmp_path: Path) -> None:
    root = _minimal_repo(tmp_path)
    os.symlink("Infrastructure/scripts", root / "scripts")

    report = validate_repo_layout.validate_repo_layout(
        root, root / "Infrastructure" / "config" / "repo-layout.v1.json"
    )

    script_findings = [finding for finding in report["findings"] if finding["path"] == "scripts"]
    assert script_findings
    assert script_findings[0]["status"] == "warning"
    assert script_findings[0]["severity"] == "warning"
    assert script_findings[0]["classification"] == "compatibility_alias"
    assert report["status"] == "pass"


def test_unknown_top_level_directory_blocks(tmp_path: Path) -> None:
    root = _minimal_repo(tmp_path)
    (root / "random-new-root").mkdir()

    report = validate_repo_layout.validate_repo_layout(
        root, root / "Infrastructure" / "config" / "repo-layout.v1.json"
    )

    assert report["status"] == "fail"
    assert any(
        finding["code"] == "top_level_unclassified"
        and finding["path"] == "random-new-root"
        for finding in report["findings"]
    )


def test_json_report_is_serializable(tmp_path: Path) -> None:
    root = _minimal_repo(tmp_path)
    report = validate_repo_layout.validate_repo_layout(
        root, root / "Infrastructure" / "config" / "repo-layout.v1.json"
    )

    assert json.loads(json.dumps(report))["schema_version"] == "repo-layout-validation.v1"
