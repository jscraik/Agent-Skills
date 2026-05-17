#!/usr/bin/env python3
"""Validate that high-signal steering has an executable uptake record."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


DEFAULT_LEDGER = Path(".harness/quality/steering-uptake.md")
ACTIVE_RULE_REQUIRED_PHRASES = (
    "high-signal candidate",
    "classified",
    "do not resume ordinary task work",
    "environment refinement",
    "systems thinker",
    "horizontal ooda",
    "vertical ooda",
    "cross-boundary",
    "target context window",
)
REQUIRED_MARKERS = (
    "Operating failure:",
    "Feedback type:",
    "Intent radius:",
    "Blocker:",
    "Horizontal OODA:",
    "Vertical OODA:",
    "Durable surface:",
    "Environment refinement:",
    "Mechanism:",
    "Proof:",
    "Validation:",
    "Repeat prevention:",
)
BROAD_RADII = {"package", "repository", "architecture_rule", "durable_memory"}
TRANSFERABLE_FEEDBACK_TYPES = {
    "api_design_rule",
    "repeated_pattern",
    "repeated_error_protocol",
    "architecture_boundary",
    "naming_language",
    "validation_gap",
    "diagnostic_debt",
    "test_contract_gap",
    "documentation_drift",
    "product_contract_rule",
    "agent_operating_rule",
}
TRANSFERABLE_INVALID_RADII = {"line", "function"}
DISPOSITION_MARKERS = (
    "fixed now",
    "different semantics",
    "deferred",
    "not applicable",
    "policy surface",
    "no code sweep",
)
DIAGNOSTIC_CLASSIFICATION_MARKER = "Diagnostic classification:"
DIAGNOSTIC_FEEDBACK_TYPES = {"diagnostic_debt"}
DIAGNOSTIC_REQUIRED_TERMS = ("category", "owner", "next action")
REPEATED_ERROR_PROTOCOL_MARKER = "Repeated error protocol:"
REPEATED_ERROR_FEEDBACK_TYPES = {"repeated_error_protocol"}
REPEATED_ERROR_REQUIRED_TERMS = (
    "same error twice",
    "research",
    "3-5",
    "choose",
    "implement",
)
PATTERN_SWEEP_REQUIRED_MARKERS = (
    "Sweep scope:",
    "Search terms:",
    "Matches considered:",
    "Exclusions:",
)
GENERALIZATION_REQUIRED_MARKERS = (
    "Generalized rule:",
    "Similar-case disposition:",
)
OODA_SCALING_PROTOCOL_MARKER = "OODA scaling protocol:"
OODA_SCALING_REQUIRED_TERMS = (
    "horizontal",
    "vertical",
    "compaction",
    "harness",
    "environment",
    "target context window",
    "reflect",
)
OODA_SCALING_TRIGGERS = (
    "cross-boundary",
    "target context window",
    "target context-window",
    "stacked trajectories",
)


def _field_value(record: str, field: str) -> str | None:
    match = re.search(rf"^{re.escape(field)}\s*([^\n]+)", record, flags=re.MULTILINE)
    if not match:
        return None
    return match.group(1).strip()


def _uptake_records(text: str) -> list[tuple[str, str]]:
    records: list[tuple[str, str]] = []
    parts = re.split(r"^## Uptake Record:\s*", text, flags=re.MULTILINE)
    for part in parts[1:]:
        title, _, body = part.partition("\n")
        records.append((title.strip(), body))
    return records


def _requires_ooda_scaling_protocol(text: str) -> bool:
    text_lower = text.lower()
    return any(trigger in text_lower for trigger in OODA_SCALING_TRIGGERS)


def validate_ledger(path: Path) -> dict[str, object]:
    errors: list[str] = []
    if not path.exists():
        return {
            "path": str(path),
            "status": "fail",
            "errors": [f"missing steering uptake ledger: {path}"],
        }

    text = path.read_text(encoding="utf-8")
    if "# Steering Uptake Ledger" not in text:
        errors.append("missing '# Steering Uptake Ledger' heading")
    if "## Active Rule" not in text:
        errors.append("missing '## Active Rule' section")
    else:
        active_rule = text.split("## Active Rule", 1)[1].split("## Uptake Record:", 1)[0]
        active_rule_lower = active_rule.lower()
        for phrase in ACTIVE_RULE_REQUIRED_PHRASES:
            if phrase.lower() not in active_rule_lower:
                errors.append(
                    f"active rule must state steering is a '{phrase}' before ordinary work"
                )
    records = _uptake_records(text)
    if not records:
        errors.append("missing at least one '## Uptake Record:' section")

    for title, body in records:
        for marker in REQUIRED_MARKERS:
            if marker not in body:
                errors.append(f"{title}: missing required marker '{marker}'")

        feedback_type = _field_value(body, "Feedback type:")
        intent_radius = _field_value(body, "Intent radius:")
        broad_radius = intent_radius in BROAD_RADII
        transferable_type = feedback_type in TRANSFERABLE_FEEDBACK_TYPES
        if transferable_type and intent_radius in TRANSFERABLE_INVALID_RADII:
            errors.append(
                f"{title}: transferable feedback cannot be scoped to {intent_radius}; "
                "choose a radius that can classify equivalent cases"
            )
        if broad_radius or transferable_type:
            if "Pattern sweep:" not in body:
                errors.append(
                    f"{title}: broad or transferable feedback requires 'Pattern sweep:'"
                )
            for marker in PATTERN_SWEEP_REQUIRED_MARKERS:
                if marker not in body:
                    errors.append(
                        f"{title}: broad or transferable feedback requires '{marker}'"
                    )
            if "Disposition:" not in body:
                errors.append(
                    f"{title}: broad or transferable feedback requires 'Disposition:'"
                )
            elif not any(marker in body for marker in DISPOSITION_MARKERS):
                errors.append(
                    f"{title}: disposition must classify matches or explain no code sweep"
                )
        if transferable_type:
            for marker in GENERALIZATION_REQUIRED_MARKERS:
                if marker not in body:
                    errors.append(
                        f"{title}: transferable feedback requires '{marker}'"
                    )
        if feedback_type in DIAGNOSTIC_FEEDBACK_TYPES:
            diagnostic_classification = _field_value(body, DIAGNOSTIC_CLASSIFICATION_MARKER)
            if diagnostic_classification is None:
                errors.append(
                    f"{title}: diagnostic feedback requires '{DIAGNOSTIC_CLASSIFICATION_MARKER}'"
                )
            elif not all(term in diagnostic_classification.lower() for term in DIAGNOSTIC_REQUIRED_TERMS):
                errors.append(
                    f"{title}: diagnostic classification must name category, owner, and next action"
                )
        if feedback_type in REPEATED_ERROR_FEEDBACK_TYPES:
            repeated_error_protocol = _field_value(body, REPEATED_ERROR_PROTOCOL_MARKER)
            if repeated_error_protocol is None:
                errors.append(
                    f"{title}: repeated error feedback requires '{REPEATED_ERROR_PROTOCOL_MARKER}'"
                )
            elif not all(term in repeated_error_protocol.lower() for term in REPEATED_ERROR_REQUIRED_TERMS):
                errors.append(
                    f"{title}: repeated error protocol must say same error twice, research 3-5 fixes, choose, and implement"
                )
        if _requires_ooda_scaling_protocol(f"{title}\n{body}"):
            ooda_scaling_protocol = _field_value(body, OODA_SCALING_PROTOCOL_MARKER)
            if ooda_scaling_protocol is None:
                errors.append(
                    f"{title}: cross-boundary OODA feedback requires '{OODA_SCALING_PROTOCOL_MARKER}'"
                )
            elif not all(
                term in ooda_scaling_protocol.lower()
                for term in OODA_SCALING_REQUIRED_TERMS
            ):
                errors.append(
                    f"{title}: OODA scaling protocol must name horizontal, vertical, compaction, harness, environment, target context window, and reflection"
                )

    status = "fail" if errors else "pass"
    return {
        "path": str(path),
        "status": status,
        "errors": errors,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        default=[DEFAULT_LEDGER],
        help="Steering uptake ledger file(s) to validate.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    results = [validate_ledger(path) for path in args.paths]
    status = "fail" if any(result["status"] == "fail" for result in results) else "pass"
    payload = {"schema_version": "steering-uptake-validation.v1", "status": status, "results": results}

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        for result in results:
            print(f"{result['status']}: {result['path']}")
            for error in result["errors"]:
                print(f"  - {error}")

    return 1 if status == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
