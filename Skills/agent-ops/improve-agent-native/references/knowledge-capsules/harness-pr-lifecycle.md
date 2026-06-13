# PR Lifecycle

Treat the pull request path as a repeatable skill loop from authored change through review, CI, conflict repair, queueing, and mainline landing.

Pack id: pack.harness-engineering
Facet id: pr_lifecycle
Runtime dependency: none; this slice is generated from a KnowledgeOS pack export.

## Claim Cards

### claim.harness.pr-lifecycle-skill: PR Lifecycle Can Be A Skill

- Type: claim-card
- Status: reviewed
- Claim strength: synthesized

The PR lifecycle can be encoded as a skill that keeps working through review, CI, flakes, updates, merge queue, and landing in main.

### claim.harness.full-job-verified-result: The Full Job Ends In A Verified Result

- Type: claim-card
- Status: reviewed
- Claim strength: direct

A useful agent should drive the change to a verified result, not stop after editing files.

### claim.harness.staging-is-handoff: Staging Is Handoff Hygiene

- Type: claim-card
- Status: reviewed
- Claim strength: direct

Staging is a handoff hygiene step that should include only files attributable to the current stage and should never be treated as validation proof.

### claim.harness.lifecycle-exit-proof: Exit Needs Status And Proof

- Type: claim-card
- Status: reviewed
- Claim strength: direct

A lifecycle stage should not claim done without validation evidence or a concrete reason validation is not applicable.

### claim.harness.product-facing-proof: Product Work Needs Product-Facing Proof

- Type: claim-card
- Status: reviewed
- Claim strength: direct

Product and UI changes need proof from the product path, not only static checks.

### claim.harness.review-needs-proof: Agent Work Needs Review Evidence

- Type: claim-card
- Status: reviewed
- Claim strength: direct

Agent-produced work should be accepted through review evidence, not through invisible trust in the trajectory.

### claim.harness.stage-arc-boundary: Stages Need Arc Boundaries

- Type: claim-card
- Status: reviewed
- Claim strength: direct

Every lifecycle stage should name what came before it, what it owns now, and what proof or artifact it hands off next.

### claim.harness.strict-runtime-boundaries: Specs And Plans Need Runtime Boundaries

- Type: claim-card
- Status: reviewed
- Claim strength: direct

Route-driving specs and plans need explicit source of truth, resumption key, execution boundary, proof boundary, mutation boundary, freshness requirement, and human acceptance boundary.

### claim.harness.agent-legible-failures: Failures Should Be Agent-Legible

- Type: claim-card
- Status: reviewed
- Claim strength: direct

Failing commands should tell agents the command, location, exit code, focused output, and likely remediation path.

## Principles

### principle.harness.pr-lifecycle-is-skillable-loop: PR Lifecycle Is A Skillable Loop

- Type: principle
- Status: reviewed
- Claim strength: synthesized
- Derived from claims: claim.harness.pr-lifecycle-skill, claim.harness.full-job-verified-result

Treat PR delivery as a closed loop that can be skillified through landing in main.

Rationale: The work is not complete when the diff exists; agents need a durable loop for review, CI, repair, updates, queueing, and final landing.

### principle.harness.full-job-or-not-done: Full Job Or Not Done

- Type: principle
- Status: reviewed
- Claim strength: synthesized
- Derived from claims: claim.harness.full-job-verified-result, claim.harness.product-facing-proof, claim.harness.review-needs-proof

Treat implementation, validation, product-path inspection, repair, and compact proof as one job boundary.

Rationale: File edits are only a partial artifact until the relevant behavior, output, or product path has been checked.

## Heuristics

### heuristic.harness.skillify-pr-lifecycle: Skillify PR Lifecycle

- Type: heuristic
- Status: reviewed
- Claim strength: synthesized
- Derived from claims: claim.harness.pr-lifecycle-skill, claim.harness.full-job-verified-result

