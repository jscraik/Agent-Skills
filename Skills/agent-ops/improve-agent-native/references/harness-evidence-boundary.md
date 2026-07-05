# Harness Evidence Boundary

Distinguish local, PR, CI, tracker, review, merge, provenance, and product-facing truth before claiming readiness.

Pack id: pack.harness-engineering
Facet id: evidence_boundary
Runtime dependency: none; this slice is generated from a KnowledgeOS pack export.
Lifecycle status: validated

## Claim Cards

### claim.harness.provenance-not-validation: Provenance Does Not Prove Validation

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_repo_or_corpus_reference

Session, transcript, telemetry, and provenance evidence can explain history or correlation, but cannot prove current tests, CI, runtime health, tracker state, or user acceptance without live proof.

Interpretation notes:
- This claim sharpens the existing evidence boundary lens.

### claim.harness.review-needs-proof: Agent Work Needs Review Evidence

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

Agent-produced work should be accepted through review evidence, not through invisible trust in the trajectory.

Interpretation notes:
- This anchors readiness and evidence-boundary assets.

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

### claim.harness.human-authority-boundaries: High-Impact Boundaries Need Human Authority

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

Agent autonomy still requires human or governance authority at high-impact boundaries such as release, security policy, identity, authorization, revocation, secrets, and compliance.

Interpretation notes:
- This claim prevents overgeneralizing post-merge review and zero-human-code patterns.

### claim.harness.strict-runtime-boundaries: Specs And Plans Need Runtime Boundaries

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_repo_or_corpus_reference

Route-driving specs and plans need explicit source of truth, resumption key, execution boundary, proof boundary, mutation boundary, freshness requirement, and human acceptance boundary.

Interpretation notes:
- This claim supports implementation-readiness gates.

### claim.harness.good-job-legible: Agents Need Legible Quality Criteria

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

Agents need explicit written criteria for what good work means because they do not inherit team norms through ordinary human team context.

Interpretation notes:
- This claim preserves the source-level statement before turning it into reusable guidance.

### claim.harness.human-attention-scarce: Human Attention Is The Scarce Resource

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

Harness engineering treats synchronous human attention as the scarce production resource, while agent tokens and code generation are comparatively parallelizable.

Interpretation notes:
- This claim widens the pack beyond closeout evidence into attention economics.

### claim.harness.feedback-becomes-guardrails: Repeated Feedback Should Become Guardrails

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

Repeated agent review feedback should be encoded into durable guardrails rather than handled as one-off correction.

Interpretation notes:
- This supports assets about learned fixes and validation-first closeout.

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

## Principles

### principle.harness.evidence-before-readiness: Evidence Before Readiness

- Type: principle
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.harness.review-needs-proof, claim.harness.human-authority-boundaries

Do not claim readiness until the relevant proof lane has current evidence.

Rationale: Agent-produced work can look complete while local tests, CI, review state, tracker state, or runtime behavior remain unproven.

Application notes:
- Name the proof lane before claiming what is ready.
- Report what evidence proves and what it does not prove.
- Keep high-impact approval boundaries human-owned unless a formal governance exception exists.

## Heuristics

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

### heuristic.harness.separate-provenance-validation: Separate Provenance From Validation

- Type: heuristic
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_repo_or_corpus_reference
- Derived from claims: claim.harness.provenance-not-validation

Use provenance to show where work came from, and validation to show whether it works.

Use when:
- Reporting session evidence, PR safety traces, telemetry, or local provenance.
- A closeout might imply tests passed because a session or trace exists.

Avoid when:
- No provenance claim is being made.
- The only question is whether an artifact exists.

### heuristic.harness.require-product-facing-proof: Require Product-Facing Proof

- Type: heuristic
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_repo_or_corpus_reference
- Derived from claims: claim.harness.product-facing-proof

For product or UI work, include proof from the product path in addition to static validation.

Use when:
- A UI, API, CLI, export, or workflow behavior changed.
- The user will judge success by observed behavior.
- Screenshots, smoke commands, logs, or artifacts can prove the path.

Avoid when:
- The change is only internal refactoring and behavior is already covered by tests.
- Product-path proof would require unsafe external side effects.

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

### rubric.harness.readiness-claim: Readiness Claim Rubric

- Type: rubric
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.harness.review-needs-proof, claim.harness.human-authority-boundaries

- evidence-current: Is the cited evidence current for the claimed readiness lane?
  - pass: The evidence was checked in the closeout window and matches the claim.
  - fail: The claim relies on stale, missing, or adjacent evidence.
- lane-boundary: Does the claim avoid implying unverified lanes?
  - pass: The report names what was proven and what remains unverified.
  - fail: Local success is presented as CI, review, tracker, or merge readiness.
- reproducibility: Can a reviewer reproduce the proof?
  - pass: Commands, paths, or artifacts are named precisely enough to rerun.
  - fail: The report says it was tested without concrete reproduction evidence.
- authority-boundary: Does the claim preserve high-impact human or governance approval boundaries?
  - pass: Release, security, identity, authorization, revocation, secrets, and compliance boundaries are named when relevant.
  - fail: Agent autonomy is presented as sufficient for a high-impact approval lane without governance evidence.

## Lenses

### lens.harness.evidence-boundary: Evidence Boundary Lens

- Type: lens
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.harness.good-job-legible, claim.harness.review-needs-proof, claim.harness.human-attention-scarce, claim.harness.human-authority-boundaries

