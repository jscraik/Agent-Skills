from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "validation-and-linting"
    / "he_artifact_identity_lint.py"
)
SPEC = importlib.util.spec_from_file_location("he_artifact_identity_lint", SCRIPT_PATH)
assert SPEC is not None
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules["he_artifact_identity_lint"] = MODULE
SPEC.loader.exec_module(MODULE)


def test_valid_tracked_plan_identity_passes() -> None:
    markdown = """---
schema_version: 1
artifact_id: agent-skills-ask-control-plane-decomposition-plan
artifact_type: he-plan
canonical_slug: agent-skills-ask-control-plane-decomposition
title: Agent Skills Ask Control Plane Decomposition Plan
harness_stage: he-plan
status: draft
traceability_required: true
linear_issue: JSC-284
origin: .harness/specs/agent-skills-ask-control-plane-decomposition-spec.md
---

# Agent Skills Ask Control Plane Decomposition Plan
"""

    result = MODULE.lint_markdown(
        Path(".harness/plan/agent-skills-ask-control-plane-decomposition-plan.md"),
        markdown,
    )

    assert result.passed


def test_valid_dated_issue_prefixed_plan_identity_passes() -> None:
    markdown = """---
schema_version: 1
artifact_id: jsc-283-packaged-skill-behavior-assurance-plan
artifact_type: he-plan
canonical_slug: jsc-283-packaged-skill-behavior-assurance
title: JSC-283 Packaged Skill Behavior Assurance Plan
harness_stage: he-plan
status: draft
date: 2026-05-08
traceability_required: true
linear_issue: JSC-283
origin: .harness/specs/2026-05-08-jsc-283-packaged-skill-behavior-assurance-spec.md
---

# JSC-283 Packaged Skill Behavior Assurance Plan
"""

    result = MODULE.lint_markdown(
        Path(".harness/plan/2026-05-08-architecture-JSC-283-packaged-skill-behavior-assurance-plan.md"),
        markdown,
    )

    assert result.passed


def test_title_must_match_h1() -> None:
    markdown = """---
schema_version: 1
artifact_id: agent-skills-ask-control-plane-decomposition-plan
artifact_type: he-plan
canonical_slug: agent-skills-ask-control-plane-decomposition
title: Agent Skills Ask Control Plane Decomposition Plan
harness_stage: he-plan
status: draft
---

# Ask Control Plane Decomposition Plan
"""

    result = MODULE.lint_markdown(
        Path(".harness/plan/agent-skills-ask-control-plane-decomposition-plan.md"),
        markdown,
    )

    assert not result.passed
    assert "frontmatter title must match the first H1 heading" in result.errors


def test_harness_root_stage_must_match() -> None:
    markdown = """---
schema_version: 1
artifact_id: agent-skills-ask-control-plane-decomposition-eval
artifact_type: he-plan
canonical_slug: agent-skills-ask-control-plane-decomposition
title: Agent Skills Ask Control Plane Decomposition Eval
harness_stage: he-plan
status: draft
---

# Agent Skills Ask Control Plane Decomposition Eval
"""

    result = MODULE.lint_markdown(
        Path(".harness/evals/agent-skills-ask-control-plane-decomposition-eval.md"),
        markdown,
    )

    assert not result.passed
    assert "frontmatter harness_stage must be he-eval-report for this .harness root" in result.errors


def test_traceability_requires_tracker_or_milestone_and_origin() -> None:
    markdown = """---
schema_version: 1
artifact_id: agent-skills-ask-control-plane-decomposition-plan
artifact_type: he-plan
canonical_slug: agent-skills-ask-control-plane-decomposition
title: Agent Skills Ask Control Plane Decomposition Plan
harness_stage: he-plan
status: draft
traceability_required: true
---

# Agent Skills Ask Control Plane Decomposition Plan
"""

    result = MODULE.lint_markdown(
        Path(".harness/plan/agent-skills-ask-control-plane-decomposition-plan.md"),
        markdown,
    )

    assert not result.passed
    assert "traceability_required artifacts need linear_issue or linear_milestone" in result.errors
    assert "traceability_required artifacts need origin or source_artifacts" in result.errors


