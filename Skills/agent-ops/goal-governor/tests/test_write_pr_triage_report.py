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
    reported_pwd: str | None = None,
    checks_exit: int = 0,
    reviews: list[object] | None = None,
    comments: list[object] | None = None,
    comments_exit: int = 0,
    pr_head: str | None = None,
    pr_author: str = "jamiecraik",
) -> write_pr_triage_report.Runner:
    actual_pwd = str(worktree if reported_pwd is None else reported_pwd)
    actual_pr_head = pr_head or expected_head
    actual_reviews = [] if reviews is None else reviews
    actual_comments = [] if comments is None else comments

    def runner(command: tuple[str, ...], cwd: Path) -> write_pr_triage_report.CommandResult:
        assert cwd == worktree
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
                        "author": {"login": pr_author},
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
            return write_pr_triage_report.CommandResult(command, comments_exit, json.dumps(actual_comments), "")
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
            runner=make_runner(
                worktree=worktree,
                reported_pwd="/tmp/other-worktree/agent-skills",
            ),
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
                reviews=[
                    {
                        "id": 1,
                        "state": "COMMENTED",
                        "user": {"login": "coderabbitai[bot]"},
                    }
                ],
            ),
            now=datetime(2026, 5, 24, tzinfo=UTC),
        )

        assert "status: pass" in report
        assert "can progress under governed workflow: yes" in report
        assert "- none" in report
        assert "independent GitHub reviews: 1" in report


def test_report_blocks_when_only_self_review_is_present() -> None:
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
                reviews=[
                    {
                        "id": 1,
                        "state": "COMMENTED",
                        "user": {"login": "jamiecraik"},
                    }
                ],
            ),
            now=datetime(2026, 5, 24, tzinfo=UTC),
        )

        assert "status: blocked" in report
        assert "independent_review_missing" in report
        assert "independent GitHub reviews: 0" in report


def test_report_blocks_when_inline_review_comments_need_triage() -> None:
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
                reviews=[
                    {
                        "id": 1,
                        "state": "COMMENTED",
                        "user": {"login": "coderabbitai[bot]"},
                    }
                ],
                comments=[
                    {
                        "id": 12,
                        "path": "Skills/agent-ops/goal-governor/scripts/write_pr_triage_report.py",
                    }
                ],
            ),
            now=datetime(2026, 5, 24, tzinfo=UTC),
        )

        assert "status: blocked" in report
        assert "review_comments_present: 1 inline review comments" in report
        assert "inline review comments: 1" in report
        assert "active inline review comments: 1" in report


def test_report_passes_when_inline_review_comments_are_addressed_for_head() -> None:
    with TemporaryDirectory() as tmp:
        worktree = Path(tmp).resolve()
        report = write_pr_triage_report.write_report(
            worktree=worktree,
            repo="jscraik/Agent-Skills",
            pr_number="196",
            expected_head="9cf424ec4d9b99cf8d5657c9485531f5f0dd198f",
            output_path=Path("artifacts/reviews/triage.md"),
            runner=make_runner(
                worktree=worktree,
                expected_head="9cf424ec4d9b99cf8d5657c9485531f5f0dd198f",
                reviews=[
                    {
                        "id": 1,
                        "state": "COMMENTED",
                        "user": {"login": "coderabbitai[bot]"},
                    }
                ],
                comments=[
                    {
                        "id": 12,
                        "path": "Skills/agent-ops/goal-governor/scripts/write_pr_triage_report.py",
                        "body": "Addressed in commit 9cf424e",
                    }
                ],
            ),
            now=datetime(2026, 5, 24, tzinfo=UTC),
        )

        assert "status: pass" in report
        assert "inline review comments: 1" in report
        assert "addressed inline review comments: 1" in report
        assert "active inline review comments: 0" in report
        assert "review_comments_present" not in report


def test_report_passes_when_inline_review_comments_are_stale_for_old_head() -> None:
    with TemporaryDirectory() as tmp:
        worktree = Path(tmp).resolve()
        report = write_pr_triage_report.write_report(
            worktree=worktree,
            repo="jscraik/Agent-Skills",
            pr_number="196",
            expected_head="9cf424ec4d9b99cf8d5657c9485531f5f0dd198f",
            output_path=Path("artifacts/reviews/triage.md"),
            runner=make_runner(
                worktree=worktree,
                expected_head="9cf424ec4d9b99cf8d5657c9485531f5f0dd198f",
                reviews=[
                    {
                        "id": 1,
                        "state": "COMMENTED",
                        "user": {"login": "coderabbitai[bot]"},
                    }
                ],
                comments=[
                    {
                        "id": 12,
                        "path": "Docs/goals/jsc-351-agent-skills-codex-abi-conformance/receipts.jsonl",
                        "line": None,
                        "commit_id": "a032eda8724d6ac1d47c18a7f75ea519746aab96",
                        "body": "Normalize receipt chronology.",
                    }
                ],
            ),
            now=datetime(2026, 5, 24, tzinfo=UTC),
        )

        assert "status: pass" in report
        assert "stale inline review comments: 1" in report
        assert "active inline review comments: 0" in report
        assert "review_comments_present" not in report


def test_report_blocks_when_comments_are_unreadable() -> None:
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
                reviews=[
                    {
                        "id": 1,
                        "state": "COMMENTED",
                        "user": {"login": "coderabbitai[bot]"},
                    }
                ],
                comments_exit=1,
            ),
            now=datetime(2026, 5, 24, tzinfo=UTC),
        )

        assert "status: blocked" in report
        assert "comments_unreadable" in report
        assert "active inline review comments: unknown" in report


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
                output_path=worktree / "triage.md",
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


def test_parse_args_rejects_relative_worktree() -> None:
    try:
        write_pr_triage_report.parse_args(
            [
                "--worktree",
                "relative/worktree",
                "--repo",
                "jscraik/Agent-Skills",
                "--pr",
                "196",
                "--head",
                "abc123",
                "--output",
                "artifacts/reviews/triage.md",
            ]
        )
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError("relative worktree was accepted")
