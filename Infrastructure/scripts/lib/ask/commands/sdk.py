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
from ask.skills_sdk.knowledge_ingest import build_knowledge_ingest
from ask.skills_sdk.placeholder_lifecycle import SURFACES
from ask.skills_sdk.review_handoff import build_review_handoff
from ask.skills_sdk.review_execute import build_review_execution
from ask.skills_sdk.review_plan import build_review_plan
from ask.skills_sdk.review_verify import build_review_verification


def _add_sdk_ir_parser(
    sdk_subparsers: argparse._SubParsersAction,
    global_parser: argparse.ArgumentParser,
) -> None:
    sdk_ir_parser = sdk_subparsers.add_parser(
        "ir",
        help="Build read-only Skills SDK intermediate representations",
        parents=[global_parser],
    )
    sdk_ir_subparsers = sdk_ir_parser.add_subparsers(dest="ir_action", required=True)
    sdk_ir_build_parser = sdk_ir_subparsers.add_parser(
        "build",
        help="Build SkillIR.v0 for one skill handle or source path",
        parents=[global_parser],
    )
    sdk_ir_build_parser.add_argument("target", help="Skill handle or repo-relative skill source path")


def _add_sdk_docs_parser(
    sdk_subparsers: argparse._SubParsersAction,
    global_parser: argparse.ArgumentParser,
) -> None:
    sdk_docs_parser = sdk_subparsers.add_parser(
        "docs",
        help="Verify Skills SDK documentation projections",
        parents=[global_parser],
    )
    sdk_docs_subparsers = sdk_docs_parser.add_subparsers(dest="docs_action", required=True)
    sdk_docs_verify_parser = sdk_docs_subparsers.add_parser(
        "verify",
        help="Verify the static capability table mirrors the SDK capability matrix",
        parents=[global_parser],
    )
    sdk_docs_verify_parser.add_argument(
        "--artifact",
        help="Optional repo-relative or absolute HTML artifact path to verify",
    )


def _add_sdk_eval_parser(
    sdk_subparsers: argparse._SubParsersAction,
    global_parser: argparse.ArgumentParser,
) -> None:
    sdk_eval_parser = sdk_subparsers.add_parser("eval", help="Run Skills SDK eval receipts", parents=[global_parser])
    sdk_eval_subparsers = sdk_eval_parser.add_subparsers(dest="eval_action", required=True)
    sdk_eval_run_parser = sdk_eval_subparsers.add_parser(
        "run",
        help="Run internal skill evals or exact-match deterministic eval cases",
        parents=[global_parser],
    )
    sdk_eval_run_parser.add_argument("target", nargs="?", help="Skill handle or source path for the internal eval runner")
    sdk_eval_run_parser.add_argument("--dataset", help="Repo-relative or absolute deterministic eval dataset")
    sdk_eval_run_parser.add_argument("--skill", help="Optional skill handle or source path for deterministic evals")
    sdk_eval_run_parser.add_argument(
        "--runner",
        choices=["auto", "internal", "deterministic-jsonl"],
        default="auto",
        help="Eval backend. auto uses deterministic-jsonl with --dataset, otherwise internal.",
    )
    sdk_eval_run_parser.add_argument("--mode", choices=["smoke", "release"], default="smoke", help="Internal eval mode.")
    sdk_eval_run_parser.add_argument("--case", action="append", dest="cases", help="Internal eval case id filter.")
    sdk_eval_run_parser.add_argument("--with-tessl", action="store_true", help="Allow internal Tessl continuation.")


