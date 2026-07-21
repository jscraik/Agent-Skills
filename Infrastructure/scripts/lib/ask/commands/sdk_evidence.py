from __future__ import annotations

import argparse
from pathlib import Path

import ask.commands.skills as skills_commands
from ask.cli_errors import build_unknown_action_result
from ask.envelope import CallResult, ErrorObject
from ask.commands.sdk_receipts import receipt_result
from ask.skills_sdk.command_evidence_plan import build_command_evidence_plan_receipt
from ask.skills_sdk.evidence_status import EvidenceStatusError, build_evidence_status_receipt
from ask.skills_sdk.lifecycle_route_map import build_lifecycle_route_map_receipt


def add_sdk_evidence_parser(
    sdk_subparsers: argparse._SubParsersAction,
    global_parser: argparse.ArgumentParser,
) -> None:
    parser = sdk_subparsers.add_parser(
        "evidence",
        help="Verify Skills SDK evidence references without crossing external proof lanes",
        parents=[global_parser],
    )
    subparsers = parser.add_subparsers(dest="evidence_action", required=True)
    verify = subparsers.add_parser(
        "verify",
        help="Verify capability matrix evidence refs as files, schemas, receipts, commands, or external lanes",
        parents=[global_parser],
    )
    verify.add_argument("--scope", choices=["capability-matrix"], default="capability-matrix")
    command_plan = subparsers.add_parser(
        "command-plan",
        help="Preview replayable command evidence refs without executing them",
        parents=[global_parser],
    )
    command_plan.add_argument("--scope", choices=["capability-matrix"], default="capability-matrix")
    command_plan.add_argument("--preview", action="store_true", help="Emit a non-mutating command evidence plan receipt")
    status = subparsers.add_parser(
        "status",
        help="Report independent local-build, acceptance, and integration evidence lanes",
        parents=[global_parser],
    )
    status.add_argument("--mode", choices=["local-build", "acceptance", "integration", "all"], default="all")
    status.add_argument(
        "--require",
        choices=["local-build", "acceptance", "integration"],
        help="Select one lane's status while still reporting the other lanes",
    )
    status.add_argument("--receipt", help="Optional revision-bound stabilization receipt path")
    status.add_argument("--qa-dispatch-record", help="Optional controller-owned QA dispatch record path")


def add_sdk_route_map_parser(
    sdk_subparsers: argparse._SubParsersAction,
    global_parser: argparse.ArgumentParser,
) -> None:
    parser = sdk_subparsers.add_parser(
        "route-map",
        help="Preview the SDK lifecycle route map from command to schema, test, and proof boundary",
        parents=[global_parser],
    )
    parser.add_argument("--preview", action="store_true", help="Emit a non-mutating lifecycle route map receipt")


def dispatch_sdk_evidence(repo_root: Path, args: argparse.Namespace) -> CallResult:
    if args.evidence_action == "verify":
        return skills_commands.skills_sdk_capability_evidence(repo_root, scope=args.scope)
    if args.evidence_action == "command-plan":
        return _dispatch_command_plan(repo_root, args)
    if args.evidence_action == "status":
        return _dispatch_status(repo_root, args)
    return build_unknown_action_result("sdk evidence", args.evidence_action)


def dispatch_sdk_route_map(repo_root: Path, args: argparse.Namespace) -> CallResult:
    if not args.preview:
        return _validation_error(
            "sdk route-map",
            "Skills SDK lifecycle route map is preview-only.",
            "ask sdk route-map --preview --json --robot",
        )
    return receipt_result(
        "sdk route-map --preview",
        "skills_sdk_lifecycle_route_map",
        build_lifecycle_route_map_receipt(repo_root),
        blocked_statuses={"blocked"},
        fix_suggestion="Inspect receipt.blockers and repair the route map, schemas, or tests.",
    )


def _dispatch_command_plan(repo_root: Path, args: argparse.Namespace) -> CallResult:
    if not args.preview:
        return _validation_error(
            "sdk evidence command-plan",
            "Skills SDK command evidence planning is preview-only.",
            "ask sdk evidence command-plan --scope capability-matrix --preview --json --robot",
        )
    return receipt_result(
        "sdk evidence command-plan --preview",
        "skills_sdk_command_evidence_plan",
        build_command_evidence_plan_receipt(repo_root, scope=args.scope),
        blocked_statuses={"blocked"},
        fix_suggestion="Inspect receipt.commands and run the listed command refs through their own proof lane.",
    )


def _dispatch_status(repo_root: Path, args: argparse.Namespace) -> CallResult:
    # Reject conflicting non-default combinations of --mode and --require
    if args.require is not None and args.mode != "all" and args.mode != args.require:
        return _validation_error(
            "sdk evidence status",
            f"Conflicting selectors: --mode {args.mode} and --require {args.require} do not match. "
            f"Use matching selectors or the default mode=all.",
            "Either use --mode all --require <lane> or --mode <lane> without --require.",
        )

    try:
        receipt = build_evidence_status_receipt(
            repo_root,
            mode=args.mode,
            required_mode=args.require,
            stabilization_receipt_path=args.receipt,
            qa_dispatch_record_path=args.qa_dispatch_record,
        )
    except EvidenceStatusError as exc:
        return _validation_error(
            "sdk evidence status",
            f"Skills SDK evidence status could not be built: {exc}",
            "Inspect the source/receipt binding and rerun ask sdk evidence status --mode all --json --robot.",
        )
    return receipt_result(
        "sdk evidence status",
        "skills_sdk_evidence_status",
        receipt,
        blocked_statuses={"blocked"},
        fix_suggestion=(
            "Select a specific lane with --mode or --require; repair only the blockers in that lane "
            "before crossing into acceptance or integration work."
        ),
    )


def _validation_error(command: str, message: str, fix_suggestion: str) -> CallResult:
    result = CallResult(status="error")
    result.metadata["command"] = command
    result.errors.append(ErrorObject(code="ERR_VALIDATION", message=message, fix_suggestion=fix_suggestion))
    return result
