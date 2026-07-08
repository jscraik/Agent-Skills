from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "validation-and-linting"
    / "validate_pm_qa_worktree_gate.py"
)
SPEC = importlib.util.spec_from_file_location("validate_pm_qa_worktree_gate", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
validate_pm_qa_worktree_gate = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validate_pm_qa_worktree_gate
SPEC.loader.exec_module(validate_pm_qa_worktree_gate)


def test_rejects_active_qa_dispatch_when_worktree_missing() -> None:
    findings = validate_pm_qa_worktree_gate.validate_payload(
        {
            "schema_version": "qa-project-backed-dispatch/v1",
            "status": "project_backed_qa_dispatched_monitoring_required",
            "qa_lane": {
                "implementation_worktree": "/private/tmp/agent-skills-missing-worktree-for-test",
            },
            "durable_preservation": {
                "strategy": "committed_branch",
                "branch": "codex/example",
                "commit_sha": "abc123",
            },
        }
    )

    assert any(finding.code == "implementation_worktree_missing" for finding in findings)


def test_dispatch_schema_with_unknown_status_fails_closed_for_missing_worktree() -> None:
    findings = validate_pm_qa_worktree_gate.validate_payload(
        {
            "schema_version": "qa-project-backed-dispatch/v1",
            "status": "qa_dispatchd",
            "qa_lane": {
                "implementation_worktree": "/private/tmp/agent-skills-missing-worktree-for-test",
            },
            "durable_preservation": {
                "strategy": "committed_branch",
                "branch": "codex/example",
                "commit_sha": "abc123",
            },
        }
    )

    assert any(finding.code == "implementation_worktree_missing" for finding in findings)


def test_unknown_status_on_worktree_missing_schema_fails_closed() -> None:
    findings = validate_pm_qa_worktree_gate.validate_payload(
        {
            "schema_version": "qa-project-backed-worktree-missing/v1",
            "status": "blockd_missing_implementation_worktree",
            "missing_target": {
                "implementation_worktree": "/private/tmp/agent-skills-missing-worktree-for-test",
            },
            "durable_preservation": {
                "strategy": "operator_approved_volatile_worktree_risk",
            },
        }
    )

    assert any(finding.code == "implementation_worktree_missing" for finding in findings)


def test_rejects_temp_worktree_without_preservation_strategy(tmp_path: Path) -> None:
    worktree = tmp_path / "agent-skills-worktree"
    worktree.mkdir()

    findings = validate_pm_qa_worktree_gate.validate_payload(
        {
            "schema_version": "qa-project-backed-dispatch/v1",
            "status": "project_backed_qa_dispatched_monitoring_required",
            "qa_lane": {
                "implementation_worktree": worktree.as_posix(),
            },
        }
    )

    assert any(finding.code == "missing_durable_preservation_strategy" for finding in findings)


def test_accepts_existing_temp_worktree_with_patch_preservation(tmp_path: Path) -> None:
    worktree = tmp_path / "agent-skills-worktree"
    patch_artifact = Path(__file__)
    worktree.mkdir()

    findings = validate_pm_qa_worktree_gate.validate_payload(
        {
            "schema_version": "qa-project-backed-dispatch/v1",
            "status": "project_backed_qa_dispatched_monitoring_required",
            "qa_lane": {
                "implementation_worktree": worktree.as_posix(),
            },
            "durable_preservation": {
                "strategy": "patch_artifact",
                "patch_artifact": patch_artifact.as_posix(),
            },
        }
    )

    assert findings == []


def test_rejects_operator_approved_volatile_risk_for_active_dispatch(tmp_path: Path) -> None:
    worktree = tmp_path / "agent-skills-worktree"
    worktree.mkdir()

    findings = validate_pm_qa_worktree_gate.validate_payload(
        {
            "schema_version": "qa-project-backed-dispatch/v1",
            "status": "project_backed_qa_dispatched_monitoring_required",
            "qa_lane": {
                "implementation_worktree": worktree.as_posix(),
            },
            "durable_preservation": {
                "strategy": "operator_approved_volatile_worktree_risk",
            },
        }
    )

    assert any(finding.code == "volatile_preservation_not_durable" for finding in findings)


def test_rejects_patch_artifact_inside_temp_worktree(tmp_path: Path) -> None:
    worktree = tmp_path / "agent-skills-worktree"
    worktree.mkdir()
    patch_artifact = worktree / "recovery.patch"
    patch_artifact.write_text("diff --git a/example b/example\n", encoding="utf-8")

    findings = validate_pm_qa_worktree_gate.validate_payload(
        {
            "schema_version": "qa-project-backed-dispatch/v1",
            "status": "project_backed_qa_dispatched_monitoring_required",
            "qa_lane": {
                "implementation_worktree": worktree.as_posix(),
            },
            "durable_preservation": {
                "strategy": "patch_artifact",
                "patch_artifact": patch_artifact.as_posix(),
            },
        }
    )

    assert any(finding.code == "volatile_patch_artifact" for finding in findings)


def test_committed_branch_requires_commit_sha(tmp_path: Path) -> None:
    worktree = tmp_path / "agent-skills-worktree"
    worktree.mkdir()

    findings = validate_pm_qa_worktree_gate.validate_payload(
        {
            "schema_version": "qa-project-backed-dispatch/v1",
            "status": "project_backed_qa_dispatched_monitoring_required",
            "qa_lane": {
                "implementation_worktree": worktree.as_posix(),
            },
            "durable_preservation": {
                "strategy": "committed_branch",
                "branch": "codex/example",
            },
        }
    )

    assert any(finding.code == "missing_preservation_commit" for finding in findings)


def test_prefers_qa_lane_implementation_worktree_over_target_worktree(tmp_path: Path) -> None:
    target_worktree = tmp_path / "qa-target"
    target_worktree.mkdir()

    findings = validate_pm_qa_worktree_gate.validate_payload(
        {
            "schema_version": "qa-project-backed-dispatch/v1",
            "status": "project_backed_qa_dispatched_monitoring_required",
            "target_worktree": target_worktree.as_posix(),
            "qa_lane": {
                "implementation_worktree": "/private/tmp/agent-skills-missing-worktree-for-test",
            },
            "durable_preservation": {
                "strategy": "committed_branch",
                "branch": "codex/example",
                "commit_sha": "abc123",
            },
        }
    )

    assert any(finding.code == "implementation_worktree_missing" for finding in findings)


def test_blocked_missing_worktree_receipt_is_allowed() -> None:
    findings = validate_pm_qa_worktree_gate.validate_payload(
        {
            "schema_version": "qa-project-backed-worktree-missing/v1",
            "status": "blocked_missing_implementation_worktree",
            "missing_target": {
                "implementation_worktree": "/private/tmp/agent-skills-missing-worktree-for-test",
            },
        }
    )

    assert findings == []


def test_cli_reports_missing_worktree(tmp_path: Path, capsys) -> None:
    fixture = tmp_path / "dispatch.json"
    fixture.write_text(
        json.dumps(
            {
                "schema_version": "qa-project-backed-dispatch/v1",
                "status": "project_backed_qa_dispatched_monitoring_required",
                "qa_lane": {
                    "implementation_worktree": "/private/tmp/agent-skills-missing-worktree-for-test",
                },
                "durable_preservation": {
                    "strategy": "operator_approved_volatile_worktree_risk",
                },
            }
        ),
        encoding="utf-8",
    )

    exit_code = validate_pm_qa_worktree_gate.main([fixture.as_posix(), "--json"])

    assert exit_code == 1
    output = json.loads(capsys.readouterr().out)
    assert output["status"] == "fail"
    assert output["findings"][0]["code"] == "implementation_worktree_missing"
