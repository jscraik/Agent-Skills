# Recon Workbench Repo Notes (Local)

Source: `/Users/jamiecraik/dev/recon-workbench`

## Purpose
- CLI-first interrogation toolkit for macOS, iOS Simulator, web apps, and OSS repos.
- Evidence-backed runs with explicit authorization, no circumvention, and artifact citations.

## Key entry points
- `README.md`: workflow, risks, prerequisites, quickstart.
- `AGENTS.md`: repo agent guardrails.
- `docs/agents/`: scope/safety, CLI usage, dev workflow, AI governance.
- `docs/reference/`: gold standard, legal notes, data handling, dependencies, schemas, probe catalog, CI checks.

## Core commands (CLI)
- Primary: `uv run python -m rwb <command>`
- Wrapper: `./recon <command>` (legacy/extended CLI; see `docs/reference/CLI_REFERENCE.md`)

Common (rwb):
- `rwb doctor`, `rwb authorize`, `rwb plan`, `rwb run`, `rwb summarize`, `rwb validate`, `rwb manifest`, `rwb cleanup`

Common (recon wrapper):
- `recon init`, `recon plan`, `recon run --write --exec --confirm-run`, `recon diff`, `recon summarize`, `recon report`

## Evidence outputs
- Preferred: `data/runs/<target>/<session>/<run>/raw/...` and `data/runs/<target>/<session>/<run>/derived/...`
- Legacy: `runs/<target>/<session>/<run>/...` is still supported.

## Notes for skill usage
- Keep CLI-first design; MCP is optional.
- Honor `docs/reference/LEGAL_NOTES_UK_EU.md` and `docs/reference/THREAT_MITIGATIONS.md`.
- Use `docs/reference/ARTIFACTS_AND_EVIDENCE.md` and `docs/reference/DATA_HANDLING.md` for evidence + redaction.
