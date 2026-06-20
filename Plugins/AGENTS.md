---
schema_version: 1
---

# plugins Agent Guide

## Scope

- Applies to lowercase `plugins/**`.
- Inherits the repository root [AGENTS.md](../AGENTS.md).

## Edit Policy

- Treat lowercase `plugins/**` as runtime, cache, or compatibility material
  unless a manifest explicitly classifies a path as canonical source.
- Canonical plugin-owned source normally belongs under uppercase `Plugins/**`
  and related `Infrastructure/**` contracts. Do not hand-edit lower-case
  mirrors to change product behavior.
- On case-insensitive filesystems, be careful with `plugins` and `Plugins`
  path collisions. Verify the real path before moving, deleting, or syncing.
- Use plugin install, status, and sync commands from the root `./bin/ask`
  surface when changing runtime readiness.

## Context Pointers

- Plugin readiness rules: [../Docs/agents/17-skill-management.md#plugin-desktop-readiness](../Docs/agents/17-skill-management.md#plugin-desktop-readiness).
- Path ownership: [../Docs/agents/14-path-ownership-boundaries.md](../Docs/agents/14-path-ownership-boundaries.md).
- Repository vocabulary: [../UBIQUITOUS_LANGUAGE.md](../UBIQUITOUS_LANGUAGE.md).

## Validation

- Before editing, prove whether the target is canonical source, generated
  tracked output, runtime cache, or local state.
- For plugin readiness claims, use the repository plugin status contract rather
  than filesystem presence alone.
