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
## Security, Privacy, and Safety
No secrets.
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
## Current State / Evidence
Spec exists.
## Implementation Strategy
Use existing account summary surface.
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
## Visual References / Diagrams
Not needed: one implementation unit.
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
        invalid = VALID_PLAN.replace(
            "Required: observable behavior proof for SA-001 using prior-art account summary tests.",
            "Required: run the unit test.",
        )

        self.assertIn(
            "Validation Gates must tie testing decisions to observable behavior, source IDs, or proof",
            MODULE.validate_plan(invalid),
        )


if __name__ == "__main__":
    unittest.main()
