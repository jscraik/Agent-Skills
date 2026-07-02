#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


DEFAULT_MAX_TOKENS_USED = 7000
FALLBACK_METADATA_RE = re.compile(r"(?i)(model metadata .*not found|fallback metadata)")
FALLBACK_MODEL_RE = re.compile(r"(?i)Model metadata for .([^\\s]+). not found")
TOKENS_USED_RE = re.compile(r"(?im)tokens used\s*(?::|\n)\s*([0-9][0-9,]*)")
JSON_TOKENS_USED_RE = re.compile(r'"tokens_used"\s*:\s*([0-9]+)')
VISIBLE_THINKING_RE = re.compile(r"(?im)(<think\b|</think>|^\s*thinking\s*$|thinking trace)")
OBSERVATION_PATTERNS = {
    "model": re.compile(r"(?im)^model:\s*(.+?)\s*$"),
    "provider": re.compile(r"(?im)^provider:\s*(.+?)\s*$"),
    "approval": re.compile(r"(?im)^approval:\s*(.+?)\s*$"),
    "sandbox": re.compile(r"(?im)^sandbox:\s*(.+?)\s*$"),
    "session_id": re.compile(r"(?im)^session id:\s*(.+?)\s*$"),
}


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _observed_tokens_used(text: str) -> int | None:
    values: list[int] = []
    for pattern in (TOKENS_USED_RE, JSON_TOKENS_USED_RE):
        for match in pattern.finditer(text):
            try:
                values.append(int(match.group(1).replace(",", "")))
            except ValueError:
                continue
    values.extend(_codex_jsonl_token_totals(text))
    return max(values) if values else None


def _codex_jsonl_token_totals(text: str) -> list[int]:
    totals: list[int] = []
    for line in text.splitlines():
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(payload, dict):
            continue
        usage = payload.get("usage")
        if not isinstance(usage, dict):
            continue
        token_values = [
            usage.get("input_tokens"),
            usage.get("output_tokens"),
            usage.get("reasoning_output_tokens"),
        ]
        total = sum(value for value in token_values if isinstance(value, int))
        if total > 0:
            totals.append(total)
    return totals


def _has_codex_reasoning_event(text: str) -> bool:
    for line in text.splitlines():
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(payload, dict):
            continue
        item = payload.get("item")
        if isinstance(item, dict) and item.get("type") == "reasoning":
            return True
    return False


def _findings(text: str, max_tokens_used: int) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    if FALLBACK_METADATA_RE.search(text):
        findings.append({
            "code": "codex_runtime_metadata_fallback",
            "message": "Codex reported missing model metadata or fallback metadata.",
        })
    if VISIBLE_THINKING_RE.search(text):
        findings.append({
            "code": "codex_runtime_visible_thinking",
            "message": "Model output exposed a thinking trace in surfaced text.",
        })
    observed_tokens = _observed_tokens_used(text)
    if observed_tokens is not None and observed_tokens > max_tokens_used:
        findings.append({
            "code": "codex_runtime_token_budget_exceeded",
            "message": f"Smoke transcript used {observed_tokens} tokens; limit is {max_tokens_used}.",
        })
    return findings


def _runtime_observations(text: str) -> dict[str, Any]:
    observations: dict[str, Any] = {}
    for key, pattern in OBSERVATION_PATTERNS.items():
        match = pattern.search(text)
        if match:
            observations[key] = match.group(1).strip()
    fallback_model_match = FALLBACK_MODEL_RE.search(text)
    if fallback_model_match and "model" not in observations:
        observations["model"] = fallback_model_match.group(1).strip()
    observed_tokens = _observed_tokens_used(text)
    if observed_tokens is not None:
        observations["tokens_used"] = observed_tokens
    observations["metadata_fallback_observed"] = bool(FALLBACK_METADATA_RE.search(text))
    observations["codex_jsonl_reasoning_event_observed"] = _has_codex_reasoning_event(text)
    observations["visible_thinking_observed"] = bool(VISIBLE_THINKING_RE.search(text))
    return observations


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate captured oss-local smoke output without invoking the local model.",
    )
    parser.add_argument("paths", nargs="+", help="Captured stdout/stderr/transcript files to inspect.")
    parser.add_argument("--max-tokens-used", type=int, default=DEFAULT_MAX_TOKENS_USED)
    parser.add_argument("--json", action="store_true", help="Emit a JSON receipt.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    texts: list[str] = []
    missing: list[str] = []
    for raw_path in args.paths:
        path = Path(raw_path)
        if not path.is_file():
            missing.append(raw_path)
            continue
        texts.append(_read_text(path))
    findings = [{"code": "smoke_output_missing", "message": path} for path in missing]
    findings.extend(_findings("\n".join(texts), args.max_tokens_used))
    receipt: dict[str, Any] = {
        "schema_version": "skills-sdk.oss-local-smoke-output-check.v0",
        "status": "pass" if not findings else "fail",
        "paths_checked": args.paths,
        "max_tokens_used": args.max_tokens_used,
        "runtime_observations": _runtime_observations("\n".join(texts)),
        "findings": findings,
    }
    if args.json:
        print(json.dumps(receipt, sort_keys=True, indent=2))
    elif findings:
        for finding in findings:
            print(f"{finding['code']}: {finding['message']}", file=sys.stderr)
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
