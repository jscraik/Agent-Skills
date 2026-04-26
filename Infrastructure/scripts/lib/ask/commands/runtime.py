from pathlib import Path
from typing import Any

from ask.commands.skills import skills_budget
from ask.envelope import CallResult, ErrorCode, ErrorObject


def add_runtime_parser(subparsers: Any, global_parser: Any) -> None:
    runtime_parser = subparsers.add_parser("runtime", help="Runtime projection reports", parents=[global_parser])
    runtime_subparsers = runtime_parser.add_subparsers(dest="action")
    for action, help_text in (
        ("surface", "Report the current runtime skill surface"),
        ("budget", "Verify the runtime context budget"),
    ):
        action_parser = runtime_subparsers.add_parser(action, help=help_text, parents=[global_parser])
        action_parser.add_argument("--default-max", type=int, default=30, help="Maximum default-visible skills")


def dispatch_runtime(repo_root: Path, args: Any) -> CallResult:
    if args.action in {"surface", "budget"}:
        result = skills_budget(repo_root, default_max=args.default_max)
        if "runtime_budget" in result.data:
            result.data["runtime_surface"] = dict(result.data["runtime_budget"])
        if args.action == "surface":
            result.data["runtime_surface_status"] = result.status
            only_validation_errors = (
                result.status == "error"
                and bool(result.errors)
                and all(error.code == ErrorCode.ERR_VALIDATION for error in result.errors)
            )
            if only_validation_errors:
                result.status = "success"
                result.errors = []
        return result

    result = CallResult()
    action_msg = f"unknown action '{args.action}'" if args.action else "missing action"
    result.status = "error"
    result.errors.append(
        ErrorObject(
            code=ErrorCode.ERR_VALIDATION,
            message=f"{action_msg} for topic 'runtime'",
            fix_suggestion="Valid actions: surface, budget",
        )
    )
    return result
