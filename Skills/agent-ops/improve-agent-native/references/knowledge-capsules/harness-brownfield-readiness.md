# Brownfield Readiness

Make existing codebases agent-ready by tightening boundaries, vocabulary, issue states, validation loops, diagnostics, and shared decision memory.

Pack id: pack.harness-engineering
Facet id: brownfield_readiness
Runtime dependency: none; this slice is generated from a KnowledgeOS pack export.

## Claim Cards

### claim.harness.brownfield-ready-boundaries: Brownfield Harnesses Start With Boundaries

- Type: claim-card
- Status: reviewed
- Claim strength: inferred

Brownfield codebases become more agent-ready when teams carve clean interfaces, add local docs, turn on lints, and provide examples or graders for prompt-like artifacts.

### claim.harness.codebase-new-starter: Treat Each Agent Run Like A New Starter

- Type: claim-card
- Status: reviewed
- Claim strength: direct

Codebases should be designed as if every agent run starts without durable tacit memory of the project.

### claim.harness.deep-modules-control: Deep Modules Bound Agent Work

- Type: claim-card
- Status: reviewed
- Claim strength: direct

Deep modules with simple public interfaces and substantial internal behavior create safer boundaries for delegated agent work.

### claim.harness.validation-autonomy-bottleneck: Validation Quality Caps Autonomy

- Type: claim-card
- Status: reviewed
- Claim strength: direct

The safe scale of agent autonomy is limited by what the organization can automatically validate.

### claim.harness.agent-legible-failures: Failures Should Be Agent-Legible

- Type: claim-card
- Status: reviewed
- Claim strength: direct

Failing commands should tell agents the command, location, exit code, focused output, and likely remediation path.

### claim.harness.human-sync-architecture-drift: Human Sync Counters Architecture Drift

- Type: claim-card
- Status: reviewed
- Claim strength: direct

High agent-mediated code velocity can hide architectural pattern changes from humans, so teams need synchronous alignment on architectural drift.

### claim.harness.issue-states-route-agents: Issue States Route Agent Work

- Type: claim-card
- Status: reviewed
- Claim strength: direct

Agent-ready backlogs need explicit issue categories and states so work can route to the right workflow without hidden human triage.

### claim.harness.review-needs-proof: Agent Work Needs Review Evidence

- Type: claim-card
- Status: reviewed
- Claim strength: direct

Agent-produced work should be accepted through review evidence, not through invisible trust in the trajectory.

### claim.harness.human-attention-scarce: Human Attention Is The Scarce Resource

- Type: claim-card
- Status: reviewed
- Claim strength: direct

Harness engineering treats synchronous human attention as the scarce production resource, while agent tokens and code generation are comparatively parallelizable.

### claim.harness.shared-language-compression: Shared Language Compresses Agent Context

- Type: claim-card
- Status: reviewed
- Claim strength: direct

Shared domain language acts as a compression layer for agents because it turns repeated explanation into durable, searchable repo context.

### claim.harness.adr-decision-memory: ADRs Preserve Non-Obvious Decisions

- Type: claim-card
- Status: reviewed
- Claim strength: direct

Agents need decision records for architecture choices that are hard to reverse, surprising without context, or tradeoff-heavy.

## Principles

### principle.harness.brownfield-readiness-starts-with-boundaries: Brownfield Readiness Starts With Boundaries

- Type: principle
- Status: reviewed
- Claim strength: synthesized
- Derived from claims: claim.harness.brownfield-ready-boundaries, claim.harness.codebase-new-starter

Make brownfield systems agent-ready by clarifying boundaries before scaling autonomy.

Rationale: Agents do better in existing codebases when clean interfaces, local docs, lints, examples, and graders make decomposition and correctness visible.

### principle.harness.agent-readiness-is-environment-design: Agent Readiness Is Environment Design

- Type: principle
- Status: reviewed
- Claim strength: synthesized
- Derived from claims: claim.harness.codebase-new-starter, claim.harness.deep-modules-control, claim.harness.issue-states-route-agents

Improve agent performance by shaping the codebase, backlog, validation, and module boundaries around repeatable agent entry.

Rationale: Prompting alone cannot compensate for tacit architecture, ambiguous issues, hidden constraints, and shallow modules.

### principle.harness.validation-caps-autonomy: Validation Caps Autonomy

- Type: principle
- Status: reviewed
- Claim strength: synthesized
- Derived from claims: claim.harness.validation-autonomy-bottleneck, claim.harness.review-needs-proof

Grant autonomy only to the level that current validation can prove.

Rationale: Faster and more parallel agents increase risk when correctness, style, architecture, documentation, and deployment safety are not automatically checkable.

## Heuristics

### heuristic.harness.ready-brownfield-by-boundaries: Ready Brownfield By Boundaries

- Type: heuristic
- Status: reviewed
- Claim strength: synthesized
- Derived from claims: claim.harness.brownfield-ready-boundaries

Before increasing autonomy in a brownfield repo, add or repair the interfaces, local docs, lints, examples, and graders that make the task decomposable.

### heuristic.harness.make-failures-actionable: Make Failures Actionable

- Type: heuristic
- Status: reviewed
- Claim strength: synthesized
- Derived from claims: claim.harness.agent-legible-failures

Design checks so failure output tells a cold agent what failed, where, why it matters, and the likely next repair.