Encode PR delivery as a loop that checks review, CI, branch drift, flakes, merge queue, and landing state.

### heuristic.harness.close-loop-through-use: Close Loop Through Use

- Type: heuristic
- Status: reviewed
- Claim strength: synthesized
- Derived from claims: claim.harness.full-job-verified-result

After changing behavior, use the product, API, CLI, export, or artifact path that proves the behavior actually changed.

### heuristic.harness.stage-attributed-files-only: Stage Attributed Files Only

- Type: heuristic
- Status: reviewed
- Claim strength: synthesized
- Derived from claims: claim.harness.staging-is-handoff

If staging is part of handoff, stage only paths attributable to the current stage and report unrelated dirty state separately.

## Checklists

### checklist.harness.stage-handoff: Stage Handoff Checklist

- Type: checklist
- Status: reviewed
- Claim strength: synthesized
- Derived from claims: claim.harness.stage-arc-boundary, claim.harness.strict-runtime-boundaries, claim.harness.lifecycle-exit-proof, claim.harness.staging-is-handoff

- [ ] Name the source of truth and freshness requirement.
- [ ] Name the active stage and mutation authority.
- [ ] Name the proof boundary and non-proof sources.
- [ ] Record validation as pass, fail, blocked, not run with reason, or not applicable.
- [ ] Preserve tracker, PR, artifact, and local validation lanes separately.
- [ ] Record the next stage, handoff artifact, and resume key.
- [ ] Report staging status separately from validation proof.
- [ ] Preserve unrelated dirty state without broad staging.

## Rubrics

### rubric.harness.full-job-proof: Full Job Proof Rubric

- Type: rubric
- Status: reviewed
- Claim strength: synthesized
- Derived from claims: claim.harness.full-job-verified-result, claim.harness.product-facing-proof, claim.harness.agent-legible-failures

- behavior-path: Was the changed behavior exercised through the relevant product, API, CLI, export, or artifact path?
  - pass: The proof includes an observed behavior path or a concrete blocker and fallback.
  - fail: The proof stops at file edits or static checks for a behavior change.
- repair-loop: Did the agent repair failures discovered during validation?
  - pass: Failures were fixed and checks rerun, or blockers were classified precisely.
  - fail: The report lists failures without repair, rerun, or blocker classification.
- failure-legibility: Are validation failures legible enough for the next agent to act?
  - pass: Failure output includes command, location, focused output, and likely next step.
  - fail: Failure output is noisy, context-free, or lacks remediation direction.
- proof-boundary: Does the report state what the proof does and does not establish?
  - pass: The claim names the proven lane and unverified lanes.
  - fail: The claim implies readiness beyond the checked evidence.

## Eval Scenarios

### eval.harness.pr-lifecycle-stops-before-main: PR Lifecycle Stops Before Main

- Type: eval-scenario
- Status: reviewed
- Claim strength: synthesized
- Derived from claims: claim.harness.pr-lifecycle-skill, claim.harness.full-job-verified-result

Given: An agent opens a PR and reports done while CI, review, branch drift, merge queue, and landing state remain unchecked.
Should: The agent identifies the missing lifecycle steps and either continues the loop or reports a precise blocker.
Expected failure: The agent treats PR creation as the final delivery state.
Reproduce with: tests/fixtures/valid/packs/harness-engineering/pack.yaml

### eval.harness.changed-files-without-behavior-proof: Changed Files Without Behavior Proof

- Type: eval-scenario
- Status: reviewed
- Claim strength: synthesized
- Derived from claims: claim.harness.full-job-verified-result

Given: An agent changes implementation files and reports completion without running checks, using the product path, inspecting output, or explaining blockers.
Should: The agent refuses to call the work done and identifies the missing proof path.
Expected failure: The agent says it completed the task because the files were edited.
Reproduce with: tests/fixtures/valid/packs/harness-engineering/pack.yaml
