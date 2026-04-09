---
title: Skill and Plugin Selection Gold-Standard Upgrade
date: 2026-04-09
status: draft
spec_required: lite
risk_level: medium
complexity: large
---

# Skill and Plugin Selection Gold-Standard Upgrade

## Table of Contents

- [Problem Frame](#problem-frame)
- [Pressure Test](#pressure-test)
- [Approaches](#approaches)
- [Recommendation](#recommendation)
- [Requirements](#requirements)
- [Success Criteria](#success-criteria)
- [Scope Boundaries](#scope-boundaries)
- [Key Decisions](#key-decisions)
- [Dependencies and Assumptions](#dependencies-and-assumptions)
- [Outstanding Questions](#outstanding-questions)
- [Next Steps](#next-steps)

## Problem Frame

`agent-skills` has strong foundations for deterministic skill routing, catalog sync, and plugin packaging,
but user-facing selection quality still depends on scattered entry points and duplicated policy definitions.

Recent cross-repo analysis of `~/dev/codex` and `~/dev/claude-code` shows three maturity gaps in
`agent-skills` that prevent a gold-standard, future-proof selection experience:

1. Routing capability exists but is not first-class in the main `ask` UX.
2. Discovery policy lives in multiple places, creating drift risk.
3. Plugin lifecycle UX is install-heavy and lacks state visibility as a primary workflow.

The goal is to raise selection correctness, explainability, and governance durability without forcing
premature complexity in wave 1.

## Pressure Test

- Is this solving the right problem? Yes. Selection misses and ambiguous routing are direct productivity tax.
- What if we do nothing? Existing behavior remains functional but inconsistent under ambiguity, and drift risk grows.
- Are we duplicating existing work? No. This is consolidation and operationalization of existing router/discovery assets.
- Is there a higher-leverage framing? Yes. Treat this as a selection-governance product surface, not isolated script upgrades.

## Approaches

### A. Router-first hardening (minimal scope)

Promote routing as a first-class `ask` command and add deterministic contract tests, while deferring
plugin lifecycle UX and discovery-policy consolidation.

Pros:

- Fastest path to immediate routing gains
- Lowest short-term implementation risk

Cons:

- Leaves discovery drift risk unresolved
- Leaves plugin state observability below gold-standard

Best fit:

- Urgent short-window improvement where only routing accuracy matters.

### B. Selection platform baseline (recommended)

Deliver one cohesive baseline across routing UX, unified discovery policy, and read-only plugin state
commands (`list/status/doctor`) with explainable outputs and deterministic fixtures.

Pros:

- Addresses the core failure modes together
- Improves trust through explainable decisions
- Creates strong base for future mutating plugin operations

Cons:

- Broader than router-only
- Requires cross-module coordination and regression fixtures

Best fit:

- Medium-term quality upgrade targeting durable operational confidence.

### C. Full lifecycle immediately (high upside, higher risk)

Ship router UX, unified discovery policy, and full plugin lifecycle state mutation (`enable/disable/refresh`)
in the same wave.

Pros:

- Maximum capability delivered early
- Fewer follow-on handoffs

Cons:

- Higher migration and operational risk
- Harder to isolate root cause if issues appear

Best fit:

- Teams willing to absorb higher rollout risk for faster feature completeness.

## Recommendation

Choose **Approach B**.

It captures the highest-leverage improvements now while preserving low-regret extension paths. This aligns
with the selected wave-1 scope decision: **read-only plugin state first**, then mutating operations in a
follow-on wave after baseline correctness and observability are proven.

## Requirements

### Routing Contract

- R1. `ask` must expose a first-class routing entry point that accepts a freeform request and returns
  ranked candidates, confidence, and rationale in a stable machine-readable contract.
- R2. Routing output must include explicit exclusion/conflict reasons when skills/plugins are rejected.
- R3. Ambiguous naming cases (skill vs plugin/app slug collisions) must produce deterministic outcomes,
  never silent nondeterministic selection.

### Discovery Governance

- R4. Skill discovery allowlist/precedence policy must be defined in one shared source and consumed by
  all relevant discovery/sync flows.
- R5. Discovery behavior must preserve canonical precedence and dedupe semantics, with regression fixtures
  to prevent policy drift.

### Plugin State Visibility (Wave 1)

- R6. `ask plugins` must provide read-only state visibility commands for `list`, `status`, and `doctor`.
- R7. Plugin state outputs must separate installed metadata from enabled/active repository state to support
  future migrations safely.
- R8. Wave 1 must not require mutation commands; mutation support is explicitly deferred.

### Determinism and Auditability

- R9. Selection behavior must be covered by deterministic fixture-based tests in CI, including ambiguity,
  precedence, and explainability assertions.
- R10. Validation output must include a routing-quality artifact suitable for trend comparison across runs.

## Success Criteria

- Routing invocation from `ask` is available and documented with a stable output contract.
- Identical inputs under identical catalog state produce identical ranked selections.
- Discovery policy changes in one location propagate consistently to all discovery/sync paths.
- `ask plugins list/status/doctor` provide actionable plugin-state visibility without mutation.
- CI fails when fixture-based selection contracts regress.
- Validation artifacts show routing confidence/exclusion details suitable for audit.

## Scope Boundaries

In scope:

- Selection UX and decision explainability for skills/plugins
- Discovery policy unification
- Read-only plugin lifecycle visibility
- Deterministic selection contract validation

Out of scope:

- Full plugin mutation lifecycle (`enable/disable/refresh`) in wave 1
- New plugin packaging architecture
- Non-selection feature work unrelated to routing/discovery/plugin-state quality

## Key Decisions

- Wave-1 plugin lifecycle scope is read-only (`list/status/doctor`) to reduce rollout risk.
- Selection quality is treated as a product contract, not only an internal script behavior.
- Deterministic auditability is required before adding mutation-heavy lifecycle controls.

## Dependencies and Assumptions

- Existing router internals are reused as the baseline rather than replaced.
- Existing sync/discovery tooling remains the transport layer, with policy centralized.
- Repository CI can host frozen selection fixtures and fail-fast regression checks.

## Outstanding Questions

### Resolve Before Planning

None. Scope, direction, and phase boundaries are sufficiently clear for planning.

### Deferred to Planning

- Exact command shape and output schema details for `ask skills route`.
- Artifact format and location for routing-quality trend output in validation.
- Exact migration strategy for introducing mutating plugin commands after wave 1.

## Next Steps

Recommended next stage: **`ce-spec`**.

Spec work should lock the contract details needed before planning:

1. Route command input/output schema and explainability fields
2. Shared discovery policy interface and precedence contract
3. Read-only plugin state model and visibility semantics
4. Selection regression fixture contract and routing-quality artifact format

---

schema_version: 1
