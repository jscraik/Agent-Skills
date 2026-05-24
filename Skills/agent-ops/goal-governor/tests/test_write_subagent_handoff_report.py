#!/usr/bin/env python3
"""Focused tests for the Goal Governor subagent handoff artifact writer."""

from __future__ import annotations

import importlib.util
import sys
from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "write_subagent_handoff_report.py"
SPEC = importlib.util.spec_from_file_location("write_subagent_handoff_report", SCRIPT_PATH)
assert SPEC is not None
assert SPEC.loader is not None
write_subagent_handoff_report = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = write_subagent_handoff_report
SPEC.loader.exec_module(write_subagent_handoff_report)


def write_expected_artifact(worktree: Path, relative_path: Path, body: str) -> None:
    destination = worktree / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(body, encoding="utf-8")


def test_report_passes_when_artifact_exists_and_wrote_line_matches() -> None:
    with TemporaryDirectory() as tmp:
        worktree = Path(tmp).resolve()
        artifact = Path("artifacts/reviews/subagent.md")
        output = Path("artifacts/reviews/handoff-health.md")
        write_expected_artifact(
            worktree,
            artifact,
            "\n".join(
                [
                    "# Subagent Artifact",
                    "",
                    "- status: pass",
                    "- evidence: local artifact was written",
                    "",
                    f"WROTE: {artifact.as_posix()}",
                    "",
                ]
            ),
        )

        report = write_subagent_handoff_report.write_report(
            worktree=worktree,
            expected_artifact=artifact,
            output_path=output,
            attempt_label="local-probe",
            agent_name="/root/probe",
            now=datetime(2026, 5, 24, tzinfo=UTC),
        )

        assert "- status: pass" in report
        assert "- source status line: - status: pass" in report
        assert "- none" in report
        assert f"WROTE: {output.as_posix()}" in report
        assert (worktree / output).is_file()


def test_report_blocks_when_expected_artifact_is_missing() -> None:
    with TemporaryDirectory() as tmp:
        worktree = Path(tmp).resolve()
        artifact = Path("artifacts/reviews/missing.md")
        report = write_subagent_handoff_report.write_report(
            worktree=worktree,
            expected_artifact=artifact,
            output_path=Path("artifacts/reviews/handoff-health.md"),
            attempt_label="local-probe",
            agent_name="/root/probe",
            now=datetime(2026, 5, 24, tzinfo=UTC),
        )

        assert "- status: blocked" in report
        assert f"artifact_missing: {artifact.as_posix()}" in report
        assert "- source status line: unknown" in report
        assert "source artifact unavailable" in report


def test_report_blocks_when_expected_artifact_is_empty() -> None:
    with TemporaryDirectory() as tmp:
        worktree = Path(tmp).resolve()
        artifact = Path("artifacts/reviews/empty.md")
        write_expected_artifact(worktree, artifact, "")

        report = write_subagent_handoff_report.write_report(
            worktree=worktree,
            expected_artifact=artifact,
            output_path=Path("artifacts/reviews/handoff-health.md"),
            attempt_label="local-probe",
            agent_name="/root/probe",
            now=datetime(2026, 5, 24, tzinfo=UTC),
        )

        assert "- status: blocked" in report
        assert f"artifact_empty: {artifact.as_posix()}" in report
        assert "artifact_wrote_mismatch" in report


def test_report_blocks_when_wrote_line_does_not_match_expected_artifact() -> None:
    with TemporaryDirectory() as tmp:
        worktree = Path(tmp).resolve()
        artifact = Path("artifacts/reviews/subagent.md")
        write_expected_artifact(
            worktree,
            artifact,
            "\n".join(
                [
                    "# Subagent Artifact",
                    "",
                    "- status: pass",
                    "",
                    "WROTE: artifacts/reviews/other.md",
                    "",
                ]
            ),
        )

        report = write_subagent_handoff_report.write_report(
            worktree=worktree,
            expected_artifact=artifact,
            output_path=Path("artifacts/reviews/handoff-health.md"),
            attempt_label="local-probe",
            agent_name="/root/probe",
            now=datetime(2026, 5, 24, tzinfo=UTC),
        )

        assert "- status: blocked" in report
        assert "artifact_wrote_mismatch" in report
        assert "WROTE: artifacts/reviews/other.md" in report


def test_worktree_must_be_absolute() -> None:
    try:
        write_subagent_handoff_report.write_report(
            worktree=Path("relative-worktree"),
            expected_artifact=Path("artifacts/reviews/subagent.md"),
            output_path=Path("artifacts/reviews/handoff-health.md"),
            attempt_label="local-probe",
            agent_name="/root/probe",
            now=datetime(2026, 5, 24, tzinfo=UTC),
        )
    except ValueError as exc:
        assert "--worktree must be an absolute path" in str(exc)
    else:
        raise AssertionError("relative worktree was accepted")


def test_expected_artifact_must_stay_inside_worktree() -> None:
    with TemporaryDirectory() as tmp:
        worktree = Path(tmp).resolve()
        try:
            write_subagent_handoff_report.write_report(
                worktree=worktree,
                expected_artifact=Path("../escape.md"),
                output_path=Path("artifacts/reviews/handoff-health.md"),
                attempt_label="local-probe",
                agent_name="/root/probe",
                now=datetime(2026, 5, 24, tzinfo=UTC),
            )
        except ValueError as exc:
            assert "--expected-artifact must stay inside --worktree" in str(exc)
        else:
            raise AssertionError("escaping expected artifact path was accepted")


def test_output_must_stay_inside_worktree() -> None:
    with TemporaryDirectory() as tmp:
        worktree = Path(tmp).resolve()
        try:
            write_subagent_handoff_report.write_report(
                worktree=worktree,
                expected_artifact=Path("artifacts/reviews/subagent.md"),
                output_path=Path("../handoff-health.md"),
                attempt_label="local-probe",
                agent_name="/root/probe",
                now=datetime(2026, 5, 24, tzinfo=UTC),
            )
        except ValueError as exc:
            assert "--output must stay inside --worktree" in str(exc)
        else:
            raise AssertionError("escaping output path was accepted")
