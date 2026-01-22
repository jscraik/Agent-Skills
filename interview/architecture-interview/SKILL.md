---
name: architecture-interview
description: "Plan and review architecture decisions via a structured interview and ADR output. Use when choosing between system design alternatives."
metadata:
  short-description: "Structured architecture decision interview with ADR output."
---

# architecture-interview (wrapper)

Use **Interview Kernel** rules, state model, synthesis, and approval gate.
Kernel-enforced: Question validity gate, DISCOVER vs DECIDE intent switch, Decisions table, and Assumptions register + approval.

## What this wrapper optimizes for

- A clear, auditable architectural choice with explicit sacrifices
- A usable ADR draft (status: Proposed) before implementation starts
- Operability: failure modes, rollout/migration, observability, verification

## Interaction notes

- Must use AskUserQuestion-style multiple choice (3–5 options, include a recommended default).
- Start in **DECIDE**: architecture is primarily decision forcing.
- In Delta mode (existing ADR/draft spec), do not re-ask settled decisions; fill gaps and verify consequences.

## User profile alignment (Jamie)

Follow `/Users/jamiecraik/.codex/USER_PROFILE.md`: single-threaded, explicit steps, low cognitive load. Keep one question per turn and map any free-text reply to the closest option with confirmation.

## Philosophy

- Architecture is decision-making under constraints; the goal is a clear, auditable tradeoff.

## Anti-patterns to avoid

- Choosing an architecture without naming what is sacrificed.
- Deferring decisions to “later” when they block progress now.
- Asking for implementation details before the decision is approved.

## Variation

- Tailor prompts to the system type (CRUD vs streaming vs ML vs infra) and scale.
- Avoid repeating identical option sets; vary tradeoffs based on context.

## Default mode + intent

- Mode: `standard` (use `deep` for major rewrites)
- Intent: start `DECIDE`

## When to use

- Choosing between architectural alternatives.
- Producing an ADR before implementation.
- Clarifying constraints (security/perf/compliance/cost) that dominate design.

## Architecture spine (10 prompts)

1) **Decision statement**
- What decision must we make? (one sentence)

2) **Decision drivers**
- Top priority driver: performance vs simplicity vs security vs extensibility?

3) **Hard constraints**
- Runtime/deployment, compliance, cost ceilings, team skill constraints, deadlines.

4) **Alternatives on the table**
- Pick 2–4 options that are truly viable.

5) **Decision criteria**
- What must be true for the chosen option to “win”? (latency, operability, cost, etc.)

6) **Tradeoff (DECIDE)**
- Which do we sacrifice: fastest implementation, lowest complexity, or best long-term flexibility?

7) **Integration boundaries**
- 1–3 most important touchpoints.

8) **Failure modes**
- Worst credible failure mode + how we detect it.

9) **Migration/rollout**
- big-bang vs incremental vs parallel run + rollback plan.

10) **Verification**
- What proves the decision works (benchmarks, tests, SLOs, incident reduction)?

## Architecture synthesis add-on (ADR required)

Append an ADR block:

```md
## ADR Draft

# ADR: <title>

## Context
## Decision
## Status
Proposed (pending approval)

## Decision drivers
## Alternatives considered
## Decision criteria
## Consequences
- Positive:
- Negative / sacrificed:

## Migration / rollout / rollback
## Verification plan
## Observability plan
```

## Inputs
- User request details and any relevant files/links.

## Outputs
- Kernel synthesis + ADR Draft (Proposed).
- Include `schema_version: 1` if outputs are contract-bound.

## Constraints
- Redact secrets/PII by default.
- Avoid destructive operations without explicit user direction.

## Validation
- Fail fast and report missing inputs before proceeding.

## Examples

- "Help me choose between a modular monolith and microservices for our app."
- "Create an ADR for moving from a REST API to GraphQL."

## References
- `references/contract.yaml` (output contract)
- `references/evals.yaml` (quality checks)

## Remember

The agent is capable of extraordinary work in this domain. These guidelines unlock that potential—they don't constrain it.
Use judgment, adapt to context, and push boundaries when appropriate.

## Procedure
1) (Optional) Delta scan: extract existing constraints/decisions from any draft ADR/spec.
2) Execute the kernel interview loop using the Architecture spine.
3) Produce ADR Draft + approval gate.
4) Handoff to planning/execution using the approved ADR.
