---
title: feat: Skill Lifecycle, Scaffold Quality, and Institutional Memory Program Delivery Plan
type: feat
status: active
date: 2026-03-24
origin: docs/brainstorms/2026-03-24-skill-lifecycle-scaffold-memory-program-brainstorm.md
spec: Docs/specs/2026-03-24-feat-skill-lifecycle-scaffold-memory-program-spec.md
deepened: 2026-03-24
---

# feat: Skill Lifecycle, Scaffold Quality, and Institutional Memory Program Delivery Plan

## Enhancement Summary

**Deepened on:** 2026-03-24
**Mode:** targeted-confidence
**Key areas improved:** sequencing gates, validation surfaces, bounded seed adoption, rollout hold rules, and evidence paths

- Tightened `P0` so the authoritative metadata-representation decision produces a concrete readiness gate before downstream work starts.
- Strengthened `P2` and `P5` with explicit healthy/degraded/blocked expectations and evidence paths so rollout posture is testable rather than interpretive.
- Narrowed `P4` with a bounded seed-set strategy that proves shape without accidentally expanding the migration scope.

## Overview

Implement the phase-one program defined by the governing spec: establish lifecycle and ownership metadata for in-scope assets, make scaffold generators lifecycle-aware and realism-first, and introduce a governed `docs/solutions/` layer for reusable solved knowledge.

Plan mode: `standard-plan`
Plan depth: `standard`
Execution posture: contract-first, characterization-first

## Problem Frame

The governing spec identifies a repo-scale control-plane gap: `Agent-Skills` can author and validate many assets, but it lacks a canonical lifecycle model, scaffold generation still normalizes placeholder-heavy outputs, and there is no reusable `docs/solutions/` layer for durable resolved knowledge.

Without a sequenced plan, implementation is likely to drift in one of three ways:
- metadata becomes ceremony without driving real workflows
- scaffolds improve locally but encode the wrong lifecycle assumptions
- `docs/solutions/` appears as a folder without admission, freshness, or ownership rules

This plan sequences the work so the lifecycle control plane lands first, then becomes the source of truth for scaffold changes and institutional-memory capture.

## Requirements Trace

- R1. Implement a phase-one control plane for canonical skills, packaged skills, and plugin packages that satisfies `SA2`, `SA3`, `SA6`, `SA9`, and `SA10`.
- R2. Upgrade scaffold generation to consume the lifecycle contract and prevent false-green placeholder-heavy outputs, satisfying `SA4`, `SA7`, and `SA9`.
- R3. Introduce `docs/solutions/` as a governed reusable-solution layer with ownership, linkage, and freshness rules, satisfying `SA5`, `SA6`, `SA8`, and `SA11`.
- R4. Preserve the spec boundary by making readiness, degraded states, and representation authority explicit in validation and documentation rather than inventing them during implementation.
- R5. Leave the repo ready for later dashboard/operator-wrapper work without implementing those second-order surfaces in this plan.

## Scope Boundaries

In scope:
- lifecycle metadata contract materialization for phase-one managed assets
- scaffold-generator updates needed to collect or derive required lifecycle fields
- validator or diagnostic updates needed to detect degraded or false-green governance states
- creation of `docs/solutions/` plus its entry contract and starter governance guidance
- repo docs and templates needed to keep the three tracks aligned

Out of scope:
- repo-wide migration of every asset type beyond canonical skills, packaged skills, and plugin packages
- dashboards, reporting UIs, or operator wrappers
- implementation of unrelated quality improvements in touched scripts
- deletion or retirement workflows beyond what is needed to represent `deprecated`
- code execution beyond the planning artifact itself

## Context & Research

### Relevant Code and Patterns

- [2026-03-24-feat-skill-lifecycle-scaffold-memory-program-spec.md](/Users/jamiecraik/dev/Agent-Skills/Docs/specs/2026-03-24-feat-skill-lifecycle-scaffold-memory-program-spec.md)
  This is the authoritative contract for scope, lifecycle semantics, degraded states, and acceptance traceability.
- [create_basic_plugin.py](/Users/jamiecraik/dev/Agent-Skills/plugin-creator/Infrastructure/scripts/create_basic_plugin.py)
  The plugin scaffolder currently emits many broad `[TODO: ...]` placeholders and is the clearest false-green generation risk.
