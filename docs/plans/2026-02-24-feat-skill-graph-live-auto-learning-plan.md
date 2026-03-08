---
title: feat: Skill Graph Live Auto-Learning (Post-Use Capture + Start-of-Run Injection)
type: feat
date: 2026-02-24
brainstorm: docs/brainstorms/2026-02-24-skill-graph-live-auto-learning-brainstorm.md
status: completed
affected_features:
  - skill runtime capture
  - evidence confidence scoring
  - lesson retrieval injection
  - rollout safety controls
---

# feat: Skill Graph Live Auto-Learning (Post-Use Capture + Start-of-Run Injection)

## Table of Contents
- [0) Outcome → opportunities → solution](#0-outcome--opportunities--solution)
- [1) Scope and boundaries](#1-scope-and-boundaries)
- [2) Plan epics and tasks](#2-plan-epics-and-tasks)
- [Task Graph (id / depends_on)](#task-graph-id--depends_on)
- [3) Acceptance criteria](#3-acceptance-criteria)
- [4) Risks and checks](#4-risks-and-checks)
- [5) Execution order and dependencies](#5-execution-order-and-dependencies)
- [6) Counterfactual Uplift Gate (causal quality control)](#6-counterfactual-uplift-gate-causal-quality-control)
- [7) Verification command set](#7-verification-command-set)
- [8) Technical review deltas (2026-02-24)](#8-technical-review-deltas-2026-02-24)
- [9) Batch execution progress (2026-02-25)](#9-batch-execution-progress-2026-02-25)

## 0) Outcome → opportunities → solution

### Outcome
Enable true end-to-end learning from normal skill usage by adding:
1) automatic post-use capture after every skill invocation, and
2) start-of-run lesson retrieval/injection for live runs.

### Opportunities
- Convert normal usage into reusable lesson candidates.
- Improve recommendation quality over time with evidence-ranked lessons.
- Preserve governance trust via confidence scoring, human promotion, and kill switches.

### Chosen solution
Implement a phased Phase-4 activation using best-effort evidence scoring, one-tap user feedback, start-of-run injection, and pilot-first guardrails (global + per-skill kill switches).

## 1) Scope and boundaries

### In scope
- Capture pipeline triggered for every skill invocation.
- Immediate one-tap post-run feedback (`worked | partly | didnt_work`) with optional note.
- Evidence collection and confidence scoring from artifacts (events, logs, traces, session signals, checks, diff context where available).
- Candidate lesson drafting from run outcome + evidence packet.
- Start-of-run retrieval/injection of relevant canonical lessons.
- Ranking that keeps low-confidence lessons injectable but down-ranked and flagged.
- Global/per-skill kill-switch controls for auto-capture and auto-apply.
- Counterfactual uplift evaluation that compares injected runs (treatment) against no-injection controls before promotion/auto-apply decisions.

### Out of scope (this phase)
- Mid-run/continuous re-injection.
- Fully autonomous canonical promotion without human gate.
- Broad rewrite of recursive engine architecture beyond required integration points.

## 2) Plan epics and tasks

### Epic A — Capture normal skill usage
- Add runtime hook to emit skill invocation envelope and output summary.
- Add immediate one-tap feedback collection path.
- Persist capture records with stable IDs and timestamps.

### Epic B — Build evidence confidence pipeline
- Build evidence assembler to collect run-local artifacts (events/logs/traces/session/check signals).
- Define confidence schema and score computation contract.
- Tag each candidate with confidence score + evidence completeness metadata.

### Epic C — Create lesson candidate drafting from captures
- Draft lesson candidates from advice + implementation/outcome evidence.
- Enforce safety and redaction checks before candidate enqueue.
- Append candidates to promotion queue artifacts with confidence fields.

### Epic D — Enable runtime retrieval/injection (start-of-run only)
- Retrieve scoped canonical lessons at run start.
- Rank by confidence-aware order (high confidence preferred; low confidence retained with warning flag).
- Record injected lesson IDs in run artifacts for attribution.

### Epic E — Safety and rollout controls
- Add global kill-switch and per-skill switch for `auto_capture` and `auto_apply`.
- Add rollout mode states (`off | observe_only | active`).
- Default to pilot-safe mode; allow quick rollback without code changes.

### Epic F — Validation, telemetry, docs
- Extend telemetry outputs with capture volume, confidence distributions, and injection usage rates.
- Add validation checks for schema, ranking invariants, and kill-switch precedence.
- Update docs and guides to reflect Phase-4 behavior and activation criteria.

### Epic G — Counterfactual Uplift Gate (single highest-leverage addition)
- For injected runs, compute a matched shadow control outcome (same context, no injection) to estimate causal uplift.
- Gate promotion and auto-apply on positive/credible uplift instead of raw outcome rates alone.
- Auto-downgrade to `observe_only` when uplift turns negative or uncertain over threshold windows.

