from __future__ import annotations

import argparse
from pathlib import Path

import ask.commands.skills as skills_commands
from ask.envelope import CallResult
from ask.cli_errors import build_unknown_action_result


def add_sdk_parser(
    subparsers: argparse._SubParsersAction,
    global_parser: argparse.ArgumentParser,
) -> None:
    sdk_parser = subparsers.add_parser("sdk", help="Skills SDK product facade", parents=[global_parser])
    sdk_subparsers = sdk_parser.add_subparsers(dest="action")
    sdk_check_parser = sdk_subparsers.add_parser(
        "check",
        help="Run the Skills SDK check facade for one skill handle or source path",
        parents=[global_parser],
    )
    sdk_check_parser.add_argument("target", help="Skill handle or repo-relative skill source path")
    sdk_check_parser.add_argument("--strict", action="store_true", help="Run strict audit instead of the default compat audit")
    sdk_check_parser.add_argument("--codex-parity", action="store_true", help="Require Codex-targeted runtime proof")


def dispatch_sdk(repo_root: Path, args: argparse.Namespace) -> CallResult:
    if args.action == "check":
        return skills_commands.skills_sdk_check(
            repo_root,
            target=args.target,
            strict=args.strict,
            codex_parity=args.codex_parity,
        )
    return build_unknown_action_result("sdk", args.action)

