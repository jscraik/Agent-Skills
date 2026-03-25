---
title: Skill Lifecycle, Scaffold Quality, and Institutional Memory Program
type: feat
status: draft
date: 2026-03-24
origin: docs/brainstorms/2026-03-24-skill-lifecycle-scaffold-memory-program-brainstorm.md
risk: medium
spec_depth: lite
ui_required: false
deepened: 2026-03-24
---

# Skill Lifecycle, Scaffold Quality, and Institutional Memory Program Spec

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
- [Resolved Phase-One Defaults](#resolved-phase-one-defaults)
- [Definition of Done](#definition-of-done)

## Enhancement Summary

**Deepened on:** 2026-03-24
**Mode:** targeted-confidence
**Key areas improved:** lifecycle transitions, metadata representation boundaries, solution-entry admission rules, degraded-state handling, observability, and readiness gates

- Added explicit phase-one lifecycle transition rules and degraded-state semantics so planning does not have to infer how assets move between states.
- Tightened the metadata and `docs/solutions/` contracts with minimum required fields, admission gates, and ownership-linkage rules grounded in existing repo governance patterns.
- Expanded observability and acceptance coverage so planning can prove readiness without inventing new contract boundaries.

## Problem Statement

`Agent-Skills` is already strong at authoring, syncing, validating, and governing a large multi-runtime skill library, but it lacks a single contract that explains:
- what each skill or related package is in lifecycle terms
- who is responsible for its quality and review posture
- what minimum quality bar newly generated assets must meet
- where durable reusable solutions should live once work is complete

That gap creates three concrete repo problems:
- the current portfolio is broad enough that ownership and maturity are not obvious from the repo surface alone
- scaffold generators still emit placeholder-heavy outputs that normalize downstream cleanup instead of first-run quality
- the repo has brainstorms, plans, todos, and agent memory, but no canonical `docs/solutions/` loop for reusable resolved knowledge

Without a shared contract, later planning would have to invent lifecycle semantics, scaffold expectations, and memory-entry rules ad hoc.

## Goals

- Define a repo-level control-plane contract for lifecycle and ownership metadata across the initial in-scope asset types.
- Define how scaffold generators must relate to that metadata contract.
- Define the role of `docs/solutions/` as the canonical reusable-solution layer for this program.
- Establish the relationships between the three tracks so later planning can sequence them without reopening core direction questions.
- Preserve a narrow enough first-phase scope that the program can move forward without boiling the ocean.

## Non-Goals

- Do not define implementation tasks, rollout sequencing, or file-by-file changes.
- Do not redesign the existing sync, validation, or recursive skill-graph systems in this spec.
- Do not require immediate repo-wide migration of every asset type on day one.
- Do not define a dashboard, operator wrapper, or deprecation workflow as part of the phase-one contract.
- Do not create a dedicated UI contract; this work does not require one at spec stage.

## System Boundary

Owned by this spec:
- the canonical meaning of lifecycle and ownership metadata for the first-phase asset set
- the relationship between lifecycle metadata and scaffold generation
- the role, entry criteria, and linkage rules for `docs/solutions/`
- the minimum cross-track invariants needed before planning can safely sequence work

Not owned by this spec:
- implementation order or execution milestones
- broad repo IA or documentation redesign
- runtime behavior changes in Codex, Claude, or Gemini
- visual UX, design tokens, or interaction-state design
- retrospective reporting surfaces such as dashboards unless a later artifact chooses them explicitly

## Core Domain Model

### Primary entities

- `ManagedAsset`
  - A repo entity governed by this program.
  - Phase-one scope:
    - canonical skills
    - packaged skills
    - plugin packages
  - Explicitly out of phase-one scope unless later planning adds them:
    - general references with no lifecycle significance
    - one-off brainstorm docs
    - transient generated artifacts under `artifacts/`

- `LifecycleState`
  - Canonical lifecycle classification for a `ManagedAsset`.
  - Required values for phase one:
    - `incubating`
    - `active`
    - `maintenance`
    - `deprecated`

- `OwnershipRecord`
  - The canonical statement of who is responsible for a `ManagedAsset`.
  - Must identify one primary accountable maintainer or owner string, even when collaborators also exist.
  - Must be compatible with existing repo governance patterns that already track owner, risk, mitigation, and review date for exceptions and control records.

- `MaturityLevel`
  - Lightweight indication of how proven the asset is.
  - Required values for phase one:
    - `experimental`
    - `validated`
    - `canonical`

- `ReviewCadence`
  - Declared expectation for how often an asset should be re-reviewed or revalidated.
  - The spec does not force one universal interval, but it does require an explicit cadence field or equivalent canonical declaration.
  - A cadence declaration must be concrete enough for later validation to distinguish "missing" from "present but overdue."

- `ScaffoldProfile`
  - The creation-time contract for generators that emit new managed assets.
  - Must capture enough input to produce realistic starter outputs aligned with the lifecycle model instead of generic placeholder debt.
  - Must be able to collect or derive the required lifecycle fields at creation time rather than leaving them to post-generation archaeology.

- `SolutionEntry`
  - A durable reusable record in `docs/solutions/`.
  - Represents a resolved pattern, fix, or reusable lesson that should outlive a single task session.

- `AssetRelationship`
  - A declared link between governed entities.
  - Required relationship types for phase one:
    - `generated_by`
    - `owned_by`
    - `documents`
    - `supersedes`
    - `supported_by_solution`

### Required fields for phase one

Every `ManagedAsset` in scope must have or derive:
- stable identifier or path
- lifecycle state
- ownership record
- maturity level
- review cadence
- declared source-of-truth location for the metadata representation

Phase-one representation rule:
- the authoritative representation is in-file metadata on the canonical managed asset
- for Markdown-governed assets, use frontmatter in the canonical file
- for non-Markdown governed assets such as plugin packages, use the native structured manifest file already treated as canonical for that asset
- sidecar files or derived indexes may exist only as subordinate mechanically derived views
- mixed representations are allowed only when the in-file canonical source remains authoritative and the others are mechanically derived from it

Every `SolutionEntry` must have or derive:
- durable title
- linked managed asset or asset family
- concise problem statement
- concise resolution statement
- evidence or source reference
- maintenance owner or owning asset reference
- last-review or freshness marker suitable for later maintenance checks

## Main Flow / Lifecycle

### 1. Asset definition or discovery

A phase-one managed asset is either:
- created by a scaffold generator
- promoted into lifecycle governance from an existing repo path

At the moment it becomes governed, the asset must acquire the required lifecycle fields.

### 2. Asset creation

If a scaffold creates a new managed asset:
- the scaffold must request or infer the required metadata fields
- the generated output must be realism-first, meaning it should prefer concrete defaults, explicit placeholders that are contractually required, and validator-aligned structure over broad instructional `TODO` blocks
- the scaffold must not emit content that disguises incompleteness as publishable quality
- the scaffold must fail or warn clearly when required lifecycle fields cannot be captured safely

Creation readiness rule:
- a newly generated governed asset must not be treated as `active` by default solely because generation succeeded
- if required metadata is missing, the asset enters a degraded `incubating` state until planning-defined repair steps complete

### 3. Active stewardship

Once governed, the asset enters one of the declared lifecycle states.

Lifecycle semantics:
- `incubating`: early, intentionally unstable, still being shaped
- `active`: supported and expected to meet normal repo quality expectations
- `maintenance`: supported but not a primary innovation target
- `deprecated`: still tracked but marked for replacement, retirement, or non-preferred use

Stewardship expectations:
- ownership is visible
- maturity is visible
- review cadence is visible
- downstream docs or solutions may reference the asset through declared relationships

Phase-one transition rules:
- `incubating -> active`
  - requires required metadata presence, ownership visibility, and passing program-defined readiness validation
- `active -> maintenance`
  - allowed when the asset remains supported but no longer expects active feature growth
- `active -> deprecated`
  - allowed when a replacement, retirement path, or non-preferred status has been explicitly declared
- `maintenance -> active`
  - allowed when the asset re-enters active investment with refreshed review expectations
- `deprecated` is not deletion
  - deprecated assets remain governable until a later workflow explicitly removes or archives them
- any transition that removes ownership, review cadence, or linked maintenance context is invalid

### 4. Solution capture

When work on a governed asset produces a reusable fix or pattern:
- the result may enter `docs/solutions/` only if it generalizes beyond a one-off journal note or transient debugging artifact
- the `SolutionEntry` must link back to the relevant managed asset or asset family
- the solution must not become an orphaned doc with no ownership or maintenance context

Admission gate for `docs/solutions/`:
- the entry must describe a repeatable problem-pattern or reusable solution, not only a single incident narrative
- the entry must point to at least one concrete source artifact such as a spec, plan, review, validation result, task artifact, diff, or governed asset path
- the entry must include enough evidence context to justify why the resolution is trustworthy, not just a bare assertion that it worked
- the entry must identify who curates it, either directly or through the owning asset relationship
- the entry must include a freshness marker and maintenance context that make later review possible
- entries that are useful only as short-lived execution notes belong elsewhere and are out of scope for this layer

### 5. Lifecycle change

Assets may transition between lifecycle states, but the transition must preserve:
- ownership continuity
- traceable state change
- compatibility with related scaffold and solution records

### 6. Degraded state handling

If an asset lacks required metadata, has stale ownership, or links to stale solutions:
- the system enters a degraded governance state rather than silently treating the asset as healthy
- planning and later workflow choices may then decide whether that gap blocks promotion, publishing, or broader rollout

Degraded-state classes for phase one:
- `missing_metadata`
- `stale_review_cadence`
- `unknown_owner`
- `orphaned_solution_link`
- `scaffold_quality_gap`

These degraded states must be observable and must not be silently collapsed into generic warning noise.

## Interfaces and Dependencies

Primary repo dependencies:
- [2026-03-24-skill-lifecycle-scaffold-memory-program-brainstorm.md](/Users/jamiecraik/dev/Agent-Skills/docs/brainstorms/2026-03-24-skill-lifecycle-scaffold-memory-program-brainstorm.md)
- scaffold generators in `skills-system/skill-creator/scripts/init_skill.py` and `skills-system/plugin-creator/scripts/create_basic_plugin.py`
- existing canonical skill and plugin package layouts under `utilities/`, `product/`, `frontend/`, `backend/`, `auth/`, `github/`, and `skills-system/`
- repo governance and validation surfaces described in [README.md](/Users/jamiecraik/dev/Agent-Skills/README.md)

Dependency rules:
- lifecycle metadata must be compatible with current repo authoring patterns and not require a parallel shadow registry unless planning later proves one is necessary
- scaffold profiles must consume the lifecycle contract rather than inventing their own separate vocabulary
- `docs/solutions/` must integrate as a canonical documentation layer, not as an ad hoc note dump
- this program may inform later dashboards, operator wrappers, or retirement workflows, but it does not depend on them in phase one
- packaged skills with a one-to-one canonical source mapping inherit lifecycle metadata from the canonical source skill in phase one
- that inheritance rule must be explicit, inspectable, and lossless enough for governance use
- plugin packages remain directly governed through their canonical manifest rather than inheriting from a separate Markdown skill by default
- if a derived asset cannot inherit required fields safely, it must declare them directly rather than relying on implicit coupling

## Invariants / Safety Requirements

- A managed asset in phase-one scope must never appear governed without an identifiable owner or maintainer field.
- Lifecycle state names must be canonical and reused consistently across the first-phase asset set.
- Scaffold outputs for governed assets must prefer realism-first structures over placeholder-heavy generic templates.
- `docs/solutions/` entries must only capture reusable resolved knowledge, not transient scratch notes or execution logs.
- A solution entry must remain linked to an owning asset, asset family, or explicit maintenance owner.
- The three tracks must remain one coordinated program; planning must not treat them as disconnected initiatives with conflicting vocabularies.
- This spec must remain system-contract only. No implementation-specific task sequencing belongs here.
- No lifecycle transition may silently elevate an asset into a healthier state than its observable metadata quality justifies.
- Derived metadata must not contradict the authoritative source representation for the same asset.

## Failure Model and Recovery

### Failure classes

- `metadata_ceremony_without_use`
  - Lifecycle fields exist, but nothing in the repo uses them meaningfully.

- `scaffold_contract_drift`
  - Generators continue emitting placeholder debt or invent lifecycle semantics inconsistent with the spec.

- `orphaned_solution_entries`
  - `docs/solutions/` grows entries that lack ownership, asset links, or maintenance context.

- `scope_bloat`
  - The program expands into dashboards, wrappers, retirement flows, and reporting layers before the core contract is stable.

- `migration_overreach`
  - Planning attempts repo-wide retrofitting of every possible asset type before the phase-one scope is proven.

- `representation_split_brain`
  - two metadata representations disagree about the same asset's owner, lifecycle state, or review cadence.

- `false_green_generation`
  - a scaffolded asset looks complete enough to merge or promote even though required governance data is absent or placeholder-derived.

### Recovery rules

- On `metadata_ceremony_without_use`
  - treat the metadata contract as incomplete
  - require planning to connect fields to at least one real lifecycle, scaffold, or solution workflow

- On `scaffold_contract_drift`
  - treat the lifecycle contract as authoritative
  - realign scaffold expectations before expanding generator coverage

- On `orphaned_solution_entries`
  - downgrade the affected entries to invalid program artifacts until ownership and linkage are repaired

- On `scope_bloat`
  - return to phase-one contract boundaries and defer second-order surfaces to later artifacts

- On `migration_overreach`
  - reduce back to the explicit in-scope asset types and sequence broader adoption only after first-phase validation

- On `representation_split_brain`
  - treat the declared authoritative representation as correct
  - mark derived views stale until regeneration or repair completes

- On `false_green_generation`
  - classify the generated asset as degraded rather than healthy
  - require explicit remediation before active-state or promotion-style workflows can treat it as ready

## Observability

Minimum observability for this program:

- `managed_asset_coverage`
  - share of phase-one assets carrying the required lifecycle fields

- `missing_owner_count`
  - count of in-scope assets lacking a valid ownership record

- `lifecycle_state_distribution`
  - distribution of `incubating | active | maintenance | deprecated`

- `scaffold_placeholder_debt_signal`
  - whether scaffold outputs still emit broad unresolved placeholder blocks for governed asset types

- `solution_entry_linkage_ratio`
  - share of `docs/solutions/` entries linked to a governed asset or owning context

- `review_cadence_visibility`
  - whether governed assets expose an explicit review expectation

- `degraded_asset_count`
  - count of in-scope assets currently in one of the defined degraded states

- `false_green_prevention_signal`
  - whether scaffold-generated assets with unresolved required metadata are prevented from being treated as healthy by default

- `solution_freshness_signal`
  - whether solution entries expose a maintenance marker that can distinguish stale knowledge from reviewed knowledge

Observability rules:
- new signals should prefer existing repo-friendly artifact patterns over bespoke reporting systems in phase one
- missing observability is degraded state, not silent success
- measurements should support later planning and validation without requiring a dashboard in this spec
- readiness checks should distinguish `healthy`, `degraded`, and `blocked` rather than collapsing all non-pass outcomes into a single status
- post-planning validation must be able to trace a degraded asset back to the violated invariant or missing field

## Acceptance and Test Matrix

| ID | Area | Requirement | Validation expectation |
| --- | --- | --- | --- |
| SA1 | Mode selection | The artifact is a standard system spec with `spec_depth: lite` and `ui_required: false` | Frontmatter and required sections match the CE spec contract |
| SA2 | Boundary | Phase-one scope is limited to canonical skills, packaged skills, and plugin packages | Planning can identify in-scope assets without inventing broader coverage |
| SA3 | Lifecycle model | The spec defines canonical lifecycle state, ownership, maturity, and review-cadence concepts | Later planning can map these fields into concrete storage and validation points |
| SA4 | Scaffold relationship | The spec defines how scaffold generation must consume the lifecycle contract and avoid placeholder-heavy outputs | Planning can design generator changes without inventing quality goals |
| SA5 | Memory relationship | The spec defines `docs/solutions/` as a reusable-solution layer with ownership and linkage rules | Planning can create the folder and entry contract without reopening brainstorm ambiguity |
| SA6 | Safety | The spec defines invariants for ownership visibility, canonical lifecycle vocabulary, and non-orphaned solution entries | Validation can detect degraded state rather than assuming healthy governance |
| SA7 | Failure handling | The spec names failure classes and recovery expectations for ceremony, drift, orphaning, scope bloat, and migration overreach | Planning can include safeguards without inventing new failure categories |
| SA8 | Observability | The spec defines minimum signals for lifecycle coverage, scaffold quality, and solution linkage | Later validation can prove the program is working without requiring a dashboard first |
| SA9 | Lifecycle readiness | The spec defines valid phase-one lifecycle transitions and degraded-state behavior for missing metadata, unknown ownership, stale review cadence, orphaned solution links, and false-green scaffold outputs | Planning can build readiness checks without inventing lifecycle semantics |
| SA10 | Representation integrity | The spec defines how authoritative versus derived metadata representations must relate, including split-brain recovery expectations | Planning can choose storage shape without inventing conflict policy |
| SA11 | Solution admission | The spec defines minimum admission criteria and freshness expectations for `docs/solutions/` entries | Planning can create the memory layer without turning it into a generic dump |

## Resolved Phase-One Defaults

- Lifecycle metadata uses an in-file authoritative representation in phase one:
  - frontmatter for canonical Markdown-governed assets
  - native structured manifest fields for plugin packages and other non-Markdown governed assets
  - any sidecar or index views remain derived and non-authoritative
- Packaged skills inherit lifecycle metadata from the canonical source skill when a one-to-one mapping exists:
  - inheritance must be explicit and validator-visible
  - if that mapping is absent or lossy, the packaged asset must declare the required lifecycle fields directly
- `docs/solutions/` entries meet the minimum evidence threshold only when they include:
  - a linked governed asset or asset family
  - at least one concrete source artifact
  - a concise problem statement and resolution statement
  - maintenance ownership context
  - a freshness marker suitable for later review

Phase-one planning note:
- The execution plan now fixes a provisional readiness-policy matrix for `incubating` assets so validation and rollout logic can proceed without guessing. `P0` may tighten that matrix during implementation, but it must not silently downgrade a documented `blocked` condition to `degraded`.

## Definition of Done

This spec is done when:
- the phase-one managed asset scope is explicit
- lifecycle, ownership, maturity, and review-cadence concepts are defined clearly enough for planning
- the relationship between lifecycle metadata, scaffold generation, and `docs/solutions/` is explicit
- required invariants, failure modes, and observability signals are recorded
- lifecycle transitions, degraded states, and representation authority rules are explicit enough that planning does not have to invent readiness semantics
- `ce-plan` can use this document without inventing program boundaries or core vocabulary
