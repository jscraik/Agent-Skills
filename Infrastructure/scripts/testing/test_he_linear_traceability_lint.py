from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "validation-and-linting"
    / "he_linear_traceability_lint.py"
)
SPEC = importlib.util.spec_from_file_location("he_linear_traceability_lint", SCRIPT_PATH)
assert SPEC is not None
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules["he_linear_traceability_lint"] = MODULE
SPEC.loader.exec_module(MODULE)


def test_valid_plan_traceability_passes() -> None:
    markdown = """---
schema_version: 1
linear_issue: JSC-224
linear_status: In Progress
traceability_required: true
---

# Plan

## Linear Work Item Contract

- Linear issue: JSC-224
- Current Linear status: In Progress

## Linear / Spec / Plan / PR Traceability

| Linear issue | Requirement | Source acceptance IDs | Plan units | Acceptance IDs | PR evidence |
| --- | --- | --- | --- | --- | --- |
| JSC-224 | R1 | SA1 | P0 | AC1 | pending |
"""

    result = MODULE.lint_markdown(Path("plan.md"), markdown)

    assert result.passed


def test_traceability_required_without_issue_fails() -> None:
    markdown = """---
schema_version: 1
linear_status: Todo
traceability_required: true
---

# Plan

## Linear Work Item Contract

- Linear issue: pending

## Linear / Spec / Plan / PR Traceability

| Linear issue | Requirement | Source acceptance IDs | Plan units | Acceptance IDs | PR evidence |
| --- | --- | --- | --- | --- | --- |
| pending | R1 | SA1 | P0 | AC1 | pending |
"""

    result = MODULE.lint_markdown(Path("plan.md"), markdown)

    assert not result.passed
    assert "frontmatter linear_issue must contain a Linear issue key like JSC-224" in result.errors


def test_missing_plan_traceability_columns_fail() -> None:
    markdown = """---
schema_version: 1
linear_issue: JSC-224
linear_status: In Progress
traceability_required: true
---

# Plan

## Linear Work Item Contract

- Linear issue: JSC-224

## Linear / Spec / Plan / PR Traceability

| Linear issue | Requirement |
| --- | --- |
| JSC-224 | R1 |
"""

    result = MODULE.lint_markdown(Path("plan.md"), markdown)

    assert not result.passed
    assert any("Linear / Spec / Plan / PR Traceability table" in error for error in result.errors)


def test_valid_spec_traceability_passes() -> None:
    markdown = """---
schema_version: 1
linear_issue: JSC-224
linear_status: In Progress
traceability_required: true
---

# Spec

## Linear Work Item Contract

- Linear issue: JSC-224
- Current Linear status: In Progress

## 17.9 Linear Acceptance Traceability

| Linear issue | Source requirement | Acceptance IDs | Planning handoff |
| --- | --- | --- | --- |
| JSC-224 | Requirement 1 | SA1, SA2 | PLAN-P0 |
"""

    result = MODULE.lint_markdown(Path("spec.md"), markdown)

    assert result.passed


def test_valid_pr_traceability_passes() -> None:
    markdown = """---
schema_version: 1
linear_issue: JSC-224
linear_status: In Review
traceability_required: true
---

# Pull Request

## Linear Work Item Contract

- Linear issue: JSC-224
- Current Linear status: In Review

## PR Traceability

| Linear issue | Acceptance IDs | Validation |
| --- | --- | --- |
| JSC-224 | AC1, AC2 | pytest passed |
"""

    result = MODULE.lint_markdown(Path("pr.md"), markdown)

    assert result.passed


def test_traceability_table_must_match_frontmatter_issue() -> None:
    markdown = """---
schema_version: 1
linear_issue: JSC-224
linear_status: In Progress
traceability_required: true
---

# Plan

## Linear Work Item Contract

- Linear issue: JSC-224

## Linear / Spec / Plan / PR Traceability

| Linear issue | Requirement | Source acceptance IDs | Plan units | Acceptance IDs | PR evidence |
| --- | --- | --- | --- | --- | --- |
| JSC-999 | R1 | SA1 | P0 | AC1 | pending |
"""

    result = MODULE.lint_markdown(Path("plan.md"), markdown)

    assert not result.passed
    assert any("frontmatter linear_issue JSC-224" in error for error in result.errors)


