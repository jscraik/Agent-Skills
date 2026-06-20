---
schema_version: 1
---

# skills-system Agent Guide

## Scope

- Applies to `skills-system/**`.
- Inherits the repository root [AGENTS.md](../AGENTS.md).

## Edit Policy

- Treat this subtree as governed system-skill bridge content, not ordinary
  first-party skill source.
- Preserve upstream lock and bridge contracts. Refresh system skills only
  through the lock/projection workflow or an explicitly documented migration.
- Do not silently fork bundled or system skills. If a local patch is necessary,
  record the reason, upstream source, expected refresh path, and validation.
- Keep creator and installer flow references under the system-skill bridge
  instead of duplicating long procedures into this AGENTS file.

## Context Pointers

- System lock: `Infrastructure/GOVERNANCE/skills-system-upstream.lock.json`.
- Repo surface ownership: [../Docs/agents/15-repo-surface-ownership.md](../Docs/agents/15-repo-surface-ownership.md).
- Path ownership: [../Docs/agents/14-path-ownership-boundaries.md](../Docs/agents/14-path-ownership-boundaries.md).

## Validation

- For system-skill refreshes, run the projection-integrity or upstream-lock
  validator that owns the changed files.
- For manual edits, report why the normal refresh path was not used and what
  downstream runtime surface was or was not proven.
