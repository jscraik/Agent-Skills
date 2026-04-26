from pathlib import Path
from typing import Any

from ask.commands.skills import skills_budget
from ask.envelope import CallResult, ErrorCode, ErrorObject


def add_runtime_parser(subparsers: Any, global_parser: Any) -> None:
    """
    Register the `runtime` CLI command with `surface` and `budget` subactions and their options.
    
    Parameters:
        subparsers (Any): The argparse subparsers object used to add the top-level `runtime` command.
        global_parser (Any): A parser whose options are inherited by the `runtime` command and its subcommands.
    """
    runtime_parser = subparsers.add_parser("runtime", help="Runtime projection reports", parents=[global_parser])
    runtime_subparsers = runtime_parser.add_subparsers(dest="action")
    for action, help_text in (
        ("surface", "Report the current runtime skill surface"),
        ("budget", "Verify the runtime context budget"),
    ):
        action_parser = runtime_subparsers.add_parser(action, help=help_text, parents=[global_parser])
        action_parser.add_argument("--default-max", type=int, default=30, help="Maximum default-visible skills")


def dispatch_runtime(repo_root: Path, args: Any) -> CallResult:
    """
    Dispatch the `runtime` CLI action and return a standardized CallResult.
    
    Calls the skills_budget check when `args.action` is "surface" or "budget", and if that result contains a `runtime_budget` entry, also exposes it as `runtime_surface` in the returned data. For any missing or unrecognized action, returns an error CallResult containing a validation ErrorObject with a fix suggestion.
    
    Parameters:
        repo_root (Path): Filesystem path to the repository root used by the skills check.
        args (Any): Parsed CLI namespace; expected attributes:
            - action: the runtime subcommand action (e.g., "surface" or "budget").
            - default_max: integer limit passed to the skills_budget call.
    
    Returns:
        CallResult: The result from `skills_budget` (possibly augmented with `runtime_surface`) when action is "surface" or "budget"; otherwise an error CallResult with `ErrorCode.ERR_VALIDATION`.
    """
    if args.action in {"surface", "budget"}:
        result = skills_budget(repo_root, default_max=args.default_max)
        if "runtime_budget" in result.data:
            result.data["runtime_surface"] = result.data["runtime_budget"]
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
