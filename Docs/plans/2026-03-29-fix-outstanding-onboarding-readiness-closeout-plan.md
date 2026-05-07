---
plan_id: ASK-ONBOARDING-CLOSEOUT-20260329
title: fix: Outstanding Onboarding and Readiness Closeout
type: fix
status: completed
date: 2026-03-29
origin: Infrastructure/artifacts/skill-graphs/onboarding/wave-readiness.json
parent_plan: Docs/plans/2026-02-26-feat-all-skills-graph-migration-onboarding-plan.md
deepened: 2026-03-29
---

# fix: Outstanding Onboarding and Readiness Closeout

## Table of Contents
- [Overview](#overview)
- [Enhancement Summary](#enhancement-summary)
- [Problem Frame](#problem-frame)
- [Requirements Trace](#requirements-trace)
- [Scope Boundaries](#scope-boundaries)
- [Context and Research](#context-and-research)
- [Key Technical Decisions](#key-technical-decisions)
- [Open Questions](#open-questions)
- [Implementation Units](#implementation-units)
- [Execution Control Gates](#execution-control-gates)
- [Task Graph (id and depends_on)](#task-graph-id-and-depends_on)
- [System-Wide Impact](#system-wide-impact)
- [Risks and Dependencies](#risks-and-dependencies)
- [Documentation and Operational Notes](#documentation-and-operational-notes)
- [Execution Ledger (Planning Mode)](#execution-ledger-planning-mode)
- [Acceptance Checklist](#acceptance-checklist)
- [Sources and References](#sources-and-references)

## Overview

Close all currently known outstanding onboarding/readiness items in this repository by:
- clearing wave-gate blockers,
- replacing checklist placeholder ownership/status with operational assignments,
- reconciling plan-state tracking,
- and finishing worktree closeout with validation evidence.

Plan mode: `standard-plan`  
Plan depth: `deep`  
Execution posture: characterization-first for telemetry gates, then deterministic remediation and evidence-first closeout.

## Enhancement Summary

**Deepened on:** 2026-03-29  
**Mode:** targeted-confidence  
**Key areas improved:** gate sequencing, telemetry-window handling, no-go controls, acceptance evidence fidelity

- Added explicit gate-to-gate progression and stop conditions so execution cannot skip unresolved blockers.
- Tightened telemetry handling to require decision-window freshness and waiver-traceability before wave promotion.
- Strengthened final validation semantics with explicit no-go posture when critical closeout criteria remain open.

## Problem Frame

The all-skills onboarding lane is in a partially complete state:
- wave gates are blocked because `event_envelope_errors` is non-zero (`8`),
- onboarding checklist entries are all placeholder state (`pending`, `unassigned`, `tbd`),
- active planning artifacts and execution status are split across files without one explicit closeout path,
- branch/worktree state includes a large unfinished delta (`M`, `D`, and `??`) that prevents clear completion reporting.
- the published daily-health snapshot is historical, so readiness interpretation can drift if decision-window freshness is not enforced during remediation.

Without a single closeout plan, remediation can appear complete locally while governance signals remain blocked at wave gates and operational ownership remains undefined.

## Requirements Trace

- R1. Wave readiness must be unblocked with `event_envelope_errors = 0` for the active decision window, with auditable evidence.
- R2. Onboarding checklist ownership/status must move from placeholder defaults to actionable assignment data and progression states.
- R3. Planning state must reflect real execution status with one canonical closeout DAG and explicit dependency order.
- R4. Worktree closeout must classify and resolve outstanding changes without losing intentional artifacts.
- R5. Validation outputs must prove readiness using repo-standard checks and regenerated onboarding artifacts.
- R6. Final handoff must include go/no-go status and remaining-risk disclosure if anything cannot be fully closed.

## Scope Boundaries

In scope:
- telemetry envelope blocker remediation in skill-graph readiness pipeline,
- onboarding checklist generation and ownership/status source-of-truth updates,
- closeout task graph definition and synchronization with planning artifacts,
- branch/worktree closeout strategy and validation evidence capture.

Out of scope:
- unrelated feature development,
- redesign of the full recursive skill loop architecture,
- broad historical telemetry rewrites beyond what is required to satisfy current readiness gates,
- new UI planning artifacts.

## Context and Research

### Relevant Code and Patterns

- `Skills/skill-builder/Infrastructure/scripts/validate_skill_graph_profiles.py`
  - owns wave readiness artifact generation and blocker logic, including `EVENT_ENVELOPE_ERRORS`.
- `Skills/skill-builder/Infrastructure/scripts/build_recursive_skill_shadow_report.py`
  - emits `event_envelope_errors` into dashboard outputs consumed downstream.
- `Skills/skill-builder/Infrastructure/scripts/generate_skill_graph_profiles.py`
  - currently generates onboarding checklist rows with hardcoded `pending`, `unassigned`, and `tbd`.
- `docs/skill-graphs/telemetry/daily-skill-health.md`
  - currently reports `Event envelope errors: 8` with run-level evidence.
- `Infrastructure/artifacts/skill-graphs/onboarding/wave-readiness.json`
  - current readiness gates show `wave-0-controls.ready = false`, cascading to wave 1 and wave 2 blocked.
- `.agents/PLANS.md`
  - contains active task DAG definitions but no closeout-specific tracking lane for the currently outstanding set.

### Institutional Learnings

- Keep evidence machine-diffable and deterministic (counts, blocker codes, concrete file outputs).
- Prefer bounded remediation over broad exploratory rewrites.
- Treat docs/CLI parity and governance checks as required for onboarding-flow changes.

### External References

- None required; local repository artifacts are sufficient for this closeout plan.

## Key Technical Decisions

- Decision 1: Treat readiness unblock as a data-integrity fix, not a presentation-only fix.
  - Rationale: wave gates depend on telemetry-derived blocker counts; changing display-only artifacts would produce false readiness.

- Decision 2: Replace checklist placeholder state via a deterministic assignment input, not manual markdown editing.
  - Rationale: generated checklist outputs must remain reproducible and auditable.

- Decision 3: Keep closeout sequencing explicit with dependency gates (`P0 -> P5`) and one active ledger step.
  - Rationale: avoids parallel partially-complete remediation lanes that can reintroduce drift.

- Decision 4: Worktree closeout uses classify-then-validate-then-commit slices.
  - Rationale: prevents mixing blocker fixes with unrelated local changes and preserves reviewability.

- Decision 5: Wave readiness freshness uses a dual gate: recency plus decision-window alignment.
  - Rationale: stale but green outputs can pass unless both artifact age and window metadata are validated.

- Decision 6: Waiver handling reuses the canonical verifier waiver contract as the single source of truth.
  - Rationale: parallel waiver schemas increase drift risk; one contract keeps readiness and verifier behavior auditable.

## Open Questions

### Resolved During Planning

- Should event-envelope remediation prefer historical backfill or waiver-aware windowing?
  - Resolution: first use deterministic evidence-based remediation for missing envelopes in the active window; allow waiver handling only when a tracked waiver artifact explicitly authorizes exclusion and validator logic enforces that contract.

- Should waivers use a new closeout-specific schema or reuse existing verifier waivers?
  - Resolution: reuse `Infrastructure/scripts/skill-graph/verify_recursive_skill_graph_artifacts.py` waiver contract and extend only minimally for readiness scope fields if needed.

- Should freshness gating check only artifact age or also window alignment?
  - Resolution: enforce both recency (`health_generated_at` max age) and decision-window alignment (`window_start/window_end` matches configured decision window).

### Resolved During Implementation

- Exact owner mapping for all 84 skills if no maintained owner registry exists.
  - Resolution: added `Infrastructure/artifacts/skill-graphs/onboarding/skill-owner-map.json` with explicit defaults plus targeted per-skill overrides; checklist generation now consumes this map deterministically.

## Implementation Units

- [x] **P0 / Baseline Freeze and Outstanding-Issue Contract**

**Goal:** Freeze the exact outstanding set and define the closeout contract before changing logic.

**Requirements:** R1, R2, R3, R6

**Dependencies:** None

**Files:**
- Modify: `.agents/PLANS.md`
- Create: `Infrastructure/artifacts/skill-graphs/onboarding/outstanding-closeout-baseline-2026-03-29.json`
- Test: `python3 ~/.codex/Infrastructure/scripts/plan-graph-lint.py .agents/PLANS.md`

**Approach:**
- Add a dedicated closeout DAG in `.agents/PLANS.md` with `P0..P5` dependency mapping.
- Snapshot current blocker counts and checklist placeholder metrics into a baseline JSON artifact.
- Define completion thresholds for each outstanding class so downstream units cannot shift goalposts.

**Patterns to follow:**
- Existing `.agents/PLANS.md` DAG format.

**Test scenarios:**
- Plan graph lints with new closeout DAG.
- Baseline artifact is reproducible on rerun without manual edits.

**Verification:**
- One explicit contract artifact exists for what "fixed" means.

**Exit criteria:**
- Closeout DAG exists and passes lint.
- Baseline artifact recorded with blocker and placeholder metrics.

- [x] **P1 / Event-Envelope Gate Remediation**

**Goal:** Drive unresolved `event_envelope_errors` to zero for the active decision window and unblock wave-0 controls.

**Requirements:** R1, R5

**Dependencies:** P0

**Files:**
- Modify: `Skills/skill-builder/Infrastructure/scripts/build_recursive_skill_shadow_report.py`
- Modify: `Skills/skill-builder/Infrastructure/scripts/validate_skill_graph_profiles.py`
- Modify: `Infrastructure/scripts/skill-graph/verify_recursive_skill_graph_artifacts.py` (waiver contract parity only if additional readiness fields are required)
- Modify: `docs/skill-graphs/telemetry/daily-skill-health.md`
- Modify: `Infrastructure/artifacts/skill-graphs/onboarding/wave-readiness.json`
- Modify: `Infrastructure/artifacts/skill-graphs/pilot/artifact-parity-waivers.json` (only when explicit waivers are required)
- Test: `Skills/skill-builder/Infrastructure/scripts/test_events_jsonl_required.py`
- Test: `Infrastructure/scripts/testing/test_verify_recursive_skill_graph_artifacts.py`

**Approach:**
- Identify each missing-envelope run in the active health window and classify as remediable or explicitly waivable.
- Reuse canonical verifier waiver input (`waived_runs`) and avoid introducing a second waiver schema for readiness.
- Implement deterministic readiness metrics with explicit buckets:
  - `event_envelope_errors_total`
  - `event_envelope_errors_waived`
  - `event_envelope_errors_unresolved`
- Enforce freshness as a dual gate:
  - recency (`health_generated_at` within max age),
  - decision-window alignment (`window_start/window_end` matches configured decision date/window-days).
- Regenerate daily health and wave readiness artifacts from source scripts after remediation.

**Execution note:** characterization-first, then targeted remediation.

**Patterns to follow:**
- Existing blocker code path in `validate_skill_graph_profiles.py`.

**Test scenarios:**
- Missing envelope in active window yields blocker.
- Resolved/backfilled/waived run no longer increments unresolved error count.
- Waived run increments `waived` but not `unresolved`.
- Stale health artifact fails recency gate even when envelope counts are green.
- Window metadata mismatch fails alignment gate.
- Wave-0 readiness flips only when unresolved count is zero and freshness gates pass.

**Verification:**
- `wave-readiness.json.summary.event_envelope_errors_unresolved == 0`.
- `wave-readiness.json.summary.event_envelope_errors_total` and `event_envelope_errors_waived` are present.
- Freshness metadata is present and validator-approved for recency and window alignment.
- `wave-0-controls.ready == true` (assuming no other controls fail).

**Exit criteria:**
- Event-envelope blocker removed from current wave readiness.
- Decision window metadata in readiness/health artifacts reflects the active closeout window and passes freshness gates.
- Any waived envelope defects are traceable to explicit waiver evidence and still reported in closeout notes.

- [x] **P2 / Checklist Ownership and Status Operationalization**

**Goal:** Replace placeholder checklist states with deterministic assignment and readiness progression data.

**Requirements:** R2, R5

**Dependencies:** P0

**Files:**
- Modify: `Skills/skill-builder/Infrastructure/scripts/generate_skill_graph_profiles.py`
- Create: `Infrastructure/artifacts/skill-graphs/onboarding/skill-owner-map.json`
- Modify: `Infrastructure/artifacts/skill-graphs/onboarding/skill-onboarding-checklist-2026-03-29.md`
- Test: `Infrastructure/scripts/testing/test_bootstrap_recursive_skill_graph_artifacts.py`

**Approach:**
- Extend checklist generation to consume an owner/status input map (with explicit defaults).
- Generate checklist rows with actionable `readiness_status`, `owner`, and `due_date`.
- Keep generation deterministic and rerunnable from source-of-truth inputs.

**Patterns to follow:**
- Existing checklist writer in `generate_skill_graph_profiles.py`.

**Test scenarios:**
- Checklist generation with owner map fills non-placeholder owner/due/status fields.
- Missing owner map entry falls back to explicit default policy value.

**Verification:**
- No checklist row remains `owner=unassigned` or `due_date=tbd` unless explicitly permitted by policy.

**Exit criteria:**
- Checklist transitions from placeholder defaults to operationally assigned state.
- Assignment source and fallback policy are documented and reproducible.

- [x] **P3 / Plan-State and Completion-Tracking Reconciliation**

**Goal:** Align active plan artifacts and acceptance tracking so completion status is explicit and auditable.

**Requirements:** R3, R6

**Dependencies:** P0, P1, P2

**Files:**
- Modify: `.agents/PLANS.md`
- Modify: `Docs/plans/2026-02-26-feat-all-skills-graph-migration-onboarding-plan.md`
- Modify: `Docs/plans/2026-03-29-fix-outstanding-onboarding-readiness-closeout-plan.md`
- Test: `python3 ~/.codex/Infrastructure/scripts/plan-graph-lint.py .agents/PLANS.md`

**Approach:**
- Add explicit status notes linking prior onboarding plan completion claims to current blocker reality.
- Keep historical plan intact while appending closeout references rather than rewriting history.
- Ensure one current canonical closeout plan is the active execution source.

**Patterns to follow:**
- Existing plan frontmatter and execution-ledger conventions in `docs/plans`.

**Test scenarios:**
- Plan graph lint passes after updates.
- Historical plan and closeout plan references do not conflict.

**Verification:**
- There is one unambiguous active closeout lane with dependency order and acceptance mapping.

**Exit criteria:**
- Plan-state drift resolved across `.agents/PLANS.md` and active plan docs.
- Exactly one closeout execution lane is marked in-progress across planning artifacts.

- [x] **P4 / Worktree Closeout and Change-Slice Hygiene**

**Goal:** Convert current local deltas into reviewable, intentional slices with no unresolved stray changes.

**Requirements:** R4, R6

**Dependencies:** P1, P2, P3

**Files:**
- Modify: repository files touched by `P1-P3` implementations (scoped closeout lanes)
- Test: `git status --short --branch`

**Approach:**
- Classify all `M`, `D`, and `??` paths into: closeout-required, pre-existing unrelated, or defer/park.
- Keep closeout commits scoped by lane (telemetry gate, checklist operationalization, plan-state reconciliation).
- Ensure deleted files are either intentionally restored or intentionally removed with rationale.

**Execution note:** external-delegate optional for large change classification, but not required.

**Patterns to follow:**
- Existing repo expectation: evidence-first reporting of what is complete vs remaining.

**Test scenarios:**
- Each changed file maps to a closeout lane or explicit deferral rationale.
- No accidental artifact-only drift remains after regeneration.

**Verification:**
- Worktree reflects intentional closeout scope only.

**Exit criteria:**
- No ambiguous local-change bucket remains.
- Deferred changes are explicitly tagged with owner and rationale in closeout notes.

- [x] **P5 / Final Validation, Readiness Decision, and Handoff**

**Goal:** Produce final go/no-go closeout evidence and handoff-ready status.

**Requirements:** R5, R6

**Dependencies:** P4

**Files:**
- Modify: `Infrastructure/artifacts/validation/latest/*` (via validation workflows)
- Modify: `Infrastructure/artifacts/skill-graphs/onboarding/wave-readiness.json`
- Modify: `Infrastructure/artifacts/skill-graphs/onboarding/skill-onboarding-checklist-2026-03-29.md`
- Test: `bash Infrastructure/scripts/lifecycle-and-sync/sync_skills.sh`
- Test: `python3 Infrastructure/scripts/validation-and-linting/docs_lint.py --mode warn --config Infrastructure/docs-policy.json`
- Test: `vale **/*.md **/*.mdx **/*.adoc **/*.rst`
- Test: `bash Infrastructure/scripts/validation-and-linting/verify-work.sh`
- Test: `just validate` (or `bash Infrastructure/scripts/validate_all.sh`)
- Evidence artifact: `Infrastructure/artifacts/validation/latest/docs-lint.log` (captures docs lint + Vale output for this closeout lane)

**Approach:**
- Run validation stack in repo-prescribed order.
- Capture blocker-free evidence for wave gates and checklist operationalization.
- Publish final summary: complete, remaining (if any), and explicit residual-risk ownership.

**Patterns to follow:**
- `Docs/agents/04-validation.md` repository checks.

**Test scenarios:**
- Validation stack passes without wave blocker regressions.
- Checklist and readiness artifacts stay consistent across reruns.

**Verification:**
- Final closeout status is evidence-backed and operationally actionable.

**Exit criteria:**
- Go/no-go decision published with exact evidence paths.
- If no-go, blockers include owner and due date.
- Final report distinguishes critical blockers from non-blocking follow-ups.

## Execution Control Gates

- **Gate G0 (Contract lock):** Do not start `P1` or `P2` until `P0` baseline metrics are persisted and plan graph lint passes.
- **Gate G1 (Readiness integrity):** Do not start `P3` until `P1` has produced refreshed readiness artifacts with explicit `total/waived/unresolved` envelope counts and passing dual freshness gates.
- **Gate G2 (Operational ownership):** Do not start `P4` until `P2` checklist outputs are generated from assignment input and not from manual markdown edits.
- **Gate G3 (Tracking coherence):** Do not start `P5` until `P3` confirms a single active closeout lane with no contradictory plan-status signals.
- **Gate G4 (Release decision):** Mark closeout `go` only when `AC1-AC6` are satisfied; otherwise mark `no-go` with blocker owner, due date, and escalation path.

Stop conditions:
- Stop immediately if readiness artifacts cannot be regenerated deterministically from source scripts.
- Stop immediately if waiver evidence is referenced but missing or unreadable.
- Stop immediately if readiness freshness metadata is missing or fails recency/window-alignment checks.
- Stop immediately if validation fails due to scope-unknown file drift and classify the drift before continuing.

## Task Graph (id and depends_on)

```yaml
tasks:
  - id: P0
    title: Baseline freeze and closeout contract
    depends_on: []
  - id: P1
    title: Event-envelope gate remediation
    depends_on: [P0]
  - id: P2
    title: Checklist ownership and status operationalization
    depends_on: [P0]
  - id: P3
    title: Plan-state and completion-tracking reconciliation
    depends_on: [P0, P1, P2]
  - id: P4
    title: Worktree closeout and change-slice hygiene
    depends_on: [P1, P2, P3]
  - id: P5
    title: Final validation and readiness handoff
    depends_on: [P4]
```

## System-Wide Impact

- **Interaction graph:** impacts onboarding artifact generation, telemetry-readiness gating, plan governance, and release/validation reporting.
- **Error propagation:** unresolved event-envelope defects continue to block wave promotion; checklist placeholder drift causes operational ambiguity.
- **State lifecycle risks:** stale generated artifacts and unmanaged local deltas can create false completion signals.
- **API surface parity:** readiness semantics must stay aligned across daily health, wave readiness JSON, and skill-state map consumers.
- **Integration coverage:** unit tests plus end-to-end artifact regeneration are required to confirm gate behavior.

## Risks and Dependencies

- Risk: historical run envelopes may be irrecoverable.
  - Mitigation: explicit waiver policy path plus validator enforcement and traceable waiver evidence.

- Risk: owner assignment source may be incomplete.
  - Mitigation: deterministic fallback owner map with explicit policy defaults and exception report.

- Risk: large pre-existing worktree could mask regressions.
  - Mitigation: classify and scope closeout slices before final validation.

- Dependency: validation tooling and scripts must remain executable in current sandbox constraints.

- Risk: stale decision-window artifacts produce false-positive readiness.
  - Mitigation: enforce decision-window freshness check before accepting wave-gate outcomes.

- Risk: checklist ownership defaults can silently persist if generator inputs are partial.
  - Mitigation: require assignment coverage report with explicit fallback counts before accepting `P2`.

- Risk: waiver semantics diverge between verifier and readiness paths.
  - Mitigation: keep a single canonical waiver contract and only extend with backwards-compatible fields.

## Documentation and Operational Notes

- Keep this plan as the active closeout artifact until `P5` evidence is complete.
- Record completion and remaining items explicitly in final handoff.
- If wave readiness cannot reach all-green due to policy constraints, publish no-go with owner, due date, and next escalation action.

## Execution Ledger (Planning Mode)

STEP_ID | status | owner | evidence
P0 | completed | Codex | Baseline freeze captured in `Infrastructure/artifacts/skill-graphs/onboarding/outstanding-closeout-baseline-2026-03-29.json`; plan graph lint passed.
P1 | completed | Codex | Event-envelope metrics now include `total/waived/unresolved`; `wave-readiness.json.summary.event_envelope_errors_unresolved == 0`; waiver scope parity enforced via `artifact-parity-waivers.json`; `test_events_jsonl_required.py` now passes under event-envelope waiver contract.
P2 | completed | Codex | Deterministic owner map added at `Infrastructure/artifacts/skill-graphs/onboarding/skill-owner-map.json`; regenerated checklist has no placeholder owner/due/status values.
P3 | completed | Codex | Plan-state reconciliation applied to `.agents/PLANS.md` and onboarding plan docs with explicit closeout references.
P4 | completed | Codex | Worktree closeout scope classified to onboarding-readiness lane; sandbox-only sync-path constraints documented and resolved for validation by running sync with explicit permission scope.
P5 | completed | Codex | Validation stack completed: `bash Infrastructure/scripts/lifecycle-and-sync/sync_skills.sh`, `python3 Infrastructure/scripts/validation-and-linting/docs_lint.py --mode warn --config Infrastructure/docs-policy.json`, `vale **/*.md **/*.mdx **/*.adoc **/*.rst`, `bash Infrastructure/scripts/validation-and-linting/verify-work.sh`, `just validate`, `python3 ~/.codex/Infrastructure/scripts/plan-graph-lint.py .agents/PLANS.md`, plus targeted closeout tests. Evidence ledger includes `Infrastructure/artifacts/validation/latest/docs-lint.log` for the explicit Vale run.

## Acceptance Checklist

- [x] AC1. Unresolved event-envelope blocker count is zero in active wave readiness outputs, waiver and total counts are explicit, and wave-0 controls are no longer blocked by envelope errors.
Traceability: R1, R5
- [x] AC2. Onboarding checklist rows use operational ownership/status values instead of global placeholder defaults.
Traceability: R2, R5
- [x] AC3. `.agents/PLANS.md` and active onboarding closeout plan references are synchronized and lint-valid.
Traceability: R3
- [x] AC4. Worktree deltas are classified and reduced to intentional closeout scope with explicit rationale for any deferred files.
Traceability: R4, R6
- [x] AC5. Repository validation stack passes (or explicit failing gate documented with owner and due date) after closeout changes.
Traceability: R5, R6
- [x] AC6. Final handoff explicitly reports done vs remaining work with evidence paths and go/no-go decision.
Traceability: R6

## Sources and References

- `Infrastructure/artifacts/skill-graphs/onboarding/wave-readiness.json`
- `Infrastructure/artifacts/skill-graphs/onboarding/skill-onboarding-checklist-2026-03-29.md`
- `docs/skill-graphs/telemetry/daily-skill-health.md`
- `Skills/skill-builder/Infrastructure/scripts/validate_skill_graph_profiles.py`
- `Skills/skill-builder/Infrastructure/scripts/build_recursive_skill_shadow_report.py`
- `Infrastructure/scripts/skill-graph/verify_recursive_skill_graph_artifacts.py`
- `Skills/skill-builder/Infrastructure/scripts/generate_skill_graph_profiles.py`
- `.agents/PLANS.md`
- `Docs/agents/04-validation.md`
- `Docs/plans/2026-02-26-feat-all-skills-graph-migration-onboarding-plan.md`
