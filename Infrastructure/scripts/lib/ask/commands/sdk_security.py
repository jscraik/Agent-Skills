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
    """
    Register CLI subcommands for SDK security adapter discovery, package signatures,
    and risk-mode classification.
    """
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
    package_signature = subparsers.add_parser(
        "package-signature",
        help="Inspect a skill package security signature without executing source content",
        parents=[global_parser],
    )
    package_signature.add_argument("target", help="Skill handle or repo-relative skill source path")
    package_signature.add_argument("--preview", action="store_true", help="Emit a non-mutating package security signature receipt")
    risk_modes = subparsers.add_parser(
        "risk-modes",
        help="Classify Tal/Podjarny skill risk modes without executing source content",
        parents=[global_parser],
    )
    risk_modes.add_argument("target", help="Skill handle or repo-relative skill source path")
    risk_modes.add_argument("--preview", action="store_true", help="Emit a non-mutating risk-mode taxonomy receipt")
    run_lane = subparsers.add_parser(
        "run-lane",
        help="Run the deterministic SDK security lane without executing skill content",
        parents=[global_parser],
    )
    run_lane.add_argument("target", help="Skill handle or repo-relative skill source path")
    run_lane.add_argument("--preview", action="store_true", help="Emit a non-mutating security lane receipt")
    run_lane.add_argument("--profile", help="Codex profile expected to review the emitted security lane receipt")
    run_lane.add_argument(
        "--require-review",
        action="store_true",
        help="Block unless a profile review receipt is attached by an external evidence lane",
    )


def dispatch_sdk_security(repo_root: Path, args: argparse.Namespace) -> CallResult:
    """
    Route SDK security subcommands to their handlers with preview-mode enforcement.
    
    Parameters:
        repo_root (Path): The root directory of the repository
        args (argparse.Namespace): Parsed command-line arguments containing security_action and preview flag
    
    Returns:
        CallResult: The result of the dispatched command or a validation/error response
    """
    if args.security_action == "adapters":
        if not args.preview:
            return build_validation_error(
                "sdk security adapters",
                "Skills SDK security adapter discovery is preview-only in PU-031 and requires --preview.",
                "ask sdk security adapters --preview --json --robot",
            )
        return skills_commands.skills_sdk_security_adapters_preview(repo_root)
    if args.security_action == "package-signature":
        if not args.preview:
            return build_validation_error(
                "sdk security package-signature",
                "Skills SDK package security signature is preview-only and requires --preview.",
                "ask sdk security package-signature <target> --preview --json --robot",
            )
        return skills_commands.skills_sdk_security_package_signature_preview(repo_root, args.target)
    if args.security_action == "risk-modes":
        if not args.preview:
            return build_validation_error(
                "sdk security risk-modes",
                "Skills SDK risk-mode taxonomy is preview-only in PU-033 and requires --preview.",
                "ask sdk security risk-modes <target> --preview --json --robot",
            )
        return skills_commands.skills_sdk_security_risk_modes_preview(repo_root, args.target)
    if args.security_action == "run-lane":
        if not args.preview:
            return build_validation_error(
                "sdk security run-lane",
                "Skills SDK security lane is preview-only and requires --preview.",
                "ask sdk security run-lane <target> --preview --json --robot",
            )
        return skills_commands.skills_sdk_security_run_lane_preview(
            repo_root,
            args.target,
            profile=args.profile,
            require_review=args.require_review,
        )
    return build_unknown_action_result("sdk security", args.security_action)
