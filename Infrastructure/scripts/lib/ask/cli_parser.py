"""Build the public Ask parser separately from CLI execution."""

from __future__ import annotations

import argparse

from ask.cli_args import build_global_parser
from ask.cli_parser_evals import add_evaluation_commands
from ask.cli_parser_misc import (
    add_graph_commands,
    add_mcp_and_memory_commands,
    add_wiki_commands,
)
from ask.cli_parser_plugins import add_plugin_commands
from ask.cli_parser_repo import add_repo_commands
from ask.cli_parser_skills import add_skills_commands
from ask.commands.workouts import add_workouts_parser


def build_parser() -> argparse.ArgumentParser:
    """Build the public command tree."""
    global_parser = build_global_parser()
    parser = argparse.ArgumentParser(
        prog="ask",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(
            "Agent Skills Kit CLI. Use --robot / --agent-mode / -r for "
            "AI-agent workflows."
        ),
        parents=[global_parser],
    )
    subparsers = parser.add_subparsers(
        dest="topic", help="Command topics (use --robot for fuzzy matching)"
    )
    add_repo_commands(subparsers, global_parser)
    add_skills_commands(subparsers, global_parser)
    add_plugin_commands(subparsers, global_parser)
    add_evaluation_commands(subparsers, global_parser)
    add_workouts_parser(subparsers, global_parser)
    add_graph_commands(subparsers, global_parser)
    add_mcp_and_memory_commands(subparsers, global_parser)
    add_wiki_commands(subparsers, global_parser)
    return parser
