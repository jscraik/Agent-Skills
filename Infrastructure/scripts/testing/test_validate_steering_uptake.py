from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = (
    REPO_ROOT
    / "Infrastructure"
    / "scripts"
    / "validation-and-linting"
    / "validate_steering_uptake.py"
)


def _load_validator():
    spec = importlib.util.spec_from_file_location("validate_steering_uptake", SCRIPT)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_transferable_feedback_requires_systems_thinking_fields(tmp_path):
    validator = _load_validator()
    ledger = tmp_path / "steering-uptake.md"
    ledger.write_text(
        """# Steering Uptake Ledger

## Active Rule

High-signal steering must become an environment mechanism.

## Uptake Record: bad local-only api feedback

Operating failure: The agent fixed only the named function.

Feedback type: api_design_rule

Intent radius: package

Blocker: Equivalent APIs can keep the same misuse pattern.

Horizontal OODA: Same API layer.

Vertical OODA: Review comment to implementation.

Durable surface: Interface guidance.

Pattern sweep: Searched the package.

Disposition: fixed now.

Validation: Validator should reject this record.

Repeat prevention: Missing mechanism and proof should block closeout.
""",
        encoding="utf-8",
    )

    result = validator.validate_ledger(ledger)

    assert result["status"] == "fail"
    assert any(
        "missing required marker 'Environment refinement:'" in error
        for error in result["errors"]
    )
    assert any("missing required marker 'Mechanism:'" in error for error in result["errors"])
    assert any("missing required marker 'Proof:'" in error for error in result["errors"])
    assert any("requires 'Sweep scope:'" in error for error in result["errors"])
    assert any("requires 'Search terms:'" in error for error in result["errors"])
    assert any("requires 'Matches considered:'" in error for error in result["errors"])
    assert any("requires 'Exclusions:'" in error for error in result["errors"])


def test_api_design_feedback_requires_semantic_pattern_sweep(tmp_path):
    validator = _load_validator()
    ledger = tmp_path / "steering-uptake.md"
    ledger.write_text(
        """# Steering Uptake Ledger

## Active Rule

Every Jamie steering item is a high-signal candidate until classified.
Do not resume ordinary task work until environment refinement is proven by a
systems thinker.
Use horizontal OODA and vertical OODA when steering spans a cross-boundary
target context window outside the active turn.

## Uptake Record: bool return feedback

Operating failure: The agent changed only function XYZ.

Feedback type: api_design_rule

Intent radius: package

Blocker: Similar APIs can keep returning bare bools for operational failure.

Pattern sweep: Searched the package.

Disposition: fixed now.

Horizontal OODA: Same API layer.

Vertical OODA: Review comment to repository-wide API design.

Durable surface: Interface guidance.

Environment refinement: Validator should reject shallow sweep evidence.

Mechanism: API design feedback must force semantic sweep evidence.

Proof: This fixture omits sweep fields.

Validation: Validator should reject this record.

Repeat prevention: Missing sweep detail should block closeout.
""",
        encoding="utf-8",
    )

    result = validator.validate_ledger(ledger)

    assert result["status"] == "fail"
    assert any("requires 'Sweep scope:'" in error for error in result["errors"])
    assert any("requires 'Search terms:'" in error for error in result["errors"])
    assert any("requires 'Matches considered:'" in error for error in result["errors"])
    assert any("requires 'Exclusions:'" in error for error in result["errors"])
    assert any("transferable feedback requires 'Generalized rule:'" in error for error in result["errors"])
    assert any("transferable feedback requires 'Similar-case disposition:'" in error for error in result["errors"])


