from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "validation-and-linting"
    / "he_frontmatter_safety_lint.py"
)
SPEC = importlib.util.spec_from_file_location("he_frontmatter_safety_lint", SCRIPT_PATH)
assert SPEC is not None
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules["he_frontmatter_safety_lint"] = MODULE
SPEC.loader.exec_module(MODULE)


# ---------------------------------------------------------------------------
# Basic safety checks
# ---------------------------------------------------------------------------


def test_valid_frontmatter_passes() -> None:
    """Well-formed frontmatter for a traceable eval artifact passes safety lint."""
    markdown = """---
schema_version: 1
artifact_id: agent-skills-ask-control-plane-decomposition-eval
artifact_type: he-eval-report
canonical_slug: agent-skills-ask-control-plane-decomposition
title: Agent Skills Ask Control Plane Decomposition Eval
harness_stage: he-eval-report
status: complete
date: 2026-05-08
traceability_required: true
origin: .harness/plan/agent-skills-ask-control-plane-decomposition-plan.md
linear_issue: JSC-284
---

# Agent Skills Ask Control Plane Decomposition Eval
"""

    result = MODULE.lint_markdown(
        Path(".harness/evals/agent-skills-ask-control-plane-decomposition-eval.md"),
        markdown,
    )

    assert result.passed, f"Unexpected errors: {result.errors}"


def test_missing_frontmatter_fails() -> None:
    """Markdown without an opening frontmatter block must fail."""
    markdown = "# Title\n\nContent without frontmatter.\n"

    result = MODULE.lint_markdown(
        Path(".harness/evals/some-eval.md"),
        markdown,
    )

    assert not result.passed
    assert any("missing or malformed" in e for e in result.errors)


# ---------------------------------------------------------------------------
# Tests for PR changes: null/unknown linear_issue, new JSC-167 eval,
# new linear plan, and extra type field.
# ---------------------------------------------------------------------------


def test_jsc167_eval_frontmatter_passes_safety_lint() -> None:
    """The new JSC-167 eval frontmatter introduced in the PR must pass safety lint.

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
linear_milestone: Command surface and ask reliability
---

# Agent Skills JSC-167 Ask Bootstrap Command Discoverability Eval
"""

    result = MODULE.lint_markdown(
        Path(
            ".harness/evals/"
            "2026-05-10-JSC-167-agent-skills-jsc-167-ask-bootstrap-command-discoverability-eval.md"
        ),
        markdown,
    )

    assert result.passed, f"Unexpected errors: {result.errors}"


def test_linear_issue_null_value_is_safe_unquoted_scalar() -> None:
    """linear_issue: null must not be flagged as an unsafe unquoted scalar.

    Covers: conditional-he-gate-selection-eval.md which changed linear_issue
    from JSC-299 to null (and linear_status to not_applicable).
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

    for error in result.errors:
        assert "should be quoted for parser safety" not in error


def test_linear_status_not_applicable_is_safe_unquoted_scalar() -> None:
    """linear_status: not_applicable is a plain identifier and must not be
    flagged as requiring quotes.

    Covers the changed linear_status value in conditional-he-gate-selection-eval.md.
    """
    markdown = """---
schema_version: 1
artifact_id: some-eval
artifact_type: he-eval-report
canonical_slug: some-eval
title: Some Eval
harness_stage: he-eval-report
status: blocked
date: 2026-05-09
linear_status: not_applicable
---

# Some Eval
"""

    result = MODULE.lint_markdown(
        Path(".harness/evals/some-eval.md"),
        markdown,
    )

    for error in result.errors:
        assert "linear_status" not in error or "should be quoted" not in error


def test_linear_milestone_with_spaces_is_quoted_and_safe() -> None:
    """linear_milestone values with spaces must be quoted to pass safety lint.

    This covers the new linear plan and JSC-167 eval where the milestone
    'HE Authority And Proof Hardening' or 'Command surface and ask reliability'
    appears as a quoted value.
    """
    # Unquoted multi-word value with no unsafe chars is fine per the safety rules,
    # but single-word without unsafe chars is also fine.  Confirm a quoted value passes.
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


def test_new_linear_plan_authority_proof_hardening_passes_safety_lint() -> None:
    """The new HE authority-proof-hardening linear plan frontmatter passes safety lint.

    Covers: .harness/linear/2026-05-09-agent-skills-he-authority-proof-hardening-linear-plan.md
    with empty string linear_issue and traceability_required: false.
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


