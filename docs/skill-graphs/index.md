# Skill Graphs (Recursive Improvement)

This section defines the MVP contracts and operating workflows for the recursive skill self-improvement loop:

`generate -> evaluate -> diagnose -> improve -> re-score`

Execution model shorthand:

- **sequential**: strict phase pipeline (`generate -> evaluate -> diagnose -> improve -> re-score`)
- **router**: profile/objective-driven branching across specialist loops
- **orchestrator**: coordinator loop that executes and reconciles child loops

## Table of Contents

- [Schemas](/docs/skill-graphs/schemas/task-profile.schema.md)
- [Knowledge graph model](/docs/skill-graphs/knowledge-graph-operating-model.md)
- [Workflows](/docs/skill-graphs/workflows/promotion-gate.md)
- [Pilots](/docs/skill-graphs/pilots/ui-skills-shadow-results.md)
- [Runbooks](/docs/skill-graphs/runbooks/kill-switch-and-escalation.md)
- [Telemetry Outputs](/docs/skill-graphs/telemetry/daily-outputs.md)
- [Execution Guide](/docs/guides/recursive-skill-loop.md)

## Scope status

- **Historical pilot baseline:** Phases 1-3 + Phase 4 capture controls.
- **Current migration:** all-skills onboarding via wave model (`wave-0-controls -> wave-1-manual -> wave-2-co-pilot`).

## MVP Scope (Phases 1-3) + Phase 4 capture baseline

- Persist canonical top-level artifacts: `run`, `iteration_journal`, `promotion_decision`.
- Phase 4 capture baseline also writes `capture_record` + `evidence_packet` per run.
- Use checkpoint adversarial evaluation (initial, final, failure-triggered).
- Keep canonical promotion human-gated with provenance + security checklist.
- Runtime retrieval/injection is rollout-controlled (`off | observe_only | active`) with pilot-safe default `observe_only`.
- Treat `run/events.jsonl` as mandatory runtime telemetry; keep optional debug traces under `run/debug/*`.
- Enforce compatibility mapping for control blockers (`run_rollforward_blocked`, `run_rollback_required`) via `terminal_status` + `stop_reason` normalization.
- Keep `mode` vocabulary canonicalized to `autopilot | co-pilot | manual` with compatibility handling for `collaboration` in legacy artifacts.

## Pilot Profile Set (historical baseline)

1. `ui-ux-creative-coding`
2. `interface-craft`
3. `frontend-ui-design`
4. `react-ui-patterns`

## All-skills onboarding contract (current)

- In-scope skills: all active `SKILL.md` files except root/system/template exclusions.
- Required per-skill profile: `<skill>/references/task-profile.json`.
- Required SKILL binding: `knowledge_graph_profile: references/task-profile.json`.
- Readiness artifacts:
  - `artifacts/skill-graphs/onboarding/profile-index.json`
  - `artifacts/skill-graphs/onboarding/wave-readiness.json`

## Normative IDs

- Threshold registry IDs: `TR-01` .. `TR-06`
- Terminal status enum: `passed | failed | escalated | aborted`
- Stop reason enum: `pass | budget_exhausted | escalated | aborted | policy_failed | evaluator_conflict | dependency_missing`

- Back to [Docs index](/docs)
