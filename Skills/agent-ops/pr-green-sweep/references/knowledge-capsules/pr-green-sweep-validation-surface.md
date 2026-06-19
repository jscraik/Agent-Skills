# Validation Surface

Match each changed surface to its owning verifier before claiming readiness or staging generated outputs.

Pack id: pack.pr-green-sweep
Facet id: validation_surface
Runtime dependency: none; this slice is generated from a KnowledgeOS pack export.
Lifecycle status: reviewed

## Claim Cards

### claim.pr-green-sweep.validation-surface-matches-change: Validation Surface Matches Change

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference, local_repo_or_corpus_reference

A PR sweep should validate each fix with the smallest verifier that owns the changed surface.

Interpretation notes:
- Generated manifests and reference docs should not be validated as source code by default.

### claim.harness.smallest-proof-surface: Select The Smallest Proof Surface

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_repo_or_corpus_reference

Gate selection should use the smallest proof surface that keeps the current slice correct, validated, traceable, maintainable, and safe to continue or close.

Interpretation notes:
- This claim prevents both under-validation and governance sprawl.

### claim.harness.strict-runtime-boundaries: Specs And Plans Need Runtime Boundaries

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_repo_or_corpus_reference

Route-driving specs and plans need explicit source of truth, resumption key, execution boundary, proof boundary, mutation boundary, freshness requirement, and human acceptance boundary.

Interpretation notes:
- This claim supports implementation-readiness gates.

### claim.harness.feedback-becomes-guardrails: Repeated Feedback Should Become Guardrails

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

Repeated agent review feedback should be encoded into durable guardrails rather than handled as one-off correction.

Interpretation notes:
- This supports assets about learned fixes and validation-first closeout.

### claim.harness.review-needs-proof: Agent Work Needs Review Evidence

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

Agent-produced work should be accepted through review evidence, not through invisible trust in the trajectory.

Interpretation notes:
- This anchors readiness and evidence-boundary assets.

### claim.harness.agent-observability: Agents Need Inspectable Observability

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

Harnesses should expose logs, metrics, traces, dashboards, and runtime state in forms agents can inspect directly.

Interpretation notes:
- This claim adds runtime inspection as part of evidence, not only command validation.

### claim.harness.on-policy-guardrails: Guardrails Should Be Native To Agent Work

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

Productive harness guardrails should live in the native media agents already use, such as code, docs, tests, lints, scripts, review comments, and CI.

Interpretation notes:
- Authority controls still need external boundaries for permissions, identity, secrets, and governance.

### claim.harness.full-job-verified-result: The Full Job Ends In A Verified Result

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_repo_or_corpus_reference

A useful agent should drive the change to a verified result, not stop after editing files.

Interpretation notes:
- This strengthens the Ryan-derived proof lane by making behavioral verification part of the job boundary.

### claim.harness.product-facing-proof: Product Work Needs Product-Facing Proof

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_repo_or_corpus_reference

Product and UI changes need proof from the product path, not only static checks.

Interpretation notes:
- Product-facing proof may be a browser smoke, API call, screenshot, log, artifact, or other user-path evidence.

### claim.harness.agent-legible-failures: Failures Should Be Agent-Legible

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_repo_or_corpus_reference

Failing commands should tell agents the command, location, exit code, focused output, and likely remediation path.

Interpretation notes:
- This turns validation failure output into part of the harness, not just a terminal event.

## Heuristics

### heuristic.pr-green-sweep.select-validation-surface: Select Validation Surface

- Type: heuristic
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_source_reference, local_repo_or_corpus_reference
- Derived from claims: claim.pr-green-sweep.validation-surface-matches-change, claim.harness.smallest-proof-surface

Choose the verifier owned by the changed surface before running gates or claiming readiness.

Use when:
- A PR mixes source code, skill packages, reference docs, generated manifests, CI config, or validation outputs.
- A failing check could be caused by the wrong validator rather than the patch.

Avoid when:
- The repo has a single documented wrapper that explicitly owns all touched paths.

### heuristic.harness.require-proof-boundary: Require A Proof Boundary

- Type: heuristic
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_repo_or_corpus_reference
- Derived from claims: claim.harness.strict-runtime-boundaries

Before a spec or plan drives work, require it to name what evidence can prove completion and what sources are not proof.

Use when:
- A plan is about to route to implementation, closure, tracker updates, or long-running work.
- The source of truth includes chat summaries, session evidence, or stale artifacts.

Avoid when:
- The task is a tiny low-risk fix with direct user authority and obvious validation.
- The artifact is explicitly research-only.

## Checklists

### checklist.harness.closeout-evidence: Closeout Evidence Checklist

- Type: checklist
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.harness.feedback-becomes-guardrails, claim.harness.review-needs-proof, claim.harness.agent-observability, claim.harness.on-policy-guardrails

- [ ] State the exact command or artifact checked.
- [ ] Mark each result as pass, fail, or blocked.
- [ ] Separate local validation from CI, review, tracker, and merge readiness.
- [ ] Record blocker class and nearest fallback when the exact proof path cannot run.
- [ ] Convert repeated feedback into a durable follow-up surface or record the skip reason.
- [ ] Include runtime evidence from logs, traces, metrics, dashboards, or smoke artifacts when behavior is the claim.
- [ ] Prefer repo-native guardrails before adding external workflow scaffolding.

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

### eval.pr-green-sweep.wrong-validator-for-reference-doc: Wrong Validator For Reference Doc

- Type: eval-scenario
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_source_reference, local_repo_or_corpus_reference
- Derived from claims: claim.pr-green-sweep.validation-surface-matches-change

Knowledge claim: Validation must match the changed surface in PR closeout work.
Behavior under test: Path-aware validation selection before gates.
Failure mode: A generic validator is used for reference docs, generated manifests, and validation output.
Expected agent move: Choose skill audit for skill packages, link or markdown checks for references, generator checks for manifests, CI config validation for CI, and repo tests for source code.
Skill lift target: Validation decisions are reported before gate execution.
Proof route: references/evals.yaml
Fixture path: references/evals/eval.pr-green-sweep.wrong-validator-for-reference-doc.md
Promotion status: candidate
Capsule refs: pr-green-sweep
Weak eval flags: none

Given: A PR touches a skill entrypoint, a standalone reference document, a generated manifest, CI config, and validation output.
Should: The agent maps each path to the owning validation surface and keeps generated or validation-only outputs out of the source fix unless the repo contract owns them.
Expected failure: The agent runs a generic test or skill audit over all paths and stages generated evidence blindly.
Reproduce with: references/evals/eval.pr-green-sweep.wrong-validator-for-reference-doc.md
