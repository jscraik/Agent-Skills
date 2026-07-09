from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = REPO_ROOT / "Infrastructure" / "scripts" / "validation-and-linting" / "validate_thread_report.py"


def _load_validator_module() -> object:
    spec = importlib.util.spec_from_file_location("validate_thread_report", VALIDATOR)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _base_report() -> dict[str, Any]:
    return {
        "schema_version": "thread-report/v1",
        "thread_id": "worker-thread-01",
        "agent_profile_selection": _profile_selection(),
        "repo_head": "main@abc123",
        "task_id": "profile-aware-dispatch-test",
        "status": "pass",
        "current_gate": "validation",
        "next_gate_allowed": False,
        "blocked_next_gates": ["implementation"],
        "commands": [_command_result()],
        "artifact_assertions": [_artifact_assertion()],
        "contradictions": [_contradiction()],
        "files_changed": [".harness/memory/LEARNINGS.md"],
        "lessons": [_lesson()],
        "next_action": "Return to PM with validation evidence.",
    }


def _profile_selection() -> dict[str, str]:
    return {
        "requested_role": "QA Disproof",
        "selected_profile_role": "correctness-reviewer",
        "profile_source": "/Users/jamiecraik/.codex/agents/manifest.json",
        "reason_selected": "Behavioral disproof needs a correctness-specialist profile.",
    }


def _command_result() -> dict[str, str]:
    return {"command": "true", "outcome": "pass", "evidence": "command exited 0"}


def _artifact_assertion() -> dict[str, str]:
    return {
        "artifact": ".harness/memory/LEARNINGS.md",
        "assertion": "learning ledger exists",
        "outcome": "pass",
    }


def _contradiction() -> dict[str, str]:
    return {"artifact": ".harness/memory/LEARNINGS.md", "problem": "none observed", "owner": "pm"}


def _lesson() -> dict[str, str]:
    return {
        "lesson": "Dispatch reports must record the agent profile used.",
        "failure_pattern": "profile-agnostic dispatch hides task routing quality.",
        "carry_forward_target": "thread-report/v1 validation",
        "deterministic_guardrail": "validate_thread_report rejects missing profile selection.",
        "recorded_in": ".harness/memory/LEARNINGS.md",
        "validation": "validate_thread_report focused tests",
    }


class TestThreadReportDispatchGuards(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.validator = _load_validator_module()

    def finding_paths(self, report: dict[str, Any]) -> set[str]:
        return {finding["path"] for finding in self.validator.validate_thread_report(report)}

    def test_thread_report_requires_agent_profile_selection(self) -> None:
        report = _base_report()
        report.pop("agent_profile_selection")

        self.assertIn("agent_profile_selection", self.finding_paths(report))

    def test_waiting_state_requires_outbound_escalation_evidence(self) -> None:
        report = _base_report()
        report["status"] = "blocked"
        report["next_action"] = "awaiting PM authorization before continuing"

        self.assertIn("outbound_escalation", self.finding_paths(report))

    def test_waiting_state_accepts_escalation_blocked_evidence(self) -> None:
        report = _base_report()
        report["status"] = "blocked"
        report["next_action"] = "awaiting PM authorization before continuing"
        report["escalation_blocked"] = {
            "target_lane": "project-pm",
            "delivery_status": "blocked",
            "evidence": "codex_app__send_message_to_thread unavailable",
        }

        self.assertNotIn("outbound_escalation", self.finding_paths(report))


if __name__ == "__main__":
    unittest.main()
