from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "Skills/agent-ops/pr-green-sweep/scripts/validate_recurring_findings.py"
SPEC = importlib.util.spec_from_file_location("validate_recurring_findings", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def _ledger(*, occurrences: int = 2, guardrail_status: str = "validated", merge_eligible: bool = True):
    invariant = "latest head must be validated before merge"
    occurrence_rows = [
        {
            "repository": "jscraik/example",
            "pull_request": number,
            "evidence_ref": f"https://github.com/jscraik/example/pull/{number}",
        }
        for number in range(1, occurrences + 1)
    ]
    if guardrail_status == "validated":
        guardrail = {
            "status": "validated",
            "artifact_ref": "validator:latest-head",
            "validation_commands": [{"command": "pytest -q", "status": "pass"}],
        }
    else:
        guardrail = {
            "status": "blocked",
            "owner": "Agent Ops Team",
            "blocker_ref": "issue:JSC-468",
            "expires_at": "2026-08-01T00:00:00Z",
            "next_review_at": "2026-07-24T00:00:00Z",
        }
    return {
        "schema_version": 1,
        "classes": [
            {
                "finding_class_id": "finding_latest_head_validation",
                "fingerprint_sha256": hashlib.sha256(invariant.encode()).hexdigest(),
                "normalized_invariant": invariant,
                "root_cause": "stale hosted evidence",
                "occurrences": occurrence_rows,
                "guardrail": guardrail,
                "merge_eligible": merge_eligible,
            }
        ],
    }


def test_repeated_finding_with_validated_guardrail_is_merge_eligible():
    assert MODULE.validate_ledger(_ledger()) == []


def test_repeated_finding_with_blocked_guardrail_cannot_be_merge_eligible():
    errors = MODULE.validate_ledger(_ledger(guardrail_status="blocked"))
    assert errors == ["merge_eligible must be false: finding_latest_head_validation"]


def test_repeated_finding_with_blocked_guardrail_can_remain_blocked():
    assert MODULE.validate_ledger(
        _ledger(guardrail_status="blocked", merge_eligible=False)
    ) == []


def test_fingerprint_must_derive_from_normalized_invariant():
    ledger = _ledger()
    ledger["classes"][0]["fingerprint_sha256"] = "0" * 64
    assert MODULE.validate_ledger(ledger) == [
        "fingerprint_sha256 does not match normalized_invariant: finding_latest_head_validation"
    ]


def test_duplicate_class_identity_is_rejected():
    ledger = _ledger()
    ledger["classes"].append(dict(ledger["classes"][0]))
    errors = MODULE.validate_ledger(ledger)
    assert "duplicate finding_class_id: finding_latest_head_validation" in errors
    assert any(error.startswith("duplicate fingerprint_sha256:") for error in errors)
