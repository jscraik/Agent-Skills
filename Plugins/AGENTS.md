---
schema_version: 1
---

# Plugins Agent Guide

## Scope

- Applies to uppercase `Plugins/**`.
- Inherits the repository root [AGENTS.md](../AGENTS.md).

## Edit Policy

- Treat uppercase `Plugins/**` as canonical plugin-owned source unless a
  nested guide or manifest explicitly marks a path as generated output.
- Keep plugin behavior in canonical plugin source, bundled hooks, and related
  `Infrastructure/**` contracts. Do not move product behavior into lowercase
  runtime/cache mirrors.
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