def test_decomposition_eval_with_extra_type_field_passes_safety_lint() -> None:
    """The decomposition eval with an additional 'type: he-eval-report' field
    must still pass frontmatter safety lint.

    Covers: agent-skills-ask-control-plane-decomposition-eval.md which gained
    'type: he-eval-report' in this PR.
    """
    markdown = """---
schema_version: 1
artifact_id: agent-skills-ask-control-plane-decomposition-eval
artifact_type: he-eval-report
type: he-eval-report
canonical_slug: agent-skills-ask-control-plane-decomposition
title: Agent Skills Ask Control Plane Decomposition Eval
harness_stage: he-eval-report
status: plan_ask_005_complete_linear_resolved
date: 2026-05-08
traceability_required: true
origin: .harness/plan/agent-skills-ask-control-plane-decomposition-plan.md
linear_issue: JSC-284
---

# Agent Skills Ask Control Plane Decomposition Eval
"""

    result = MODULE.lint_markdown(
        Path(".harness/evals/agent-skills-ask-control-plane-decomposition-eval.md"),
        markdown,
    )

    assert result.passed, f"Unexpected errors: {result.errors}"


def test_title_mismatch_h1_fails_safety_lint() -> None:
    """Frontmatter title that does not match the first H1 must fail safety lint."""
    markdown = """---
schema_version: 1
artifact_id: agent-skills-jsc-167-ask-bootstrap-command-discoverability-eval
artifact_type: he-eval-report
canonical_slug: agent-skills-jsc-167-ask-bootstrap-command-discoverability
title: Agent Skills JSC-167 Ask Bootstrap Command Discoverability Eval
harness_stage: he-eval-report
status: blocked
date: 2026-05-10
---

# Wrong Title For JSC-167
"""

    result = MODULE.lint_markdown(
        Path(".harness/evals/2026-05-10-JSC-167-agent-skills-jsc-167-ask-bootstrap-command-discoverability-eval.md"),
        markdown,
    )

    assert not result.passed
    assert any("title" in e for e in result.errors)


def test_date_prefixed_filename_with_uppercase_issue_key_validates_date_safety() -> None:
    """Date extraction from 2026-05-10-JSC-167-... filename must work correctly.

    A mismatched date in frontmatter must fail; a matching date must pass.
    """
    good_markdown = """---
schema_version: 1
artifact_id: agent-skills-jsc-167-ask-bootstrap-command-discoverability-eval
artifact_type: he-eval-report
canonical_slug: agent-skills-jsc-167-ask-bootstrap-command-discoverability
title: Agent Skills JSC-167 Ask Bootstrap Command Discoverability Eval
harness_stage: he-eval-report
status: blocked
date: 2026-05-10
---

# Agent Skills JSC-167 Ask Bootstrap Command Discoverability Eval
"""
    bad_markdown = good_markdown.replace("date: 2026-05-10", "date: 2026-01-01")

    good_path = Path(
        ".harness/evals/"
        "2026-05-10-JSC-167-agent-skills-jsc-167-ask-bootstrap-command-discoverability-eval.md"
    )

    good_result = MODULE.lint_markdown(good_path, good_markdown)
    for error in good_result.errors:
        assert "date-prefixed filename must match frontmatter date" not in error

    bad_result = MODULE.lint_markdown(good_path, bad_markdown)
    assert not bad_result.passed
    assert "date-prefixed filename must match frontmatter date" in bad_result.errors


def test_traceable_artifact_missing_date_fails() -> None:
    """A traceable .harness eval without a date field must fail safety lint."""
    markdown = """---
schema_version: 1
artifact_id: agent-skills-jsc-167-ask-bootstrap-command-discoverability-eval
artifact_type: he-eval-report
canonical_slug: agent-skills-jsc-167-ask-bootstrap-command-discoverability
title: Agent Skills JSC-167 Ask Bootstrap Command Discoverability Eval
harness_stage: he-eval-report
status: blocked
---

# Agent Skills JSC-167 Ask Bootstrap Command Discoverability Eval
"""

    result = MODULE.lint_markdown(
        Path(".harness/evals/some-eval.md"),
        markdown,
    )

    assert not result.passed
    assert any("date" in e for e in result.errors)