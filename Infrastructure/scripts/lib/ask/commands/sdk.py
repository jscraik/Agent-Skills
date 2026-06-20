from __future__ import annotations

import argparse
from pathlib import Path

import ask.commands.skills as skills_commands
from ask.envelope import CallResult, ErrorObject
from ask.cli_errors import build_unknown_action_result
from ask.commands.sdk_ci import add_sdk_ci_parser, dispatch_sdk_ci
from ask.commands.sdk_emitter import add_sdk_emitter_parser, dispatch_sdk_emitter
from ask.commands.sdk_eval import add_sdk_eval_parser, dispatch_sdk_eval
from ask.commands.sdk_explorer import add_sdk_explorer_parser, dispatch_sdk_explorer
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


def _add_sdk_ir_parser(sdk_subparsers: argparse._SubParsersAction, global_parser: argparse.ArgumentParser) -> None:
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


def _add_sdk_docs_parser(sdk_subparsers: argparse._SubParsersAction, global_parser: argparse.ArgumentParser) -> None:
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
        "signing-intent": "Build a non-mutating signing intent receipt from package identity and policy",
    }.items():
        parser = sdk_package_subparsers.add_parser(action, help=help_text, parents=[global_parser])
        parser.add_argument("target", help="Skill handle or repo-relative skill source path")
        if action == "signing-intent":
            parser.add_argument("--policy", required=True, help="Repo-relative or absolute signing policy JSON")


def _add_sdk_sandbox_parser(
    sdk_subparsers: argparse._SubParsersAction,
    global_parser: argparse.ArgumentParser,
) -> None:
    sdk_sandbox_parser = sdk_subparsers.add_parser(
        "sandbox",
        help="Validate Skills SDK sandbox profiles without executing providers",
        parents=[global_parser],
    )
    sdk_sandbox_subparsers = sdk_sandbox_parser.add_subparsers(dest="sandbox_action", required=True)
    sdk_sandbox_validate_parser = sdk_sandbox_subparsers.add_parser(
        "validate",
        help="Validate a deny-by-default sandbox profile receipt",
        parents=[global_parser],
    )
    sdk_sandbox_validate_parser.add_argument("--profile", required=True, help="Repo-relative or absolute sandbox profile JSON")


def _add_sdk_trust_parser(
    sdk_subparsers: argparse._SubParsersAction,
    global_parser: argparse.ArgumentParser,
) -> None:
    sdk_trust_parser = sdk_subparsers.add_parser("trust", help="Preview or append local Skills SDK trust decisions", parents=[global_parser])
    sdk_trust_subparsers = sdk_trust_parser.add_subparsers(dest="trust_action", required=True)
    decide = sdk_trust_subparsers.add_parser("decide", help="Build a local trust decision receipt for one package identity", parents=[global_parser])
    decide.add_argument("target", help="Skill handle or repo-relative skill source path")
    decide.add_argument("--decision", choices=["trust", "distrust", "revoke"], required=True)
    decide.add_argument("--reason", required=True, help="Human-readable decision reason")
    decide.add_argument("--owner", required=True, help="Decision owner")
    decide.add_argument("--expires-at", help="Optional ISO-8601 expiry for the decision")
    decide.add_argument("--revoked-package-digest", help="Required when --decision revoke")
    decide.add_argument("--ledger", help="Repo-relative or temporary JSONL ledger path")
    decide.add_argument("--preview", action="store_true", help="Emit the receipt without writing the ledger")
    decide.add_argument("--apply", action="store_true", help="Append the decision to the local ledger")


def _add_sdk_observability_parser(sdk_subparsers: argparse._SubParsersAction, global_parser: argparse.ArgumentParser) -> None:
    parser = sdk_subparsers.add_parser("observability", help="Preview redacted runtime feedback candidates", parents=[global_parser])
    subparsers = parser.add_subparsers(dest="observability_action", required=True)
    feedback = subparsers.add_parser("feedback", help="Mine redacted event JSONL into blocked eval and skill-gap candidates", parents=[global_parser])
    feedback.add_argument("--skill", required=True, help="Skill handle or repo-relative skill source path")
    feedback.add_argument("--events", required=True, help="Repo-relative or temporary redacted events JSONL")
    feedback.add_argument("--preview", action="store_true", help="Emit a non-mutating feedback receipt")


def _add_sdk_check_parser(
    sdk_subparsers: argparse._SubParsersAction,
    global_parser: argparse.ArgumentParser,
) -> None:
    parser = sdk_subparsers.add_parser(
        "check",
        help="Run the Skills SDK check facade for one skill handle or source path",
        parents=[global_parser],
    )
    parser.add_argument("target", help="Skill handle or repo-relative skill source path")
    parser.add_argument("--strict", action="store_true", help="Run strict audit instead of the default compat audit")
    parser.add_argument("--codex-parity", action="store_true", help="Require Codex-targeted runtime proof")


