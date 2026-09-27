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
the [approved lifecycle](/Docs/agents/14-path-ownership-boundaries.md#approved-lifecycle)
for managed installation. Flat sync is limited to explicitly authorised
transitional recovery, not ordinary home-runtime installation. Generate `.skillsets/**`
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

The historical rooted sync at user scope also risked relinking home directories
to an incorrect repo-local runtime surface when that surface was stale, flat,
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

Follow the [transitional recovery runbook](/Docs/runbooks/migrate-flat-projection-to-rooted.md)
to select the existing consumer, source, targets and mutation authority. It
separates workspace refresh from home-runtime relinking. Preserve prior working
state; do not substitute source relinking for an unavailable SDK/Tessl route.

Maintain legacy `.skillsets/**` compatibility metadata separately:

```bash
python3 Infrastructure/scripts/lifecycle-and-sync/generate_skillset_manifests.py --write --json
python3 Infrastructure/scripts/validation-and-linting/check_context_budget.py --projection rooted --json
```

## Evidence

- `Docs/runbooks/migrate-flat-projection-to-rooted.md` records the retirement,
  the supported `flat` mode, explicit recovery authority, and the current
  compatibility commands.
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