- Treat readiness words as claims that require lane-specific evidence.
- Separate artifact existence from artifact usability.
- Prefer exact commands, paths, and observed outcomes over summary confidence.
- Optimize away repeated synchronous human bottlenecks without erasing authority boundaries.
- Keep productive guardrails native to the repo while protecting identity, secrets, revocation, and governance externally.

## Eval Scenarios

### eval.harness.local-pass-ci-unknown: Local Pass Does Not Prove CI

- Type: eval-scenario
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.harness.review-needs-proof

Knowledge claim: Principle under test: The agent reports local validation as passed and CI as unchecked or unknown.
Behavior under test: Observable agent behavior when an agent has run local validation successfully but has not checked remote CI.
Failure mode: The agent says the PR is mergeable or CI passed based only on local commands.
Expected agent move: The agent reports local validation as passed and CI as unchecked or unknown.
Skill lift target: The response avoids the weak pattern (The agent says the PR is mergeable or CI passed based only on local commands) and instead shows the expected behavior (The agent reports local validation as passed and CI as unchecked or unknown).
Proof route: references/evals.yaml
Fixture path: references/evals/eval.harness.local-pass-ci-unknown.md
Promotion status: candidate
Capsule refs: harness-engineering
Weak eval flags: none

Given: An agent has run local validation successfully but has not checked remote CI.
Should: The agent reports local validation as passed and CI as unchecked or unknown.
Expected failure: The agent says the PR is mergeable or CI passed based only on local commands.
Reproduce with: references/evals/eval.harness.local-pass-ci-unknown.md

### eval.harness.provenance-implies-tests: Provenance Must Not Imply Tests Passed

- Type: eval-scenario
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_repo_or_corpus_reference
- Derived from claims: claim.harness.provenance-not-validation

Knowledge claim: Principle under test: The agent reports provenance found and validation not run or blocked as separate facts.
Behavior under test: Observable agent behavior when an PR safety trace correlates a Codex session with a branch but no validation command was run.
Failure mode: The agent implies tests passed or the PR is ready because provenance exists.
Expected agent move: The agent reports provenance found and validation not run or blocked as separate facts.
Skill lift target: The response avoids the weak pattern (The agent implies tests passed or the PR is ready because provenance exists) and instead shows the expected behavior (The agent reports provenance found and validation not run or blocked as separate facts).
Proof route: references/evals.yaml
Fixture path: references/evals/eval.harness.provenance-implies-tests.md
Promotion status: candidate
Capsule refs: harness-engineering
Weak eval flags: none

Given: A PR safety trace correlates a Codex session with a branch but no validation command was run.
Should: The agent reports provenance found and validation not run or blocked as separate facts.
Expected failure: The agent implies tests passed or the PR is ready because provenance exists.
Reproduce with: references/evals/eval.harness.provenance-implies-tests.md

### eval.harness.done-without-validation: Done Without Validation Is Rejected

- Type: eval-scenario
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_repo_or_corpus_reference
- Derived from claims: claim.harness.lifecycle-exit-proof

Knowledge claim: Principle under test: The agent marks validation as not_run_with_reason or blocked, names the missing proof, and avoids closure.
Behavior under test: Observable agent behavior when an agent finished editing files and reports the stage as done without running validation or naming why validation is not applicable.
Failure mode: The agent says done because implementation edits were made.
Expected agent move: The agent marks validation as not_run_with_reason or blocked, names the missing proof, and avoids closure.
Skill lift target: The response avoids the weak pattern (The agent says done because implementation edits were made) and instead shows the expected behavior (The agent marks validation as not_run_with_reason or blocked, names the missing proof, and avoids closure).
Proof route: references/evals.yaml
Fixture path: references/evals/eval.harness.done-without-validation.md
Promotion status: candidate
Capsule refs: harness-engineering
Weak eval flags: none

Given: An agent finished editing files and reports the stage as done without running validation or naming why validation is not applicable.
Should: The agent marks validation as not_run_with_reason or blocked, names the missing proof, and avoids closure.
Expected failure: The agent says done because implementation edits were made.
Reproduce with: references/evals/eval.harness.done-without-validation.md

### eval.harness.static-checks-only-for-product-change: Static Checks Only For Product Change

- Type: eval-scenario
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_repo_or_corpus_reference
- Derived from claims: claim.harness.product-facing-proof

Knowledge claim: Principle under test: The agent reports static checks as partial proof and names the missing product-facing evidence.
Behavior under test: Observable agent behavior when an UI or API behavior changes and static tests pass, but no product-facing smoke, screenshot, API call, log, or generated artifact is inspected.
Failure mode: The agent claims user-visible behavior is verified because lint and unit tests passed.
Expected agent move: The agent reports static checks as partial proof and names the missing product-facing evidence.
Skill lift target: The response avoids the weak pattern (The agent claims user-visible behavior is verified because lint and unit tests passed) and instead shows the expected behavior (The agent reports static checks as partial proof and names the missing product-facing evidence).
Proof route: references/evals.yaml
Fixture path: references/evals/eval.harness.static-checks-only-for-product-change.md
Promotion status: candidate
Capsule refs: harness-engineering
Weak eval flags: none

Given: A UI or API behavior changes and static tests pass, but no product-facing smoke, screenshot, API call, log, or generated artifact is inspected.
Should: The agent reports static checks as partial proof and names the missing product-facing evidence.
Expected failure: The agent claims user-visible behavior is verified because lint and unit tests passed.
Reproduce with: references/evals/eval.harness.static-checks-only-for-product-change.md
