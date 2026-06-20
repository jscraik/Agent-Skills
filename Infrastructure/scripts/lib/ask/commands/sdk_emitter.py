from __future__ import annotations

import argparse
from pathlib import Path

import ask.commands.skills as skills_commands
from ask.envelope import CallResult, ErrorObject
from ask.cli_errors import build_unknown_action_result


def add_sdk_emitter_parser(
    sdk_subparsers: argparse._SubParsersAction,
    global_parser: argparse.ArgumentParser,
) -> None:
    parser = sdk_subparsers.add_parser(
        "emitter",
        help="Preview Skills SDK generated-output write plans",
        parents=[global_parser],
    )
    subparsers = parser.add_subparsers(dest="emitter_action", required=True)
    preview = subparsers.add_parser(
        "preview",
        help="Plan a local runtime projection write without emitting files",
        parents=[global_parser],
    )
    preview.add_argument("--skill", required=True, help="Skill handle or repo-relative skill source path")
    preview.add_argument(
        "--projection",
        choices=["runtime-skill"],
        default="runtime-skill",
        help="Projection contract to preview",
    )
    preview.add_argument(
        "--target-root",
        default=".agents/skills",
        help="Local projection root. PU-027 only supports .agents/skills.",
    )
    preview.add_argument("--preview", action="store_true", help="Emit a non-mutating write-plan receipt")


def dispatch_sdk_emitter(repo_root: Path, args: argparse.Namespace) -> CallResult:
    if args.emitter_action == "preview":
        if not args.preview:
            return _validation_error(
                "sdk emitter preview",
                "Skills SDK emitter preview is non-mutating and requires --preview in PU-027.",
                "ask sdk emitter preview --skill <target> --preview --json --robot",
            )
        return skills_commands.skills_sdk_emitter_preview(
            repo_root,
            target=args.skill,
            projection=args.projection,
            target_root=args.target_root,
        )
    return build_unknown_action_result("sdk emitter", args.emitter_action)


def _validation_error(command: str, message: str, fix_suggestion: str) -> CallResult:
    result = CallResult(status="error")
    result.metadata["command"] = command
    result.errors.append(
        ErrorObject(code="ERR_VALIDATION", message=message, fix_suggestion=fix_suggestion)
    )
    return result
