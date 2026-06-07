from __future__ import annotations

import argparse
from pathlib import Path

import ask.commands.skills as skills_commands
from ask.envelope import CallResult, ErrorObject
from ask.cli_errors import build_unknown_action_result
from ask.skills_sdk.determinism import audit_skill_determinism
from ask.skills_sdk.lenses import (
    KNOWN_TASK_INTENTS,
    LensCatalogError,
    explain_lens,
    list_lenses,
    select_lenses,
    validate_lens_catalog,
)
from ask.skills_sdk.placeholder_lifecycle import SURFACES


def add_sdk_parser(
    subparsers: argparse._SubParsersAction,
    global_parser: argparse.ArgumentParser,
) -> None:
    """
    Register the 'sdk' CLI command and its subcommands on the provided subparsers.
    
    This adds the top-level "sdk" parser with subcommands: check, install, rollback, uninstall, lifecycle, status, and a nested read-only "project" group with "status" and "doctor". Each subcommand is configured with its expected arguments and shared parents.
    
    Parameters:
        subparsers (argparse._SubParsersAction): The parent subparsers object to which the "sdk" parser will be attached.
        global_parser (argparse.ArgumentParser): A parser containing global/common arguments to be included as a parent for all "sdk" subcommands.
    """
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
    sdk_lenses_parser = sdk_subparsers.add_parser(
        "lenses",
        help="List, explain, validate, or select generic SDK lenses",
        parents=[global_parser],
    )
    sdk_lenses_subparsers = sdk_lenses_parser.add_subparsers(dest="lenses_action", required=True)
    sdk_lenses_list_parser = sdk_lenses_subparsers.add_parser(
        "list",
        help="List the shared SDK lens catalog",
        parents=[global_parser],
    )
    sdk_lenses_explain_parser = sdk_lenses_subparsers.add_parser(
        "explain",
        help="Explain one shared SDK lens",
        parents=[global_parser],
    )
    sdk_lenses_explain_parser.add_argument("lens_id", help="Lens id, for example lens.progressive-disclosure")
    sdk_lenses_validate_parser = sdk_lenses_subparsers.add_parser(
        "validate",
        help="Validate the shared SDK lens catalog",
        parents=[global_parser],
    )
    sdk_lenses_select_parser = sdk_lenses_subparsers.add_parser(
        "select",
        help="Select shared SDK lenses for a task using deterministic signals",
        parents=[global_parser],
    )
    sdk_lenses_select_parser.add_argument("--prompt", required=True, help="Task prompt or summary to route through lenses")
    sdk_lenses_select_parser.add_argument("--skill", help="Optional skill handle or path receiving the lenses")
    sdk_lenses_select_parser.add_argument(
        "--intent",
        "--task-intent",
        dest="task_intent",
        choices=list(KNOWN_TASK_INTENTS),
        help="Optional normalized task intent; inferred from prompt when omitted",
    )
    sdk_lenses_select_parser.add_argument(
        "--repo-file",
        action="append",
        default=[],
        help="Repo-relative file signal to include in selection; repeat for multiple files",
    )
    sdk_lenses_select_parser.add_argument(
        "--max-lenses",
        type=int,
        default=4,
        help="Maximum selected lenses to return",
    )
    for parser_with_registry in (
        sdk_lenses_parser,
        sdk_lenses_list_parser,
        sdk_lenses_explain_parser,
        sdk_lenses_validate_parser,
        sdk_lenses_select_parser,
    ):
        parser_with_registry.add_argument(
            "--registry",
            help="Optional repo-relative or absolute lens registry path",
        )
    sdk_determinism_parser = sdk_subparsers.add_parser(
        "determinism",
        help="Find skill guidance that can become deterministic SDK checks",
        parents=[global_parser],
    )
    sdk_determinism_subparsers = sdk_determinism_parser.add_subparsers(dest="determinism_action", required=True)
    sdk_determinism_audit_parser = sdk_determinism_subparsers.add_parser(
        "audit",
        help="Audit skills for prompt-only rules that can become validators, schemas, or selectors",
        parents=[global_parser],
    )
    sdk_determinism_audit_parser.add_argument(
        "--scope",
        choices=["skills"],
        default="skills",
        help="Audit scope; currently scans canonical skill source roots",
    )
    sdk_determinism_audit_parser.add_argument(
        "--path",
        action="append",
        default=[],
        help="Skill directory or SKILL.md path to audit; repeat for multiple paths",
    )
    sdk_determinism_audit_parser.add_argument(
        "--limit",
        type=int,
        help="Limit returned candidates after deterministic priority sorting",
    )


