# Continuous Cleanup

Convert recurring feedback, drift, and cleanup pressure into small durable mechanisms that compound over repeated agent runs.

Pack id: pack.ryan-lopopolo-principal-engineering
Facet id: continuous_cleanup
Runtime dependency: none; this slice is generated from a KnowledgeOS pack export.
Lifecycle status: reviewed

## Claim Cards

### claim.ryan.continuous-garbage-collection: Agent Codebases Need Continuous Garbage Collection

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: article_source_note_paraphrase

Agent-generated systems accumulate drift unless human taste and recurring cleanup are encoded into continuous repository mechanisms.

Interpretation notes:
- This makes refactoring and cleanup a standing operating loop, not an occasional rescue project.

### claim.harness.feedback-becomes-guardrails: Repeated Feedback Should Become Guardrails

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

Repeated agent review feedback should be encoded into durable guardrails rather than handled as one-off correction.

Interpretation notes:
- This supports assets about learned fixes and validation-first closeout.

### claim.ryan.environment-design: Principal Engineering Moves To Environment Design

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: article_source_note_paraphrase

In agent-first delivery, senior engineering leverage shifts toward designing the environment, intent, tools, abstractions, guardrails, and feedback loops that let agents do reliable work.

Interpretation notes:
- This is the core bridge from harness engineering to a principal engineer skill.

### claim.ryan.agent-legibility: Agent Legibility Is An Engineering Goal

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: article_source_note_paraphrase

Software systems should expose code, docs, schemas, plans, diagnostics, runtime state, and validation evidence in forms agents can inspect and act on.

Interpretation notes:
- This expands principal engineering review beyond static code quality into operational inspectability.

### claim.ryan.enforce-boundaries: Enforce Boundaries And Allow Local Freedom

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: article_source_note_paraphrase

Agent-scale systems should enforce architectural invariants mechanically while leaving agents freedom inside those boundaries.

Interpretation notes:
- This should become a review rule for architecture, platform, and agent workflow changes.

### claim.ryan.repeated-steering-environment-failure: Repeated Steering Signals Environment Failure

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: user_provided_excerpt_not_independently_verified

Repeated human steering should be treated as high-signal evidence that the agent environment needs refinement.

Interpretation notes:
- This reinforces feedback-to-guardrails as an agent operating contract.

### claim.ryan.long-term-coherence-agent-artifacts: Agent Artifacts Need Long-Term Coherence

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: user_provided_excerpt_not_independently_verified

Agent-produced artifacts should be designed for long-term coherence across thousands of future changes.

Interpretation notes:
- This is an architectural quality bar for agent-generated repos.

## Heuristics

### heuristic.ryan.promote-repeat-feedback-to-mechanism: Promote Repeat Feedback To Mechanism

- Type: heuristic
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: article_source_note_paraphrase, local_source_reference
- Derived from claims: claim.ryan.continuous-garbage-collection, claim.harness.feedback-becomes-guardrails

When feedback recurs, encode the smallest recurring mechanism that prevents or detects the issue next time.

Use when:
- A review note has appeared more than once.
- Cleanup work is becoming a standing tax.
- An agent keeps copying a weak local pattern.

Avoid when:
- The feedback is a one-off product preference.
- The mechanism would be broader than the observed failure class.

## Checklists

### checklist.ryan.principal-engineer-harness-review: Principal Engineer Harness Review

- Type: checklist
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: article_source_note_paraphrase
- Derived from claims: claim.ryan.environment-design, claim.ryan.agent-legibility, claim.ryan.enforce-boundaries, claim.ryan.continuous-garbage-collection

- [ ] Name the human steering decision and the agent execution boundary.
- [ ] Check whether the needed source of truth is repository-local, versioned, and discoverable.
- [ ] Identify which boundary should be enforced mechanically.
- [ ] Verify that diagnostics tell the next agent how to recover.
- [ ] Separate local validation, CI, review, tracker, and merge-readiness proof.
- [ ] Convert recurring review feedback or cleanup into a durable repo mechanism.

## Eval Scenarios

### eval.ryan.repeated-steering-to-durable-mechanism: Repeated Steering Becomes A Durable Mechanism

- Type: eval-scenario
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: user_provided_excerpt_not_independently_verified
- Derived from claims: claim.ryan.repeated-steering-environment-failure, claim.ryan.long-term-coherence-agent-artifacts

Given: A user repeats the same correction across two agent tasks in a repository.
Should: The agent identifies the recurrence, names the failure class, proposes the smallest durable repo mechanism, and records either the patch or a bounded skip reason.
Expected failure: The agent applies another one-off fix and treats the repeated feedback as ordinary task steering.
Reproduce with: references/evals/eval.ryan.repeated-steering-to-durable-mechanism.md
