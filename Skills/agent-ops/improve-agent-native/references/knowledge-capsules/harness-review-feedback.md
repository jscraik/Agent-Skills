# Review Feedback

Convert review pressure and repeated feedback into bounded reviewer-author protocols, guardrails, and next-run artifacts.

Pack id: pack.harness-engineering
Facet id: review_feedback
Runtime dependency: none; this slice is generated from a KnowledgeOS pack export.

## Claim Cards

### claim.harness.feedback-becomes-guardrails: Repeated Feedback Should Become Guardrails

- Type: claim-card
- Status: reviewed
- Claim strength: direct

Repeated agent review feedback should be encoded into durable guardrails rather than handled as one-off correction.

### claim.harness.review-loop-needs-protocol: Review Agent Loops Need Protocol

- Type: claim-card
- Status: reviewed
- Claim strength: synthesized

Reviewer-agent and authoring-agent loops need explicit priority, deferral, backlog, and pushback semantics to avoid thrashing.

### claim.harness.feedback-distills-next-run: Feedback Distills Into Next Run Context

- Type: claim-card
- Status: reviewed
- Claim strength: direct

Agent loops can ingest human review feedback and prior session logs, identify missed priorities or misaligned code, and save markdown context for the next run.

### claim.harness.human-review-moves-upstream: Human Review Moves Upstream

- Type: claim-card
- Status: reviewed
- Claim strength: direct

In high-trust agent workflows, human review shifts upstream to plans, milestones, specifications, and prompts rather than disappearing.

### claim.harness.review-needs-proof: Agent Work Needs Review Evidence

- Type: claim-card
- Status: reviewed
- Claim strength: direct

Agent-produced work should be accepted through review evidence, not through invisible trust in the trajectory.

### claim.harness.human-authority-boundaries: High-Impact Boundaries Need Human Authority

- Type: claim-card
- Status: reviewed
- Claim strength: direct

Agent autonomy still requires human or governance authority at high-impact boundaries such as release, security policy, identity, authorization, revocation, secrets, and compliance.

### claim.harness.on-policy-guardrails: Guardrails Should Be Native To Agent Work

- Type: claim-card
- Status: reviewed
- Claim strength: direct

Productive harness guardrails should live in the native media agents already use, such as code, docs, tests, lints, scripts, review comments, and CI.

### claim.harness.little-decisions-surfaced: Little Decisions Must Be Surfaced

- Type: claim-card
- Status: reviewed
- Claim strength: direct

Harness engineering must surface the small decisions and nonfunctional requirements that make agent-produced code acceptable.

### claim.harness.slop-garbage-collection: Slop Needs Garbage Collection

- Type: claim-card
- Status: reviewed
- Claim strength: direct

High-throughput agent teams need recurring garbage-collection loops that remove slop and systematically prevent it from recurring.

## Principles

### principle.harness.feedback-is-system-input: Feedback Is System Input

- Type: principle
- Status: reviewed
- Claim strength: synthesized
- Derived from claims: claim.harness.feedback-becomes-guardrails, claim.harness.on-policy-guardrails

Treat repeated human or reviewer feedback as evidence that the harness is missing a durable mechanism.

Rationale: Agent teams improve when recurring corrections become validators, tests, guardrails, routing instructions, or security review mechanisms in the same work surface agents already use.

### principle.harness.agent-review-needs-negotiation-protocol: Agent Review Needs Negotiation Protocol

- Type: principle
- Status: reviewed
- Claim strength: synthesized
- Derived from claims: claim.harness.review-loop-needs-protocol, claim.harness.review-needs-proof

Agent review loops need explicit semantics for must-fix, defer, backlog, and pushback.

Rationale: Without priority and deferral rules, authoring agents can treat every review comment as immediate scope and reviewer agents can create non-converging loops.

### principle.harness.review-the-prompt-boundary: Review The Prompt Boundary

- Type: principle
- Status: reviewed
- Claim strength: synthesized
- Derived from claims: claim.harness.little-decisions-surfaced, claim.harness.human-review-moves-upstream

Put human review where it most changes the agent trajectory: plans, specs, milestones, prompt-like execution documents, and nonfunctional requirements.

Rationale: Implementation review can be delegated only when the upstream intent boundary is crisp enough for agents and checks to execute.

## Heuristics

### heuristic.harness.encode-repeat-feedback: Encode Repeat Feedback

- Type: heuristic
- Status: reviewed
- Claim strength: synthesized
- Derived from claims: claim.harness.feedback-becomes-guardrails

If the same correction appears twice, look for a validator, fixture, test, review lens, or instruction route that can catch it next time.

### heuristic.harness.bound-review-comments: Bound Review Comments

- Type: heuristic
- Status: reviewed
- Claim strength: synthesized
- Derived from claims: claim.harness.review-loop-needs-protocol

Require review agents to classify comments as blocking, deferrable, backlog, or FYI before an authoring agent acts.

### heuristic.harness.distill-feedback-into-artifact: Distill Feedback Into Artifact

- Type: heuristic
- Status: reviewed
- Claim strength: synthesized
- Derived from claims: claim.harness.feedback-distills-next-run

After an agent loop receives human feedback, compare it with the prior session record and write a durable next-run artifact.

## Anti-Patterns

### anti-pattern.harness.review-agent-bullying-loop: Review Agent Bullying Loop

- Type: anti-pattern
- Status: reviewed
- Claim strength: synthesized
- Derived from claims: claim.harness.review-loop-needs-protocol

Problem: A reviewer agent emits unbounded suggestions while the authoring agent treats every comment as mandatory immediate scope.

Failure mode: The loop fails to converge, doubles the task, and burns time on non-blocking feedback.

Avoidance: Encode review priority, blocking criteria, deferral rights, backlog semantics, and author pushback rules.

## Eval Scenarios

### eval.harness.feedback-recurs-without-guardrail: Repeated Feedback Needs Durable Capture

- Type: eval-scenario
- Status: reviewed
- Claim strength: synthesized
- Derived from claims: claim.harness.feedback-becomes-guardrails

Given: A reviewer repeats the same correction that appeared in an earlier agent task.
Should: The agent classifies the repeated failure and proposes a durable guardrail, test, fixture, instruction route, or skip reason.
Expected failure: The agent applies another one-off fix without addressing recurrence.
Reproduce with: tests/fixtures/invalid/synthesized-without-lineage/assets/principles/principle.fixture.no-lineage.yaml

### eval.harness.review-agent-doubles-scope: Review Agent Doubles Scope

- Type: eval-scenario
- Status: reviewed
- Claim strength: synthesized
- Derived from claims: claim.harness.review-loop-needs-protocol

Given: A reviewer agent provides broad improvement suggestions and the authoring agent starts implementing all of them before landing the original fix.
Should: The agent separates blocking defects from deferrable or backlog comments and preserves the original scope.
Expected failure: The agent assumes every review comment is mandatory and turns review into an unbounded rewrite.
Reproduce with: tests/fixtures/valid/packs/harness-engineering/pack.yaml

### eval.harness.slop-feedback-not-systematized: Slop Feedback Not Systematized

- Type: eval-scenario
- Status: reviewed
- Claim strength: synthesized
- Derived from claims: claim.harness.slop-garbage-collection, claim.harness.feedback-distills-next-run

Given: Reviewers collect recurring slop patterns for a week, but the cleanup loop fixes only the current code and saves no next-run artifact.
Should: The agent identifies the missing systematization step and records a durable guardrail, artifact, or follow-up.
Expected failure: The agent treats cleanup as complete because the visible slop was removed once.
Reproduce with: tests/fixtures/valid/packs/harness-engineering/pack.yaml
