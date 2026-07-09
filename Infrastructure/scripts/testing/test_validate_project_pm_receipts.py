from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "validation-and-linting"
    / "validate_project_pm_receipts.py"
)
SPEC = importlib.util.spec_from_file_location("validate_project_pm_receipts", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
validate_project_pm_receipts = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validate_project_pm_receipts
SPEC.loader.exec_module(validate_project_pm_receipts)


def test_requires_evidence_boundary_and_next_owner() -> None:
    findings = validate_project_pm_receipts.validate_payload(
        ".harness/reports/project-pm/example.json",
        {"schema_version": "pm-heartbeat/v1", "status": "done"},
    )

    assert {finding.code for finding in findings} == {
        "missing_command_evidence",
        "missing_unproven_boundary",
        "missing_next_owner_or_outbound",
    }


def test_accepts_outbound_commit_closeout_shape() -> None:
    findings = validate_project_pm_receipts.validate_payload(
        ".harness/reports/project-pm/example.json",
        {
            "schema_version": "pm-outbound-commit-closeout/v1",
            "status": "committed_not_pushed",
            "validation": [{"command": "python3 check.py", "outcome": "pass"}],
            "what_remains_unproven": ["hosted CI"],
            "push_or_pr_needed": {"needed": True, "reason": "local branch is ahead"},
        },
    )

    assert findings == []


def test_scan_does_not_apply_qa_worktree_gate_to_outbound_receipts(tmp_path: Path, monkeypatch) -> None:
    receipt = tmp_path / ".harness" / "reports" / "project-pm" / "agent-skills" / "outbound.json"
    receipt.parent.mkdir(parents=True)
    receipt.write_text(
        """{
          "schema_version": "pm-outbound-commit-closeout/v1",
          "status": "committed_not_pushed",
          "validation": [{"command": "python3 check.py", "outcome": "pass"}],
          "what_remains_unproven": ["hosted CI"],
          "push_or_pr_needed": {"needed": true, "reason": "local branch is ahead"}
        }""",
        encoding="utf-8",
    )
    monkeypatch.setattr(validate_project_pm_receipts, "REPO_ROOT", tmp_path)

    findings = validate_project_pm_receipts.scan_paths(
        [".harness/reports/project-pm/agent-skills/outbound.json"]
    )

    assert findings == []


def test_only_scans_project_pm_json_receipts() -> None:
    assert validate_project_pm_receipts.should_scan_path(
        ".harness/reports/project-pm/agent-skills/no-breadcrumbs/outbound-commit-closeout-20260706T072500Z.json"
    )
    assert not validate_project_pm_receipts.should_scan_path(
        ".harness/reports/thread-replies/example/latest.json"
    )


def test_project_pm_scan_runs_qa_worktree_gate(tmp_path: Path, monkeypatch) -> None:
    receipt = tmp_path / ".harness" / "reports" / "project-pm" / "agent-skills" / "dispatch.json"
    receipt.parent.mkdir(parents=True)
    receipt.write_text(
        """{
          "schema_version": "qa-project-backed-dispatch/v1",
          "status": "project_backed_qa_dispatched_monitoring_required",
          "commands": [{"command": "dispatch", "outcome": "pass"}],
          "claims_boundary": {"not_proven": ["implementation worktree"]},
          "next_action": "block QA",
          "qa_lane": {
            "implementation_worktree": "/private/tmp/agent-skills-missing-worktree-for-test"
          },
          "durable_preservation": {
            "strategy": "committed_branch",
            "branch": "codex/example",
            "commit_sha": "abc123"
          }
        }""",
        encoding="utf-8",
    )
    monkeypatch.setattr(validate_project_pm_receipts, "REPO_ROOT", tmp_path)

    findings = validate_project_pm_receipts.scan_paths(
        [".harness/reports/project-pm/agent-skills/dispatch.json"]
    )

    assert any(finding.code == "implementation_worktree_missing" for finding in findings)