def test_api_design_feedback_cannot_be_line_or_function_scoped(tmp_path):
    validator = _load_validator()
    ledger = tmp_path / "steering-uptake.md"
    ledger.write_text(
        """# Steering Uptake Ledger

## Active Rule

Every Jamie steering item is a high-signal candidate until classified.
Do not resume ordinary task work until environment refinement is proven by a
systems thinker.

## Uptake Record: bool return line fix

Operating failure: The agent treated API design feedback as a one-function edit.

Feedback type: api_design_rule

Intent radius: function

Blocker: Similar APIs can keep returning bare bools for operational failure.

Pattern sweep: Searched only function XYZ.

Sweep scope: function XYZ.

Search terms: bool return.

Matches considered: function XYZ only.

Exclusions: Other package APIs were skipped.

Generalized rule: Operational API failures should return named errors, not bare booleans.

Similar-case disposition: function XYZ fixed now; no broader API cases classified.

Disposition: fixed now.

Horizontal OODA: Same API layer.

Vertical OODA: Review comment to repository API design.

Durable surface: Interface guidance.

Environment refinement: Validator should reject function-scoped API design uptake.

Mechanism: API design feedback must force a broader radius.

Proof: This fixture uses function radius.

Validation: Validator should reject this record.

Repeat prevention: Function-scoped API design uptake should fail.
""",
        encoding="utf-8",
    )

    result = validator.validate_ledger(ledger)

    assert result["status"] == "fail"
    assert any("transferable feedback cannot be scoped to function" in error for error in result["errors"])


def test_non_api_transferable_feedback_requires_generalized_rule(tmp_path):
    validator = _load_validator()
    ledger = tmp_path / "steering-uptake.md"
    ledger.write_text(
        """# Steering Uptake Ledger

## Active Rule

Every Jamie steering item is a high-signal candidate until classified.
Do not resume ordinary task work until environment refinement is proven by a
systems thinker.

## Uptake Record: validation example overfit

Operating failure: The agent fixed one validator case while missing the wider validation rule.

Feedback type: validation_gap

Intent radius: repository

Blocker: Equivalent validation gaps can remain after one named example is fixed.

Pattern sweep: Checked validator surfaces.

Sweep scope: validators and tests.

Search terms: warning, blocker, closeout.

Matches considered: validator cases and closeout summaries.

Exclusions: unrelated package code.

Disposition: fixed now.

Horizontal OODA: Validation and closeout context.

Vertical OODA: Feedback to future validation behavior.

Durable surface: Validator guidance.

Environment refinement: Validator should reject missing generalized rule.

Mechanism: Transferable feedback needs generalization across domains, not only API design.

Proof: This fixture omits generalized markers.

Validation: Validator should reject this record.

Repeat prevention: Non-API feedback cannot pass as a one-example fix.
""",
        encoding="utf-8",
    )

    result = validator.validate_ledger(ledger)

    assert result["status"] == "fail"
    assert any("transferable feedback requires 'Generalized rule:'" in error for error in result["errors"])
    assert any("transferable feedback requires 'Similar-case disposition:'" in error for error in result["errors"])


def test_repeated_error_feedback_requires_research_protocol(tmp_path):
    validator = _load_validator()
    ledger = tmp_path / "steering-uptake.md"
    ledger.write_text(
        """# Steering Uptake Ledger

## Active Rule

Every Jamie steering item is a high-signal candidate until classified.
Do not resume ordinary task work until environment refinement is proven by a
systems thinker.

## Uptake Record: repeated error loop

Operating failure: The agent retried the same failure without changing approach.

Feedback type: repeated_error_protocol

Intent radius: repository

Blocker: The same error twice can waste time and hide known fixes.

Pattern sweep: Checked workflow guidance.

Sweep scope: workflow guidance.

Search terms: repeated error.

Matches considered: retry guidance.

Exclusions: source code.

Disposition: fixed now.

Horizontal OODA: Tooling and web context.

Vertical OODA: Error, research, option selection, implementation.

Durable surface: Workflow guidance.

Environment refinement: Validator should reject missing repeated error protocol.

Mechanism: Repeated errors need a protocol.

Proof: This fixture omits the protocol.

Validation: Validator should fail.

Repeat prevention: Missing protocol should block closeout.
""",
        encoding="utf-8",
    )

    result = validator.validate_ledger(ledger)

    assert result["status"] == "fail"
    assert any("Repeated error protocol:" in error for error in result["errors"])


