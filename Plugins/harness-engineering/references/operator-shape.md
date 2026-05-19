# Harness Engineering Operator Shape

Read when: creating, migrating, auditing, or refactoring Harness Engineering
stage skills.

HE skills should stay stage-specific, compact, and executable. Keep the
always-loaded `SKILL.md` focused on routing, first action, stage workflow,
stop conditions, and concise output. Move bulky examples, gotchas, negative
prompts, scoring rubrics, and mode matrices into references or evals.

## Required Shape

Each active HE stage skill must carry this shape in `references/contract.yaml`:

- routing payload: domain, verbs, artifact, constraints
- immediate operator path: first read/tool/command and proceed rule
- source order: local `.harness`/repo truth, live tracker/PR state when needed,
  official docs/source/types, user confirmation for irreversible action
- tool resolution: preferred repo wrapper or HE script, safe fallback, and
  status/doctor command when tool state matters
- freshness/proof: cached reads may discover candidates, but live readback is
  required before writes, tracker changes, closure, or status changes
- boundaries: no tracker mutation, destructive action, credential access,
  external write, or closure claim without explicit authority and proof
- retry/stop: retry transient tool failures once when safe, then stop with the
  exact blocker, attempted fallback, and next safe action
- validation tiers: fast, standard, and deep; default to the smallest tier that
  proves the changed surface
- concise output: changed artifacts, important decisions, validation, residual
  risks, and next HE stage or blocker

## Required Regression Evals

Each active HE stage skill must include regression coverage for:

- happy operator path: stage starts from the first useful read/tool/command
- missing-input proceed rule: infer harmless details, ask only for blocking
  ownership, destructive behavior, tracker mutation, publication, or external
  writes
- no governance bloat: preserve useful constraints and gotchas in references,
  not as always-loaded bulk
- no stale/deferred active handle: active stage guidance must resolve to the
  canonical live plugin source, generated handle, or explicit overlay
- neighboring lane: adjacent tasks should route away from the stage

## Placement

Critical safety boundaries belong in `SKILL.md`. Situational constraints,
extended gotchas, examples, failure ladders, and rubrics belong in references.
Behavior that can regress belongs in eval cases. Machine-checkable drift belongs
in validators.
