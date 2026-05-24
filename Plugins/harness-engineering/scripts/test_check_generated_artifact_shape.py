#!/usr/bin/env python3
"""Focused tests for generated HE artifact shape validation."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).with_name("check_generated_artifact_shape.py")
SPEC = importlib.util.spec_from_file_location("check_generated_artifact_shape", MODULE_PATH)
assert SPEC is not None
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


VALID_SPEC = """
## Command Summary
BLUF: This spec defines account insights for customers.
## Purpose
Make account insight behavior reviewable.
## Problem Statement
Customers cannot see enough spending context to make informed decisions.
## User / Operator Scenarios
### User Stories
1. As a mobile bank customer, I want balance insights, so that I can make better spending decisions.
2. As an overdraft-risk customer, I want early warning context, so that I can avoid fees.
3. As a support operator, I want insight state to be explainable, so that I can answer customer questions.
## Goals
Improve insight confidence.
## Non-Goals
Automated money movement.
## Current State / Evidence
Linear JSC-312 and source artifact SA-001.
## Authority and Scope Boundary
requested_depth: full_implementation
approved_execution_boundary: Linear JSC-312 approved source artifact.
downscope_authority: not_applicable
external_mutation_boundary: none
freshness_required: branch
human_acceptance_boundary: required
## Proposed Behavior
### User-Facing Solution
Users see read-only account insights before taking action.
## Requirements
FR-001 Insights MUST be read-only.
## Interfaces
No public API change.
## Data / Domain Contract
No schema change. Required fields, optional fields, compatibility, versioning,
unknown-field behavior, and error handling are not changed.
## Enforcement Contract
essential_decisions: read-only insight behavior.
fillable_gaps: display copy and existing surface wiring.
guardrails: focused behavior test.
refusal_triggers: any money movement or new persistence.
durable_memory: not_applicable.
professional_output: files changed, commands, rollback, and blockers.
## Proof and Runtime Boundary
proof_boundary: focused behavior validation plus acceptance evidence.
non_proof_sources: chat_summary, raw_logs, aggregate_stats, stale_session.
runtime_state: not_applicable.
resumption_key: .harness/specs/account-insights.md#SA-001.
runtime_invocation_receipt: not_applicable.
artifact_chain_key: account-insights.
persistent_artifacts: .harness/specs/account-insights.md.
live_state_refresh: required.
session_evidence_status: not_used.
## Coding and Testing Lenses
coding_lens: account insight surface only; no API, schema, or money movement.
testing_lens: observable behavior for SA-001 with positive, negative, and stale-state checks.
## Security, Privacy, and Safety
No secrets.
## Accessibility and Operator Ergonomics
Readable status text and non-color-only unavailable state.
## Failure and Recovery
Show unavailable state.
## Validation Plan
Test external behavior and acceptance evidence.
## Acceptance Criteria
SA-001 Read-only insights are visible.
## Visual References / Diagrams
Not needed: single-surface read-only display.
## Evidence and References
JSC-312.
"""


VALID_PLAN = """
## Command Summary
BLUF: This plan implements account insights safely.
## Objective
Implement read-only insights.
## Source Contract
FR-001 and SA-001.
## Scope and Boundaries
Read-only behavior.
## Authority and Scope Boundary
requested_depth: approved_slice
approved_execution_boundary: .harness/specs/account-insights.md SA-001.
downscope_authority: not_applicable
external_mutation_boundary: none
freshness_required: branch
human_acceptance_boundary: required
## Current State / Evidence
Spec exists.
## Implementation Strategy
Use existing account summary surface.
## Runtime Persistence and State
runtime_state: PU-001 ready for implementation.
resumption_key: .harness/plan/account-insights.md#PU-001.
runtime_invocation_receipt: not_applicable.
artifact_chain_key: account-insights.
persistent_artifacts: .harness/plan/account-insights.md.
live_state_refresh: required.
session_evidence_status: not_used.
proof_boundary: focused behavior validation for SA-001.
## Enforcement Contract
essential_decisions: insight behavior stays read-only.
fillable_gaps: wiring into existing account summary.
guardrails: focused behavior validation.
refusal_triggers: any account mutation or new public API.
durable_memory: not_applicable.
professional_output: files changed, commands, blockers, next action, rollback.
## Coding and Testing Lenses
coding_lens: allowed path account insight surface; forbidden path payment execution; no public API or schema change.
testing_lens: observable behavior proof for SA-001 using prior-art account summary tests plus negative mutation check.
## Work Units
### PU-001 Read-only insight surface
Source: FR-001, SA-001.
Allowed path: account insight surface.
Forbidden path: payment execution.
Validation: external behavior check.
Stop condition: insight action mutates account state.
Rollback: remove insight registration.
Handoff: he-code-review.
## Validation Gates
Required: observable behavior proof for SA-001 using prior-art account summary tests.
## Review Plan
Review behavior.
## Rollback Plan
Remove registration.
## Risk Register
Mutation risk.
## Observability and Evidence
Record validation command output and blocked gates.
## Visual References / Diagrams
Not needed: one implementation unit.
## Accessibility and Operator Ergonomics
Maintain readable status text.
## Open Questions
None.
## Final Decision
Ready for he-work.
"""


class GeneratedArtifactShapeTests(unittest.TestCase):
    def test_spec_accepts_extensive_user_story_shape(self) -> None:
        self.assertEqual(MODULE.validate_spec(VALID_SPEC), [])

    def test_spec_rejects_too_few_requested_user_stories(self) -> None:
        invalid = VALID_SPEC.replace(
            "2. As an overdraft-risk customer, I want early warning context, so that I can avoid fees.\n"
            "3. As a support operator, I want insight state to be explainable, so that I can answer customer questions.\n",
            "",
        )

        self.assertIn(
            "User Stories section must include at least three stories when requested",
            MODULE.validate_spec(invalid),
        )

    def test_plan_validation_gates_require_observable_proof_language(self) -> None:
        """
        Verify that plan validation requires Validation Gates to reference observable behavior, source IDs, or explicit proof.
        
        Asserts that replacing an observable-proof requirement with a generic "run the unit test." causes validate_plan to return an error containing "Validation Gates must tie testing decisions to observable behavior, source IDs, or proof".
        """
        invalid = VALID_PLAN.replace(
            "Required: observable behavior proof for SA-001 using prior-art account summary tests.",
            "Required: run the unit test.",
        )

        self.assertIn(
            "Validation Gates must tie testing decisions to observable behavior, source IDs, or proof",
            MODULE.validate_plan(invalid),
        )

    def test_spec_rejects_missing_scope_authority(self) -> None:
        invalid = VALID_SPEC.replace("downscope_authority: not_applicable\n", "")

        self.assertIn(
            "Authority and Scope Boundary missing required field: downscope_authority",
            MODULE.validate_spec(invalid),
        )

    def test_plan_rejects_missing_testing_lens(self) -> None:
        invalid = VALID_PLAN.replace(
            "testing_lens: observable behavior proof for SA-001 using prior-art account summary tests plus negative mutation check.\n",
            "",
        )

        self.assertIn(
            "Coding and Testing Lenses missing required field: testing_lens",
            MODULE.validate_plan(invalid),
        )


if __name__ == "__main__":
    unittest.main()
