---
name: architecture-interview
description: "Plan and review architecture decisions via a structured interview and ADR output. Use when choosing between system design alternatives."
---

# architecture-interview (wrapper)

Use **Interview Kernel** rules, state model, synthesis, and approval gate.
Kernel-enforced: Question validity gate, DISCOVER vs DECIDE intent switch, Decisions table, and Assumptions register + approval.

## Philosophy
- Architecture is decision-making under constraints; the goal is a clear, auditable tradeoff.

## Anti-patterns to avoid
- Avoid choosing an architecture without naming what is sacrificed.
- Avoid deferring decisions to “later” when they block progress now.
- Avoid asking for implementation details before the decision is approved.

## Variation
- Weight questions toward the dominant constraint (performance, security, simplicity).

## Empowerment
- Make the decision table the source of truth; require explicit approval.

## Default mode + intent

* Mode: `standard` (use `deep` for major rewrites)
* Intent: start `DECIDE` (architecture is mostly decision forcing)

## When to use

- Use when choosing between architectural alternatives.
- Use when constraints require explicit tradeoffs.
- Use when an ADR must be produced before implementation.

## Example prompts

- "We need to pick between two architectures — help me decide."
- "I want an ADR before we build this system."
- "We have security and performance constraints to trade off."

## Architecture spine (9 prompts)

1. **Decision statement**

* “What decision must we make? (Choose the best one-sentence framing.)”

2. **Decision drivers**

* “Top priority driver: performance vs simplicity vs security vs extensibility?”

3. **Constraints**

* “Hard constraints (runtime, deployment, compliance, cost ceilings)?”

4. **Alternatives**

* “Which alternatives are on the table? (Pick 2–4.)”

5. **Tradeoff (DECIDE)**

* “Which do we sacrifice: fastest implementation, lowest complexity, or best long-term flexibility?”

6. **Integration boundaries**

* “What systems/modules does this touch? Name the 1–3 most important touchpoints.”

7. **Failure modes**

* “What’s the worst credible failure mode here?”

8. **Migration/rollout**

* “Migration strategy: big-bang vs incremental vs parallel run?”

9. **Verification**

* “What proves the decision works (benchmarks, tests, SLOs, incident reduction)?”

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
## Consequences
- Positive:
- Negative / sacrificed:

## Migration / rollout
## Verification plan
```

## Remember

The agent is capable of extraordinary work in this domain. These guidelines unlock that potential—they don't constrain it.
Use judgment, adapt to context, and push boundaries when appropriate.

## Inputs
- User request details and any relevant files/links.


## Outputs
- A structured response or artifact appropriate to the skill.
- Include `schema_version: 1` if outputs are contract-bound.


## Constraints
- Redact secrets/PII by default.
- Avoid destructive operations without explicit user direction.


## Validation
- Run any relevant checks or scripts when available.
- Fail fast and report errors before proceeding.
## Procedure
1) Clarify scope and inputs.
2) Execute the core workflow.
3) Summarize outputs and next steps.

## Antipatterns
- Do not add features outside the agreed scope.
