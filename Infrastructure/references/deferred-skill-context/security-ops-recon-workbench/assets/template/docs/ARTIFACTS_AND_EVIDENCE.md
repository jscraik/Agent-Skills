# Artifacts & Evidence Standard

Goal: every conclusion must be reproducible and auditable.

## Required per run
- manifest.json (target hash, timestamp, tool versions)
- raw/<probe_id>/... (unaltered probe outputs)
- derived/findings.json (schema-valid)
- derived/report.md (human report; every claim references artifact paths)

## Evidence rules
- Every finding must cite at least one evidence path.
- If evidence is insufficient, mark as hypothesis and request additional probes.

## Integrity
- Include SHA-256 hashes for artifacts in manifest.json.
- Treat the manifest as the source of truth for run provenance.

## Baseline vs stimulus
- Always record a baseline run before stimulus runs if the goal is "understand behavior".
- Diffs typically provide higher signal than raw logs.