def dispatch_sdk(repo_root: Path, args: argparse.Namespace) -> CallResult:
    """
    Dispatches an SDK CLI action to the corresponding skills command and validates required argument combinations.
    
    Parameters:
        repo_root (Path): Repository root path passed to SDK handlers.
        args (argparse.Namespace): Parsed CLI arguments. Expected attributes vary by action:
            - action: one of "check", "install", "rollback", "uninstall", "lifecycle", "status", "project".
            - For "check": target, strict, codex_parity.
            - For "install": target, preview, apply, project_root, scope.
            - For "rollback": receipt, preview, apply, project_root.
            - For "uninstall": skill_id, preview, apply, project_root.
            - For "lifecycle": surface, risk_tier.
            - For "project": project_action (e.g., "status" or "doctor"), project_root.
            Provide only the attributes required for the chosen action.
    
    Returns:
        CallResult: Result produced by the invoked skills command. If argument validation fails, returns a `CallResult` with `status="error"` and an `ERR_VALIDATION` error; if the action is unrecognized, returns an unknown-action `CallResult`.
    """
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
    if args.action == "lenses":
        return _dispatch_sdk_lenses(repo_root, args)
    if args.action == "determinism":
        return _dispatch_sdk_determinism(repo_root, args)
    return build_unknown_action_result("sdk", args.action)


def _dispatch_sdk_lenses(repo_root: Path, args: argparse.Namespace) -> CallResult:
    result = CallResult(status="success")
    command_action = args.lenses_action
    result.metadata["command"] = f"sdk lenses {command_action}"
    try:
        if command_action == "list":
            result.data["lens_catalog"] = list_lenses(repo_root, registry_path=args.registry)
            return result
        if command_action == "explain":
            result.data["lens"] = explain_lens(repo_root, args.lens_id, registry_path=args.registry)
            return result
        if command_action == "validate":
            validation = validate_lens_catalog(repo_root, registry_path=args.registry)
            result.data["lens_catalog_validation"] = validation
            if validation["status"] != "pass":
                result.status = "error"
                result.errors.append(
                    ErrorObject(
                        code="ERR_VALIDATION",
                        message="Shared SDK lens catalog validation failed.",
                        fix_suggestion="Run ask sdk lenses validate --json --robot and fix the reported findings.",
                    )
                )
            return result
        if command_action == "select":
            selection = select_lenses(
                repo_root,
                prompt=args.prompt,
                task_intent=args.task_intent,
                repo_files=args.repo_file,
                max_lenses=args.max_lenses,
                skill=args.skill,
                registry_path=args.registry,
            )
            result.data["lens_selection"] = selection
            if selection["status"] != "pass":
                result.status = "error"
                result.errors.append(
                    ErrorObject(
                        code="ERR_VALIDATION",
                        message="Shared SDK lens selection could not run because catalog validation failed.",
                        fix_suggestion="Run ask sdk lenses validate --json --robot and fix the reported findings.",
                    )
                )
            return result
    except LensCatalogError as exc:
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=str(exc),
                fix_suggestion="Run ask sdk lenses validate --json --robot to inspect the shared lens catalog.",
            )
        )
        return result
    return build_unknown_action_result("sdk lenses", command_action)


def _dispatch_sdk_determinism(repo_root: Path, args: argparse.Namespace) -> CallResult:
    result = CallResult(status="success")
    command_action = args.determinism_action
    result.metadata["command"] = f"sdk determinism {command_action}"
    if command_action == "audit":
        try:
            result.data["determinism_audit"] = audit_skill_determinism(
                repo_root,
                scope=args.scope,
                paths=args.path,
                limit=args.limit,
            )
        except ValueError as exc:
            result.status = "error"
            result.errors.append(
                ErrorObject(
                    code="ERR_VALIDATION",
                    message=str(exc),
                    fix_suggestion="Run ask sdk determinism audit --scope skills --json --robot.",
                )
            )
        return result
    return build_unknown_action_result("sdk determinism", command_action)