def test_linear_issue_must_be_in_canonical_slug() -> None:
    markdown = """---
schema_version: 1
artifact_id: packaged-skill-behavior-assurance-plan
artifact_type: he-plan
canonical_slug: packaged-skill-behavior-assurance
title: JSC-283 Packaged Skill Behavior Assurance Plan
harness_stage: he-plan
status: draft
date: 2026-05-08
traceability_required: true
linear_issue: JSC-283
origin: .harness/specs/2026-05-08-jsc-283-packaged-skill-behavior-assurance-spec.md
---

# JSC-283 Packaged Skill Behavior Assurance Plan
"""

    result = MODULE.lint_markdown(
        Path(".harness/plan/2026-05-08-packaged-skill-behavior-assurance-plan.md"),
        markdown,
    )

    assert not result.passed
    assert "frontmatter canonical_slug must include lower-case linear_issue" in result.errors


def test_date_prefixed_filename_must_match_frontmatter_date() -> None:
    markdown = """---
schema_version: 1
artifact_id: jsc-283-packaged-skill-behavior-assurance-plan
artifact_type: he-plan
canonical_slug: jsc-283-packaged-skill-behavior-assurance
title: JSC-283 Packaged Skill Behavior Assurance Plan
harness_stage: he-plan
status: draft
date: 2026-05-07
traceability_required: true
linear_issue: JSC-283
origin: .harness/specs/2026-05-08-jsc-283-packaged-skill-behavior-assurance-spec.md
---

# JSC-283 Packaged Skill Behavior Assurance Plan
"""

    result = MODULE.lint_markdown(
        Path(".harness/plan/2026-05-08-jsc-283-packaged-skill-behavior-assurance-plan.md"),
        markdown,
    )

    assert not result.passed
    assert "date-prefixed filenames must have matching frontmatter date" in result.errors


# ---------------------------------------------------------------------------
# Tests for new eval artifacts added in PR (harness control-plane refactor)
# ---------------------------------------------------------------------------


def test_valid_ask_control_plane_decomposition_eval_identity_passes() -> None:
    """Frontmatter matching the new ask-control-plane-decomposition eval file passes."""
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


def test_valid_jsc_284_eval_identity_passes() -> None:
    """Frontmatter matching the new JSC-284 eval report passes validation."""
    markdown = """---
schema_version: 1
artifact_id: agent-skills-jsc-284-he-eval-report
artifact_type: he-eval-report
canonical_slug: agent-skills-jsc-284
title: Agent Skills JSC-284 Eval Report
harness_stage: he-eval-report
status: complete
traceability_required: true
origin: .harness/plan/agent-skills-ask-control-plane-decomposition-plan.md
linear_issue: JSC-284
---

# Agent Skills JSC-284 Eval Report
"""

    result = MODULE.lint_markdown(
        Path(".harness/evals/agent-skills-jsc-284-eval.md"),
        markdown,
    )

    assert result.passed, f"Unexpected errors: {result.errors}"


def test_eval_artifact_type_must_contain_harness_stage() -> None:
    """artifact_type must contain the expected harness_stage (he-eval-report for evals/)."""
    markdown = """---
schema_version: 1
artifact_id: agent-skills-ask-control-plane-decomposition-eval
artifact_type: he-plan
canonical_slug: agent-skills-ask-control-plane-decomposition
title: Agent Skills Ask Control Plane Decomposition Eval
harness_stage: he-eval-report
status: draft
---

# Agent Skills Ask Control Plane Decomposition Eval
"""

    result = MODULE.lint_markdown(
        Path(".harness/evals/agent-skills-ask-control-plane-decomposition-eval.md"),
        markdown,
    )

    assert not result.passed
    assert "frontmatter artifact_type must include the owning harness_stage" in result.errors


def test_eval_missing_frontmatter_fails() -> None:
    """Eval markdown without YAML frontmatter must fail with a clear error."""
    markdown = """# Agent Skills Ask Control Plane Decomposition Eval

Some content without frontmatter.
"""

    result = MODULE.lint_markdown(
        Path(".harness/evals/agent-skills-ask-control-plane-decomposition-eval.md"),
        markdown,
    )

    assert not result.passed
    assert "missing YAML frontmatter" in result.errors


