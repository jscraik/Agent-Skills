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
        help="Preview or apply a bounded Skills SDK project install",
        parents=[global_parser],
    )
    sdk_install_parser.add_argument("target", help="Skill handle or repo-relative skill source path")
    sdk_install_parser.add_argument("--preview", action="store_true", help="Plan the install without performing writes")
    sdk_install_parser.add_argument("--apply", action="store_true", help="Perform a real project install")
    sdk_install_parser.add_argument("--project-root", help="Absolute marked project root for --apply installs")
    sdk_install_parser.add_argument(
        "--scope",
        choices=["project", "workspace", "global"],
        default="project",
        help="Install scope to model in the preview; real installs only support project",
    )
    sdk_rollback_parser = sdk_subparsers.add_parser(
        "rollback",
        help="Preview or apply receipt-proven Skills SDK project rollback",
        parents=[global_parser],
    )
    sdk_rollback_parser.add_argument("--receipt", required=True, help="Path to a Skills SDK project install receipt")
    sdk_rollback_parser.add_argument("--preview", action="store_true", help="Plan rollback without performing writes")
    sdk_rollback_parser.add_argument("--apply", action="store_true", help="Perform rollback in an explicit project root")
    sdk_rollback_parser.add_argument("--project-root", help="Absolute marked project root for live validation or apply")
    sdk_uninstall_parser = sdk_subparsers.add_parser(
        "uninstall",
        help="Preview or apply receipt-proven Skills SDK project uninstall",
        parents=[global_parser],
    )
    sdk_uninstall_parser.add_argument("skill_id", help="Installed skill id to resolve through skills.lock.json")
    sdk_uninstall_parser.add_argument("--preview", action="store_true", help="Plan uninstall without performing writes")
    sdk_uninstall_parser.add_argument("--apply", action="store_true", help="Perform uninstall in an explicit project root")
    sdk_uninstall_parser.add_argument("--project-root", required=True, help="Absolute marked project root containing skills.lock.json")
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
    sdk_subparsers.add_parser(
        "status",
        help="Report the Skills SDK capability truth matrix",
        parents=[global_parser],
    )
    sdk_project_parser = sdk_subparsers.add_parser(
        "project",
        help="Inspect read-only Skills SDK project conformance",
        parents=[global_parser],
    )
    sdk_project_subparsers = sdk_project_parser.add_subparsers(dest="project_action")
    for project_action in ("status", "doctor"):
        project_parser = sdk_project_subparsers.add_parser(
            project_action,
            help=f"Run read-only Skills SDK project {project_action}",
            parents=[global_parser],
        )
        project_parser.add_argument(
            "--project-root",
            required=True,
            help="Absolute marked project root to inspect without mutation",
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
        if args.preview and args.apply:
            result = CallResult(status="error")
            result.metadata["command"] = "sdk install"
            result.errors.append(
                ErrorObject(
                    code="ERR_VALIDATION",
                    message="Skills SDK install accepts either --preview or --apply, not both.",
                    fix_suggestion="ask sdk install <target> --preview --json --robot",
                )
            )
            return result
        if args.apply:
            return skills_commands.skills_sdk_project_install(
                repo_root,
                target=args.target,
                project_root=args.project_root,
                scope=args.scope,
            )
        if not args.preview:
            result = CallResult(status="error")
            result.metadata["command"] = "sdk install"
            result.errors.append(
                ErrorObject(
                    code="ERR_VALIDATION",
                    message="Skills SDK install requires --preview for read-only planning or --apply with --project-root for real project writes.",
                    fix_suggestion="ask sdk install <target> --preview --json --robot",
                )
            )
            return result
        return skills_commands.skills_sdk_install_preview(
            repo_root,
            target=args.target,
            scope=args.scope,
        )
    if args.action == "rollback":
        if args.preview == args.apply:
            result = CallResult(status="error")
            result.metadata["command"] = "sdk rollback"
            result.errors.append(
                ErrorObject(
                    code="ERR_VALIDATION",
                    message="Skills SDK rollback requires exactly one of --preview or --apply.",
                    fix_suggestion="ask sdk rollback --receipt <path> --preview --json --robot",
                )
            )
            return result
        return skills_commands.skills_sdk_project_rollback(
            repo_root,
            receipt_path=args.receipt,
            project_root=args.project_root,
            apply=args.apply,
        )
    if args.action == "uninstall":
        if args.preview == args.apply:
            result = CallResult(status="error")
            result.metadata["command"] = "sdk uninstall"
            result.errors.append(
                ErrorObject(
                    code="ERR_VALIDATION",
                    message="Skills SDK uninstall requires exactly one of --preview or --apply.",
                    fix_suggestion="ask sdk uninstall <skill-id> --project-root /path/to/project --preview --json --robot",
                )
            )
            return result
        return skills_commands.skills_sdk_project_uninstall(
            repo_root,
            skill_id=args.skill_id,
            project_root=args.project_root,
            apply=args.apply,
        )
    if args.action == "lifecycle":
        return skills_commands.skills_sdk_placeholder_lifecycle(
            repo_root,
            surface=args.surface,
            risk_tier=args.risk_tier,
        )
    if args.action == "status":
        return skills_commands.skills_sdk_status(repo_root)
    if args.action == "project":
        if args.project_action in {"status", "doctor"}:
            return skills_commands.skills_sdk_project_conformance(
                repo_root,
                project_root=args.project_root,
                mode=args.project_action,
            )
        return build_unknown_action_result("sdk", args.project_action)
    return build_unknown_action_result("sdk", args.action)
