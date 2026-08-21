---
title: Skill and Plugin Selection Gold-Standard Specification
type: feat
status: draft
date: 2026-04-09
origin: docs/brainstorms/2026-04-09-skill-plugin-selection-gold-standard-requirements.md
risk: medium
spec_depth: lite
ui_required: false
deepened: 2026-04-09
---

# Skill and Plugin Selection Gold-Standard Specification

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
- [Verification Targets](#verification-targets)
- [Open Questions](#open-questions)
- [Definition of Done](#definition-of-done)

## Enhancement Summary

**Deepened on:** 2026-04-09  
**Mode:** targeted-confidence  
**Key areas improved:** lifecycle precedence, contract versioning, failure determinism, observability gates, acceptance precision

- Added explicit lifecycle decision-precedence and terminal-state rules across route, goal, and catalog diagnostics.
- Added payload schema-version and compatibility expectations so parser/contract evolution is predictable.
- Strengthened observability with hard and soft readiness gates, including breach behavior expectations.
- Tightened acceptance criteria for docs discoverability and CLI modularity verification without relying on ad-hoc command recipes.

## Problem Statement

`agent-skills` already has meaningful routing and governance primitives, but the user-facing trust contract is fragmented across multiple discovery surfaces.

Current observed mismatch on 2026-04-09:

- `README.md` reports 129 skills.
- Root `SKILL.md` reports 116 skills.
- `ask skills list --json` returns 103 skills.
- `ask skills route ...` reports `considered_total: 116`.

This creates a practical trust failure for both humans and coding agents: there is no single answer to "what catalog is real right now," and non-expert users still need high prompt precision to get reliable routing outcomes.

This spec defines the wave-1 contract to make selection explainable, parity-verified, and easier to use through an intent-first entrypoint and starter-oriented discovery posture, while keeping plugin lifecycle operations read-only.

## Goals

- Define a durable skill-routing contract at `ask` with deterministic ranking, explainability, and explicit non-success statuses.
- Enforce one canonical catalog manifest consumed by all count/reporting surfaces.
- Add a first-class catalog parity diagnostic surface that explains drift in one command.
- Add an intent-first entrypoint for non-expert users that returns one recommendation plus alternatives and disambiguation hints.
- Add a starter-mode discovery posture for high-signal stable skills by archetype.
- Preserve read-only plugin lifecycle visibility (`list`, `status`, `doctor`) as wave-1 baseline.
- Keep CLI growth maintainable by separating parsing/dispatch from topic handlers.

## Non-Goals

- Plugin mutation commands (`enable`, `disable`, `refresh`) in wave 1.
- Plugin packaging or installer trust-policy redesign.
- UI surface design work (`ui_required: false`).
- Large-scale skill retirement/pruning unrelated to selection trust/parity.

## System Boundary

Owned by this spec:

- `ask skills route` decision contract and deterministic behavior for skills.
- `ask skills goal` intent-to-skill recommendation contract.
- Canonical catalog manifest contract and parity-locked count projections.
- `ask repo doctor-catalog` diagnostic contract for trust/drift visibility.
- Read-only plugin lifecycle visibility (`ask plugins list|status|doctor`).
- Selection validation artifacts and fail-fast quality gates.
- CLI modularity contract for dispatch growth.

Not owned by this spec:

- Plugin lifecycle mutation workflows.
- Skill content quality policy and authoring standards.
- External app connector behavior.
- Non-selection product features.

## Core Domain Model

- `SelectionRequest`
  - Freeform request text plus optional constraints.
  - Required fields: `request`, `top_k`, `considered_limit`.

- `GoalRequest`
  - User intent request for guided recommendation.
  - Required field: `intent_text`.

- `Candidate`
  - Routeable skill entity in wave 1 (`candidate_type: skill` only).
  - Required fields: `candidate_id`, `candidate_type`, `name`, `path`, `scope_rank`, `canonical_sort_key`, `candidate_state`.

- `SelectionDecision`
  - Deterministic route outcome payload.
  - Required top-level fields: `schema_version`, `request_id`, `policy_identity`, `decision_status`, `failure_class`, `operator_action`, `considered_limit`, `considered_total`, `considered_truncated`, `truncated_count`, `ordering`, `selected_candidates`, `considered_candidates`, `excluded_candidates`.

- `GoalRecommendation`
  - Intent-entrypoint payload.
  - Required fields: `schema_version`, `recommended_candidate`, `alternative_candidates` (exactly 2 when available), `disambiguation_prompts`, `decision_status`, `failure_class`, `operator_action`, `policy_identity`.

- `PluginCandidate` (deferred)
  - Cross-type routing candidate for future waves.
  - Explicitly out of scope for wave-1 route/goal ranking semantics.

- `CatalogManifest`
  - Canonical machine-readable catalog source.
  - Required fields: `manifest_version`, `generated_at`, `policy_identity`, `skills`, `plugins`, `canonical_counts`.

- `CatalogProjection`
  - Surface-specific projection generated from `CatalogManifest`.
  - Required fields: `surface_name`, `observed_count`, `canonical_count`, `parity_ok`, `projection_revision`.

- `CatalogParityReport`
  - Diagnostic payload for trust-state checks.
  - Required fields: `schema_version`, `policy_identity`, `canonical_count`, `surfaces`, `drift_detected`, `drift_class`, `blocking_reason`, `operator_action`.

- `PluginStateSnapshot`
  - Read-only plugin lifecycle state.
  - Required groups: `installed_state`, `activation_state`, `health_state`.

- `RoutingQualityArtifact`
  - Validation artifact for cross-run comparison.
  - Required fields: `run_id`, `policy_identity`, `decision_status_counts`, `unresolved_ambiguity_rate`, `no_candidate_rate`, `top_rejection_reasons`, `explainability_completeness_ratio`, `parity_status`.

## Main Flow / Lifecycle

### A. Route lifecycle (`ask skills route`)

1. Receive `SelectionRequest`.
2. Normalize aliases and request shape to canonical route form before evaluation.
3. Load active `DiscoveryPolicy` and canonical `CatalogManifest` identity.
4. Evaluate blocking parity gates in order:
   - Gate A: policy identity parity
   - Gate B: catalog parity for required surfaces
5. Enumerate eligible skill candidates from canonical projections.
6. Canonically sort candidates by `canonical_sort_key` before truncation.
7. Apply bounded `considered_limit` and retain truncation metadata.
8. Score/rank via router.
9. Build `SelectionDecision` with explicit selected and excluded reasons.
10. Resolve terminal status using deterministic precedence:

- `blocked_policy_drift`
- `blocked_catalog_parity`
- `unresolved_ambiguity`
- `degraded_no_candidates`
- `resolved`

11. Emit decision and quality telemetry.

### B. Intent lifecycle (`ask skills goal`)

1. Receive `GoalRequest` text.
2. Run same underlying routing contract used by `ask skills route`.
3. If route status is `resolved`, select one recommendation plus two alternatives when available.
4. If route status is non-resolved, emit `intent_unresolved` with structured disambiguation prompts.
5. Produce concise disambiguation prompts when confidence is close or constraints are missing.
6. Return `GoalRecommendation` including all required fields: `schema_version`, `recommended_candidate`, `alternative_candidates`, `disambiguation_prompts`, `decision_status`, `failure_class`, `operator_action`, and `policy_identity`.

### C. Catalog trust lifecycle (`ask repo doctor-catalog`)

1. Read canonical counts from `CatalogManifest`.
2. Read projected counts for `README`, root `SKILL.md`, `ask skills list`, and route considered metadata.
3. Compare each surface to canonical counts.
4. Return `CatalogParityReport` including all required fields: `schema_version`, `policy_identity`, `canonical_count`, `surfaces`, `drift_detected`, `drift_class`, `blocking_reason`, and `operator_action`.
5. Emit `blocked_catalog_parity` when any required surface parity fails.
6. Fail validation when any required surface parity fails.

Strict mode semantics (`--strict`):

- Default mode checks required surfaces only (`README`, root `SKILL.md`, `ask skills list`, route considered metadata).
- Strict mode additionally treats missing surface projections and missing per-surface policy identity stamps as blocking drift, not warnings.
- Strict mode escalates soft-gate deterioration signals into blocking catalog diagnostics when deterioration thresholds are breached.
- Strict mode computes soft-gate deterioration only when canonical local routing-quality history exists at `.tmp/agent-skills-artifacts/selection-quality/history.jsonl`. Missing history reports `history_status: "not_collected"` without drift because absent telemetry is unknown, not source failure.
- If collected history contains fewer than eight usable rows, strict mode reports `history_status: "insufficient_history"` as an explicit collecting state without claiming trend health or source drift. Schema-invalid or non-finite values block with `history_status: "schema_invalid_history"`.

### D. Plugin visibility lifecycle (`ask plugins list|status|doctor`)

1. Build `PluginStateSnapshot`.
2. Separate installed metadata from activation state.
3. Run health checks in doctor mode.
4. Surface blockers without mutating state.

Lifecycle ownership rule:

- Route and goal must not mutate catalog or plugin state.
- Catalog diagnostics must not mutate catalog sources.
- Plugin visibility must not mutate plugin activation/install state.
- Canonical manifest/projection ownership is explicit:
  - `Infrastructure/scripts/lifecycle-and-sync/skill_catalog.py` owns canonical catalog manifest derivation.
  - `Infrastructure/scripts/lifecycle-and-sync/sync_skills.sh` owns required projection refresh for root `SKILL.md` and `README.md`.
- Strict trend history ownership is explicit:
  - `.tmp/agent-skills-artifacts/selection-quality/history.jsonl` is append-only per completed validation run and is not release evidence.
  - retention pruning is oldest-first under explicit cap and must preserve schema-valid entries.
  - direct mutation outside validation/reporting pathways is out of contract.

## Interfaces and Dependencies

Primary interfaces:

- CLI entrypoint: `bin/ask`.
- Skills command handlers: `Infrastructure/scripts/lib/ask/commands/skills.py`.
- Plugin state command handlers: `Infrastructure/scripts/lib/ask/commands/plugins.py`.
- Selection payload contract: `Infrastructure/scripts/lib/ask/selection_contract.py`.
- Plugin state collector: `Infrastructure/scripts/lib/ask/plugin_state.py`.

Normative CLI grammar (wave 1):

| Surface             | Canonical syntax                                                       | Required output contract                                                                                                                                                                                                                                 |
| ------------------- | ---------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Skills route        | `ask skills route \"<request>\" [--top-k N] [--considered-limit N]`    | `decision` payload containing all required `SelectionDecision` fields (`schema_version`, `request_id`, `policy_identity`, `decision_status`, `failure_class`, `operator_action`, considered metadata, ordering, selected/considered/excluded candidates) |
| Intent route        | `ask skills goal \"<intent_text>\" [--top-k N] [--considered-limit N]` | `goal_decision` payload with `schema_version`, one `recommended_candidate`, up to two `alternative_candidates`, `disambiguation_prompts`, `decision_status`, `failure_class`, `operator_action`, `policy_identity`                                       |
| Catalog diagnostics | `ask repo doctor-catalog [--strict]`                                   | `catalog_parity` payload with `schema_version`, `canonical_count`, per-surface observed counts, `drift_detected`, `drift_class`, `blocking_reason`, `operator_action`, `policy_identity`                                                                 |

Compatibility aliases:

- `ask goal \"<intent_text>\"` must map to `ask skills goal \"<intent_text>\"`.
- `ask doctor catalog` must map to `ask repo doctor-catalog`.
- Alias behavior must be consistent in normal mode and robot/fuzzy mode; correction messages must preserve canonical command names in guidance output.

Governance and parity dependencies:

- Canonical discovery policy identity from selection policy/discovery layer.
- Canonical catalog manifest and projection generators used by docs and CLI surfaces.
  - Canonical manifest source: `Infrastructure/scripts/lifecycle-and-sync/skill_catalog.py`.
  - Projection refresh source: `Infrastructure/scripts/lifecycle-and-sync/sync_skills.sh`.
- Validation wrappers (`Infrastructure/scripts/validation-and-linting/verify-work.sh`, `ask repo validate`) to run fail-fast parity and routing quality gates.
- Canonical routing-quality trend history source at `.tmp/agent-skills-artifacts/selection-quality/history.jsonl`, consumed by strict catalog diagnostics and validation trend checks.

Contract versioning dependencies:

- Route payload schema version: `selection-decision.v1`.
- Goal payload schema version: `goal-decision.v1`.
- Catalog diagnostics schema version: `catalog-parity.v1`.
- Backward-compatibility rule: additive fields are allowed within v1; breaking field removals/renames require v2.

Architectural dependency constraint:

- `bin/ask` remains parse/dispatch focused.
- Topic/action behavior lives in command modules to avoid continued growth of one orchestrator file.

## Invariants / Safety Requirements

- Determinism invariant:
  - identical request + identical manifest + identical policy identity => identical ordered decision payload.

- Catalog truth invariant:
  - required surfaces must report counts derived from the same `CatalogManifest`.
  - parity mismatch is a blocking trust failure.

- Explainability invariant:
  - selected candidates include confidence and rationale.
  - considered but non-selected candidates include exclusion reason.

- Ambiguity safety invariant:
  - no silent nondeterministic winner when confidence overlap is unresolved.

- Intent safety invariant:
  - `ask skills goal` always returns a recommendation contract, not freeform prose-only output.

- Plugin safety invariant:
  - wave-1 plugin state commands are read-only with zero mutation side effects.

- Modularity invariant:
  - adding a topic/action does not require embedding business logic into the central parser file.

## Failure Model and Recovery

Failure classes:

- `DISCOVERY_POLICY_DRIFT`
- `CATALOG_PARITY_DRIFT`
- `AMBIGUITY_UNRESOLVED`
- `NO_ELIGIBLE_CANDIDATES`
- `INCOMPLETE_EXPLAINABILITY`
- `INTENT_UNRESOLVED`
- `PLUGIN_STATE_UNAVAILABLE`
- `PLUGIN_SKILL_SHADOWING`
- `SELECTION_REGRESSION`

Recovery posture:

- Fail fast in CI for `CATALOG_PARITY_DRIFT`, `INCOMPLETE_EXPLAINABILITY`, `SELECTION_REGRESSION`, and `PLUGIN_SKILL_SHADOWING`.
- Return explicit error/degraded statuses (not silent fallback) for ambiguity, no-candidate, intent-unresolved, and plugin-state failures.
- For catalog parity drift, surface per-surface mismatch and canonical count in one diagnostic payload.
- For policy drift, block release-ready status until policy identity parity is restored.

Required decision/error/exit mapping:

| Surface outcome                                                    | `decision_status`          | `failure_class`            | CLI `ErrorCode`  | Exit code class  |
| ------------------------------------------------------------------ | -------------------------- | -------------------------- | ---------------- | ---------------- |
| Route success                                                      | `resolved`                 | `null`                     | `SUCCESS`        | `SUCCESS`        |
| Goal success                                                       | `resolved`                 | `null`                     | `SUCCESS`        | `SUCCESS`        |
| Route ambiguity unresolved                                         | `unresolved_ambiguity`     | `AMBIGUITY_UNRESOLVED`     | `ERR_CONFLICT`   | `ERR_CONFLICT`   |
| Route policy parity blocked                                        | `blocked_policy_drift`     | `DISCOVERY_POLICY_DRIFT`   | `ERR_DEPENDENCY` | `ERR_DEPENDENCY` |
| Route no eligible candidates                                       | `degraded_no_candidates`   | `NO_ELIGIBLE_CANDIDATES`   | `ERR_VALIDATION` | `ERR_VALIDATION` |
| Route catalog parity blocked                                       | `blocked_catalog_parity`   | `CATALOG_PARITY_DRIFT`     | `ERR_VALIDATION` | `ERR_VALIDATION` |
| Goal non-success translation (from any route non-resolved outcome) | `intent_unresolved`        | `INTENT_UNRESOLVED`        | `ERR_VALIDATION` | `ERR_VALIDATION` |
| Plugin state unavailable                                           | `degraded` (plugin doctor) | `PLUGIN_STATE_UNAVAILABLE` | `ERR_VALIDATION` | `ERR_VALIDATION` |

Deterministic failure precedence rules:

- If policy and catalog parity both fail, outcome must be `blocked_policy_drift`.
- `intent_unresolved` applies only to goal surface and must be used for any goal non-success after translating upstream route non-resolved outcomes.
- `degraded_no_candidates` is valid only when blocking parity gates have passed.
- Each non-success route/goal/catalog outcome must include a non-empty `operator_action`.
- Plugin doctor non-success must include at least one blocking reason and explicit remediation guidance.

Required operator signals:

| Failure class               | Required operator signal                               |
| --------------------------- | ------------------------------------------------------ |
| `DISCOVERY_POLICY_DRIFT`    | mismatched policy identities by surface                |
| `CATALOG_PARITY_DRIFT`      | canonical count and per-surface observed counts        |
| `AMBIGUITY_UNRESOLVED`      | top conflicting candidates and disambiguation prompt   |
| `NO_ELIGIBLE_CANDIDATES`    | request fingerprint, policy identity, eligibility hint |
| `INCOMPLETE_EXPLAINABILITY` | missing field list by candidate/decision id            |
| `INTENT_UNRESOLVED`         | why recommendation could not be safely resolved        |
| `PLUGIN_STATE_UNAVAILABLE`  | missing or invalid plugin state source                 |
| `PLUGIN_SKILL_SHADOWING`    | overlapping names and ownership hint                   |
| `SELECTION_REGRESSION`      | fixture ids and behavioral diff summary                |

## Observability

Required metrics:

- Route invocations by `decision_status`.
- Unresolved ambiguity rate.
- No-candidate degradation rate.
- Confidence distribution of selected candidates.
- Exclusion-reason frequency.
- Goal-entrypoint adoption and unresolved-intent rate.
- Catalog parity pass/fail rate by surface.
- Plugin state visibility command pass/fail rate.
- Selection regression fixture pass/fail history.
- Alias-to-canonical command normalization rate and mismatch rate.
- Route-to-goal translation success/failure rate.

Required artifacts:

- `RoutingQualityArtifact` for route and goal decisions.
- `CatalogParityReport` artifact from diagnostic checks.
- Canonical local trend history at `.tmp/agent-skills-artifacts/selection-quality/history.jsonl` for strict-mode deterioration checks.

Artifact minimum fields:

- `run_id`
- `policy_identity`
- `decision_status_counts`
- `unresolved_ambiguity_rate`
- `no_candidate_rate`
- `top_rejection_reasons`
- `explainability_completeness_ratio`
- `parity_status`

Readiness gates:

- Hard gate G1: required-surface catalog parity must be 100% before release progression.
- Hard gate G2: explainability completeness must be 100% for resolved decisions.
- Hard gate G3: failure mapping completeness must be 100% for non-success outcomes.
- Soft gate G4: unresolved ambiguity and no-candidate rates must remain visible and trend-stable across releases using a rolling 14-run window.

Soft-gate deterioration thresholds:

- Deterioration is true when either metric increases by more than 20% relative to the rolling baseline median and by at least +1 absolute percentage point.
- Baseline is the median of the previous 7 completed validation runs within the rolling window.
- Insufficient baseline history (<7 prior accepted runs) is reported as `insufficient_history`; it remains an explicit collecting state and is never labeled healthy-by-default.

Breach behavior:

- Any hard-gate breach blocks release-ready status.
- Soft-gate deterioration requires explicit operator note in validation artifact before progression.
- Strict-mode diagnostics block on schema-invalid canonical history and deterioration. Missing or insufficient history remains explicitly unknown or collecting, rather than being treated as healthy-by-default.

## Acceptance and Test Matrix

- SA1: `ask skills route` accepts freeform requests and returns deterministic ranked skill candidates.
- SA2: Route output includes every required `SelectionDecision` field: `schema_version`, `request_id`, `policy_identity`, `decision_status`, `failure_class`, `operator_action`, `considered_limit`, `considered_total`, `considered_truncated`, `truncated_count`, `ordering`, `selected_candidates`, `considered_candidates`, and `excluded_candidates`.
- SA3: Selected candidates include confidence and rationale; considered non-selected candidates include exclusion reason.
- SA4: Ambiguity yields deterministic winner only when rules resolve; otherwise returns explicit `unresolved_ambiguity` payload.
- SA5: Candidate ordering is canonicalized before scoring/truncation and output includes considered-limit/truncation metadata.
- SA6: Discovery policy identity is exposed and parity-checkable across route/discovery/sync surfaces.
- SA7: A canonical machine-readable `CatalogManifest` exists and is the single source for required catalog counts.
- SA8: `README`, root `SKILL.md`, `ask skills list`, and route considered metadata are parity-locked to canonical manifest counts.
- SA9: `ask repo doctor-catalog` returns canonical count, per-surface observed counts, policy identity, and blocking drift reason.
- SA10: `ask skills goal` returns one recommendation, two alternatives when available, and disambiguation prompts.
- SA11: `ask skills goal` uses the same policy identity and route semantics as `ask skills route`.
- SA12: Starter-oriented discovery mode exists and prioritizes stable high-signal skills by archetype.
- SA13: Documentation includes a "5-minute success path" at `Docs/agents/5-minute-success-path.md` with a required section named `First Validated Outcome`, validated by the repo docs gate.
- SA14: `ask plugins list|status|doctor` expose read-only installed, activation, and health state.
- SA15: Plugin state visibility commands perform no mutation side effects.
- SA16: CI includes deterministic fixture tests for precedence, ambiguity, and explainability behaviors.
- SA17: Validation emits routing-quality artifacts with unresolved-ambiguity, no-candidate, and rejection-reason metrics.
- SA18: Validation fails fast on explainability gaps, policy drift, and catalog parity drift.
- SA19: Plugin-skill shadowing is a blocking readiness failure in wave 1.
- SA20: CLI command architecture preserves modular command handlers with measurable constraints: `bin/ask` remains parse/dispatch only for skills/plugins and gate verification includes the canonical `ask_cli_modularity` validation check in repo validation output.
- SA21: Route, goal, and catalog diagnostic surfaces implement deterministic terminal-status precedence exactly as specified in lifecycle and failure-precedence rules.
- SA22: Route/goal/catalog payloads expose explicit schema versions with v1 backward-compatibility guarantees for additive-only changes.
- SA23: Validation artifacts encode hard-gate and soft-gate outcomes, and hard-gate breaches block release-ready status.
- SA24: Alias-to-canonical command normalization is deterministic and reported in observability metrics.
- SA25: `ask repo doctor-catalog --strict` enforces strict-mode semantics and reports strict-mode failures as blocking outcomes.

## Verification Targets

Required implementation and verification targets:

- CLI command-surface behavior:
  - `Infrastructure/tests/test_ask_cli.py`
  - `Infrastructure/tests/test_ask_skills_route.py`
  - `Infrastructure/tests/test_ask_skills_goal.py`
  - `Infrastructure/tests/test_ask_repo_doctor_catalog.py`
  - `Infrastructure/tests/test_ask_skills_starter.py`
  - `Infrastructure/tests/test_ask_plugins_state.py`
- Contract and schema validators:
  - `Infrastructure/scripts/validation-and-linting/verify_selection_contract.py`
  - `Infrastructure/scripts/validation-and-linting/verify_router_schema.py`
  - `Infrastructure/scripts/validation-and-linting/verify_ask_cli.py`
  - `Infrastructure/scripts/validation-and-linting/verify_ask_cli_final.py`
- Catalog and lifecycle parity gates:
  - `Infrastructure/scripts/validation-and-linting/verify_skill_catalog_freshness.py`
  - `Infrastructure/scripts/testing/test_skill_lifecycle_validation.py`
- Aggregate release-readiness gate:
  - `Infrastructure/scripts/validate_all.sh`

Verification expectation:

- Route, goal, starter, catalog-diagnostics, and plugin-state contracts are all enforced by deterministic tests and validators in the targets above.
- Required gates fail fast when contract-required payload fields, parity outcomes, strict-mode semantics, or modularity evidence regress.

## Open Questions

- Exact output schema shape for `ask skills goal` and whether alternatives remain fixed at two or become configurable by policy.
- Starter-mode namespace shape (`ask skills list --starter` vs `ask skills starter`) and default archetype taxonomy.
- Whether v2 should include interactive fallback prompts for unresolved statuses without changing CI semantics.

## Definition of Done

- All acceptance criteria `SA1`-`SA25` are implemented and validated.
- Required routing and parity artifacts are emitted in repo validation flows.
- Catalog trust mismatch reproductions are eliminated for required surfaces.
- Wave-1 plugin visibility remains read-only and shadowing-protected.
- Spec is ready for sequencing in `ce-plan` without adding behavioral assumptions.
- Canonical commands and aliases are documented and covered by parser/contract tests.
- CLI error and exit-code mapping is validated for all non-success route/goal/catalog outcomes.