## Task Graph (id / depends_on)
```yaml
tasks:
  - id: T1
    title: Define capture + feedback event schema for all skill invocations
    depends_on: []
  - id: T2
    title: Implement post-run one-tap feedback capture flow
    depends_on: [T1]
  - id: T3
    title: Build evidence packet assembler (events/logs/traces/sessions/checks)
    depends_on: [T1]
  - id: T4
    title: Implement confidence scoring contract and calibration buckets
    depends_on: [T3]
  - id: T5
    title: Generate lesson candidates from advice/implementation/outcome evidence
    depends_on: [T2, T4]
  - id: T6
    title: Extend promotion queue artifacts with confidence and evidence completeness fields
    depends_on: [T5]
  - id: T7
    title: Implement start-of-run retrieval and scoped lesson injection
    depends_on: [T1]
  - id: T8
    title: Add confidence-aware ranking with low-confidence warning/down-rank behavior
    depends_on: [T4, T7]
  - id: T9
    title: Persist injected lesson attribution in run artifacts
    depends_on: [T7]
  - id: T10
    title: Add global and per-skill kill switches for auto-capture/auto-apply
    depends_on: [T1]
  - id: T11
    title: Add rollout modes (off, observe_only, active) and pilot-safe defaults
    depends_on: [T10]
  - id: T12
    title: Extend telemetry dashboards and daily reports for live auto-learning metrics
    depends_on: [T6, T8, T9]
  - id: T13
    title: Add full validation suite for schema, ranking invariants, uplift contracts, and switch precedence
    depends_on: [T6, T8, T9, T10, T11, T16, T18]
  - id: T14
    title: Update docs and activation runbooks for Phase-4 live learning
    depends_on: [T12, T13]
  - id: T15
    title: Execute pilot rollout verification and publish go/no-go summary
    depends_on: [T11, T12, T13, T14, T16, T19]
  - id: T16
    title: Implement counterfactual uplift gate (treatment vs control) for promotion and auto-apply decisions
    depends_on: [T8, T9, T11, T12, T18]
  - id: T17
    title: Version promotion decision schema to include uplift, match-quality, and decision metadata fields
    depends_on: [T6, T9]
  - id: T18
    title: Update promotion validators and CI enforcement for uplift and match-quality contracts
    depends_on: [T17]
  - id: T19
    title: Run rollback drill and kill-switch propagation verification with evidence capture
    depends_on: [T10, T11, T13, T16]
```

## 3) Acceptance criteria
- Every skill run creates a capture record and supports immediate one-tap outcome feedback.
- Each candidate lesson includes confidence score + evidence completeness metadata.
- Start-of-run injection is active and logged with injected lesson IDs.
- Low-confidence lessons appear in retrieval results but are down-ranked and visibly flagged.
- Kill switches preempt runtime behavior and can disable capture/apply immediately.
- Promotion queue and daily telemetry expose live-learning metrics (capture count, confidence distribution, injection rate, post-injection outcome trend).
- Promotion and auto-apply require positive/credible uplift versus matched no-injection controls, with automatic downgrade to `observe_only` when uplift regresses.
- No transition to broad `active` rollout occurs unless `T16` uplift criteria and match-quality validity gates pass.
- Redaction-at-ingest, scope isolation, and kill-switch precedence tests pass before go/no-go.
- Rollback drill evidence and kill-switch propagation verification are attached to the go/no-go summary.

## 4) Risks and checks
| Risk | Impact | Mitigation |
|---|---|---|
| Noisy evidence causes weak lessons | recommendation drift | confidence weighting + promotion gate + down-rank low-confidence lessons |
| Feedback prompt fatigue | low user response rate | one-tap UX + optional note + fallback to system-only evidence |
| False attribution of success/failure | poor lesson quality | require explicit evidence packet and attribution fields |
| Kill switch bypass | unsafe rollout | precedence truth-table tests + fail-closed behavior + rollback drills |
| Over-scope into continuous orchestration | delivery delay | keep injection start-of-run only for this phase |
| Statistical peeking or weak matching | false uplift signals | fixed decision windows + match-quality gates + insufficient-data fallback |
| Secret/PII leakage via capture pipeline | compliance and trust risk | redaction-at-ingest + telemetry allowlist + canary leakage tests |

## 5) Execution order and dependencies
- Foundation first: `T1 -> T2/T3/T7/T10`.
- Evidence and quality core: `T3 -> T4 -> T5 -> T6` and `T7 -> T8 -> T9`.
- Schema/contract hardening for causal gating: `T6 + T9 -> T17 -> T18`.
- Causal quality gate before expansion: `T8 + T9 + T11 + T12 + T18 -> T16`; do not advance from pilot to broad active rollout without stable positive uplift.
- Full validation and safety drill path: `T6/T8/T9/T10/T11/T16/T18 -> T13 -> T19`.
- Final docs and rollout gate: `T12 + T13 -> T14`; `T11/T12/T13/T14/T16/T19 -> T15`.

