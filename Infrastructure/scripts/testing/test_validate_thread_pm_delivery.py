from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "validation-and-linting"
    / "validate_thread_pm_delivery.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("validate_thread_pm_delivery", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _valid_report() -> str:
    return json.dumps(
        {
            "schema_version": "thread-report/v1",
            "thread_id": "019f0ab5-07bb-7091-a6a2-9f74d07a65cb",
            "repo_head": "842bda239",
            "task_id": "technical-writer-handoff-readiness-ratchet",
            "status": "blocked",
            "current_gate": "oss-local-repair",
            "next_gate_allowed": False,
            "blocked_next_gates": ["oss-cloud", "tessl-dry-run", "tessl-live"],
            "commands": [_command()],
            "artifact_assertions": [_artifact_assertion()],
            "contradictions": [_contradiction()],
            "files_changed": ["Infrastructure/scripts/lib/ask/skills_sdk/handoff_readiness.py"],
            "lessons": [_lesson()],
            "next_action": "Repair oss-local release-lane failures before oss-cloud.",
        },
        indent=2,
    )


def _command() -> dict[str, str]:
    return {
        "command": "./bin/ask sdk eval run Skills/agent-ops/technical-writer --runner internal --mode release --codex-profile oss-local --json --robot",
        "outcome": "fail",
        "evidence": ".harness/evidence/handoff/technical-writer/oss-local.json",
    }


def _artifact_assertion() -> dict[str, str]:
    return {
        "artifact": ".harness/evidence/handoff/technical-writer/oss-local.json",
        "assertion": "receipt.status == fail",
        "outcome": "pass",
    }


def _contradiction() -> dict[str, str]:
    return {
        "artifact": ".harness/evidence/handoff/technical-writer/eval-handoff-readiness-preview.json",
        "problem": "required_next_actions must route to oss-local repair",
        "owner": "handoff_readiness",
    }


def _lesson() -> dict[str, str]:
    return {
        "lesson": "Profile invocation proof is not behavioral acceptance for oss-local release gates.",
        "failure_pattern": "The lane invoked oss-local correctly but release behavior still failed.",
        "carry_forward_target": ".harness/memory/LEARNINGS.md",
        "deterministic_guardrail": "validate_thread_report.py requires lessons in thread-report/v1.",
        "recorded_in": ".harness/memory/LEARNINGS.md",
        "validation": "python3 Infrastructure/scripts/validation-and-linting/validate_thread_report.py .harness/reports/thread-replies/019f0ab5-07bb-7091-a6a2-9f74d07a65cb/latest.json --json",
    }


def _valid_delivery() -> str:
    return """{
  "schema_version": "thread-report-delivery/v1",
  "thread_id": "019f0ab5-07bb-7091-a6a2-9f74d07a65cb",
  "pm_thread_id": "019f0314-ba59-7a00-ab78-9bd3174d1d03",
  "report_path": "latest.json",
  "delivery_method": "codex_app__send_message_to_thread",
  "delivery_status": "delivered",
  "delivered_at": "2026-06-28T18:30:00Z",
  "message_summary": "Sent PM update referencing the validated thread-report artifact.",
  "delivery_evidence": "send_message_to_thread returned threadId 019f0314-ba59-7a00-ab78-9bd3174d1d03"
}
"""


def test_missing_delivery_receipt_fails_when_required(tmp_path: Path) -> None:
    module = _load_module()
    report = tmp_path / "latest.json"
    report.write_text(_valid_report(), encoding="utf-8")

    findings = module.validate_delivery(
        report,
        tmp_path / "pm-delivery.json",
        require_delivery=True,
    )

    assert any("missing PM delivery receipt" in finding["message"] for finding in findings)


def test_missing_delivery_receipt_can_validate_report_only(tmp_path: Path) -> None:
    module = _load_module()
    report = tmp_path / "latest.json"
    report.write_text(_valid_report(), encoding="utf-8")

    findings = module.validate_delivery(
        report,
        tmp_path / "pm-delivery.json",
        require_delivery=False,
    )

    assert findings == []


def test_delivered_receipt_passes_when_required(tmp_path: Path) -> None:
    module = _load_module()
    report = tmp_path / "latest.json"
    delivery = tmp_path / "pm-delivery.json"
    report.write_text(_valid_report(), encoding="utf-8")
    delivery.write_text(_valid_delivery(), encoding="utf-8")

    findings = module.validate_delivery(report, delivery, require_delivery=True)

    assert findings == []


def test_blocked_delivery_receipt_fails_when_delivery_required(tmp_path: Path) -> None:
    module = _load_module()
    report = tmp_path / "latest.json"
    delivery = tmp_path / "pm-delivery.json"
    report.write_text(_valid_report(), encoding="utf-8")
    delivery.write_text(
        _valid_delivery()
        .replace('"delivery_status": "delivered"', '"delivery_status": "blocked"')
        .replace('"delivery_method": "codex_app__send_message_to_thread"', '"delivery_method": "blocked_no_thread_tool"'),
        encoding="utf-8",
    )

    findings = module.validate_delivery(report, delivery, require_delivery=True)

    assert any(finding["path"] == "delivery.delivery_status" for finding in findings)


def test_delivery_thread_id_must_match_report(tmp_path: Path) -> None:
    module = _load_module()
    report = tmp_path / "latest.json"
    delivery = tmp_path / "pm-delivery.json"
    report.write_text(_valid_report(), encoding="utf-8")
    delivery.write_text(
        _valid_delivery().replace("019f0ab5-07bb-7091-a6a2-9f74d07a65cb", "019f-other-thread", 1),
        encoding="utf-8",
    )

    findings = module.validate_delivery(report, delivery, require_delivery=True)

    assert any(finding["path"] == "delivery.thread_id" for finding in findings)


def test_thread_report_requires_lessons_for_carry_forward(tmp_path: Path) -> None:
    module = _load_module()
    report = tmp_path / "latest.json"
    report.write_text(_valid_report().replace('  "lessons": [', '  "missing_lessons": ['), encoding="utf-8")

    findings = module.validate_delivery(
        report,
        tmp_path / "pm-delivery.json",
        require_delivery=False,
    )

    assert any(finding["path"] == "report.$" and "lessons" in finding["message"] for finding in findings)


def test_thread_report_lesson_cannot_only_point_at_thread_report(tmp_path: Path) -> None:
    module = _load_module()
    report = tmp_path / "latest.json"
    report.write_text(
        _valid_report().replace(
            '"recorded_in": ".harness/memory/LEARNINGS.md"',
            '"recorded_in": ".harness/reports/thread-replies/019f0ab5/latest.json"',
        ),
        encoding="utf-8",
    )

    findings = module.validate_delivery(
        report,
        tmp_path / "pm-delivery.json",
        require_delivery=False,
    )

    assert any(finding["path"] == "report.lessons.0.recorded_in" for finding in findings)


def test_thread_report_requires_learning_ledger_record(tmp_path: Path) -> None:
    module = _load_module()
    report = tmp_path / "latest.json"
    report.write_text(
        _valid_report().replace(
            '"recorded_in": ".harness/memory/LEARNINGS.md"',
            '"recorded_in": "Skills/agent-ops/technical-writer/references/evals.yaml"',
        ),
        encoding="utf-8",
    )

    findings = module.validate_delivery(
        report,
        tmp_path / "pm-delivery.json",
        require_delivery=False,
    )

    assert any(finding["path"] == "report.lessons" for finding in findings)
