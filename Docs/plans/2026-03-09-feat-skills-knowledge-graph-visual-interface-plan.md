---
plan_id: ASK-SKILLS-KG-VISUAL-20260309
title: feat: Skills Knowledge Graph Visual Interface Delivery Plan
type: feat
status: active
date: 2026-03-09
origin: docs/brainstorms/2026-02-24-skill-graph-live-auto-learning-brainstorm.md
spec: Docs/specs/2026-03-09-feat-skills-knowledge-graph-visual-interface-spec.md
deepened: 2026-03-09
research_agents: 3
---

# feat: Skills Knowledge Graph Visual Interface Delivery Plan

## Enhancement Summary

**Deepened on:** 2026-03-09
**Key areas improved:** decision-closure gates, lifecycle transition rigor, recovery constants, observability coverage, rollout decision protocol

- Added an explicit pre-implementation decision-closure gate so unresolved spec questions are frozen before coding begins.
- Pinned refresh/retry/stale-lock/staleness values to spec constants to prevent implementation drift.
- Expanded validation coverage for disallowed transitions, envelope integrity variants, path-safety invariants, and partial degradation behavior.
- Locked service-local diagnostics authorization, atomic control-write command path, and strict refresh hard-cap enforcement.
- Tightened task dependencies so gate/HOLD rendering and rollout handoff require upstream state/evidence completeness.
- Removed rollout-state and ownership ambiguities by tightening phase gates, owner map consistency, and rollback execution contracts.

