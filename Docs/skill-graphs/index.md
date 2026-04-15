# Skill Graphs (Recursive Improvement)

This section defines the MVP contracts and operating workflows for the recursive skill self-improvement loop

`generate -> evaluate -> diagnose -> improve -> re-score`

Execution model shorthand:

- **sequential**: strict phase pipeline (`generate -> evaluate -> diagnose -> improve -> re-score`)
- **router**: profile/objective-driven branching across specialist loops
- **orchestrator**: coordinator loop that executes and reconciles child loops

## Table of Contents

- [Schemas](/docs/skill-graphs/schemas/task-profile.schema.md)
- [Skill lesson observation schema](/docs/skill-graphs/schemas/skill-lesson-observation.schema.md)
- [Knowledge graph model](/docs/skill-graphs/knowledge-graph-operating-model.md)
- [Question lifecycle contract](/docs/skill-graphs/question-lifecycle.md)
- [Workflows](/docs/skill-graphs/workflows/promotion-gate.md)
- [Skill learning loop](/docs/skill-graphs/workflows/skill-learning-loop.md)
- [Pilots](/docs/skill-graphs/pilots/ui-skills-shadow-results.md)
- [Runbooks](/docs/skill-graphs/runbooks/kill-switch-and-escalation.md)
- [Telemetry Outputs](/docs/skill-graphs/telemetry/daily-outputs.md)
- [Execution Guide](/docs/guides/recursive-skill-loop.md)

## Scope status

- **Historical pilot baseline:** Phases 1-3 + Phase 4 capture controls.
- **Current migration:** all-skills onboarding via wave model (`wave-0-controls -> wave-1-manual -> wave-2-co-pilot`).
- **Migration complete:** Canonical onboarding artifacts currently cover 112 active skills with valid profiles.

## LearningPosture (pilot contract)

The learning-preserving pilot adds one bounded, additive dimension:

- `LearningPosture` values are `learn | guided | execute`.
- `LearningPosture` is explicit and separate from `delegation.mode`.
- `delegation.mode` remains canonical `autopilot | co-pilot | manual`.
- For this pilot, `autopilot + learn` is disallowed and `autopilot + guided` is treated as degraded.
- `manual` and `co-pilot` may support `learn`, `guided`, and `execute`.

Canonical source of truth:

- Repository-level declaration: this document plus pilot profile metadata in `Infrastructure/references/task-profile.json`.
- Pilot conformance summary: `Infrastructure/artifacts/skill-graphs/pilot/learning-posture-pilot-conformance-summary.json`.

Authoring contract for pilot skills:

- `Infrastructure/references/task-profile.json` must include a `learning_posture` block with:
  - `supported`: list of allowed values (`learn`, `guided`, `execute`)
  - `default`: default posture for unscoped runs (`learn | guided | execute`)
- Validators treat missing `learning_posture` on pilot skills as a hard conformance failure.
- Pairing matrix is explicit and evaluated in repository-level checks (not at runtime in v1).

## Skill Genome Loop

- [Runbook](/docs/skill-graphs/runbooks/skill-genome-loop.md)
- [Telemetry Health](/docs/skill-graphs/telemetry/daily-skill-health.md)
- Controls: `Infrastructure/artifacts/skill-graphs/controls/`
- Candidates: `Infrastructure/artifacts/skill-graphs/telemetry/candidates.jsonl`

The Skill Genome Loop is a nightly batch process that:
1. Ingests run/session artifacts from the recursive skill loop
2. Computes routing confusion and outcome quality signals per skill
3. Emits high-confidence, human-gated draft PR candidates for skill-definition improvements

**Execution:**
- **Schedule:** Nightly at 4:00 AM UTC (cron)
- **Mode:** Controlled via `rollout-mode.txt` (`off | observe_only | active`)
- **Review:** Human gate via `review_candidates.py` before candidates are finalized

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
- Required per-skill profile: `<skill>/Infrastructure/references/task-profile.json`.
- Required SKILL binding: `knowledge_graph_profile: Infrastructure/references/task-profile.json`.
- Readiness artifacts:
  - `Infrastructure/artifacts/skill-graphs/onboarding/profile-index.json`
  - `Infrastructure/artifacts/skill-graphs/onboarding/wave-readiness.json`

## Normative IDs

- Threshold registry IDs: `TR-01` .. `TR-06`
- Terminal status enum: `passed | failed | escalated | aborted`
- Stop reason enum: `pass | budget_exhausted | escalated | aborted | policy_failed | evaluator_conflict | dependency_missing`

- Back to [Docs index](/docs)