def test_traceability_table_requires_exact_issue_key_match() -> None:
    markdown = """---
schema_version: 1
linear_issue: JSC-22
linear_status: In Progress
traceability_required: true
---

# Plan

## Linear Work Item Contract

- Linear issue: JSC-22

## Linear / Spec / Plan / PR Traceability

| Linear issue | Requirement | Source acceptance IDs | Plan units | Acceptance IDs | PR evidence |
| --- | --- | --- | --- | --- | --- |
| JSC-224 | R1 | SA1 | P0 | AC1 | pending |
"""

    result = MODULE.lint_markdown(Path("plan.md"), markdown)

    assert not result.passed
    assert any("frontmatter linear_issue JSC-22" in error for error in result.errors)


def test_pr_traceability_requires_validation_column() -> None:
    markdown = """---
schema_version: 1
linear_issue: JSC-224
linear_status: In Review
traceability_required: true
---

# Pull Request

## Linear Work Item Contract

- Linear issue: JSC-224

## PR Traceability

| Linear issue | Acceptance IDs |
| --- | --- |
| JSC-224 | AC1 |
"""

    result = MODULE.lint_markdown(Path("pr.md"), markdown)

    assert not result.passed
    assert any("PR Traceability table must include columns: Validation" in error for error in result.errors)


# ---------------------------------------------------------------------------
# Tests for PR changes: null/unknown linear_issue, new JSC-167 eval,
# traceability_required with non-key values.
# ---------------------------------------------------------------------------


def test_linear_issue_null_string_fails_traceability_check() -> None:
    """linear_issue: null (string 'null') must fail traceability lint because
    it does not contain a valid Linear issue key like JSC-NNN.

    Covers: conditional-he-gate-selection-eval.md which changed linear_issue
    from JSC-299 to null while keeping traceability_required: true.
    """
    markdown = """---
schema_version: 1
artifact_id: 2026-05-09-agent-skills-conditional-he-gate-selection-eval
artifact_type: he-eval-report
canonical_slug: agent-skills-conditional-he-gate-selection
title: Agent Skills Conditional HE Gate Selection Eval
harness_stage: he-eval-report
status: blocked_release_confidence
date: 2026-05-09
traceability_required: true
origin: .harness/plan/2026-05-09-agent-skills-conditional-he-gate-selection-plan.md
linear_issue: null
linear_status: not_applicable
linear_milestone: null
---

# Agent Skills Conditional HE Gate Selection Eval
"""

    result = MODULE.lint_markdown(
        Path(".harness/evals/2026-05-09-agent-skills-conditional-he-gate-selection-eval.md"),
        markdown,
    )

    assert not result.passed
    assert "frontmatter linear_issue must contain a Linear issue key like JSC-224" in result.errors


def test_linear_issue_unknown_string_fails_traceability_check() -> None:
    """linear_issue: unknown must fail traceability lint because 'unknown' does
    not match the ISSUE_KEY_RE pattern.

    Covers: he-fresh-release-lane-eval.md which changed linear_issue
    from JSC-299 to 'unknown'.
    """
    markdown = """---
schema_version: 1
artifact_id: 2026-05-10-agent-skills-he-fresh-release-lane-eval
artifact_type: he-eval-report
canonical_slug: agent-skills-he-fresh-release-lane
title: Agent Skills HE Fresh Release Lane Eval
harness_stage: he-eval-report
status: blocked
date: 2026-05-10
traceability_required: true
origin: .harness/linear/agent-skills-linear-plan.md
linear_issue: unknown
linear_status: keep open
linear_milestone: HE Plugin Release Confidence
---

# Agent Skills HE Fresh Release Lane Eval
"""

    result = MODULE.lint_markdown(
        Path(".harness/evals/2026-05-10-agent-skills-he-fresh-release-lane-eval.md"),
        markdown,
    )

    assert not result.passed
    assert "frontmatter linear_issue must contain a Linear issue key like JSC-224" in result.errors


def test_traceability_not_required_skips_all_checks() -> None:
    """An artifact with traceability_required: false and no traceability headings
    must pass traceability lint without any checks.

    Covers: the new linear plan 2026-05-09-agent-skills-he-authority-proof-hardening-linear-plan.md
    which has traceability_required: false and an empty linear_issue.
    """
    markdown = """---
schema_version: 1
artifact_id: agent-skills-he-authority-proof-hardening-linear-plan
artifact_type: he-linear-plan
canonical_slug: agent-skills-he-authority-proof-hardening
title: HE Authority And Proof Hardening Linear Plan
harness_stage: he-linear-plan
status: active
date: 2026-05-09
traceability_required: false
origin: .harness/refactors/2026-05-09-agent-skills-he-authority-proof-hardening.md
linear_issue: ""
linear_milestone: "HE Authority And Proof Hardening"
---

# HE Authority And Proof Hardening Linear Plan
"""

    result = MODULE.lint_markdown(
        Path(".harness/linear/2026-05-09-agent-skills-he-authority-proof-hardening-linear-plan.md"),
        markdown,
    )

    assert result.passed, f"Unexpected errors: {result.errors}"


