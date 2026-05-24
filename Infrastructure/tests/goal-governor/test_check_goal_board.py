#!/usr/bin/env python3
"""Focused regression tests for the Goal Governor board validator."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory


REPO_ROOT = Path(__file__).resolve().parents[3]
SKILL_ROOT = REPO_ROOT / "Skills" / "agent-ops" / "goal-governor"
SCRIPT_PATH = SKILL_ROOT / "scripts" / "check_goal_board.py"
SKILL_PATH = SKILL_ROOT / "SKILL.md"
CONTRACT_PATH = SKILL_ROOT / "references" / "contract.yaml"
EVALS_PATH = SKILL_ROOT / "references" / "evals.yaml"
SPEC = importlib.util.spec_from_file_location("check_goal_board", SCRIPT_PATH)
assert SPEC is not None
assert SPEC.loader is not None
check_goal_board = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(check_goal_board)


def test_goal_governor_review_mode_guard_is_documented() -> None:
    skill = SKILL_PATH.read_text(encoding="utf-8")
    normalized_skill = " ".join(skill.split())
    contract = check_goal_board.load_yaml(CONTRACT_PATH)
    evals = check_goal_board.load_yaml(EVALS_PATH)

    for expected in (
        "review",
        "PROMPT_REVIEW_ONLY",
        "proceed with governed implementation",
        "check this prompt",
        "not start yet",
    ):
        assert expected in normalized_skill

    review_contract = contract["review_mode_contract"]
    assert review_contract["execution_override_phrase"] == "proceed with governed implementation"
    assert review_contract["route_when_override_present"] == "continue"
    assert contract["output_contract"]["mode_specific_overrides"]["review"]

    assert review_contract["required_fields"] == [
        "prompt_readiness",
        "interpreted_objective",
        "target_repository",
        "proposed_first_slice",
        "required_permissions",
        "external_systems_that_would_be_touched",
        "expected_artifacts",
        "stop_conditions",
        "questions_or_contradictions",
        "governor_start_command",
    ]
    assert review_contract["forbidden_actions"] == [
        "create_goal",
        "native goal continuation",
        "spawn agents",
        "tracker mutation",
        "commit",
        "pull request",
        "CI monitoring",
        "implementation edits",
    ]

    cases = {case["id"]: case for case in evals["cases"]}
    assert cases["review-goal-prompt-not-start-yet"]["expected_route"] == "review"
    assert cases["review-language-with-execution-override"]["expected_route"] == "continue"


def test_goal_md_must_be_a_file() -> None:
    with TemporaryDirectory() as tmp:
        goal_dir = Path(tmp)
        (goal_dir / "goal.md").mkdir()
        (goal_dir / "goal.md" / ".gitkeep").write_text("", encoding="utf-8")
        (goal_dir / "notes").mkdir()
        (goal_dir / "state.yaml").write_text(
            """\
version: 2
goal:
  slug: invalid-goal-dir
  status: active
  objective: "Reject boards where goal.md is not a file."
completion_contract:
  outcome: "Reject boards where goal.md is not a file."
  verification_surface:
    - "Goal board validator output."
  constraints:
    - "Preserve board safety rules."
  boundaries:
    - "Use only this temporary goal directory."
  iteration_policy: "Fix the next validator blocker."
  blocked_stop_condition: "Stop with the validator error."
tasks:
  - id: T001
    type: scout
    assignee: Scout
    status: active
    objective: "Find validation commands."
    inputs: []
    constraints:
      - "Read-only."
    expected_output: "Evidence receipt."
    allowed_files: []
    verify: []
    stop_if:
      - "Needs write access."
    receipt_id: null
