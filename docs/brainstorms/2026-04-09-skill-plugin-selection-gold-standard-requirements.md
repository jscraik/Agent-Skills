---
title: Skill and Plugin Selection Gold-Standard Upgrade
date: 2026-04-09
status: draft
spec_required: lite
risk_level: medium
complexity: large
schema_version: 1
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

Live repository checks also show trust-eroding catalog drift across discovery surfaces:

- `README.md` reports 129 skills.
- `SKILL.md` reports 116 skills.
- `ask skills list --json` currently returns 103 skills.
- `ask skills route ...` currently reports `considered_total: 116`.

This mismatch makes both humans and agents uncertain about which surface is authoritative.

Current state therefore has four maturity gaps that prevent a gold-standard, future-proof selection experience:

1. Routing capability exists but is not first-class in the main `ask` UX.
2. Discovery policy lives in multiple places, creating drift risk.
3. Plugin lifecycle UX is install-heavy and lacks state visibility as a primary workflow.
4. Onboarding and intent-to-skill ergonomics are too heavy for new or occasional operators.

The goal is to raise selection correctness, explainability, and governance durability without forcing
premature complexity in wave 1.

## Pressure Test

- Is this solving the right problem? Yes. Selection misses and ambiguous routing are direct productivity tax.
- What if we do nothing? Existing behavior remains functional but inconsistent under ambiguity, and drift risk grows.
- Are we duplicating existing work? No. This is consolidation and operationalization of existing router/discovery assets.
- Is there a higher-leverage framing? Yes. Treat this as a trust-and-intent product surface, not isolated script upgrades.
- Is there a lower-complexity alternative? Yes. Keep wave-1 read-only and prioritize catalog parity plus intent entrypoint before lifecycle mutation.

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
commands (`list/status/doctor`) with explainable outputs, deterministic fixtures, and explicit trust/parity checks.

Pros:

- Addresses the core failure modes together
- Improves trust through explainable decisions
- Closes catalog-truth ambiguity across docs and CLI surfaces
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
- R4. `ask` must expose a first-class intent entrypoint for non-expert users that returns:
  one recommended skill, two viable alternatives, and concise disambiguation prompts.

### Discovery Governance

- R5. Skill discovery allowlist/precedence policy must be defined in one shared source and consumed by
  all relevant discovery/sync flows.
- R6. Discovery behavior must preserve canonical precedence and dedupe semantics, with regression fixtures
  to prevent policy drift.
- R7. All catalog-facing surfaces (`README` counters, root `SKILL.md`, `ask skills list`, and routing
  considered-set metadata) must derive counts from the same canonical manifest and fail validation on mismatch.
- R8. `ask` must provide an explicit catalog parity diagnostic command that reports:
  canonical count, per-surface observed counts, policy identity, and blocking drift reason.

### Plugin State Visibility (Wave 1)

- R9. `ask plugins` must provide read-only state visibility commands for `list`, `status`, and `doctor`.
- R10. Plugin state outputs must separate installed metadata from enabled/active repository state to support
  future migrations safely.
- R11. Wave 1 must not require mutation commands; mutation support is explicitly deferred.

### Determinism and Auditability

- R12. Selection behavior must be covered by deterministic fixture-based tests in CI, including ambiguity,
  precedence, and explainability assertions.
- R13. Validation output must include a routing-quality artifact suitable for trend comparison across runs.
- R14. Routing-quality artifacts must include unresolved ambiguity rate, no-candidate rate, and top rejection reasons.

### Onboarding and Operator Ergonomics

- R15. `ask` must provide a starter-oriented discovery mode that prioritizes high-signal, stable skills
  by task archetype instead of presenting full catalog breadth by default.
- R16. Documentation must include a "5-minute success path" that gets a new operator from zero to one
  validated useful outcome with minimal policy overhead.
- R17. CLI entrypoint responsibilities must remain modular enough that topic/action expansion does not
  require a single growing monolithic dispatcher.

## Success Criteria

- Routing invocation from `ask` is available and documented with a stable output contract.
- Intent entrypoint exists and returns one recommendation plus alternatives with disambiguation guidance.
- Identical inputs under identical catalog state produce identical ranked selections.
- Discovery policy changes in one location propagate consistently to all discovery/sync paths.
- Catalog counts remain parity-locked across `README`, `SKILL.md`, `skills list`, and routing metadata.
- Catalog parity diagnostics clearly identify source-of-truth and drift causes in one command.
- `ask plugins list/status/doctor` provide actionable plugin-state visibility without mutation.
- CI fails when fixture-based selection contracts regress.
- Validation artifacts show routing confidence/exclusion details and unresolved-ambiguity trends suitable for audit.
- Starter workflow adoption path is documented and usable without reading deep governance docs first.

## Scope Boundaries

In scope:

- Selection UX and decision explainability for skills/plugins
- Discovery policy unification
- Catalog parity diagnostics and source-of-truth enforcement
- Intent-oriented entrypoint and starter discovery surface
- Read-only plugin lifecycle visibility
- Deterministic selection contract validation

Out of scope:

- Full plugin mutation lifecycle (`enable/disable/refresh`) in wave 1
- New plugin packaging architecture
- Non-selection feature work unrelated to routing/discovery/plugin-state quality
- Automated retirement/pruning of legacy skills unrelated to current selection trust gaps

## Key Decisions

- Wave-1 plugin lifecycle scope is read-only (`list/status/doctor`) to reduce rollout risk.
- Selection quality is treated as a product contract, not only an internal script behavior.
- Catalog count parity is a hard trust gate, not a soft reporting mismatch.
- Intent-first entrypoint and starter mode are required to reduce operator cognitive load.
- Deterministic auditability is required before adding mutation-heavy lifecycle controls.

## Dependencies and Assumptions

- Existing router internals are reused as the baseline rather than replaced.
- Existing sync/discovery tooling remains the transport layer, with policy centralized.
- Repository CI can host frozen selection fixtures and fail-fast regression checks.
- Existing docs and generated indexes can be updated to consume one canonical manifest source.

## Outstanding Questions

### Resolve Before Planning

None. Scope, direction, and phase boundaries are sufficiently clear for planning.

### Deferred to Planning

- Exact command shape and output schema details for `ask skills route`.
- Exact command shape and output schema details for intent entrypoint and catalog parity diagnostics.
- Artifact format and location for routing-quality trend output in validation.
- Starter-mode ranking heuristics and default archetype taxonomy.
- Exact migration strategy for introducing mutating plugin commands after wave 1.

## Next Steps

Recommended next stage: **`ce-spec`**.

Spec work should lock the contract details needed before planning:

1. Route command input/output schema and explainability fields
2. Intent entrypoint schema plus starter-mode behavior contract
3. Shared discovery policy interface, canonical manifest contract, and parity diagnostics
4. Read-only plugin state model and visibility semantics
5. Selection regression fixture contract and routing-quality artifact format
