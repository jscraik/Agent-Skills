#!/usr/bin/env python3
"""Write a deterministic report for subagent artifact handoff health."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass(frozen=True)
class ArtifactCheck:
    path: Path
    exists: bool
    bytes_count: int
    final_line: str
    status_line: str
    blockers: tuple[str, ...]


def indented(text: str) -> str:
    if not text:
        return "    (empty)"
    return "\n".join(f"    {line.rstrip()}" for line in text.rstrip().splitlines())


def resolve_inside_worktree(worktree: Path, relative_path: Path, *, option_name: str) -> Path:
    if relative_path.is_absolute():
        raise ValueError(f"{option_name} must be relative to --worktree")
    destination = (worktree / relative_path).resolve()
    try:
        destination.relative_to(worktree)
    except ValueError as exc:
        raise ValueError(f"{option_name} must stay inside --worktree") from exc
    return destination


def check_artifact(worktree: Path, expected_artifact: Path) -> ArtifactCheck:
    artifact_path = resolve_inside_worktree(
        worktree,
        expected_artifact,
        option_name="--expected-artifact",
    )
    blockers: list[str] = []
    final_line = ""
    status_line = ""
    bytes_count = 0

    if not artifact_path.exists():
        blockers.append(f"artifact_missing: {expected_artifact.as_posix()}")
        return ArtifactCheck(artifact_path, False, 0, "", "", tuple(blockers))

    if not artifact_path.is_file():
        blockers.append(f"artifact_not_file: {expected_artifact.as_posix()}")
        return ArtifactCheck(artifact_path, True, 0, "", "", tuple(blockers))

    content = artifact_path.read_text(encoding="utf-8")
    bytes_count = len(content.encode("utf-8"))
    if bytes_count == 0:
        blockers.append(f"artifact_empty: {expected_artifact.as_posix()}")
    lines = content.splitlines()
    if lines:
        final_line = lines[-1]
        status_line = next((line for line in lines if line.startswith("- status: ")), "")
    expected_wrote = f"WROTE: {expected_artifact.as_posix()}"
    if final_line != expected_wrote:
        blockers.append(
            f"artifact_wrote_mismatch: expected final line {expected_wrote!r}, got {final_line!r}"
        )

    return ArtifactCheck(
        artifact_path,
        True,
        bytes_count,
        final_line,
        status_line,
        tuple(blockers),
    )


def render_report(
    *,
    worktree: Path,
    expected_artifact: Path,
    output_path: Path,
    attempt_label: str,
    agent_name: str,
    check: ArtifactCheck,
    now: datetime,
) -> str:
    status = "blocked" if check.blockers else "pass"
    lines = [
        "# Subagent Handoff Health Report",
        "",
        "## Summary",
        "",
        f"- status: {status}",
        f"- attempt: {attempt_label}",
        f"- agent: {agent_name}",
        f"- checked at: {now.isoformat().replace('+00:00', 'Z')}",
        f"- worktree: {worktree}",
        f"- expected artifact: {expected_artifact.as_posix()}",
        "",
        "## Artifact Check",
        "",
        f"- exists: {check.exists}",
        f"- bytes: {check.bytes_count}",
        f"- source status line: {check.status_line or 'unknown'}",
        f"- final line: {check.final_line or 'missing'}",
        "",
        "## Blockers",
        "",
    ]
    if check.blockers:
        lines.extend(f"- {blocker}" for blocker in check.blockers)
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Source Artifact Preview",
            "",
        ]
    )
    if check.exists and check.path.is_file():
        lines.append(indented(check.path.read_text(encoding="utf-8")[:4000]))
    else:
        lines.append("    (source artifact unavailable)")

    lines.extend(
        [
            "",
            f"WROTE: {output_path.as_posix()}",
        ]
    )
    return "\n".join(lines) + "\n"


def write_report(
    *,
    worktree: Path,
    expected_artifact: Path,
    output_path: Path,
    attempt_label: str,
    agent_name: str,
    now: datetime | None = None,
) -> str:
    if not worktree.is_absolute():
        raise ValueError("--worktree must be an absolute path")
    expected_worktree = worktree.resolve()
    destination = resolve_inside_worktree(expected_worktree, output_path, option_name="--output")
    check = check_artifact(expected_worktree, expected_artifact)
    report = render_report(
        worktree=expected_worktree,
        expected_artifact=expected_artifact,
        output_path=output_path,
        attempt_label=attempt_label,
        agent_name=agent_name,
        check=check,
        now=now or datetime.now(UTC),
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(report, encoding="utf-8")
    return report


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worktree", required=True, help="Absolute path to the checkout to inspect.")
    parser.add_argument("--expected-artifact", required=True, help="Artifact path relative to --worktree.")
    parser.add_argument("--output", required=True, help="Report path relative to --worktree.")
    parser.add_argument("--attempt-label", required=True, help="Short label for the handoff attempt.")
    parser.add_argument("--agent-name", required=True, help="Subagent task name or id.")
    args = parser.parse_args(argv)
    if not Path(args.worktree).is_absolute():
        parser.error("--worktree must be an absolute path")
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    report = write_report(
        worktree=Path(args.worktree),
        expected_artifact=Path(args.expected_artifact),
        output_path=Path(args.output),
        attempt_label=args.attempt_label,
        agent_name=args.agent_name,
    )
    print(report.splitlines()[-1])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
