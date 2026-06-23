from __future__ import annotations

import argparse
from pathlib import Path

from ask.cli_errors import build_unknown_action_result
from ask.envelope import CallResult, ErrorObject
from ask.commands.sdk_receipts import receipt_result
from ask.skills_sdk.knowledge_durability import build_knowledge_durability_receipt
from ask.skills_sdk.knowledge_ingest import build_knowledge_ingest


def add_sdk_knowledge_parser(
    sdk_subparsers: argparse._SubParsersAction,
    global_parser: argparse.ArgumentParser,
) -> None:
    parser = sdk_subparsers.add_parser(
        "knowledge",
        help="Vendor portable knowledge bundles into skill packages",
        parents=[global_parser],
    )
    subparsers = parser.add_subparsers(dest="knowledge_action", required=True)
    _add_ingest_parser(subparsers, global_parser)
    _add_durability_parser(subparsers, global_parser)


def dispatch_sdk_knowledge(repo_root: Path, args: argparse.Namespace) -> CallResult:
    if args.knowledge_action == "ingest":
        return _dispatch_ingest(repo_root, args)
    if args.knowledge_action == "durability":
        return _dispatch_durability(repo_root, args)
    return build_unknown_action_result("sdk knowledge", args.knowledge_action)


def _add_ingest_parser(
    subparsers: argparse._SubParsersAction,
    global_parser: argparse.ArgumentParser,
) -> None:
    ingest = subparsers.add_parser(
        "ingest",
        help="Validate and vendor a KnowledgeOS extraction into a skill package",
        parents=[global_parser],
    )
    ingest.add_argument("--extraction", required=True, help="KnowledgeOS extraction directory")
    ingest.add_argument("--skill", required=True, help="Repo-local skill directory or SKILL.md")
    ingest.add_argument("--preview", action="store_true", help="Validate and report writes without mutating")
    ingest.add_argument("--apply", action="store_true", help="Vendor references and update skill routing")
    ingest.add_argument("--run-proof", action="store_true", help="Run package audit and verify after apply")


def _add_durability_parser(
    subparsers: argparse._SubParsersAction,
    global_parser: argparse.ArgumentParser,
) -> None:
    durability = subparsers.add_parser(
        "durability",
        help="Preview durable-source coverage for KnowledgeOS skill references",
        parents=[global_parser],
    )
    durability.add_argument("--skill", required=True, help="Repo-local skill directory or SKILL.md")
    durability.add_argument("--preview", action="store_true", help="Emit a non-mutating durability receipt")


def _dispatch_ingest(repo_root: Path, args: argparse.Namespace) -> CallResult:
    error = _ingest_argument_error(args)
    if error:
        return error
    try:
        payload = build_knowledge_ingest(
            repo_root,
            extraction=args.extraction,
            skill=args.skill,
            apply=args.apply,
            run_proof=args.run_proof,
        )
    except ValueError as exc:
        return _validation_error(
            "sdk knowledge ingest",
            str(exc),
            "Check that --extraction is a KnowledgeOS extraction with references/ and --skill is repo-local.",
        )
    return _ingest_result(payload)


def _dispatch_durability(repo_root: Path, args: argparse.Namespace) -> CallResult:
    if not args.preview:
        return _validation_error(
            "sdk knowledge durability",
            "Skills SDK knowledge durability checks are preview-only.",
            "ask sdk knowledge durability --skill <skill-path> --preview --json --robot",
        )
    return receipt_result(
        "sdk knowledge durability --preview",
        "skills_sdk_knowledge_durability",
        build_knowledge_durability_receipt(repo_root, skill=args.skill),
        blocked_statuses={"blocked"},
        fix_suggestion="Apply KnowledgeOS references to the durable plugin source, then rebuild or refresh cache.",
    )


def _ingest_argument_error(args: argparse.Namespace) -> CallResult | None:
    if args.preview == args.apply:
        return _validation_error(
            "sdk knowledge ingest",
            "Skills SDK knowledge ingest requires exactly one of --preview or --apply.",
            "ask sdk knowledge ingest --extraction <KnowledgeOS extraction> --skill <skill path> --preview --json --robot.",
        )
    if args.run_proof and not args.apply:
        return _validation_error(
            "sdk knowledge ingest",
            "--run-proof is only valid with --apply.",
            "Run knowledge ingest with --apply --run-proof or drop --run-proof for preview.",
        )
    return None


def _ingest_result(payload: dict) -> CallResult:
    result = CallResult(status="success")
    result.metadata["command"] = "sdk knowledge ingest"
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


def _validation_error(command: str, message: str, fix_suggestion: str) -> CallResult:
    result = CallResult(status="error")
    result.metadata["command"] = command
    result.errors.append(ErrorObject(code="ERR_VALIDATION", message=message, fix_suggestion=fix_suggestion))
    return result