def test_eval_canonical_slug_must_be_in_artifact_id() -> None:
    """canonical_slug must appear in artifact_id for eval artifacts."""
    markdown = """---
schema_version: 1
artifact_id: unrelated-eval-identifier
artifact_type: he-eval-report
canonical_slug: agent-skills-ask-control-plane-decomposition
title: Agent Skills Ask Control Plane Decomposition Eval
harness_stage: he-eval-report
status: draft
---

# Agent Skills Ask Control Plane Decomposition Eval
"""

    result = MODULE.lint_markdown(
        Path(".harness/evals/unrelated-eval-identifier.md"),
        markdown,
    )

    assert not result.passed
    assert "frontmatter artifact_id must contain canonical_slug" in result.errors


def test_eval_jsc_284_canonical_slug_contains_issue_key() -> None:
    """When linear_issue JSC-284 appears in path/artifact_id, canonical_slug must include jsc-284."""
    markdown = """---
schema_version: 1
artifact_id: agent-skills-jsc-284-he-eval-report
artifact_type: he-eval-report
canonical_slug: agent-skills-report
title: Agent Skills JSC-284 Eval Report
harness_stage: he-eval-report
status: complete
traceability_required: true
origin: .harness/plan/agent-skills-ask-control-plane-decomposition-plan.md
linear_issue: JSC-284
---

# Agent Skills JSC-284 Eval Report
"""

    result = MODULE.lint_markdown(
        Path(".harness/evals/agent-skills-jsc-284-eval.md"),
        markdown,
    )

    assert not result.passed
    assert "frontmatter canonical_slug must include lower-case linear_issue" in result.errors


def test_eval_traceability_required_without_origin_fails() -> None:
    """traceability_required: true without origin or source_artifacts must fail."""
    markdown = """---
schema_version: 1
artifact_id: agent-skills-ask-control-plane-decomposition-eval
artifact_type: he-eval-report
canonical_slug: agent-skills-ask-control-plane-decomposition
title: Agent Skills Ask Control Plane Decomposition Eval
harness_stage: he-eval-report
status: complete
traceability_required: true
linear_issue: JSC-284
---

# Agent Skills Ask Control Plane Decomposition Eval
"""

    result = MODULE.lint_markdown(
        Path(".harness/evals/agent-skills-ask-control-plane-decomposition-eval.md"),
        markdown,
    )

    assert not result.passed
    assert "traceability_required artifacts need origin or source_artifacts" in result.errors


def test_eval_title_must_match_h1_heading() -> None:
    """frontmatter title must match the first H1 heading in eval artifacts."""
    markdown = """---
schema_version: 1
artifact_id: agent-skills-jsc-284-he-eval-report
artifact_type: he-eval-report
canonical_slug: agent-skills-jsc-284
title: Agent Skills JSC-284 Eval Report
harness_stage: he-eval-report
status: complete
---

# Wrong Heading For JSC-284 Report
"""

    result = MODULE.lint_markdown(
        Path(".harness/evals/agent-skills-jsc-284-eval.md"),
        markdown,
    )

    assert not result.passed
    assert "frontmatter title must match the first H1 heading" in result.errors


def test_eval_filename_must_contain_canonical_slug() -> None:
    """The eval filename stem must contain the canonical_slug."""
    markdown = """---
schema_version: 1
artifact_id: agent-skills-ask-control-plane-decomposition-eval
artifact_type: he-eval-report
canonical_slug: agent-skills-ask-control-plane-decomposition
title: Agent Skills Ask Control Plane Decomposition Eval
harness_stage: he-eval-report
status: complete
---

# Agent Skills Ask Control Plane Decomposition Eval
"""

    result = MODULE.lint_markdown(
        Path(".harness/evals/completely-different-name-eval.md"),
        markdown,
    )

    assert not result.passed
    assert "filename stem must contain canonical_slug" in result.errors


def test_eval_schema_version_is_required() -> None:
    """schema_version is a required field for eval artifacts."""
    markdown = """---
artifact_id: agent-skills-jsc-284-he-eval-report
artifact_type: he-eval-report
canonical_slug: agent-skills-jsc-284
title: Agent Skills JSC-284 Eval Report
harness_stage: he-eval-report
status: complete
---

# Agent Skills JSC-284 Eval Report
"""

    result = MODULE.lint_markdown(
        Path(".harness/evals/agent-skills-jsc-284-eval.md"),
        markdown,
    )

    assert not result.passed
    assert "frontmatter schema_version is required" in result.errors
