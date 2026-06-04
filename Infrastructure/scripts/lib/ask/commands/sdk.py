from __future__ import annotations

import argparse
from pathlib import Path

import ask.commands.skills as skills_commands
from ask.envelope import CallResult, ErrorObject
from ask.cli_errors import build_unknown_action_result
from ask.skills_sdk.placeholder_lifecycle import SURFACES


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
    sdk_install_parser = sdk_subparsers.add_parser(
        "install",
        help="Preview a Skills SDK install without writing install state",
        parents=[global_parser],
    )
    sdk_install_parser.add_argument("target", help="Skill handle or repo-relative skill source path")
    sdk_install_parser.add_argument("--preview", action="store_true", help="Plan the install without performing writes")
    sdk_install_parser.add_argument(
        "--scope",
        choices=["project", "workspace", "global"],
        default="project",
        help="Install scope to model in the preview",
    )
    sdk_lifecycle_parser = sdk_subparsers.add_parser(
        "lifecycle",
        help="Emit honest placeholder lifecycle receipts for unavailable V1.0 surfaces",
        parents=[global_parser],
    )
    sdk_lifecycle_parser.add_argument(
        "--surface",
        choices=list(SURFACES),
        help="Limit output to one lifecycle surface",
    )
    sdk_lifecycle_parser.add_argument(
        "--risk-tier",
        choices=["low", "medium", "high", "privileged", "published"],
        default="medium",
        help="Risk tier used to decide whether unavailable adapters block",
    )


def dispatch_sdk(repo_root: Path, args: argparse.Namespace) -> CallResult:
    if args.action == "check":
        return skills_commands.skills_sdk_check(
            repo_root,
            target=args.target,
            strict=args.strict,
            codex_parity=args.codex_parity,
        )
    if args.action == "install":
        if not args.preview:
            result = CallResult(status="error")
            result.metadata["command"] = "sdk install"
            result.errors.append(
                ErrorObject(
                    code="ERR_VALIDATION",
                    message="Skills SDK install is preview-only in V1.0; pass --preview to model writes without performing them.",
                    fix_suggestion="ask sdk install <target> --preview --json --robot",
                )
            )
            return result
        return skills_commands.skills_sdk_install_preview(
            repo_root,
            target=args.target,
            scope=args.scope,
        )
    if args.action == "lifecycle":
        return skills_commands.skills_sdk_placeholder_lifecycle(
            repo_root,
            surface=args.surface,
            risk_tier=args.risk_tier,
        )
    return build_unknown_action_result("sdk", args.action)