- [init_skill.py](/Users/jamiecraik/dev/Agent-Skills/skill-builder/Infrastructure/scripts/init_skill.py)
  This is the canonical skill scaffolder used by `skill-builder`, so lifecycle-aware realism-first generation has to land here first.
- [exceptions.md](/Users/jamiecraik/dev/Agent-Skills/GOVERNANCE/exceptions.md)
  Existing governance already uses owner/risk/review-date patterns, which is a useful alignment point for lifecycle metadata and review cadence semantics.

### Institutional Learnings

- Global learnings emphasize stale guidance, config drift, and mirrored-source ambiguity. That supports choosing one authoritative metadata representation and avoiding split-brain derived views.
- This repo already has strong governance and validation surfaces; the plan should plug into those rather than creating a parallel governance system.

### External References

- None needed. The local spec and repo evidence are sufficient for this planning pass.

## Key Technical Decisions

- Metadata-first sequencing is mandatory.
  Rationale: scaffold and `docs/solutions/` work become second-order if the authoritative lifecycle model is not chosen first.

- Use one authoritative metadata representation with optional derived views.
  Rationale: the spec explicitly treats split-brain metadata as a failure class, so planning must prevent equal-authority duplicates.

- Treat scaffold output quality as a readiness concern, not a cosmetic cleanup concern.
  Rationale: false-green generation is a named spec failure and must be blocked by contract-aware validation.

- Introduce `docs/solutions/` with an admission gate and maintenance context from day one.
  Rationale: a naive folder drop would violate `SA5` and `SA11` by turning reusable memory into an unowned note dump.

## Open Questions

### Resolved During Planning

- Should the work be treated as one program or separate initiatives?
  Resolution: one coordinated delivery plan with the lifecycle control plane as the anchor.

- Should the plan include UI-specific branches?
  Resolution: no. The governing spec sets `ui_required: false`, so a standard plan is sufficient.

### Deferred to Implementation
- None. The deepened spec now fixes the phase-one defaults for authoritative metadata representation, packaged-skill inheritance, and minimum `docs/solutions/` evidence thresholds. `P0` is responsible for materializing those defaults in repo-native surfaces without widening scope.

## High-Level Technical Design

> This is directional guidance for review and implementation alignment, not implementation code.

Program flow:
1. Materialize the lifecycle control plane in the canonical docs/Infrastructure/templates/validation layer.
2. Thread that control plane into skill/plugin scaffolds so generation captures required lifecycle data and avoids false-green output.
3. Add `docs/solutions/` plus a small governed entry contract that references managed assets and maintenance ownership.
4. Extend diagnostics/validation so degraded states, missing ownership, stale cadence, and orphaned solution links are observable.
5. Refresh any catalog or surfaced docs that depend on the new governance vocabulary.

Readiness model:
- `healthy`
  - required lifecycle fields exist in the authoritative representation
  - derived views agree or are freshly regenerated
  - scaffold output contains no unresolved governance placeholders
- `degraded`
  - asset exists and is governable, but one or more readiness invariants are missing or stale
- `blocked`
  - representation choice, ownership, or validation state is too ambiguous for safe adoption or promotion-style workflows

Phase-one incubating asset policy:
- `blocked`
  - ownership is missing
  - authoritative and derived lifecycle representations disagree and regeneration cannot reconcile them
  - required representation rules are absent, so the validator cannot tell where lifecycle truth lives
- `degraded`
  - review cadence exists but is overdue
  - `docs/solutions/` freshness or linkage is stale but the asset remains attributable and governable
  - non-critical lifecycle metadata is incomplete, but the authoritative representation is still readable
- `healthy`
  - only when the incubating asset meets the same required representation and ownership invariants as any other managed asset

Policy note:
- `P0` must preserve or tighten this matrix. It may not silently relax a `blocked` case into `degraded`.

## Implementation Units

- [ ] **P0 / Contract Materialization and Representation Baseline**

**Goal:** Materialize the lifecycle control plane in repo-native docs/templates and implement the spec's phase-one representation defaults without violating the spec.

**Requirements:** R1, R4

**Dependencies:** None

