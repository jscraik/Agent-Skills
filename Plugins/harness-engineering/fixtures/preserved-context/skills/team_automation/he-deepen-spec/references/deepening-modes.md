# Harness Engineering Deepen Spec Modes

Read when: you need to choose between targeted-confidence and max-coverage, decide whether artifact-backed execution is warranted, or score which spec sections deserve intervention.

## Table of Contents
- [Purpose](#purpose)
- [Deepening modes](#deepening-modes)
- [Spec kinds and risk](#spec-kinds-and-risk)
- [Weak-spot scoring](#weak-spot-scoring)
- [Agent mapping](#agent-mapping)
- [Execution modes](#execution-modes)
- [Legacy coverage preservation](#legacy-coverage-preservation)

## Purpose
This reference preserves the behavior of the legacy `deepen-spec` prompt while making the safer modern defaults explicit.

## Deepening modes
### `targeted-confidence`
Use by default.

Best for:
- standard or UI specs with 2-5 weak sections
- high-risk specs where tighter contract detail matters more than full exhaust
- users who want a safer second pass without massive context growth

Rules:
- choose only the top 2-5 sections by score
- use at most 1-3 agents per section
- usually keep the total research fan-out to 8 agents or fewer
- rewrite only the selected weak sections

### `max-coverage`
Use only when the user explicitly asks for exhaustive coverage or when preserving the legacy prompt's broad fan-out is clearly the right call.

Best for:
- explicit "run everything" requests
- highly sensitive or cross-cutting specs where multiple reviewer lenses are wanted
- preserving the original deepen-spec workflow's broad coverage strengths

Rules:
- still build a section manifest first
- discover skills, agents, and learnings from the current platform, project, and installed registries when available
- apply clearly relevant skills
- scan deeper learnings under `docs/solutions/`
- run a broader reviewer sweep
- synthesize findings back into the spec instead of pasting raw agent output

## Spec kinds and risk
### Spec kinds
- `standard-spec`: system, service, backend, workflow, or cross-layer contract
- `dedicated-ui-spec`: UI contract under `.harness/specs/`
- `legacy-ui-spec`: compatibility UI contract under `.harness/specs/...-ui-spec.md`

### High-risk signals
- authentication or authorization
- payments, billing, or financial flows
- migrations, backfills, or persistent data changes
- external APIs or third-party integrations
- privacy, compliance, or user-data handling
- concurrency, retries, or long-running workflows
- cross-interface parity
- rollout, monitoring, or operational safety concerns

## Weak-spot scoring
Use a checklist-first, risk-weighted scoring pass.

For each section:
- trigger count = number of checklist problems that apply
- risk bonus = +1 when the topic is high risk and the section materially affects that risk
- critical-section bonus = +1 for `System Boundary`, `Main Flow / Lifecycle`, `Failure Model and Recovery`, `Observability`, or `Acceptance and Test Matrix`

Treat a section as a candidate if:
- it scores 2 or more total points, or
- it scores 1 or more point in a high-risk domain and is materially important

Checklist triggers:
- `Problem Statement / Goals / Non-Goals`
  - problem frame is vague
  - goals lack operational meaning
  - non-goals are missing or weak
- `System Boundary / Core Domain Model`
  - vague nouns or missing entities
  - ownership is unclear
  - fields, defaults, or constraints are missing where they matter
- `Main Flow / Lifecycle`
  - state transitions are missing
  - timing, retries, cancels, or cleanup behavior is unclear
  - happy-path prose hides important edge behavior
- `Interfaces and Dependencies`
  - contracts with external systems are unclear
  - dependency assumptions are unstated
  - trust boundaries are implicit
- `Invariants / Safety Requirements`
  - permissions, secrets, sandboxing, or path/data constraints are underexplored
  - durable-state guarantees are missing
- `Failure Model and Recovery`
  - failure classes are vague
  - retry or cleanup rules are unclear
  - operator expectations are absent
- `Observability`
  - logs, metrics, dashboards, or post-deploy checks are weak
  - there is no practical way to know if the system is healthy
- `Acceptance and Test Matrix / Visual Acceptance Criteria`
  - `SA` or `VAC` items are missing or vague
  - failure, operational, or state-heavy scenarios are absent
- `Open Questions`
  - blockers are hidden as assumptions
  - product questions and technical questions are mixed together

## Agent mapping
Use `Infrastructure/references/sub-agent-map.md` as the canonical lane map.

Default lanes:
- `repo-research-analyst`
- `learnings-researcher`
- `spec-flow-analyzer`

Then add only the specialist lanes that match selected weak sections (for example `architecture-strategist`, `design-lens-reviewer`, `security-lens-reviewer`, `reliability-reviewer`, `api-contract-reviewer`, `deployment-verification-agent`).

## Execution modes
### `direct`
Default.

Use when:
- the selected research scope is small
- inline findings will not create avoidable context pressure

### `artifact-backed`
Use only when:
- more than 5 agents are likely to return meaningful findings
- long section excerpts would be repeated wastefully
- the topic is high risk and bulky research output is likely

Scratch path:
- `.context/harness-engineering/he-deepen-spec/<run-id-or-spec-stem>/`

Artifact rules:
- one compact artifact per section or reviewer cluster
- findings only, no implementation code, no command recipes
- clean up unless the user asked to inspect them

Role availability guardrail:
- before delegation, keep only roles present in `~/.codex/agents/manifest.json`
- if required roles are missing, continue inline/manual and route role creation to `[[codex-agent-creator]]`

## Legacy coverage preservation
The original `deepen-spec` prompt was intentionally direct and broad:
- full spec reread plus linked artifacts
- weak-spot identification
- targeted repo and learnings research
- optional external best-practices and framework-docs grounding
- in-place enhancement summary and next-step menu

The migrated skill preserves those behaviors directly and adds `max-coverage` only as an explicit legacy-compatible extension.
