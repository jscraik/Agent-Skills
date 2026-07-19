#!/usr/bin/env python3
"""Validate recurring PR findings and their merge-eligibility boundary."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = SKILL_ROOT / "references" / "recurring-finding-ledger.v1.schema.json"


def validate_ledger(ledger: object) -> list[str]:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = [error.message for error in validator.iter_errors(ledger)]
    if errors or not isinstance(ledger, dict):
        return sorted(errors)

    seen_ids: set[str] = set()
    seen_fingerprints: set[str] = set()
    for finding in ledger["classes"]:
        class_id = finding["finding_class_id"]
        fingerprint = finding["fingerprint_sha256"]
        expected = hashlib.sha256(
            finding["normalized_invariant"].strip().lower().encode("utf-8")
        ).hexdigest()
        if class_id in seen_ids:
            errors.append(f"duplicate finding_class_id: {class_id}")
        if fingerprint in seen_fingerprints:
            errors.append(f"duplicate fingerprint_sha256: {fingerprint}")
        if fingerprint != expected:
            errors.append(f"fingerprint_sha256 does not match normalized_invariant: {class_id}")
        seen_ids.add(class_id)
        seen_fingerprints.add(fingerprint)

        occurrences = finding["occurrences"]
        occurrence_keys = {
            (item["repository"], item["pull_request"], item["evidence_ref"])
            for item in occurrences
        }
        if len(occurrence_keys) != len(occurrences):
            errors.append(f"duplicate occurrence evidence: {class_id}")

        repeated = len(occurrences) >= 2
        guardrail_validated = finding["guardrail"]["status"] == "validated"
        expected_merge_eligible = not repeated or guardrail_validated
        if finding["merge_eligible"] != expected_merge_eligible:
            errors.append(
                f"merge_eligible must be {str(expected_merge_eligible).lower()}: {class_id}"
            )
    return sorted(errors)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", type=Path, required=True)
    args = parser.parse_args()
    try:
        ledger = json.loads(args.ledger.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "fail", "findings": [f"failed to read ledger: {exc}"]}))
        return 1
    errors = validate_ledger(ledger)
    print(json.dumps({"status": "fail" if errors else "pass", "findings": errors}))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
