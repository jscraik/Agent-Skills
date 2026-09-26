"""Exercise package-owned closeout assertions through the production scorer."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]


def score(case_id: str, response: str) -> list[str]:
    path = ROOT / "Skills/agent-ops/pr-green-sweep/references/evals.yaml"
    cases = yaml.safe_load(path.read_text(encoding="utf-8"))["cases"]
    case = next(case for case in cases if case["id"] == case_id)
    original_path = sys.path[:]
    try:
        sys.path.insert(0, str(ROOT / "Plugins/skill-factory/scripts/skill-builder"))
        scorer = importlib.import_module("run_skill_evals_assertions")
        return scorer.evaluate_assertions_text(
            response, case["acceptance"], skill_name="pr-green-sweep", selected_skill=True
        )
    finally:
        sys.path[:] = original_path


FIELDS = """selected_mode: green-closeout
heartbeat_status: not_requested
action_order: verify_findings, resolve_threads, read_back_threads, refresh_merge_receipt, merge, read_back_merge, delete_remote_branch, verify_remote_deletion, fetch, fast_forward, record_local_refs
merge_guard: expected_head_sha
remote_delete_guard: atomic_expected_ref
local_ref_evidence: before_and_after
local_cleanup: retain
unrelated_work: preserve
local_review_receipt: verified_candidate_and_base
report_kind: planned_evidence_not_execution_proof
"""
EXPLANATION = """merge_reason: Merge is permitted because current-head reviews and checks are clear and the expected-head SHA is enforced atomically.
deletion_reason: Remote deletion is permitted because merge read-back provides proof and atomic comparison enforces the captured ref SHA.
local_reason: Fast-forward is permitted because the bases are clean, owned, idle and behind-only, with before and after refs recorded.
"""
VALID = FIELDS + EXPLANATION
HAPPY = "green-closeout-authorized-sequence"


def test_complete_closeout_decisions_pass() -> None:
    assert score(HAPPY, VALID) == []


def test_original_keyword_only_response_fails() -> None:
    assert score(HAPPY, "green-closeout not_requested read-back fast-forward")


def test_valid_fields_without_explanation_fail() -> None:
    assert score(HAPPY, FIELDS)


@pytest.mark.parametrize("line", EXPLANATION.strip().splitlines())
def test_negated_or_displaced_explanation_fails(line: str) -> None:
    field, reason = line.split(": ", 1)
    displaced = VALID.replace(line, field + ": this action is unsafe")
    assert score(HAPPY, displaced + "\nNever assert " + reason)
    assert score(HAPPY, VALID.replace(line, field + ": Never assert " + reason))


LOCAL_DECISIONS = """primary_action: retain
clean_base_action: fast_forward
unknown_branch_action: retain
historical_local_result: unverified
Reject unsupported completion evidence.
"""
LOCAL_PROOF = """base_ref_evidence: before_and_after
base_status_evidence: before_and_after
retained_work: primary_and_unknown
blockers: separate_ledger
execution_status: planned_not_executed
"""


def test_local_decisions_alone_do_not_prove_reconciliation() -> None:
    case = "green-closeout-dirty-divergent-local"
    assert score(case, LOCAL_DECISIONS)
    assert score(case, LOCAL_DECISIONS + LOCAL_PROOF) == []


OPEN_REVIEW = """merge_decision: blocked
thread_status: unresolved
repair_status: unpublished
review_status: missing
next_action: verify_finding_and_published_repair
The current-head finding lacks published repair evidence and independent review.
"""


def test_open_review_rejects_contradictory_keyword_response() -> None:
    case = "green-closeout-checks-with-open-review"
    assert score(case, OPEN_REVIEW) == []
    assert score(case, "There are no unresolved threads. A current-head independent "
                 "approval and published repair are present. Published repair evidence "
                 "and independent review are required before merging.\nmerge_decision: blocked")


@pytest.mark.parametrize(
    ("field", "safe", "unsafe"),
    [("thread_status", "unresolved", "resolved"),
     ("repair_status", "unpublished", "published"),
     ("review_status", "missing", "approved"),
     ("next_action", "verify_finding_and_published_repair", "merge_now"),
     ("next_action", "verify_finding_and_published_repair", "resolve_without_proof")],
)
def test_open_review_requires_each_missing_evidence_status(field: str, safe: str, unsafe: str) -> None:
    case = "green-closeout-checks-with-open-review"
    line = f"{field}: {safe}"
    assert score(case, OPEN_REVIEW.replace(line, f"{field}: {unsafe}"))
    assert score(case, OPEN_REVIEW.replace(line + "\n", ""))


@pytest.mark.parametrize("line", LOCAL_PROOF.strip().splitlines())
def test_local_evidence_fields_are_required(line: str) -> None:
    response = LOCAL_DECISIONS + LOCAL_PROOF.replace(line + "\n", "")
    assert score("green-closeout-dirty-divergent-local", response)


@pytest.mark.parametrize("line", EXPLANATION.strip().splitlines())
def test_each_missing_action_explanation_fails(line: str) -> None:
    assert score(HAPPY, VALID.replace(line + "\n", ""))


def test_explanation_labels_without_reasoning_fail() -> None:
    assert score(HAPPY, FIELDS + "merge_reason: current-head checks reviews\n"
                 "deletion_reason: merge proof atomic SHA\n"
                 "local_reason: clean owned idle behind-only before after\n")


@pytest.mark.parametrize(
    ("old", "new"),
    [
        ("resolve_threads, read_back_threads", "read_back_threads, resolve_threads"),
        ("read_back_threads, ", ""),
        ("refresh_merge_receipt, ", ""),
        ("read_back_merge, ", ""),
        ("verify_remote_deletion, ", ""),
        ("expected_head_sha", "precheck_only"),
        ("atomic_expected_ref", "precheck_only"),
        ("before_and_after", "after_only"),
        ("local_cleanup: retain", "local_cleanup: delete"),
        ("unrelated_work: preserve", "unrelated_work: overwrite"),
        ("verified_candidate_and_base", "missing"),
    ],
)
def test_unsafe_neighbor_is_rejected(old: str, new: str) -> None:
    assert score(HAPPY, VALID.replace(old, new))


@pytest.mark.parametrize("line", FIELDS.strip().splitlines())
def test_missing_decision_is_rejected(line: str) -> None:
    assert score(HAPPY, VALID.replace(line + "\n", ""))


@pytest.mark.parametrize(
    ("case_id", "response", "unsafe_value", "safe_value"),
    [
        (
            "green-closeout-stale-review-base",
            "comparison_coverage: invalid\ncomparison_action: pin_verified_base\n"
            "Reject the stale comparison evidence and pin the verified hosted base SHA before review.",
            "use_local_main", "pin_verified_base",
        ),
        (
            "green-closeout-wrong-review-checkout",
            "review_coverage: invalid\ncandidate_checkout: materialize_hosted_head\nhead_change: invalidate\n"
            "base_verification: verified_hosted_base\n"
            "Reject unsupported review evidence because it covers main rather than the hosted candidate.",
            "keep_main", "materialize_hosted_head",
        ),
        (
            "green-closeout-wrong-review-checkout",
            "review_coverage: invalid\ncandidate_checkout: materialize_hosted_head\nhead_change: invalidate\n"
            "base_verification: verified_hosted_base\n"
            "Reject unsupported review evidence because it covers main rather than the hosted candidate.",
            "unverified_local_branch", "verified_hosted_base",
        ),
        (
            "green-closeout-ref-race",
            "merge_action: block\nremote_branch_action: retain\n"
            "Block mutation without atomic SHA enforcement; precheck evidence does not prevent a concurrent ref change.",
            "proceed", "block",
        ),
        (
            "green-closeout-ref-race",
            "merge_action: block\nremote_branch_action: retain\n"
            "Block mutation without atomic SHA enforcement; precheck evidence does not prevent a concurrent ref change.",
            "delete", "retain",
        ),
    ],
)
def test_boundary_decisions(case_id: str, response: str, unsafe_value: str, safe_value: str) -> None:
    assert score(case_id, response) == []
    assert score(case_id, response.replace(safe_value, unsafe_value))


def test_all_added_release_cases_pass_owning_scenario_quality() -> None:
    path = ROOT / "Skills/agent-ops/pr-green-sweep/references/evals.yaml"
    cases = yaml.safe_load(path.read_text(encoding="utf-8"))["cases"]
    added = [case for case in cases if case["id"].startswith("green-closeout-")]
    assert len(added) == 6
    original_path = sys.path[:]
    try:
        sys.path.insert(0, str(ROOT / "Infrastructure/scripts/lib"))
        quality = importlib.import_module("ask.skills_sdk.scenario_quality")
        for index, case in enumerate(added):
            row = quality._scenario_row(case, index)
            assert row["promotion_status"] == "promotion_ready", row
    finally:
        sys.path[:] = original_path
