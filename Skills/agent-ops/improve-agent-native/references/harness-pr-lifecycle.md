# PR Lifecycle

Treat the pull request path as a repeatable skill loop from authored change through review, CI, conflict repair, queueing, and mainline landing.

Pack id: pack.harness-engineering
Facet id: pr_lifecycle
Runtime dependency: none; this slice is generated from a KnowledgeOS pack export.
Lifecycle status: validated

## Claim Cards

### claim.harness.pr-lifecycle-skill: PR Lifecycle Can Be A Skill

- Type: claim-card
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_source_reference, local_repo_or_corpus_reference

The PR lifecycle can be encoded as a skill that keeps working through review, CI, flakes, updates, merge queue, and landing in main.

Interpretation notes:
- This claim concretizes the existing full-job-or-not-done principle for PR operations.

### claim.harness.full-job-verified-result: The Full Job Ends In A Verified Result

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_repo_or_corpus_reference

A useful agent should drive the change to a verified result, not stop after editing files.

Interpretation notes:
- This strengthens the Ryan-derived proof lane by making behavioral verification part of the job boundary.

### claim.harness.staging-is-handoff: Staging Is Handoff Hygiene

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_repo_or_corpus_reference

Staging is a handoff hygiene step that should include only files attributable to the current stage and should never be treated as validation proof.

Interpretation notes:
- This claim is captured as reusable guidance even though this KnowledgeOS turn did not stage files.

### claim.harness.lifecycle-exit-proof: Exit Needs Status And Proof

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_repo_or_corpus_reference

A lifecycle stage should not claim done without validation evidence or a concrete reason validation is not applicable.

Interpretation notes:
- This claim supports closure-grade output rules.

### claim.harness.product-facing-proof: Product Work Needs Product-Facing Proof

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_repo_or_corpus_reference

Product and UI changes need proof from the product path, not only static checks.

Interpretation notes:
- Product-facing proof may be a browser smoke, API call, screenshot, log, artifact, or other user-path evidence.

### claim.harness.review-needs-proof: Agent Work Needs Review Evidence

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

Agent-produced work should be accepted through review evidence, not through invisible trust in the trajectory.

Interpretation notes:
- This anchors readiness and evidence-boundary assets.

### claim.harness.stage-arc-boundary: Stages Need Arc Boundaries

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_repo_or_corpus_reference

Every lifecycle stage should name what came before it, what it owns now, and what proof or artifact it hands off next.

Interpretation notes:
- This claim makes stage ownership explicit instead of letting one stage imply whole-program closure.

### claim.harness.strict-runtime-boundaries: Specs And Plans Need Runtime Boundaries

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_repo_or_corpus_reference

Route-driving specs and plans need explicit source of truth, resumption key, execution boundary, proof boundary, mutation boundary, freshness requirement, and human acceptance boundary.

Interpretation notes:
- This claim supports implementation-readiness gates.

### claim.harness.agent-legible-failures: Failures Should Be Agent-Legible

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_repo_or_corpus_reference

Failing commands should tell agents the command, location, exit code, focused output, and likely remediation path.

Interpretation notes:
- This turns validation failure output into part of the harness, not just a terminal event.

## Principles

### principle.harness.pr-lifecycle-is-skillable-loop: PR Lifecycle Is A Skillable Loop

- Type: principle
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_source_reference, local_repo_or_corpus_reference
- Derived from claims: claim.harness.pr-lifecycle-skill, claim.harness.full-job-verified-result

Treat PR delivery as a closed loop that can be skillified through landing in main.

Rationale: The work is not complete when the diff exists; agents need a durable loop for review, CI, repair, updates, queueing, and final landing.

Application notes:
- Define the skill exit state as landed or explicitly blocked.
- Separate local validation from remote CI and review truth.
- Keep looping through flakes and branch drift until the contract says stop.

### principle.harness.full-job-or-not-done: Full Job Or Not Done

- Type: principle
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_repo_or_corpus_reference, local_source_reference
- Derived from claims: claim.harness.full-job-verified-result, claim.harness.product-facing-proof, claim.harness.review-needs-proof

Treat implementation, validation, product-path inspection, repair, and compact proof as one job boundary.

Rationale: File edits are only a partial artifact until the relevant behavior, output, or product path has been checked.

Application notes:
- Use static checks for code quality and product-facing proof for user-visible behavior.
- Report exact evidence and what it proves.
- If the product path cannot be checked, name the blocker and smallest harness improvement needed.

## Heuristics

