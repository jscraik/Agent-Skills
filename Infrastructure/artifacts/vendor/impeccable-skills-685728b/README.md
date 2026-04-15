# impeccable Skills Quarantine

Pinned upstream quarantine for the `pbakaus/impeccable` skill set referenced by the user.

## Provenance
- Source repository: `https://github.com/pbakaus/impeccable`
- Pinned ref: `685728b992e873be2d27cc187cf4cdc104582ae7`
- Source subtree: `.codex/skills`
- Imported on: `2026-03-29`
- Import mode: quarantine only

## Purpose
- Preserve the upstream skill tree inside the repo for review without changing live routing.
- Keep the import reversible and auditable.
- Separate upstream review from canonicalization work.

## Contents
- `skills/`: upstream skill tree copied as-is from the pinned ref
- `SHA256SUMS.txt`: file-level SHA-256 manifest for the quarantined copy
- `DECONFLICT.md`: overlap matrix and uplift recommendations against the current local skill graph

## Routing boundary
These skills are **not** part of the canonical repo inventory and are **not** included in sync or surfaced loader paths.

## Next-step guidance
- Use this quarantine when comparing upstream design-skill doctrine to local canonical skills.
- If any of these are promoted later, prefer wrapper/canonicalization work over raw direct import.
