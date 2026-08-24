"""Skill contract and routing parser registration."""

from __future__ import annotations

import argparse

from ask.commands.runtime import add_runtime_parser
from ask.commands.sdk import add_sdk_parser


def _add_conformance(actions, global_parser: argparse.ArgumentParser) -> None:
    parser = actions.add_parser(
        "conformance",
        help="Run skill conformance suites with replayable evidence",
        parents=[global_parser],
    )
    conformance = parser.add_subparsers(dest="conformance_action")
    run = conformance.add_parser(
        "run", help="Run a deterministic conformance suite", parents=[global_parser]
    )
    run.add_argument(
        "--suite",
        default="codex-parity",
        choices=["codex-parity"],
        help="Conformance suite to run",
    )
    run.add_argument(
        "--evidence-dir",
        required=True,
        help="Directory where JSON evidence files will be written",
    )


def _add_metadata(actions, global_parser: argparse.ArgumentParser) -> None:
    profiles = actions.add_parser(
        "profiles",
        help="Show skill operation profiles and readiness contracts",
        parents=[global_parser],
    )
    profiles.add_argument("profile", nargs="?", help="Optional profile name")
    events = actions.add_parser(
        "events", help="Show skill lifecycle event contracts", parents=[global_parser]
    )
    events.add_argument("event_type", nargs="?", help="Optional lifecycle event type")


def _add_memory(actions, global_parser: argparse.ArgumentParser) -> None:
    parser = actions.add_parser(
        "memory",
        help="List, read, or search durable skill memory",
        parents=[global_parser],
    )
    parser.add_argument(
        "mode", choices=["list", "read", "search"], help="Memory provider mode"
    )
    parser.add_argument(
        "query", nargs="?", help="Entry id/path for read, or search query"
    )
    parser.add_argument("--source", dest="source_id", help="Filter by memory source id")
    parser.add_argument(
        "--limit", type=int, default=8, help="Maximum entries to return"
    )


def _add_reviewers(subparsers, global_parser: argparse.ArgumentParser) -> None:
    parser = subparsers.add_parser(
        "reviewers", help="Reviewer/subagent handle management", parents=[global_parser]
    )
    actions = parser.add_subparsers(dest="action")
    resolve = actions.add_parser(
        "resolve", help="Resolve a reviewer/subagent handle", parents=[global_parser]
    )
    resolve.add_argument(
        "handle", help="Reviewer handle to resolve, with or without leading @"
    )


def add_contract_commands(
    subparsers, actions, global_parser: argparse.ArgumentParser
) -> None:
    """Register skill contracts plus SDK, reviewer, and runtime topics."""
    _add_conformance(actions, global_parser)
    _add_metadata(actions, global_parser)
    _add_memory(actions, global_parser)
    add_sdk_parser(subparsers, global_parser)
    _add_reviewers(subparsers, global_parser)
    add_runtime_parser(subparsers, global_parser)


def _add_route_command(
    actions,
    global_parser: argparse.ArgumentParser,
    action: str,
    positional: str,
    description: str,
    positional_help: str,
) -> None:
    parser = actions.add_parser(action, help=description, parents=[global_parser])
    parser.add_argument(positional, nargs="+", help=positional_help)
    parser.add_argument(
        "--top-k", type=int, default=3, help="Max ranked candidates to consider"
    )
    parser.add_argument(
        "--considered-limit",
        type=int,
        default=20,
        help="Max eligible candidates considered before truncation",
    )


def _add_routing(actions, global_parser: argparse.ArgumentParser) -> None:
    specs = (
        (
            "route",
            "request",
            "Route a request to matching skills",
            "Request text to route",
        ),
        (
            "goal",
            "intent",
            "Resolve intent into one recommended skill",
            "Intent text to route",
        ),
        (
            "improve",
            "goal",
            "Recommend one capability for an agent improvement goal",
            "Improvement goal text to route",
        ),
    )
    for action, positional, description, positional_help in specs:
        _add_route_command(
            actions, global_parser, action, positional, description, positional_help
        )


def _add_starter(actions, global_parser: argparse.ArgumentParser) -> None:
    parser = actions.add_parser(
        "starter", help="List starter-mode curated skills", parents=[global_parser]
    )
    parser.add_argument(
        "--archetype",
        default="general",
        help="Starter archetype (general|delivery|review|docs)",
    )
    parser.add_argument(
        "--limit", type=int, default=12, help="Max starter skills to return"
    )


def _add_sync(actions, global_parser: argparse.ArgumentParser) -> None:
    parser = actions.add_parser(
        "sync", help="Synchronize skill symlinks", parents=[global_parser]
    )
    parser.add_argument(
        "--scope",
        choices=["user", "workspace"],
        default="workspace",
        help="Tier to sync",
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview changes")
    parser.add_argument("--projection", help="Runtime projection mode: flat")
    parser.add_argument(
        "--plugin-cache-refresh",
        choices=["auto", "skip", "only"],
        default="auto",
        help="Plugin runtime cache refresh mode",
    )
    parser.add_argument(
        "--user-sync-mode",
        choices=["full", "links-only"],
        default=None,
        help="For user scope, sync runtime links only; use full to refresh plugin mirrors",
    )


def _add_audit(actions, global_parser: argparse.ArgumentParser) -> None:
    parser = actions.add_parser(
        "audit", help="Run audits on a skill", parents=[global_parser]
    )
    parser.add_argument("path", help="Path to the skill directory")
    parser.add_argument(
        "--level", choices=["compat", "strict"], default="compat", help="Audit depth"
    )
    parser.add_argument(
        "--source-only",
        action="store_true",
        help="Validate canonical source without requiring a generated runtime projection",
    )


def add_routing_commands(actions, global_parser: argparse.ArgumentParser) -> None:
    """Register skill routing, sync, and audit commands."""
    _add_routing(actions, global_parser)
    _add_starter(actions, global_parser)
    _add_sync(actions, global_parser)
    _add_audit(actions, global_parser)
