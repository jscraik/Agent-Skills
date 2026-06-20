from __future__ import annotations

import argparse
from pathlib import Path

import ask.commands.skills as skills_commands
from ask.cli_errors import build_unknown_action_result, build_validation_error
from ask.envelope import CallResult


def add_sdk_security_parser(
    sdk_subparsers: argparse._SubParsersAction,
    global_parser: argparse.ArgumentParser,
) -> None:
    parser = sdk_subparsers.add_parser(
        "security",
        help="Preview local Skills SDK security adapter discovery",
        parents=[global_parser],
    )
    subparsers = parser.add_subparsers(dest="security_action", required=True)
    adapters = subparsers.add_parser(
        "adapters",
        help="Discover configured local security adapters without running scanners",
        parents=[global_parser],
    )
    adapters.add_argument("--preview", action="store_true", help="Emit a non-mutating adapter discovery receipt")


def dispatch_sdk_security(repo_root: Path, args: argparse.Namespace) -> CallResult:
    if args.security_action == "adapters":
        if not args.preview:
            return build_validation_error(
                "sdk security adapters",
                "Skills SDK security adapter discovery is preview-only in PU-031 and requires --preview.",
                "ask sdk security adapters --preview --json --robot",
            )
        return skills_commands.skills_sdk_security_adapters_preview(repo_root)
    return build_unknown_action_result("sdk security", args.security_action)
