---
title: Legacy Skillset Metadata Ownership Guard
asset_family: legacy skillset metadata and context-budget validation
owner: Agent Skills Team
source_artifact: Docs/runbooks/migrate-flat-projection-to-rooted.md
freshness_reviewed_on: 2026-07-26
last_updated: 2026-07-26
review_after_days: 90
---

# Legacy Skillset Metadata Ownership Guard

## Table of Contents
- [Problem](#problem)
- [Resolution](#resolution)
- [Evidence](#evidence)
- [Follow-up](#follow-up)

## Problem

The word `rooted` is retained for legacy `.skillsets/**` metadata and
context-budget validation. It is not a supported runtime projection mode.
Hand-written or stale files under `.skillsets/**` make
`check_context_budget.py --projection rooted --json` fail with
`UNOWNED_SKILLSET_FILE`; that is an ownership signal for metadata, not evidence
that a runtime sync failed.

The old rooted runtime route is retired. Runtime users must not interpret a
legacy metadata result as a reason to relink `~/.agents/skills`,
`~/.codex/skills`, or a workspace runtime surface.

## Resolution

Treat `generate_skillset_manifests.py` as the owner of generated
`.skillsets/**/manifest.jsonl` metadata. The rooted context-budget check
validates that legacy metadata surface and rejects unowned entries rather than
silently treating them as generated output.

For installed runtime projection, use the supported `flat` or `hybrid` routes
in [the flat/hybrid projection runbook](/Docs/runbooks/migrate-flat-projection-to-rooted.md).
Those commands and their current ownership checks determine runtime state. A
successful legacy `.skillsets` check does not prove installed skills, profile
links, cache freshness, or activation.

## Evidence

- `Docs/runbooks/migrate-flat-projection-to-rooted.md` records that rooted
  runtime projection is retired and identifies `flat` and `hybrid` as the
  supported runtime modes.
- `Infrastructure/scripts/validation-and-linting/generate_skillset_manifests.py`
  owns the legacy manifest projection.
- `Infrastructure/scripts/validation-and-linting/check_context_budget.py
  --projection rooted --json` checks legacy metadata ownership and context
  budgets.
- `Infrastructure/tests/test_context_budgeted_skillsets.py` covers the legacy
  budget/ownership surface; `Infrastructure/tests/test_ask_skills_sync_security.py`
  covers supported runtime sync boundaries.

## Follow-up

- Keep legacy `.skillsets` generator and context-budget regressions paired
  whenever that metadata contract changes.
- Do not reintroduce `skills sync --projection rooted`. Any future runtime-mode
  change requires a separately authorised projection contract decision.
- When runtime behavior is the question, follow the current flat/hybrid
  runbook, not this legacy-metadata guard.
