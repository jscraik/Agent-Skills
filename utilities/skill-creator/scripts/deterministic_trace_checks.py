#!/usr/bin/env python3
"""
Deterministic trace checks for Codex JSONL event streams.

This module provides lightweight, explainable checks for skill eval traces:
- required/forbidden commands
- command ordering
- command count/thrash heuristics
- required/forbidden event types
- token/turn budgets
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


@dataclass
class TokenUsage:
    input_tokens: int = 0
    output_tokens: int = 0
    reasoning_tokens: int = 0
    total_tokens: int = 0


@dataclass
class TraceMetrics:
    event_count: int
    command_count: int
    unique_command_count: int
    duplicate_command_ratio: float
    max_repeated_command_count: int
    turn_count: int
    error_event_count: int
    token_usage: TokenUsage


@dataclass
class DeterministicTraceResult:
    hard_failures: List[str]
    soft_failures: List[str]
    warnings: List[str]
    metrics: TraceMetrics

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["tier1_failures"] = payload.pop("hard_failures")
        payload["tier2_failures"] = payload.pop("soft_failures")
        return payload


def load_jsonl_events(path: Path) -> Tuple[List[Dict[str, Any]], List[str]]:
    events: List[Dict[str, Any]] = []
    warnings: List[str] = []
    if not path.exists():
        return events, [f"JSONL file not found: {path}"]

    for idx, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        text = line.strip()
        if not text:
            continue
        try:
            obj = json.loads(text)
        except json.JSONDecodeError as exc:
            warnings.append(f"Line {idx}: invalid JSON ({exc})")
            continue
        if isinstance(obj, dict):
            events.append(obj)
        else:
            warnings.append(f"Line {idx}: expected JSON object event, got {type(obj).__name__}")
    return events, warnings


def evaluate_trace(
    events: List[Dict[str, Any]],
    deterministic_checks: Optional[Dict[str, Any]] = None,
    budgets: Optional[Dict[str, Any]] = None,
) -> DeterministicTraceResult:
    deterministic_checks = deterministic_checks or {}
    budgets = budgets or {}

    commands = _extract_commands(events)
    event_types = [str(e.get("type", "")) for e in events if isinstance(e, dict)]
    turn_count = sum(1 for e in event_types if e == "turn.started")
    error_count = sum(1 for e in event_types if e == "error")

    unique_commands = len(set(commands))
    duplicate_ratio = 0.0
    max_repeats = 0
    if commands:
        counts: Dict[str, int] = {}
        for c in commands:
            counts[c] = counts.get(c, 0) + 1
        max_repeats = max(counts.values())
        duplicate_ratio = max(0.0, (len(commands) - unique_commands) / float(len(commands)))

    usage = _extract_token_usage(events)

    metrics = TraceMetrics(
        event_count=len(events),
        command_count=len(commands),
        unique_command_count=unique_commands,
        duplicate_command_ratio=round(duplicate_ratio, 4),
        max_repeated_command_count=max_repeats,
        turn_count=turn_count,
        error_event_count=error_count,
        token_usage=usage,
    )

    hard_failures: List[str] = []
    soft_failures: List[str] = []
    warnings: List[str] = []

    # Tier-1 deterministic checks
    for required in _list_of_strings(deterministic_checks.get("required_commands")):
        if not _contains_command(commands, required):
            hard_failures.append(f"required command not found: {required!r}")

    for forbidden in _list_of_strings(deterministic_checks.get("forbidden_commands")):
        if _contains_command(commands, forbidden):
            hard_failures.append(f"forbidden command was executed: {forbidden!r}")

    command_order = _list_of_strings(deterministic_checks.get("command_order"))
    if command_order:
        if not _check_command_order(commands, command_order):
            hard_failures.append(
                "command_order failed: expected sequence "
                + " -> ".join(repr(x) for x in command_order)
            )

    required_events = _list_of_strings(deterministic_checks.get("required_event_types"))
    for evt in required_events:
        if evt not in event_types:
            hard_failures.append(f"required event type not found: {evt!r}")

    forbidden_events = _list_of_strings(deterministic_checks.get("forbidden_event_types"))
    for evt in forbidden_events:
        if evt in event_types:
            hard_failures.append(f"forbidden event type present: {evt!r}")

    min_cmd = _as_int(deterministic_checks.get("min_command_executions"))
    if min_cmd is not None and len(commands) < min_cmd:
        hard_failures.append(
            f"min_command_executions failed: got {len(commands)} < expected {min_cmd}"
        )

    max_cmd = _as_int(deterministic_checks.get("max_command_executions"))
    if max_cmd is not None and len(commands) > max_cmd:
        hard_failures.append(
            f"max_command_executions failed: got {len(commands)} > allowed {max_cmd}"
        )

    max_repeat = _as_int(deterministic_checks.get("max_repeated_command_count"))
    if max_repeat is not None and max_repeats > max_repeat:
        hard_failures.append(
            f"max_repeated_command_count failed: got {max_repeats} > allowed {max_repeat}"
        )

    max_dup_ratio = _as_float(deterministic_checks.get("max_duplicate_command_ratio"))
    if max_dup_ratio is not None and duplicate_ratio > max_dup_ratio:
        hard_failures.append(
            f"max_duplicate_command_ratio failed: got {duplicate_ratio:.3f} > allowed {max_dup_ratio:.3f}"
        )

    # Tier-2 efficiency budgets (warn/fail controlled by caller)
    _check_budget_max(
        soft_failures,
        "max_input_tokens",
        usage.input_tokens,
        budgets,
    )
    _check_budget_max(
        soft_failures,
        "max_output_tokens",
        usage.output_tokens,
        budgets,
    )
    _check_budget_max(
        soft_failures,
        "max_reasoning_tokens",
        usage.reasoning_tokens,
        budgets,
    )
    _check_budget_max(
        soft_failures,
        "max_total_tokens",
        usage.total_tokens,
        budgets,
    )
    _check_budget_max(
        soft_failures,
        "max_turns",
        turn_count,
        budgets,
    )
    _check_budget_max(
        soft_failures,
        "max_command_budget",
        len(commands),
        budgets,
    )

    budget_dup = _as_float(budgets.get("max_duplicate_command_ratio"))
    if budget_dup is not None and duplicate_ratio > budget_dup:
        soft_failures.append(
            f"budget max_duplicate_command_ratio failed: got {duplicate_ratio:.3f} > allowed {budget_dup:.3f}"
        )

    budget_repeat = _as_int(budgets.get("max_repeated_command_count"))
    if budget_repeat is not None and max_repeats > budget_repeat:
        soft_failures.append(
            f"budget max_repeated_command_count failed: got {max_repeats} > allowed {budget_repeat}"
        )

    if not events:
        warnings.append("No events found in JSONL trace.")

    return DeterministicTraceResult(
        hard_failures=hard_failures,
        soft_failures=soft_failures,
        warnings=warnings,
        metrics=metrics,
    )


def _check_budget_max(failures: List[str], key: str, actual: int, budgets: Dict[str, Any]) -> None:
    v = _as_int(budgets.get(key))
    if v is not None and actual > v:
        failures.append(f"budget {key} failed: got {actual} > allowed {v}")


def _as_int(value: Any) -> Optional[int]:
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        try:
            return int(value.strip())
        except ValueError:
            return None
    return None


def _as_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            return None
    return None


def _list_of_strings(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        out: List[str] = []
        for item in value:
            if isinstance(item, str) and item.strip():
                out.append(item)
        return out
    return []


def _contains_command(commands: List[str], needle: str) -> bool:
    needle_norm = needle.strip().lower()
    if not needle_norm:
        return False
    return any(needle_norm in c.lower() for c in commands)


def _check_command_order(commands: List[str], sequence: List[str]) -> bool:
    if not sequence:
        return True
    seq_idx = 0
    for command in commands:
        target = sequence[seq_idx].strip().lower()
        if target and target in command.lower():
            seq_idx += 1
            if seq_idx >= len(sequence):
                return True
    return False


def _extract_commands(events: List[Dict[str, Any]]) -> List[str]:
    completed = _extract_commands_by_event_type(events, "item.completed")
    if completed:
        return completed
    started = _extract_commands_by_event_type(events, "item.started")
    if started:
        return started

    # Fallback: capture any event with command_execution marker.
    commands: List[str] = []
    for event in events:
        if not isinstance(event, dict):
            continue
        if "command_execution" not in json.dumps(event, ensure_ascii=False):
            continue
        for cmd in _candidate_commands_from_event(event):
            commands.append(cmd)
    return commands


def _extract_commands_by_event_type(events: List[Dict[str, Any]], event_type: str) -> List[str]:
    commands: List[str] = []
    for event in events:
        if not isinstance(event, dict):
            continue
        if str(event.get("type", "")) != event_type:
            continue
        item = event.get("item")
        if not isinstance(item, dict):
            continue
        if str(item.get("type", "")) != "command_execution":
            continue
        command = item.get("command")
        if isinstance(command, str) and command.strip():
            commands.append(command.strip())
    return commands


def _candidate_commands_from_event(event: Dict[str, Any]) -> Iterable[str]:
    keys = {"command", "cmd", "shell_command"}

    def walk(value: Any) -> Iterable[Tuple[Optional[str], Any]]:
        if isinstance(value, dict):
            for k, v in value.items():
                yield (k, v)
                yield from walk(v)
        elif isinstance(value, list):
            for x in value:
                yield from walk(x)

    for key, value in walk(event):
        if key in keys and isinstance(value, str) and value.strip():
            yield value.strip()


def _extract_token_usage(events: List[Dict[str, Any]]) -> TokenUsage:
    usage = TokenUsage()

    for event in events:
        if not isinstance(event, dict):
            continue
        if str(event.get("type", "")) != "turn.completed":
            continue

        usage_dicts = _collect_usage_dicts(event)
        for d in usage_dicts:
            in_tok = _num(d.get("input_tokens"), _num(d.get("prompt_tokens"), 0))
            out_tok = _num(d.get("output_tokens"), _num(d.get("completion_tokens"), 0))
            reason_tok = _num(d.get("reasoning_tokens"), 0)
            total_tok = _num(d.get("total_tokens"), in_tok + out_tok + reason_tok)

            usage.input_tokens += in_tok
            usage.output_tokens += out_tok
            usage.reasoning_tokens += reason_tok
            usage.total_tokens += total_tok

    if usage.total_tokens == 0:
        usage.total_tokens = usage.input_tokens + usage.output_tokens + usage.reasoning_tokens

    return usage


def _collect_usage_dicts(root: Any) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    seen_ids = set()

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            oid = id(value)
            if oid in seen_ids:
                return
            seen_ids.add(oid)

            keys = set(value.keys())
            if keys & {
                "input_tokens",
                "output_tokens",
                "reasoning_tokens",
                "total_tokens",
                "prompt_tokens",
                "completion_tokens",
            }:
                out.append(value)

            for child in value.values():
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    walk(root)
    return out


def _num(primary: Any, default: int = 0) -> int:
    if isinstance(primary, bool):
        return default
    if isinstance(primary, int):
        return primary
    if isinstance(primary, float):
        return int(primary)
    if isinstance(primary, str):
        text = primary.strip()
        if not text:
            return default
        if re.fullmatch(r"-?\d+", text):
            return int(text)
    return default


def _load_json_payload(
    *,
    inline_json: Optional[str],
    json_file: Optional[str],
    label: str,
) -> Optional[Dict[str, Any]]:
    if inline_json and json_file:
        raise ValueError(f"Provide only one of --{label}-json or --{label}-file.")

    if inline_json:
        obj = json.loads(inline_json)
    elif json_file:
        obj = json.loads(Path(json_file).expanduser().read_text(encoding="utf-8"))
    else:
        return None

    if not isinstance(obj, dict):
        raise ValueError(f"{label} payload must be a JSON object.")
    return obj


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Run deterministic trace checks over a Codex JSONL trace.")
    p.add_argument("jsonl_path", help="Path to Codex JSONL events file.")
    p.add_argument("--checks-json", help="Inline JSON for deterministic_checks.")
    p.add_argument("--checks-file", help="JSON file containing deterministic_checks.")
    p.add_argument("--budgets-json", help="Inline JSON for budgets.")
    p.add_argument("--budgets-file", help="JSON file containing budgets.")
    p.add_argument("--tier2-mode", choices=["warn", "fail", "off"], default="warn")
    p.add_argument("--format", choices=["text", "json"], default="text")
    return p


def main(argv: Optional[List[str]] = None) -> int:
    args = _build_parser().parse_args(argv)

    try:
        checks = _load_json_payload(
            inline_json=args.checks_json,
            json_file=args.checks_file,
            label="checks",
        ) or {}
        budgets = _load_json_payload(
            inline_json=args.budgets_json,
            json_file=args.budgets_file,
            label="budgets",
        ) or {}
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    events, parse_warnings = load_jsonl_events(Path(args.jsonl_path).expanduser())
    result = evaluate_trace(events, deterministic_checks=checks, budgets=budgets)
    all_warnings = [*parse_warnings, *result.warnings]

    payload = {
        "tier1_failures": result.hard_failures,
        "tier2_failures": result.soft_failures,
        "warnings": all_warnings,
        "metrics": asdict(result.metrics),
    }

    tier1_failed = len(result.hard_failures) > 0
    tier2_failed = len(result.soft_failures) > 0
    passed = (not tier1_failed) and (args.tier2_mode != "fail" or not tier2_failed)

    if args.format == "json":
        out = dict(payload)
        out["passed"] = passed
        out["tier2_mode"] = args.tier2_mode
        print(json.dumps(out, indent=2, ensure_ascii=False))
    else:
        print(f"Trace events: {result.metrics.event_count}")
        print(f"Commands: {result.metrics.command_count}")
        print(f"Tier1 failures: {len(result.hard_failures)}")
        print(f"Tier2 findings: {len(result.soft_failures)} (mode={args.tier2_mode})")
        for msg in result.hard_failures:
            print(f"- TIER1: {msg}")
        for msg in result.soft_failures:
            print(f"- TIER2: {msg}")
        for msg in all_warnings:
            print(f"- WARN: {msg}")
        print(f"RESULT: {'PASS' if passed else 'FAIL'}")

    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