def test_jsc167_eval_passes_traceability_lint_with_body_reference() -> None:
    """The new JSC-167 eval file must pass traceability lint when the body
    contains the issue key and all required traceability sections are present.

    Covers: 2026-05-10-JSC-167-agent-skills-jsc-167-ask-bootstrap-command-discoverability-eval.md
    """
    markdown = """---
schema_version: 1
artifact_id: agent-skills-jsc-167-ask-bootstrap-command-discoverability-eval
artifact_type: he-eval-report
canonical_slug: agent-skills-jsc-167-ask-bootstrap-command-discoverability
title: Agent Skills JSC-167 Ask Bootstrap Command Discoverability Eval
harness_stage: he-eval-report
status: blocked
date: 2026-05-10
traceability_required: true
origin: .harness/plan/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-plan.md
linear_issue: JSC-167
linear_status: in_progress
linear_milestone: Command surface and ask reliability
---

# Agent Skills JSC-167 Ask Bootstrap Command Discoverability Eval

## Linear Work Item Contract

- Linear issue: JSC-167
- Status: in_progress

## Linear / Spec / Plan / PR Traceability

| Linear issue | Requirement | Source acceptance IDs | Plan units | Acceptance IDs | PR evidence |
| --- | --- | --- | --- | --- | --- |
| JSC-167 | Bootstrap discoverability | SA1 | P0 | AC1 | pending |
"""

    result = MODULE.lint_markdown(
        Path(
            ".harness/evals/"
            "2026-05-10-JSC-167-agent-skills-jsc-167-ask-bootstrap-command-discoverability-eval.md"
        ),
        markdown,
    )

    assert result.passed, f"Unexpected errors: {result.errors}"


def test_jsc167_body_must_include_issue_key() -> None:
    """When linear_issue is JSC-167, the artifact body must reference JSC-167.

    If the body (outside the frontmatter) does not contain the issue key,
    traceability lint must fail with the appropriate error.
    """
    # Construct markdown where the frontmatter correctly declares JSC-167 but
    # the body uses a placeholder so the issue key is absent from the body.
    frontmatter = """---
schema_version: 1
artifact_id: agent-skills-jsc-167-ask-bootstrap-command-discoverability-eval
artifact_type: he-eval-report
canonical_slug: agent-skills-jsc-167-ask-bootstrap-command-discoverability
title: Agent Skills JSC-167 Ask Bootstrap Command Discoverability Eval
harness_stage: he-eval-report
status: blocked
date: 2026-05-10
traceability_required: true
origin: .harness/plan/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-plan.md
linear_issue: JSC-167
linear_status: in_progress
linear_milestone: Command surface and ask reliability
---
"""
    # Body deliberately omits the issue key (uses PENDING instead of JSC-167).
    # The H1 must also not reference JSC-167 so the body truly lacks the key.
    # Update the title frontmatter to match the H1 we use here.
    frontmatter = frontmatter.replace(
        "title: Agent Skills JSC-167 Ask Bootstrap Command Discoverability Eval",
        "title: Agent Skills Ask Bootstrap Command Discoverability Eval",
    )
    body = """
# Agent Skills Ask Bootstrap Command Discoverability Eval

## Linear Work Item Contract

- Linear issue: PENDING

## Linear / Spec / Plan / PR Traceability

| Linear issue | Requirement | Source acceptance IDs | Plan units | Acceptance IDs | PR evidence |
| --- | --- | --- | --- | --- | --- |
| PENDING | Bootstrap discoverability | SA1 | P0 | AC1 | pending |
"""
    markdown_no_key = frontmatter + body

    result = MODULE.lint_markdown(
        Path(
            ".harness/evals/"
            "2026-05-10-JSC-167-agent-skills-jsc-167-ask-bootstrap-command-discoverability-eval.md"
        ),
        markdown_no_key,
    )

    assert not result.passed
    assert any("artifact body must include frontmatter linear_issue" in e for e in result.errors)