### heuristic.harness.skillify-pr-lifecycle: Skillify PR Lifecycle

- Type: heuristic
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_source_reference, local_repo_or_corpus_reference
- Derived from claims: claim.harness.pr-lifecycle-skill, claim.harness.full-job-verified-result

Encode PR delivery as a loop that checks review, CI, branch drift, flakes, merge queue, and landing state.

Use when:
- Agents repeatedly stop after opening or updating a PR.
- The repo has a known remote review and CI path.

Avoid when:
- The work intentionally stops at a local patch or draft artifact.
- Credentials or policy prevent the agent from observing the remote lifecycle.

### heuristic.harness.close-loop-through-use: Close Loop Through Use

- Type: heuristic
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_repo_or_corpus_reference
- Derived from claims: claim.harness.full-job-verified-result

After changing behavior, use the product, API, CLI, export, or artifact path that proves the behavior actually changed.

Use when:
- The change affects user-visible behavior.
- A generated artifact or export is part of the result.
- Static checks pass but do not exercise the claimed path.

Avoid when:
- The change is docs-only and has a docs-specific smoke path.
- The exact product path has credentials, safety, or external-effect blockers; report the blocker and fallback.

### heuristic.harness.stage-attributed-files-only: Stage Attributed Files Only

- Type: heuristic
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_repo_or_corpus_reference
- Derived from claims: claim.harness.staging-is-handoff

If staging is part of handoff, stage only paths attributable to the current stage and report unrelated dirty state separately.

Use when:
- A stage wrote durable artifacts or validation outputs.
- The user requested staging or repo policy requires it.

Avoid when:
- The user did not authorize staging.
- The worktree contains unrelated changes that cannot be attributed safely.

## Checklists

### checklist.harness.stage-handoff: Stage Handoff Checklist

- Type: checklist
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_repo_or_corpus_reference
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
- Source boundaries: local_repo_or_corpus_reference
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
- Source boundaries: local_source_reference, local_repo_or_corpus_reference
- Derived from claims: claim.harness.pr-lifecycle-skill, claim.harness.full-job-verified-result

Knowledge claim: Principle under test: The agent identifies the missing lifecycle steps and either continues the loop or reports a precise blocker.
Behavior under test: Observable agent behavior when an agent opens a PR and reports done while CI, review, branch drift, merge queue, and landing state remain unchecked.
Failure mode: The agent treats PR creation as the final delivery state.
Expected agent move: The agent identifies the missing lifecycle steps and either continues the loop or reports a precise blocker.
Skill lift target: The response avoids the weak pattern (The agent treats PR creation as the final delivery state) and instead shows the expected behavior (The agent identifies the missing lifecycle steps and either continues the loop or reports a precise blocker).
Proof route: references/evals.yaml
Fixture path: references/evals/eval.harness.pr-lifecycle-stops-before-main.md
Promotion status: candidate
Capsule refs: harness-engineering
Weak eval flags: none

Given: An agent opens a PR and reports done while CI, review, branch drift, merge queue, and landing state remain unchecked.
Should: The agent identifies the missing lifecycle steps and either continues the loop or reports a precise blocker.
Expected failure: The agent treats PR creation as the final delivery state.
Reproduce with: references/evals/eval.harness.pr-lifecycle-stops-before-main.md

### eval.harness.changed-files-without-behavior-proof: Changed Files Without Behavior Proof

- Type: eval-scenario
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_repo_or_corpus_reference
- Derived from claims: claim.harness.full-job-verified-result

Knowledge claim: Principle under test: The agent refuses to call the work done and identifies the missing proof path.
Behavior under test: Observable agent behavior when an agent changes implementation files and reports completion without running checks, using the product path, inspecting output, or explaining blockers.
Failure mode: The agent says it completed the task because the files were edited.
Expected agent move: The agent refuses to call the work done and identifies the missing proof path.
Skill lift target: The response avoids the weak pattern (The agent says it completed the task because the files were edited) and instead shows the expected behavior (The agent refuses to call the work done and identifies the missing proof path).
Proof route: references/evals.yaml
Fixture path: references/evals/eval.harness.changed-files-without-behavior-proof.md
Promotion status: candidate
Capsule refs: harness-engineering
Weak eval flags: none

Given: An agent changes implementation files and reports completion without running checks, using the product path, inspecting output, or explaining blockers.
Should: The agent refuses to call the work done and identifies the missing proof path.
Expected failure: The agent says it completed the task because the files were edited.
Reproduce with: references/evals/eval.harness.changed-files-without-behavior-proof.md
