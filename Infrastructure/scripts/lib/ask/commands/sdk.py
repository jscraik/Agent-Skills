from __future__ import annotations

import argparse
from pathlib import Path

import ask.commands.skills as skills_commands
from ask.command_metadata import SDK_AUTHOR_FACING_ACTIONS
from ask.envelope import CallResult, ErrorObject
from ask.cli_errors import build_unknown_action_result
from ask.cli_args import FacadeActionChoices, facade_help_action
from ask.commands.sdk_ci import add_sdk_ci_parser, dispatch_sdk_ci
from ask.commands.sdk_emitter import add_sdk_emitter_parser, dispatch_sdk_emitter
from ask.commands.sdk_eval import add_sdk_eval_parser, dispatch_sdk_eval
from ask.commands.sdk_evidence import (
    add_sdk_evidence_parser,
    add_sdk_route_map_parser,
    dispatch_sdk_evidence,
    dispatch_sdk_route_map,
)
from ask.commands.sdk_explorer import add_sdk_explorer_parser, dispatch_sdk_explorer
from ask.commands.sdk_intake import add_sdk_intake_parser, dispatch_sdk_intake
from ask.commands.sdk_knowledge import add_sdk_knowledge_parser, dispatch_sdk_knowledge
from ask.commands.sdk_plugin import add_sdk_plugin_parser, dispatch_sdk_plugin
from ask.commands.sdk_security import add_sdk_security_parser, dispatch_sdk_security
from ask.commands.sdk_dispatch_surfaces import (
    _dispatch_sdk_lenses,
    _dispatch_sdk_observability,
    _dispatch_sdk_review,
    _dispatch_sdk_score,
)
from ask.commands.sdk_surface_parsers import (
    add_determinism_parser,
    add_lenses_parser,
    add_lifecycle_status_parsers,
    add_project_mutation_parsers,
    add_project_parser,
    add_review_parser,
)
from ask.skills_sdk.determinism import audit_skill_determinism
from ask.skills_sdk.local_score import (
    LOCAL_SCORE_GATES,
)


DEFAULT_SDK_ACTIONS = SDK_AUTHOR_FACING_ACTIONS


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
    parser = sdk_subparsers.add_parser("observability", help="Preview redacted runtime feedback and Phoenix evidence mirrors", parents=[global_parser])
    subparsers = parser.add_subparsers(dest="observability_action", required=True)
    feedback = subparsers.add_parser("feedback", help="Mine redacted event JSONL into blocked eval and skill-gap candidates", parents=[global_parser])
    feedback.add_argument("--skill", required=True, help="Skill handle or repo-relative skill source path")
    feedback.add_argument("--events", required=True, help="Repo-relative or temporary redacted events JSONL")
    feedback.add_argument("--preview", action="store_true", help="Emit a non-mutating feedback receipt")

    promote = subparsers.add_parser("promote", help="Preview feedback candidate promotion against package and eval receipts", parents=[global_parser])
    promote.add_argument("--feedback-receipt", required=True, help="Repo-relative or temporary observability feedback receipt JSON")
    promote.add_argument("--package-receipt", required=True, help="Repo-relative or temporary package digest receipt JSON")
    promote.add_argument("--eval-run-receipt", required=True, help="Repo-relative or temporary eval run receipt JSON")
    promote.add_argument("--preview", action="store_true", help="Emit a non-mutating promotion receipt")

    phoenix_status = subparsers.add_parser("phoenix-status", help="Check the Phoenix OSS service endpoint used for eval observability", parents=[global_parser])
    phoenix_status.add_argument("--base-url", default="http://localhost:6006", help="Phoenix UI base URL")
    phoenix_status.add_argument("--timeout-seconds", type=float, default=2.0, help="HTTP timeout for the Phoenix status check")

    phoenix_smoke = subparsers.add_parser("phoenix-smoke", help="Emit a deterministic Phoenix OSS smoke trace", parents=[global_parser])
    phoenix_smoke.add_argument("--base-url", default="http://localhost:6006", help="Phoenix UI base URL")
    phoenix_smoke.add_argument("--profile", choices=["oss-local", "oss-cloud"], default="oss-local", help="OSS Codex profile to attach to the smoke span")
    phoenix_smoke.add_argument("--otel-python", help="Python executable with opentelemetry-proto installed; defaults to ~/.agents/otel-collector/.venv/bin/python")
    phoenix_smoke.add_argument("--model", help="Optional LLM model name to attach for Phoenix model metrics")
    phoenix_smoke.add_argument("--provider", help="Optional LLM provider/system to attach with --model")
    phoenix_smoke.add_argument("--prompt-tokens", type=int, default=0, help="Prompt/input token count for --model smoke traces")
    phoenix_smoke.add_argument("--completion-tokens", type=int, default=0, help="Completion/output token count for --model smoke traces")
    phoenix_smoke.add_argument("--timeout-seconds", type=float, default=10.0, help="HTTP timeout for the Phoenix OTLP export")

    phoenix_mirror = subparsers.add_parser("phoenix-mirror", help="Mirror an eval or observability receipt into redacted Phoenix-ready JSONL", parents=[global_parser])
    phoenix_mirror.add_argument("--receipt", required=True, help="Repo-relative or temporary eval/observability receipt JSON")
    phoenix_mirror.add_argument("--out", help="Repo-relative or temporary JSONL output path")
    phoenix_mirror.add_argument("--preview", action="store_true", help="Emit a non-mutating mirror receipt")
    phoenix_mirror.add_argument("--write", action="store_true", help="Write the redacted JSONL mirror to --out")


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


