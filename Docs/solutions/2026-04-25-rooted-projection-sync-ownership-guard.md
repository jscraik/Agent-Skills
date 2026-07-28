---
title: Rooted Projection Sync Ownership Guard
asset_family: rooted skill runtime projection
owner: Agent Skills Team
source_artifact: Docs/plans/2026-04-24-feat-context-budgeted-skill-trees-plan.md
freshness_reviewed_on: 2026-07-28
review_after_days: 90
---

# Rooted Projection Sync Ownership Guard

## Status

Rooted runtime projection mode is retired. This entry preserves the historical
ownership failure and its lesson; it is not a current operator runbook. Use
`flat` for normal workspace and user sync. Generate `.skillsets/**`
compatibility manifests with the dedicated manifest generator rather than the
removed rooted sync mode.

## Table of Contents

- [Status](#status)
- [Problem](#problem)
- [Resolution](#resolution)
- [Evidence](#evidence)
- [Follow-up](#follow-up)

## Problem

The retired rooted projection mutation could become misleading when it
validated only freshly generated in-memory reports and ignored stale files
already on disk. A hand-written file under `.skillsets/**` could make the
compatibility context-budget check fail with `UNOWNED_SKILLSET_FILE` even after
the historical rooted sync command reported success.

The historical user-scope rooted sync also risked relinking home directories to
an incorrect repo-local runtime surface when that surface was stale, flat,
missing, or rolled back.

## Resolution

### Historical Resolution

The removed rooted workspace sync owned the generated `.skillsets/**` surface
and pruned files that were not canonical `<root>/manifest.jsonl` outputs before
writing generated manifests. The removed user sync also validated the rooted
workspace surface before relinking home runtime directories.

Those behaviors are historical evidence only. Current operators must not run
`ask skills sync --projection rooted`; the CLI rejects that mode with
`ERR_INVALID_PROJECTION_MODE`.

### Current Resolution

Use flat projection sync for normal workspace and user runtime materialization:

```bash
python3 bin/ask skills sync --scope workspace --projection flat --json
python3 bin/ask skills sync --scope user --projection flat --json
python3 bin/ask skills handles --check --json
```

Maintain legacy `.skillsets/**` compatibility metadata separately:

```bash
python3 Infrastructure/scripts/lifecycle-and-sync/generate_skillset_manifests.py --write --json
python3 Infrastructure/scripts/validation-and-linting/check_context_budget.py --projection rooted --json
```

## Evidence

- `Docs/runbooks/migrate-flat-projection-to-rooted.md` records the retirement,
  supported `flat` and `hybrid` modes, and the current compatibility commands.
- `Infrastructure/scripts/lib/ask/commands/skills_impl.py` returns
  `ERR_INVALID_PROJECTION_MODE` for removed projection modes and directs SDK
  callers to `--projection flat`.
- The historical implementation and tests remain useful for understanding why
  generated compatibility surfaces require one owner, but they do not prove a
  runnable rooted sync path today.

## Follow-up

- Keep compatibility-manifest generation and context-budget validation paired
  whenever `.skillsets/**` changes.
- If supported projection modes change, update
  `Docs/runbooks/migrate-flat-projection-to-rooted.md`, current command
  metadata, and this historical solution entry together.
