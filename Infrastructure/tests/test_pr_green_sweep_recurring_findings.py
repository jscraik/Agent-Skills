from __future__ import annotations

import hashlib
import importlib.util
import re
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "Skills/agent-ops/pr-green-sweep/scripts/validate_recurring_findings.py"
EVALS_PATH = ROOT / "Skills/agent-ops/pr-green-sweep/references/evals.yaml"
CONTRACT_PATH = ROOT / "Skills/agent-ops/pr-green-sweep/references/contract.yaml"
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


def test_fingerprint_normalizes_invariant_before_hashing():
    invariant = "  Latest Head Must Be Validated Before Merge  "
    normalized = "latest head must be validated before merge"
    ledger = _ledger()
    ledger["classes"][0]["normalized_invariant"] = invariant
    ledger["classes"][0]["fingerprint_sha256"] = hashlib.sha256(normalized.encode()).hexdigest()
    assert MODULE.validate_ledger(ledger) == []


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


def _sandbox_environment_acceptance() -> str:
    payload = yaml.safe_load(EVALS_PATH.read_text(encoding="utf-8"))
    cases = payload["cases"]
    case = next(item for item in cases if item["id"] == "happy-open-pr-sweep")
    acceptance = next(
        item
        for item in case["acceptance"]
        if item["type"] == "regex" and "MISE_TRUSTED_CONFIG_PATHS" in item["value"]
    )
    return acceptance["value"]


def test_pr_sweep_environment_contract_requires_root_trust_config_file():
    contract = yaml.safe_load(CONTRACT_PATH.read_text(encoding="utf-8"))
    trusted = contract["environment_contract"]["trusted_config_path_contract"]

    assert trusted["form"] == "one or more explicitly approved root mise config files"
    assert trusted["repository_example"] == "$(git rev-parse --show-toplevel)/.mise.toml"
    assert re.search(
        _sandbox_environment_acceptance(),
        'XDG_CACHE_HOME=/tmp/cache XDG_STATE_HOME=/tmp/state MISE_CACHE_DIR=/tmp/mise-cache MISE_STATE_DIR=/tmp/mise-state MISE_TRUSTED_CONFIG_PATHS="$(git rev-parse --show-toplevel)/.mise.toml" gh pr list',
    )


def test_pr_sweep_environment_contract_rejects_noncanonical_mise_trust_paths():
    pattern = _sandbox_environment_acceptance()
    base = "XDG_CACHE_HOME=/tmp/cache XDG_STATE_HOME=/tmp/state MISE_CACHE_DIR=/tmp/mise-cache MISE_STATE_DIR=/tmp/mise-state "

    for invalid_value in ("$PWD", "${PWD}", "$(pwd)", "$(git rev-parse --show-toplevel)"):
        assert not re.search(pattern, f"{base}MISE_TRUSTED_CONFIG_PATHS={invalid_value} gh pr list")


def test_pr_sweep_environment_contract_rejects_bare_variable_mentions():
    pattern = _sandbox_environment_acceptance()
    response = "XDG_CACHE_HOME XDG_STATE_HOME MISE_CACHE_DIR MISE_STATE_DIR MISE_TRUSTED_CONFIG_PATHS"

    assert not re.search(pattern, response)


def test_blocked_external_ci_eval_rejects_negated_classification():
    payload = yaml.safe_load(EVALS_PATH.read_text(encoding="utf-8"))
    case = next(
        item
        for item in payload["cases"]
        if item["id"] == "eval.pr-green-sweep.blocked-external-ci-keeps-independent-lanes-visible"
    )
    rejection = next(item for item in case["acceptance"] if item["type"] == "not_regex")

    assert re.search(
        rejection["value"],
        "Snyk is not blocked_external_ci; it is source-owned.",
    )
    assert not re.search(
        rejection["value"],
        "Snyk is blocked_external_ci and the merge remains blocked.",
    )