def test_cross_boundary_ooda_feedback_requires_scaling_protocol(tmp_path):
    validator = _load_validator()
    ledger = tmp_path / "steering-uptake.md"
    ledger.write_text(
        """# Steering Uptake Ledger

## Active Rule

Every Jamie steering item is a high-signal candidate until classified.
Do not resume ordinary task work until environment refinement is proven by a
systems thinker. Use horizontal OODA and vertical OODA with cross-boundary
target context window reflection when context sits outside the active turn.

## Uptake Record: cross-boundary OODA gap

Operating failure: The agent oriented only on the active turn.

Feedback type: agent_operating_rule

Intent radius: repository

Blocker: Cross-boundary context can live outside the current transcript.

Pattern sweep: Checked steering surfaces.

Sweep scope: steering protocol and validator.

Search terms: cross-boundary, target context window, stacked trajectories.

Matches considered: steering protocol.

Exclusions: implementation code.

Generalized rule: Cross-boundary OODA requires deliberate context-window reflection.

Similar-case disposition: policy surface fixed now.

Disposition: fixed now.

Horizontal OODA: Adjacent org activity can change what action is safe.

Vertical OODA: Stacked trajectories can change what action is complete.

Durable surface: Steering protocol.

Environment refinement: Validator should reject missing OODA scaling protocol.

Mechanism: Cross-boundary steering must name the reflection loop.

Proof: This fixture omits the protocol.

Validation: Validator should fail.

Repeat prevention: Missing context-window protocol should block closeout.
""",
        encoding="utf-8",
    )

    result = validator.validate_ledger(ledger)

    assert result["status"] == "fail"
    assert any("OODA scaling protocol:" in error for error in result["errors"])


def test_incidental_diagnostic_and_repeated_error_words_do_not_trigger_specialized_rules(tmp_path):
    validator = _load_validator()
    ledger = tmp_path / "steering-uptake.md"
    ledger.write_text(
        """# Steering Uptake Ledger

## Active Rule

Every Jamie steering item is a high-signal candidate until classified.
Do not resume ordinary task work until environment refinement is proven by a
systems thinker.
Use horizontal OODA and vertical OODA when steering spans a cross-boundary
target context window outside the active turn.

## Uptake Record: transferable operating principle

Operating failure: The agent treated one example as isolated feedback.

Feedback type: agent_operating_rule

Intent radius: repository

Blocker: The rule mentions diagnostic reporting and same error twice only as examples.

Generalized rule: Extract the transferable principle before editing.

Similar-case disposition: policy surface fixed now; implementation sweeps run only when active.

Pattern sweep: Checked the steering policy surface.

Sweep scope: steering policy docs.

Search terms: diagnostic reporting, same error twice.

Matches considered: incidental wording in the operating-rule example.

Exclusions: source code because this fixture tests validator triggering only.

Disposition: fixed now.

Horizontal OODA: Steering, validation, diagnostics, and repeated errors can all carry examples.

Vertical OODA: Move from example to principle to durable surface.

Durable surface: Steering validator.

Environment refinement: Validator keys specialized requirements off feedback type.

Mechanism: Incidental prose does not toggle diagnostic or repeated-error gates.

Proof: This fixture intentionally omits specialized markers and should pass.

Validation: Validator should pass.

Repeat prevention: Future prose examples should not create false-negative ledger validation.
""",
        encoding="utf-8",
    )

    result = validator.validate_ledger(ledger)

    assert result == {
        "path": str(ledger),
        "status": "pass",
        "errors": [],
    }


