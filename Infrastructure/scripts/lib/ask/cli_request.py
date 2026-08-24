"""Argument preparation and recovery for the Ask command-line facade."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass

from ask.cli_args import prepare_args
from ask.cli_errors import (
    _merge_corrections,
    build_argument_error,
    build_helpful_error,
    parse_args_with_capture,
    try_fuzzy_parse,
)
from ask.cli_output import print_first_validation_command
from ask.command_metadata import VALID_ACTIONS, VALID_TOPICS
from ask.envelope import CallResult, ErrorCode, ErrorObject


@dataclass(frozen=True)
class ParsedCommand:
    """The normalized command and parser result used by the facade."""

    args: argparse.Namespace
    raw_args: list[str]
    correction_note: str | None


def _emit_parse_result(
    result: CallResult, raw_args: list[str], correction_note: str | None
) -> None:
    result.metadata["command"] = " ".join(sys.argv[1:])
    if correction_note:
        result.metadata["correction_note"] = correction_note.replace("\n", " ")
    if "--json" in raw_args:
        print(result.to_json())
        return
    if correction_note:
        print(f"{correction_note}\n")
    print(result.errors[0].message)
    print_first_validation_command(result.data)


def _failed_parse_result(
    topic: str | None,
    action: str | None,
    raw_args: list[str],
    parser_stderr: str,
) -> CallResult:
    is_known_command = topic in VALID_TOPICS and action in VALID_ACTIONS.get(topic, [])
    factory = build_argument_error if is_known_command else build_helpful_error
    return factory(topic, action, raw_args, parser_error=parser_stderr)


def _parse_robot_recovery(
    parser: argparse.ArgumentParser,
    raw_args: list[str],
    correction_note: str | None,
    parser_stderr: str,
) -> tuple[argparse.Namespace, str | None]:
    topic, action, remaining_args, fuzzy_note = try_fuzzy_parse(
        raw_args, robot_mode=True
    )
    correction_note = _merge_corrections(correction_note, fuzzy_note)
    if topic not in VALID_TOPICS or action not in VALID_ACTIONS.get(topic, []):
        _emit_parse_result(
            _failed_parse_result(topic, action, raw_args, parser_stderr),
            raw_args,
            correction_note,
        )
        raise SystemExit(2)
    parsed, exit_code, corrected_stderr = parse_args_with_capture(
        parser, [topic, action, *remaining_args]
    )
    if parsed is not None:
        return parsed, correction_note
    if exit_code == 0:
        raise SystemExit(0)
    result = build_argument_error(
        topic, action, raw_args, parser_error=corrected_stderr or parser_stderr
    )
    _emit_parse_result(result, raw_args, correction_note)
    raise SystemExit(2)


def _parse_human_recovery(raw_args: list[str], parser_stderr: str) -> None:
    topic, action, _, _ = try_fuzzy_parse(raw_args, robot_mode=False)
    _emit_parse_result(
        _failed_parse_result(topic, action, raw_args, parser_stderr), raw_args, None
    )
    raise SystemExit(2)


def _failed_argument_result(raw_args: list[str]) -> None:
    result = CallResult(status="error")
    result.errors.append(
        ErrorObject(
            code=ErrorCode.ERR_VALIDATION,
            message="Failed to parse command arguments.",
            fix_suggestion="Check command format and try again.",
        )
    )
    if "--json" in raw_args:
        print(result.to_json())
    else:
        print("❌ Failed to parse command arguments.")
    raise SystemExit(2)


def parse_command(parser: argparse.ArgumentParser) -> ParsedCommand:
    """Prepare, parse, and recover the current command-line invocation."""
    prepared = prepare_args(sys.argv[1:])
    if not prepared.filtered_args or prepared.filtered_args[0] in ("-h", "--help"):
        parser.print_help()
        raise SystemExit(0)
    args, exit_code, parser_stderr = parse_args_with_capture(parser, prepared.raw_args)
    correction_note = prepared.alias_correction_note
    if args is None and exit_code == 0:
        raise SystemExit(0)
    if args is None and prepared.robot_mode:
        args, correction_note = _parse_robot_recovery(
            parser, prepared.raw_args, correction_note, parser_stderr
        )
    if args is None:
        _parse_human_recovery(prepared.raw_args, parser_stderr)
    if args is None:
        _failed_argument_result(prepared.raw_args)
    return ParsedCommand(
        args=args, raw_args=prepared.raw_args, correction_note=correction_note
    )
