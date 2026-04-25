---
title: Rooted Projection Sync Ownership Guard
asset_family: rooted skill runtime projection
owner: Agent Skills Team
source_artifact: Docs/plans/2026-04-24-feat-context-budgeted-skill-trees-plan.md
freshness_reviewed_on: 2026-04-25
review_after_days: 90
---

# Rooted Projection Sync Ownership Guard

## Table of Contents
- [Problem](#problem)
- [Resolution](#resolution)
- [Evidence](#evidence)
- [Follow-up](#follow-up)

## Problem

Rooted projection mutation can become misleading when it validates only the
freshly generated in-memory reports and ignores stale files that already exist
on disk. A hand-written file under `.skillsets/**` can make
`check_context_budget.py --projection rooted` fail with
`UNOWNED_SKILLSET_FILE` even if `ask skills sync --scope workspace
--projection rooted` reports success.

User-scope rooted sync has a related runtime risk: relinking home directories to
`.agents/skills` is only safe when the repo-local workspace is already the
generated rooted runtime surface. If the workspace is stale, flat, missing, or
rolled back, user sync can expose the wrong runtime while still reporting
`projection_mode: rooted`.

## Resolution

Treat rooted workspace sync as the owner of the generated `.skillsets/**`
surface. During rooted workspace mutation, prune files that are not canonical
`<root>/manifest.jsonl` outputs before writing the generated manifests. This
keeps the mutation command and the context-budget validation gate aligned.

Treat rooted user sync as a relink-only step that depends on a valid rooted
workspace runtime. Before relinking `~/.agents/skills` or `~/.codex/skills`,
verify that repo-local `.agents/skills` contains only expected first-level root
skill sets and that those roots are generated rooted projection directories. If
the check fails, return `ERR_VALIDATION` and tell the operator to run workspace
rooted sync first.

## Evidence

- `Infrastructure/scripts/lib/ask/commands/skills.py` prunes unowned
  `.skillsets/**` files during rooted workspace sync.
- `Infrastructure/scripts/lib/ask/commands/skills.py` rejects rooted user sync
  when the workspace runtime surface is missing, flat, stale, or non-generated.
- `Infrastructure/tests/test_ask_skills_sync_security.py` covers unowned
  `.skillsets` pruning, valid rooted user relink, and invalid rooted workspace
  rejection.
- `python3 -m py_compile Infrastructure/scripts/lib/ask/commands/skills.py Infrastructure/tests/test_ask_skills_sync_security.py`
  passed.
- `ruff check Infrastructure/scripts/lib/ask/commands/skills.py Infrastructure/tests/test_ask_skills_sync_security.py`
  passed.
- `python3 -m pytest Infrastructure/tests/test_ask_skills_sync_security.py Infrastructure/tests/test_context_budgeted_skillsets.py -q`
  passed with `37 passed`.

## Follow-up

- Keep rooted sync regression tests paired with context-budget tests whenever
  `.skillsets/**`, `.agents/skills/**`, or user-scope relink behavior changes.
- If the rooted workspace/user sync contract changes, update
  `Docs/runbooks/migrate-flat-projection-to-rooted.md` and this solution entry
  together.
