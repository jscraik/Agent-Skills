# Harness Review Feedback

Convert review pressure and repeated feedback into bounded reviewer-author protocols, guardrails, and next-run artifacts.

Pack id: pack.harness-engineering
Facet id: review_feedback
Runtime dependency: none; this slice is generated from a KnowledgeOS pack export.
Lifecycle status: validated

## Claim Cards

### claim.harness.feedback-becomes-guardrails: Repeated Feedback Should Become Guardrails

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

Repeated agent review feedback should be encoded into durable guardrails rather than handled as one-off correction.

Interpretation notes:
- This supports assets about learned fixes and validation-first closeout.

### claim.harness.review-loop-needs-protocol: Review Agent Loops Need Protocol

- Type: claim-card
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_source_reference

Reviewer-agent and authoring-agent loops need explicit priority, deferral, backlog, and pushback semantics to avoid thrashing.

Interpretation notes:
- This uses a condensed secondary transcript, so the asset is marked synthesized rather than direct.

### claim.harness.feedback-distills-next-run: Feedback Distills Into Next Run Context

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

Agent loops can ingest human review feedback and prior session logs, identify missed priorities or misaligned code, and save markdown context for the next run.

Interpretation notes:
- This is a concrete operational pattern for durable feedback capture.

### claim.harness.human-review-moves-upstream: Human Review Moves Upstream

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

In high-trust agent workflows, human review shifts upstream to plans, milestones, specifications, and prompts rather than disappearing.

Interpretation notes:
- This clarifies that implementation-level review can be delegated only when upstream intent is crisp and mechanisms check execution.

### claim.harness.review-needs-proof: Agent Work Needs Review Evidence

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

Agent-produced work should be accepted through review evidence, not through invisible trust in the trajectory.

Interpretation notes:
- This anchors readiness and evidence-boundary assets.

### claim.harness.human-authority-boundaries: High-Impact Boundaries Need Human Authority

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

Agent autonomy still requires human or governance authority at high-impact boundaries such as release, security policy, identity, authorization, revocation, secrets, and compliance.

Interpretation notes:
- This claim prevents overgeneralizing post-merge review and zero-human-code patterns.

### claim.harness.on-policy-guardrails: Guardrails Should Be Native To Agent Work

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

Productive harness guardrails should live in the native media agents already use, such as code, docs, tests, lints, scripts, review comments, and CI.

Interpretation notes:
- Authority controls still need external boundaries for permissions, identity, secrets, and governance.

### claim.harness.little-decisions-surfaced: Little Decisions Must Be Surfaced

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

Harness engineering must surface the small decisions and nonfunctional requirements that make agent-produced code acceptable.

Interpretation notes:
- This strengthens earlier quality-criteria claims with a narrower focus on decision timing and nonfunctional requirements.

### claim.harness.slop-garbage-collection: Slop Needs Garbage Collection

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

High-throughput agent teams need recurring garbage-collection loops that remove slop and systematically prevent it from recurring.

Interpretation notes:
- This turns quality cleanup into a recurring harness loop rather than occasional refactoring.

## Principles

### principle.harness.feedback-is-system-input: Feedback Is System Input

- Type: principle
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.harness.feedback-becomes-guardrails, claim.harness.on-policy-guardrails

Treat repeated human or reviewer feedback as evidence that the harness is missing a durable mechanism.

Rationale: Agent teams improve when recurring corrections become validators, tests, guardrails, routing instructions, or security review mechanisms in the same work surface agents already use.

Application notes:
- Classify repeated feedback by failure class before choosing the durable surface.
- Prefer narrow mechanisms that prevent recurrence without adding broad context load.

### principle.harness.agent-review-needs-negotiation-protocol: Agent Review Needs Negotiation Protocol

- Type: principle
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.harness.review-loop-needs-protocol, claim.harness.review-needs-proof

Agent review loops need explicit semantics for must-fix, defer, backlog, and pushback.

Rationale: Without priority and deferral rules, authoring agents can treat every review comment as immediate scope and reviewer agents can create non-converging loops.

Application notes:
- Require severity and evidence for blocking comments.
- Give authoring agents permission to defer or challenge non-blocking requests.
- Preserve backlog suggestions without letting them double the current task.

### principle.harness.review-the-prompt-boundary: Review The Prompt Boundary

- Type: principle
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.harness.little-decisions-surfaced, claim.harness.human-review-moves-upstream

Put human review where it most changes the agent trajectory: plans, specs, milestones, prompt-like execution documents, and nonfunctional requirements.

Rationale: Implementation review can be delegated only when the upstream intent boundary is crisp enough for agents and checks to execute.

Application notes:
- Review week-scale or high-complexity execution plans before they become agent prompts.
- Treat underspecified plans as likely generators of low-quality implementation.
- Keep tests and reviewer agents responsible for implementation-level proof.

## Heuristics

### heuristic.harness.encode-repeat-feedback: Encode Repeat Feedback

- Type: heuristic
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.harness.feedback-becomes-guardrails

If the same correction appears twice, look for a validator, fixture, test, review lens, or instruction route that can catch it next time.

Use when:
- Review comments repeat across agent tasks.
- Failed commands reveal missing remediation guidance.

Avoid when:
- The correction depends on private judgment that cannot yet be made deterministic.
- Encoding the rule would block valid work more often than it catches failures.

### heuristic.harness.bound-review-comments: Bound Review Comments

- Type: heuristic
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.harness.review-loop-needs-protocol

Require review agents to classify comments as blocking, deferrable, backlog, or FYI before an authoring agent acts.