def _add_sdk_project_mutation_parsers(
    sdk_subparsers: argparse._SubParsersAction,
    global_parser: argparse.ArgumentParser,
) -> None:
    install = sdk_subparsers.add_parser("install", help="Preview or apply a bounded Skills SDK project install", parents=[global_parser])
    install.add_argument("target", help="Skill handle or repo-relative skill source path")
    install.add_argument("--preview", action="store_true", help="Plan the install without performing writes")
    install.add_argument("--apply", action="store_true", help="Perform a real project install")
    install.add_argument("--project-root", help="Absolute marked project root for --apply installs")
    install.add_argument("--scope", choices=["project", "workspace", "global"], default="project", help="Install scope to model in the preview; real installs only support project")

    rollback = sdk_subparsers.add_parser("rollback", help="Preview or apply receipt-proven Skills SDK project rollback", parents=[global_parser])
    rollback.add_argument("--receipt", required=True, help="Path to a Skills SDK project install receipt")
    rollback.add_argument("--preview", action="store_true", help="Plan rollback without performing writes")
    rollback.add_argument("--apply", action="store_true", help="Perform rollback in an explicit project root")
    rollback.add_argument("--project-root", help="Absolute marked project root for live validation or apply")

    uninstall = sdk_subparsers.add_parser("uninstall", help="Preview or apply receipt-proven Skills SDK project uninstall", parents=[global_parser])
    uninstall.add_argument("skill_id", help="Installed skill id to resolve through skills.lock.json")
    uninstall.add_argument("--preview", action="store_true", help="Plan uninstall without performing writes")
    uninstall.add_argument("--apply", action="store_true", help="Perform uninstall in an explicit project root")
    uninstall.add_argument("--project-root", required=True, help="Absolute marked project root containing skills.lock.json")


def _add_sdk_lifecycle_status_parsers(
    sdk_subparsers: argparse._SubParsersAction,
    global_parser: argparse.ArgumentParser,
) -> None:
    lifecycle = sdk_subparsers.add_parser(
        "lifecycle",
        help="Emit honest placeholder lifecycle receipts for unavailable V1.0 surfaces",
        parents=[global_parser],
    )
    lifecycle.add_argument("--surface", choices=list(SURFACES), help="Limit output to one lifecycle surface")
    lifecycle.add_argument(
        "--risk-tier",
        choices=["low", "medium", "high", "privileged", "published"],
        default="medium",
        help="Risk tier used to decide whether unavailable adapters block",
    )
    sdk_subparsers.add_parser("status", help="Report the Skills SDK capability truth matrix", parents=[global_parser])


def _add_sdk_knowledge_parser(
    sdk_subparsers: argparse._SubParsersAction,
    global_parser: argparse.ArgumentParser,
) -> None:
    parser = sdk_subparsers.add_parser("knowledge", help="Vendor portable knowledge bundles into skill packages", parents=[global_parser])
    subparsers = parser.add_subparsers(dest="knowledge_action", required=True)
    ingest = subparsers.add_parser("ingest", help="Validate and vendor a KnowledgeOS extraction into a skill package", parents=[global_parser])
    ingest.add_argument("--extraction", required=True, help="KnowledgeOS extraction directory")
    ingest.add_argument("--skill", required=True, help="Repo-local skill directory or SKILL.md")
    ingest.add_argument("--preview", action="store_true", help="Validate and report writes without mutating")
    ingest.add_argument("--apply", action="store_true", help="Vendor references and update skill routing")
    ingest.add_argument("--run-proof", action="store_true", help="Run package audit and verify after apply")


def _add_sdk_project_parser(
    sdk_subparsers: argparse._SubParsersAction,
    global_parser: argparse.ArgumentParser,
) -> None:
    parser = sdk_subparsers.add_parser("project", help="Inspect read-only Skills SDK project conformance", parents=[global_parser])
    subparsers = parser.add_subparsers(dest="project_action")
    for project_action in ("status", "doctor"):
        project_parser = subparsers.add_parser(project_action, help=f"Run read-only Skills SDK project {project_action}", parents=[global_parser])
        project_parser.add_argument("--project-root", required=True, help="Absolute marked project root to inspect without mutation")