def _add_sdk_score_parser(
    sdk_subparsers: argparse._SubParsersAction,
    global_parser: argparse.ArgumentParser,
) -> None:
    parser = sdk_subparsers.add_parser("score", help="Build local Skills SDK score receipts", parents=[global_parser])
    subparsers = parser.add_subparsers(dest="score_action", required=True)
    local = subparsers.add_parser("local", help="Build a local Quality/Impact/Security score receipt", parents=[global_parser])
    local.add_argument("target", help="Skill handle or repo-relative skill source path")
    local.add_argument("--gate", choices=LOCAL_SCORE_GATES, default="creation")
    local.add_argument("--ttl-seconds", type=int, default=300)
    local.add_argument("--write-current", action="store_true", help="Write current.json plus immutable history for SkillsBar consumption")


def _add_sdk_start_parser(
    sdk_subparsers: argparse._SubParsersAction,
    global_parser: argparse.ArgumentParser,
) -> None:
    parser = sdk_subparsers.add_parser(
        "start",
        help="Classify a skill target and emit the next Skills SDK lifecycle command",
        parents=[global_parser],
    )
    parser.add_argument("target", help="Skill handle, source path, or project-local SKILL.md path")
    parser.add_argument("--project-root", help="Absolute owner project root for project-local skills")


def add_sdk_parser(
    subparsers: argparse._SubParsersAction,
    global_parser: argparse.ArgumentParser,
) -> None:
    sdk_parser = subparsers.add_parser("sdk", help="Skills SDK product facade", parents=[global_parser])
    sdk_subparsers = sdk_parser.add_subparsers(
        dest="action",
        action=facade_help_action(DEFAULT_SDK_ACTIONS),
    )
    sdk_subparsers.metavar = "{" + ",".join(DEFAULT_SDK_ACTIONS) + "}"
    _add_sdk_start_parser(sdk_subparsers, global_parser)
    _add_sdk_check_parser(sdk_subparsers, global_parser)
    _add_sdk_score_parser(sdk_subparsers, global_parser)
    _add_sdk_ir_parser(sdk_subparsers, global_parser)
    _add_sdk_docs_parser(sdk_subparsers, global_parser)
    add_sdk_evidence_parser(sdk_subparsers, global_parser)
    add_sdk_route_map_parser(sdk_subparsers, global_parser)
    add_sdk_eval_parser(sdk_subparsers, global_parser)
    _add_sdk_package_parser(sdk_subparsers, global_parser)
    _add_sdk_sandbox_parser(sdk_subparsers, global_parser)
    add_sdk_intake_parser(sdk_subparsers, global_parser)
    _add_sdk_trust_parser(sdk_subparsers, global_parser)
    _add_sdk_observability_parser(sdk_subparsers, global_parser)
    add_sdk_emitter_parser(sdk_subparsers, global_parser)
    add_sdk_ci_parser(sdk_subparsers, global_parser)
    add_sdk_explorer_parser(sdk_subparsers, global_parser)
    add_sdk_security_parser(sdk_subparsers, global_parser)
    add_sdk_plugin_parser(sdk_subparsers, global_parser)
    add_project_mutation_parsers(sdk_subparsers, global_parser)
    add_lifecycle_status_parsers(sdk_subparsers, global_parser)
    add_sdk_knowledge_parser(sdk_subparsers, global_parser)
    add_project_parser(sdk_subparsers, global_parser)
    add_lenses_parser(sdk_subparsers, global_parser)
    add_determinism_parser(sdk_subparsers, global_parser)
    add_review_parser(sdk_subparsers, global_parser)
    sdk_subparsers.choices = FacadeActionChoices(
        sdk_subparsers._name_parser_map,
        DEFAULT_SDK_ACTIONS,
    )


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


def _dispatch_sdk_start(repo_root: Path, args: argparse.Namespace) -> CallResult:
    return skills_commands.skills_sdk_start(
        repo_root,
        target=args.target,
        project_root=args.project_root,
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


def _dispatch_sdk_improve(repo_root: Path, args: argparse.Namespace) -> CallResult:
    if args.preview == args.apply:
        return _validation_error(
            "sdk improve",
            "Skills SDK improve requires exactly one of --preview or --apply.",
            "ask sdk improve <project-skill> --project-root /path/to/project --preview --json --robot",
        )
    return skills_commands.skills_sdk_project_improve(
        repo_root,
        target=args.target,
        project_root=args.project_root,
        run_evals=args.evals,
        mode=args.mode,
        codex_profile=args.codex_profile,
        apply=args.apply,
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
        "start": _dispatch_sdk_start,
        "check": _dispatch_sdk_check,
        "score": _dispatch_sdk_score,
        "ir": _dispatch_sdk_ir,
        "docs": _dispatch_sdk_docs,
        "evidence": dispatch_sdk_evidence,
        "route-map": dispatch_sdk_route_map,
        "eval": dispatch_sdk_eval,
        "package": _dispatch_sdk_package,
        "sandbox": _dispatch_sdk_sandbox,
        "intake": dispatch_sdk_intake,
        "trust": _dispatch_sdk_trust,
        "observability": _dispatch_sdk_observability,
        "emitter": dispatch_sdk_emitter,
        "ci": dispatch_sdk_ci,
        "explorer": dispatch_sdk_explorer,
        "security": dispatch_sdk_security,
        "plugin": dispatch_sdk_plugin,
        "improve": _dispatch_sdk_improve,
        "install": _dispatch_sdk_install,
        "rollback": _dispatch_sdk_rollback,
        "uninstall": _dispatch_sdk_uninstall,
        "lifecycle": _dispatch_sdk_lifecycle,
        "status": lambda root, _args: skills_commands.skills_sdk_status(root),
        "knowledge": dispatch_sdk_knowledge,
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
