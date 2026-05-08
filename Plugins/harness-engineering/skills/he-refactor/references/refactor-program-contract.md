# Refactor Program Contract

Use this reference after `he-refactor` accepts a high-leverage migration
candidate. A refactor program is a deterministic migration safety rail, not an
implementation spec or backlog dump.

## Naming

- With Linear context:
  `.harness/refactors/YYYY-MM-DD-JSC-###-<refactor-slug>.md`
- Without Linear context:
  `.harness/refactors/YYYY-MM-DD-<repo-name>-<refactor-slug>.md`
- Legacy stable names remain readable but are not preferred for new programs.

## Required Program Sections

- Refactor Classification
- Problem Statement
- Root Cause Analysis
- Evidence
- Architectural Impact
- Desired End State
- Migration Strategy
- Execution Phases
- Linear Mapping
- Anti-Regression Constraints
- Eval Requirements
- Success Criteria
- Safe Rollback Conditions
- Future-Agent Guidance
- Related Systems

## Phase Contract

Each phase must include:

- Objective
- Affected systems
- Expected risk
- Can run in parallel: `yes` or `no`
- Validation requirements
- Rollback conditions
- Linear mapping
- Agent-safe: `yes`, `no`, or `assisted`
- Human review required: `yes` or `no`

## High-Leverage Threshold

Create a program only when completion materially improves architecture,
determinism, cognition, routing, context load, governance simplicity, eval
quality, moat protection, or Linear execution hygiene.

Classify as `Do Not Create` when the finding is cosmetic, speculative, local
cleanup, routine dependency work, or better handled by one small Linear issue.

## Closure Proof

Every program must define the expected eval artifact:

```text
.harness/evals/YYYY-MM-DD-JSC-###-<repo-name>-<slug>-eval.md
```

No related Linear parent, milestone, or slice should be recommended complete
without this proof artifact or a documented exception.
