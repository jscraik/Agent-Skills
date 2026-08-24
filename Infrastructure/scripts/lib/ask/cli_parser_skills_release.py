"""Skill review, validation, installation, and authoring parser registration."""

from __future__ import annotations

import argparse


def _add_external_review_core(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("path", help="Path to the skill directory")
    parser.add_argument(
        "--audit-level",
        choices=["compat", "strict"],
        default="strict",
        help="Internal ask audit depth",
    )
    parser.add_argument(
        "--skip-plugin-eval", action="store_true", help="Skip plugin-eval comparison"
    )
    parser.add_argument(
        "--skip-tessl", action="store_true", help="Skip Tessl local lint and review"
    )
    parser.add_argument(
        "--with-tessl-review",
        action="store_true",
        help="Explicitly run Tessl content review after local lint; disabled by default",
    )
    parser.add_argument(
        "--skip-tessl-review",
        action="store_true",
        help="Compatibility flag; Tessl content review is disabled by default",
    )


def _add_external_review_output(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--include-snyk",
        action="store_true",
        help="Run optional Snyk CLI external security advisory",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=180,
        help="Timeout for each local reviewer command",
    )
    parser.add_argument("--report-path", help="Optional repo-relative JSON report path")
    parser.add_argument(
        "--dashboard",
        action="store_true",
        help="Render a local HTML dashboard beside the review report",
    )
    parser.add_argument(
        "--dashboard-path", help="Optional repo-relative HTML dashboard path"
    )


def _add_external_review(actions, global_parser: argparse.ArgumentParser) -> None:
    parser = actions.add_parser(
        "external-review",
        help="Run the local-only external-style skill review lane",
        parents=[global_parser],
    )
    _add_external_review_core(parser)
    _add_external_review_output(parser)


def _add_validation_commands(actions, global_parser: argparse.ArgumentParser) -> None:
    specs = (
        (
            "validate-skill-gate",
            "path",
            "Run the canonical skill gate",
            "Path to the skill directory",
        ),
        (
            "validate-boundaries",
            "handle",
            "Show canonical-versus-projection ownership for a skill target",
            "Skill target or source path to validate",
        ),
    )
    for action, positional, description, positional_help in specs:
        parser = actions.add_parser(action, help=description, parents=[global_parser])
        parser.add_argument(positional, help=positional_help)
    openai = actions.add_parser(
        "validate-openai-format",
        help="Run the canonical OpenAI skill format validator",
        parents=[global_parser],
    )
    openai.add_argument("path", help="Path to the skill directory")
    openai.add_argument(
        "--mode", choices=["warn", "strict"], default="strict", help="Validation mode"
    )


def _add_install(actions, global_parser: argparse.ArgumentParser) -> None:
    parser = actions.add_parser(
        "install", help="Install a skill from GitHub", parents=[global_parser]
    )
    parser.add_argument("url", help="GitHub URL of the skill")
    parser.add_argument(
        "--dest",
        default="Skills/github",
        help="Repo-relative canonical category directory under Skills/ (default: Skills/github)",
    )
    parser.add_argument(
        "--remediate", action="store_true", help="Scaffold missing contract/eval files"
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview installation")


def _add_fold(actions, global_parser: argparse.ArgumentParser) -> None:
    parser = actions.add_parser(
        "fold", help="Suggest folding source into target", parents=[global_parser]
    )
    parser.add_argument("source", help="Skill to be folded")
    parser.add_argument("target", help="Skill to merge into")
    parser.add_argument(
        "--sensitivity", type=float, default=0.2, help="Overlap threshold"
    )


def _add_init(actions, global_parser: argparse.ArgumentParser) -> None:
    parser = actions.add_parser(
        "init", help="Initialize a new skill scaffold", parents=[global_parser]
    )
    parser.add_argument("name", help="Name of the new skill")
    parser.add_argument("--category", required=True, help="Category directory")
    parser.add_argument(
        "--description", required=True, help="Short routing description"
    )


def add_release_commands(actions, global_parser: argparse.ArgumentParser) -> None:
    """Register skill review, validation, installation, and authoring commands."""
    _add_external_review(actions, global_parser)
    _add_validation_commands(actions, global_parser)
    _add_install(actions, global_parser)
    _add_fold(actions, global_parser)
    _add_init(actions, global_parser)
