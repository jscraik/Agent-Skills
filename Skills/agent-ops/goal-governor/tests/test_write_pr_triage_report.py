#!/usr/bin/env python3
"""Focused tests for the Goal Governor PR triage artifact writer."""

from __future__ import annotations

import importlib.util
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "write_pr_triage_report.py"
SPEC = importlib.util.spec_from_file_location("write_pr_triage_report", SCRIPT_PATH)
assert SPEC is not None
assert SPEC.loader is not None
write_pr_triage_report = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = write_pr_triage_report
SPEC.loader.exec_module(write_pr_triage_report)


def make_runner(
    *,
    worktree: Path,
    expected_head: str = "abc123",
    pwd: str | None = None,
    checks_exit: int = 0,
    reviews: list[object] | None = None,
    pr_head: str | None = None,
) -> write_pr_triage_report.Runner:
    actual_pwd = str(worktree if pwd is None else pwd)
    actual_pr_head = pr_head or expected_head
    actual_reviews = [] if reviews is None else reviews

    def runner(command: tuple[str, ...], cwd: Path) -> write_pr_triage_report.CommandResult:
        outputs = {
            ("pwd",): actual_pwd + "\n",
            ("git", "branch", "--show-current"): "codex/jsc-351-skills-sdk-service-boundary\n",
            ("git", "rev-parse", "HEAD"): expected_head + "\n",
            ("git", "status", "--short", "--branch"): "## codex/jsc-351-skills-sdk-service-boundary...origin/codex/jsc-351-skills-sdk-service-boundary\n",
        }
        if command in outputs:
            return write_pr_triage_report.CommandResult(command, 0, outputs[command], "")
        if command[:3] == ("gh", "pr", "view"):
            return write_pr_triage_report.CommandResult(
                command,
                0,
                json.dumps(
                    {
                        "number": 196,
                        "state": "OPEN",
                        "isDraft": True,
                        "mergeable": "MERGEABLE",
                        "reviewDecision": "",
                        "headRefOid": actual_pr_head,
                        "headRefName": "codex/jsc-351-skills-sdk-service-boundary",
                        "url": "https://github.com/jscraik/Agent-Skills/pull/196",
                        "title": "refactor(jsc-351): extract skills sdk service boundaries",
                    }
                ),
                "",
            )
        if command[:3] == ("gh", "pr", "checks"):
            return write_pr_triage_report.CommandResult(
                command,
                checks_exit,
                "test pass 28s https://example.test\n" if checks_exit == 0 else "test fail 28s https://example.test\n",
                "",
            )
        if command[-1].endswith("/reviews"):
            return write_pr_triage_report.CommandResult(command, 0, json.dumps(actual_reviews), "")
        if command[-1].endswith("/comments"):
            return write_pr_triage_report.CommandResult(command, 0, "[]", "")
        raise AssertionError(f"unexpected command: {command_text(command)}")

    return runner


def command_text(command: tuple[str, ...]) -> str:
    return " ".join(command)


def test_report_blocks_when_submitted_reviews_are_missing() -> None:
    with TemporaryDirectory() as tmp:
        worktree = Path(tmp).resolve()
        report = write_pr_triage_report.write_report(
            worktree=worktree,
            repo="jscraik/Agent-Skills",
            pr_number="196",
            expected_head="abc123",
            output_path=Path("artifacts/reviews/triage.md"),
            runner=make_runner(worktree=worktree),
            now=datetime(2026, 5, 24, tzinfo=UTC),
        )

        assert "status: blocked" in report
        assert "independent_review_missing" in report
        assert "WROTE: artifacts/reviews/triage.md" in report
        assert (worktree / "artifacts/reviews/triage.md").is_file()


def test_report_blocks_wrong_worktree_identity() -> None:
    with TemporaryDirectory() as tmp:
        worktree = Path(tmp).resolve()
        report = write_pr_triage_report.write_report(
            worktree=worktree,
            repo="jscraik/Agent-Skills",
            pr_number="196",
            expected_head="abc123",
            output_path=Path("artifacts/reviews/triage.md"),
            runner=make_runner(worktree=worktree, pwd="/Users/jamiecraik/dev/agent-skills"),
            now=datetime(2026, 5, 24, tzinfo=UTC),
        )

        assert "wrong_worktree" in report
        assert f"expected {worktree}" in report


def test_report_passes_when_worktree_head_checks_and_review_are_present() -> None:
    with TemporaryDirectory() as tmp:
        worktree = Path(tmp).resolve()
        report = write_pr_triage_report.write_report(
            worktree=worktree,
            repo="jscraik/Agent-Skills",
            pr_number="196",
            expected_head="abc123",
            output_path=Path("artifacts/reviews/triage.md"),
            runner=make_runner(
                worktree=worktree,
                reviews=[{"id": 1, "state": "COMMENTED"}],
            ),
            now=datetime(2026, 5, 24, tzinfo=UTC),
        )

        assert "status: pass" in report
        assert "can progress under governed workflow: yes" in report
        assert "- none" in report


def test_report_blocks_pr_head_mismatch() -> None:
    with TemporaryDirectory() as tmp:
        worktree = Path(tmp).resolve()
        report = write_pr_triage_report.write_report(
            worktree=worktree,
            repo="jscraik/Agent-Skills",
            pr_number="196",
            expected_head="abc123",
            output_path=Path("artifacts/reviews/triage.md"),
            runner=make_runner(worktree=worktree, pr_head="def456"),
            now=datetime(2026, 5, 24, tzinfo=UTC),
        )

        assert "pr_head_mismatch" in report


def test_report_rejects_absolute_output_path() -> None:
    with TemporaryDirectory() as tmp:
        worktree = Path(tmp).resolve()

        try:
            write_pr_triage_report.write_report(
                worktree=worktree,
                repo="jscraik/Agent-Skills",
                pr_number="196",
                expected_head="abc123",
                output_path=Path("/tmp/triage.md"),
                runner=make_runner(worktree=worktree),
                now=datetime(2026, 5, 24, tzinfo=UTC),
            )
        except ValueError as exc:
            assert "relative" in str(exc)
        else:
            raise AssertionError("absolute output path was accepted")


def test_report_rejects_output_path_escape() -> None:
    with TemporaryDirectory() as tmp:
        worktree = Path(tmp).resolve()

        try:
            write_pr_triage_report.write_report(
                worktree=worktree,
                repo="jscraik/Agent-Skills",
                pr_number="196",
                expected_head="abc123",
                output_path=Path("../triage.md"),
                runner=make_runner(worktree=worktree),
                now=datetime(2026, 5, 24, tzinfo=UTC),
            )
        except ValueError as exc:
            assert "inside" in str(exc)
        else:
            raise AssertionError("escaping output path was accepted")