def _add_sdk_lenses_parser(
    sdk_subparsers: argparse._SubParsersAction,
    global_parser: argparse.ArgumentParser,
) -> None:
    parser = sdk_subparsers.add_parser("lenses", help="List, explain, validate, or select generic SDK lenses", parents=[global_parser])
    subparsers = parser.add_subparsers(dest="lenses_action", required=True)
    list_parser = subparsers.add_parser("list", help="List the shared SDK lens catalog", parents=[global_parser])
    explain = subparsers.add_parser("explain", help="Explain one shared SDK lens", parents=[global_parser])
    explain.add_argument("lens_id", help="Lens id, for example lens.progressive-disclosure")
    validate = subparsers.add_parser("validate", help="Validate the shared SDK lens catalog", parents=[global_parser])
    select = subparsers.add_parser("select", help="Select shared SDK lenses for a task using deterministic signals", parents=[global_parser])
    select.add_argument("--prompt", required=True, help="Task prompt or summary to route through lenses")
    select.add_argument("--skill", help="Optional skill handle or path receiving the lenses")
    select.add_argument("--intent", "--task-intent", dest="task_intent", choices=list(KNOWN_TASK_INTENTS), help="Optional normalized task intent; inferred from prompt when omitted")
    select.add_argument("--repo-file", action="append", default=[], help="Repo-relative file signal to include in selection; repeat for multiple files")
    select.add_argument("--max-lenses", type=int, default=4, help="Maximum selected lenses to return")
    for registry_parser in (parser, list_parser, explain, validate, select):
        registry_parser.add_argument("--registry", help="Optional repo-relative or absolute lens registry path")


def _add_sdk_determinism_parser(
    sdk_subparsers: argparse._SubParsersAction,
    global_parser: argparse.ArgumentParser,
) -> None:
    parser = sdk_subparsers.add_parser("determinism", help="Find skill guidance that can become deterministic SDK checks", parents=[global_parser])
    subparsers = parser.add_subparsers(dest="determinism_action", required=True)
    audit = subparsers.add_parser("audit", help="Audit skills for prompt-only rules that can become validators, schemas, or selectors", parents=[global_parser])
    audit.add_argument("--scope", choices=["skills"], default="skills", help="Audit scope; currently scans canonical skill source roots")
    audit.add_argument("--path", action="append", default=[], help="Skill directory or SKILL.md path to audit; repeat for multiple paths")
    audit.add_argument("--limit", type=int, help="Limit returned candidates after deterministic priority sorting")


def _add_sdk_review_plan_parser(
    subparsers: argparse._SubParsersAction,
    global_parser: argparse.ArgumentParser,
) -> None:
    parser = subparsers.add_parser("plan", help="Emit a schema-backed read-only review plan receipt", parents=[global_parser])
    parser.add_argument("--target", required=True, help="Repo path or handle to review")
    parser.add_argument("--intent", "--task-intent", dest="task_intent", choices=list(KNOWN_TASK_INTENTS), required=True, help="Normalized review intent used for lens selection")
    parser.add_argument("--prompt", help="Optional review prompt or summary")
    parser.add_argument("--repo-file", action="append", default=[], help="Repo-relative file signal to include in review routing; repeat for multiple paths")
    parser.add_argument("--max-lenses", type=int, default=4, help="Maximum selected lenses to include in the review plan")
    parser.add_argument("--receipt-out", help="Optional repo-local path for writing the review plan receipt")


def _add_sdk_review_handoff_parser(
    subparsers: argparse._SubParsersAction,
    global_parser: argparse.ArgumentParser,
) -> None:
    parser = subparsers.add_parser("handoff", help="Emit a schema-backed read-only review handoff receipt from a review plan receipt", parents=[global_parser])
    parser.add_argument("--plan", required=True, help="Repo-local review plan receipt path")
    parser.add_argument("--target", required=True, help="Repo path or handle from the source review plan")
    parser.add_argument("--intent", "--task-intent", dest="task_intent", choices=list(KNOWN_TASK_INTENTS), required=True, help="Normalized review intent from the source review plan")
    parser.add_argument("--receipt-out", help="Optional repo-local path for writing the review handoff receipt")


def _add_sdk_review_parser(
    sdk_subparsers: argparse._SubParsersAction,
    global_parser: argparse.ArgumentParser,
) -> None:
    parser = sdk_subparsers.add_parser("review", help="Plan read-only SDK reviews using deterministic lens selection", parents=[global_parser])
    subparsers = parser.add_subparsers(dest="review_action", required=True)
    _add_sdk_review_plan_parser(subparsers, global_parser)
    _add_sdk_review_handoff_parser(subparsers, global_parser)
    execute = subparsers.add_parser("execute", help="Materialize required local review artifacts from a review handoff receipt", parents=[global_parser])
    execute.add_argument("--handoff", required=True, help="Repo-local review handoff receipt path")
    execute.add_argument("--receipt-out", help="Optional repo-local path for writing the review execution receipt")
    verify = subparsers.add_parser("verify", help="Verify required local artifacts from a review handoff receipt without external readiness claims", parents=[global_parser])
    verify.add_argument("--handoff", required=True, help="Repo-local review handoff receipt path")
    verify.add_argument("--receipt-out", help="Optional repo-local path for writing the review verification receipt")


