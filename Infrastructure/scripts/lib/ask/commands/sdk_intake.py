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
    """
    Register the 'intake' subcommand with 'inspect' and 'review' sub-subcommands.
    
    Parameters:
    	sdk_subparsers (argparse._SubParsersAction): The subparsers action for the SDK command.
    	global_parser (argparse.ArgumentParser): The parent parser to use for all subcommands.
    """
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
    review = sdk_intake_subparsers.add_parser(
        "review",
        help="Build an external skill intake review receipt from quarantine and risk-mode receipts",
        parents=[global_parser],
    )
    review.add_argument("source", help="External skill directory to review")
    review.add_argument("--preview", action="store_true", help="Emit a non-mutating review receipt")
    review.add_argument(
        "--source-kind",
        choices=["directory", "archive"],
        default="directory",
        help="Input kind; archive unpacking is intentionally blocked in this slice",
    )


def _validation_error(command: str, message: str, fix_suggestion: str) -> CallResult:
    """
    Build a standardized validation error result.
    
    Parameters:
    	command (str): The command associated with the error.
    	message (str): The error message.
    	fix_suggestion (str): A suggested fix for the error.
    
    Returns:
    	CallResult: An error CallResult with validation error code.
    """
    result = CallResult(status="error")
    result.metadata["command"] = command
    result.errors.append(ErrorObject(code="ERR_VALIDATION", message=message, fix_suggestion=fix_suggestion))
    return result


def dispatch_sdk_intake(repo_root: Path, args: argparse.Namespace) -> CallResult:
    """
    Route the `intake` subcommand to its handler, enforcing preview-only mode.
    
    Dispatches `inspect` or `review` based on the parsed action. Returns a validation 
    error if `--preview` is not set, as both operations are preview-only. Otherwise 
    invokes the corresponding handler with the source and source kind arguments.
    
    Parameters:
        repo_root (Path): The repository root directory.
        args (argparse.Namespace): Parsed arguments containing intake_action, preview, source, and source_kind.
    
    Returns:
        CallResult: A validation error if preview is not set; otherwise, the outcome of the intake operation.
    """
    if args.intake_action == "inspect":
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
    if args.intake_action == "review":
        if not args.preview:
            return _validation_error(
                "sdk intake review",
                "Skills SDK intake review is preview-only in this slice.",
                "ask sdk intake review <skill-dir> --preview --json --robot",
            )
        return skills_commands.skills_sdk_intake_review(
            repo_root,
            source=args.source,
            source_kind=args.source_kind,
        )
    return build_unknown_action_result("sdk intake", args.intake_action)
