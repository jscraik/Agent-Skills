"""Repository command parser registration."""

from __future__ import annotations

import argparse

from ask.commands.repo_cli import add_repo_auxiliary_parsers


def _add_status(actions, global_parser: argparse.ArgumentParser) -> None:
    parser = actions.add_parser(
        "status", help="Show repository status", parents=[global_parser]
    )
    parser.add_argument("--verbose", action="store_true", help="Include more details")
    parser.add_argument(
        "--baseline-path",
        help="Include Git shape-baseline data for a repo-relative path",
    )


def _add_validate(actions, global_parser: argparse.ArgumentParser) -> None:
    parser = actions.add_parser(
        "validate", help="Run all repository validations", parents=[global_parser]
    )
    parser.add_argument(
        "--ephemeral",
        action="store_true",
        help="Do not mutate repo validation artifacts",
    )
    parser.add_argument(
        "--fail-fast", action="store_true", help="Stop after the first required failure"
    )
    parser.add_argument(
        "--scope",
        default="all",
        choices=[
            "all",
            "lint",
            "typecheck",
            "test",
            "audit",
            "check",
            "skills-sdk",
            "consistency-advisory",
            "consistency-health",
        ],
        help="Run a named validation subset for CI check-name parity",
    )
    parser.add_argument(
        "--changed-files",
        nargs="+",
        default=[],
        help="Scope validation to these changed files",
    )


def _add_yaml_inspect(actions, global_parser: argparse.ArgumentParser) -> None:
    parser = actions.add_parser(
        "yaml-inspect",
        help="Parse a repo YAML file with the managed PyYAML interpreter",
        parents=[global_parser],
    )
    parser.add_argument("path", help="Repo-relative YAML file path")
    parser.add_argument(
        "--query", help="Optional dotted query path, including numeric list indexes"
    )


def _add_stability(actions, global_parser: argparse.ArgumentParser) -> None:
    parser = actions.add_parser(
        "check-stability",
        help="Check stable skills not deleted without deprecation",
        parents=[global_parser],
    )
    parser.add_argument(
        "--changed-files", nargs="+", default=[], help="Changed SKILL.md files to check"
    )


def _add_closeout(actions, global_parser: argparse.ArgumentParser) -> None:
    parser = actions.add_parser(
        "closeout", help="Report completion readiness", parents=[global_parser]
    )
    parser.add_argument(
        "--changed",
        action="store_true",
        help="Infer staged, unstaged, and untracked changed files for commit readiness",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat diagnostic debt as closeout blocking",
    )


def add_repo_commands(subparsers, global_parser: argparse.ArgumentParser) -> None:
    """Register repository-management commands."""
    repo_parser = subparsers.add_parser(
        "repo", help="Repository management", parents=[global_parser]
    )
    actions = repo_parser.add_subparsers(dest="action")
    _add_status(actions, global_parser)
    _add_validate(actions, global_parser)
    _add_yaml_inspect(actions, global_parser)
    _add_stability(actions, global_parser)
    actions.add_parser(
        "doctor",
        help="Agent-facing repository health entrypoint",
        description="Agent-facing repository health entrypoint",
        parents=[global_parser],
    )
    _add_closeout(actions, global_parser)
    add_repo_auxiliary_parsers(actions, global_parser)
