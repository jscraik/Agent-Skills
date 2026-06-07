# Skills SDK Main Reconciliation Route Tracker

## Route Tracker

Route id: PU-013B-sdk-capability-truth-reconcile-lenses-determinism

## Exact Next Slice

Reconcile merged PR 242 into SDK capability truth by updating `ask sdk status`, status tests, and SDK pipeline/status artifacts so the lens and determinism commands are visible as implemented advisory/read-only capabilities with executable evidence.

## Current Main Truth

- `ask sdk lenses validate --json --robot` is implemented and validates the lens catalog without mutation.
- `ask sdk lenses select --prompt 'review a skill for validation confidence' --intent validation_review --json --robot` is implemented and emits deterministic lens selection receipts without mutation.
- `ask sdk determinism audit --scope skills --limit 10 --json --robot` is implemented and emits advisory candidate reports without mutation.
- Before PU-013B, `ask sdk status --json --robot` did not expose dedicated capability rows for these merged PR 242 surfaces.

## Closeout Evidence

- `ask sdk status` now exposes `sdk_lenses` and `determinism_audit` as `implemented`, non-mutating capabilities.
- `artifacts/recommended-skills-sdk-pipeline.html` contains matching capability truth rows for both capabilities.
- Focused validation covers the status matrix, live SDK status payload, pipeline artifact, lens commands, determinism audit command, and interpreter-preserving public wrappers.

## Resume Condition

Resume implementation only after the worktree is clean, `main` is current, and PU-013B is performed in a dedicated feature worktree without mixing preserved primary-checkout dirty state.