Use when:
- Review feedback could expand the task beyond its original scope.
- Multiple agents are iterating on the same change.

Avoid when:
- The comment identifies a clear correctness or security defect.
- A human has explicitly asked to broaden the scope.

### heuristic.harness.distill-feedback-into-artifact: Distill Feedback Into Artifact

- Type: heuristic
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.harness.feedback-distills-next-run

After an agent loop receives human feedback, compare it with the prior session record and write a durable next-run artifact.

Use when:
- Human thumbs-up/down or review comments reveal missed priorities.
- An automated loop will run again.
- The agent can identify why its previous output was misaligned.

Avoid when:
- The feedback is private and cannot be safely persisted.
- The loop is one-off and no future run will consume the artifact.

## Anti-Patterns

### anti-pattern.harness.review-agent-bullying-loop: Review Agent Bullying Loop

- Type: anti-pattern
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.harness.review-loop-needs-protocol

Problem: A reviewer agent emits unbounded suggestions while the authoring agent treats every comment as mandatory immediate scope.

Failure mode: The loop fails to converge, doubles the task, and burns time on non-blocking feedback.

Avoidance: Encode review priority, blocking criteria, deferral rights, backlog semantics, and author pushback rules.

## Eval Scenarios

### eval.harness.feedback-recurs-without-guardrail: Repeated Feedback Needs Durable Capture

- Type: eval-scenario
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.harness.feedback-becomes-guardrails

Knowledge claim: Principle under test: The agent classifies the repeated failure and proposes a durable guardrail, test, fixture, instruction route, or skip reason.
Behavior under test: Observable agent behavior when an reviewer repeats the same correction that appeared in an earlier agent task.
Failure mode: The agent applies another one-off fix without addressing recurrence.
Expected agent move: The agent classifies the repeated failure and proposes a durable guardrail, test, fixture, instruction route, or skip reason.
Skill lift target: The response avoids the weak pattern (The agent applies another one-off fix without addressing recurrence) and instead shows the expected behavior (The agent classifies the repeated failure and proposes a durable guardrail, test, fixture, instruction route, or skip reason).
Proof route: references/evals.yaml
Fixture path: references/evals/eval.harness.feedback-recurs-without-guardrail.md
Promotion status: candidate
Capsule refs: harness-engineering
Weak eval flags: none

Given: A reviewer repeats the same correction that appeared in an earlier agent task.
Should: The agent classifies the repeated failure and proposes a durable guardrail, test, fixture, instruction route, or skip reason.
Expected failure: The agent applies another one-off fix without addressing recurrence.
Reproduce with: references/evals/eval.harness.feedback-recurs-without-guardrail.md

### eval.harness.review-agent-doubles-scope: Review Agent Doubles Scope

- Type: eval-scenario
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.harness.review-loop-needs-protocol

Knowledge claim: Principle under test: The agent separates blocking defects from deferrable or backlog comments and preserves the original scope.
Behavior under test: Observable agent behavior when an reviewer agent provides broad improvement suggestions and the authoring agent starts implementing all of them before landing the original fix.
Failure mode: The agent assumes every review comment is mandatory and turns review into an unbounded rewrite.
Expected agent move: The agent separates blocking defects from deferrable or backlog comments and preserves the original scope.
Skill lift target: The response avoids the weak pattern (The agent assumes every review comment is mandatory and turns review into an unbounded rewrite) and instead shows the expected behavior (The agent separates blocking defects from deferrable or backlog comments and preserves the original scope).
Proof route: references/evals.yaml
Fixture path: references/evals/eval.harness.review-agent-doubles-scope.md
Promotion status: candidate
Capsule refs: harness-engineering
Weak eval flags: none

Given: A reviewer agent provides broad improvement suggestions and the authoring agent starts implementing all of them before landing the original fix.
Should: The agent separates blocking defects from deferrable or backlog comments and preserves the original scope.
Expected failure: The agent assumes every review comment is mandatory and turns review into an unbounded rewrite.
Reproduce with: references/evals/eval.harness.review-agent-doubles-scope.md

### eval.harness.slop-feedback-not-systematized: Slop Feedback Not Systematized

- Type: eval-scenario
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.harness.slop-garbage-collection, claim.harness.feedback-distills-next-run

Knowledge claim: Principle under test: The agent identifies the missing systematization step and records a durable guardrail, artifact, or follow-up.
Behavior under test: Observable agent behavior when reviewers collect recurring slop patterns for a week, but the cleanup loop fixes only the current code and saves no next-run artifact.
Failure mode: The agent treats cleanup as complete because the visible slop was removed once.
Expected agent move: The agent identifies the missing systematization step and records a durable guardrail, artifact, or follow-up.
Skill lift target: The response avoids the weak pattern (The agent treats cleanup as complete because the visible slop was removed once) and instead shows the expected behavior (The agent identifies the missing systematization step and records a durable guardrail, artifact, or follow-up).
Proof route: references/evals.yaml
Fixture path: references/evals/eval.harness.slop-feedback-not-systematized.md
Promotion status: candidate
Capsule refs: harness-engineering
Weak eval flags: none

Given: Reviewers collect recurring slop patterns for a week, but the cleanup loop fixes only the current code and saves no next-run artifact.
Should: The agent identifies the missing systematization step and records a durable guardrail, artifact, or follow-up.
Expected failure: The agent treats cleanup as complete because the visible slop was removed once.
Reproduce with: references/evals/eval.harness.slop-feedback-not-systematized.md
