# Validation Artifacts Retention

This directory intentionally includes both passing and failed historical validation runs.

## Why failed runs are kept

- Some snapshots are preserved as regression evidence for harness behavior, including timeout-driven failures (`exit_code: 124`) under older runner conditions.
- These artifacts support reproducibility and review continuity when hardening validation/reporting logic.

## Interpretation notes

- Files under `Infrastructure/artifacts/validation/touched-skills-20260329-full/` are historical evidence snapshots, not a claim that current head state is passing.
- Current validation status should be determined from active CI and fresh `ask repo validate` / targeted script runs, not from historical retained artifacts alone.
