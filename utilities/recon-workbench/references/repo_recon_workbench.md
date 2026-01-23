# Recon Workbench Repo Notes (Local)

Source: `/Users/jamiecraik/dev/recon-workbench`

## Purpose
- CLI-first interrogation toolkit for macOS apps, iOS simulator apps, web/React apps, and OSS repos.
- Evidence-backed runs with explicit authorization, no circumvention, and artifact citations.

## Key entry points
- `README.md`: workflow, risks, prerequisites, quickstart.
- `Skills.md`: skill index and guardrails; probe catalog overview.
- `docs/`: authoritative details for probes, schemas, legal notes, artifacts, and CI checks.

## Core commands (CLI)
- `./recon doctor`, `./recon setup`
- `./recon init`, `./recon plan`, `./recon run --confirm-run`
- `./recon diff`, `./recon summarize`, `./recon report`

## Evidence outputs
- `runs/<target>/<session>/<run>/raw/...`
- `runs/<target>/<session>/<run>/derived/findings.json`
- `runs/<target>/<session>/<run>/report.md`

## Notes for skill usage
- Keep CLI-first design; MCP is optional layer.
- Honor AGENTS.md and docs/LEGAL_NOTES_UK_EU.md.
- Use docs/ARTIFACTS_AND_EVIDENCE.md and docs/DATA_HANDLING.md for evidence and redaction rules.