**Files:**
- Modify: `Docs/specs/2026-03-24-feat-skill-lifecycle-scaffold-memory-program-spec.md`
- Modify: `README.md`
- Modify: `SKILL.md`
- Modify: `Docs/agents/04-validation.md`
- Create or modify: `docs/reference/` files if a small canonical metadata reference is needed
- Test: `Infrastructure/scripts/validate_all.sh`
- Test: `Infrastructure/scripts/validation-and-linting/verify_skill_catalog_freshness.py`

**Approach:**
- Materialize the spec's in-file authoritative metadata model and document derivation rules for any subordinate views.
- Materialize the packaged-skill inheritance rule and minimum `docs/solutions/` evidence threshold in repo-native docs and validation surfaces.
- Add the minimum repo-facing documentation needed so later phases do not invent lifecycle vocabulary.
- Keep the decision small and phase-one scoped.

**Decision gate:**
- `P0` is not complete until the implementation records:
  - the authoritative in-file representation used by each in-scope asset category
  - whether any derived representations exist
  - which file or doc becomes the canonical source of truth
  - what event regenerates any derived views
  - what constitutes `degraded` versus `blocked` when those representations disagree
  - which exact packaged-skill artifact or path will serve as the phase-one proof target for the adopted inheritance model

**Execution note:** characterization-first

**Patterns to follow:**
- [exceptions.md](/Users/jamiecraik/dev/Agent-Skills/GOVERNANCE/exceptions.md)
- [2026-03-24-feat-skill-lifecycle-scaffold-memory-program-spec.md](/Users/jamiecraik/dev/Agent-Skills/Docs/specs/2026-03-24-feat-skill-lifecycle-scaffold-memory-program-spec.md)

**Test scenarios:**
- lifecycle representation is documented once and does not conflict with any derived view
- repo-facing docs expose lifecycle and ownership expectations clearly enough for scaffold and validation phases to reuse

**Verification:**
- authoritative metadata representation is explicit
- no split-brain representation remains unresolved
- downstream phases can identify exactly where to read lifecycle truth
- packaged-skill inheritance is explicit enough for validators and migration work to inspect
- `docs/solutions/` minimum evidence rules are documented once and reused downstream

**Exit criteria:**
- planning source of truth for representation choice exists
- downstream phases can reference one authoritative metadata shape
- readiness outcomes for representation conflicts are documented as `degraded` or `blocked`

- [ ] **P1 / Scaffold Generators Adopt Lifecycle-Aware Realism-First Output**

**Goal:** Update the skill and plugin scaffold generators so new managed assets capture required lifecycle data and no longer default to broad false-green placeholder debt.

**Requirements:** R2, R4

**Dependencies:** P0

**Files:**
- Modify: `Skills/skill-builder/Infrastructure/scripts/init_skill.py`
- Modify: `Skills/skill-builder/workflows/create-new-skill.md`
- Modify: `Skills/plugin-creator/Infrastructure/scripts/create_basic_plugin.py`
- Modify: `Skills/skill-creator/Infrastructure/scripts/init_skill.py`
- Modify: `Infrastructure/templates/SKILL.md.template`
- Modify: `Skills/plugin-creator/Infrastructure/references/plugin-json-spec.md`
- Create: `Infrastructure/scripts/testing/test_skill_creator_lifecycle_scaffold.py`
- Create: `Infrastructure/scripts/testing/test_plugin_creator_lifecycle_scaffold.py`
- Test: `Infrastructure/scripts/testing/test_skill_creator_lifecycle_scaffold.py`
- Test: `Infrastructure/scripts/testing/test_plugin_creator_lifecycle_scaffold.py`

**Approach:**
- capture required lifecycle fields at creation time or fail/warn clearly
- replace broad placeholder debt with narrower required fields and realism-first starter content
- keep generator outputs aligned with the chosen authoritative metadata representation
- treat `Skills/skill-builder/Infrastructure/scripts/init_skill.py` as the canonical skill scaffold surface and keep `Skills/skill-creator/Infrastructure/scripts/init_skill.py` as a compatibility wrapper rather than a second drifting implementation

**Execution note:** test-first

**Patterns to follow:**
- [init_skill.py](/Users/jamiecraik/dev/Agent-Skills/skill-builder/Infrastructure/scripts/init_skill.py)
- [create_basic_plugin.py](/Users/jamiecraik/dev/Agent-Skills/plugin-creator/Infrastructure/scripts/create_basic_plugin.py)