## Table of Contents
- [Enhancement Summary](#enhancement-summary)
- [Overview](#overview)
- [Origin Traceability](#origin-traceability)
- [Problem Statement / Motivation](#problem-statement--motivation)
- [Scope and Non-Goals](#scope-and-non-goals)
- [Implementation Phases](#implementation-phases)
- [Task Graph (id / depends_on)](#task-graph-id--depends_on)
- [Planned File Map](#planned-file-map)
- [Dependencies and Risks](#dependencies-and-risks)
- [Evidence Paths and Gate Commands](#evidence-paths-and-gate-commands)
- [Test and Validation Strategy](#test-and-validation-strategy)
- [Rollout / Migration / Monitoring](#rollout--migration--monitoring)
- [Acceptance Checklist](#acceptance-checklist)
- [Sources & References](#sources--references)

## Overview
Implement the skills knowledge graph visual interface as a safe, read-only operational surface that consumes existing canonical artifacts and preserves the state, control, and telemetry contracts defined in the spec.

Plan posture:
- Spec-first and contract-preserving.
- Safety gates before UI interactivity.
- Deterministic joins, deterministic status model, and auditable validation.

## Origin Traceability
Mapped from `docs/brainstorms/2026-02-24-skill-graph-live-auto-learning-brainstorm.md` to this plan/spec contract:
- Post-run capture and lesson visibility:
  - surfaced through run/compliance + learning/change views and capture-coverage telemetry.
- Start-of-run lesson injection traceability:
  - surfaced in observability panels and validation cross-checks against promotion/queue artifacts.
- Kill-switch-first safety posture:
  - preserved through fail-closed control precedence and rollout rollback matrices.

## Problem Statement / Motivation
The repository has strong skill-graph artifacts and scripts, but there is no implementation plan sequencing how to deliver a visual interface without violating:
- control precedence (`kill-switch > rollback-required > rollout-mode`),
- mandatory event envelope requirements (`events.jsonl`, `run_state_changed`, blocked-path `run_blocked + blocker_code`),
- gate semantics (`TR-01..TR-06`) and HOLD/no-go behavior.

This plan defines implementation order, dependencies, and validation gates so delivery can proceed safely without inventing new system behavior.

## Scope and Non-Goals
In scope:
- Implement interface delivery in phases aligned with spec lifecycle states (`S0..S5`).
- Reuse `Infrastructure/scripts/lifecycle-and-sync/build_skill_state_map.py` pipeline contracts and canonical artifacts.
- Implement deterministic status resolution for `READY`, `DEGRADED`, and `BLOCKED`.
- Implement observability and validation checks required by spec and runbooks.
- Add rollout gates and downgrade behavior aligned with existing threshold/runbook contracts.

Non-goals:
- Changing schema semantics in `docs/skill-graphs/schemas/*`.
- Mutating rollout controls from the UI (UI remains read-only for control files).
- Replacing existing telemetry generation pipelines.
- Redefining TR thresholds or promotion governance policy.

## Implementation Phases
### Phase 0: Contract Preflight and Baseline
Objective: establish authoritative inputs, fixtures, and validation harness before feature work.

Work:
- Lock source-of-truth references from spec and runbooks.
- Build plan fixture set for normal, degraded, and blocked snapshots.
- Write and approve the v1 decision record at `docs/decisions/2026-03-09-skills-graph-ui-v1-decisions.md` (persona priority and export-tab scope).
- Freeze v1 ingestion to pipeline-composed inputs only (no direct raw artifact ingestion).
- Freeze unresolved defaults before implementation:
  - service-local diagnostics authz contract (`viewer|operator|release-owner`) is mandatory.
  - rollback control updates must use one canonical atomic control-write command path.
  - refresh SLO hard cap is strict (`p95<=6000ms`, `p99<=6000ms`).
- Capture precedence reconciliation notes where existing runtime checks differ in order (`kill-switch`, `rollback-required`, `rollout-mode`).
- Confirm linked spec frontmatter is `status: active` before implementation sequencing starts.
- Resolve and record named DRIs + backups for each gate owner role in the release checklist artifact.
- Verify docs/plan lint path and contract-check scripts are runnable.

Exit criteria:
- Baseline fixture bundle exists for all core state classes.
- Decision record exists at the required path with owner and approval timestamp; if missing, Phase 1 is blocked (fail closed).
- Linked spec is `status: active`; otherwise plan remains HOLD.
- Named DRIs and backup owners are captured in release checklist artifact; placeholders are not allowed.
- Validation commands are executable and documented.

### Phase 1: Safety Gate Foundation (Must Complete Before Interactivity)
Objective: enforce control precedence and event-envelope integrity first.

Work:
- Implement control resolution module with fail-closed behavior.
- Implement envelope integrity checks for mandatory events/fields.
- Implement transition guards for disallowed lifecycle edges (`* -> S2` without `S1`, and `S4` exit without control re-evaluation).
- Implement deterministic state resolution precedence:
  - `BLOCKED` wins for action availability.
  - `DEGRADED` remains visible as secondary diagnostics.

Exit criteria:
- No mutating/actionable affordances are enabled until control + envelope checks pass; in `S3_DEGRADED`, safe read-only interactions remain available for unaffected panels.
- Combined failure scenarios (control+envelope) return deterministic status and remediation.
- Transition-negative tests pass and are required in CI gates.

### Phase 2: Data Materialization and Join Integrity
Objective: build deterministic composed view state from canonical artifacts.

Work:
- Reuse canonical input paths/defaults from `build_skill_state_map` contract.
- Implement strict alias-safe joins and explicit `unmatched` bucket behavior.
- Implement snapshot composition with completeness indicators.
- Constrain composition to adapter/wrapper reuse of canonical pipeline outputs; do not duplicate join/normalization semantics.
- Enforce canonical daily-health path contract and reject path-divergent source mixes.

Exit criteria:
- Materialization output is deterministic across repeated runs on unchanged inputs.
- Ambiguous joins never auto-resolve and are operator-visible.
- Source completeness and `unmatched` diagnostics are visible per panel.
- Adapter parity checks against canonical pipeline outputs pass.

### Phase 3: Interface Behavior and Accessibility
Objective: deliver interface flows for graph/list/detail with spec-required UX constraints.

Work:
- Implement `S2_READY`, `S3_DEGRADED`, `S4_BLOCKED`, `S5_REFRESHING` interaction model.
- Implement refresh, retry, timeout, and stale-lock recovery behavior using spec constants:
  - `6000ms` global refresh deadline,
  - `5s` soft timeout per source class (first attempt),
  - retry backoff `250ms` then `500ms`,
  - stale-lock threshold `60s`,
  - staleness warning threshold `30m`.
- Implement single-flight refresh semantics for lock age `<=60s` and stale-lock local release only when lock age `>60s`.
- Implement keyboard/focus/labels and reduced-motion parity for all primary interactions.

Exit criteria:
- Interaction latency and state transitions satisfy explicit SLO thresholds and spec acceptance checks.
- Accessibility and reduced-motion tests pass for critical flows.
- Recovery constants are asserted in automated tests.
- `refresh_end_to_end_ms` budgets pass with parallel fan-out and capped retry envelope.

### Phase 4: Gate Panels, HOLD Reasoning, and Observability
Objective: expose operational truth and diagnostics needed for safe decision-making.

Work:
- Implement TR gate panel rendering (`TR-01..TR-06`) with class semantics (blocking/advisory).
- Implement explicit HOLD reasons with evidence references.
- Render completeness indicators for `events|logs|traces|session_signals|checks`.
- Render snapshot version markers and source-version stamps in UI-visible diagnostics.
- Render capture coverage, confidence bucket counts, injection usage, and suppression counts in the observability surface.
- Surface envelope-failure rule identifiers (`missing_events`, `missing_run_state_changed`, `missing_run_blocked_code`).
- Emit runtime telemetry for snapshot load, precedence evaluation, contract failures, and interaction latency.

Exit criteria:
- Gate panel values match schema/runbook contracts.
- HOLD/no-go reasoning is explicit and auditable in UI outputs and logs.
- UI telemetry surface matches spec observability requirements exactly, including version markers and learning telemetry counts.

### Phase 5: Rollout, Validation, and Operational Handoff
Objective: release behind safe gating with deterministic rollback posture.

Work:
- Run combined-failure and regression suites (including historical missing-events scenario).
- Validate forced-downgrade behavior under trigger conditions.
- Produce rollout checklist, evidence bundle, and operator runbook handoff notes.
- Validate rollback drill recency gate before rollout approval.

Exit criteria:
- Validation suite passes with evidence.
- Rollout gate decision and fallback behavior documented.
- Handoff includes owner-mapped go/no-go decision table and rollback triggers.
- Rollback execution matrix and post-rollback verification checklist are complete and tested.

## Task Graph (id / depends_on)
```yaml
tasks:
  - id: P0A
    title: Freeze v1 decision record and implementation assumptions
    depends_on: []
  - id: P0
    title: Build planning fixture pack for ready/degraded/blocked snapshots
    depends_on: [P0A]
  - id: P1
    title: Implement control precedence resolver (fail-closed)
    depends_on: [P0A]
  - id: P2
    title: Implement mandatory event-envelope validator
    depends_on: [P0A]
  - id: P3
    title: Implement deterministic state resolution (blocked vs degraded precedence)
    depends_on: [P1, P2]
  - id: P4
    title: Implement canonical artifact materialization pipeline
    depends_on: [P0]
  - id: P5
    title: Implement alias-safe join and unmatched bucket behavior
    depends_on: [P4]
  - id: P6
    title: Implement refresh/timeout/retry/stale-lock lifecycle handling
    depends_on: [P3, P4]
  - id: P7
    title: Implement interface interactions and accessibility/reduced-motion parity
    depends_on: [P3, P5, P6]
  - id: P8
    title: Implement TR gate panel and HOLD reason synthesis
    depends_on: [P3, P4, P5]
  - id: P9
    title: Instrument observability events and latency metrics
    depends_on: [P3, P7, P8]
  - id: P10
    title: Add combined-failure acceptance tests and regression fixtures
    depends_on: [P3, P6, P8, P9]
  - id: P11
    title: Execute rollout validation and produce handoff checklist
    depends_on: [P9, P10]
```

## Planned File Map
- `Infrastructure/scripts/lifecycle-and-sync/build_skill_state_map.py`:
  - Treat as authoritative composition source for controls, joins, and typed-graph outputs.
  - No semantic rewrite of join/normalization behavior in UI adapter code.
- `Infrastructure/scripts/skill-graph/verify_recursive_skill_graph_artifacts.py`:
  - Reuse as rollout evidence source for blocked-path and envelope integrity checks.
- `Skills/skill-builder/Infrastructure/scripts/build_recursive_skill_shadow_report.py`:
  - Reuse envelope error computation to drive degraded-mode fixtures and assertions.
- `docs/skill-graphs/schemas/gate-contract.schema.md`:
  - Keep TR threshold and event enum rendering aligned to this contract.
- `docs/skill-graphs/telemetry/daily-outputs.md`:
  - Treat as mandatory envelope behavior reference (`events.jsonl`, `run_state_changed`, `run_blocked + blocker_code`).
- `docs/skill-graphs/knowledge-graph-operating-model.md`:
  - Treat as canonical domain model reference for node/edge semantics and graph/table parity.
- `docs/skill-graphs/schemas/task-profile.schema.md`:
  - Treat as canonical profile shape and enum source for model normalization.
- `docs/skill-graphs/schemas/evidence-packet.schema.md`:
  - Treat as canonical evidence structure for observability completeness checks.
- `docs/skill-graphs/runbooks/kill-switch-and-escalation.md`:
  - Treat as normative precedence source for blocker resolution.
- `docs/skill-graphs/runbooks/skill-genome-loop.md`:
  - Treat as operational rollback reference; execution must use canonical atomic writer path.
- `Infrastructure/scripts/write_skill_graph_controls_atomic.py`:
  - Planned canonical control-write command for rollback/clear/re-entry operations.
  - Enforce preflight (`controls path exists/writable`, owner/mode checks), atomic write semantics (`temp -> fsync -> rename`), and post-write tuple verification.
- `Infrastructure/artifacts/skill-graphs/controls/hard-gate-mode.txt`:
  - Canonical hard-gate activation source (`auto|force_on|force_off`, default `auto`).

## Dependencies and Risks
Dependencies:
- Spec contract: `Docs/specs/2026-03-09-feat-skills-knowledge-graph-visual-interface-spec.md`.
- Canonical sources: `docs/skill-graphs/*` schemas/runbooks and `Infrastructure/artifacts/skill-graphs/*`.
- Existing composition pipeline: `Infrastructure/scripts/lifecycle-and-sync/build_skill_state_map.py`.
- Validation scripts: `Infrastructure/scripts/validation-and-linting/docs_lint.py`, `Infrastructure/scripts/validate_all.sh`, and graph/contract validators.

Risks and mitigations:
- Risk: interactive UI ships before safety gates.
  - Mitigation: Phase 1 is hard precondition for any interactive routes.
- Risk: ambiguous status when control blockers and envelope failures co-occur.
  - Mitigation: deterministic state precedence with explicit action suppression rules.
- Risk: join drift from alias ambiguity.
  - Mitigation: strict alias-safe matching and explicit unmatched accounting.
- Risk: refresh race/lock deadlock.
  - Mitigation: stale-lock recovery, bounded retry, controlled failure path.
- Risk: gate panel drift from schema.
  - Mitigation: bind rendering to `gate-contract.schema.md` enums/threshold refs.
- Risk: precedence-order drift between existing runtime scripts and new interface behavior.
  - Mitigation: Phase 0 precedence reconciliation note + Phase 1 canonical precedence tests.
- Risk: hidden safety regressions from untrusted filter/search or unexpected artifact paths.
  - Mitigation: explicit safety tests for untrusted input handling and path allowlisting.
- Risk: canonical path bypass through symlinks or traversal sequences.
  - Mitigation: canonical path (`realpath`) enforcement, symlink-escape rejection, traversal negative tests, and TOCTOU-resistant read checks.
- Risk: leaking absolute filesystem paths through degraded diagnostics.
  - Mitigation: emit repo-relative identifiers in UI/standard logs; restrict absolute paths to authorized diagnostics exports only.
- Risk: unauthorized diagnostics export access or missing authorization checks.
  - Mitigation: service-local RBAC contract with deny-by-default behavior and audited export events.
- Risk: stale/replayed telemetry snapshots misrepresent operational truth.
  - Mitigation: freshness invariants (monotonic timestamp/run-id and source hash when available) with fail-to-degraded behavior.
- Risk: partial control writes leave contradictory rollout state.
  - Mitigation: single canonical atomic control writer with preflight and post-write tuple assertions.
- Risk: missing institutional `docs/solutions` history for this topic.
  - Mitigation: treat runbooks/spec/scripts as authoritative now and add a post-implementation `docs/solutions` entry.

## Evidence Paths and Gate Commands
Phase-gate evidence paths (required):
- Phase 0 decision record: `docs/decisions/2026-03-09-skills-graph-ui-v1-decisions.md`
- Phase 0 fixture baseline: `Infrastructure/artifacts/skill-graphs/telemetry/ui-plan-fixtures/2026-03-09-baseline.json`
- Phase 0-4 staging evidence directory: `Infrastructure/artifacts/skill-graphs/telemetry/staging/<YYYYMMDDTHHMMSSZ>/`
- Phase 5 rollout decision log: `Infrastructure/artifacts/skill-graphs/telemetry/releases/<YYYYMMDDTHHMMSSZ>/rollout-decision-log.md`
- Phase 5 telemetry thresholds: `Infrastructure/artifacts/skill-graphs/telemetry/releases/<YYYYMMDDTHHMMSSZ>/telemetry-thresholds.json`
- Phase 5 verification manifest: `Infrastructure/artifacts/skill-graphs/telemetry/releases/<YYYYMMDDTHHMMSSZ>/manifest.json`
- Phase 5 sealed evidence source: copy/verify from staging directory to immutable release directory before go/no-go.

Phase-gate command matrix:
- `Phase 0 -> Phase 1`:
  - `python3 Infrastructure/scripts/validation-and-linting/docs_lint.py --mode block --config Infrastructure/docs-policy.json`
  - `python3 ~/.codex/Infrastructure/scripts/plan-graph-lint.py /Users/jamiecraik/dev/Agent-Skills/Docs/plans/2026-03-09-feat-skills-knowledge-graph-visual-interface-plan.md`
  - artifact gate: decision record and fixture baseline both present.
- `Phase 1 -> Phase 2`:
  - run control/envelope transition test suites with CI-required status.
  - artifact gate: transition-negative test report committed to staging evidence directory.
- `Phase 2 -> Phase 3`:
  - run adapter parity and deterministic join suite.
  - artifact gate: parity output report and `TR-04`/`TR-05` evidence per hard-gate activation contract.
- `Phase 3 -> Phase 4`:
  - run accessibility, reduced-motion, and performance SLO suites.
  - artifact gate: `ui_interaction_latency_ms`, `ui_interaction_complete_ms`, and `refresh_end_to_end_ms` reports with sample-volume metadata.
- `Phase 4 -> Phase 5`:
  - verify gate panel parity and observability threshold checks.
  - artifact gate: gate panel snapshot + threshold evaluation report.
- `Phase 5 -> completion`:
  - `python3 Infrastructure/scripts/skill-graph/verify_recursive_skill_graph_artifacts.py --run-state-check --strict --manifest Infrastructure/artifacts/skill-graphs/telemetry/releases/<YYYYMMDDTHHMMSSZ>/manifest.json`
  - artifact gate: complete evidence bundle with hash-valid `manifest.json`.

## Test and Validation Strategy
Unit/contract tests:
- Control resolution and fail-closed behavior.
- Event-envelope validation rules and blocker code requirements.
- State resolution precedence (`BLOCKED` vs `DEGRADED`).
- Alias ambiguity handling and deterministic unmatched counts.
- Disallowed transition guards (`* -> S2` without `S1`, `S4 -> S2` without re-evaluating controls).
- Unknown enum normalization to warning-visible `unknown` states.
- Canonical path safety checks (`realpath` root allowlist, `..` traversal rejection, symlink escape rejection).
- Output encoding and log-sanitization checks for untrusted artifact/user-provided text.
- Redaction contract assertions for telemetry-sensitive fields.
- Snapshot freshness and anti-replay checks (monotonic run/timestamp, stale payload downgrade behavior).
- Service-local RBAC checks for diagnostics export and control re-check actions (deny-by-default on missing/unknown role).

Integration tests:
- End-to-end lifecycle transitions (`S0 -> S1 -> S2/S3/S4 -> S5 -> S2/S3/S4`).
- Combined-failure scenarios:
  - control blocker + missing envelope event,
  - stale lock + timeout + retry exhaustion,
  - control clear while `S4_BLOCKED` forcing `S4 -> S1 -> S2/S3` re-evaluation,
  - missing `run_state_changed` envelope event,
  - blocked path with missing `blocker_code`,
  - advisory gate fail with hard gate pass,
  - partial artifact corruption + join ambiguity.
- Cold-start failure scenario with no last-known-good snapshot (`cold_start_no_snapshot`) with explicit action whitelist (`retry`, `open runbook`, role-authorized `download diagnostics`) and all other actions blocked.
- Partial degradation behavior where unaffected panels remain usable.
- Atomic refresh behavior where snapshot state is single-version consistent or fully falls back to last-known-good.
- Non-retryable operator-action scenarios (`invalid_control_contents`, `schema_version_incompatible`) verify no retry loop and explicit operator remediation path.
- Concurrent refresh behavior:
  - repeated refresh triggers while lock age `<=60s` must dedupe to a single active attempt per `(operator_session_id, interface_instance_id)` lock scope.
  - stale lock (`>60s`) release and one re-attempt path must be deterministic.

Accessibility/performance tests:
- Keyboard-only traversal and screen reader label coverage.
- Reduced-motion parity for all animated transitions.
- Interaction feedback latency SLO checks for high-frequency actions:
  - metric semantics: `ui_interaction_latency_ms` measured from `interaction_start` to `next_paint_complete`.
  - completion metric: `ui_interaction_complete_ms` measured from `interaction_start` to `state_committed`.
  - required dimensions: `action_type`, `fixture_size`, `device_class`, `reduced_motion`.
  - `select/filter/toggle` p95 `<=100ms`, p99 `<=150ms`.
  - completion SLO: `ui_interaction_complete_ms` p95 `<=150ms`, p99 `<=250ms`.
  - lab sample guard: `lab_min_samples=500` per action type on full-inventory fixtures.
- Recovery timing assertions for refresh constants (`5s`, `250ms`, `500ms`, `60s`, `30m`).
- Refresh SLO checks:
  - `refresh_end_to_end_ms` p95 `<=6000ms`.
  - `refresh_end_to_end_ms` p99 `<=6000ms`.
  - metric semantics: measured from `refresh_requested` to `state_committed` with dimensions `fixture_size`, `device_class`, `refresh_result`.
  - source loads execute in parallel fan-out (not serial).
  - retries remain inside one global refresh-attempt budget.
- Scale checks:
  - baseline fixture uses current full inventory (`114` active skills at time of plan deepening).
  - stress fixtures at `2x` and `5x` synthesized node counts with proportional edge fan-out expansion.
  - stress history-depth fixtures at `2x` and `5x` run-history depth.
  - stress artifact-size fixtures at `2x` and `5x` file size envelopes.
  - repeated refresh loop memory ceiling enforced with numeric gates:
    - baseline fixture (`1x`): peak RSS `<=400MB`.
    - stress fixture (`2x`): peak RSS `<=650MB`.
    - stress fixture (`5x`): peak RSS `<=1200MB`.
    - leak guard: peak RSS growth after 20 refresh loops `<=8%` versus loop-1 baseline for each fixture tier.

Safety tests:
- Untrusted filter/search input is never executed as instructions.
- Input budget and throttling checks:
  - payload sizes at `2047`, `2048`, `2049` bytes.
  - request rate at threshold and threshold+1 for `30 req/min/session`.
  - rejected requests emit `over_budget` diagnostics and perform no partial execution.
- Artifact reads outside canonical pipeline-composed outputs under `Infrastructure/artifacts/skill-graphs/**` are rejected and logged.
- Symlink and traversal payloads cannot escape allowed roots.
- TOCTOU-resistant path-read checks validate no symlink-swap escape between check/open and verify post-open inode/device constraints.
- Rendered diagnostics and logs escape/sanitize untrusted payload strings (XSS/log injection payload suite).
- Path exposure checks ensure UI and standard logs render only repo-relative identifiers; absolute paths allowed only in restricted diagnostics export.
- Diagnostics export authorization tests validate role gating, deny-by-default behavior, redacted denial payloads, and audit event emission.
- Runbook target tests verify immutable allowlisted runbook IDs and rejection of `javascript:`, `file://`, traversal, and external URL payloads.
- Observability field parity golden tests verify presence of source version markers and learning telemetry counts.

Validation commands:
Authoring checks:
- `bash Infrastructure/scripts/lifecycle-and-sync/sync_skills.sh`
- `python3 Infrastructure/scripts/validation-and-linting/docs_lint.py --mode warn --config Infrastructure/docs-policy.json`
- `vale Docs/plans/2026-03-09-feat-skills-knowledge-graph-visual-interface-plan.md`
- `bash Infrastructure/scripts/validate_all.sh`
Release gates (blocking):
- `python3 Infrastructure/scripts/validation-and-linting/docs_lint.py --mode block --config Infrastructure/docs-policy.json`
- `vale Docs/plans/2026-03-09-feat-skills-knowledge-graph-visual-interface-plan.md`
- `bash Infrastructure/scripts/validation-and-linting/verify-work.sh`

## Rollout / Migration / Monitoring
Rollout approach:
- Deliver behind phased enablement aligned to phase gates.
- Keep read-only default until validation evidence for combined-failure scenarios is green.
- Do not enable interactive routes unless Phase 1 exit criteria are satisfied.
- Treat wave progression as blocked whenever envelope integrity errors are non-zero.

Migration:
- No schema migrations planned; consume existing artifact contracts.
- Maintain compatibility with existing blocker/status mappings.

Monitoring:
- Track interface health events:
  - `ui_snapshot_loaded`
  - `ui_join_ambiguity_detected`
  - `ui_accessibility_mode`
  - `ui_control_precedence_evaluated`
  - `ui_event_envelope_contract_failed`
  - `ui_degraded_mode_entered` / `ui_degraded_mode_cleared`
  - `ui_interaction_latency_ms`
  - `ui_interaction_complete_ms`
  - `refresh_end_to_end_ms`
  - `ui_action_denied`
  - `ui_diagnostics_downloaded`
- Track operational quality:
  - envelope error count,
  - HOLD reason distribution,
  - forced-downgrade trigger frequency.

Monitoring thresholds and paging:
- `ui_interaction_latency_ms`:
  - hold/escalate when p95 exceeds `100ms` for any high-frequency action class in a 1h window with `n>=200` samples per action class.
  - hold/escalate when p99 exceeds `150ms` for any high-frequency action class in a 1h window with `n>=200` samples per action class.
  - if `n<200` in 1h, mark `insufficient_data` and evaluate the 24h window before paging.
- `ui_interaction_complete_ms`:
  - hold/escalate when p95 exceeds `150ms` for any high-frequency action class in a 1h window with `n>=200` samples per action class.
  - hold/escalate when p99 exceeds `250ms` for any high-frequency action class in a 1h window with `n>=200` samples per action class.
  - if `n<200` in 1h, mark `insufficient_data` and evaluate the 24h window before paging.
- `refresh_end_to_end_ms`:
  - hold/escalate when p95 exceeds `6000ms` in a 1h window with `n>=200` refresh samples.
  - hold/escalate when p99 exceeds `6000ms` in a 1h window with `n>=200` refresh samples.
  - if `n<200` in 1h, mark `insufficient_data` and evaluate the 24h window before paging.
- `ui_join_ambiguity_detected`:
  - hold/escalate when either ambiguity rate rises by `>=2%` absolute or impacted-row count rises by `>=20%` versus the prior 7d baseline.
- `ui_accessibility_mode`:
  - escalate when reduced-motion coverage telemetry is missing or parity checks fail.
- `ui_event_envelope_contract_failed`:
  - immediate hold when non-zero in current run; wave progression blocked until cleared.

Release accountability:
- Final go/no-go authority: `release owner` (single DRI for this rollout).
- Owner role map (must be resolved to named DRIs in release checklist):
  - `release owner`: final authority for release decision and TR-01..TR-03.
  - `evaluation maintainer`: TR-04 and TR-05.
  - `promotion owner`: TR-06.
  - `telemetry owner`: envelope/freshness gates.
- Required gate owners:
  - `release owner`: TR-01, TR-02, TR-03, final go/no-go.
  - `evaluation maintainer`: TR-04, TR-05.
  - `promotion owner`: TR-06.
  - `telemetry owner`: event envelope and freshness gates.
- Backup ownership:
  - each gate owner must name one backup approver in the release checklist artifact.
  - takeover trigger: if the primary owner does not acknowledge a gate page within `2 minutes`, backup assumes authority and records takeover in `rollout-decision-log.md`.
  - incident channel of record: release incident thread linked from the rollout decision log.

Hard-gate activation contract:
- Source file: `Infrastructure/artifacts/skill-graphs/controls/hard-gate-mode.txt`.
- Allowed values: `auto|force_on|force_off`.
- Default when missing/invalid: `auto` (fail-closed).
- `auto` semantics:
  - `TR-04` and `TR-05` are hard gates from Phase 3+.
  - `TR-06` is a hard gate from Phase 4+.
- `force_on`: treat `TR-04`, `TR-05`, `TR-06` as hard gates immediately.
- `force_off`: non-production only; requires explicit incident ticket reference in rollout decision log.

Rollout decision protocol:

| Signal | Threshold | Window | Detector | Approver | Executor | Action |
|---|---|---|---|---|---|---|
| `TR-01` stability | `N>=1` (MVP baseline) | 7d | release owner | release owner | release owner | Hold when below threshold |
| `TR-02` critical non-regression | `100%` | 7d | release owner | release owner | release owner | Rollback-required when violated |
| `TR-03` budget compliance | `>=95%` | 7d | release owner | release owner | release owner | Hold when below threshold |
| `TR-04` evaluator consistency | `<=3%` | 7d | evaluation maintainer | release owner | release owner | Advisory in MVP; hard block Phase 3+ when `hard-gate-mode=auto|force_on` |
| `TR-05` judge calibration | `>=80%` | 14d | evaluation maintainer | release owner | release owner | Advisory in MVP; hard block Phase 3+ when `hard-gate-mode=auto|force_on` |
| `TR-06` promotion precision | `>=70%` | 14d | promotion owner | release owner | release owner | Hard block Phase 4+ when `hard-gate-mode=auto|force_on` |
| Event envelope errors | `0` hard requirement; escalation at `>=3` consecutive failing runs or `>=10` unique failures in rolling 24h | current run + 7d trend | telemetry owner | release owner | release owner | Non-zero enters `S3_DEGRADED`; escalation threshold breach triggers `rollback-required` and `S4_BLOCKED` |

Event envelope aggregation semantics:
- Unique failure key: `(run_id, failing_rule, source_version)`.
- Consecutive-run counter resets after a fully passing run (`0` envelope errors).
- 24h window is rolling (not fixed calendar) and evaluated at each run completion.
- Escalation decisions must persist computed counters in the release evidence bundle.

TR-03 mapping contract:
- Lab numerator: validation-fixture runs where high-frequency interaction p95, refresh-end-to-end SLO, and retry-envelope constraints all pass.
- Lab denominator: all runs on full-inventory validation fixtures.
- Runtime numerator: qualifying windows where the same SLO checks pass and runtime sample guards are met (`runtime_min_samples=200` per action class/window).
- Runtime denominator:
  - interaction latency track: windows with `runtime_min_samples=200` per action class.
  - refresh latency track: windows with `runtime_min_samples=200` refresh events.
- Coverage guard: if `<80%` of eligible runtime windows meet runtime sample guards across 24h, mark `insufficient_data` and hold progression to next rollout wave.
- Source: emitted runtime telemetry metrics + validation artifacts in release evidence bundle.
- Gate rule: lab track is always blocking; runtime track is advisory in MVP and blocking from Phase 4 onward.

Phase promotion gates:
- Phase 0 -> Phase 1:
  - decision-closure record complete and fixture baseline signed.
- Phase 1 -> Phase 2:
  - precedence + envelope checks green, transition-negative tests green.
- Phase 2 -> Phase 3:
  - adapter parity checks and deterministic join tests green.
  - `TR-04` and `TR-05` thresholds satisfied when `hard-gate-mode=auto|force_on`.
- Phase 3 -> Phase 4:
  - performance SLO and accessibility parity checks green.
  - `TR-04` and `TR-05` thresholds satisfied per hard-gate activation contract.
- Phase 4 -> Phase 5:
  - gate panel parity and observability thresholds green.
  - `TR-04`, `TR-05`, and `TR-06` remain passing (persistent hard-gate rule while in Phase 4+).
- Phase 5 -> rollout completion:
  - evidence bundle complete, rollback drill fresh, go/no-go approval recorded.
  - any `TR-04`/`TR-05` breach during Phase 3+ reverts status to HOLD until resolved.
  - any `TR-06` breach during Phase 4+ reverts status to HOLD until resolved.

Required release evidence bundle:
- Required artifacts:
  - `tests-summary.json` with unit/integration/accessibility/performance results.
  - `telemetry-thresholds.json` proving TR thresholds and envelope/freshness checks.
  - `rollout-decision-log.md` with owner approvals and timestamps.
  - `manifest.json` with SHA-256 for every evidence file.
- Required location:
  - one staging directory under `Infrastructure/artifacts/skill-graphs/telemetry/staging/<YYYYMMDDTHHMMSSZ>/` used during Phases 0-4.
  - one immutable release evidence directory under `Infrastructure/artifacts/skill-graphs/telemetry/releases/<YYYYMMDDTHHMMSSZ>/` created by seal/copy from staging during Phase 5.
  - any hash mismatch in `manifest.json` is a fail-closed hold.

Rollback execution matrix:
| Trigger | Detection source | Max time to act | Command(s) | Detector | Approver | Executor | Post-rollback checks |
|---|---|---|---|---|---|---|---|
| Critical gate violation (`TR-02`) | rollout decision protocol | 5 minutes | `python3 Infrastructure/scripts/write_skill_graph_controls_atomic.py --set kill-switch=on --set rollout-mode=off --reason "<incident>" --operator "<executor>" --approver "<approver>" --require-writable --verify` | release owner | release owner | release owner | verify `S4_BLOCKED`; verify `run_state_changed`/blocked envelope events; rerun validation bundle |
| Promotion precision hard-gate violation (`TR-06`) | rollout decision protocol | 5 minutes | `python3 Infrastructure/scripts/write_skill_graph_controls_atomic.py --set kill-switch=on --set rollout-mode=off --reason "<incident>" --operator "<executor>" --approver "<approver>" --require-writable --verify` (after promotion owner raises incident) | promotion owner | release owner | release owner | verify `S4_BLOCKED`; verify `run_state_changed`/blocked envelope events; rerun validation bundle |
| Envelope integrity failure spike | telemetry checks | 5 minutes | `python3 Infrastructure/scripts/write_skill_graph_controls_atomic.py --set rollback-required=on --set rollout-mode=off --reason "<incident>" --operator "<executor>" --approver "<approver>" --require-writable --verify` | telemetry owner | release owner | release owner | confirm `S4_BLOCKED`; confirm envelope errors trending to zero; verify no interactive/mutating affordances |
| Operator-issued emergency rollback | incident channel | 5 minutes | `python3 Infrastructure/scripts/write_skill_graph_controls_atomic.py --set kill-switch=on --set rollout-mode=off --reason "<incident>" --operator "<executor>" --approver "<approver>" --require-writable --verify` | release owner backup | release owner backup | release owner backup | verify `S4_BLOCKED`; verify no interactive/mutating affordances |

Rollback control-write contract:
- Approved command path is only `python3 Infrastructure/scripts/write_skill_graph_controls_atomic.py` (single canonical writer), aligned to `docs/skill-graphs/runbooks/skill-genome-loop.md`.
- Every execution must run preflight checks (`controls path exists`, `controls path writable`, owner/mode valid) before write.
- Required permission contract for preflight:
  - controls directory mode `0750` or stricter.
  - control file mode `0640` or stricter.
  - owner UID/GID must match rollout operator account from deployment config.
- Write semantics must be atomic (`temp -> fsync -> rename`) and verified as full control tuple after write.
- Every rollback command execution must append operator identity, approver identity, incident link, and timestamp to `rollout-decision-log.md`.
- `TR-06` and envelope-spike rollback paths require dual approval (detector + approver) before command execution unless emergency override is declared in the incident thread.
- Emergency backup authority is valid only after takeover trigger or explicit emergency override is recorded in `rollout-decision-log.md` before control writes.

Rollback clear and re-entry procedure:
- Clear command (`rollback-required` path): `python3 Infrastructure/scripts/write_skill_graph_controls_atomic.py --clear rollback-required --set rollout-mode=observe_only --reason "<resolution>" --operator "<executor>" --approver "<approver>" --require-writable --verify`.
- Clear command (`kill-switch` path): `python3 Infrastructure/scripts/write_skill_graph_controls_atomic.py --clear kill-switch --set rollout-mode=observe_only --reason "<resolution>" --operator "<executor>" --approver "<approver>" --require-writable --verify`.
- Required approvals: detector + release owner (or documented emergency override chain).
- Required verification sequence:
  - trigger explicit control re-check (`S4 -> S1`) and verify transition within 60s.
  - verify envelope contract pass (`ui_event_envelope_contract_failed == 0`) for the recovery run.
  - verify gate protocol status is neither `rollback-required` nor `kill-switch-active` before restoring rollout mode.

Post-release verification cadence:
- `+5m`: smoke checks + envelope integrity + control precedence.
  - command: `python3 Infrastructure/scripts/skill-graph/verify_recursive_skill_graph_artifacts.py --run-state-check --strict --manifest Infrastructure/artifacts/skill-graphs/telemetry/releases/<ts>/manifest.json`.
  - pass/fail: non-zero exit or missing blocked/envelope events is immediate hold.
- `+1h`: SLO and alert-threshold checks (latency, refresh, ambiguity, degraded frequency).
  - command: `jq -e '.runtime_alerts_checked == true and .runtime_min_samples == 200 and .ui_interaction_latency_ms.p95 <= 100 and .ui_interaction_latency_ms.p99 <= 150 and .ui_interaction_complete_ms.p95 <= 150 and .ui_interaction_complete_ms.p99 <= 250 and .refresh_end_to_end_ms.p95 <= 6000 and .refresh_end_to_end_ms.p99 <= 6000' Infrastructure/artifacts/skill-graphs/telemetry/releases/<ts>/telemetry-thresholds.json`.
  - pass/fail: threshold breach with sufficient sample volume is hold/escalate.
- `+24h`: full gate protocol review including trend windows and rollback-drill freshness.
  - command: `python3 Infrastructure/scripts/skill-graph/verify_recursive_skill_graph_artifacts.py --run-state-check --strict --manifest Infrastructure/artifacts/skill-graphs/telemetry/releases/<ts>/manifest.json && jq -e '.rollback_drill_age_days <= 14 and .release_status != \"hold\"' Infrastructure/artifacts/skill-graphs/telemetry/releases/<ts>/rollout-summary.json`.
  - pass/fail: hash drift, stale drill evidence, or unresolved holds blocks completion.

Rollback drill freshness gate:
- Require successful rollback drill evidence within last 14 days before rollout completion.

Pre-deploy artifact freshness gate:
- Required telemetry artifacts must be present and fresh before go/no-go.
- Max staleness:
  - core telemetry inputs <= 24h old,
  - decision artifacts <= 7d old.
- If decision artifacts exceed 7d, create and approve `docs/decisions/2026-03-09-skills-graph-ui-v1-decisions-refresh.md` before rollout continuation.
- Missing/stale required artifacts fail closed to hold state.

## Acceptance Checklist
- [ ] Plan honors spec boundaries and does not invent contract behavior.
- [ ] Decision record exists at `docs/decisions/2026-03-09-skills-graph-ui-v1-decisions.md` with owner and approval timestamp.
- [ ] Phase 1 safety gates are mandatory before interactivity.
- [ ] In `S3_DEGRADED`, safe read-only interactions remain available for unaffected panels.
- [ ] State resolution precedence for blocked/degraded is deterministic and tested.
- [ ] `rollback-required` control path verifies `S4_BLOCKED` behavior (not `S3_DEGRADED`).
- [ ] Disallowed lifecycle transitions are covered by negative tests.
- [ ] Alias-safe join + unmatched behavior is deterministic and operator-visible.
- [ ] Refresh/retry/stale-lock behavior is implemented and tested.
- [ ] Refresh constants match spec values (`5s`, `250ms/500ms`, `60s`, `30m`).
- [ ] Refresh budget contract enforces `6000ms` global deadline with sample-volume-qualified SLO checks.
- [ ] TR gate panel and HOLD reasons match schema/runbook semantics.
- [ ] Phase promotion gates explicitly enforce TR hard gates (`TR-04`, `TR-05`, `TR-06`) per hard-gate activation contract.
- [ ] Combined-failure scenarios are included in integration tests.
- [ ] `cold_start_no_snapshot` action whitelist is enforced (`retry`, `open runbook`, role-authorized `download diagnostics`) and non-whitelisted actions are blocked.
- [ ] Envelope integrity variants (`missing_events`, `missing_run_state_changed`, `missing_run_blocked_code`) are tested.
- [ ] `S5` exit branches (`S2|S3|S4`) and atomic refresh fallback behavior are tested.
- [ ] Accessibility and reduced-motion parity tests are included.
- [ ] Safety invariants for untrusted input and artifact path restrictions are explicitly tested.
- [ ] Input-budget and throttling constraints (`2048` bytes, `30 req/min/session`) are enforced and tested at threshold edges.
- [ ] Path canonicalization, symlink escape rejection, and traversal rejection tests are included.
- [ ] Redaction and output-encoding/log-sanitization tests are included.
- [ ] UI and standard logs expose only repo-relative artifact identifiers; absolute paths are limited to restricted diagnostics exports.
- [ ] Diagnostics export authorization is service-local, deny-by-default, and audited (`ui_action_denied`, `ui_diagnostics_downloaded`).
- [ ] Runbook navigation uses immutable allowlisted IDs and rejects raw URL/path payloads.
- [ ] Performance SLOs (`p95/p99` and refresh global budget) are measurable and enforced.
- [ ] Rollback execution uses canonical atomic writer path (`Infrastructure/scripts/write_skill_graph_controls_atomic.py`) with preflight + post-write verification.
- [ ] Rollback clear and re-entry procedure covers both blocker sources (`rollback-required`, `kill-switch`) and is tested (`S4 -> S1 -> S2|S3` recovery path).
- [ ] Rollout evidence bundle, accountability map, and rollback execution matrix are complete.
- [ ] Release evidence bundle includes hash-valid `manifest.json` and immutable timestamped directory.
- [ ] Rollout and monitoring checks are defined with concrete signals.

## Sources & References
- Spec:
  - `Docs/specs/2026-03-09-feat-skills-knowledge-graph-visual-interface-spec.md`
- Decision record:
  - `docs/decisions/2026-03-09-skills-graph-ui-v1-decisions.md`
- Origin brainstorm:
  - `docs/brainstorms/2026-02-24-skill-graph-live-auto-learning-brainstorm.md`
- Core contracts/runbooks:
  - `docs/skill-graphs/telemetry/daily-outputs.md`
  - `docs/skill-graphs/schemas/gate-contract.schema.md`
  - `docs/skill-graphs/runbooks/kill-switch-and-escalation.md`
  - `docs/skill-graphs/runbooks/skill-genome-loop.md`
  - `docs/skill-graphs/runbooks/skill-router.md`
  - `docs/skill-graphs/runbooks/events-jsonl-fix.md`
  - `docs/skill-graphs/pilots/rollback-drill.md`
- Existing implementation anchors:
  - `Infrastructure/scripts/lifecycle-and-sync/build_skill_state_map.py`
  - `Skills/skill-builder/Infrastructure/scripts/build_recursive_skill_shadow_report.py`
  - `Skills/skill-builder/Infrastructure/scripts/validate_skill_graph_profiles.py`
  - `Skills/skill-builder/Infrastructure/scripts/recursive_skill_loop.py`
  - `Infrastructure/scripts/skill-graph/verify_recursive_skill_graph_artifacts.py`
  - `Infrastructure/scripts/validate_all.sh`
