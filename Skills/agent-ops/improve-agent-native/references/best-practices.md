# Agent-Native Repo Best Practices

Use this reference for practical next moves after an audit identifies repo-readiness gaps.

## Default Improvement Order

1. Clarify AGENTS.md and source-of-truth routing.
2. Add or tighten fast mechanical guardrails.
3. Improve autonomous validation and proof loops.
4. Move durable knowledge into docs, schemas, scripts, or tests.
5. Add recurring maintenance only after the core loop is legible.

## Human Intent, Agent Execution

Keep humans focused on goals, risk, acceptance criteria, and priorities. Let agents handle implementation and routine verification.

When agent behavior repeatedly misses the mark, improve the repo surface that shaped the behavior.

## Repo As System Of Record

Store durable knowledge in versioned files:

- architecture and boundaries
- exact reference facts
- active project state
- decisions
- validation contracts

Do not rely on chat memory for agent-critical instructions.

## Mechanical Invariants

Prefer checks over reminders. Good candidates include:

- validators for generated/source ownership boundaries
- schema checks for machine-readable config
- tests for repeated regressions
- hooks or CI for fast safety gates
- CLI wrappers that emit structured errors

## Proof Loops

Make it easy for an agent to run the nearest meaningful proof:

- fast checks for ordinary edits
- full checks for high-risk changes
- product/API/browser smoke paths where behavior changed
- evidence artifacts where UI or runtime state matters

Skipped checks should be reported as blocked with a concrete reason.

## Lightweight Solo Defaults

Use the smallest process that preserves velocity and recovery:

- concise root guidance
- docs for durable detail
- direct, recoverable workflows where appropriate
- explicit escalation only for judgment-heavy or irreversible decisions
- periodic cleanup only when drift is visible
