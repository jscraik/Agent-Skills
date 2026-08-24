"""Evaluation command parser registration."""

from __future__ import annotations

import argparse


def _add_run_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("path", help="Path to the skill directory")
    parser.add_argument(
        "--mode", choices=["smoke", "release"], default="smoke", help="Evaluation mode"
    )
    parser.add_argument(
        "--runner",
        choices=["codex", "discovery-smoke"],
        default="codex",
        help=(
            "Evaluation runner. Use discovery-smoke for local-only contract smoke "
            "scorecards that do not call a model."
        ),
    )
    parser.add_argument("--model", help="Override the smoke eval Codex model")
    parser.add_argument(
        "--profile",
        help="Override the Codex config profile for codex-runner scenario proof",
    )
    parser.add_argument(
        "--case", action="append", default=[], help="Run matching eval case ids/names"
    )
    parser.add_argument(
        "--timeout-seconds", type=int, help="Override the internal eval runner timeout"
    )


def _add_run_tessl_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--skip-tessl",
        action="store_true",
        help=(
            "Explicitly skip the local Tessl lane that runs by default; only use for "
            "documented outage, policy block, or intentionally scoped debug run"
        ),
    )
    parser.add_argument(
        "--allow-tessl-project-save",
        action="store_true",
        help="Compatibility no-op for Tessl evals",
    )
    parser.add_argument(
        "--tessl-live-private",
        action="store_true",
        help="Use opt-in private Tessl tile eval staging",
    )
    parser.add_argument(
        "--tessl-workspace",
        help="Workspace namespace for Tessl project checks and private tile evals",
    )
    parser.add_argument(
        "--tessl-live-dry-run",
        action="store_true",
        help="Stage private Tessl tile eval inputs without invoking Tessl",
    )


def _add_run_output_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--handoff-readiness",
        help="Current repo-relative handoff readiness manifest under .harness/evidence/handoff",
    )
    parser.add_argument(
        "--no-dashboard",
        action="store_true",
        help=(
            "Do not render the optional local HTML dashboard; JSON remains the "
            "canonical eval result"
        ),
    )


def _add_closeout(actions, global_parser: argparse.ArgumentParser) -> None:
    parser = actions.add_parser(
        "closeout",
        help="Inspect eval workflow closeout receipts",
        parents=[global_parser],
    )
    closeout_actions = parser.add_subparsers(dest="closeout_action", required=True)
    doctor = closeout_actions.add_parser(
        "doctor",
        help="Diagnose a workflow-closeout.json receipt or report directory",
        parents=[global_parser],
    )
    doctor.add_argument(
        "path", help="Path to workflow-closeout.json or its report directory"
    )


def _add_macro_report(actions, global_parser: argparse.ArgumentParser) -> None:
    parser = actions.add_parser(
        "macro-report",
        help="Export deterministic macro-eval events from saved skill eval summaries",
        parents=[global_parser],
    )
    parser.add_argument(
        "--output-dir", default=None, help="Directory for macro-eval artifacts"
    )
    parser.add_argument(
        "--summaries-glob",
        default=None,
        help="Repo-relative glob for summary.json files",
    )


def _add_tessl_preparation(actions, global_parser: argparse.ArgumentParser) -> None:
    parser = actions.add_parser(
        "prepare-tessl-scenarios",
        help=(
            "Stage a skill and optionally install Tessl's scenario-generation tile "
            "in temp space"
        ),
        parents=[global_parser],
    )
    parser.add_argument("path", help="Path to the skill directory")
    parser.add_argument(
        "--tessl-workspace",
        required=True,
        help="Workspace namespace for the staged private tile",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--execute",
        action="store_true",
        help="Explicitly install Tessl's scenario-generation tile after staging",
    )
    mode.add_argument(
        "--dry-run",
        action="store_true",
        help="Compatibility flag; staging-only is the default and does not invoke Tessl install",
    )


def add_evaluation_commands(subparsers, global_parser: argparse.ArgumentParser) -> None:
    """Register evaluation and benchmarking commands."""
    evals_parser = subparsers.add_parser(
        "evals", help="Evaluation and Benchmarking", parents=[global_parser]
    )
    actions = evals_parser.add_subparsers(dest="action")
    run_parser = actions.add_parser(
        "run", help="Run evaluation cases for a skill", parents=[global_parser]
    )
    _add_run_arguments(run_parser)
    _add_run_tessl_arguments(run_parser)
    _add_run_output_arguments(run_parser)
    actions.add_parser(
        "benchmark", help="Run full repository benchmark suite", parents=[global_parser]
    )
    actions.add_parser(
        "dashboard", help="Generate evaluation dashboard", parents=[global_parser]
    )
    _add_closeout(actions, global_parser)
    _add_macro_report(actions, global_parser)
    _add_tessl_preparation(actions, global_parser)
