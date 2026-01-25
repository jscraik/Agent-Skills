# Artifacts & Evidence Standard

Summary from `docs/reference/ARTIFACTS_AND_EVIDENCE.md`.

## Required per run
- `manifest.json` (hashes + provenance)
- `raw/<probe_id>/...` (unaltered probe outputs)
- `derived/findings.json` (schema-valid)
- Target-level `report.md` and `report.json`

Preferred storage: `data/runs/<target>/<session>/<run>/...` (legacy `runs/...` still supported).

## Evidence rules
- Every finding must cite at least one evidence path.
- If evidence is insufficient, mark as hypothesis and request additional probes.

## Integrity
- Include SHA-256 hashes for artifacts in `manifest.json`.
- Treat the manifest as source of truth for provenance.

## Baseline vs stimulus
- Record a baseline run before stimulus when the goal is behavior understanding.
- Diffs typically provide higher signal than raw logs.
