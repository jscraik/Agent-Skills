# Ryan Environment Design

Review agent work by improving the tools, context, feedback loops, and authority boundaries that let agents execute reliably.

Pack id: pack.ryan-lopopolo-principal-engineering
Facet id: environment_design
Runtime dependency: none; this slice is generated from a KnowledgeOS pack export.
Lifecycle status: reviewed

## Claim Cards

### claim.ryan.environment-design: Principal Engineering Moves To Environment Design

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: article_source_note_paraphrase

In agent-first delivery, senior engineering leverage shifts toward designing the environment, intent, tools, abstractions, guardrails, and feedback loops that let agents do reliable work.

Interpretation notes:
- This is the core bridge from harness engineering to a principal engineer skill.

### claim.ryan.humans-steer-agents-execute: Humans Steer And Agents Execute

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: article_source_note_paraphrase

Human engineers remain responsible for steering, prioritizing, acceptance criteria, outcome validation, and system improvement while agents execute the implementation loop.

Interpretation notes:
- The skill should preserve human authority boundaries instead of simulating autonomous judgment over high-impact decisions.

### claim.ryan.merge-gates-depend-on-recovery-loops: Merge Gates Depend On Recovery Loops

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: article_source_note_paraphrase

Agent throughput changes merge-gate tradeoffs; short-lived pull requests, cheap follow-up correction, and minimal blocking gates can be reasonable only when validation and remediation systems are strong enough.

Interpretation notes:
- The claim is conditional; it does not justify loosening gates without strong recovery loops.

### claim.ryan.autonomy-threshold-tooling: Autonomy Rises With Encoded Development Loops

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: article_source_note_paraphrase

Agent autonomy should increase as the development loop is encoded into tools, including state validation, bug reproduction, evidence capture, fixes, validation, PR creation, feedback handling, build remediation, escalation, and merge.

Interpretation notes:
- This turns autonomy into an evidence-backed tooling threshold rather than a model-confidence claim.

### claim.harness.codebase-new-starter: Treat Each Agent Run Like A New Starter

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_repo_or_corpus_reference

Codebases should be designed as if every agent run starts without durable tacit memory of the project.

Interpretation notes:
- This does not require more documentation everywhere; it requires visible structure where tacit knowledge would otherwise be necessary.

### claim.harness.deep-modules-control: Deep Modules Bound Agent Work

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_repo_or_corpus_reference

Deep modules with simple public interfaces and substantial internal behavior create safer boundaries for delegated agent work.

Interpretation notes:
- Boundary tests and clear interfaces matter more than directory neatness alone.

### claim.ryan.context-and-validation-loop: AI Pairing Needs Context And Validation

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: article_source_note_paraphrase

Agent pairing improves when the agent receives relevant code or bug context and is steered through local validation feedback.

Interpretation notes:
- This supports a skill behavior of asking for or discovering the smallest relevant context slice before changing code.

### claim.ryan.agent-legibility: Agent Legibility Is An Engineering Goal

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: article_source_note_paraphrase

Software systems should expose code, docs, schemas, plans, diagnostics, runtime state, and validation evidence in forms agents can inspect and act on.

Interpretation notes:
- This expands principal engineering review beyond static code quality into operational inspectability.

### claim.harness.human-authority-boundaries: High-Impact Boundaries Need Human Authority

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

Agent autonomy still requires human or governance authority at high-impact boundaries such as release, security policy, identity, authorization, revocation, secrets, and compliance.

Interpretation notes:
- This claim prevents overgeneralizing post-merge review and zero-human-code patterns.

### claim.ryan.enforce-boundaries: Enforce Boundaries And Allow Local Freedom

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: article_source_note_paraphrase

Agent-scale systems should enforce architectural invariants mechanically while leaving agents freedom inside those boundaries.

Interpretation notes:
- This should become a review rule for architecture, platform, and agent workflow changes.

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

### principle.ryan.principal-engineer-designs-agent-environment: Principal Engineer Designs The Agent Environment

- Type: principle
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: article_source_note_paraphrase, local_repo_or_corpus_reference
- Derived from claims: claim.ryan.environment-design, claim.harness.codebase-new-starter, claim.harness.deep-modules-control

A principal engineer in an agent-first codebase improves the environment agents operate inside before asking for more effort from the agent.

