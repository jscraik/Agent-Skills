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
