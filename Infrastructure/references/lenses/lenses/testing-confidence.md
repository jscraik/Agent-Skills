---
id: lens.testing-confidence
title: Testing Confidence
type: expert_lens
version: 1.0.0
status: stable
triggers:
  keywords:
    - test
    - tests
    - validation
    - regression
    - confidence
    - CI
    - eval
  task_intents:
    - validation_review
    - refactor_plan
    - skill_authoring
    - sdk_contract_review
  file_signals:
    - tests/
    - test/
    - pytest.ini
    - vitest.config.ts
    - .github/workflows/
strengths:
  - regression_proof
  - fixture_design
  - behavior_coverage
  - validation_mapping
avoid_when:
  - task_intent: pure_visual_polish
pairs_well_with:
  - lens.operator-evidence
  - lens.progressive-disclosure
output_categories:
  - missing_regression_guard
  - weak_assertion
  - unproven_behavior_path
  - brittle_fixture
priority: 85
---

# Testing Confidence

## Review Questions

1. Does the test prove behavior that matters to a user, agent, or operator?
2. Is the assertion strong enough to fail for the regression we care about?
3. Are edge cases, negative cases, and blocked paths represented where risk warrants them?
4. Is the validation command the repo's canonical command rather than an ad hoc proxy?
5. Does the test avoid depending on incidental formatting or implementation details?

## Failure Modes

- A test checks wording but not the contract.
- A validator can pass while silently skipping the changed surface.
- The proof path exercises a helper but not the public command or workflow.
- A fixture is so idealized that it misses the real failure mode.
- CI, local tests, and runtime evidence are treated as the same truth lane.

## Recommended Moves

- Add one focused regression test before widening coverage.
- Assert full pass/fail status for happy paths, not only absence of one warning.
- Include changed-files or public-command coverage when routing logic changes.
- Report exact commands and outcomes separately from release readiness.
