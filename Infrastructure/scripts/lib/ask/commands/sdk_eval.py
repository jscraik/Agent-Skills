from __future__ import annotations

import argparse
from pathlib import Path

import ask.commands.skills as skills_commands
from ask.cli_errors import build_unknown_action_result
from ask.envelope import CallResult, ErrorObject


def add_sdk_eval_parser(
    sdk_subparsers: argparse._SubParsersAction,
    global_parser: argparse.ArgumentParser,
) -> None:
    parser = sdk_subparsers.add_parser("eval", help="Run Skills SDK eval receipts", parents=[global_parser])
    subparsers = parser.add_subparsers(dest="eval_action", required=True)
    run = subparsers.add_parser(
        "run",
        help="Run internal skill evals or exact-match deterministic eval cases",
        parents=[global_parser],
    )
    run.add_argument("target", nargs="?", help="Skill handle or source path for the internal eval runner")
    run.add_argument("--dataset", help="Repo-relative or absolute deterministic eval dataset")
    run.add_argument("--skill", help="Optional skill handle or source path for deterministic evals")
    run.add_argument(
        "--runner",
        choices=["auto", "internal", "deterministic-jsonl"],
        default="auto",
        help="Eval backend. auto uses deterministic-jsonl with --dataset, otherwise internal.",
    )
    run.add_argument("--mode", choices=["smoke", "release"], default="smoke", help="Internal eval mode.")
    run.add_argument("--case", action="append", dest="cases", help="Internal eval case id filter.")
    run.add_argument("--with-tessl", action="store_true", help="Allow internal Tessl continuation.")
    quality = subparsers.add_parser(
        "scenario-quality",
        help="Preview eval scenario promotion quality for a skill",
        parents=[global_parser],
    )
    quality.add_argument("target", help="Skill handle or repo-relative skill source path")
    quality.add_argument("--preview", action="store_true", help="Emit a non-mutating scenario quality receipt")


def dispatch_sdk_eval(repo_root: Path, args: argparse.Namespace) -> CallResult:
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
    if args.eval_action == "scenario-quality":
        if not args.preview:
            return _validation_error(
                "sdk eval scenario-quality",
                "Skills SDK scenario quality is preview-only in PU-030 and requires --preview.",
                "ask sdk eval scenario-quality <skill> --preview --json --robot",
            )
        return skills_commands.skills_sdk_eval_scenario_quality(repo_root, target=args.target)
    return build_unknown_action_result("sdk eval", args.eval_action)


def _validation_error(command: str, message: str, fix_suggestion: str) -> CallResult:
    result = CallResult(status="error")
    result.metadata["command"] = command
    result.errors.append(ErrorObject(code="ERR_VALIDATION", message=message, fix_suggestion=fix_suggestion))
    return result
