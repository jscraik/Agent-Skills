# Execution Invariants

Purpose: preserve safe, observable, reversible execution.

## Proven Invariants

- Agent-facing commands need machine-readable outputs where practical.
- `--json --robot` is the machine consumer contract.
- Validation must report exact blockers and next actions.
- Catalog parity drift blocks source/projection trust.
- Closeout evidence is required before "done" claims.
- Migration work must be staged and reversible.

## Strategic Assumptions

- Fast daily truth should come from `repo doctor`; full validation is release confidence.
- Eval proof is required for orchestration, routing, and promotion changes.
- Outcome proof is stronger than invocation, telemetry, or structural audit.

## Operating Principles

- Preserve current behavior before extracting internals.
- Make rollback conditions explicit for migrations.
- Validate focused behavior before broad suites.
- Do not close Linear parent work without the related eval artifact.
- Treat non-deterministic command output as execution drift.

## Forbidden Regressions

- Claims of completion without validation evidence.
- New orchestration without eval proof.
- Irreversible migrations without rollback path.
- Validation failures that require archaeology to interpret.
- Invocation analytics treated as outcome success.

## Evidence Basis

- `.harness/refactors/*.md`
- `.harness/strategy/agent-skills-strategy.md`
- `.harness/review/agent-skills-architecture-review.md`
