from __future__ import annotations

import argparse
from pathlib import Path

import ask.commands.skills as skills_commands
from ask.cli_errors import build_unknown_action_result
from ask.envelope import CallResult, ErrorObject


def add_sdk_intake_parser(
    sdk_subparsers: argparse._SubParsersAction,
    global_parser: argparse.ArgumentParser,
) -> None:
    sdk_intake_parser = sdk_subparsers.add_parser(
        "intake",
        help="Inspect external skill sources in a non-mutating quarantine lane",
        parents=[global_parser],
    )
    sdk_intake_subparsers = sdk_intake_parser.add_subparsers(dest="intake_action", required=True)
    inspect = sdk_intake_subparsers.add_parser(
        "inspect",
        help="Build an external skill intake receipt without execution or install",
        parents=[global_parser],
    )
    inspect.add_argument("source", help="External skill directory to inspect")
    inspect.add_argument("--preview", action="store_true", help="Emit a non-mutating intake receipt")
    inspect.add_argument(
        "--source-kind",
        choices=["directory", "archive"],
        default="directory",
        help="Input kind; archive unpacking is intentionally blocked in this slice",
    )


def _validation_error(command: str, message: str, fix_suggestion: str) -> CallResult:
    result = CallResult(status="error")
    result.metadata["command"] = command
    result.errors.append(ErrorObject(code="ERR_VALIDATION", message=message, fix_suggestion=fix_suggestion))
    return result


def dispatch_sdk_intake(repo_root: Path, args: argparse.Namespace) -> CallResult:
    if args.intake_action != "inspect":
        return build_unknown_action_result("sdk intake", args.intake_action)
    if not args.preview:
        return _validation_error(
            "sdk intake inspect",
            "Skills SDK intake inspection is preview-only in this slice.",
            "ask sdk intake inspect <skill-dir> --preview --json --robot",
        )
    return skills_commands.skills_sdk_intake_inspect(
        repo_root,
        source=args.source,
        source_kind=args.source_kind,
    )