**Test harness note:** New scaffold tests should follow the repo's existing `Infrastructure/scripts/test_*.py` pattern and be runnable through the validation surface selected in `P2`.

**Test scenarios:**
- skill scaffold fails or warns when required lifecycle fields are absent
- plugin scaffold does not emit merge-looking placeholder content for required governance fields
- generated outputs reflect the chosen lifecycle vocabulary consistently

**Verification:**
- scaffold outputs no longer create false-green governed assets by default
- new tests cover both happy-path and missing-metadata behavior

**Exit criteria:**
- generators can produce governed starter assets without broad placeholder debt
- false-green generation prevention is testable and observable

- [ ] **P2 / Validation and Diagnostics Enforce Degraded-State Semantics**

**Goal:** Extend repo-native validation or diagnostics so missing ownership, stale cadence, representation conflicts, and false-green scaffold outputs become explicit degraded or blocked states.

**Requirements:** R1, R2, R4

**Dependencies:** P0, P1

**Files:**
- Modify: `Infrastructure/scripts/lifecycle-and-sync/diagnose_skill.py`
- Modify: `Infrastructure/scripts/validate_all.sh`
- Modify: `Infrastructure/scripts/validation-and-linting/verify_skill_catalog_freshness.py`
- Create: `Infrastructure/scripts/testing/test_skill_lifecycle_validation.py`
- Test: `Infrastructure/scripts/testing/test_skill_lifecycle_validation.py`
- Test: `Infrastructure/scripts/validate_all.sh`

**Approach:**
- choose the narrowest existing validation surfaces that can carry lifecycle-readiness checks
- distinguish `healthy`, `degraded`, and `blocked` outcomes where the spec requires it
- make any representation or ownership failures attributable to a concrete violated invariant

**Validation targets:**
- lifecycle representation integrity
- ownership presence
- review-cadence presence and overdue detection
- false-green scaffold output detection
- solution-entry linkage and freshness checks where applicable

**Execution note:** characterization-first

**Patterns to follow:**
- [validate_all.sh](/Users/jamiecraik/dev/Agent-Skills/Infrastructure/scripts/validate_all.sh)
- [verify_skill_catalog_freshness.py](/Users/jamiecraik/dev/Agent-Skills/Infrastructure/scripts/validation-and-linting/verify_skill_catalog_freshness.py)

**Test harness note:** New validation tests should remain in the `Infrastructure/scripts/test_*.py` family and be wired into the chosen repo-native validation path rather than creating a parallel runner.

**Test scenarios:**
- missing owner is reported as degraded or blocked rather than silently ignored
- split-brain metadata is attributed to the authoritative representation rule
- stale review cadence is observable

**Verification:**
- lifecycle-readiness failures are actionable and map back to the spec failure classes
- validation output makes it obvious whether execution may proceed, proceed with caution, or must stop

**Exit criteria:**
- validation can surface the spec’s degraded-state classes explicitly
- readiness semantics are no longer implicit
- at least one validator or diagnostic path can explain why an asset is `healthy`, `degraded`, or `blocked`

- [ ] **P3 / Governed docs/solutions Layer and Entry Contract**

**Goal:** Create `docs/solutions/` and establish a governed reusable-solution entry contract linked back to managed assets and maintenance context.

**Requirements:** R3, R4

**Dependencies:** P0

**Files:**
- Create: `docs/solutions/`
- Create: `docs/solutions/README.md`
- Create: `docs/solutions/solution-entry-template.md`
- Modify: `README.md`
- Modify: `docs/index.md`
- Test: `Infrastructure/scripts/validation-and-linting/docs_lint.py`

**Approach:**
- define what belongs in `docs/solutions/` and what does not
- require asset linkage, ownership context, evidence/source reference, and freshness metadata
- keep the initial shape lightweight enough to preserve signal

**Execution note:** characterization-first

**Patterns to follow:**
- [2026-03-24-feat-skill-lifecycle-scaffold-memory-program-spec.md](/Users/jamiecraik/dev/Agent-Skills/Docs/specs/2026-03-24-feat-skill-lifecycle-scaffold-memory-program-spec.md)
- [docs/index.md](/Users/jamiecraik/dev/Agent-Skills/docs/index.md)

**Test scenarios:**
- a valid solution entry includes required linkage and maintenance context
- an execution-log-style note clearly fails the admission rule