def test_active_rule_requires_default_high_signal_candidate_posture(tmp_path):
    validator = _load_validator()
    ledger = tmp_path / "steering-uptake.md"
    ledger.write_text(
        """# Steering Uptake Ledger

## Active Rule

High-signal steering must become an environment mechanism.

## Uptake Record: otherwise complete record

Operating failure: The agent missed the classification default.

Feedback type: agent_operating_rule

Intent radius: repository

Blocker: Future agents may wait for magic trigger phrases.

Pattern sweep: Searched steering surfaces.

Disposition: fixed now.

Horizontal OODA: Repo operating context.

Vertical OODA: Future steering and closeout.

Durable surface: Steering ledger.

Environment refinement: Validator should reject the active rule.

Mechanism: The active rule must encode the default classification posture.

Proof: This fixture omits the required wording.

Validation: Validator should fail.

Repeat prevention: Missing default posture should block closeout.
""",
        encoding="utf-8",
    )

    result = validator.validate_ledger(ledger)

    assert result["status"] == "fail"
    assert any("high-signal candidate" in error for error in result["errors"])


def test_active_rule_requires_halt_and_environment_refinement_posture(tmp_path):
    validator = _load_validator()
    ledger = tmp_path / "steering-uptake.md"
    ledger.write_text(
        """# Steering Uptake Ledger

## Active Rule

Every Jamie steering item is a high-signal candidate until classified.

## Uptake Record: otherwise complete record

Operating failure: The agent classified feedback but kept working the old lane.

Feedback type: agent_operating_rule

Intent radius: repository

Blocker: The active rule did not force a halt-and-prove loop.

Pattern sweep: Searched steering surfaces.

Disposition: fixed now.

Horizontal OODA: Repo operating context.

Vertical OODA: Future steering and closeout.

Durable surface: Steering ledger.

Environment refinement: Validator should reject the active rule.

Mechanism: The active rule must require halt, refinement, and proof.

Proof: This fixture omits the required wording.

Validation: Validator should fail.

Repeat prevention: Missing halt posture should block closeout.
""",
        encoding="utf-8",
    )

    result = validator.validate_ledger(ledger)

    assert result["status"] == "fail"
    assert any("do not resume ordinary task work" in error for error in result["errors"])
    assert any("environment refinement" in error for error in result["errors"])
    assert any("systems thinker" in error for error in result["errors"])


def test_current_ledger_satisfies_systems_thinking_contract():
    validator = _load_validator()
    result = validator.validate_ledger(REPO_ROOT / ".harness/quality/steering-uptake.md")

    assert result == {
        "path": str(REPO_ROOT / ".harness/quality/steering-uptake.md"),
        "status": "pass",
        "errors": [],
    }


def test_diagnostic_feedback_requires_category_owner_and_next_action(tmp_path):
    validator = _load_validator()
    ledger = tmp_path / "steering-uptake.md"
    ledger.write_text(
        """# Steering Uptake Ledger

## Active Rule

High-signal steering must become an environment mechanism.

## Uptake Record: diagnostic debt flattening

Operating failure: The agent called diagnostic findings nonblocking without classifying them.

Feedback type: diagnostic_debt

Intent radius: repository

Blocker: Large diagnostic counts can hide ownership debt.

Horizontal OODA: Repo doctor, closeout, and validation reporting all consume diagnostics.

Vertical OODA: The rule must carry from warning to owner decision.

Durable surface: Validator and repo doctor.

Pattern sweep: Checked diagnostic reporting surfaces.

Disposition: policy surface updates now.

Environment refinement: Validator should reject vague diagnostic uptake.

Mechanism: Diagnostic records need a structured classification.

Proof: This test fixture omits the classification.

Validation: Run the steering uptake validator.

Repeat prevention: Future agents must classify diagnostic debt before closeout.
""",
        encoding="utf-8",
    )

    result = validator.validate_ledger(ledger)

    assert result["status"] == "fail"
    assert any(
        "diagnostic feedback requires 'Diagnostic classification:'" in error
        for error in result["errors"]
    )
