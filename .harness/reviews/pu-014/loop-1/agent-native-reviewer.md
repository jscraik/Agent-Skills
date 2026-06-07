# Agent-Native Architecture Review

## Summary
The PU-014 spec and trace plan are broadly aligned on a read-only SDK review route that reuses existing lens selection, emits a schema-backed receipt, and updates status/artifact truth. The plan is strongest on non-mutation and advisory positioning, but it still leaves a few agent-operability gaps in handoff determinism, error-path coverage, and discoverability commitment.

## Findings

1. **P1 - Acceptance coverage is incomplete for handoff determinism** -- The spec requires both stable `selected_lenses` and stable `next_commands`, plus status evidence that the route is implemented and non-mutating, but the trace plan only traces stable lens ids and omits explicit coverage for `next_commands` and the status-field assertions. Evidence: [spec lines 152-161](/private/tmp/agent-skills-skills-sdk-pu-014-lens-routed-review/.harness/specs/2026-06-07-skills-sdk-pu-014-lens-routed-review-spec.md#L152-L161), [trace plan lines 31-38](/private/tmp/agent-skills-skills-sdk-pu-014-lens-routed-review/.harness/plan/2026-06-07-skills-sdk-pu-014-lens-routed-review-trace-plan.md#L31-L38), [trace plan lines 77-82](/private/tmp/agent-skills-skills-sdk-pu-014-lens-routed-review/.harness/plan/2026-06-07-skills-sdk-pu-014-lens-routed-review-trace-plan.md#L77-L82). Why it matters: an agent could get a stable lens list but a drifting or unverified handoff route, which weakens repeatability and review usability. Fix: add an explicit test row and validation assertion for `next_commands` stability across identical inputs, and make the status check assert `review_plan`, `feature_executed=true`, and `mutation_performed=false`.

2. **P1 - Catalog-validation failure is required by spec but not traced** -- The spec says the command must error when the lens catalog fails validation, but the implementation tasks and test list do not include a dedicated catalog-failure path. Evidence: [spec lines 92-100](/private/tmp/agent-skills-skills-sdk-pu-014-lens-routed-review/.harness/specs/2026-06-07-skills-sdk-pu-014-lens-routed-review-spec.md#L92-L100), [trace plan lines 42-63](/private/tmp/agent-skills-skills-sdk-pu-014-lens-routed-review/.harness/plan/2026-06-07-skills-sdk-pu-014-lens-routed-review-trace-plan.md#L42-L63), [trace plan lines 77-82](/private/tmp/agent-skills-skills-sdk-pu-014-lens-routed-review/.harness/plan/2026-06-07-skills-sdk-pu-014-lens-routed-review-trace-plan.md#L77-L82). Why it matters: this is one of the explicit refusal cases in the public contract, so missing trace coverage makes it easier to ship a route that fails open or reports a malformed receipt when the lens catalog is invalid. Fix: add a negative test that forces catalog validation failure and asserts a robot error envelope with no receipt write.

3. **P2 - Discoverability is left conditional instead of committed** -- The trace plan only says to add `review` to `VALID_ACTIONS["sdk"]` and examples "if command metadata expects every public action listed," which leaves route discoverability unresolved as an implementation choice rather than a guaranteed outcome. Evidence: [trace plan lines 51-55](/private/tmp/agent-skills-skills-sdk-pu-014-lens-routed-review/.harness/plan/2026-06-07-skills-sdk-pu-014-lens-routed-review-trace-plan.md#L51-L55), [trace plan lines 64-66](/private/tmp/agent-skills-skills-sdk-pu-014-lens-routed-review/.harness/plan/2026-06-07-skills-sdk-pu-014-lens-routed-review-trace-plan.md#L64-L66). Why it matters: the route may exist but still be hard for agents or maintainers to find, which undermines the operator-handoff goal of this slice. Fix: make the help/registry update unconditional for the public route, and add a validation check that the new `sdk review plan` action is surfaced in the robot discoverability path.

## What's Working Well
- The plan correctly keeps the route read-only by default and explicitly separates receipt writing from normal execution.
- The spec and trace plan both preserve reuse of the existing lens-selection primitive instead of duplicating scoring.
- The trace plan already treats status truth and the pipeline artifact as separate surfaces, which is the right shape for avoiding drift.

## Accountability Receipt
- status: complete
- artifact_paths:
  - /private/tmp/agent-skills-skills-sdk-pu-014-lens-routed-review/.harness/reviews/pu-014/loop-1/agent-native-reviewer.md
  - /private/tmp/agent-skills-skills-sdk-pu-014-lens-routed-review/artifacts/agent-runs/agent-native-reviewer-2026-06-07-pu-014-loop-1/manifest.json
- findings:
- P1: handoff determinism trace is incomplete
- P1: catalog-validation failure path is not traced
- P2: discoverability is conditional instead of committed
- failures_or_blockers: none
- improvement_opportunities:
- add explicit next_commands stability coverage
- add a catalog-validation negative test
- make command discoverability updates unconditional
- strengths:
- non-mutating default is explicit
- review route reuses existing lens selection
- status/artifact truth are planned separately
- validation_evidence:
- read spec and trace plan on disk with line-numbered inspection
- confirmed the relevant memory note about this repo's review-chain expectations
- next_action:
- implement the traced validation gaps before coding the route
- manifest_path: /private/tmp/agent-skills-skills-sdk-pu-014-lens-routed-review/artifacts/agent-runs/agent-native-reviewer-2026-06-07-pu-014-loop-1/manifest.json

WROTE: /private/tmp/agent-skills-skills-sdk-pu-014-lens-routed-review/.harness/reviews/pu-014/loop-1/agent-native-reviewer.md
