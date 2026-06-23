from __future__ import annotations

import argparse
from pathlib import Path

import ask.commands.skills as skills_commands
from ask.cli_errors import build_unknown_action_result
from ask.envelope import CallResult, ErrorObject
from ask.skills_sdk.adoption_decision import build_adoption_decision_receipt


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
    _add_inspect_parser(sdk_intake_subparsers, global_parser)
    _add_review_parser(sdk_intake_subparsers, global_parser)
    _add_adopt_parser(sdk_intake_subparsers, global_parser)


def _add_inspect_parser(
    subparsers: argparse._SubParsersAction,
    global_parser: argparse.ArgumentParser,
) -> None:
    inspect = subparsers.add_parser(
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


def _add_review_parser(
    subparsers: argparse._SubParsersAction,
    global_parser: argparse.ArgumentParser,
) -> None:
    review = subparsers.add_parser(
        "review",
        help="Build an external skill intake review receipt from quarantine and risk-mode receipts",
        parents=[global_parser],
    )
    review.add_argument("source", help="External skill directory to review")
    review.add_argument("--preview", action="store_true", help="Emit a non-mutating review receipt")
    review.add_argument(
        "--source-kind",
        choices=["directory"],
        default="directory",
        help="Input kind; review currently accepts directory input only",
    )


def _add_adopt_parser(
    subparsers: argparse._SubParsersAction,
    global_parser: argparse.ArgumentParser,
) -> None:
    adopt = subparsers.add_parser(
        "adopt",
        help="Preview an adoption decision from intake, review, package identity, and trust receipts",
        parents=[global_parser],
    )
    adopt.add_argument("source", help="External skill directory to assess for adoption")
    adopt.add_argument("--preview", action="store_true", help="Emit a non-mutating adoption decision receipt")
    adopt.add_argument(
        "--source-kind",
        choices=["directory"],
        default="directory",
        help="Input kind; adoption currently accepts directory input only",
    )
    adopt.add_argument("--trust-receipt", help="Repo-local trust decision receipt for the exact package digest")


def _validation_error(command: str, message: str, fix_suggestion: str) -> CallResult:
    result = CallResult(status="error")
    result.metadata["command"] = command
    result.errors.append(ErrorObject(code="ERR_VALIDATION", message=message, fix_suggestion=fix_suggestion))
    return result


def dispatch_sdk_intake(repo_root: Path, args: argparse.Namespace) -> CallResult:
    if args.intake_action == "inspect":
        return _dispatch_inspect(repo_root, args)
    if args.intake_action == "review":
        return _dispatch_review(repo_root, args)
    if args.intake_action == "adopt":
        return _dispatch_adopt(repo_root, args)
    return build_unknown_action_result("sdk intake", args.intake_action)


def _dispatch_inspect(repo_root: Path, args: argparse.Namespace) -> CallResult:
    if not args.preview:
        return _validation_error(
            "sdk intake inspect",
            "Skills SDK intake inspection is preview-only in this slice.",
            "ask sdk intake inspect <skill-dir> --preview --json --robot",
        )
    return skills_commands.skills_sdk_intake_inspect(repo_root, source=args.source, source_kind=args.source_kind)


def _dispatch_review(repo_root: Path, args: argparse.Namespace) -> CallResult:
    if not args.preview:
        return _validation_error(
            "sdk intake review",
            "Skills SDK intake review is preview-only in this slice.",
            "ask sdk intake review <skill-dir> --preview --json --robot",
        )
    return skills_commands.skills_sdk_intake_review(repo_root, source=args.source, source_kind=args.source_kind)


def _dispatch_adopt(repo_root: Path, args: argparse.Namespace) -> CallResult:
    if not args.preview:
        return _validation_error(
            "sdk intake adopt",
            "Skills SDK adoption decisions are preview-only in this slice.",
            "ask sdk intake adopt <skill-dir> --trust-receipt <trust.json> --preview --json --robot",
        )
    receipt = build_adoption_decision_receipt(
        repo_root,
        source=args.source.strip(),
        source_kind=args.source_kind,
        trust_receipt_path=args.trust_receipt,
    )
    result = CallResult()
    result.metadata["command"] = "sdk intake adopt --preview"
    result.data["skills_sdk_adoption_decision"] = {"status": receipt["status"], "receipt": receipt}
    if receipt["status"] == "blocked":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=receipt["agent_summary"],
                fix_suggestion="Inspect data.skills_sdk_adoption_decision.receipt.blockers before adoption.",
            )
        )
    return result
