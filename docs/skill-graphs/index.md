# Skill Graphs (Recursive Improvement)

This section defines the MVP contracts and operating workflows for the recursive skill self-improvement loop:

`generate -> evaluate -> diagnose -> improve -> re-score`

## Table of Contents

- [Schemas](/docs/skill-graphs/schemas/task-profile.schema.md)
- [Workflows](/docs/skill-graphs/workflows/promotion-gate.md)
- [Pilots](/docs/skill-graphs/pilots/ui-skills-shadow-results.md)
- [Runbooks](/docs/skill-graphs/runbooks/kill-switch-and-escalation.md)
- [Telemetry Outputs](/docs/skill-graphs/telemetry/daily-outputs.md)
- [Execution Guide](/docs/guides/recursive-skill-loop.md)

## MVP Scope (Phases 1-3)

- Persist only three canonical top-level artifacts: `run`, `iteration_journal`, `promotion_decision`.
- Use checkpoint adversarial evaluation (initial, final, failure-triggered).
- Keep canonical promotion human-gated with provenance + security checklist.
- Keep runtime retrieval injection disabled until Phase 4.
- Treat optional runtime traces as debug output only (`run/debug/*`) and keep them gitignored.

## Pilot Profile Set (fixed)

1. `ui-ux-creative-coding`
2. `interface-craft`
3. `frontend-ui-design`
4. `react-ui-patterns`

## Normative IDs

- Threshold registry IDs: `TR-01` .. `TR-06`
- Terminal status enum: `passed | failed | escalated | aborted`
- Stop reason enum: `pass | budget_exhausted | escalated | aborted | policy_failed | evaluator_conflict | dependency_missing`

- Back to [Docs index](/docs)
