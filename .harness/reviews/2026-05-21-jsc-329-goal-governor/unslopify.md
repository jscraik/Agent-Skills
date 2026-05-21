# Unslopify Review: JSC-329 Goal Governor Review Mode

## Findings

### Medium: Regression Test Was Too Coupled To Prose

Evidence:
- `Skills/agent-ops/goal-governor/tests/test_check_goal_board.py:22`

The first version of the review-mode regression test could pass or fail based on incidental wording in `SKILL.md`. That made the guard brittle: harmless phrasing edits could fail the test, while contradictory YAML structure could still keep the right keywords and pass.

Disposition: fixed. The test now parses `contract.yaml` and `evals.yaml`, verifies the execution override route, asserts the review-mode output fields and forbidden actions structurally, and keeps only a small set of sentinel checks against the human-facing skill instructions.

## Residual Risk

The broader Goal Governor instructions still contain some duplicated normative language across checklist and response sections. That is pre-existing documentation shape debt and is intentionally deferred because this slice is limited to the prompt-review/not-start-yet safety guard.

WROTE: .harness/reviews/2026-05-21-jsc-329-goal-governor/unslopify.md
