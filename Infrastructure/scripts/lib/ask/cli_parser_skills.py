"""Skill command parser registration."""

from __future__ import annotations

import argparse

from ask.cli_args import FacadeActionChoices, facade_help_action
from ask.cli_parser_skills_contract import add_contract_commands, add_routing_commands
from ask.cli_parser_skills_identity import add_identity_commands
from ask.cli_parser_skills_preview import add_preview_commands
from ask.cli_parser_skills_release import add_release_commands
from ask.command_metadata import SKILLS_AUTHOR_FACING_ACTIONS


def add_skills_commands(subparsers, global_parser: argparse.ArgumentParser) -> None:
    """Register the skills command family and its related top-level topics."""
    skills_parser = subparsers.add_parser(
        "skills", help="Skill management", parents=[global_parser]
    )
    actions = skills_parser.add_subparsers(
        dest="action", action=facade_help_action(SKILLS_AUTHOR_FACING_ACTIONS)
    )
    actions.metavar = "{" + ",".join(SKILLS_AUTHOR_FACING_ACTIONS) + "}"
    add_preview_commands(actions, global_parser)
    add_identity_commands(actions, global_parser)
    add_contract_commands(subparsers, actions, global_parser)
    add_routing_commands(actions, global_parser)
    add_release_commands(actions, global_parser)
    actions.choices = FacadeActionChoices(
        actions._name_parser_map, SKILLS_AUTHOR_FACING_ACTIONS
    )