**Verification:**
- `docs/solutions/` exists with explicit governed entry criteria and does not read like a generic notes folder

**Exit criteria:**
- reusable-solution entry contract exists
- folder-level ownership/linkage expectations are explicit

- [ ] **P4 / Portfolio Adoption and Seed Migration**

**Goal:** Apply the lifecycle contract to the initial in-scope asset set and seed the first governed solution entries without expanding beyond phase-one scope.

**Requirements:** R1, R3, R5

**Dependencies:** P1, P2, P3

**Files:**
- Modify: `Skills/coding-harness/SKILL.md`
- Modify: `Skills/skill-builder/SKILL.md`
- Modify: `Plugins/compound-engineering-router/.codex-plugin/plugin.json`
- Create: `docs/solutions/2026-03-24-skill-scaffold-false-green-prevention.md`
- Create: `docs/solutions/2026-03-24-lifecycle-metadata-representation-decision.md`
- Test: `Infrastructure/scripts/lifecycle-and-sync/diagnose_skill.py`
- Test: `Infrastructure/scripts/validation-and-linting/verify_skill_catalog_freshness.py`

**Approach:**
- choose a bounded seed set of canonical skills, packaged skills, and plugin packages representative enough to prove the phase-one model
- apply the lifecycle contract without forcing immediate repo-wide migration
- create at least two high-signal solution entries that demonstrate the new layer’s intended use
- use the packaged-skill proof target recorded by `P0` rather than letting `P4` choose a different packaged representation ad hoc

**Seed-set rule:**
- select the smallest representative set that proves:
  - one canonical skill
  - one packaged skill
  - one plugin package
- do not broaden the seed set within the same pass unless a chosen seed is shown to be structurally unrepresentative
- record why each selected seed was chosen so later expansion can compare against the original proof-of-shape baseline
- the packaged-skill proof is not complete until the exact artifact or path named by `P0` demonstrates the chosen representation or inheritance rule in a way validators can inspect

**Execution note:** external-delegate optional

**Patterns to follow:**
- [Skills/coding-harness/SKILL.md](/Users/jamiecraik/dev/Agent-Skills/coding-harness/SKILL.md)
- [Skills/skill-builder/SKILL.md](/Users/jamiecraik/dev/Agent-Skills/skill-builder/SKILL.md)
- [plugin-contract.md](/Users/jamiecraik/dev/Agent-Skills/Plugins/compound-engineering-router/Infrastructure/references/plugin-contract.md)

**Test scenarios:**
- seeded assets expose lifecycle state, owner, maturity, and review cadence in the chosen representation
- seeded solution entries link back to governed assets and include freshness markers
- non-seeded assets remain out of scope without being mislabeled as migrated

**Verification:**
- phase-one adoption is proven on a bounded seed set
- the repo remains within the scope promised by the spec
- each seeded asset demonstrates a different phase-one asset category or a justified substitute when one category is unavailable
- the packaged-skill category is proven through the concrete proof target fixed by `P0`, not by a looser substitute chosen during migration

**Exit criteria:**
- representative in-scope assets use the new contract successfully
- `docs/solutions/` contains at least two valid entries
- migration remains demonstrably bounded and explainable

- [ ] **P5 / Final Validation, Rollout Note, and Handoff Readiness**

**Goal:** Confirm the program is ready for broader execution or issue handoff without expanding into second-order surfaces.

**Requirements:** R1, R2, R3, R4, R5

**Dependencies:** P2, P3, P4

**Files:**
- Modify: `Docs/plans/2026-03-24-feat-skill-lifecycle-scaffold-memory-program-plan.md`
- Modify: `Docs/specs/2026-03-24-feat-skill-lifecycle-scaffold-memory-program-spec.md`
- Test: `Infrastructure/scripts/validate_all.sh`
- Test: `Infrastructure/scripts/validation-and-linting/verify_skill_catalog_freshness.py`
- Test: `Infrastructure/scripts/validation-and-linting/docs_lint.py`

**Approach:**
- run the broad repo checks chosen in prior phases
- record any residual degraded states or rollout holds explicitly
- update plan evidence so handoff to `ce-work` or `[[linear]]` is based on current validation reality

