"""Skill preview command parser registration."""

from __future__ import annotations

import argparse


def _add_list(actions, global_parser: argparse.ArgumentParser) -> None:
    parser = actions.add_parser(
        "list", help="List discovered skills", parents=[global_parser]
    )
    parser.add_argument("--category", help="Filter by category")
    parser.add_argument(
        "--advanced",
        action="store_true",
        help="Compatibility alias; full repo inventory is now the default",
    )
    parser.add_argument(
        "--visible-only",
        action="store_true",
        help="Show only the narrower picker/runtime-visible skill subset",
    )
    parser.add_argument(
        "--starter", action="store_true", help="Return starter-mode curated skills"
    )
    parser.add_argument(
        "--archetype",
        default="general",
        help="Starter archetype (general|delivery|review|docs)",
    )
    parser.add_argument(
        "--limit", type=int, default=12, help="Max starter skills to return"
    )


def _add_budget_and_capabilities(
    actions, global_parser: argparse.ArgumentParser
) -> None:
    budget = actions.add_parser(
        "budget", help="Verify default skill runtime budget", parents=[global_parser]
    )
    budget.add_argument(
        "--default-max", type=int, default=30, help="Maximum default-visible skills"
    )
    capabilities = actions.add_parser(
        "capabilities",
        aliases=["capability"],
        help="Report runtime proof-plane capability discovery",
        parents=[global_parser],
    )
    capabilities.add_argument(
        "--runtime-target",
        default="codex",
        help="Runtime target to describe: any, codex, or agents",
    )


def _add_basic_previews(actions, global_parser: argparse.ArgumentParser) -> None:
    actions.add_parser(
        "codex-preview",
        help="Show Codex preview command family and source-model basis",
        parents=[global_parser],
    )
    actions.add_parser(
        "load-preview",
        help="Preview Codex skill loader behavior",
        parents=[global_parser],
    )
    render = actions.add_parser(
        "render-preview",
        help="Preview Codex available-skills rendering",
        parents=[global_parser],
    )
    render.add_argument(
        "--context-window",
        type=int,
        help="Optional context window for Codex 2 percent metadata budget modeling",
    )


def _add_config(actions, global_parser: argparse.ArgumentParser) -> None:
    parser = actions.add_parser(
        "config",
        help="Explain Codex skill config rule behavior",
        parents=[global_parser],
    )
    config_actions = parser.add_subparsers(dest="config_action", required=True)
    config_actions.add_parser(
        "explain",
        help="Explain Codex skills.config rule semantics",
        parents=[global_parser],
    )


def _add_selection_previews(actions, global_parser: argparse.ArgumentParser) -> None:
    inject = actions.add_parser(
        "inject-preview",
        help="Preview Codex explicit skill mention selection",
        parents=[global_parser],
    )
    inject.add_argument("text", nargs="+", help="User text containing $skill mentions")
    implicit = actions.add_parser(
        "implicit-preview",
        help="Preview Codex implicit skill invocation attribution",
        parents=[global_parser],
    )
    implicit.add_argument(
        "--command", required=True, help="Shell command text to inspect"
    )
    implicit.add_argument(
        "--workdir", help="Working directory used to resolve relative command paths"
    )


def add_preview_commands(actions, global_parser: argparse.ArgumentParser) -> None:
    """Register listing and preview commands."""
    _add_list(actions, global_parser)
    _add_budget_and_capabilities(actions, global_parser)
    _add_basic_previews(actions, global_parser)
    _add_config(actions, global_parser)
    _add_selection_previews(actions, global_parser)