""",
            encoding="utf-8",
        )

        assert "goal.md must be a file" in check_goal_board.validate_board(goal_dir)


def test_native_objective_has_codex_length_limit() -> None:
    state = {
        "goal": {
            "status": "active",
            "native_objective": "x" * 4001,
            "native_status": "active",
            "token_budget": 1000,
            "tokens_used": 0,
            "time_used_seconds": 0,
        }
    }

    errors, _ = check_goal_board.validate_goal_section(state)

    assert "goal.native_objective must be at most 4000 characters" in errors


def test_native_goal_runtime_fields_accept_budget_limited_status() -> None:
    state = {
        "goal": {
            "status": "active",
            "native_objective": "/goal Follow docs/goals/current/goal.md",
            "native_status": "budget_limited",
            "token_budget": 1000,
            "tokens_used": 1000,
            "time_used_seconds": 60,
        }
    }

    errors, goal_status = check_goal_board.validate_goal_section(state)

    assert errors == []
    assert goal_status == "active"


def test_native_goal_runtime_fields_accept_raw_budget_limited_status() -> None:
    state = {
        "goal": {
            "status": "active",
            "native_objective": "/goal Follow docs/goals/current/goal.md",
            "native_status": "budgetLimited",
            "token_budget": 1000,
            "tokens_used": 1000,
            "time_used_seconds": 60,
        }
    }

    errors, goal_status = check_goal_board.validate_goal_section(state)

    assert errors == []
    assert goal_status == "active"


def test_native_goal_runtime_fields_accept_identity_and_timestamps() -> None:
    state = {
        "goal": {
            "status": "active",
            "native_objective": "/goal Follow docs/goals/current/goal.md",
            "native_status": "active",
            "native_goal_id": "goal_abc-123",
            "native_created_at": "2026-05-13T10:00:00Z",
            "native_updated_at": "2026-05-13T10:05:00Z",
            "token_budget": 1000,
            "tokens_used": 10,
            "time_used_seconds": 60,
        }
    }

    errors, goal_status = check_goal_board.validate_goal_section(state)

    assert errors == []
    assert goal_status == "active"


def test_native_goal_runtime_fields_accept_usage_limited_statuses() -> None:
    for native_status in ("usageLimited", "usage_limited"):
        state = {
            "goal": {
                "status": "blocked",
                "native_objective": "/goal Follow docs/goals/current/goal.md",
                "native_status": native_status,
                "token_budget": 1000,
                "tokens_used": 1000,
                "time_used_seconds": 60,
            }
        }

        errors, goal_status = check_goal_board.validate_goal_section(state)

        assert errors == []
        assert goal_status == "blocked"


def test_native_goal_runtime_fields_accept_blocked_status() -> None:
    state = {
        "goal": {
            "status": "blocked",
            "native_objective": "/goal Follow docs/goals/current/goal.md",
            "native_status": "blocked",
            "token_budget": None,
            "tokens_used": 500,
            "time_used_seconds": 90,
        }
    }

    errors, goal_status = check_goal_board.validate_goal_section(state)

    assert errors == []
    assert goal_status == "blocked"


def test_native_goal_id_must_be_opaque_identifier_when_present() -> None:
    state = {
        "goal": {
            "status": "active",
            "native_objective": "/goal Follow docs/goals/current/goal.md",
            "native_status": "active",
            "native_goal_id": "not an id",
        }
    }

    errors, _ = check_goal_board.validate_goal_section(state)

    assert "goal.native_goal_id must be a non-empty opaque id when present" in errors


def test_completion_contract_is_required() -> None:
    state = {
        "goal": {
            "status": "active",
            "objective": "Keep working until the board has evidence.",
        }
    }

    errors = check_goal_board.validate_completion_contract(state)

    assert "completion_contract must be a mapping" in errors


def test_completion_contract_requires_goal_shape_fields() -> None:
    state = {
        "completion_contract": {
            "outcome": "Produce an auditable goal board.",
            "verification_surface": ["check_goal_board.py output"],
            "constraints": ["Do not broaden Worker scope."],
            "boundaries": ["docs/goals/current"],
            "iteration_policy": "Choose the next action from current evidence.",
            "blocked_stop_condition": "Stop with blocker evidence when no safe path remains.",
        }
    }

    assert check_goal_board.validate_completion_contract(state) == []


def test_continuation_gate_accepts_idle_thread_contract() -> None:
    state = {
        "continuation_gate": {
            "native_status": "active",
            "goal_active": "pass",
            "thread_idle": "pass",
            "queued_user_input": "absent",
            "pending_work": "absent",
            "auto_continue_allowed": "yes",
        }
    }

    assert check_goal_board.validate_continuation_gate(state) == []


def test_claim_ledger_validates_research_status_shape() -> None:
    state = {
        "claims": [
            {
                "id": "C001",
                "claim": "The research result is approximately reproduced.",
                "evidence_surface": ["benchmark output", "generated report"],
                "route": "approximate",
                "status": "supported",
                "remaining_uncertainty": ["Original seeds are unavailable."],
            }
        ]
    }

    assert check_goal_board.validate_claims(state) == []
