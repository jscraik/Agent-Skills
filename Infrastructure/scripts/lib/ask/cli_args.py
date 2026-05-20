from __future__ import annotations

import argparse
import os
from dataclasses import dataclass

from ask.cli_errors import _normalize_token, consume_global_prefix_flags


ROBOT_FLAGS = {"--robot", "--agent-mode", "-r"}


@dataclass(frozen=True)
class PreparedArgs:
    raw_args: list[str]
    filtered_args: list[str]
    alias_correction_note: str | None
    robot_mode: bool


def prepare_args(raw_args: list[str]) -> PreparedArgs:
    alias_correction_note = None
    prefix_flags, positional_args = consume_global_prefix_flags(raw_args)
    first_positional = _normalize_token(positional_args[0]) if positional_args else None
    second_positional = _normalize_token(positional_args[1]) if len(positional_args) > 1 else None
    if first_positional == "goal":
        raw_args = [*prefix_flags, "skills", "goal", *positional_args[1:]]
        alias_correction_note = "💡 Alias: 'ask goal' maps to 'ask skills goal'."
    elif first_positional == "doctor" and second_positional == "catalog":
        raw_args = [*prefix_flags, "repo", "doctor-catalog", *positional_args[2:]]
        alias_correction_note = "💡 Alias: 'ask doctor catalog' maps to 'ask repo doctor-catalog'."
    return PreparedArgs(
        raw_args=raw_args,
        filtered_args=[arg for arg in raw_args if arg not in ROBOT_FLAGS],
        alias_correction_note=alias_correction_note,
        robot_mode=any(flag in raw_args for flag in ROBOT_FLAGS),
    )


def build_global_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--json", action="store_true", help="Output results in JSON format for programmatic use")
    parser.add_argument("--trace-id", help="Trace ID for correlating logs", default=os.environ.get("ASK_TRACE_ID"))
    parser.add_argument(
        "--robot",
        "--agent-mode",
        "-r",
        dest="robot_mode",
        action="store_true",
        help="AI-agent mode: honors clear intent despite minor syntax issues, emits correction notes, and returns detailed guided errors on ambiguity",
    )
    return parser
