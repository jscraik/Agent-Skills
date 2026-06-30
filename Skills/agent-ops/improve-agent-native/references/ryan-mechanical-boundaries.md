# Mechanical Boundaries

Encode architecture and workflow invariants into enforceable repo mechanisms while leaving local implementation freedom.

Pack id: pack.ryan-lopopolo-principal-engineering
Facet id: mechanical_boundaries
Runtime dependency: none; this slice is generated from a KnowledgeOS pack export.
Lifecycle status: reviewed

## Claim Cards

### claim.ryan.enforce-boundaries: Enforce Boundaries And Allow Local Freedom

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: article_source_note_paraphrase

Agent-scale systems should enforce architectural invariants mechanically while leaving agents freedom inside those boundaries.

Interpretation notes:
- This should become a review rule for architecture, platform, and agent workflow changes.

### claim.ryan.executable-conventions: Conventions Should Become Executable

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: article_source_note_paraphrase

Principal-engineering conventions should be encoded into executable repo tooling rather than left as tribal memory.

Interpretation notes:
- This extends the harness pack from agent legibility into everyday principal engineering mechanics.

### claim.harness.feedback-becomes-guardrails: Repeated Feedback Should Become Guardrails

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

Repeated agent review feedback should be encoded into durable guardrails rather than handled as one-off correction.

Interpretation notes:
- This supports assets about learned fixes and validation-first closeout.

### claim.harness.strict-runtime-boundaries: Specs And Plans Need Runtime Boundaries

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_repo_or_corpus_reference

Route-driving specs and plans need explicit source of truth, resumption key, execution boundary, proof boundary, mutation boundary, freshness requirement, and human acceptance boundary.

Interpretation notes:
- This claim supports implementation-readiness gates.

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

### claim.ryan.continuous-garbage-collection: Agent Codebases Need Continuous Garbage Collection

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: article_source_note_paraphrase

Agent-generated systems accumulate drift unless human taste and recurring cleanup are encoded into continuous repository mechanisms.

Interpretation notes:
- This makes refactoring and cleanup a standing operating loop, not an occasional rescue project.

### claim.harness.agent-legible-failures: Failures Should Be Agent-Legible

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_repo_or_corpus_reference

Failing commands should tell agents the command, location, exit code, focused output, and likely remediation path.

Interpretation notes:
- This turns validation failure output into part of the harness, not just a terminal event.

## Principles

### principle.ryan.repo-contracts-are-executable: Repo Contracts Are Executable

- Type: principle
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: article_source_note_paraphrase, local_source_reference
- Derived from claims: claim.ryan.executable-conventions, claim.ryan.enforce-boundaries, claim.harness.feedback-becomes-guardrails

Important repository conventions should exist as runnable contracts, not merely prose expectations.

Rationale: Agents and teams can repeatedly satisfy conventions when checks, errors, package boundaries, and validation commands encode the rule.

Application notes:
- Promote recurring style, architecture, or content feedback into lints, schemas, tests, or scripts.
- Write diagnostics as instructions for the next repair attempt.
- Keep prose docs aligned to executable checks instead of relying on docs alone.

## Heuristics

### heuristic.ryan.enforce-boundaries-not-implementations: Enforce Boundaries Not Implementations

- Type: heuristic
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: article_source_note_paraphrase, local_repo_or_corpus_reference
- Derived from claims: claim.ryan.enforce-boundaries, claim.harness.strict-runtime-boundaries

Encode architectural and operational boundaries mechanically, then allow agents freedom in how they satisfy those boundaries.

Use when:
- A team wants agent throughput without architectural drift.
- Review comments repeatedly ask for the same structural constraint.
- A rule can be expressed as a lint, schema, test, script, or diagnostic.

Avoid when:
- The decision depends on product judgment that has not been made explicit.
- The rule would freeze an implementation detail instead of protecting a boundary.

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

## Rubrics

### rubric.ryan.principal-engineer-agent-readiness: Principal Engineer Agent Readiness

- Type: rubric
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: article_source_note_paraphrase, local_repo_or_corpus_reference
- Derived from claims: claim.ryan.agent-legibility, claim.ryan.enforce-boundaries, claim.harness.agent-legible-failures

- local-context: Can a cold agent find the relevant source of truth without hidden human context?
  - pass: Entry points route to current repo-local docs, schemas, plans, and validation commands.
  - fail: The work depends on chat history, external docs, tacit memory, or one giant instruction blob.
- enforceable-boundaries: Are the important architectural and workflow boundaries mechanically enforced?
  - pass: Linters, schemas, tests, scripts, or diagnostics encode the boundary and recovery path.
  - fail: The boundary exists only as advice, preference, or review folklore.
- recovery-loop: Can the agent observe failure and recover through owned tools?
  - pass: Logs, metrics, traces, screenshots, tests, or command diagnostics expose the failure and next action.
  - fail: Failure requires a human to inspect inaccessible runtime state or infer missing context.
