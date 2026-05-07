---
plan_id: ASK-INTENT-ROUTER-SCORECARD-20260304
title: feat: Intent-First Skill Router Scorecard (Top-3 + Confidence)
type: feat
status: completed
date: 2026-03-04
origin: docs/brainstorms/2026-03-04-skill-router-brainstorm.md
---

# feat: Intent-First Skill Router Scorecard (Top-3 + Confidence)

## Table of Contents
- [Overview](#overview)
- [Problem Statement / Motivation](#problem-statement--motivation)
- [Research Summary](#research-summary)
- [Proposed Solution](#proposed-solution)
- [Alternative Approaches Considered](#alternative-approaches-considered)
- [Premortem (Failure Scenario: 2026-09-04)](#premortem-failure-scenario-2026-09-04)
- [Plan Revisions from Premortem](#plan-revisions-from-premortem)
- [Technical Considerations](#technical-considerations)
- [System-Wide Impact](#system-wide-impact)
- [Implementation Phases](#implementation-phases)
- [Planned File Map](#planned-file-map)
- [Task Graph (id / depends_on)](#task-graph-id--depends_on)
- [Risk-First Execution Order (Top 5)](#risk-first-execution-order-top-5)
- [Execution Progress (2026-03-05)](#execution-progress-2026-03-05)
- [Acceptance Criteria](#acceptance-criteria)
- [Success Metrics](#success-metrics)
- [Dependencies & Risks](#dependencies--risks)
- [Open Questions](#open-questions)
- [AI-Era Delivery Considerations](#ai-era-delivery-considerations)
- [Validation Commands](#validation-commands)
- [Technical Review Deltas (2026-03-04)](#technical-review-deltas-2026-03-04)
- [Sources & References](#sources--references)

## Overview
Build a v1 intent-first skill router that returns deterministic top-3 skill recommendations with confidence and rationale, optimized for both humans and AI coding agents (see brainstorm: `docs/brainstorms/2026-03-04-skill-router-brainstorm.md`).

The v1 surface is CLI/report-first (no heavy UI), with rule-first deterministic scoring and auditable outputs (see brainstorm: `docs/brainstorms/2026-03-04-skill-router-brainstorm.md`).

## Problem Statement / Motivation
Today, skill selection depends heavily on prompt phrasing and manual judgment. This increases misroutes, slows starts, and creates avoidable correction loops. The repository already has strong skill metadata and governance mechanisms, but lacks a dedicated routing layer for first-choice quality.

Primary motivation carried forward from brainstorm: improve **first-hit routing accuracy** while preserving deterministic behavior and governance controls (see brainstorm: `docs/brainstorms/2026-03-04-skill-router-brainstorm.md`).

## Research Summary
### Brainstorm origin (primary input)
- Chosen approach: deterministic scorecard router.
- Rejected alternatives (for v1):
  - deterministic + confirm-step as default,
  - hybrid rules+LLM tie-break.
- Scope constraints:
  - top-3 + confidence + rationale output contract,
  - optimize for both humans and agents,
  - CLI/report-first delivery.

(All above carried forward from: `docs/brainstorms/2026-03-04-skill-router-brainstorm.md`.)

### Local repo findings
- Skill system is canonicalized around `SKILL.md` plus flat symlink sync flow (`README.md:176-180`, `Infrastructure/scripts/lifecycle-and-sync/sync_skills.sh:126`, `Infrastructure/scripts/lifecycle-and-sync/sync_skills.sh:158`).
- Existing recursive loop explicitly models routing concepts and router execution mode (`docs/skill-graphs/index.md:10`).
- Genome loop already computes routing confusion and candidate confidence controls (`Infrastructure/scripts/lifecycle-and-sync/run_skill_genome_loop.py:241`, `Infrastructure/scripts/lifecycle-and-sync/run_skill_genome_loop.py:391`, `Infrastructure/scripts/lifecycle-and-sync/run_skill_genome_loop.py:37-39`).
- Existing runbook defines candidate fields and fail-closed redaction posture (`docs/skill-graphs/runbooks/skill-genome-loop.md:92-115`, `docs/skill-graphs/runbooks/skill-genome-loop.md:147`).
- AGENTS requirements emphasize explicit tooling, discovery order, and docs TOC (`AGENTS.md:74`, `AGENTS.md:101`, `AGENTS.md:14`).

### Institutional learnings (closest equivalent)
- No `docs/solutions/` entries were found for this topic.
- Closest internal equivalents:
  - `docs/brainstorms/2026-02-24-skill-graph-live-auto-learning-brainstorm.md`
  - `Docs/plans/2026-02-24-feat-skill-graph-live-auto-learning-plan.md`
  - `docs/skill-graphs/runbooks/skill-genome-loop.md`
  - `docs/skill-graphs/knowledge-graph-operating-model.md`

### External research decision
No external research performed. Reason: low external-risk domain, strong internal patterns already present, and clear origin decisions from the brainstorm.

### SpecFlow analysis highlights incorporated
- Define deterministic tie-break contract.
- Define confidence bands and machine-readable schema.
- Define low/zero-confidence fallback behavior.
- Define actor-specific first-hit instrumentation.
- Define non-interactive execution policy for agents.
- Add adversarial/abuse fixtures and telemetry redaction invariants.

## Proposed Solution
Create a scorecard-based router layer that evaluates each skill candidate using deterministic rules and outputs ranked top-3 recommendations.

### Core v1 behavior
1. Normalize input request.
2. Load active skill catalog from canonical source.
3. Apply deterministic feature scoring (trigger overlap, explicit mention, anti-trigger penalties, context alignment).
4. Stable sort with deterministic tie-breakers.
5. Return top-3 with confidence + rationale in both human and JSON views.
6. Emit routing telemetry for first-hit KPI tracking.

### Why this approach
This is the smallest useful slice that preserves auditability and governance while improving routing quality (see brainstorm: `docs/brainstorms/2026-03-04-skill-router-brainstorm.md`). It avoids premature model dependency and keeps failure modes explicit.

## Alternative Approaches Considered
1. **Deterministic + mandatory confirm step**
   - Benefit: lower accidental auto-selection risk.
   - Rejection for v1: adds interaction overhead before baseline signal is established (see brainstorm: `docs/brainstorms/2026-03-04-skill-router-brainstorm.md`).
2. **Hybrid rules + LLM tie-breaker**
   - Benefit: potentially stronger handling for highly ambiguous requests.
   - Rejection for v1: increased complexity, lower auditability, and harder deterministic testing (see brainstorm: `docs/brainstorms/2026-03-04-skill-router-brainstorm.md`).

## Premortem (Failure Scenario: 2026-09-04)
Six months later, the router rollout is considered a failure. First-hit accuracy improved on paper but trust declined. Users bypassed suggestions, agents misrouted high-confidence tasks, and maintainers disabled active mode.

### What went wrong
- Confidence scores were overfit and poorly calibrated; “high confidence” often meant “most keyword overlap,” not true intent.
- Skill catalog drifted (stale sync, inconsistent metadata quality), so deterministic ranking was deterministically wrong.
- Ambiguous and multi-intent prompts were forced into single-intent ranking without strong uncertainty handling.
- Human and agent execution policies diverged in practice; agent consumers auto-ran risky suggestions.
- Metrics were gameable (top-1 acceptance rose because UI nudged top candidate).
- Telemetry quality was noisy/incomplete, reducing ability to detect regressions early.

### False assumptions
- Assumed skill descriptions/triggers were sufficiently clean for reliable scoring.
- Assumed deterministic output alone would create user trust.
- Assumed low-confidence fallback states were rare.
- Assumed one KPI (first-hit) captured real quality and user value.

### Edge cases missed
- Negation prompts (“don’t use X”), mixed intents, and comparative asks.
- Typos, alias drift, deprecated skills, and synonym gaps.
- Long prompts with conflicting cues and non-English phrasing.
- Requests mentioning dangerous capabilities where auto-run should never trigger.

### Integration issues overlooked
- Catalog version mismatch between router and consumer runtimes.
- Incomplete contract tests across CLI, JSON consumers, and agent orchestration.
- Missing strong gates for rollout-state propagation and rollback drills.

### What users hated
- Opaque rationales (“matched keywords”) that felt generic.
- Confidently wrong top suggestion appearing repeatedly.
- Too much friction on uncertain prompts and too little safety on risky ones.

## Plan Revisions from Premortem
To reduce these failure modes, this plan now adds:
1. **Calibration-first rollout:** mandatory baseline dataset + calibration checks before active mode.
2. **Quality-gated metadata:** catalog freshness and SKILL metadata quality checks as preconditions.
3. **Uncertainty and safety-first policy:** explicit no-auto-run rules for risky/ambiguous cases.
4. **Anti-gaming metrics:** add override regret and correction-latency metrics, not just top-1 acceptance.
5. **Cross-surface contract testing:** strict roundtrip tests for CLI, JSON, and agent consumers.
6. **Operational resilience:** hard control precedence, rollback drills, and auto-downgrade triggers.

## Technical Considerations
- **Architecture impacts**
  - Introduce a routing contract layer separate from existing skill definitions.
  - Reuse current metadata pipeline (`SKILL.md` index and sync artifacts) rather than adding a second skill registry.
  - Keep rollout controls compatible with existing `off | observe_only | active` posture.

- **Performance implications**
  - Target low-latency local ranking for interactive CLI usage.
  - Use precomputed skill metadata snapshot where possible.
  - Keep deterministic sort and scoring O(n) or O(n log n) over skill count.

- **Security considerations**
  - Do not persist raw sensitive prompt text in routing logs.
  - Enforce telemetry allowlist + redaction-at-write.
  - Ensure non-interactive mode cannot silently auto-run low-confidence routes.
  - Default `agent_mode=observe_only` until rollout gates pass.

## System-Wide Impact
- **Interaction graph**
  - Request ingestion triggers router scoring, which produces ranked candidates, then selected skill execution, then telemetry logging.
  - In observe-only mode, execution behavior remains unchanged; only recommendation + telemetry layers are added.

- **Error propagation**
  - Catalog load or schema errors must return machine-readable error payloads and non-zero exit.
  - Low-confidence is not an error; it is an explicit routing state with fallback guidance.
  - Invalid controls (missing/unreadable/malformed) fail closed to safe mode (`observe_only` or `off`).

- **State lifecycle risks**
  - Risk: stale skill index causing poor recommendations.
  - Mitigation: include Infrastructure/catalog/version metadata in each router result and block active mode when freshness checks fail.

- **API surface parity**
  - Human CLI report and JSON output must reflect identical ranking and confidence values.
  - Agent consumers must rely on the same schema version used by CLI JSON output.

- **Integration test scenarios**
  1. Ambiguous request with two near-equal candidates yields stable order across repeated runs.
  2. Explicit skill mention always outranks generic intent-only matches.
  3. Non-interactive low-confidence request returns `requires_clarification=true` and no implicit auto-run.
  4. Broken skill metadata entry is skipped/flagged without crashing full ranking.
  5. First-hit telemetry records rank-chosen and actor type correctly.
  6. Multi-intent and negation prompts produce uncertainty flags instead of false-confidence routing.

## Implementation Phases
### Phase 1: Contract + control foundation
- Define invocation boundary contract (input shape, actor type, policy mode, output/error contract).
- Define router output schema v1 (human + JSON parity).
- Define telemetry allowlist/redaction contract with forbidden fields.
- Define deterministic scoring/tie-break specification and confidence bands.
- Define rollout control precedence (`kill-switch > rollback-required > rollout-mode`) with fail-closed behavior.

### Phase 2: Data quality + calibration foundation
- Build benchmark fixture set (clear, ambiguous, adversarial, multi-intent, negation, deprecated aliases).
- Define calibration policy (threshold bands + acceptable error rates by actor type).
- Add catalog freshness/version checks tied to sync pipeline.
- Add metadata quality checks (required fields, trigger completeness, anti-trigger presence where applicable).

### Phase 3: Router execution path
- Implement input normalization and candidate scoring.
- Implement deterministic ranking and rationale generation.
- Add CLI/report rendering and JSON output mode.
- Add explicit uncertainty handling for ambiguous/multi-intent prompts.

### Phase 4: Metrics + controlled rollout
- Add first-hit instrumentation by actor type (`human|agent`).
- Add anti-gaming metrics (override regret, correction latency, repeat-misroute rate).
- Add observe-only rollout baseline window and go/no-go thresholds.
- Add rollback drill and kill-switch propagation verification before active mode.
- Add auto-downgrade triggers back to `observe_only` on safety/quality regressions.

## Planned File Map
- `Skills/skill-builder/Infrastructure/scripts/skill_router.py` (new router engine)
- `Skills/skill-builder/Infrastructure/scripts/lifecycle-and-sync/skill_catalog.py` (canonical catalog loader + quality checks)
- `Skills/skill-builder/Infrastructure/scripts/skill_router_schema.py` (schema + confidence contract)
- `Skills/skill-builder/Infrastructure/scripts/test_skill_router.py` (determinism + edge-case tests)
- `Skills/skill-builder/Infrastructure/scripts/test_skill_router_fixtures.json` (ranking/adversarial fixtures)
- `Infrastructure/scripts/validation-and-linting/verify_router_schema.py` (schema/telemetry contract verifier)
- `Infrastructure/scripts/validation-and-linting/verify_skill_catalog_freshness.py` (catalog freshness and metadata quality gates)
- `Infrastructure/scripts/lifecycle-and-sync/skill_router_metrics.py` (first-hit + guardrail KPI aggregation)
- `Infrastructure/scripts/lifecycle-and-sync/run_skill_router_rollback_drill.sh` (control-precedence rollback drill)
- `docs/skill-graphs/schemas/skill-router.schema.md` (versioned contract)
- `docs/skill-graphs/runbooks/skill-router.md` (operational runbook)
- `docs/skill-graphs/telemetry/daily-skill-health.md` (metric additions)
- `docs/skill-graphs/telemetry/skill-router-go-no-go-thresholds.md` (rollout go/no-go thresholds)

## Task Graph (id / depends_on)
```yaml
tasks:
  - id: T0
    title: Define router invocation contract + control-plane precedence checks
    depends_on: []
  - id: T0A
    title: Define privacy-safe telemetry schema (allowlist, forbidden fields, redaction invariants)
    depends_on: [T0]
  - id: T0B
    title: Add versioned skill-router schema under docs/skill-graphs/schemas and validator integration
    depends_on: [T0A]
  - id: T0C
    title: Define catalog freshness contract tied to Infrastructure/scripts/lifecycle-and-sync/sync_skills.sh and SKILL frontmatter validation
    depends_on: [T0]
  - id: T1
    title: Define router scorecard specification (features, weights, confidence bands, deterministic tie-break order)
    depends_on: [T0]
  - id: T1A
    title: Build benchmark fixture corpus (clear, ambiguous, adversarial, multi-intent, negation)
    depends_on: [T1]
  - id: T1B
    title: Define calibration policy and acceptance thresholds by actor type
    depends_on: [T1A]
  - id: T2
    title: Define versioned router output schema (human parity + JSON)
    depends_on: [T1, T0B]
  - id: T3
    title: Build skill-catalog loader from canonical skill metadata sources
    depends_on: [T0C]
  - id: T3A
    title: Add metadata quality and freshness gate checks before routing
    depends_on: [T3]
  - id: T4
    title: Implement deterministic scoring and stable ranking engine
    depends_on: [T1, T3A]
  - id: T5
    title: Implement rationale generator, confidence band mapping, and uncertainty-state handling
    depends_on: [T2, T4, T1B]
  - id: T6
    title: Implement CLI/report outputs with --json contract support
    depends_on: [T2, T5]
  - id: T7
    title: Implement low-confidence and no-match fallback states
    depends_on: [T5, T6]
  - id: T8
    title: Instrument first-hit telemetry by actor type and chosen rank with redaction enforcement
    depends_on: [T0A, T6, T7]
  - id: T8A
    title: Add anti-gaming metrics (override regret, correction latency, repeat misroute rate)
    depends_on: [T8]
  - id: T9
    title: Add observe-only rollout control, policy gating, and explicit agent execution defaults
    depends_on: [T0, T7, T8]
  - id: T9A
    title: Define rollout go/no-go thresholds and auto-downgrade triggers to observe_only
    depends_on: [T9, T8A, T1B]
  - id: T9B
    title: Run rollback drill and kill-switch propagation test with evidence artifact
    depends_on: [T9A]
  - id: T10
    title: Add integration and adversarial fixtures (determinism, redaction-fail, blocked-auto-run, contract roundtrip)
    depends_on: [T6, T7, T8, T9A]
  - id: T11
    title: Update docs/runbooks and validate schema + telemetry contracts in repo validation flow
    depends_on: [T0B, T10, T9B]
```

## Risk-First Execution Order (Top 5)
Prioritize these first to reduce the highest-likelihood failure modes identified in the premortem:

1. **T0 + T0A** — Invocation and telemetry safety contracts  
   Prevents unsafe execution defaults and sensitive-data leakage.
2. **T0C + T3A** — Catalog freshness + metadata quality gates  
   Prevents deterministically wrong routing from stale/low-quality skill metadata.
3. **T1 + T1A + T1B** — Deterministic scoring + calibration baseline  
   Prevents overfit confidence and unstable tie-breaking behavior.
4. **T9 + T9A + T9B** — Rollout safety controls + rollback drills  
   Prevents unsafe active rollout and ensures rapid containment on regressions.
5. **T10** — Adversarial + contract roundtrip integration tests  
   Prevents cross-surface integration drift and missed edge cases before rollout.

## Execution Progress (2026-03-05)
- [x] T0 — Define router invocation contract + control-plane precedence checks
- [x] T0A — Define privacy-safe telemetry schema (allowlist + forbidden fields + redaction invariants)
- [x] T0B — Add versioned skill-router schema doc + validator integration scripts
- [x] T0C — Add catalog freshness + metadata quality validator (`Infrastructure/scripts/validation-and-linting/verify_skill_catalog_freshness.py`)
- [x] T1 — Define deterministic scorecard/tie-break implementation in router engine
- [x] T1A — Add benchmark/adversarial fixture corpus (`test_skill_router_fixtures.json`)
- [x] T1B — Finalize calibration thresholds by actor type (`ACTOR_THRESHOLDS` in `skill_router_schema.py`)
- [x] T2 — Define versioned router output schema (human parity + JSON) via schema doc + `validate_router_result`
- [x] T3 — Build canonical skill-catalog loader (`skill_catalog.py`)
- [x] T3A — Add metadata quality + freshness gate checks before routing
- [x] T4 — Implement deterministic scoring + stable ranking engine
- [x] T5 — Implement rationale/confidence mapping + uncertainty-state handling
- [x] T6 — Implement CLI/report outputs with `--json` contract support
- [x] T7 — Implement low-confidence/no-match style fallback behavior and clarify states
- [x] T8 — Add routing telemetry event emission (`--events-out`) with redaction-safe payload
- [x] T8A — Add anti-gaming metrics aggregation (`Infrastructure/scripts/lifecycle-and-sync/skill_router_metrics.py`)
- [x] T9 — Enforce explicit agent execution defaults and policy gating
- [x] T9A — Define rollout go/no-go thresholds + auto-downgrade policy artifacts
- [x] T9B — Execute rollback drill + kill-switch propagation evidence capture (`Infrastructure/scripts/lifecycle-and-sync/run_skill_router_rollback_drill.sh`)
- [x] T10 — Add integration/adversarial fixture coverage for determinism + contracts
- [x] T11 — Update schema/runbook docs and validation wiring in repo scripts

## Acceptance Criteria
- [x] Router returns deterministic top-3 results for identical input and catalog version.
- [x] Each candidate includes confidence score and concise rationale.
- [x] CLI human output and `--json` output are schema-consistent.
- [x] Low-confidence and no-match states are explicit and non-crashing.
- [x] Non-interactive agent mode defaults to `observe_only`; auto-run only when explicit policy gate passes.
- [x] First-hit metrics are captured separately for human and agent actors.
- [x] Anti-gaming metrics are captured: override regret, correction latency, repeat misroute rate.
- [x] No telemetry record contains raw prompt/objective text or secret-like tokens.
- [x] If controls are missing/unreadable/invalid, routing mode fails closed to safe state.
- [x] High-risk skill recommendations require explicit confirmation.
- [x] Catalog freshness and metadata quality checks gate active routing mode.
- [x] Schema compatibility changes require schema version bump + validator update.
- [x] Docs include usage guidance, control hierarchy, and rollback procedure.

## Success Metrics
- **Primary KPI:** top-1 first-hit routing accuracy improves over baseline (see brainstorm: `docs/brainstorms/2026-03-04-skill-router-brainstorm.md`).
- **Guardrail KPIs:**
  - override regret decreases,
  - correction latency decreases,
  - repeat misroute rate decreases,
  - low-confidence false auto-run rate approaches zero,
  - telemetry redaction violation rate remains zero.

## Dependencies & Risks
### Dependencies
- Canonical skill metadata consistency (`SKILL.md`, sync outputs, and skill folders).
- Existing telemetry artifact paths for routing outcomes.
- Rollout-control conventions already used in skill-graph runbooks.

### Risks and mitigations
- **Underspecified confidence semantics** → lock versioned confidence-band contract and calibration thresholds.
- **Tie instability across environments** → deterministic tie-break order and golden fixture tests.
- **Overfitting score weights** → benchmark + calibration window before active mode.
- **Telemetry sensitivity leakage** → allowlist + redaction-at-write + invariant tests.
- **Control misconfiguration** → explicit precedence checks and fail-closed safe mode.
- **Catalog drift** → freshness and metadata quality gates.
- **Scope creep into UI or LLM tie-breakers** → defer until v1 KPIs/guardrails validate deterministic baseline (see brainstorm: `docs/brainstorms/2026-03-04-skill-router-brainstorm.md`).

## Open Questions
From premortem + technical review, carry forward for implementation-resolution:
1. Exact numeric thresholds for confidence bands and policy gates.
2. Minimum baseline sample window for go/no-go active rollout.
3. Whether deprecated aliases are included in v1 compatibility scope.
4. Final list of router JSON fields needed by downstream agent orchestration.

## AI-Era Delivery Considerations
- Keep router outputs easily consumable by both humans and agents from day one.
- Require explicit test fixtures for ambiguous/adversarial prompts to prevent regression from rapid iteration.
- Treat auto-routing behavior as high-impact; require human review for threshold/policy changes.
- Document generated scoring heuristics and keep rationale traceable to stable rule identifiers.

## Validation Commands
- `python3 ~/.codex/Infrastructure/scripts/plan-graph-lint.py Docs/plans/2026-03-04-feat-intent-first-skill-router-scorecard-plan.md`
- `python3 Infrastructure/scripts/validation-and-linting/docs_lint.py --mode warn --config Infrastructure/docs-policy.json`
- `python3 Infrastructure/scripts/validation-and-linting/verify_router_schema.py --fail-on-sensitive-fields`
- `python3 Infrastructure/scripts/validation-and-linting/verify_skill_catalog_freshness.py --strict`
- `python3 Infrastructure/scripts/lifecycle-and-sync/skill_router_metrics.py --events Infrastructure/artifacts/skill-graphs/telemetry/skill-router-events.jsonl --json`
- `bash Infrastructure/scripts/lifecycle-and-sync/run_skill_router_rollback_drill.sh`
- `bash Infrastructure/scripts/validate_all.sh`

## Technical Review Deltas (2026-03-04)
Applied deltas from architecture and security review:
- Added explicit control precedence and fail-closed control behavior.
- Added telemetry contract hardening (allowlist, forbidden fields, redaction invariants).
- Added invocation boundary and machine-readable error/exit contract requirements.
- Added schema governance integration under `docs/skill-graphs/schemas` + validator wiring.
- Added enforceable rollout gates, rollback drill requirement, and auto-downgrade rules.

## Sources & References
- **Origin brainstorm:** `docs/brainstorms/2026-03-04-skill-router-brainstorm.md`
  - Carried-forward decisions: deterministic rule-first routing, top-3 confidence+rationale output, CLI/report-first surface, first-hit accuracy KPI.
- **Repo architecture and conventions:**
  - `AGENTS.md:14`
  - `AGENTS.md:74`
  - `AGENTS.md:101`
  - `README.md:176-180`
  - `Infrastructure/scripts/lifecycle-and-sync/sync_skills.sh:126`
  - `Infrastructure/scripts/lifecycle-and-sync/sync_skills.sh:158`
- **Routing/telemetry precedents:**
  - `docs/skill-graphs/index.md:10`
  - `docs/skill-graphs/runbooks/skill-genome-loop.md:92-115`
  - `docs/skill-graphs/runbooks/skill-genome-loop.md:147`
  - `Infrastructure/scripts/lifecycle-and-sync/run_skill_genome_loop.py:37-39`
  - `Infrastructure/scripts/lifecycle-and-sync/run_skill_genome_loop.py:241`
  - `Infrastructure/scripts/lifecycle-and-sync/run_skill_genome_loop.py:391`
- **Related internal artifacts (institutional context):**
  - `docs/brainstorms/2026-02-24-skill-graph-live-auto-learning-brainstorm.md`
  - `Docs/plans/2026-02-24-feat-skill-graph-live-auto-learning-plan.md`
  - `docs/skill-graphs/knowledge-graph-operating-model.md`