## 6) Counterfactual Uplift Gate (causal quality control)
- **Core mechanism:** on each injected run (treatment), score a matched shadow control outcome with lesson injection disabled for the same context slice (`skill_id`, repo/workspace, task profile, recency window).
- **Primary outcome contract:** `primary_outcome = first_pass_acceptance_rate` (binary per run); `uplift_delta = p_treatment - p_matched_control`.
- **Uncertainty contract:** compute `uplift_confidence_band` as a versioned 95% CI method; persist method/version alongside every decision.
- **Matching validity contract:** required covariates = `skill_id`, `workspace/repo`, `task_profile`, `recency_bucket`; require post-match `|SMD| <= 0.10` per covariate and treated unmatched rate `<= 15%`, else `decision = insufficient_match_quality`.
- **Promotion pass threshold:** `sample_size >= 40` matched pairs total and `>= 10` per pilot skill, `uplift_delta >= +0.03`, and CI lower bound `> 0`.
- **Auto-apply expansion pass threshold:** `sample_size >= 100` matched pairs total and `>= 20` per pilot skill, `uplift_delta >= +0.05`, and CI lower bound `>= +0.02` for 2 consecutive 7-day windows.
- **Automatic downgrade triggers (fail-safe):** force `observe_only` within one control cycle if any: CI lower bound `<= 0`, `uplift_delta <= -0.02`, kill-switch propagation verification fails, or required telemetry integrity gates regress.
- **Decision cadence guardrail:** one go/no-go decision per fixed 7-day window; no intra-window promotion decisions.
- **Minimum reporting contract:** persist `control_outcome`, `treatment_outcome`, `uplift_delta`, `uplift_confidence_band`, `sample_size`, `match_quality_metrics`, `analysis_method_version`, and `decision` in rollout artifacts.

## 7) Verification command set
- `python3 ~/.codex/scripts/plan-graph-lint.py docs/plans/2026-02-24-feat-skill-graph-live-auto-learning-plan.md`
- `python3 ~/.codex/scripts/plan-graph-lint.py .agent/PLANS.md`
- `bash ~/.codex/scripts/verify-work.sh`
- `bash scripts/validate_recursive_promotions.sh`

Optional dry-run checks once implementation starts:
- `bash scripts/run_recursive_skill_shadow_cycle.sh --runs-per-profile 1 --window-days 3`
- `python3 utilities/skill-builder/scripts/build_recursive_skill_shadow_report.py --runs-root artifacts/skill-graphs/runs --window-days 3`
- `python3 utilities/skill-builder/scripts/validate_recursive_promotion.py --runs-root artifacts/skill-graphs/runs --window-days 3`

## 8) Technical review deltas (2026-02-24)
- Added hard dependency from rollout go/no-go path to counterfactual uplift gate readiness.
- Added explicit uplift math, matching validity checks, and pass/fail thresholds.
- Added schema/validator task chain (`T17 -> T18`) to bind uplift fields to CI enforcement.
- Expanded validation and rollout tasks to include rollback drill + kill-switch propagation evidence (`T19`).
- Added security/quality checks for redaction-at-ingest, scope isolation, and fail-closed behavior.

## 9) Batch execution progress (2026-02-25)
- [x] T1: Define capture + feedback event schema for all skill invocations
- [x] T2: Implement post-run one-tap feedback capture flow
- [x] T3: Build evidence packet assembler (events/logs/traces/sessions/checks)
- [x] T4: Implement confidence scoring contract and calibration buckets
- [x] T5: Generate lesson candidates from advice/implementation/outcome evidence
- [x] T6: Extend promotion queue artifacts with confidence and evidence completeness fields
- [x] T7: Implement start-of-run retrieval and scoped lesson injection
- [x] T8: Add confidence-aware ranking with low-confidence warning/down-rank behavior
- [x] T9: Persist injected lesson attribution in run artifacts
- [x] T10: Add global and per-skill kill switches for auto-capture/auto-apply
- [x] T11: Add rollout modes (off, observe_only, active) and pilot-safe defaults
- [x] T12: Extend telemetry dashboards and daily reports for live auto-learning metrics
- [x] T13: Add full validation suite for schema, ranking invariants, uplift contracts, and switch precedence
- [x] T16: Implement counterfactual uplift gate (treatment vs control) for promotion and auto-apply decisions
- [x] T17: Version promotion decision schema to include uplift, match-quality, and decision metadata fields
- [x] T18: Update promotion validators and CI enforcement for uplift and match-quality contracts
- [x] T14: Update docs and activation runbooks for Phase-4 live learning
- [x] T19: Run rollback drill and kill-switch propagation verification with evidence capture
- [x] T15: Execute pilot rollout verification and publish go/no-go summary