**Rollout hold rules:**
- hold broader adoption if the authoritative representation is still contested
- hold broader adoption if any seeded asset is `blocked`
- allow cautious continuation only when residual issues are explicitly `degraded`, scoped, and documented with an owner and follow-up path
- do not treat missing `docs/solutions/` freshness or orphaned-link detection as a documentation-only follow-up

**Execution note:** characterization-first

**Patterns to follow:**
- [2026-03-10-feat-learning-preserving-skill-design-plan.md](/Users/jamiecraik/dev/Agent-Skills/Docs/plans/2026-03-10-feat-learning-preserving-skill-design-plan.md)

**Test scenarios:**
- all planned validation surfaces still agree on lifecycle-readiness outcomes
- no second-order dashboard or wrapper work slipped into the delivery path

**Verification:**
- final evidence path is current and execution-ready
- rollout posture is recorded as `healthy`, `degraded`, or `blocked` with explicit reasons

**Exit criteria:**
- residual blockers are explicit
- plan is ready for `ce-work` or tracker handoff
- any non-healthy rollout state has a named owner and mitigation note

## Task Graph (id / depends_on)

```yaml
tasks:
  - id: P0
    title: Materialize lifecycle control-plane baseline in docs and validation guidance
    depends_on: []
  - id: P1
    title: Update skill and plugin scaffold generators plus regression tests
    depends_on: [P0]
  - id: P2
    title: Extend validation and diagnostics with lifecycle readiness semantics
    depends_on: [P0, P1]
  - id: P3
    title: Create governed docs/solutions entry contract
    depends_on: [P0]
  - id: P4
    title: Apply bounded seed adoption across canonical, packaged, and plugin proof targets
    depends_on: [P1, P2, P3]
  - id: P5
    title: Record final validation evidence and rollout posture
    depends_on: [P2, P3, P4]
```

## System-Wide Impact

- **Interaction graph:** touches skill and plugin creation, catalog freshness, diagnostics, repo docs, and future reusable-solution documentation.
- **Error propagation:** lifecycle-readiness failures should surface through diagnostics and validation rather than hiding in generated content.
- **State lifecycle risks:** split-brain metadata, stale review cadence, false-green generation, and orphaned solution entries are the primary state risks.
- **API surface parity:** canonical skills, packaged skills, and plugin packages must share the same lifecycle vocabulary even if represented differently.
- **Integration coverage:** repo-wide validation plus representative seed migration is needed; unit tests alone will not prove the control plane is coherent.

## Risks & Dependencies

- Choosing the wrong authoritative metadata representation would force rework across all later phases.
- Over-tightening scaffold requirements too early could make generators painful to use if required fields are not collected ergonomically.
- `docs/solutions/` can become clutter quickly if admission criteria are weak or freshness expectations are omitted.
- Seed migration must remain bounded; converting too much of the repo during proof-of-shape would violate the governing spec.
- Validation drift is a real risk: if diagnostics, catalog checks, and docs interpret readiness differently, the plan can produce false confidence.

Mitigations:
- treat the representation decision as a hard exit gate for `P0`
- keep the seed set intentionally minimal and justified in writing
- require rollout posture language in `P5` instead of informal success claims
- prefer one validation surface to classify readiness and let others consume or echo that classification

## Documentation / Operational Notes

- Update repo-facing documentation only where it materially changes contributor behavior.
- Keep rollout notes explicit about phase-one scope and any residual degraded states.
- If tracker handoff is desired later, use this plan as the canonical issue body rather than rewriting scope in a separate system.

Evidence paths to keep synchronized:
- governing spec: `Docs/specs/2026-03-24-feat-skill-lifecycle-scaffold-memory-program-spec.md`
- lifecycle/readiness plan: this document
- scaffold surfaces: `Skills/skill-builder/Infrastructure/scripts/init_skill.py`, `Skills/skill-creator/Infrastructure/scripts/init_skill.py`, `Skills/plugin-creator/Infrastructure/scripts/create_basic_plugin.py`
- validation surfaces: repo-native validator/diagnostic files chosen in `P2`
- reusable-memory layer: `docs/solutions/README.md` and seeded `docs/solutions/*.md`

## Execution Ledger (Planning Mode)

