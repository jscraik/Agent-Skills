# Recon Workbench -- Agent Instructions (AGENTS.md)

## Scope & safety
- Only analyze targets you own or have explicit permission to test, or open-source repos.
- Do not propose or run DRM/TPM bypass, decryption/circumvention, license checks bypass, or credential theft.
- Prefer observation-first methods (OS/browser instrumentation, logs, traffic capture).
- Use approved probes from probes/catalog.json. Avoid ad-hoc commands when a probe exists.

## Evidence discipline
- Every finding must cite one or more evidence paths under `data/runs/...` (preferred) or legacy `runs/...`
- If evidence is insufficient, request additional probes rather than speculating.
- Summaries must list commands used + artifact locations.

## Outputs
- Write derived output to `data/runs/<target>/<session>/<run>/derived/` (legacy `runs/...` supported)
- Produce:
  - findings.json (schema-valid)
  - report.md (human-readable; all claims anchored to artifact paths)

## Escalation
- When static signal is low or protections are detected, switch to $worst_case_interrogation.
