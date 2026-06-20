from __future__ import annotations

import argparse
from pathlib import Path

import ask.commands.skills as skills_commands
from ask.envelope import CallResult, ErrorObject
from ask.cli_errors import build_unknown_action_result


def add_sdk_ci_parser(
    sdk_subparsers: argparse._SubParsersAction,
    global_parser: argparse.ArgumentParser,
) -> None:
    parser = sdk_subparsers.add_parser(
        "ci",
        help="Preview Skills SDK CI policy requirements",
        parents=[global_parser],
    )
    subparsers = parser.add_subparsers(dest="ci_action", required=True)
    policy = subparsers.add_parser(
        "policy",
        help="Preview required CI checks from an SDK risk tier",
        parents=[global_parser],
    )
    policy.add_argument(
        "--risk-tier",
        choices=["low", "medium", "high", "privileged", "published"],
        default="medium",
        help="Risk tier used to select required checks",
    )
    policy.add_argument("--preview", action="store_true", help="Emit a non-mutating CI policy receipt")


def dispatch_sdk_ci(repo_root: Path, args: argparse.Namespace) -> CallResult:
    if args.ci_action == "policy":
        if not args.preview:
            return _validation_error(
                "sdk ci policy",
                "Skills SDK CI policy is preview-only in PU-028 and requires --preview.",
                "ask sdk ci policy --risk-tier high --preview --json --robot",
            )
        return skills_commands.skills_sdk_ci_policy_preview(repo_root, risk_tier=args.risk_tier)
    return build_unknown_action_result("sdk ci", args.ci_action)


def _validation_error(command: str, message: str, fix_suggestion: str) -> CallResult:
    result = CallResult(status="error")
    result.metadata["command"] = command
    result.errors.append(
        ErrorObject(code="ERR_VALIDATION", message=message, fix_suggestion=fix_suggestion)
    )
    return result
