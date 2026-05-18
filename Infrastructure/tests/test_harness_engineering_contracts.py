import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PLUGIN_ROOT = REPO_ROOT / "Plugins" / "harness-engineering"


def load_shape_checker():
    script = PLUGIN_ROOT / "scripts" / "check_generated_artifact_shape.py"
    spec = importlib.util.spec_from_file_location("check_generated_artifact_shape", script)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_lifecycle_tracer_covers_main_stages() -> None:
    tracer = PLUGIN_ROOT / "references" / "lifecycle-tracer-evals.yaml"
    text = tracer.read_text(encoding="utf-8")

    for stage in [
        "he-brainstorm",
        "he-spec",
        "he-plan",
        "he-work",
        "he-fix-bugs",
        "he-improve",
        "he-code-review",
        "he-heartbeat",
        "he-reconcile",
        "he-reinforce",
        "he-eval-report",
        "he-strategy",
        "he-reframe",
        "he-linear-plan",
    ]:
        assert f"stage: {stage}" in text
        assert f"expected_route: {stage}" in text

    assert "stage: he-compound" in text
    assert "expected_route: he-reconcile" in text
    assert "expected_route: he-reinforce" in text


def test_deferred_context_index_stays_router_with_preserved_context() -> None:
    index = PLUGIN_ROOT / "references" / "deferred-context-index.md"
    text = index.read_text(encoding="utf-8")

    assert "references/goal-continuity.md" in text
    assert "references/artifact-classification-and-traceability.md" in text
    assert "## Preserved Entry Point Lines" in text
    assert "Return schema_version when structured." not in text


def test_pragmatic_contract_is_wired_to_review_surfaces() -> None:
    pragmatic = "pragmatic-programmer-review-contract.md"
    strategy = PLUGIN_ROOT / "skills" / "he-strategy" / "SKILL.md"
    code_review = PLUGIN_ROOT / "skills" / "he-code-review" / "SKILL.md"

    assert pragmatic in strategy.read_text(encoding="utf-8")
    assert pragmatic in code_review.read_text(encoding="utf-8")


def test_apparatus_enforcement_contract_is_wired_to_he_spec_and_plan() -> None:
    lens = "skills-sdk-apparatus-lens.md"
    fields = [
        "essential_decisions",
        "fillable_gaps",
        "guardrails",
        "refusal_triggers",
        "durable_memory",
        "professional_output",
    ]
    surfaces = [
        PLUGIN_ROOT / "skills" / "he-spec" / "SKILL.md",
        PLUGIN_ROOT / "skills" / "he-plan" / "SKILL.md",
        PLUGIN_ROOT / "references" / "skills" / "he-spec" / "spec-artifact-contract.md",
        PLUGIN_ROOT / "references" / "skills" / "he-plan" / "plan-artifact-contract.md",
    ]

    for surface in surfaces:
        text = surface.read_text(encoding="utf-8")
        assert lens in text
        for field in fields:
            assert field in text


def test_generated_artifact_shape_requires_enforcement_contract_fields() -> None:
    checker = load_shape_checker()
    body = """
## Command Summary
BLUF: Test artifact.
## Purpose
Purpose.
## Problem Statement
Problem.
## User / Operator Scenarios
Scenario.
## Goals
Goal.
## Non-Goals
Non-goal.
## Current State / Evidence
Evidence.
## Proposed Behavior
Behavior.
## Requirements
FR-001: Requirement.
## Interfaces
Interface.
## Data / Domain Contract
Contract.
## Enforcement Contract
essential_decisions:
- Locked API shape.
fillable_gaps:
- Boilerplate tests.
guardrails:
- python3 -m pytest tests/example.py -q
refusal_triggers:
- Stop on schema changes.
durable_memory:
- Closeout artifact.
## Security, Privacy, and Safety
Safety.
## Failure and Recovery
Rollback.
## Validation Plan
Validation.
## Acceptance Criteria
SA-001: Acceptance.
## Visual References / Diagrams
Not needed: no multi-surface flow.
## Evidence and References
Reference.
"""

    errors = checker.validate_spec(body)

    assert "Enforcement Contract missing required field: professional_output" in errors
