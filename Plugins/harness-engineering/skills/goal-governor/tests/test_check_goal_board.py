#!/usr/bin/env python3
"""Focused regression tests for the Goal Governor board validator."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "check_goal_board.py"
SPEC = importlib.util.spec_from_file_location("check_goal_board", SCRIPT_PATH)
assert SPEC is not None
assert SPEC.loader is not None
check_goal_board = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(check_goal_board)


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
