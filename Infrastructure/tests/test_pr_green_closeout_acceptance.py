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


VALID = """selected_mode: green-closeout
heartbeat_status: not_requested
action_order: verify_findings, resolve_threads, read_back_threads, refresh_merge_receipt, merge, read_back_merge, delete_remote_branch, verify_remote_deletion, fetch, fast_forward, record_local_refs
merge_guard: expected_head_sha
remote_delete_guard: atomic_expected_ref
local_ref_evidence: before_and_after
local_cleanup: retain
unrelated_work: preserve
"""
HAPPY = "green-closeout-authorized-sequence"


def test_complete_closeout_decisions_pass() -> None:
    assert score(HAPPY, VALID) == []


def test_original_keyword_only_response_fails() -> None:
    assert score(HAPPY, "green-closeout not_requested read-back fast-forward")


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
    ],
)
def test_unsafe_neighbor_is_rejected(old: str, new: str) -> None:
    assert score(HAPPY, VALID.replace(old, new))


@pytest.mark.parametrize("line", VALID.strip().splitlines())
def test_missing_decision_is_rejected(line: str) -> None:
    assert score(HAPPY, VALID.replace(line + "\n", ""))


@pytest.mark.parametrize(
    ("case_id", "response", "unsafe_value", "safe_value"),
    [
        (
            "green-closeout-wrong-review-checkout",
            "review_coverage: invalid\ncandidate_checkout: materialize_hosted_head\nhead_change: invalidate",
            "keep_main", "materialize_hosted_head",
        ),
        (
            "green-closeout-ref-race",
            "merge_action: block\nremote_branch_action: retain",
            "proceed", "block",
        ),
        (
            "green-closeout-ref-race",
            "merge_action: block\nremote_branch_action: retain",
            "delete", "retain",
        ),
    ],
)
def test_boundary_decisions(case_id: str, response: str, unsafe_value: str, safe_value: str) -> None:
    assert score(case_id, response) == []
    assert score(case_id, response.replace(safe_value, unsafe_value))