def add_sdk_parser(
    subparsers: argparse._SubParsersAction,
    global_parser: argparse.ArgumentParser,
) -> None:
    sdk_parser = subparsers.add_parser("sdk", help="Skills SDK product facade", parents=[global_parser])
    sdk_subparsers = sdk_parser.add_subparsers(dest="action")
    _add_sdk_check_parser(sdk_subparsers, global_parser)
    _add_sdk_ir_parser(sdk_subparsers, global_parser)
    _add_sdk_docs_parser(sdk_subparsers, global_parser)
    add_sdk_eval_parser(sdk_subparsers, global_parser)
    _add_sdk_package_parser(sdk_subparsers, global_parser)
    _add_sdk_sandbox_parser(sdk_subparsers, global_parser)
    _add_sdk_trust_parser(sdk_subparsers, global_parser)
    _add_sdk_observability_parser(sdk_subparsers, global_parser)
    add_sdk_emitter_parser(sdk_subparsers, global_parser)
    add_sdk_ci_parser(sdk_subparsers, global_parser)
    add_sdk_explorer_parser(sdk_subparsers, global_parser)
    _add_sdk_project_mutation_parsers(sdk_subparsers, global_parser)
    _add_sdk_lifecycle_status_parsers(sdk_subparsers, global_parser)
    _add_sdk_knowledge_parser(sdk_subparsers, global_parser)
    _add_sdk_project_parser(sdk_subparsers, global_parser)
    _add_sdk_lenses_parser(sdk_subparsers, global_parser)
    _add_sdk_determinism_parser(sdk_subparsers, global_parser)
    _add_sdk_review_parser(sdk_subparsers, global_parser)


def _validation_error(command: str, message: str, fix_suggestion: str) -> CallResult:
    result = CallResult(status="error")
    result.metadata["command"] = command
    result.errors.append(
        ErrorObject(code="ERR_VALIDATION", message=message, fix_suggestion=fix_suggestion)
    )
    return result


def _dispatch_sdk_check(repo_root: Path, args: argparse.Namespace) -> CallResult:
    return skills_commands.skills_sdk_check(
        repo_root,
        target=args.target,
        strict=args.strict,
        codex_parity=args.codex_parity,
    )


def _dispatch_sdk_install(repo_root: Path, args: argparse.Namespace) -> CallResult:
    if args.preview and args.apply:
        return _validation_error(
            "sdk install",
            "Skills SDK install accepts either --preview or --apply, not both.",
            "ask sdk install <target> --preview --json --robot",
        )
    if args.apply:
        return skills_commands.skills_sdk_project_install(
            repo_root,
            target=args.target,
            project_root=args.project_root,
            scope=args.scope,
        )
    if args.preview:
        return skills_commands.skills_sdk_install_preview(repo_root, target=args.target, scope=args.scope)
    return _validation_error(
        "sdk install",
        "Skills SDK install requires --preview for read-only planning or --apply with --project-root for real project writes.",
        "ask sdk install <target> --preview --json --robot",
    )


def _dispatch_sdk_rollback(repo_root: Path, args: argparse.Namespace) -> CallResult:
    if args.preview == args.apply:
        return _validation_error(
            "sdk rollback",
            "Skills SDK rollback requires exactly one of --preview or --apply.",
            "ask sdk rollback --receipt <path> --preview --json --robot",
        )
    return skills_commands.skills_sdk_project_rollback(
        repo_root,
        receipt_path=args.receipt,
        project_root=args.project_root,
        apply=args.apply,
    )


def _dispatch_sdk_uninstall(repo_root: Path, args: argparse.Namespace) -> CallResult:
    if args.preview == args.apply:
        return _validation_error(
            "sdk uninstall",
            "Skills SDK uninstall requires exactly one of --preview or --apply.",
            "ask sdk uninstall <skill-id> --project-root /path/to/project --preview --json --robot",
        )
    return skills_commands.skills_sdk_project_uninstall(
        repo_root,
        skill_id=args.skill_id,
        project_root=args.project_root,
        apply=args.apply,
    )


