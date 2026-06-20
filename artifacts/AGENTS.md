---
schema_version: 1
---

# artifacts Agent Guide

## Scope

- Applies to `artifacts/**`.
- Inherits the repository root [AGENTS.md](../AGENTS.md); this file only adds
  artifact-specific authority rules.

## Edit Policy

- Treat this subtree as evidence, generated reports, review outputs, and
  intentionally retained artifacts unless a nearby index or schema proves a file
  is an authored source or fixture.
- Do not add new run logs, ad hoc telemetry, or historical output here as normal
  source. Convert it to a documented fixture, reference, summary, or allowlisted
  archive first.
- Keep local code/test truth, artifact evidence, PR state, review state, and
  release-readiness claims separate in closeout language.
- For ownership questions, follow [Repo Surface Ownership](../Docs/agents/15-repo-surface-ownership.md)
  and [Path Ownership Boundaries](../Docs/agents/14-path-ownership-boundaries.md).

## Context Pointers

- Historical artifact policy: [Repo Surface Ownership](../Docs/agents/15-repo-surface-ownership.md#future-artifact-rule).
- Review evidence patterns: `artifacts/reviews/**`.
- Generated SDK visual/reference artifacts: `artifacts/*.html`.

## Validation

- For changed artifact files, prove the owning generator, reader, fixture role,
  or retention reason before closeout.
- Run the narrowest command that reproduces or validates the artifact. If the
  generator cannot run, report `blocked` and keep the artifact claim bounded to
  manual inspection.