def _add_sdk_package_parser(
    sdk_subparsers: argparse._SubParsersAction,
    global_parser: argparse.ArgumentParser,
) -> None:
    sdk_package_parser = sdk_subparsers.add_parser(
        "package",
        help="Build read-only Skills SDK package identity receipts",
        parents=[global_parser],
    )
    sdk_package_subparsers = sdk_package_parser.add_subparsers(dest="package_action", required=True)
    for action, help_text in {
        "build": "Build a digest-backed package identity receipt without emitting an archive",
        "harden": "Build a read-only package hardening receipt from package identity",
    }.items():
        parser = sdk_package_subparsers.add_parser(action, help=help_text, parents=[global_parser])
        parser.add_argument("target", help="Skill handle or repo-relative skill source path")


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
    _add_sdk_ir_parser(sdk_subparsers, global_parser)
    _add_sdk_docs_parser(sdk_subparsers, global_parser)
    _add_sdk_eval_parser(sdk_subparsers, global_parser)
    _add_sdk_package_parser(sdk_subparsers, global_parser)
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
    sdk_knowledge_parser = sdk_subparsers.add_parser(
        "knowledge",
        help="Vendor portable knowledge bundles into skill packages",
        parents=[global_parser],
    )
    sdk_knowledge_subparsers = sdk_knowledge_parser.add_subparsers(dest="knowledge_action", required=True)
    sdk_knowledge_ingest_parser = sdk_knowledge_subparsers.add_parser(
        "ingest",
        help="Validate and vendor a KnowledgeOS extraction into a skill package",
        parents=[global_parser],
    )
    sdk_knowledge_ingest_parser.add_argument("--extraction", required=True, help="KnowledgeOS extraction directory")
    sdk_knowledge_ingest_parser.add_argument("--skill", required=True, help="Repo-local skill directory or SKILL.md")
    sdk_knowledge_ingest_parser.add_argument("--preview", action="store_true", help="Validate and report writes without mutating")
    sdk_knowledge_ingest_parser.add_argument("--apply", action="store_true", help="Vendor references and update skill routing")
    sdk_knowledge_ingest_parser.add_argument("--run-proof", action="store_true", help="Run package audit and verify after apply")
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
    sdk_review_parser = sdk_subparsers.add_parser(
        "review",
        help="Plan read-only SDK reviews using deterministic lens selection",
        parents=[global_parser],
    )
    sdk_review_subparsers = sdk_review_parser.add_subparsers(dest="review_action", required=True)
    sdk_review_plan_parser = sdk_review_subparsers.add_parser(
        "plan",
        help="Emit a schema-backed read-only review plan receipt",
        parents=[global_parser],
    )
    sdk_review_plan_parser.add_argument("--target", required=True, help="Repo path or handle to review")
    sdk_review_plan_parser.add_argument(
        "--intent",
        "--task-intent",
        dest="task_intent",
        choices=list(KNOWN_TASK_INTENTS),
        required=True,
        help="Normalized review intent used for lens selection",
    )
    sdk_review_plan_parser.add_argument("--prompt", help="Optional review prompt or summary")
    sdk_review_plan_parser.add_argument(
        "--repo-file",
        action="append",
        default=[],
        help="Repo-relative file signal to include in review routing; repeat for multiple files",
    )
    sdk_review_plan_parser.add_argument(
        "--max-lenses",
        type=int,
        default=4,
        help="Maximum selected lenses to include in the review plan",
    )
    sdk_review_plan_parser.add_argument(
        "--receipt-out",
        help="Optional repo-local path for writing the review plan receipt",
    )
    sdk_review_handoff_parser = sdk_review_subparsers.add_parser(
        "handoff",
        help="Emit a schema-backed read-only review handoff receipt from a review plan receipt",
        parents=[global_parser],
    )
    sdk_review_handoff_parser.add_argument("--plan", required=True, help="Repo-local review plan receipt path")
    sdk_review_handoff_parser.add_argument("--target", required=True, help="Repo path or handle from the source review plan")
    sdk_review_handoff_parser.add_argument(
        "--intent",
        "--task-intent",
        dest="task_intent",
        choices=list(KNOWN_TASK_INTENTS),
        required=True,
        help="Normalized review intent from the source review plan",
    )
    sdk_review_handoff_parser.add_argument(
        "--receipt-out",
        help="Optional repo-local path for writing the review handoff receipt",
    )
    sdk_review_execute_parser = sdk_review_subparsers.add_parser(
        "execute",
        help="Materialize required local review artifacts from a review handoff receipt",
        parents=[global_parser],
    )
    sdk_review_execute_parser.add_argument("--handoff", required=True, help="Repo-local review handoff receipt path")
    sdk_review_execute_parser.add_argument(
        "--receipt-out",
        help="Optional repo-local path for writing the review execution receipt",
    )
    sdk_review_verify_parser = sdk_review_subparsers.add_parser(
        "verify",
        help="Verify required local artifacts from a review handoff receipt without external readiness claims",
        parents=[global_parser],
    )
    sdk_review_verify_parser.add_argument("--handoff", required=True, help="Repo-local review handoff receipt path")
    sdk_review_verify_parser.add_argument(
        "--receipt-out",
        help="Optional repo-local path for writing the review verification receipt",
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
    core_dispatchers = {
        "ir": _dispatch_sdk_ir,
        "docs": _dispatch_sdk_docs,
        "eval": _dispatch_sdk_eval,
        "package": _dispatch_sdk_package,
    }
    if args.action in core_dispatchers:
        return core_dispatchers[args.action](repo_root, args)
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
    tail_dispatchers = {
        "knowledge": _dispatch_sdk_knowledge,
        "lenses": _dispatch_sdk_lenses,
        "determinism": _dispatch_sdk_determinism,
        "review": _dispatch_sdk_review,
    }
    if args.action in tail_dispatchers:
        return tail_dispatchers[args.action](repo_root, args)
    if args.action == "project":
        if args.project_action in {"status", "doctor"}:
            return skills_commands.skills_sdk_project_conformance(
                repo_root,
                project_root=args.project_root,
                mode=args.project_action,
            )
        return build_unknown_action_result("sdk", args.project_action)
    return build_unknown_action_result("sdk", args.action)


def _dispatch_sdk_ir(repo_root: Path, args: argparse.Namespace) -> CallResult:
    if args.ir_action == "build":
        return skills_commands.skills_sdk_ir_build(repo_root, target=args.target)
    return build_unknown_action_result("sdk ir", args.ir_action)


def _dispatch_sdk_docs(repo_root: Path, args: argparse.Namespace) -> CallResult:
    if args.docs_action == "verify":
        return skills_commands.skills_sdk_docs_verify(repo_root, artifact=args.artifact)
    return build_unknown_action_result("sdk docs", args.docs_action)


def _dispatch_sdk_eval(repo_root: Path, args: argparse.Namespace) -> CallResult:
    if args.eval_action == "run":
        return skills_commands.skills_sdk_eval_run(
            repo_root,
            dataset=args.dataset,
            target=args.skill or args.target,
            mode=args.mode,
            runner=args.runner,
            skip_tessl=not args.with_tessl,
            cases=args.cases,
        )
    return build_unknown_action_result("sdk eval", args.eval_action)


def _dispatch_sdk_package(repo_root: Path, args: argparse.Namespace) -> CallResult:
    if args.package_action == "build":
        return skills_commands.skills_sdk_package_build(repo_root, target=args.target)
    if args.package_action == "harden":
        return skills_commands.skills_sdk_package_harden(repo_root, target=args.target)
    return build_unknown_action_result("sdk package", args.package_action)


def _dispatch_sdk_knowledge(repo_root: Path, args: argparse.Namespace) -> CallResult:
    result = CallResult(status="success")
    command_action = args.knowledge_action
    result.metadata["command"] = f"sdk knowledge {command_action}"
    if command_action == "ingest":
        if args.preview == args.apply:
            result.status = "error"
            result.errors.append(
                ErrorObject(
                    code="ERR_VALIDATION",
                    message="Skills SDK knowledge ingest requires exactly one of --preview or --apply.",
                    fix_suggestion=(
                        "Run ask sdk knowledge ingest --extraction <KnowledgeOS extraction> "
                        "--skill <skill path> --preview --json --robot."
                    ),
                )
            )
            return result
        if args.run_proof and not args.apply:
            result.status = "error"
            result.errors.append(
                ErrorObject(
                    code="ERR_VALIDATION",
                    message="--run-proof is only valid with --apply.",
                    fix_suggestion="Run knowledge ingest with --apply --run-proof or drop --run-proof for preview.",
                )
            )
            return result
        try:
            payload = build_knowledge_ingest(
                repo_root,
                extraction=args.extraction,
                skill=args.skill,
                apply=args.apply,
                run_proof=args.run_proof,
            )
        except ValueError as exc:
            result.status = "error"
            result.errors.append(
                ErrorObject(
                    code="ERR_VALIDATION",
                    message=str(exc),
                    fix_suggestion=(
                        "Check that --extraction is a KnowledgeOS extraction with references/ and "
                        "--skill is a repo-local Skills SDK package."
                    ),
                )
            )
            return result
        result.data["knowledge_ingest"] = payload
        if payload["status"] not in {"preview", "applied"}:
            result.status = "error"
            result.errors.append(
                ErrorObject(
                    code="ERR_VALIDATION",
                    message="Skills SDK knowledge ingest was blocked by extraction validation findings.",
                    fix_suggestion="Fix the reported knowledge_ingest.findings before applying.",
                )
            )
        return result
    return build_unknown_action_result("sdk knowledge", command_action)


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


def _dispatch_sdk_review(repo_root: Path, args: argparse.Namespace) -> CallResult:
    result = CallResult(status="success")
    command_action = args.review_action
    result.metadata["command"] = f"sdk review {command_action}"
    if command_action == "plan":
        try:
            review_plan = build_review_plan(
                repo_root,
                target=args.target,
                task_intent=args.task_intent,
                prompt=args.prompt,
                repo_files=args.repo_file,
                max_lenses=args.max_lenses,
                receipt_out=args.receipt_out,
            )
        except (LensCatalogError, ValueError) as exc:
            result.status = "error"
            result.errors.append(
                ErrorObject(
                    code="ERR_VALIDATION",
                    message=str(exc),
                    fix_suggestion="Run ask sdk review plan --target <path-or-handle> --intent validation_review --json --robot.",
                )
            )
            return result
        result.data["review_plan"] = review_plan
        if review_plan["status"] != "pass":
            result.status = "error"
            result.errors.append(
                ErrorObject(
                    code="ERR_VALIDATION",
                    message="Skills SDK review plan could not be built.",
                    fix_suggestion="Run ask sdk lenses validate --json --robot and fix catalog findings.",
                )
            )
        return result
    if command_action == "handoff":
        try:
            review_handoff = build_review_handoff(
                repo_root,
                plan_path=args.plan,
                target=args.target,
                task_intent=args.task_intent,
                receipt_out=args.receipt_out,
            )
        except ValueError as exc:
            result.status = "error"
            result.errors.append(
                ErrorObject(
                    code="ERR_VALIDATION",
                    message=str(exc),
                    fix_suggestion=(
                        "Run ask sdk review plan --target <path> --intent validation_review "
                        "--receipt-out .harness/artifacts/sdk-review-plan/<name>.json --json --robot, "
                        "then retry ask sdk review handoff with matching --plan, --target, and --intent."
                    ),
                )
            )
            return result
        result.data["review_handoff"] = review_handoff
        return result
    if command_action == "execute":
        try:
            review_execution = build_review_execution(
                repo_root,
                handoff_path=args.handoff,
                receipt_out=args.receipt_out,
            )
        except ValueError as exc:
            result.status = "error"
            result.errors.append(
                ErrorObject(
                    code="ERR_VALIDATION",
                    message=str(exc),
                    fix_suggestion=(
                        "Run ask sdk review handoff --plan <plan-receipt> --target <path> "
                        "--intent validation_review --receipt-out <handoff-receipt> --json --robot, "
                        "then retry ask sdk review execute with --handoff <handoff-receipt>."
                    ),
                )
            )
            return result
        result.data["review_execution"] = review_execution
        if review_execution["status"] != "pass":
            result.status = "error"
            result.errors.append(
                ErrorObject(
                    code="ERR_VALIDATION",
                    message="Skills SDK review execution could not materialize every required artifact.",
                    fix_suggestion="Repair every path in data.review_execution.failed_artifacts.",
                )
            )
        return result
    if command_action == "verify":
        try:
            review_verification = build_review_verification(
                repo_root,
                handoff_path=args.handoff,
                receipt_out=args.receipt_out,
            )
        except ValueError as exc:
            result.status = "error"
            result.errors.append(
                ErrorObject(
                    code="ERR_VALIDATION",
                    message=str(exc),
                    fix_suggestion=(
                        "Run ask sdk review handoff --plan <plan-receipt> --target <path> "
                        "--intent validation_review --receipt-out <handoff-receipt> --json --robot, "
                        "then retry ask sdk review verify with --handoff <handoff-receipt>."
                    ),
                )
            )
            return result
        result.data["review_verification"] = review_verification
        if review_verification["status"] != "pass":
            result.status = "error"
            result.errors.append(
                ErrorObject(
                    code="ERR_VALIDATION",
                    message="Skills SDK review artifacts are missing or invalid.",
                    fix_suggestion="Create or repair every path in data.review_verification.missing_or_invalid_artifacts.",
                )
            )
        return result
    return build_unknown_action_result("sdk review", command_action)