def _dispatch_sdk_lifecycle(repo_root: Path, args: argparse.Namespace) -> CallResult:
    return skills_commands.skills_sdk_placeholder_lifecycle(
        repo_root,
        surface=args.surface,
        risk_tier=args.risk_tier,
    )


def _dispatch_sdk_project(repo_root: Path, args: argparse.Namespace) -> CallResult:
    if args.project_action in {"status", "doctor"}:
        return skills_commands.skills_sdk_project_conformance(
            repo_root,
            project_root=args.project_root,
            mode=args.project_action,
        )
    return build_unknown_action_result("sdk", args.project_action)


def dispatch_sdk(repo_root: Path, args: argparse.Namespace) -> CallResult:
    dispatchers = {
        "check": _dispatch_sdk_check,
        "ir": _dispatch_sdk_ir,
        "docs": _dispatch_sdk_docs,
        "eval": dispatch_sdk_eval,
        "package": _dispatch_sdk_package,
        "sandbox": _dispatch_sdk_sandbox,
        "trust": _dispatch_sdk_trust,
        "observability": _dispatch_sdk_observability,
        "emitter": dispatch_sdk_emitter,
        "ci": dispatch_sdk_ci,
        "explorer": dispatch_sdk_explorer,
        "install": _dispatch_sdk_install,
        "rollback": _dispatch_sdk_rollback,
        "uninstall": _dispatch_sdk_uninstall,
        "lifecycle": _dispatch_sdk_lifecycle,
        "status": lambda root, _args: skills_commands.skills_sdk_status(root),
        "knowledge": _dispatch_sdk_knowledge,
        "lenses": _dispatch_sdk_lenses,
        "determinism": _dispatch_sdk_determinism,
        "review": _dispatch_sdk_review,
        "project": _dispatch_sdk_project,
    }
    if args.action in dispatchers:
        return dispatchers[args.action](repo_root, args)
    return build_unknown_action_result("sdk", args.action)


def _dispatch_sdk_ir(repo_root: Path, args: argparse.Namespace) -> CallResult:
    if args.ir_action == "build":
        return skills_commands.skills_sdk_ir_build(repo_root, target=args.target)
    return build_unknown_action_result("sdk ir", args.ir_action)


def _dispatch_sdk_docs(repo_root: Path, args: argparse.Namespace) -> CallResult:
    if args.docs_action == "verify":
        return skills_commands.skills_sdk_docs_verify(repo_root, artifact=args.artifact)
    return build_unknown_action_result("sdk docs", args.docs_action)


def _dispatch_sdk_package(repo_root: Path, args: argparse.Namespace) -> CallResult:
    if args.package_action == "build":
        return skills_commands.skills_sdk_package_build(repo_root, target=args.target)
    if args.package_action == "harden":
        return skills_commands.skills_sdk_package_harden(repo_root, target=args.target)
    if args.package_action == "signing-intent":
        return skills_commands.skills_sdk_package_signing_intent(
            repo_root,
            target=args.target,
            policy=args.policy,
        )
    return build_unknown_action_result("sdk package", args.package_action)


def _dispatch_sdk_sandbox(repo_root: Path, args: argparse.Namespace) -> CallResult:
    if args.sandbox_action == "validate":
        return skills_commands.skills_sdk_sandbox_validate(repo_root, profile=args.profile)
    return build_unknown_action_result("sdk sandbox", args.sandbox_action)


def _dispatch_sdk_trust(repo_root: Path, args: argparse.Namespace) -> CallResult:
    if args.trust_action == "decide":
        if args.preview == args.apply:
            return _validation_error(
                "sdk trust decide",
                "Skills SDK trust decide accepts exactly one of --preview or --apply.",
                "ask sdk trust decide <target> --decision trust --reason <reason> --owner <owner> --preview --json --robot",
            )
        return skills_commands.skills_sdk_trust_decide(
            repo_root,
            target=args.target,
            decision=args.decision,
            reason=args.reason,
            owner=args.owner,
            preview=args.preview,
            apply=args.apply,
            ledger=args.ledger,
            expires_at=args.expires_at,
            revoked_package_digest=args.revoked_package_digest,
        )
    return build_unknown_action_result("sdk trust", args.trust_action)


def _dispatch_sdk_observability(repo_root: Path, args: argparse.Namespace) -> CallResult:
    if args.observability_action == "feedback":
        if not args.preview:
            return _validation_error("sdk observability feedback", "Skills SDK observability feedback is preview-only in PU-026.", "ask sdk observability feedback --skill <target> --events <events.jsonl> --preview --json --robot")
        return skills_commands.skills_sdk_observability_feedback(repo_root, target=args.skill, events=args.events)
    return build_unknown_action_result("sdk observability", args.observability_action)


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