STEP_ID | status | owner | evidence
P0 | completed | Codex | Lifecycle baseline documented in `docs/reference/managed-asset-lifecycle.md`; targeted checks passed via `python3 Infrastructure/scripts/validation-and-linting/docs_lint.py --mode warn --config Infrastructure/docs-policy.json` and `python3 Infrastructure/scripts/validation-and-linting/verify_skill_catalog_freshness.py --strict`
P1 | completed | Codex | Canonical scaffold updated in `Skills/skill-builder/Infrastructure/scripts/init_skill.py`; plugin scaffold updated in `Skills/plugin-creator/Infrastructure/scripts/create_basic_plugin.py`; regression tests passed via `python3 Infrastructure/scripts/testing/test_skill_creator_lifecycle_scaffold.py` and `python3 Infrastructure/scripts/testing/test_plugin_creator_lifecycle_scaffold.py`
P2 | completed | Codex | Lifecycle readiness classification landed in `Infrastructure/scripts/validation-and-linting/verify_skill_catalog_freshness.py` and `Infrastructure/scripts/lifecycle-and-sync/diagnose_skill.py`; regression coverage passed via `python3 Infrastructure/scripts/testing/test_skill_lifecycle_validation.py`
P3 | completed | Codex | Governed `docs/solutions/` layer created with README, template, and validation-aligned frontmatter contract
P4 | completed | Codex | Seeded lifecycle metadata on `Skills/skill-builder/SKILL.md`, `Skills/coding-harness/SKILL.md`, `product/Infrastructure/ops/compound-engineering-router/SKILL.md`, and `Plugins/compound-engineering-router/.codex-plugin/plugin.json`; added two governed solution entries
P5 | in_progress | Codex | Targeted final evidence passed via `python3 Infrastructure/scripts/validation-and-linting/verify_skill_catalog_freshness.py --strict`, `python3 Infrastructure/scripts/validation-and-linting/docs_lint.py --mode warn --config Infrastructure/docs-policy.json`, and `python3 Infrastructure/scripts/lifecycle-and-sync/diagnose_skill.py compound-engineering-router`; one broad `bash Infrastructure/scripts/validate_all.sh` run surfaced schema-placement and missing task-graph issues, both were fixed, and the exact rerun was then blocked by sandbox policy before a fresh all-green capture could be recorded

## Acceptance Checklist

- [x] AC1. `P0` defines one authoritative lifecycle-metadata representation and keeps any derived views subordinate.
Traceability: `SA1`, `SA3`, `SA10`
- [x] AC2. `P1` updates skill and plugin scaffolds so governed assets no longer default to broad false-green placeholder outputs.
Traceability: `SA4`, `SA7`, `SA9`
- [x] AC3. `P2` makes degraded-state and readiness semantics observable through repo-native validation or diagnostics.
Traceability: `SA6`, `SA7`, `SA8`, `SA9`
- [x] AC4. `P3` creates `docs/solutions/` with explicit admission, linkage, ownership, and freshness rules.
Traceability: `SA5`, `SA11`
- [x] AC5. `P4` proves the phase-one model on a bounded seed set spanning canonical skills, packaged skills, and plugin packages.
Traceability: `SA2`, `SA3`, `SA5`
- [ ] AC6. `P5` records current evidence, residual blockers, and rollout posture without widening scope into dashboards or wrappers.
Traceability: `SA6`, `SA8`

## Sources & References

- [Skill lifecycle brainstorm](/Users/jamiecraik/dev/Agent-Skills/docs/brainstorms/2026-03-24-skill-lifecycle-scaffold-memory-program-brainstorm.md)
- [Skill lifecycle spec](/Users/jamiecraik/dev/Agent-Skills/Docs/specs/2026-03-24-feat-skill-lifecycle-scaffold-memory-program-spec.md)
- [Learning-preserving delivery plan](/Users/jamiecraik/dev/Agent-Skills/Docs/plans/2026-03-10-feat-learning-preserving-skill-design-plan.md)
- [Skill creator scaffold](/Users/jamiecraik/dev/Agent-Skills/skill-creator/Infrastructure/scripts/init_skill.py)
- [Plugin creator scaffold](/Users/jamiecraik/dev/Agent-Skills/plugin-creator/Infrastructure/scripts/create_basic_plugin.py)
- [Governance exceptions register](/Users/jamiecraik/dev/Agent-Skills/GOVERNANCE/exceptions.md)
