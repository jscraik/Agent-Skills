from __future__ import annotations

import argparse
from pathlib import Path

import ask.commands.skills as skills_commands
from ask.envelope import CallResult, ErrorObject
from ask.cli_errors import build_unknown_action_result


def add_sdk_explorer_parser(
    sdk_subparsers: argparse._SubParsersAction,
    global_parser: argparse.ArgumentParser,
) -> None:
    parser = sdk_subparsers.add_parser(
        "explorer",
        help="Preview static Skills SDK explorer indexes",
        parents=[global_parser],
    )
    subparsers = parser.add_subparsers(dest="explorer_action", required=True)
    static = subparsers.add_parser(
        "static",
        help="Build a JSON-only local explorer index preview",
        parents=[global_parser],
    )
    static.add_argument("--preview", action="store_true", help="Emit a non-mutating explorer receipt")


def dispatch_sdk_explorer(repo_root: Path, args: argparse.Namespace) -> CallResult:
    if args.explorer_action == "static":
        if not args.preview:
            return _validation_error(
                "sdk explorer static",
                "Skills SDK static explorer is preview-only in PU-029 and requires --preview.",
                "ask sdk explorer static --preview --json --robot",
            )
        return skills_commands.skills_sdk_static_explorer_preview(repo_root)
    return build_unknown_action_result("sdk explorer", args.explorer_action)


def _validation_error(command: str, message: str, fix_suggestion: str) -> CallResult:
    result = CallResult(status="error")
    result.metadata["command"] = command
    result.errors.append(
        ErrorObject(code="ERR_VALIDATION", message=message, fix_suggestion=fix_suggestion)
    )
    return result
