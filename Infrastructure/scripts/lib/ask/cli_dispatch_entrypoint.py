"""Top-level command dispatch for the ask CLI."""

from argparse import ArgumentParser, Namespace
from dataclasses import dataclass
from pathlib import Path
import sys
import time

from ask.cli_dispatch_auxiliary import (
    dispatch_graph,
    dispatch_mcp,
    dispatch_memory,
    dispatch_reviewers,
)
from ask.cli_dispatch_evals import dispatch_evals
from ask.cli_dispatch_plugins import dispatch_plugins
from ask.cli_dispatch_repo import dispatch_repo
from ask.cli_dispatch_skills import dispatch_skills
from ask.cli_dispatch_wiki import dispatch_wiki
from ask.cli_errors import build_unknown_action_result
from ask.commands.runtime import dispatch_runtime
from ask.commands.sdk import dispatch_sdk
from ask.commands.workouts import dispatch_workouts
from ask.envelope import CallResult
from ask.phoenix_auto_trace import maybe_emit_phoenix_trace


@dataclass(frozen=True)
class DispatchRequest:
    """Inputs that remain coupled for one top-level CLI dispatch."""

    parser: ArgumentParser
    repo_root: Path
    args: Namespace
    raw_args: list[str]
    correction_note: str | None
    result: CallResult
    start_time: float


def dispatch_command(request: DispatchRequest):
    """Dispatch one parsed CLI request and attach common receipt metadata."""
    result = _dispatch_topic(
        request.parser,
        request.repo_root,
        request.args,
        request.raw_args,
        request.result,
    )
    _attach_result_metadata(
        request.args,
        request.correction_note,
        result,
        request.start_time,
    )
    maybe_emit_phoenix_trace(request.repo_root, request.args, result)
    return result


def _dispatch_topic(parser, repo_root, args, raw_args, result):
    """Select the bounded dispatcher that owns the parsed topic."""
    if args.topic is None:
        return result
    handlers = {
        "repo": lambda: dispatch_repo(repo_root, args),
        "skills": lambda: dispatch_skills(parser, repo_root, args, raw_args),
        "reviewers": lambda: dispatch_reviewers(repo_root, args),
        "sdk": lambda: dispatch_sdk(repo_root, args),
        "runtime": lambda: dispatch_runtime(repo_root, args),
        "plugins": lambda: dispatch_plugins(repo_root, args),
        "evals": lambda: dispatch_evals(repo_root, args),
        "workouts": lambda: dispatch_workouts(repo_root, args),
        "graph": lambda: dispatch_graph(repo_root, args),
        "mcp": lambda: dispatch_mcp(repo_root, args),
        "memory": lambda: dispatch_memory(repo_root, args),
        "wiki": lambda: dispatch_wiki(repo_root, args, result),
    }
    handler = handlers.get(args.topic)
    return (
        handler() if handler else build_unknown_action_result(args.topic, args.action)
    )


def _attach_result_metadata(args, correction_note, result, start_time):
    """Attach metadata shared by every command result."""
    result.metadata["command"] = " ".join(sys.argv[1:])
    if correction_note:
        result.metadata["correction_note"] = correction_note.replace("\n", " ")
    result.telemetry["latency_ms"] = int((time.time() - start_time) * 1000)
    if args.trace_id:
        result.trace_id = args.trace_id