Rationale: Agent failures often reveal missing scaffolding, unclear contracts, weak diagnostics, slow validation, inaccessible runtime state, or unenforced boundaries.

Application notes:
- Treat repeated agent failure as a harness-design signal.
- Prefer durable repo mechanisms over larger prompts.
- Review tools, docs, tests, scripts, and diagnostics as part of the architecture.

## Heuristics

### heuristic.ryan.pair-with-agents-through-context-and-tests: Pair With Agents Through Context And Tests

- Type: heuristic
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: article_source_note_paraphrase
- Derived from claims: claim.ryan.context-and-validation-loop

Give the agent the smallest relevant context slice, ask for review or implementation, and feed local validation results back into the loop.

Use when:
- The task involves code repair, test expansion, or refactoring.
- A bug report, failing test, or adjacent implementation can anchor the work.
- The agent can run or inspect validation locally.

Avoid when:
- The task requires hidden context the agent cannot inspect.
- Validation is unavailable and the risk of hallucinated behavior is high.

### heuristic.ryan.scale-autonomy-through-recovery-loops: Scale Autonomy Through Recovery Loops

- Type: heuristic
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: article_source_note_paraphrase
- Derived from claims: claim.ryan.merge-gates-depend-on-recovery-loops, claim.ryan.autonomy-threshold-tooling

Loosen merge gates or increase agent autonomy only to the level that validation, remediation, feedback handling, escalation, and rollback loops can reliably absorb.

Use when:
- A team wants higher agent throughput without turning every PR into synchronous human review.
- Validation and recovery loops are observable enough to catch and repair mistakes quickly.
- Gate ceremony is slowing safe, short-lived changes more than it is reducing risk.

Avoid when:
- The system cannot reproduce failures, capture evidence, remediate builds, or escalate ambiguous risk.
- Human authority boundaries for release, security, compliance, identity, or irreversible decisions are unclear.
- The argument for autonomy is based on model capability rather than encoded tooling and recovery evidence.

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

## Lenses

### lens.ryan.harness-minded-principal-engineer: Harness-Minded Principal Engineer

- Type: lens
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: article_source_note_paraphrase, local_source_reference
- Derived from claims: claim.ryan.humans-steer-agents-execute, claim.ryan.agent-legibility, claim.harness.human-authority-boundaries

- Look for the environment change that would make the agent more reliable next time.
- Preserve human authority at product, security, release, and irreversible judgment boundaries.
- Prefer repo-local maps, validators, diagnostics, and small durable mechanisms over more prompt text.
- Treat agent legibility as an architectural quality, not a documentation nicety.

## Eval Scenarios

### eval.ryan.autonomy-gate-threshold: Autonomy Follows Recovery Evidence

- Type: eval-scenario
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: article_source_note_paraphrase
- Derived from claims: claim.ryan.merge-gates-depend-on-recovery-loops, claim.ryan.autonomy-threshold-tooling

Knowledge claim: Principle under test: The agent evaluates current validation, remediation, feedback handling, escalation, rollback, and human-authority boundaries before recommending a gate posture.
Behavior under test: Observable agent behavior when an team asks whether to let agents merge low-risk pull requests with fewer blocking human gates.
Failure mode: The agent recommends either more ceremony or more autonomy based only on model capability, team preference, or generic throughput goals.
Expected agent move: The agent evaluates current validation, remediation, feedback handling, escalation, rollback, and human-authority boundaries before recommending a gate posture.
Skill lift target: The response avoids the weak pattern (The agent recommends either more ceremony or more autonomy based only on model capability, team preference, or generic throughput goals) and instead shows the expected behavior (The agent evaluates current validation, remediation, feedback handling, escalation, rollback, and human-authority boundaries before recommending a gate posture).
Proof route: references/evals.yaml
Fixture path: references/evals/eval.ryan.autonomy-gate-threshold.md
Promotion status: candidate
Capsule refs: principal-engineering
Weak eval flags: none

Given: A team asks whether to let agents merge low-risk pull requests with fewer blocking human gates.
Should: The agent evaluates current validation, remediation, feedback handling, escalation, rollback, and human-authority boundaries before recommending a gate posture.
Expected failure: The agent recommends either more ceremony or more autonomy based only on model capability, team preference, or generic throughput goals.
Reproduce with: references/evals/eval.ryan.autonomy-gate-threshold.md
