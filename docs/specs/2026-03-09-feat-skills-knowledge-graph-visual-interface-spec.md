---
title: Skills Knowledge Graph Visual Interface
type: feat
status: active
date: 2026-03-09
origin: docs/brainstorms/2026-02-24-skill-graph-live-auto-learning-brainstorm.md
risk: medium
spec_depth: lite
---

# Skills Knowledge Graph Visual Interface Spec

## Table of Contents
- [Enhancement Summary](#enhancement-summary)
- [Problem Statement](#problem-statement)
- [Goals](#goals)
- [Non-Goals](#non-goals)
- [System Boundary](#system-boundary)
- [Core Domain Model](#core-domain-model)
- [Main Flow / Lifecycle](#main-flow--lifecycle)
- [Interfaces and Dependencies](#interfaces-and-dependencies)
- [Invariants / Safety Requirements](#invariants--safety-requirements)
- [Failure Model and Recovery](#failure-model-and-recovery)
- [Observability](#observability)
- [Acceptance and Test Matrix](#acceptance-and-test-matrix)
- [Open Questions](#open-questions)
- [Definition of Done](#definition-of-done)

## Enhancement Summary

**Deepened on:** 2026-03-09  
**Key areas improved:** lifecycle state machine, failure/retry semantics, gate thresholds, observability and validation realism

- Added explicit UI state transitions with allowed/disallowed edges and control-precedence behavior.
- Added concrete retry, timeout, stale-lock, and degraded-mode recovery rules tied to existing runbooks.
- Added hard validation gates for `TR-01..TR-06`, event-envelope completeness, and fail-fast operational checks.
- Locked v1 ingestion to canonical pipeline-composed outputs (no direct raw-artifact reads).
- Closed v1 persona/export ambiguity with explicit defaults and a required decision-record artifact.

## Problem Statement
Current skill-graph reporting is generated as static operational artifacts (for example state-map HTML, onboarding readiness JSON, parity and telemetry files), but there is no explicit behavioral contract for an operator-facing visual interface that explains graph structure, readiness/risk state, and next actions in one consistent interaction model.

Without a spec-level contract, future UI work risks:
- breaking established data semantics (entity aliases, wave/readiness meaning, parity states),
- creating inconsistent failure handling versus control-file precedence,
- hiding observability signals required for safe rollout decisions.

## Goals
- Define a deterministic visual interface contract for skill knowledge graph navigation and operation review.
- Preserve canonical skill-graph semantics already defined by existing schemas, runbooks, and renderer inputs.
- Specify lifecycle behavior across load, filtering, node selection, refresh, and degraded-data scenarios.
- Encode failure handling and recovery rules aligned with existing control precedence (`kill-switch > rollback-required > rollout-mode`).
- Define observability and validation gates so `/prompts:workflow-plan` can produce implementation phases without inventing behavior.

## Non-Goals
- No implementation patching of `scripts/build_skill_state_map.py` or front-end code in this spec.
- No schema redesign of existing skill-graph contracts (`task-profile`, `evidence-packet`, event envelope).
- No expansion of rollout policy/governance thresholds beyond current runbook thresholds.
- No replacement of existing generated artifacts; the interface is a consumer of canonical outputs, not a new source of truth.

## System Boundary
Owned by this component:
- Visual rendering and interaction behavior for skill graph exploration and operations triage.
- Read-only aggregation of canonical artifacts into a unified UI state model.
- Explicit user actions for filtering, inspecting nodes/edges, and viewing blocker/recovery context.
- Accessibility behavior (focus order, keyboard traversal, reduced-motion parity) and interaction latency contract.

Not owned by this component:
- Generation of core artifacts (profile generation, parity manifests, candidate computation, shadow cycle orchestration).
- Promotion approval decisions and governance authorization.
- Control-file state mutation (kill switch, rollout mode, rollback required).
- Persistence and retention policy for telemetry artifacts.

## Core Domain Model
Primary entities:
- `SkillProfileNode`: identity + delegation + wave/readiness + scope slice (`core|extended|system`) from profile index and task profile.
- `RunNode`: run metadata and terminal state (`passed|failed|escalated|aborted`) with stop reason/blocker context.
- `IterationNode`: per-run iteration details from iteration journals.
- `CandidateLessonNode`: queued or proposed lessons with confidence/evidence metadata.
- `PromotionDecisionNode`: gate outcome (`pass|hold|insufficient_data|regressed` when present).
- `CanonicalLessonNode`: approved lesson lineage with supersession references.

Primary edges:
- `profile -> run`
- `run -> iteration`
- `iteration -> candidate_lesson`
- `candidate_lesson -> promotion_decision`
- `promotion_decision -> canonical_lesson`
- `canonical_lesson -> canonical_lesson` (supersedes)

Normalization rules:
- Alias joins are strict and ambiguity-safe; ambiguous aliases are excluded from automatic joins rather than guessed.
- Delegation mode normalizes to `autopilot|co-pilot|manual`; legacy `collaboration` is treated as compatibility input only.
- Parity and blocker values are treated as enums from existing contracts; unknown values are surfaced as `unknown` with warning state.

## Main Flow / Lifecycle
Lifecycle states:
- `S0_UNINITIALIZED`: initial state before artifact discovery.
- `S1_LOADING`: reading controls and required artifacts.
- `S2_READY`: fully materialized and interactive.
- `S3_DEGRADED`: partial data or contract violations; limited interaction.
- `S4_BLOCKED`: control-precedence lock (`kill-switch` or `rollback-required`) active.
- `S5_REFRESHING`: manual refresh in progress with prior snapshot retained.

Allowed transitions:
- `S0 -> S1`
- `S1 -> S2 | S3 | S4`
- `S2 -> S5 | S3 | S4`
- `S3 -> S5 | S2 | S4`
- `S5 -> S2 | S3 | S4`
- `S4 -> S1` only after controls clear

Disallowed transitions:
- Any direct transition to `S2` that bypasses `S1`.
- Any transition that exits `S4` without re-running control resolution.

Step contract:
1. Bootstrap (`S0 -> S1`)
- Load artifact pointers and verify required inputs are readable.
- Parse control files with fail-closed defaults: invalid/unknown values force safe lock behavior.

2. Materialization (`S1 -> S2|S3|S4`)
- Build canonical node set from profile inventory and system-slice policy.
- Attach run/parity/promotion/candidate telemetry via strict alias-safe joins.
- Emit composed UI state with explicit completeness flags and unmatched-join buckets.

3. Initial render (`S2` or `S3`)
- Present global status strip, graph/map view, run/compliance table, and learning/change view.
- Default to read-only degraded mode when mandatory event envelope requirements fail.

4. Interaction lifecycle (`S2` steady state)
- Filter by slice/wave/delegation/blocker.
- Select node to inspect details, linked runs, and recovery hints.
- Toggle scope density (`core` vs `full`) without mutating source artifacts.
- High-frequency actions must provide visible feedback in <=100ms perceived latency.

5. Refresh lifecycle (`S2|S3 -> S5 -> S2|S3|S4`)
- Manual refresh re-loads all source artifacts atomically for one consistent snapshot.
- Budget contract:
  - Global refresh deadline: `6000ms` wall-clock per refresh attempt.
  - Per-source soft timeout: `5000ms` on first attempt.
  - Retries (`250ms`, `500ms`) are allowed only for fast-fail transient errors and only while the global deadline budget remains.
- Preserve last-known-good snapshot on timeout or retry exhaustion.
- Staleness warning threshold: 30 minutes without successful refresh.

6. Reduced motion lifecycle (cross-state)
- Motion communicates focus/context only; when reduced motion is enabled, transitions become non-animated state changes with identical information content.

## Interfaces and Dependencies
Primary local contracts:
- `docs/skill-graphs/knowledge-graph-operating-model.md`
- `docs/skill-graphs/schemas/task-profile.schema.md`
- `docs/skill-graphs/schemas/evidence-packet.schema.md`
- `docs/skill-graphs/telemetry/daily-outputs.md`
- `docs/skill-graphs/runbooks/kill-switch-and-escalation.md`
- `docs/skill-graphs/runbooks/skill-genome-loop.md`

v1 UI input contract (authoritative):
- UI must consume only pipeline-composed outputs from `scripts/build_skill_state_map.py` adapters and canonical telemetry summaries.
- Raw artifact files are upstream/transitive dependencies and must not be independently parsed by UI code paths.

Primary upstream artifact dependencies (transitive via composed outputs):
- `artifacts/skill-graphs/onboarding/profile-index.json`
- `artifacts/skill-graphs/onboarding/wave-readiness.json`
- `artifacts/skill-graphs/pilot/shadow-dashboard.json`
- `artifacts/skill-graphs/pilot/artifact-parity-manifest.json`
- `artifacts/skill-graphs/telemetry/candidates.jsonl`
- `artifacts/skill-graphs/telemetry/promotion-queue.md`
- `artifacts/skill-graphs/telemetry/daily-skill-health.md`

Implementation anchor (existing pipeline):
- `scripts/build_skill_state_map.py` remains the authoritative state composition pipeline for input shape and join semantics.
- v1 ingestion contract: UI consumes canonical pipeline-composed outputs; direct raw artifact ingestion is out of scope.
- v1 decision artifact: `docs/decisions/2026-03-09-skills-graph-ui-v1-decisions.md` is required input for persona/export defaults.

## Invariants / Safety Requirements
- The interface must remain read-only against source artifacts and controls.
- Control precedence is fail-closed and never overridden by UI preference.
- Ambiguous identity joins must be dropped and surfaced, never silently resolved.
- A missing mandatory event envelope must produce degraded-warning status, not implicit success.
- Sensitive fields must remain redacted according to telemetry privacy rules.
- Interaction feedback for high-frequency actions must appear within 100ms perceived latency.
- Accessibility invariants: full keyboard parity, deterministic focus order, accessible names for all controls, and reduced-motion parity.
- Trust boundary invariant: user-entered filter/search text is treated as untrusted data and never interpreted as executable instructions.
- Input-budget invariant:
  - max filter/search payload size: `2048` bytes.
  - max filter/search requests: `30` requests per minute per operator session.
  - max concurrent refresh attempts per session: `1` (single-flight).
  - over-budget requests are rejected with `over_budget` diagnostics and no partial execution.
- Path-safety invariant: artifact reads are restricted to expected `docs/skill-graphs` and `artifacts/skill-graphs` sources after canonical path resolution.
- Path traversal/symlink invariant: `..` traversal and symlink-escape paths are rejected before read.
- Path read integrity invariant: reads are TOCTOU-resistant (final path component opened with no-follow semantics and post-open inode/device verification inside allowed roots).
- Refresh concurrency invariant: refresh uses single-flight dedupe while lock age is `<=60s`; only stale locks (`>60s`) are eligible for local release/retry.
- Rendering/logging invariant: untrusted artifact and user text must be context-encoded/escaped in UI and logs; raw HTML/script interpretation is disallowed.
- Redaction invariant:
  - UI and standard logs expose only repo-relative artifact identifiers.
  - absolute paths are disallowed in UI and standard logs.
  - absolute paths may appear only in restricted diagnostics exports for authorized operators.
- Hard-gate activation invariant:
  - source file: `artifacts/skill-graphs/controls/hard-gate-mode.txt`
  - allowed values: `auto|force_on|force_off`
  - default when missing/invalid: `auto`
  - `auto` semantics: `TR-04`/`TR-05` hard gate from Phase 3+, `TR-06` hard gate from Phase 4+.

## Failure Model and Recovery
Failure classes:
- Artifact missing/unreadable.
- Artifact malformed/schema-incompatible.
- Join ambiguity or orphaned references.
- Control state conflict (for example active mode blocked by rollback requirement).
- Stale snapshot or partial refresh.

Recovery behavior:
- Missing mandatory artifact class: keep last-known-good data, mark section as degraded, show repo-relative missing path identifier.
- Malformed payload: isolate failed data source, keep unaffected panels functional, emit parse error summary.
- Join ambiguity: suppress ambiguous mappings, place impacted rows in an explicit `unmatched` bucket.
- Control conflict: lock actionable affordances and show blocker code plus runbook link target.
- Refresh failure: preserve current render and expose retry control with timestamped failure reason.
- Cold start without last-known-good snapshot: enter `S3_DEGRADED`, show `cold_start_no_snapshot`, and allow only `retry`, `open runbook`, and `download diagnostics`.
- Missing `events.jsonl` or missing `run_state_changed`: treat as hard envelope-contract failure and force `S3_DEGRADED`; wave promotion remains blocked until resolved.
- Blocked control path without `run_blocked` + non-null `blocker_code`: treat as contract violation and surface `telemetry_integrity_failed`.
- Stale/replayed snapshot evidence: fail to `S3_DEGRADED` when freshness checks fail (non-monotonic timestamp/run-id, stale beyond threshold, or mismatched source identity where available).
- Envelope escalation path: if envelope errors breach release escalation threshold (`>=3` consecutive runs or `>=10` errors in a 24h window), set `rollback-required` and re-evaluate controls to enter `S4_BLOCKED`.

Retry/timeout policy:
- Retryable: transient read errors and stale snapshot conditions.
- Non-retryable until operator action: kill-switch active, rollback-required active, invalid control file contents, schema-version incompatibility.
- Retry schedule: up to 2 retry attempts with exponential backoff (`250ms`, `500ms`) during a single refresh, but only for fast-fail transient errors and only inside the `6000ms` global refresh deadline.
- Timeout handling: full-timeout (`5000ms`) source attempts are terminal for that source in the current refresh attempt (no additional timeout retries).
- Stale-lock handling:
  - lock age `<=60s`: dedupe to active refresh attempt (no new refresh start).
  - lock age `>60s`: mark stale, release locally, and re-attempt once.

Abort vs retry:
- Abort to `S4_BLOCKED` when kill-switch or rollback-required controls are active.
- Remain in `S3_DEGRADED` for envelope/schema failures until corrected upstream, unless envelope escalation threshold is met.
- Combined-failure precedence: when control blockers and envelope failures co-occur, `S4_BLOCKED` is primary state for action gating and `S3_DEGRADED` diagnostics remain visible as secondary context.

## Observability
Required UI-visible telemetry:
- Data snapshot timestamp and source artifact version markers.
- Control state banner including active blocker code when present.
- Completeness indicators per evidence class (`events|logs|traces|session_signals|checks`).
- Run-level status distribution and blocker distribution.
- Capture coverage, confidence bucket counts, injection usage, suppression counts.
- Gate threshold panel for `TR-01..TR-06` with current value, target, and pass/fail state.
- Explicit HOLD reason list derived from gate failures (for example critical non-regression <100%, budget <95%).

Required logs/metrics for interface runtime:
- `ui_snapshot_loaded` (counts of loaded/missing sources, latency).
- `ui_join_ambiguity_detected` (alias key, affected rows count).
- `ui_degraded_mode_entered` and `ui_degraded_mode_cleared`.
- `ui_interaction_latency_ms` for select/filter/toggle events.
- `refresh_end_to_end_ms` measured from `refresh_requested` to `state_committed`.
- `ui_accessibility_mode` (`reduced_motion_on|off`) to validate parity coverage.
- `ui_control_precedence_evaluated` with final resolved state (`blocked|degraded|ready`) and reason.
- `ui_event_envelope_contract_failed` with failing rule (`missing_events`, `missing_run_state_changed`, `missing_run_blocked_code`).

Metric semantics:
- `ui_interaction_latency_ms` is measured from `interaction_start` to `next_paint_complete`.
- `ui_interaction_latency_ms` dimensions: `action_type`, `fixture_size`, `device_class`, `reduced_motion`.
- `refresh_end_to_end_ms` dimensions: `fixture_size`, `device_class`, `refresh_result` (`success|fallback|blocked`).
- Lab validation guard: `lab_min_samples=500` per high-frequency action type.
- Runtime alert guard: `runtime_min_samples=200` per action class in the evaluation window.
- Alert windows requiring percentile checks that miss runtime guard must emit `insufficient_data` and carry evaluation to the 24h window.

Operational SLO windows:
- 7-day window for `TR-01`, `TR-02`, `TR-03`, `TR-04`.
- 14-day window for `TR-05`, `TR-06`.

## Acceptance and Test Matrix
Contract and data correctness:
- Verify entity and edge mapping fidelity against existing operating model.
- Verify alias-collision behavior results in explicit unmatched output, not incorrect joins.
- Verify enum normalization for delegation and terminal statuses.
- Verify blocker mapping compatibility:
  - `run_rollforward_blocked -> failed/policy_failed`
  - `run_rollback_required -> failed/dependency_missing`
  - `kill_switch_activated -> aborted/aborted`
  - `run_aborted` (legacy alias) -> `kill_switch_activated` normalization before terminal mapping

Failure and recovery:
- Simulate missing `events.jsonl`/parity/candidate inputs and confirm degraded render behavior.
- Simulate malformed JSON and confirm isolation to affected panel.
- Simulate control conflicts and confirm fail-closed action gating.
- Simulate missing `run_state_changed` and validate hard envelope-contract failure path.
- Simulate blocked path without `blocker_code` and validate integrity-failure state.
- Simulate stale refresh lock and validate stale-lock recovery path.

Accessibility and interaction:
- Keyboard-only traversal across all primary panes and node detail actions.
- Screen reader labels/roles on graph nodes, filters, and state banners.
- Reduced-motion parity test for all animated transitions.
- Contrast and focus-visible checks across default/active/error/degraded states.
- Verify safe read-only interactions remain available for unaffected panels in `S3_DEGRADED`.

Performance and responsiveness:
- High-frequency selection/filter feedback under 100ms perceived latency.
- High-frequency selection/filter/toggle feedback must meet p95 `<=100ms` and p99 `<=150ms` with lab/runtime sample guards.
- No large layout shift during refresh or panel state transitions.
- Large-inventory render test (all active skills) with acceptable interaction responsiveness.
- Refresh lifecycle p95 remains within global end-to-end budget with parallel source fan-out.

Operational validation:
- Cross-check rendered metrics against `daily-skill-health.md` and `promotion-queue.md`.
- Validate blocker state consistency with rollback drill expectations and control hierarchy.
- Validate gate threshold rendering against schema targets:
  - `TR-01`: stability consecutive passes `>=1` (MVP)
  - `TR-02`: critical non-regression `=100%`
  - `TR-03`: budget compliance `>=95%`
  - `TR-04`: evaluator consistency flip rate `<=3%` (advisory MVP, hard Phase 3+)
  - `TR-05`: judge calibration agreement `>=80%` (advisory MVP, hard Phase 3+)
  - `TR-06`: promotion precision `>=70%` (hard Phase 4+)
- Validate wave-promotion eligibility gate: event envelope errors must equal `0`.
- Validate redaction enforcement and output encoding for telemetry/user-provided content.
- Validate path canonicalization, symlink-escape rejection, and traversal rejection.
- Validate refresh exits for all branches (`S5 -> S2|S3|S4`) with atomic snapshot consistency.

Validation command set (spec verification hygiene):
- `bash scripts/sync_skills.sh`
- `python3 scripts/docs_lint.py --mode block --config docs-policy.json`
- `bash ~/.codex/scripts/verify-work.sh`

## Open Questions
- No blocking open questions for v1.
- v1 defaults are frozen as:
  - persona priority: `operator-first`.
  - graph-adapter export views (`typed-graph.json`, notes): deferred from v1.
- Decision record requirement: `docs/decisions/2026-03-09-skills-graph-ui-v1-decisions.md` must exist before implementation start; if absent, these defaults remain mandatory (fail closed).

## Definition of Done
- A reviewed spec exists at this path with all required contract sections completed.
- System boundary and ownership are explicit enough that implementation planning requires no behavior invention.
- Failure/recovery and observability rules are explicit and aligned with existing runbooks and telemetry contracts.
- Acceptance matrix is detailed enough for `/prompts:workflow-plan` to decompose into implementation/test phases.
- Enhancement summary is present and dated.