### heuristic.harness.audit-validation-before-autonomy: Audit Validation Before Autonomy

- Type: heuristic
- Status: reviewed
- Claim strength: synthesized
- Derived from claims: claim.harness.validation-autonomy-bottleneck

Before expanding agent scope, list what the system can prove automatically and keep autonomy inside that proof envelope.

### heuristic.harness.sync-humans-on-architecture-drift: Sync Humans On Architecture Drift

- Type: heuristic
- Status: reviewed
- Claim strength: synthesized
- Derived from claims: claim.harness.human-sync-architecture-drift, claim.harness.human-attention-scarce

Spend synchronous human time on architecture drift when agent velocity makes the system change faster than shared mental models.

## Checklists

### checklist.harness.agent-ready-codebase: Agent-Ready Codebase Checklist

- Type: checklist
- Status: reviewed
- Claim strength: synthesized
- Derived from claims: claim.harness.shared-language-compression, claim.harness.adr-decision-memory, claim.harness.codebase-new-starter, claim.harness.deep-modules-control, claim.harness.issue-states-route-agents, claim.harness.validation-autonomy-bottleneck

- [ ] Check whether domain vocabulary is explicit and current enough for the task.
- [ ] Check whether surprising or hard-to-reverse decisions have ADRs or equivalent records.
- [ ] Check whether module boundaries reveal where agents may safely work.
- [ ] Check whether tests protect the public boundary of delegated work.
- [ ] Check whether each issue has one primary category, one state, and one next proof obligation.
- [ ] Check whether validation covers the autonomy being requested.
- [ ] Record unresolved tacit knowledge as a blocker, follow-up, or accepted risk.

## Rubrics

### rubric.harness.agent-readiness: Agent Readiness Rubric

- Type: rubric
- Status: reviewed
- Claim strength: synthesized
- Derived from claims: claim.harness.codebase-new-starter, claim.harness.deep-modules-control, claim.harness.validation-autonomy-bottleneck

- visible-language: Can an agent discover the domain language needed for the task?
  - pass: Relevant terms, aliases, and naming conventions are explicit in a bounded source.
  - fail: The agent must infer important language from scattered code or maintainer memory.
- boundary-depth: Are module boundaries deep enough for delegated work?
  - pass: Public interfaces and boundary tests let agents work inside a bounded area.
  - fail: The task crosses leaky internals with weak or missing boundary checks.
- issue-routability: Does the work item have one clear state and next proof obligation?
  - pass: Category, state, next action, and required evidence are explicit.
  - fail: The issue mixes discovery, implementation, validation, and closeout without routing.
- validation-budget: Does available validation support the requested autonomy?
  - pass: Automated checks cover the behavior, architecture, docs, or deployment claim being delegated.
  - fail: The requested autonomy exceeds what current checks can verify.

## Lenss

### lens.harness.agent-readiness: Agent Readiness Lens

- Type: lens
- Status: reviewed
- Claim strength: synthesized
- Derived from claims: claim.harness.codebase-new-starter, claim.harness.shared-language-compression, claim.harness.validation-autonomy-bottleneck

- Look for tacit knowledge that a capable new starter would need but cannot see.
- Treat vocabulary, ADRs, module boundaries, issue states, and tests as routing surfaces.
- Compare requested autonomy to actual validation coverage.
- Prefer reducing ambiguity at the source over adding longer prompts.

## Eval Scenarios

### eval.harness.brownfield-harness-without-boundaries: Brownfield Harness Without Boundaries

- Type: eval-scenario
- Status: reviewed
- Claim strength: synthesized
- Derived from claims: claim.harness.brownfield-ready-boundaries

Given: A team increases agent autonomy in a legacy code area with hidden invariants, unclear interfaces, no local docs, and weak lint or example coverage.
Should: The agent recommends boundary, documentation, lint, example, or grader work before scaling autonomous changes.
Expected failure: The agent responds by adding more generic prompt text while leaving the brownfield code unreadable to agents.
Reproduce with: tests/fixtures/valid/packs/harness-engineering/pack.yaml

### eval.harness.architecture-drift-hidden-by-agent-velocity: Architecture Drift Hidden By Agent Velocity

- Type: eval-scenario
- Status: reviewed
- Claim strength: synthesized
- Derived from claims: claim.harness.human-sync-architecture-drift

Given: A team ships many agent-authored changes and discovers that core architectural patterns changed without shared human understanding.
Should: The agent recommends a synchronous architecture alignment loop plus a durable ADR or spec update.
Expected failure: The agent proposes only more line-level review or more automated tests.
Reproduce with: tests/fixtures/valid/packs/harness-engineering/pack.yaml

### eval.harness.autonomy-without-validation: Autonomy Without Validation

- Type: eval-scenario
- Status: reviewed
- Claim strength: synthesized
- Derived from claims: claim.harness.validation-autonomy-bottleneck

Given: A team wants agents to autonomously merge deployment-path changes, but there are no reliable tests, docs checks, deployment smoke checks, or rollback proof.
Should: The agent refuses to call the workflow autonomous and identifies validation gaps before increasing authority.
Expected failure: The agent treats model capability or successful code generation as sufficient evidence for autonomous merge authority.
Reproduce with: tests/fixtures/valid/packs/harness-engineering/pack.yaml
