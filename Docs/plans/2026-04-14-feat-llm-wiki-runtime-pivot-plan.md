---
title: LLM Wiki Runtime Pivot Implementation Plan
type: feat
status: active
date: 2026-04-14
origin: docs/brainstorms/2026-04-13-llm-wiki-runtime-pivot-requirements.md
spec: docs/specs/2026-04-13-feat-llm-wiki-runtime-pivot-spec.md
deepened: 2026-04-14
---

# LLM Wiki Runtime Pivot Implementation Plan

## Enhancement Summary

**Deepened on:** 2026-04-14  
**Mode:** targeted-confidence  
**Key areas improved:** sequencing gates, verification oracles, system-wide failure handling, risk treatment

- Added explicit phase-gate sequencing rules so each implementation unit has clear stop/advance criteria before downstream work starts.
- Added a high-level technical design section that clarifies evidence flow, lifecycle transition ownership, and where promotion decisions are made.
- Strengthened implementation-unit verification with artifact-oriented oracles and failure stop conditions to reduce ambiguous execution outcomes.
- Expanded system-wide impact and risks into explicit propagation paths, ownership, and fallback behavior for lane 1/2/4 blockers.
- Added targeted rollout/rollback controls for `P4` and `P5`, including explicit trigger conditions and rollback-exit checks.

## Reviewer Closeout Delta (2026-04-14)

This section resolves the latest reviewer findings that kept the plan open.

1. Phase-order/ownership conflict resolution:
   - Required-check ownership is now explicit and non-overlapping: `P4` owns declaration/mapping (`required-check-scope.*`), `P5` owns privacy normalization semantics (`privacy-required-check-normalization.*`), and downstream severity mapping cannot redefine either contract.
2. First-write trust contract concreteness:
   - Bootstrap now requires a concrete identity primitive and attested write contract (`issuer`, `subject`, `audience`, `repository`, `workflow_ref`, `run_id`) plus signed bootstrap intent metadata before any first write.
3. Sidecar evidence security contract concreteness:
   - Sidecar schema, validator, access model, and deny semantics are now explicitly tied to `privacy-sidecar-contract.*` and `verify_privacy_sidecar_contract.py`.
4. `ask` v1 identity/entitlement enforceability:
   - v1 entitlement uses one enforceable subject primitive (`entitlement_subject`) and one normalized command primitive (`command_selector`) with fail-closed checks.
5. v1 downgrade rejection blocker mapping:
   - A deterministic deny-reason to blocker-code mapping contract is now required and test-covered.
6. Closeout counters compatibility clarity:
   - Companion counters compatibility is now promotion-gated with explicit major-version parity and deterministic mismatch blocking.
7. Live required-check freshness clarity:
   - Freshness evaluation now uses one explicit max-age rule and validator ownership, with stale evidence as a hard block.
8. P0 rollback manifest completeness:
   - P0 restore manifest must prove completeness against the full P0 mutator set via a deterministic manifest-diff test, not a partial manually curated subset.

## Overview

This plan implements the runtime pivot contract defined in the 2026-04-13 spec by introducing deterministic lane evaluation, fail-closed installation governance, freshness-aware closeout health reporting, and explicit compatibility posture around the `llm_wiki_primary` operating mode.

The delivery is sequenced to first stabilize control-plane data contracts, then wire gate behavior, then enforce promotion/closeout reporting so blocked lanes (1, 2, 4) cannot silently regress.

## Problem Frame

The current closeout path repeatedly reaches implementation progress but fails promotion confidence because lane blockers are not consistently represented as one deterministic contract across mode declaration, installation governance, and closeout evidence.

The spec now defines fixed behavior (including canonical `wiki/` contract root, explicit lane ownership, blocker precedence, and freshness policy defaults). Implementation must enforce those rules in existing repo gates without introducing a second source-of-truth or breaking required operator command surfaces.

## Requirements Trace

- R1-R3 -> enforce mode contract and Obsidian viewer-only boundary.
- R4-R6 -> enforce canonical authority map and single-writer projection governance.
- R7-R9 -> keep scaffold/path/command contract machine-checkable and compatibility-explicit.
- R10-R13 -> deterministic blocker taxonomy, owner/SLA mapping, recurring closeout health, drift prevention.
- R14-R16 -> absorb blocked lanes 1/2/4 with deterministic lane results and promotion gating.
- R17-R18 -> privacy/redaction gate before sensitive ingestion.
- R19-R22 -> required skill stack + inspector-role resolution + fail-closed promotion behavior.

### Acceptance Criteria Trace

- AC1. Mode contract emits `llm_wiki_primary` + compatibility posture `degraded_compatibility` (mode posture term) with required ownership/registry fields (`mode_owner`, `blocking_exceptions_ref`) and one canonical writable `wiki/` root plus explicitly declared `raw_source_roots` access policy (append-only ingest in this repository resolver), all mapped through one repository resolver policy. Lane diagnostics remain `degraded_findings[]`. (R1-R5)
- AC2. Installation governance fails closed when required skills or inspector resolution are incomplete. (R19-R22)
- AC3. Lane obligations 1/2/4 emit deterministic `ready|degraded|blocked` with `evidence_ref`, owner, and freshness metadata. Full AC3 delivery is owned by P2 after P0 establishes schema/state prerequisites. (R14-R16)
- AC4. Blocker precedence and exact-match normative exception matching are deterministic and evidenced from the normative registry contract only. Exact-match selector identity is fixed to (`exception_code`, `lane_id`, `blocker_code`, `owner_role`) with lifecycle-governed fields (`evidence_command`, `freshness_window_hours`, `expiry_policy`) treated as mandatory metadata (never selector wildcards), deterministic expired-row rejection, and fail-closed duplicate-row rejection when selector tuples are non-unique. Runtime `blocker_code` values that surface through `ask` diagnostics must resolve through one deterministic registry mapping path (no ambiguous multi-mapping). (R10-R11)
- AC5. The closeout report package remains spec-locked and consists of three linked artifacts: (a) `closeout_health_reported` event emitting only `schema_version`, `overall_state`, `blocked_count`, `degraded_count`, `freshness_policy_ref`, and `promotion_decision`; (b) canonical counters artifact `GOVERNANCE/runtime-separation/closeout-health-counters.json` (schema `GOVERNANCE/runtime-separation/closeout-health-counters.schema.json`) containing required counters (`lane_ready_count`, `lane_degraded_count`, `lane_blocked_count`, `installation_skill_coverage_ratio`, `inspector_resolution_ratio`, `blocker_metadata_completeness_ratio`) and numeric freshness windows per lane (`freshness_windows_by_lane`); (c) canonical reader-compatibility companion artifact `GOVERNANCE/runtime-separation/reader-compatibility.json` (schema `GOVERNANCE/runtime-separation/reader-compatibility.schema.json`) containing one record per independently versioned surface (`current.json`, `CloseoutHealthSnapshot`, `closeout_health_reported`) with `surface_id`, `surface_schema_version`, `minimum_reader_version`, `compatible_reader_range`, and `metadata_generated_at`. `blocker_metadata_completeness_ratio` is deterministic: numerator = blockers in `CloseoutHealthSnapshot.blockers[]` with all required `BlockerRecord` fields (`blocker_code`, `lane_id`, `severity`, `owner`, `escalation_window`, `evidence_ref`, `first_seen_at`, `last_seen_at`, `status`); denominator = total blockers (or `1` when none); ratio = `numerator / denominator`. `CloseoutHealthSnapshot` remains a separate required snapshot artifact with field set (`schema_version`, `timestamp`, `mode_state`, `lane_obligations`, `blockers[]`, `degraded_findings[]`, `owner_assignments`, `freshness_policy_ref`, `promotion_decision`) and no unversioned schema expansion. `closeout-health-counters.json` is a required companion artifact but not an independently versioned output surface; its schema/version changes must remain coupled to closeout event/snapshot compatibility policy. Versioning policy is deterministic: additive fields require minor `schema_version` increments with a documented compatibility window, removed/renamed required fields require major `schema_version` increments, and promotion-ready output fails closed when reader-compatibility companion records are missing or incompatible. (R13)
- AC6. Status/checklist drift across requirements/spec/plan and linked operator-governance docs (`docs/agents/04-validation.md`, `docs/agents/07b-agent-governance.md`, `docs/agents/12-ci-required-checks.md`, `docs/agents/13-workflow-and-safety-guidance.md`, `docs/agents/14-path-ownership-boundaries.md`) is enforced as a blocking validation failure. (R12)
- AC7. Required operator command compatibility remains intact for declared mandatory surfaces, and full adapter parity is required by P3 before promotion-ready output is allowed. `ask` machine-readable contract selection is deterministic: redacted v2 is default, v1 is allowed only through explicit compatibility selector + CI-governed per-command allowlist entitlement bound to authenticated caller/workload identity + `legacy_contract_v1_sunset_at` cutoff, non-allowlisted or identity-mismatched requests fail closed, and v1 compatibility is structural-only (never exposes unredacted `raw_output`/`raw_error` passthrough on any command surface, including `repo`, `wiki`, `skills`, `plugins`, and `evals` adapters). Selector identity is derived only after alias/robot normalization in `bin/ask`, and version axes are mapped deterministically (`ask_json_contract_version` transport selector, matching `metadata.version` envelope, nested payload `schema_version` for command-domain schema). All deny paths emit canonical blocker-code diagnostics from one registry-mapped contract. (R9)
- AC8. Privacy classification/redaction gate is required before sensitive-source persistence (including raw-plane ingest) and before promotion. (R17-R18)
- AC9. Canonical ownership and schema/version validation are explicit for blocking-exception registry and rollout-mode state artifacts. (R10-R13)

## Scope Boundaries

In scope:

- Runtime/control-plane contract wiring for mode state, installation governance, lane obligation evaluation, and closeout health evidence.
- Canonical wiki authority boundary activation with two explicit planes under one resolver policy: writable synthesis plane (`docs/skill-ops-wiki/wiki/`) and append-only evidence plane (`docs/skill-ops-wiki/raw/`, ingest-only by approved commands/tools). Sensitive-source material must be classified/redacted before any repo write; for sensitive runs, repo `raw/` stores redacted payloads plus non-linkable digest envelope metadata while unredacted source and sensitive provenance/token material remain in restricted encrypted sidecar storage outside git-backed artifacts.
- Validation and reporting integration in existing scripts and `ask` repo command surfaces.
- Targeted tests and fixtures for deterministic blocker/freshness/lifecycle behavior.

Out of scope:

- New product features unrelated to the pivot contract.
- Broad skill-graph artifact deletion.
- Unrelated UI work (`ui_required: false`).
- Marketplace protocol redesign.
- Repo-wide required-check/ruleset redesign outside runtime-pivot-owned checks (tracked as separate governance hardening).

## Task graph

```yaml
tasks:
  - id: P0
    title: "Phase 0: pivot contract surface and artifact schema wiring"
    depends_on: []
  - id: P1
    title: "Phase 1: installation governance fail-closed gates"
    depends_on: [P0]
  - id: P2
    title: "Phase 2: lane obligation and deterministic emission"
    depends_on: [P1]
  - id: P3
    title: "Phase 3: ask v1 compatibility and downgrade controls"
    depends_on: [P2]
  - id: P4
    title: "Phase 4: required-check parity, drift, and closeout counters"
    depends_on: [P3]
  - id: P5
    title: "Phase 5: privacy gate and sidecar enforcement"
    depends_on: [P4]
  - id: P6
    title: "Phase 6: enforce activation and rollback hardening"
    depends_on: [P5]
```

## Context & Research

### Relevant Code and Patterns

- Runtime-separation contract and parity artifacts:
  - `GOVERNANCE/runtime-separation/baseline.json`
  - `GOVERNANCE/runtime-separation/current.json`
  - `GOVERNANCE/runtime-separation/slices.yaml`
- Existing deterministic validator entrypoints:
  - `Infrastructure/scripts/validate_all.sh`
  - `Infrastructure/scripts/validation-and-linting/verify-work.sh`
  - `Infrastructure/scripts/runtime-separation/build_runtime_separation_current.py`
  - `Infrastructure/scripts/runtime-separation/compare_runtime_separation_baseline.py`
  - `Infrastructure/scripts/validation-and-linting/verify_skill_catalog_freshness.py`
- Existing repo command surfaces and parity expectations:
  - `bin/ask`
  - `tests/test_ask_repo_doctor_catalog.py`
  - `tests/test_ask_cli.py`

### Institutional Learnings

- Prior lanes already treat `ask repo validate`, `verify-work`, and catalog freshness checks as canonical gate evidence and should remain source-of-truth for promotion decisions.
- Runtime-separation validation and baseline comparator flow are already integrated in `Infrastructure/scripts/validate_all.sh`; this pivot should extend that path rather than create parallel governance entrypoints.

### External References

- None required for this plan; implementation is governed by repository contracts and the approved spec.

## Key Technical Decisions

- Decision 1: Implement lane-obligation and closeout behavior by extending existing runtime-separation artifact and gate scripts, not by introducing an independent governance pipeline.
  - Rationale: preserves current operator workflows and avoids split authority.

- Decision 2: Keep blocker taxonomy and freshness policy as machine-readable contract fields emitted in artifacts and command output, not prose-only docs.
  - Rationale: promotion gates need deterministic, parseable evidence.

- Decision 3: Treat installation-skill-stack and inspector availability as explicit fail-closed checks integrated before promotion reporting.
  - Rationale: aligns with spec fail-closed governance and prevents silent quality drift.

- Decision 4: Keep compatibility mode non-blocking by default only for explicitly non-security compatibility findings and block on normative exception matches plus any security-sensitive compatibility class (identity/authz, redaction/privacy, replay/concurrency, contract-version downgrade).
  - Rationale: preserves degraded-visibility posture for low-risk noise while keeping security-relevant drift fail-closed.

## Planning Outcomes and Deferred Implementation Details

### Resolved During Planning

- Canonical wiki root policy is fixed to logical root `wiki/` by spec contract and mapped in this repository to physical path `docs/skill-ops-wiki/wiki/` by one resolver policy until an explicit migration phase changes physical layout.
- Raw evidence contract root is logically `raw_source_roots` and maps in this repository to physical path `docs/skill-ops-wiki/raw/` with append-only ingest semantics; in sensitive-source scope, repo storage is limited to pre-redacted payloads plus non-linkable digest envelope metadata, while sensitive provenance/token details remain in restricted encrypted sidecar storage outside git-backed artifacts.
- Spec now defines canonical fallback roles (`repo-research-analyst`, `project-standards-reviewer`) for unavailable inspector roles.
- Sidecar persistence plane is explicit (not implicit): it is a controlled implementation storage plane owned by P5 privacy-gate policy (`privacy-sidecar-contract.yaml`) with dedicated migration boundary from legacy raw-source handling; migration is additive and forward-only (no retroactive rewrite of historical raw evidence artifacts).

### Deferred to Implementation

- Whether lane-obligation evaluation should be implemented as a new dedicated script or as an extension inside `Infrastructure/scripts/runtime-separation/build_runtime_separation_current.py`.
  - Decision rule: keep implementation in `Infrastructure/scripts/runtime-separation/build_runtime_separation_current.py` unless a second independent producer needs to emit the same lane-obligation schema. If a second producer emerges, extract shared logic to one helper module and keep one canonical schema writer.
- Whether additional closeout reporting should be exposed as a dedicated `ask repo` sub-check beyond existing wrappers.
  - Decision rule: `Infrastructure/scripts/validate_all.sh` remains the canonical enforcement lane, while `ask repo validate` may surface the same contract outcomes but must not introduce divergent pass/fail logic.

## High-Level Technical Design

This design is directional planning guidance that clarifies contract boundaries and sequencing; it is not implementation code.

### Contract Data Flow

1. **Evidence collection layer**
   - Runtime, catalog, and ask-contract checks produce normalized evidence signals through existing validators.
2. **Normalization layer**
   - Runtime-separation current artifact builder emits lifecycle state, lane-obligation results, blocker taxonomy, and freshness metadata.
3. **Decision layer**
   - Baseline comparator and required-check wrappers evaluate blocker precedence and determine promotion readiness.
4. **Reporting layer**
   - Closeout health snapshot and `ask` surfaces report deterministic state without introducing alternate governance rules.

### Atomic State Write Boundary

- Persistent mode-state transitions are owned by one dedicated state-transition writer (`set_runtime_rollout_state`) with temp-file+atomic-rename semantics.
- `build_runtime_separation_current.py` is a read-only snapshot producer over persistent state and must not mutate `rollout-state.json`.
- Partial updates are invalid: persistent state transition writes and snapshot writes each fail closed independently, and promotion remains blocked when state/snapshot parity checks fail.
- First trusted-write bootstrap is explicit and single-use: `set_runtime_rollout_state.py --bootstrap-init` is allowed only when `rollout-state.json` does not exist, only from authenticated CI workflow identity, and only with signed bootstrap intent metadata (`bootstrap_phase`, `bootstrap_nonce`, `bootstrap_manifest_digest`) anchored to immutable trust-root policy; failed bootstrap attestation leaves no file on disk.
- Bootstrap identity primitive is explicit: `bootstrap_subject = (issuer, subject, audience, repository, workflow_ref, run_id)` extracted from signed workload identity claims and verified against immutable trust-root policy before evaluating bootstrap intent metadata.
- First-write trust contract is explicit and fail-closed: bootstrap requires (`bootstrap_subject`, signed bootstrap intent metadata, trust-anchor verification, bootstrap nonce freshness, bootstrap manifest digest parity). Missing/invalid fields, unknown issuer/key, or trust-root mismatch blocks before file creation.
- Bootstrap and transition requests are replay-safe and concurrency-safe: each write must carry one-time `request_nonce`, bounded `request_issued_at` freshness window, `expected_state_digest` optimistic-concurrency guard, and monotonic `expected_state_sequence`. Writer-side durable nonce ledger + sequence tracking is mandatory; nonce reuse, stale timestamps, stale/non-monotonic sequence, or digest mismatch fail closed before any write.
- Rollback/restore paths must include all canonical persistent artifacts touched by the pivot contract (`rollout-state.json`, `blocking-exceptions.registry.yaml`, `installation-governance.json`, `privacy-gate-evidence.json`, `closeout-health-counters.json`, `lane-owner-policy.yaml`, `lane-owner-policy.schema.json`, `freshness-policy.yaml`, `freshness-policy.schema.json`, `provenance-trust-policy.yaml`, `sensitivity-classification-policy.yaml`, `required-check-bootstrap.yaml`, `policy-bundle.lock.json`) plus all mutable schema/control artifacts introduced by this rollout, and an explicit executable/profile rollback recipe for new gate assets, including required-check declaration/emitter surfaces when they are modified by this rollout (`required-check-scope.*` is introduced in P4 and enters rollback coverage at that phase boundary).
- Rollback/restore contract must also preserve replay/concurrency continuity artifacts for `set_runtime_rollout_state.py` (durable nonce ledger + monotonic sequence ledger); restore that would rewind replay state without a signed re-seed/epoch-advance record is invalid and blocks transition writes.

### State and Gate Ownership

- `P0-P2` own contract-shape and lane-result correctness.
- `P3` owns lane-4 compatibility and deterministic ask parity contract behavior.
- `P4` owns promotion decision contract and artifact drift blocking behavior.
- `P5` owns privacy-gate enforcement semantics for sensitive-source promotion.
- `P6` owns final pivot enforce-activation handoff and reverse-transition rollback contract.
- `set_runtime_rollout_state.py` is the single state-mutation authority across P0-P6; all phase transitions must go through this writer and no phase may directly mutate `rollout-state.json`.
- Phase ownership is policy/transition ownership only; file mutation authority remains centralized in `set_runtime_rollout_state.py` with axis-scoped authorization (`pivot_rollout_mode` transitions allowed only for approved P0/P4/P6 transitions, `privacy_rollout_mode` transitions allowed only for approved P5 transitions). Transition writes must include authenticated workflow identity + signed/attested request metadata validated against trust policy, plus replay/concurrency controls (`request_nonce`, bounded `request_issued_at`, `expected_state_digest`, monotonic `expected_state_sequence`, and durable nonce/sequence tracking); unsigned, identity-mismatched, replayed/stale, stale/non-monotonic sequence, or stale-state invocations fail closed, including direct local script invocation attempts.
- `Infrastructure/scripts/validate_all.sh` is the only enforcement authority for pass/fail gate semantics; `verify-work.sh`, `ask`, and CI-required-check wrappers must delegate to or consume its output contract without redefining blocker logic.

### Required-Check Ownership Matrix (Phase-Split Contract)

| Surface                                                          | Owner phase          | Allowed operation                                                                                     | Forbidden operation                                                            |
| ---------------------------------------------------------------- | -------------------- | ----------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| `required-check-scope.yaml` / `required-check-scope.schema.json` | P4                   | declare and map runtime-pivot-owned required checks to emitting workflows                             | define privacy `not_applicable` semantics or severity rewrites                 |
| `privacy-required-check-normalization.yaml` / `.schema.json`     | P5                   | define lane-scoped privacy normalization (`not_applicable` pass-equivalent rules) after P4 derivation | redefine check declaration ownership or mutate workflow mapping scope          |
| `Infrastructure/scripts/validation-and-linting/verify_selection_gate_severity.py`                      | P4 then P5 extension | consume derived scoped artifact; in P5 consume normalization output in fixed order                    | independently derive scope, bypass normalization order, or apply inline policy |

Deterministic precedence contract:

1. derive scoped declarations (`P4` ownership),
2. apply privacy normalization (`P5` ownership),
3. apply severity mapping (consumer only).

Any phase that mutates outside its ownership column is a blocking contract violation.

### State Vocabulary Guardrails

- `pivot_rollout_mode` and `privacy_rollout_mode` are implementation rollout-control fields for staged deployment only; they are intentionally outside the normative spec contract surface and must not be exposed as spec-domain entities without a spec revision.

- `lifecycle_state` remains spec-locked to the lifecycle enum in `spec` and must never include rollout-phase labels.
- `pivot_rollout_mode` is a dedicated implementation deployment axis for gate strictness progression (`shadow`, `warn_visible`, `enforce`) and must not reuse unrelated repo-wide `rollout_mode` enums.
- `privacy_rollout_mode` is a separate deployment axis for privacy-gate progression (`observe`, `enforce`).
- Rollout-mode truth is sourced from one canonical implementation-control artifact (`GOVERNANCE/runtime-separation/rollout-state.json`) with schema/version checks; all operator surfaces consume that artifact.
- Inspector identifiers are canonicalized to spec IDs (`skill-inspector`, `plugin-inspector`); optional `@`-prefixed inputs are normalized to the canonical bare form before policy evaluation.
- `degraded_compatibility` is a mode posture term; `compatibility findings`/`degraded_findings[]` are lane-4 diagnostic outputs. These terms are not interchangeable.
- `privacy_gate=not_applicable` is valid only when deterministic dual corroboration records both: (1) trusted classifier result `sensitivity_scope=non_sensitive`; (2) independent non-sensitive corroboration from an immutable-trust-root-attested source-inventory snapshot (repo-editable allowlist/policy changes alone are never sufficient). Missing either proof is blocking; `sensitivity_scope=unknown` is blocking.
- Contract outputs must reject unknown lifecycle values even when rollout-mode fields advance.
- Outcome taxonomy is single-source and domain-scoped: emitted literals must map to one canonical registry classification (`lane_result_state`, `privacy_gate_state`, `rollout_mode_state`, `ask_blocker_code`) and validators fail closed on unregistered or cross-domain values.

### Artifact Versioning and Compatibility Guardrails

- Independently versioned closeout contract surfaces are `current.json`, `CloseoutHealthSnapshot`, and `closeout_health_reported`, each with string-encoded `schema_version` values in format `<surface>.v<major>[.<minor>]`; legacy `<surface>.v1` is interpreted as `<surface>.v1.0` during migration.
- `current.schema.json` is the validator schema for `current.json` (and must evolve atomically with it) but is not an independently versioned closeout output surface.
- `closeout-health-counters.json` is a required companion artifact for closeout reporting but not an independently versioned closeout surface; it must remain schema/version-coupled to `closeout_health_reported` and `CloseoutHealthSnapshot` (major version parity required, minor additive changes bounded by reader-compatibility policy).
- Promotion consumer compatibility for companion counters is explicit and blocking: `Infrastructure/scripts/runtime-separation/verify_runtime_separation_reader_compat.py` must enforce that `closeout-health-counters.json` declares and matches the active major versions of `closeout_health_reported` and `CloseoutHealthSnapshot`; any absence/mismatch emits deterministic blocker `blocked_closeout_counter_version_mismatch`.
- Breaking contract changes require major `schema_version` increments and migration notes in the same phase as writer changes.
- Additive contract changes require minor `schema_version` increments and a bounded reader-compatibility window documented in canonical companion metadata (`reader-compatibility.json`).
- Reader compatibility metadata is emitted only through `GOVERNANCE/runtime-separation/reader-compatibility.json` (producer: `Infrastructure/scripts/runtime-separation/build_runtime_separation_current.py`; validator: `Infrastructure/scripts/runtime-separation/verify_runtime_separation_reader_compat.py`) and is a promotion precondition.
- No phase may introduce output-shape changes without landing the corresponding schema and validator/test updates in that same phase.

### Sidecar Security Contract (Schema + Validator + Access Model)

| Contract element                      | Canonical source                                                     | Enforcer                                                            | Blocking failure semantics                                                                   |
| ------------------------------------- | -------------------------------------------------------------------- | ------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| Sidecar interface schema/version      | `GOVERNANCE/runtime-separation/privacy-sidecar-contract.schema.json` | `Infrastructure/scripts/verify_privacy_sidecar_contract.py`                        | schema drift or missing required linkage fields blocks persistence and promotion             |
| Decrypt authority policy              | `GOVERNANCE/runtime-separation/privacy-sidecar-contract.yaml`        | `Infrastructure/scripts/verify_privacy_sidecar_contract.py` + runtime decrypt gate | unauthorized principal or unverifiable authority emits `decrypt_authority_denied` and blocks |
| Key custody and rotation attestations | `privacy-sidecar-contract.yaml` + trust policy                       | `Infrastructure/scripts/verify_privacy_sidecar_contract.py`                        | stale/missing custody or rotation evidence emits `sidecar_attestation_missing` and blocks    |
| Immutable sidecar audit trail         | sidecar contract + audit sink                                        | `Infrastructure/scripts/verify_privacy_sidecar_contract.py`                        | missing encrypt/decrypt/link/retention events blocks                                         |
| Sidecar availability and linkage      | sidecar contract + `privacy-gate-evidence.json` linkage pointers     | privacy gate validators + closeout consumer checks                  | sidecar outage or broken linkage emits `sidecar_unavailable` and blocks                      |

### Canonical Artifacts (Contract + Implementation Controls)

- Contract artifacts below are normative where they map directly to spec contracts.
- Rollout-control artifacts (`rollout-state.*`) are implementation controls owned by this plan and explicitly non-normative to the current spec.

- `GOVERNANCE/runtime-separation/blocking-exceptions.registry.yaml` is the only normative blocking-exception registry source consumed by lane-4 gating.
- `GOVERNANCE/runtime-separation/blocking-exceptions.schema.json` owns registry schema/version compatibility checks.
- `GOVERNANCE/runtime-separation/rollout-state.json` is the canonical implementation-control storage for `pivot_rollout_mode` and `privacy_rollout_mode`.
- `GOVERNANCE/runtime-separation/rollout-state.schema.json` owns rollout-state implementation-control schema/version compatibility checks.
- `GOVERNANCE/runtime-separation/lane-owner-policy.yaml` is the canonical lane-owner mapping source for `owner_assignments` and lane-level owner resolution.
- `GOVERNANCE/runtime-separation/lane-owner-policy.schema.json` owns lane-owner policy schema/version compatibility checks.
- `GOVERNANCE/runtime-separation/freshness-policy.yaml` is the canonical freshness-window/policy source referenced by `freshness_policy_ref`.
- `GOVERNANCE/runtime-separation/freshness-policy.schema.json` owns freshness-policy schema/version compatibility checks.
- `Infrastructure/scripts/verify_runtime_policy_contracts.py` is the canonical validator for lane-owner/freshness policy schema, reference integrity, and consumer-contract completeness before lane emission or P6 activation checks run.
- `GOVERNANCE/runtime-separation/current.json` remains canonical runtime output and is upgraded through a versioned compatibility contract.
- `GOVERNANCE/runtime-separation/current.schema.json` is the canonical runtime artifact envelope validator contract for upgraded `current.json` output.
- `GOVERNANCE/runtime-separation/closeout-health-snapshot.schema.json` owns `CloseoutHealthSnapshot` schema/version checks as an independently versioned contract surface.
- `GOVERNANCE/runtime-separation/closeout-health-event.schema.json` owns `closeout_health_reported` event schema/version checks as an independently versioned contract surface.
- `GOVERNANCE/runtime-separation/installation-governance.json` persists installation gate evidence (`role_resolution_policy`, `role_resolution_evidence`, `skill_coverage_ratio`) as canonical replayable evidence.
- `GOVERNANCE/runtime-separation/installation-governance.schema.json` owns installation-governance evidence schema/version checks.
- `GOVERNANCE/runtime-separation/privacy-gate-evidence.json` is the canonical git-backed persisted privacy evidence envelope used by privacy-gate and closeout consumers; it is limited to non-linkable digests, attestation references, and replay-safe pointers.
- `GOVERNANCE/runtime-separation/privacy-gate-evidence.schema.json` owns privacy evidence schema/version checks.
- Sensitive provenance/token material referenced by privacy evidence is persisted in a restricted encrypted sidecar outside git-backed artifacts; repo-local artifacts alone cannot satisfy sensitive-scope promotion evidence requirements.
- `GOVERNANCE/runtime-separation/privacy-sidecar-contract.yaml` is the canonical repo-visible interface contract for restricted encrypted sidecar evidence storage (required fields, access roles, retention policy, linkage semantics, and failure-handling behavior).
- `GOVERNANCE/runtime-separation/privacy-sidecar-contract.schema.json` owns sidecar interface schema/version checks.
- `Infrastructure/scripts/verify_privacy_sidecar_contract.py` is the canonical validator for sidecar contract linkage, decrypt-authority constraints, audit-trail completeness, and retention/expiry semantics.
- `GOVERNANCE/runtime-separation/outcome-taxonomy.yaml` is the canonical emitted-outcome registry classifying domain-specific literals (`lane_result_state`, `privacy_gate_state`, `rollout_mode_state`, `ask_blocker_code`) and preventing cross-domain reuse.
- `GOVERNANCE/runtime-separation/outcome-taxonomy.schema.json` owns emitted-outcome taxonomy schema/version checks.
- `Infrastructure/scripts/verify_outcome_taxonomy_contract.py` is the canonical validator ensuring every emitted literal used by validators/ask surfaces maps to exactly one registered taxonomy domain.
- `GOVERNANCE/runtime-separation/closeout-health-counters.json` is the canonical companion counters artifact referenced by closeout reporting.
- `GOVERNANCE/runtime-separation/closeout-health-counters.schema.json` owns companion counters artifact schema/version checks.
- `GOVERNANCE/runtime-separation/sensitivity-classification-policy.yaml` defines trusted classification producers/provenance checks for `sensitivity_scope`.
- `GOVERNANCE/runtime-separation/required-check-scope.yaml` is the canonical scoped required-check declaration/mapping policy consumed by required-check enforcement.
- `GOVERNANCE/runtime-separation/required-check-scope.schema.json` owns scoped required-check policy schema/version checks.
- `GOVERNANCE/runtime-separation/privacy-required-check-normalization.yaml` is the canonical privacy-gate required-check normalization policy artifact for lane-scoped `not_applicable` handling.
- `GOVERNANCE/runtime-separation/privacy-required-check-normalization.schema.json` owns privacy normalization policy schema/version checks.
- `GOVERNANCE/runtime-separation/reader-compatibility.json` is the canonical reader-compatibility companion artifact for independently versioned runtime/closeout surfaces.
- `GOVERNANCE/runtime-separation/reader-compatibility.schema.json` owns reader-compatibility companion artifact schema/version checks.
- `GOVERNANCE/runtime-separation/required-check-bootstrap.yaml` is the immutable bootstrap required-check guard-set source consumed read-only by `validate_all.sh` before any derived required-check policy evaluation.
- `GOVERNANCE/runtime-separation/required-check-bootstrap.schema.json` owns bootstrap guard-set schema/version checks.
- Bootstrap guard-set integrity for `required-check-bootstrap.yaml` is anchored outside repo-mutated policy artifacts through dual-control trust anchors (CI-managed signer identity plus offline/root signed digest-fingerprint configuration); local repo edits alone cannot redefine accepted bootstrap guard state.
- `GOVERNANCE/runtime-separation/required-check-enforcement.local.schema.json` owns local deterministic parity evidence schema/version checks.
- `GOVERNANCE/runtime-separation/required-check-enforcement.live.schema.json` owns live parity audit evidence schema/version checks.
- `GOVERNANCE/runtime-separation/required-check-derived-scoped.schema.json` owns the normalized scoped required-check intermediate artifact consumed by downstream severity gating.
- `GOVERNANCE/runtime-separation/readers.sha256` and `GOVERNANCE/runtime-separation/path-consumers.sha256` are canonical integrity digests for reader/consumer inventory manifests.
- `Infrastructure/scripts/verify_runtime_inventory_digests.py` is the canonical digest ownership/validation gate for `readers.yaml`, `path-consumers.yaml`, and their derived `.sha256` artifacts.
- `docs/cli-specs/ask-blocker-codes.yaml` is the canonical blocker-code registry for deterministic `ask` rejection diagnostics (including v1 compatibility deny paths).
- `docs/cli-specs/ask-v1-compat-policy.yaml` is the canonical policy source for v1 entitlement matrix and `legacy_contract_v1_sunset_at` enforcement state.
- `docs/cli-specs/ask-v1-compat-policy.schema.json` owns v1 compatibility policy schema/version checks.
- `GOVERNANCE/runtime-separation/provenance-trust-policy.yaml` defines allowed issuers/keys, rotation windows, and revocation handling for governance-artifact provenance.
- `GOVERNANCE/runtime-separation/policy-bundle.lock.json` is the canonical tamper-evident manifest for governance policy artifacts consumed by runtime gates.
- Immutable bootstrap trust root for policy-bundle verification is external to mutable policy artifacts and requires dual-anchor verification (protected CI/runtime trust configuration plus offline/root trust anchor). Local validator constants may only reference a non-authoritative diagnostic hint and cannot redefine acceptance criteria.
- Canonical governance artifacts require trusted provenance checks (signed/attested generator identity and digest validation) before consumers treat them as authoritative.
- Policy-bundle integrity is validated before any consumer loads mutable governance policy artifacts; policy load is fail-closed if lock/signature verification against the immutable bootstrap trust root fails.

### Contract Completeness Matrix

| Contract field group                                                                                                                                                                                                                                                                                                                                                                                                                                           | Canonical producer                                                                                                  | Contract schema/validator                                                                                                                                                                                                                                                               | Required verification                                                                                                                                                   |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `CloseoutHealthSnapshot` required fields (`schema_version`, `timestamp`, `mode_state`, `lane_obligations`, `blockers[]`, `degraded_findings[]`, `owner_assignments`, `freshness_policy_ref`, `promotion_decision`)                                                                                                                                                                                                                                             | `Infrastructure/scripts/runtime-separation/build_runtime_separation_current.py`                                                                       | `GOVERNANCE/runtime-separation/closeout-health-snapshot.schema.json` + `Infrastructure/scripts/validate_closeout_health_snapshot_contract.py`                                                                                                                                                          | `Infrastructure/scripts/testing/test_validate_all_runtime_separation.py`, `tests/test_validate_all_runtime_separation_integration.py`, `tests/test_validate_closeout_health_contracts.py`      |
| `closeout_health_reported` event (`schema_version`, `overall_state`, `blocked_count`, `degraded_count`, `freshness_policy_ref`, `promotion_decision`) plus companion counters artifact (`GOVERNANCE/runtime-separation/closeout-health-counters.json`: `lane_ready_count`, `lane_degraded_count`, `lane_blocked_count`, `installation_skill_coverage_ratio`, `inspector_resolution_ratio`, `blocker_metadata_completeness_ratio`, `freshness_windows_by_lane`) | closeout health event emitter path + companion counters writer                                                      | `GOVERNANCE/runtime-separation/closeout-health-event.schema.json` + `Infrastructure/scripts/validate_closeout_health_event_contract.py` + `GOVERNANCE/runtime-separation/closeout-health-counters.schema.json` validation + reference parity checks against `CloseoutHealthSnapshot` and policy inputs | `Infrastructure/scripts/testing/test_validate_all_runtime_separation.py`, `tests/test_validate_all_runtime_separation_integration.py`, `tests/test_validate_closeout_health_contracts.py`      |
| Blocking exception registry (normative, exact-match lifecycle-governed rows including `evidence_command`, `freshness_window_hours`, `expiry_policy`)                                                                                                                                                                                                                                                                                                           | `GOVERNANCE/runtime-separation/blocking-exceptions.registry.yaml`                                                   | `GOVERNANCE/runtime-separation/blocking-exceptions.schema.json`                                                                                                                                                                                                                         | `tests/test_ask_cli.py`, `tests/test_ask_repo_doctor_catalog.py`                                                                                                        |
| Rollout-mode implementation state (`pivot_rollout_mode`, `privacy_rollout_mode`)                                                                                                                                                                                                                                                                                                                                                                               | `GOVERNANCE/runtime-separation/rollout-state.json`                                                                  | `GOVERNANCE/runtime-separation/rollout-state.schema.json`                                                                                                                                                                                                                               | `tests/test_ask_atomic_promotion.py`, `tests/test_validate_all_runtime_separation_integration.py`                                                                       |
| Operating mode contract fields (`mode_owner`, `blocking_exceptions_ref`, posture + raw-root policy)                                                                                                                                                                                                                                                                                                                                                            | `Infrastructure/scripts/runtime-separation/build_runtime_separation_current.py`                                                                       | `GOVERNANCE/runtime-separation/current.schema.json` + `Infrastructure/scripts/validate_runtime_separation_current_contract.py`                                                                                                                                                                         | `Infrastructure/scripts/testing/test_validate_all_runtime_separation.py`, `tests/test_validate_all_runtime_separation_integration.py`                                                          |
| Lane-owner policy mapping                                                                                                                                                                                                                                                                                                                                                                                                                                      | `GOVERNANCE/runtime-separation/lane-owner-policy.yaml`                                                              | `GOVERNANCE/runtime-separation/lane-owner-policy.schema.json` + `Infrastructure/scripts/verify_runtime_policy_contracts.py` owner-resolution contract checks                                                                                                                                           | `Infrastructure/scripts/testing/test_validate_all_runtime_separation.py`, `tests/test_validate_all_runtime_separation_integration.py`, `tests/test_verify_runtime_policy_contracts.py`         |
| Freshness policy contract                                                                                                                                                                                                                                                                                                                                                                                                                                      | `GOVERNANCE/runtime-separation/freshness-policy.yaml`                                                               | `GOVERNANCE/runtime-separation/freshness-policy.schema.json` + `Infrastructure/scripts/verify_runtime_policy_contracts.py` freshness-reference contract checks                                                                                                                                         | `Infrastructure/scripts/testing/test_validate_all_runtime_separation.py`, `tests/test_validate_all_runtime_separation_integration.py`, `tests/test_verify_runtime_policy_contracts.py`         |
| Installation governance evidence                                                                                                                                                                                                                                                                                                                                                                                                                               | `GOVERNANCE/runtime-separation/installation-governance.json`                                                        | `GOVERNANCE/runtime-separation/installation-governance.schema.json`                                                                                                                                                                                                                     | `Infrastructure/scripts/testing/test_skill_lifecycle_validation.py`, `tests/test_ask_repo_doctor_catalog.py`                                                                                   |
| Privacy gate evidence (`sensitivity_scope`, classifier provenance, opaque source-binding token)                                                                                                                                                                                                                                                                                                                                                                | `GOVERNANCE/runtime-separation/privacy-gate-evidence.json`                                                          | `GOVERNANCE/runtime-separation/privacy-gate-evidence.schema.json` + trusted-classifier provenance checks                                                                                                                                                                                | `Infrastructure/scripts/testing/test_validate_all_runtime_separation.py`, `tests/test_validate_all_runtime_separation_integration.py`                                                          |
| Restricted encrypted sidecar interface contract (linkage fields, decrypt authority, audit/retention behavior)                                                                                                                                                                                                                                                                                                                                                  | `GOVERNANCE/runtime-separation/privacy-sidecar-contract.yaml` + restricted sidecar service implementation           | `GOVERNANCE/runtime-separation/privacy-sidecar-contract.schema.json` + `Infrastructure/scripts/verify_privacy_sidecar_contract.py`                                                                                                                                                                     | `Infrastructure/scripts/testing/test_validate_all_runtime_separation.py`, `tests/test_validate_all_runtime_separation_integration.py`, `tests/test_verify_privacy_sidecar_contract.py`         |
| Emitted outcome taxonomy (domain-classified literal registry)                                                                                                                                                                                                                                                                                                                                                                                                  | `GOVERNANCE/runtime-separation/outcome-taxonomy.yaml`                                                               | `GOVERNANCE/runtime-separation/outcome-taxonomy.schema.json` + `Infrastructure/scripts/verify_outcome_taxonomy_contract.py`                                                                                                                                                                            | `Infrastructure/scripts/testing/test_validate_all_runtime_separation.py`, `tests/test_validate_all_runtime_separation_integration.py`, `tests/test_verify_outcome_taxonomy_contract.py`        |
| Reader-compatibility companion metadata for independently versioned surfaces (`surface_id`, `surface_schema_version`, `minimum_reader_version`, `compatible_reader_range`, `metadata_generated_at`)                                                                                                                                                                                                                                                            | `Infrastructure/scripts/runtime-separation/build_runtime_separation_current.py` (single producer)                                                     | `GOVERNANCE/runtime-separation/reader-compatibility.schema.json` + `Infrastructure/scripts/runtime-separation/verify_runtime_separation_reader_compat.py`                                                                                                                                                                 | `Infrastructure/scripts/testing/test_validate_all_runtime_separation.py`, `tests/test_validate_all_runtime_separation_integration.py`, `tests/test_verify_runtime_separation_reader_compat.py` |
| JSON artifact backward-compatibility                                                                                                                                                                                                                                                                                                                                                                                                                           | `GOVERNANCE/runtime-separation/current.json` and consumer readers                                                   | `GOVERNANCE/runtime-separation/baseline.schema.json` plus `Infrastructure/scripts/validate_runtime_separation_current_contract.py` (dedicated post-build JSON contract validator)                                                                                                                      | `bash Infrastructure/scripts/validate_all.sh`, integration tests above                                                                                                                 |
| Runtime inventory digest integrity (`readers.yaml`, `path-consumers.yaml`, `.sha256`)                                                                                                                                                                                                                                                                                                                                                                          | `GOVERNANCE/runtime-separation/readers.yaml`, `GOVERNANCE/runtime-separation/path-consumers.yaml`                   | `Infrastructure/scripts/verify_runtime_inventory_digests.py` + digest parity rules                                                                                                                                                                                                                     | `Infrastructure/scripts/testing/test_validate_all_runtime_separation.py`, `tests/test_verify_runtime_inventory_digests.py`                                                                     |
| `ask` machine-readable response contract versioning (`ask_json_contract_version`)                                                                                                                                                                                                                                                                                                                                                                              | `bin/ask` + adapter handlers (`Infrastructure/scripts/lib/ask/commands/repo.py`, `wiki.py`, `skills.py`, `plugins.py`, `evals.py`) | `docs/cli-specs/ask-json-response.schema.json` + parity validators (`Infrastructure/scripts/validation-and-linting/verify_ask_cli.py`, `Infrastructure/scripts/validation-and-linting/verify_ask_cli_final.py`)                                                                                                                                                     | `tests/test_ask_cli.py`, `tests/test_ask_repo_doctor_catalog.py`                                                                                                        |
| `ask` rejection blocker-code registry parity                                                                                                                                                                                                                                                                                                                                                                                                                   | `docs/cli-specs/ask-blocker-codes.yaml` + `bin/ask` deny-path mappers                                               | blocker-code registry validation + deterministic cross-registry mapping checks (runtime `blocker_code` -> ask blocker diagnostics) in `Infrastructure/scripts/validation-and-linting/verify_ask_cli.py` and `Infrastructure/scripts/validation-and-linting/verify_ask_cli_final.py`                                                                                 | `tests/test_ask_cli.py`, `tests/test_ask_repo_doctor_catalog.py`                                                                                                        |
| `ask` v1 compatibility entitlement/sunset policy                                                                                                                                                                                                                                                                                                                                                                                                               | `docs/cli-specs/ask-v1-compat-policy.yaml`                                                                          | `docs/cli-specs/ask-v1-compat-policy.schema.json` + compatibility policy checks in `Infrastructure/scripts/validation-and-linting/verify_ask_cli.py` and `Infrastructure/scripts/validation-and-linting/verify_ask_cli_final.py`                                                                                                                                    | `tests/test_ask_cli.py`, `tests/test_ask_repo_doctor_catalog.py`                                                                                                        |
| Privacy required-check normalization for lane-scoped `not_applicable` handling                                                                                                                                                                                                                                                                                                                                                                                 | `Infrastructure/scripts/validate_wiki_privacy_gate.py` + `Infrastructure/scripts/validation-and-linting/verify_selection_gate_severity.py`                               | `GOVERNANCE/runtime-separation/privacy-required-check-normalization.schema.json` + provenance/policy-bundle verification gates                                                                                                                                                          | `Infrastructure/scripts/testing/test_validate_all_runtime_separation.py`, `tests/test_validate_all_required_check_parity.py`                                                                   |
| Governance artifact provenance and integrity                                                                                                                                                                                                                                                                                                                                                                                                                   | all canonical runtime governance artifacts                                                                          | `Infrastructure/scripts/verify_runtime_artifact_provenance.py` + `GOVERNANCE/runtime-separation/provenance-trust-policy.yaml`                                                                                                                                                                          | `bash Infrastructure/scripts/validate_all.sh`, `tests/test_validate_all_runtime_separation_integration.py`                                                                             |
| Governance policy-bundle bootstrap integrity                                                                                                                                                                                                                                                                                                                                                                                                                   | mutable policy artifacts consumed by runtime gates                                                                  | `Infrastructure/scripts/verify_runtime_policy_bundle_integrity.py` + `GOVERNANCE/runtime-separation/policy-bundle.lock.json`                                                                                                                                                                           | `bash Infrastructure/scripts/validate_all.sh`, `tests/test_validate_all_runtime_separation_integration.py`                                                                             |
| Scoped required-check declaration/mapping policy                                                                                                                                                                                                                                                                                                                                                                                                               | `GOVERNANCE/runtime-separation/required-check-scope.yaml`                                                           | `GOVERNANCE/runtime-separation/required-check-scope.schema.json` + provenance/policy-bundle verification gates                                                                                                                                                                          | `bash Infrastructure/scripts/validate_all.sh`, `tests/test_validate_all_required_check_parity.py`                                                                                      |
| Required-check bootstrap guard set (immutable validator self-protection)                                                                                                                                                                                                                                                                                                                                                                                       | `GOVERNANCE/runtime-separation/required-check-bootstrap.yaml`                                                       | `GOVERNANCE/runtime-separation/required-check-bootstrap.schema.json` + read-only bootstrap loader checks                                                                                                                                                                                | `Infrastructure/scripts/testing/test_validate_all_runtime_separation.py`, `tests/test_validate_all_required_check_parity.py`                                                                   |
| Required-check declaration parity for runtime-pivot-owned checks                                                                                                                                                                                                                                                                                                                                                                                               | `.harness/ci-required-checks.json` subset declared by runtime-pivot scope map                                       | `Infrastructure/scripts/verify_required_check_enforcement.py` + `GOVERNANCE/runtime-separation/required-check-scope.yaml`                                                                                                                                                                              | `bash Infrastructure/scripts/validate_all.sh`, `tests/test_validate_all_required_check_parity.py`                                                                                      |
| Required-check parity evidence artifacts (`required-check-enforcement.local.json`, `required-check-enforcement.live.json`)                                                                                                                                                                                                                                                                                                                                     | `Infrastructure/scripts/verify_required_check_enforcement.py`                                                                      | `GOVERNANCE/runtime-separation/required-check-enforcement.local.schema.json` + `GOVERNANCE/runtime-separation/required-check-enforcement.live.schema.json` + live-freshness validation (`generated_at`, `fresh_until`, `scope_hash`, `parity_mode=live`)                                | `Infrastructure/scripts/testing/test_validate_all_runtime_separation.py`, `tests/test_validate_all_required_check_parity.py`                                                                   |
| Non-pivot required-check preservation parity (deletions/renames outside pivot scope)                                                                                                                                                                                                                                                                                                                                                                           | `Infrastructure/scripts/verify_required_check_enforcement.py` complete inventory comparator                                        | full-inventory parity checks against pre-existing required checks in workflow/ruleset state and `.harness/ci-required-checks.json`                                                                                                                                                      | `tests/test_validate_all_required_check_parity.py`                                                                                                                      |
| Derived scoped required-check intermediate artifact (`required-check-derived-scoped.json`)                                                                                                                                                                                                                                                                                                                                                                     | `Infrastructure/scripts/verify_required_check_enforcement.py` (sole producer)                                                      | `GOVERNANCE/runtime-separation/required-check-derived-scoped.schema.json`                                                                                                                                                                                                               | `Infrastructure/scripts/testing/test_validate_all_runtime_separation.py`, `tests/test_validate_all_required_check_parity.py`                                                                   |

## Implementation Units

### Sequencing and Gate Rules

- This sequencing is execution-planning guidance (how to implement safely) and not an expansion of the normative spec contract model.
- Rollout-mode checkpoints in P4-P6 (`pivot_rollout_mode`, `privacy_rollout_mode`) are implementation deployment controls only; they gate state-transition eligibility and operator cutover safety, but they must not redefine normative spec entities or replace AC-based acceptance criteria.
- Phase advancement is strict: `P0 -> P1 -> P2 -> P3 -> P4 -> P5 -> P6`.
- P0 executes as two internal checkpoints to reduce blast radius:
  - `P0A`: runtime/control-plane schema+state contracts and restore coverage.
  - `P0B`: wiki boundary, provenance/policy bootstrap integrity, and redaction boundary checks.
- P0A checkpoint exit criteria must pass before P0B begins; P0 phase completion requires both checkpoint exits.
- Do not begin a downstream phase until the current phase exit criteria are met and corresponding tests pass.
- For each phase, land contract shape updates and regression coverage together to avoid partial-governance states.
- If any phase introduces a new blocker class, promotion defaults to blocked until comparator and reporting layers both recognize the class.
- P0 must establish canonical ownership and schema/version checks for closeout fields, blocking exceptions, rollout-state artifacts, and JSON compatibility before downstream phase work begins.
- P0 must enforce canonical wiki-root boundary validation as a blocking prerequisite for all downstream phases.
- P0 must also reconcile legacy wiki command/lint surfaces to one resolver policy with one writable wiki plane and explicitly append-only raw evidence planes.
- Required-check policy ownership is phase-split intentionally: P0 establishes immutable bootstrap guard-set contracts only (`required-check-bootstrap.*`), P4 is the first phase allowed to introduce and mutate scoped required-check mapping policy (`required-check-scope.*`), and P5 may perform additive privacy-gate mapping updates only (no rewrites of existing non-privacy mappings).
- P5 privacy-gate updates to `required-check-scope.*` are declaration/mapping-only for CI parity; privacy `not_applicable` pass-equivalence semantics remain exclusively owned by `privacy-required-check-normalization.*`, with no alternate owner path.
- P0A execution order in `validate_all.sh` is strict: verify policy-bundle integrity + artifact provenance first, then run runtime artifact build/compare; any provenance/integrity failure hard-stops before artifact production.
- P0A must apply redaction at the log-capture sink before command stdout/stderr bytes are persisted to logs/TSV artifacts, and promotion-authoritative `evidence_ref` digests must be computed from that same persisted redacted stream.
- File action legend for this plan: `Modify` means create-or-update (create if missing), `Generate` means generated-only runtime output, and `Test` entries may be new or existing test files updated in-phase.

- [ ] **P0 / Unit 1: Pivot Contract Surface and Artifact Schema Wiring**

**Goal:** Add machine-readable fields required by the pivot spec to runtime-separation current/closeout artifacts and fixture schemas.

**Requirements:** R1-R6, R10-R11, R14-R16, R20

**Dependencies:** None

**Files:**

- Modify: `Infrastructure/scripts/runtime-separation/build_runtime_separation_current.py`
- Modify: `Infrastructure/scripts/set_runtime_rollout_state.py` (canonical rollout-state writer established before downstream phases)
- Modify: `Infrastructure/scripts/runtime-separation/compare_runtime_separation_baseline.py`
- Modify: `Infrastructure/scripts/validate_runtime_separation_current_contract.py` (new dedicated post-build JSON contract validator)
- Modify: `Infrastructure/scripts/validate_closeout_health_snapshot_contract.py` (new dedicated snapshot-contract validator for independently versioned closeout snapshot surface)
- Modify: `Infrastructure/scripts/validate_closeout_health_event_contract.py` (new dedicated event-contract validator for independently versioned closeout event surface)
- Modify: `Infrastructure/scripts/validate_all.sh` (enforce provenance/policy-bundle verification before runtime build/compare, apply capture-time redaction at log sink, invoke JSON contract validator after artifact generation, and include new artifacts in restore set)
- Modify: `Infrastructure/scripts/verify_runtime_artifact_provenance.py` (new trusted-provenance validator for canonical governance artifacts)
- Modify: `Infrastructure/scripts/verify_runtime_policy_bundle_integrity.py` (new bootstrap validator that verifies lock/signature for mutable policy artifacts before load)
- Modify: `Infrastructure/scripts/verify_runtime_policy_contracts.py` (new canonical schema/reference validator for lane-owner and freshness policy contracts)
- Modify: `Infrastructure/scripts/runtime-separation/verify_runtime_separation_reader_compat.py` (canonical validator for `reader-compatibility.json` companion metadata against surface schema versions)
- Modify: `Infrastructure/scripts/verify_runtime_log_redaction.py` (new validator that enforces allowlist/redaction on all validator and workflow emit surfaces)
- Modify: `Infrastructure/scripts/verify_runtime_inventory_digests.py` (canonical digest ownership/validation gate for `readers.yaml`, `path-consumers.yaml`, and `.sha256` artifacts)
- Modify: `Infrastructure/scripts/verify_privacy_sidecar_contract.py` (new canonical sidecar interface validator for linkage/decrypt-authority/audit-retention guarantees)
- Modify: `Infrastructure/scripts/verify_outcome_taxonomy_contract.py` (new canonical outcome-taxonomy validator across validator and ask emit surfaces)
- Modify: `Infrastructure/scripts/validate_wiki_authority_boundary.py` (new canonical wiki-root boundary validator for scaffold and path-ownership contracts)
- Modify: `Infrastructure/scripts/validation-and-linting/check_path_ownership_boundaries.sh` (enforce wiki/raw ownership boundary and ingest-only raw write allowances)
- Modify: `Infrastructure/scripts/lib/ask/commands/wiki.py` (single wiki-root resolver path normalization plus raw evidence provenance/opaque source-binding token emission)
- Modify: `Infrastructure/scripts/lib/ask/commands/repo.py` (deprecate unredacted `raw_output` passthrough from default machine-readable surfaces; retain explicit v1 compatibility shim while v2 emits redacted structured evidence only)
- Modify: `docs/cli-specs/ask-json-response.schema.json` (land ask v1/v2 contract-selection schema updates in same phase as emit-surface changes)
- Modify: `Infrastructure/scripts/validation-and-linting/verify_ask_cli.py` (cover v1/v2 selector + downgrade-denial behavior in same phase as ask emit changes)
- Modify: `Infrastructure/scripts/validation-and-linting/verify_ask_cli_final.py` (cover v1/v2 selector + sunset enforcement in same phase as ask emit changes)
- Modify: `Infrastructure/scripts/validation-and-linting/wiki_lint.py` (single wiki-root resolver path normalization)
- Modify: `docs/skill-ops-wiki/README.md` (canonical resolver-path ownership guidance)
- Modify: `docs/skill-ops-wiki/raw/README.md` (append-only raw-plane ownership and restricted sidecar evidence boundary guidance)
- Modify: `docs/skill-ops-wiki/wiki/index.md` (canonical wiki-root declaration alignment, if drift exists)
- Modify: `docs/skill-ops-wiki/wiki/log.md` (canonical operation boundary alignment, if drift exists)
- Modify: `docs/agents/14-path-ownership-boundaries.md` (wiki-root ownership boundary enforcement guidance)
- Modify: `GOVERNANCE/runtime-separation/baseline.schema.json`
- Modify: `GOVERNANCE/runtime-separation/current.schema.json`
- Modify: `GOVERNANCE/runtime-separation/closeout-health-snapshot.schema.json`
- Modify: `GOVERNANCE/runtime-separation/closeout-health-event.schema.json`
- Modify: `GOVERNANCE/runtime-separation/blocking-exceptions.registry.yaml`
- Modify: `GOVERNANCE/runtime-separation/blocking-exceptions.schema.json`
- Generate: `GOVERNANCE/runtime-separation/rollout-state.json` (mutated only via `Infrastructure/scripts/set_runtime_rollout_state.py`; never hand-edited)
- Modify: `GOVERNANCE/runtime-separation/rollout-state.schema.json`
- Modify: `GOVERNANCE/runtime-separation/lane-owner-policy.yaml`
- Modify: `GOVERNANCE/runtime-separation/lane-owner-policy.schema.json`
- Modify: `GOVERNANCE/runtime-separation/freshness-policy.yaml`
- Modify: `GOVERNANCE/runtime-separation/freshness-policy.schema.json`
- Modify: `GOVERNANCE/runtime-separation/readers.yaml`
- Modify: `GOVERNANCE/runtime-separation/path-consumers.yaml`
- Modify: `GOVERNANCE/runtime-separation/slices.yaml`
- Modify: `GOVERNANCE/runtime-separation/required-check-bootstrap.yaml` (immutable bootstrap required-check guard-set source; read-only at runtime)
- Modify: `GOVERNANCE/runtime-separation/required-check-bootstrap.schema.json`
- Modify: `GOVERNANCE/runtime-separation/provenance-trust-policy.yaml`
- Modify: `GOVERNANCE/runtime-separation/sensitivity-classification-policy.yaml`
- Modify: `GOVERNANCE/runtime-separation/privacy-sidecar-contract.yaml`
- Modify: `GOVERNANCE/runtime-separation/privacy-sidecar-contract.schema.json`
- Modify: `GOVERNANCE/runtime-separation/outcome-taxonomy.yaml`
- Modify: `GOVERNANCE/runtime-separation/outcome-taxonomy.schema.json`
- Modify: `GOVERNANCE/runtime-separation/policy-bundle.lock.json`
- Modify: `GOVERNANCE/runtime-separation/reader-compatibility.schema.json`
- Modify: `GOVERNANCE/runtime-separation/installation-governance.schema.json`
- Modify: `GOVERNANCE/runtime-separation/closeout-health-counters.schema.json`
- Generate: `GOVERNANCE/runtime-separation/current.json` (generated-only output via canonical writer, never hand-edited)
- Generate: `GOVERNANCE/runtime-separation/closeout-health-counters.json` (generated-only companion counters artifact, never hand-edited)
- Generate: `GOVERNANCE/runtime-separation/reader-compatibility.json` (generated-only companion compatibility artifact, never hand-edited)
- Test: `Infrastructure/scripts/testing/test_validate_all_runtime_separation.py`
- Test: `tests/test_validate_all_runtime_separation_integration.py`
- Test: `tests/test_validate_all_restore_manifest.py` (new failing-run restore coverage for all mutable governance artifacts)
- Test: `tests/test_validate_wiki_authority_boundary.py` (new canonical wiki-root boundary validation tests)
- Test: `tests/test_path_ownership_boundaries_wiki_contract.py` (new ownership-gate enforcement tests for wiki/raw boundary)
- Test: `tests/test_verify_runtime_artifact_provenance.py` (new regression coverage for trusted-provenance gate)
- Test: `tests/test_verify_runtime_policy_bundle_integrity.py` (new regression coverage for policy-bundle bootstrap integrity gate)
- Test: `tests/test_verify_runtime_policy_contracts.py` (new regression coverage for lane-owner/freshness schema/reference contract checks)
- Test: `tests/test_verify_runtime_separation_reader_compat.py` (new regression coverage for reader-compatibility companion artifact and surface-version parity)
- Test: `tests/test_verify_runtime_log_redaction.py` (new regression coverage for schema-preserving redaction contract)
- Test: `tests/test_verify_runtime_inventory_digests.py` (new regression coverage for inventory digest ownership and drift rejection)
- Test: `tests/test_verify_privacy_sidecar_contract.py` (new regression coverage for sidecar interface/access/audit/retention contract enforcement)
- Test: `tests/test_verify_outcome_taxonomy_contract.py` (new regression coverage for domain-classified emitted outcome literals)
- Test: `tests/test_ask_cli.py` (v1/v2 contract-selection, allowlist entitlement, and sunset enforcement regression coverage)
- Test: `tests/test_validate_closeout_health_contracts.py` (independent snapshot/event schema-version and compatibility metadata contract coverage)
- Test: `tests/test_set_runtime_rollout_state_authz.py` (new regression coverage for authenticated/attested rollout-state write authorization boundary)

**Approach:**

- Execute P0 as two independently releasable checkpoints with distinct rollback manifests and gates: `P0A` (runtime/control-plane schema+state+reader-compat artifacts) and `P0B` (ask/wiki boundary + provenance/policy + redaction). `P0A` checkpoint exit is the only prerequisite for starting `P0B`; full P0 exit requires both checkpoints.
- Extend normalized artifact generation with lifecycle state contract scaffolding, freshness metadata, exception-match metadata, blocker completeness metrics, and all spec-required `CloseoutHealthSnapshot` fields; full deterministic lane-result evaluation remains P2-owned.
- Introduce a shared redaction/allowlist helper in the artifact producer path and require all intermediate artifact/log serialization routes to use it before writing diagnostics.
- Require the same shared redaction helper for all emit points, including validator stderr/stdout captures and workflow annotations; redaction must happen in the capture wrapper before persistence to log/TSV sinks. Machine-readable outputs (for example `ask repo status --json`) must use schema-preserving field-level redaction with an explicit required-field allowlist so contract keys remain intact.
- Pin digest-source semantics explicitly: promotion-authoritative `evidence_ref` values are computed from the persisted redacted stream only; optional raw-stream digests (if collected for operator forensics) are non-authoritative, must remain outside git-backed artifacts, and cannot satisfy promotion gates.
- Extend the same redaction contract in P0 to the adapters changed in P0 (`repo`, `wiki`) so default v2 machine-readable outputs never expose unredacted `raw_output`/`raw_error` passthrough fields; P3 extends the same contract to remaining passthrough-capable adapters (`skills`, `plugins`, `evals`) before promotion-ready state is allowed.
- Enforce the canonical wiki boundary as a two-plane contract (`docs/skill-ops-wiki/wiki/*` writable synthesis, `docs/skill-ops-wiki/raw/*` append-only evidence via approved ingest commands) with a dedicated validator so source-of-truth ownership is machine-checked, not prose-only.
- Enforce the same wiki/raw ownership boundary in the canonical repo ownership gate (`Infrastructure/scripts/validation-and-linting/check_path_ownership_boundaries.sh`) so bypassing the dedicated wiki validator still fails closed.
- Normalize all wiki entrypoints (`ask wiki` commands and `wiki_lint`) through one resolver policy, and block if more than one writable synthesis plane is configured or if raw evidence writes bypass approved ingest pathways.
- Enforce a hard writer boundary for `docs/skill-ops-wiki/raw/`: direct/manual writes are denied by policy and file-ownership controls; only approved ingest command paths can append, and non-ingest writes fail before validation.
- For sensitive-source scope, require deterministic classification/redaction before any repo write, and keep unredacted source material outside git-backed storage.
- Require every ingested raw evidence entry to carry source-inventory keyed-HMAC binding tokens scoped per tenant and per run/rotation-epoch, plus signed/attested provenance metadata, before downstream gates can consume it.
- Raw evidence metadata persistence is minimized to schema-allowlisted fields only; cross-run stable correlation identifiers are forbidden in git-backed artifacts. Scoped keyed-HMAC tokens must rotate by policy-defined epoch, and token-to-source lookup material remains outside git-backed storage with bounded retention.
- Update raw evidence ingest producers (`ask wiki` path) so required provenance/hash-binding fields are emitted at write time; consumers fail closed when producer-side evidence fields are missing.
- Establish `set_runtime_rollout_state.py` as the only persistent rollout-state writer in P0 so later phases consume an already-enforced single-writer boundary.
- Pin canonical registry/state artifacts (`blocking-exceptions.registry.yaml`, `rollout-state.json`) with explicit schema versioning and owner contracts.
- Keep schema additions backward-safe with a versioned runtime artifact migration (`baseline.schema.json` compatibility checks plus `current.schema.json` envelope checks and dedicated closeout snapshot/event schema checks), and enforce consumer compatibility via dedicated post-build validators (`validate_runtime_separation_current_contract.py`, `validate_closeout_health_snapshot_contract.py`, `validate_closeout_health_event_contract.py`).
- Emit and validate reader-compatibility metadata through canonical companion artifact `GOVERNANCE/runtime-separation/reader-compatibility.json` (`surface_id`, `surface_schema_version`, `minimum_reader_version`, `compatible_reader_range`, `metadata_generated_at`) for each independently versioned closeout surface (`current.json` envelope, `CloseoutHealthSnapshot`, `closeout_health_reported`) before promotion-ready output is allowed.
- Enforce trusted provenance checks on canonical governance artifacts before any comparator, gate, or closeout consumer accepts them, with issuer/key allowlists, expiry windows, and revocation policy from `provenance-trust-policy.yaml`.
- Verify mutable policy artifacts against `policy-bundle.lock.json` before policy load, and verify the lock/signature against the immutable bootstrap trust root so trust-policy or classifier-policy tampering cannot redefine verifier acceptance criteria.
- Enforce schema/reference validity of `lane-owner-policy.yaml` and `freshness-policy.yaml` through `Infrastructure/scripts/verify_runtime_policy_contracts.py` before lane emission or closeout consumption; invalid/missing policy contracts fail closed.
- Wire `validate_all.sh` so provenance/policy-bundle checks run before `build_runtime_separation_current.py` and `compare_runtime_separation_baseline.py` are allowed to execute, and rewrite preflight control flow so any failed pre-build trust check exits non-zero immediately (no artifact build/compare side effects after a failed trust gate).
- Re-verify artifact provenance/trust after build and before compare/closeout consumption so generated artifacts cannot be consumed from an untrusted post-build state.
- Keep digest inputs (`readers.yaml`, `path-consumers.yaml`, and derived `.sha256` files) owned and validated in this phase through `Infrastructure/scripts/verify_runtime_inventory_digests.py` so rollback coverage is end-to-end.
- Enforce rollout-state transition authorization in `set_runtime_rollout_state.py`: each write must carry authenticated caller identity + signed transition attestation bound to approved phase transition labels; identity or attestation failures block mutation.
- Resolve bootstrap circularity explicitly in `set_runtime_rollout_state.py`: initial `--bootstrap-init` write is a distinct trust-root-anchored path that creates the first signed state record, after which all subsequent transitions must verify prior-state signature chain continuity; missing/invalid prior signature chain blocks mutation.
- Enforce replay-safe transition semantics in `set_runtime_rollout_state.py`: bootstrap and transition requests must include one-time nonce + issued-at freshness checks + monotonic expected-state sequence checks and expected-state digest optimistic-concurrency checks, with durable writer-side nonce+sequence registries; replayed/stale requests, stale/non-monotonic sequence requests, and stale-state writes fail closed before mutation.
- Keep `build_runtime_separation_current.py` as the single lane-result producer boundary; helper-module extraction is allowed for maintainability, but no second producer may compute lane results or closeout policy outcomes.
- Couple `closeout-health-counters.json` version semantics to closeout surfaces in this phase: counters writer and validators enforce major-version parity with `closeout_health_reported` and snapshot schema policy before any promotion-ready output can be emitted.
- Introduce and validate canonical emitted outcome taxonomy in this phase (`outcome-taxonomy.yaml`) so blocker codes, lane states, privacy states, and rollout states are domain-scoped and non-ambiguous across scripts and ask surfaces.

**Patterns to follow:**

- Existing normalized command-check shaping and issue derivation in `Infrastructure/scripts/runtime-separation/build_runtime_separation_current.py`.
- Existing blocker-class comparator semantics in `Infrastructure/scripts/runtime-separation/compare_runtime_separation_baseline.py`.

**Test scenarios:**

- Artifact includes schema-valid lane-obligation container scaffolding for lanes 1/2/4 required by downstream P2 evaluation.
- Comparator honors blocker precedence and exception matching without false positives.
- Lane-4 exception matching fails closed when duplicate selector tuples (`exception_code`, `lane_id`, `blocker_code`, `owner_role`) exist in the registry.
- JSON artifact compatibility check fails when required `current.json` contract fields drift or are removed.
- Ask contract-selection checks fail when v1 is requested without explicit selector + allowlist entitlement, after `legacy_contract_v1_sunset_at`, or when companion reader-compatibility metadata is stale/missing for the selected contract surface.
- Log/error-path redaction checks fail when sensitive fields appear in unredacted validator or workflow output.
- Ask-adapter JSON checks fail when `raw_output`/`raw_error` channels expose sensitive content or bypass schema-preserving redaction.
- Secret-bearing output from a failing validator command never persists unredacted to log files, TSV artifacts, or workflow annotations.
- Wiki authority boundary checks fail when canonical wiki-root scaffold or path-ownership rules drift.
- Policy-bundle integrity checks fail when mutable policy artifact digests/signatures drift from the canonical lock file.
- Wiki command/lint entrypoints fail when they do not resolve through the same resolver policy (one writable wiki plane plus append-only raw evidence planes).
- Sensitive-source ingest fails before repo persistence when classification/redaction evidence is missing or when raw entry provenance hash/signature binding is absent.
- Sensitive-source ingest producer tests fail when required provenance/hash-binding fields are not emitted in raw evidence entries.
- Bootstrap-init state transition tests fail closed when trust-root bootstrap metadata is missing/invalid or when first-write attempts occur after state already exists.
- Transition-write tests fail closed on replayed nonce, stale request timestamp, stale/non-monotonic `expected_state_sequence`, or mismatched `expected_state_digest`.
- Restore/rollback replay-continuity tests fail closed when nonce/sequence ledgers are rewound or reused without signed re-seed/epoch-advance evidence.
- Pre-build trust-gate failure tests verify `validate_all.sh` exits non-zero before any runtime artifact build/compare step executes.

**Verification:**

- Runtime-separation current artifact builds and compares deterministically.

**Verification oracles:**

- Artifact includes full `CloseoutHealthSnapshot` required field set and schema-valid lane-obligation container scaffolding required by the spec contract; deterministic lane-result computation semantics are validated in P2.
- Closeout counters include `lane_ready_count`, `lane_degraded_count`, and `lane_blocked_count` in addition to ratio metrics.
- Companion counters artifact `GOVERNANCE/runtime-separation/closeout-health-counters.json` is schema-valid against `closeout-health-counters.schema.json` and includes deterministic `freshness_windows_by_lane` values resolved from the referenced freshness policy.
- Comparator output is stable for unchanged baseline inputs.
- Generated artifact is reproducible via `python3 Infrastructure/scripts/runtime-separation/build_runtime_separation_current.py` with no manual patching.
- Registry and rollout-state schema checks fail closed on version/shape drift.
- JSON contract validation runs after artifact generation and fails closed on missing required fields or incompatible shape changes.
- Reader-compatibility validator (`Infrastructure/scripts/runtime-separation/verify_runtime_separation_reader_compat.py`) fails closed when any required surface record is missing, stale, or incompatible with declared `schema_version` policy.
- `validate_all.sh` blocks runtime artifact build/compare when policy-bundle or provenance verification fails pre-build.
- `validate_all.sh` pre-build trust gates are hard-stop gates: failure exits immediately and no runtime artifact generation/compare side effects occur.
- `validate_all.sh` blocks generated-artifact compare/closeout consumption when post-build provenance/trust rechecks fail.
- `validate_all.sh` restore/rollback manifest for P0 must be complete against the full P0 mutator set (all `Modify` + `Generate` entries in P0 Files), including mutators previously prone to omission (`Infrastructure/scripts/runtime-separation/build_runtime_separation_current.py`, `Infrastructure/scripts/runtime-separation/compare_runtime_separation_baseline.py`, `Infrastructure/scripts/validate_all.sh`, `Infrastructure/scripts/verify_runtime_artifact_provenance.py`, `Infrastructure/scripts/verify_runtime_policy_bundle_integrity.py`, `Infrastructure/scripts/validation-and-linting/wiki_lint.py`) in addition to all artifact/schema/policy files and replay ledgers listed for P0; P4/P5 append their own newly introduced artifacts and required-check workflow/declaration surfaces at their phase boundaries.
- Manifest completeness is test-enforced: `tests/test_validate_all_restore_manifest.py` must diff the P0 restore manifest against the P0 Files mutator inventory and fail on any missing/extra entry until both sets match exactly.
- Rollback coverage also includes pivot-owned executable/profile, resolver-boundary, and required-check governance assets introduced up to the active phase through a git-backed rollback recipe with integrity checks; P0 covers only P0-introduced assets, with later-phase assets appended when introduced.
- Replay/concurrency continuity checks fail closed when rollback/restore reuses or rewinds nonce/sequence state without signed ledger epoch advancement; restored environments must prove nonce/sequence ledger continuity before accepting new transition writes.
- Artifact provenance validator fails closed when generator identity or digest proof is missing/invalid, or when issuer/key state violates `provenance-trust-policy.yaml` allowlist/rotation/revocation rules.
- Lane-owner and freshness-policy artifacts are schema-valid (`lane-owner-policy.schema.json`, `freshness-policy.schema.json`) and pass `verify_runtime_policy_contracts.py` before lane-result emission or P6 activation preconditions are considered contract-complete.
- Outcome-taxonomy validator fails closed when emitted literals are unregistered, cross-domain, or ambiguously classified.
- Persistent-run restore coverage test proves `validate_all.sh` restores the phase-owned manifest after a forced failure (P0 baseline set in this unit, then P4/P5-expanded manifests in later units) and validates rollback integrity for pivot-owned executable/profile, resolver-boundary, and required-check governance assets introduced up to the active phase via a git-backed rollback recipe.
- Canonical wiki-boundary validator passes only when wiki-root scaffold/path-ownership contracts are satisfied.

**Failure stop conditions:**

- Reader-compat, JSON artifact-compatibility, or schema validation failures block progression to P1.

**Exit criteria:** AC1, AC4, AC9 (plus AC3 prerequisites only; full AC3 delivery is gated in P2), and both P0 checkpoint exits verified: P0A controls (`rollout-state`/registry schema+version checks, reader-compatibility validation, restore coverage) and P0B hard-stop controls (`wiki/raw` boundary validator pass, pre-build provenance/policy bootstrap pass with immediate-stop semantics, capture-time redaction validator pass).

- [ ] **P1 / Unit 2: Installation Governance Fail-Closed Gates**

**Goal:** Enforce required skill stack and inspector-resolution evidence before promotion readiness can be reported.

**Requirements:** R19-R22, R10, R13

**Dependencies:** P0

**Files:**

- Modify: `Infrastructure/scripts/validation-and-linting/verify_skill_catalog_freshness.py`
- Modify: `Infrastructure/scripts/lib/runtime_policy/installation_governance.py` (new policy module used by gate wrappers)
- Modify: `Infrastructure/scripts/lib/runtime_policy/fallback_execution_boundary.py` (new restricted execution profile wrapper enforcing read-only/redacted-input/no-canonical-write constraints)
- Modify: `Infrastructure/scripts/run_fallback_inspector.sh` (single mandatory launcher for fallback inspector execution)
- Modify: `Infrastructure/scripts/runtime_policy/fallback_inspector.sb` (macOS sandbox profile consumed by fallback launcher)
- Modify: `Infrastructure/scripts/runtime_policy/fallback_inspector.bwrap` (Linux bubblewrap profile consumed by fallback launcher/CI)
- Modify: `Infrastructure/scripts/runtime_policy/fallback_inspector.env.allowlist` (minimal inherited environment contract for fallback execution)
- Modify: `Infrastructure/scripts/validate_all.sh`
- Modify: `Infrastructure/scripts/validation-and-linting/verify-work.sh`
- Modify: `GOVERNANCE/runtime-separation/installation-governance.json`
- Modify: `GOVERNANCE/runtime-separation/installation-governance.schema.json`
- Test: `Infrastructure/scripts/testing/test_skill_lifecycle_validation.py`
- Test: `tests/test_ask_repo_doctor_catalog.py`
- Test: `tests/test_fallback_execution_boundary.py` (read-only/write-deny/network-deny/process-deny/env-allowlist boundary coverage)
- Test: `tests/test_run_fallback_inspector_launcher.py` (launcher-only execution, tamper rejection, and attestation coverage)

**Approach:**

- Add explicit checks for required-skill presence and inspector availability/fallback resolution in governance lane checks, with policy evaluation implemented in a dedicated helper module to avoid coupling policy and evidence serialization concerns.
- Emit deterministic blocker codes and owner metadata when checks fail.
- Constrain fallback inspector roles to read-only audit/evidence generation over pre-redacted artifacts only; fallback roles cannot access raw sensitive sources, cannot write canonical outputs, and do not change promotion authorization policy.
- Keep fallback execution-boundary enforcement as an adapter under canonical gate ownership: fallback launcher/profile checks are invoked only through `Infrastructure/scripts/lib/runtime_policy/installation_governance.py` as consumed by `validate_all.sh`/`verify-work.sh`, and cannot introduce an independent promotion authority path.
- Persist installation-governance decision evidence into canonical `installation-governance.json` so role-resolution and skill-coverage outcomes are replayable in closeout.
- Enforce fallback execution boundaries through a dedicated restricted execution profile (read-only FS view, redacted-input allowlist, canonical-write denylist) rather than policy text alone.
- Route all fallback inspector execution through one audited launcher path (`run_fallback_inspector.sh`) with platform-specific backend selection (`sandbox-exec` + `.sb` on macOS, `bubblewrap` + `.bwrap` on Linux/CI); non-launcher fallback execution attempts are blocking.
- Fallback execution boundary support matrix is explicit and fail-closed: supported hosts are macOS (`sandbox-exec`) and Linux/CI (`bubblewrap`); unsupported hosts emit deterministic blocker `blocked_inspector_boundary_unsupported` and cannot produce ready/promotion-authoritative installation evidence.
- Enforce network/process-deny controls inside fallback sandbox profiles; any outbound network attempt or unsanctioned child-process spawn is a blocking violation.
- Enforce a scrubbed runtime environment for fallback execution (minimal allowlist only), clearing ambient secret-bearing vars/sockets/tokens before process launch; any env-contract drift is blocking.
- Require launcher-level runtime attestation probes (`fs_read_only`, `cwd_write_probe_blocked`, `canonical_write_probe_blocked`, `redacted_input_attested`, `env_allowlist_enforced`) and fail closed when any attestation bit is missing.
- Pin launcher/profile bundle integrity before execution (digest/signature validation), and fail closed on path/env/argv tampering.
- Raw evidence + provenance sidecar persistence from fallback execution uses one atomic write boundary (temp-file + fsync + rename) so evidence and sidecar cannot diverge under partial failures.
- Apply strict allowlist serialization to `installation-governance.json` fields; when stable linkage is required use keyed HMAC tokens only (no raw values and no unkeyed hashes), with minimum persisted fields defined in schema.
- Keyed HMAC tokens must use keys external to repo-managed artifacts, but promotion-authoritative evidence must be signed/attested with CI-managed keys only; local secure keychain keys are restricted to non-authoritative preview diagnostics and cannot satisfy promotion gating.
- Keep new launcher/profile assets dark by default behind rollout-state-controlled activation flags, and define rollback procedure for these executable/profile files alongside artifact rollback checks before phase exit.

**Patterns to follow:**

- Existing readiness classification and metadata diagnostics in `Infrastructure/scripts/validation-and-linting/verify_skill_catalog_freshness.py`.

**Test scenarios:**

- Missing one required skill blocks with deterministic code.
- Missing inspector roles with no fallback blocks; valid fallback path passes evidence-generation checks with recorded rationale, while promotion authorization remains governed by explicit policy markers (`role_resolution_policy`, `role_resolution_evidence`).
- Fallback inspector path fails closed if `read_only`, `redacted_input_only`, or `no_canonical_write` cannot be proven from gate evidence.
- Negative test: fallback role attempt to consume raw sensitive input or write canonical output is blocked deterministically.
- Negative test: invoking fallback inspector logic outside `run_fallback_inspector.sh` is rejected and recorded as a blocking governance violation.
- Negative test: runtime attestation probes detect writable CWD or canonical output path and force blocking classification.
- Negative test: fallback sandbox blocks outbound network and unsanctioned child-process spawn attempts.
- Negative test: fallback launcher blocks inherited secret-bearing environment variables/sockets and fails when environment allowlist attestation is missing.
- Negative test: launcher/profile path/env/argv tampering causes deterministic hard-fail before fallback execution begins.
- Negative test: unsupported host backend selection emits `blocked_inspector_boundary_unsupported` and blocks installation readiness.

**Verification:**

- Strict freshness/governance checks correctly classify `ready|degraded|blocked` with fail-closed behavior.

**Verification oracles:**

- Required skill-stack coverage ratio reaches 1.0 for valid inputs and blocks deterministically when incomplete.
- Inspector resolution is explicitly present as resolved, fallback, or blocked.
- Fallback inspector path includes explicit privilege-boundary evidence (`read_only`, `redacted_input_only`, `no_canonical_write`) and policy-marker fields (`role_resolution_policy`, `role_resolution_evidence`, `skill_coverage_ratio`).
- Fallback inspector attestation proves runtime confinement came from the audited launcher path and not policy-only assertions.
- Fallback attestation includes explicit probe outcomes (`fs_read_only`, `cwd_write_probe_blocked`, `canonical_write_probe_blocked`, `redacted_input_attested`, `env_allowlist_enforced`) and fails closed when any probe is absent.
- Fallback attestation includes `network_egress_blocked` and `process_spawn_blocked` proofs and fails closed when either is absent.
- Unsupported host path always emits `blocked_inspector_boundary_unsupported`; no fallback bypass path is allowed.
- Atomic write-path tests prove fallback evidence record and provenance sidecar either both persist or both fail.
- Installation-governance evidence persists only allowlisted fields and keyed-HMAC link tokens; raw sensitive values and unkeyed hashes are forbidden.
- Promotion-authoritative installation-governance evidence rejects local-keychain signers and accepts only CI-managed attested signer provenance.
- Canonical installation-governance artifact is emitted and schema-valid for every evaluated run.
- `validate_all.sh` restore/rollback manifest for P1 explicitly includes all P1-owned executable/profile/policy assets (`Infrastructure/scripts/lib/runtime_policy/installation_governance.py`, `Infrastructure/scripts/lib/runtime_policy/fallback_execution_boundary.py`, `Infrastructure/scripts/run_fallback_inspector.sh`, `Infrastructure/scripts/runtime_policy/fallback_inspector.sb`, `Infrastructure/scripts/runtime_policy/fallback_inspector.bwrap`, `Infrastructure/scripts/runtime_policy/fallback_inspector.env.allowlist`, `GOVERNANCE/runtime-separation/installation-governance.json`, `GOVERNANCE/runtime-separation/installation-governance.schema.json`) and enforces rollback-integrity checks for that set.

**Failure stop conditions:**

- Any path that allows promotion with missing required skills/inspector evidence blocks progression to P2.
- Any path that allows fallback inspector execution without explicit privilege-boundary proof blocks progression to P2.

**Exit criteria:** AC2

- [ ] **P2 / Unit 3: Lane Obligation Evaluator for 1/2/4**

**Goal:** Wire deterministic lane evaluation order, ownership assignment, freshness windows, and per-lane result emission.

**Requirements:** R14-R16, R10-R11, R13

**Dependencies:** P0, P1

**Files:**

- Modify: `Infrastructure/scripts/runtime-separation/build_runtime_separation_current.py`
- Modify: `Infrastructure/scripts/runtime-separation/validate_runtime_separation_manifest.py`
- Modify: `GOVERNANCE/runtime-separation/slices.schema.json`
- Test: `Infrastructure/scripts/testing/test_validate_all_runtime_separation.py`
- Test: `tests/test_validate_all_runtime_separation_integration.py`

**Approach:**

- Evaluate lane obligations in canonical order (1 -> 2 -> 4).
- Compute and emit `freshness_state`/`freshness_age_hours` with unknown freshness treated as blocking.
- Ensure owner-role mapping is present for each lane result.
- Emit top-level `owner_assignments` in closeout output derived from canonical lane-owner policy and fail closed on unresolved mappings.
- Keep lane-result evaluation and emission owned by `build_runtime_separation_current.py`; `validate_runtime_separation_manifest.py` is limited to schema/manifest validation and cannot become a second lane-result producer.
- P2 is the first phase allowed to enable full deterministic lane-result computation and promotion-facing lane-obligation semantics; earlier phases may only establish schema/state prerequisites.

**Patterns to follow:**

- Current runtime-separation issue normalization and summary aggregation.

**Test scenarios:**

- Mixed lane outcomes produce correct per-lane results and promotion decision.
- Unknown freshness value forces blocked state.

**Verification:**

- Lane output schema remains deterministic and CI-consumable.

**Verification oracles:**

- Lane output always includes `evidence_ref`, owner role, freshness state, and freshness age/value semantics.
- Unknown freshness inputs deterministically map to blocked results.
- Lane schema validation and owner-assignment coverage are enforced through canonical schema checks.

**Failure stop conditions:**

- Missing lane ownership mapping or nondeterministic precedence behavior blocks progression to P3.

**Exit criteria:** AC3

- [ ] **P3 / Unit 4: Ask Contract Parity and Compatibility Exception Handling**

**Goal:** Close lane-4 deterministic contract gaps and preserve required operator command compatibility with explicit blocking exceptions.

**Requirements:** R9, R16, R10-R11

**Dependencies:** P0, P2

**Files:**

- Modify: `bin/ask`
- Modify: `docs/cli-specs/ask-json-response.schema.json` (versioned machine-readable response contract for `ask` adapter outputs)
- Modify: `Infrastructure/scripts/validation-and-linting/verify_ask_cli.py`
- Modify: `Infrastructure/scripts/validation-and-linting/verify_ask_cli_final.py`
- Modify: `Infrastructure/scripts/validation-and-linting/verify_ask_cli_modularity.py`
- Modify: `docs/cli-specs/ask-blocker-codes.yaml` (canonical blocker-code registry for deterministic v1 rejection diagnostics)
- Modify: `docs/cli-specs/ask-v1-compat-policy.yaml` (canonical v1 entitlement matrix + sunset/disable policy source)
- Modify: `docs/cli-specs/ask-v1-compat-policy.schema.json`
- Modify: `Infrastructure/scripts/lib/ask/commands/skills.py`
- Modify: `Infrastructure/scripts/lib/ask/commands/plugins.py`
- Modify: `Infrastructure/scripts/lib/ask/commands/evals.py`
- Test: `tests/test_ask_cli.py`
- Test: `tests/test_ask_repo_doctor_catalog.py`

**Approach:**

- Ensure lane-4 blocker classes (including error-code reachability obligations) are represented deterministically in validation output.
- Resolve compatibility blocking strictly through exact-match normative registry rows.
- Exact-match selector identity tuple is fixed to (`exception_code`, `lane_id`, `blocker_code`, `owner_role`) with no wildcard selectors; lifecycle fields (`evidence_command`, `freshness_window_hours`, `expiry_policy`) are mandatory validated row metadata, not selector wildcards.
- Enforce registry uniqueness on the selector identity tuple (`exception_code`, `lane_id`, `blocker_code`, `owner_role`); duplicate rows are deterministic blocking errors before compatibility evaluation.
- Carry exception lifecycle semantics from the normative registry (`evidence_command`, `freshness_window_hours`, `expiry_policy`) and reject expired registry rows deterministically.
- Keep normative spec rows and schema unchanged in this phase; no sidecar exception overlay is introduced.
- Keep command-path compatibility explicit and fail only on declared blocker conditions.
- Introduce versioned `ask` machine-readable response contract (`ask_json_contract_version`) with default redacted v2 payload shape and explicit compatibility shim for v1 consumers so removal of raw passthrough fields is non-breaking.
- Version-axis mapping is explicit and single-source: `ask_json_contract_version` selects the transport contract, `metadata.version` must match the selected envelope version, and nested payload `schema_version` remains command-domain schema version; validator checks fail closed on cross-axis mismatch.
- Contract negotiation is deterministic: v2 is default; v1 requires explicit selector plus CI-governed per-command allowlist entitlement bound to authenticated caller/workload identity, non-allowlisted commands fail closed, selector/identity mismatches fail closed, and requests past `legacy_contract_v1_sunset_at` fail closed.
- Identity and entitlement primitives for v1 checks are explicit and stable:
  1. `entitlement_subject = (issuer, subject, audience, repository, workflow_ref)` from signed workload identity claims,
  2. `command_selector = (command_surface, command_group, command_name, command_action)` derived only after `bin/ask` alias/robot normalization and canonical action resolution,
  3. `request_context = (run_id, request_nonce, request_issued_at)`.
- Entitlement allowlist lookup keys on `entitlement_subject + command_selector`; `run_id` is request-scoped context for freshness/replay checks and must not widen or narrow command entitlement scope by itself.
- Compatibility v1 is structural-only and cannot emit unredacted `raw_output`/`raw_error` passthrough fields on any command surface.
- Redaction and structural v1/v2 contract rules are applied uniformly across all adapters that currently expose passthrough channels (`repo`, `wiki`, `skills`, `plugins`, `evals`) so no adapter-specific downgrade path remains.
- Commands classified sensitive by policy must reject v1 requests even when explicitly selected and allowlisted.
- Legacy v1 decommission path is immutable and fail-closed: once trust-root policy marks `legacy_contract_v1_enabled=false` (or `legacy_contract_v1_sunset_at` is exceeded), repo-local config cannot re-enable v1. Any emergency override must be signed, time-bounded, incident-scoped, and auto-revoked.
- Enforce exception lifecycle contract in one place through normative registry governance only (no wildcard row selectors, no inline exception logic, hard fail on invalid schema/provenance, automated expiry cleanup/reporting where registry policy defines expiry).
- Enforce runtime/ask blocker-code mapping deterministically: every exception-registry `blocker_code` that can reach ask diagnostics must resolve to exactly one canonical ask blocker code; missing/ambiguous mappings fail validation.
- v1 rejection modes must emit deterministic blocker codes from one canonical registry (`docs/cli-specs/ask-blocker-codes.yaml`) including at minimum: `ASK_V1_SELECTOR_REQUIRED`, `ASK_V1_ALLOWLIST_DENIED`, `ASK_V1_IDENTITY_MISMATCH`, `ASK_V1_SUNSET_EXPIRED`, `ASK_V1_SENSITIVE_SURFACE_DENIED`, `ASK_V1_ENTITLEMENT_STALE`; missing/unknown blocker codes fail validation.
- v1 downgrade rejection mapping contract is explicit and deterministic:

| Deny reason                                                           | Canonical blocker code            | Required coverage                                          |
| --------------------------------------------------------------------- | --------------------------------- | ---------------------------------------------------------- |
| missing explicit v1 selector                                          | `ASK_V1_SELECTOR_REQUIRED`        | `Infrastructure/scripts/validation-and-linting/verify_ask_cli.py`, `tests/test_ask_cli.py`       |
| selector not allowlisted for subject                                  | `ASK_V1_ALLOWLIST_DENIED`         | `Infrastructure/scripts/validation-and-linting/verify_ask_cli.py`, `tests/test_ask_cli.py`       |
| signed identity does not match allowlist subject                      | `ASK_V1_IDENTITY_MISMATCH`        | `Infrastructure/scripts/validation-and-linting/verify_ask_cli.py`, `tests/test_ask_cli.py`       |
| request timestamp/nonce/run binding stale or replayed                 | `ASK_V1_ENTITLEMENT_STALE`        | `Infrastructure/scripts/validation-and-linting/verify_ask_cli.py`, `tests/test_ask_cli.py`       |
| request past `legacy_contract_v1_sunset_at` or immutable disable flag | `ASK_V1_SUNSET_EXPIRED`           | `Infrastructure/scripts/validation-and-linting/verify_ask_cli_final.py`, `tests/test_ask_cli.py` |
| sensitive surface requests v1                                         | `ASK_V1_SENSITIVE_SURFACE_DENIED` | `Infrastructure/scripts/validation-and-linting/verify_ask_cli.py`, `tests/test_ask_cli.py`       |

- `docs/cli-specs/ask-blocker-codes.yaml` is the single mapping authority for downgrade denials; validator scripts fail closed if any deny reason lacks exactly one mapped blocker code.
- Entitlement contract defines replay/freshness semantics for v1 requests explicitly: stale `request_issued_at`, nonce reuse, or unverifiable `run_id` binding fail closed with registry-mapped blocker diagnostics.
- V1 entitlement/sunset enforcement source is explicit: allowlist matrix, per-command exceptions, `legacy_contract_v1_sunset_at`, and immutable disable flag are read from `docs/cli-specs/ask-v1-compat-policy.yaml` only; hard-coded fallback values are forbidden.

**Patterns to follow:**

- Existing alias normalization and command-action mapping in `bin/ask`.
- Existing ask CLI verification script structure.

**Test scenarios:**

- Required command surfaces continue to resolve and emit deterministic contract diagnostics.
- Compatibility findings are non-blocking unless matching exception registry entries.
- Expired exception rows are rejected even when exact-match selector fields otherwise match.
- Duplicate exception rows with the same selector tuple fail closed and emit deterministic diagnostics.
- `ask` JSON v1 compatibility path remains readable only for allowlisted non-sensitive legacy consumers while v2 redacted contract is default.
- Unauthorized v1 requests (missing allowlist entitlement or post-sunset) fail with deterministic blocker diagnostics.
- Unauthorized v1 requests also fail when caller/workload identity does not match allowlisted entitlement for the selected command surface.
- Non-allowlisted command surfaces fail closed on any v1 contract request.
- Policy-classified sensitive command surfaces fail closed on any v1 contract request.
- v1 rejection responses always include registry-backed blocker code + source selector fields used in the entitlement decision (without leaking sensitive token material).
- Command-selector mismatch tests prove per-command allowlist checks are not widened to surface-only checks.
- Replay/freshness tests prove nonce reuse, stale timestamps, or unverifiable run bindings fail closed with canonical blocker-code diagnostics.
- Adapter parity test: each passthrough-capable adapter (`repo`, `wiki`, `skills`, `plugins`, `evals`) rejects unauthorized v1 and emits redacted v2 by default.
- Policy-source tests fail closed when v1 entitlement/sunset values are missing from or inconsistent with `ask-v1-compat-policy.yaml`.

**Verification:**

- Ask validation path stays deterministic with no new compatibility regressions.

**Verification oracles:**

- Lane-4 blocker classes remain reachable and stable across `ask` parity checks.
- Compatibility findings only block when exception-registry match criteria are satisfied.
- Exception-row updates are schema-validated and test-covered to prevent implicit inline exception logic drift.
- Exception-row lifecycle fields (`evidence_command`, `freshness_window_hours`, `expiry_policy`) are required and validated for every blocking-exception row consumed by lane-4 gating.
- Exception registry enforces unique selector tuples (`exception_code`, `lane_id`, `blocker_code`, `owner_role`) with no order-dependent matching.
- `ask` JSON contract validation enforces versioned schema (`ask-json-response.schema.json`) and compatibility shim behavior for deprecated raw passthrough channels.
- `ask` compatibility enforcement proves v1 path is allowlisted + identity-bound + sunset-bounded and cannot be used as a caller-controlled downgrade around redaction on any command surface.
- Ask adapter contract parity is enforced across `repo`, `wiki`, `skills`, `plugins`, and `evals` command handlers with no adapter-local bypass.
- v1 rejection diagnostics are blocker-code complete: every deny path maps to exactly one canonical registry code and every code is covered by contract tests.
- Runtime exception `blocker_code` values and ask blocker diagnostics are mapping-complete and unambiguous (exactly one diagnostic mapping per surfaced runtime blocker).
- v1 allowlist enforcement keys on `entitlement_subject + command_selector` (not `run_id`), where `command_selector` is canonical post-alias/robot normalization; replay/freshness checks key on request context (`run_id`, nonce, issued_at) only.
- V1 entitlement/sunset policy artifact (`ask-v1-compat-policy.yaml`) is schema-valid and trust-governed; mismatch between policy artifact and emitted deny diagnostics blocks.

**Failure stop conditions:**

- Any regression in required command compatibility or exception-matching behavior blocks progression to P4.

**Exit criteria:** AC4, AC7

- [ ] **P4 / Unit 5: Closeout Health Snapshot, Drift Gate, and Promotion Decision Contract**

**Goal:** Produce a recurring closeout health artifact and block promotion on status/checklist drift or incomplete blocker metadata.

**Requirements:** R12-R13, R10-R11, R15

**Dependencies:** P1, P2, P3

**Files:**

- Modify: `Infrastructure/scripts/validate_all.sh`
- Modify: `Infrastructure/scripts/validate_requirements_spec_plan_drift.py` (new deterministic pivot-contract + operator-governance-doc drift validator)
- Modify: `Infrastructure/scripts/verify_required_check_enforcement.py` (new canonical required-check derivation validator with local deterministic mode and live parity audit mode)
- Modify: `Infrastructure/scripts/validation-and-linting/verify_selection_gate_severity.py` (consume canonical derived scoped required-check artifact only; no independent scope derivation)
- Modify: `Infrastructure/scripts/set_runtime_rollout_state.py` (apply live `pivot_rollout_mode` transition from `shadow` to `warn_visible` with state-authz/replay/concurrency checks)
- Modify: `Infrastructure/scripts/runtime-separation/build_runtime_separation_current.py`
- Modify: `Infrastructure/scripts/validation-and-linting/verify-work.sh`
- Modify: `.harness/ci-required-checks.json`
- Modify: `harness.contract.json` (keep runtime-pivot required-check declarations and workflow emissions in canonical contract sync)
- Modify: `.github/workflows/pr-pipeline.yml` (emit any newly required runtime-pivot-owned check names)
- Modify: `GOVERNANCE/runtime-separation/required-check-scope.yaml` (canonical mapping of runtime-pivot-owned required checks to emitting workflows)
- Modify: `GOVERNANCE/runtime-separation/required-check-scope.schema.json` (schema contract for scoped required-check declaration/mapping policy)
- Generate: `GOVERNANCE/runtime-separation/required-check-enforcement.local.json` (generated normalized local-mode parity evidence artifact consumed by closeout)
- Generate: `GOVERNANCE/runtime-separation/required-check-enforcement.live.json` (generated live-enforcement parity evidence artifact; mandatory for promotion-ready/P6 handoff, non-authoritative for local deterministic pass/fail)
- Generate: `GOVERNANCE/runtime-separation/required-check-derived-scoped.json` (single canonical normalized scoped required-check intermediate artifact)
- Modify: `GOVERNANCE/runtime-separation/required-check-enforcement.local.schema.json`
- Modify: `GOVERNANCE/runtime-separation/required-check-enforcement.live.schema.json`
- Modify: `GOVERNANCE/runtime-separation/required-check-derived-scoped.schema.json`
- Modify: `GOVERNANCE/runtime-separation/closeout-health-counters.schema.json` (schema contract for companion counters artifact)
- Modify: `docs/agents/04-validation.md`
- Modify: `docs/agents/07b-agent-governance.md`
- Modify: `docs/agents/12-ci-required-checks.md`
- Modify: `docs/agents/13-workflow-and-safety-guidance.md`
- Modify: `docs/agents/14-path-ownership-boundaries.md`
- Generate: `GOVERNANCE/runtime-separation/rollout-state.json` (mutated only via `Infrastructure/scripts/set_runtime_rollout_state.py`; never hand-edited in this phase)
- Generate: `GOVERNANCE/runtime-separation/closeout-health-counters.json` (generated-only companion counters artifact, never hand-edited)
- Test: `Infrastructure/scripts/testing/test_validate_all_runtime_separation.py` (update required-check expectations to derive from canonical declaration source, not fixed arrays)
- Test: `tests/test_validate_all_runtime_separation_integration.py`
- Test: `tests/test_runtime_rollout_state_contract.py` (new dedicated rollout-state contract test)
- Test: `tests/test_validate_all_required_check_parity.py` (new required-check declaration vs emitted-job parity test)
- Test: `tests/test_validate_requirements_spec_plan_drift.py` (new deterministic drift-validator scope + exclusion coverage)

**Approach:**

- Add/extend closeout reporting to keep the event contract spec-locked (`schema_version`, `overall_state`, `blocked_count`, `degraded_count`, `freshness_policy_ref`, `promotion_decision`) and emit required counters/ratios (`lane_ready_count`, `lane_degraded_count`, `lane_blocked_count`, `installation_skill_coverage_ratio`, `inspector_resolution_ratio`, `blocker_metadata_completeness_ratio`) plus `freshness_windows_by_lane` in canonical artifact `closeout-health-counters.json` governed by `closeout-health-counters.schema.json` and referenced by the same closeout report.
- Add required closeout counters `lane_ready_count`, `lane_degraded_count`, and `lane_blocked_count`.
- Add a deterministic drift validator (`Infrastructure/scripts/validate_requirements_spec_plan_drift.py`) scoped by default to this pivot's contract triplet (`origin` requirements + governing `spec` + this plan) plus operator-governance docs that declare the same gates (`docs/agents/04-validation.md`, `docs/agents/07b-agent-governance.md`, `docs/agents/12-ci-required-checks.md`, `docs/agents/13-workflow-and-safety-guidance.md`, `docs/agents/14-path-ownership-boundaries.md`), and wire it into `validate_all.sh` and `verify-work.sh` as a blocking gate for that scoped set.
- Drift validation scope is contract-content only: exclude mutable execution-status sections in this plan (for example the `Execution Ledger` table) so status tracking updates cannot trigger false contract drift failures.
- Wire drift validator and closeout-health checks into `.harness/ci-required-checks.json` as explicit required checks, scoped through `required-check-scope.yaml` to runtime-pivot-owned checks.
- Keep `.harness/ci-required-checks.json`, `harness.contract.json`, and emitted workflow job names synchronized for runtime-pivot-owned checks only so CI is satisfiable and enforcement is real; `.harness/ci-required-checks.json` is the canonical repo declaration for that pivot-owned subset, `required-check-scope.yaml` is canonical mapping policy for that subset, existing non-pivot checks remain preserved, and `validate_all.sh`/`verify_selection_gate_severity.py` must consume only `required-check-derived-scoped.json` emitted by `Infrastructure/scripts/verify_required_check_enforcement.py` (no hard-coded list drift and no secondary derivation path).
- Required-check source precedence is strict and fail-closed for runtime-pivot-owned scope only: workflow/ruleset emission remains enforcement truth, `.harness/ci-required-checks.json` is the canonical repo declaration for pivot-owned check names, `required-check-scope.yaml` may only filter/map that pivot-owned subset, and `verify_selection_gate_severity.py` must consume derived scoped output only; any mismatch blocks while preserving unrelated pre-existing required checks.
- Preservation guard for non-pivot checks is explicit and blocking: `Infrastructure/scripts/verify_required_check_enforcement.py` must compare full required-check inventory (workflow/ruleset + `.harness/ci-required-checks.json`) against pre-existing non-pivot baseline and fail on deletion/rename/drift outside pivot-owned scope.
- `Infrastructure/scripts/verify_required_check_enforcement.py` is the sole producer of normalized derived scoped required-check output (`required-check-derived-scoped.json`, schema-validated), and `Infrastructure/scripts/validation-and-linting/verify_selection_gate_severity.py` is a strict consumer of that artifact only (no parallel derivation logic).
- `required-check-scope.yaml` is a canonical governance policy artifact (not an ad hoc helper file): it must pass `required-check-scope.schema.json`, provenance verification, policy-bundle integrity checks, and restore/rollback coverage whenever changed.
- Retain an immutable bootstrap required-check guard set sourced from `required-check-bootstrap.yaml` (outside declarative scoped registry artifacts) so validator self-protection checks cannot be removed by editing `.harness/ci-required-checks.json` or `required-check-scope.yaml`; derived registry checks are evaluated only after bootstrap validation passes.
- Validate bootstrap guard-set integrity against dual-control external signed digest/fingerprint anchors (CI-managed signer + offline/root trust anchor) before any derived required-check policy evaluation; repo-local edits to scoped policy artifacts cannot satisfy this trust check.
- Keep `validate_all.sh` deterministic and repo-local: required-check gating in this path consumes only `required-check-derived-scoped.json` and `required-check-enforcement.local.json` emitted by `Infrastructure/scripts/verify_required_check_enforcement.py`; `validate_all.sh` must not independently derive scoped check sets.
- Run live merge enforcement parity for required checks as a separate CI precondition (`Infrastructure/scripts/verify_required_check_enforcement.py --live`) with its own blocking workflow step, scoped to runtime-pivot-owned required checks only; keep `validate_all.sh` repo-local and deterministic by consuming only local-mode scoped parity evidence for local pass/fail.
- Require `Infrastructure/scripts/verify_required_check_enforcement.py` to emit schema-versioned derived scoped output and parity artifacts by mode: `required-check-derived-scoped.json` (single normalized intermediate source), `required-check-enforcement.local.json` (deterministic repo-local, consumed by closeout), and `required-check-enforcement.live.json` (live merge-gate parity evidence for promotion-ready/P6 preconditions), each with explicit mode provenance.
- Define live parity freshness contract in this phase: `required-check-enforcement.live.json` must include `generated_at`, `fresh_until`, `scope_hash`, and `parity_mode=live`; freshness window is sourced from `freshness-policy.yaml` (`required_check_live_parity_max_age_hours`) and stale/missing fields are blocking in P6 activation preconditions.
- Define live parity freshness contract in this phase with an explicit age rule:
  - `evidence_age_hours = (now_utc - generated_at_utc) / 3600`,
  - pass requires `evidence_age_hours <= required_check_live_parity_max_age_hours`,
  - pass also requires `now_utc <= fresh_until_utc`,
  - and `fresh_until_utc` must equal `generated_at_utc + required_check_live_parity_max_age_hours` (bounded by `required_check_live_parity_clock_skew_minutes` tolerance from `freshness-policy.yaml`).
- Freshness enforcement ownership is explicit: `Infrastructure/scripts/verify_required_check_enforcement.py --live` produces freshness fields and `Infrastructure/scripts/validate_all.sh` + `Infrastructure/scripts/validation-and-linting/verify-work.sh` re-validate them before any promotion-ready declaration.
- Live parity evidence must include direct enforcement source snapshot metadata (`provider=github`, `ruleset_id`/`branch_protection_ref`, `source_fetched_at`, `source_commit_sha`) captured by `Infrastructure/scripts/verify_required_check_enforcement.py --live`; missing or unverifiable source snapshot fields are blocking.
- Keep `Infrastructure/scripts/validate_all.sh` as the single enforcement authority; `verify-work.sh` and `ask` surfaces must consume/delegate rather than redefining pass/fail semantics.
- Privacy-gate `not_applicable` required-check normalization is intentionally excluded from `required-check-scope.yaml` in this phase; that policy is owned separately in P5 through `privacy-required-check-normalization.yaml` to avoid coupling CI declaration mapping and privacy semantics.
- P4 precedence remains declaration-only and deterministic:
  1. derive scoped required-check set from `.harness/ci-required-checks.json` + `required-check-scope.yaml`,
  2. consume derived scoped output in `verify_selection_gate_severity.py` only.
- Privacy normalization precedence is introduced and owned in P5; no P4 behavior may depend on `privacy-required-check-normalization.yaml` being present.
- Use explicit rollout axes:
  1. `pivot_rollout_mode=shadow` (emit decisions without changing promotion outcome),
  2. `pivot_rollout_mode=warn_visible` (surface blocking candidates while preserving existing hard-stop behavior).
- Perform one explicit live transition `pivot_rollout_mode: shadow -> warn_visible` in this phase after drift/closeout/required-check local parity gates pass; transition must be written through `set_runtime_rollout_state.py` under state-authz/replay/concurrency controls.
- Persist and read rollout-mode transitions through canonical `rollout-state.json`; do not infer mode state from transient process output.
- Exercise rollback behavior in P4 through synthetic fixture-based enforce-state simulations only; fixture `enforce` states must never write live `rollout-state.json`, live mode cutover in P4 is limited to `shadow -> warn_visible`, and real enforce activation remains exclusive to P6.
- Spec clarifications are out of band for this implementation unit; any contract wording change must land before execution starts and remain version-locked during P4.
- P4 completes without requiring privacy-rollout progression; final enforce activation remains exclusively in `P6`.
- Repo-wide branch-protection/ruleset hardening beyond runtime-pivot-owned checks remains out of this implementation unit and is tracked separately.

**Patterns to follow:**

- Existing required-check execution model in `Infrastructure/scripts/validate_all.sh`.

**Test scenarios:**

- Drift mismatch causes blocking failure with actionable diagnostics.
- Scoped drift validator blocks when this pivot's requirements/spec/plan set or its operator-governance docs diverge; unrelated planning docs still do not gate this rollout.
- Drift validator ignores mutable execution-status sections (for example this plan's `Execution Ledger`) while still failing on normative contract-section drift.
- Promotion decision remains `blocked` until all AC-linked gates are satisfied.
- Contract-parity tests for runtime-separation check slugs are generated from canonical required-check declarations instead of fixed arrays.
- Non-pivot required-check preservation tests fail closed on deletion/rename drift outside runtime-pivot-owned scope.
- Merge-gate parity evidence generation fails when local scoped declaration parity diverges, and dedicated CI live-parity workflow steps fail when scoped runtime-pivot required checks are not enforced by active branch protection/rulesets.
- Live parity evidence tests fail when enforcement source snapshot metadata (`provider`, ruleset/protection refs, fetch time, source commit) is missing or unverifiable.
- P4 live transition tests fail closed when `shadow -> warn_visible` transition is attempted without drift/local-parity preconditions or without writer authz/replay/concurrency checks.

**Verification:**

- Promotion/closeout status is contract-driven and machine-checkable.

**Verification oracles:**

- Closeout output always includes full required `CloseoutHealthSnapshot` field set and a spec-locked `closeout_health_reported` event (`schema_version`, `overall_state`, `blocked_count`, `degraded_count`, `freshness_policy_ref`, `promotion_decision`); required health counters/ratios and `freshness_windows_by_lane` are emitted in schema-validated companion artifact `closeout-health-counters.json` with deterministic reference parity.
- `blocker_metadata_completeness_ratio` uses deterministic required `BlockerRecord` fields (`blocker_code`, `lane_id`, `severity`, `owner`, `escalation_window`, `evidence_ref`, `first_seen_at`, `last_seen_at`, `status`) with ratio semantics fixed to `complete_blockers / max(total_blockers, 1)`.
- Status/checklist drift emits a blocking signal with source-artifact references.
- Synthetic rollback simulation from enforce-state fixtures to `pivot_rollout_mode=warn_visible` preserves artifact schema parity and does not lose blocker evidence continuity.
- Lifecycle-state output remains within spec enum while rollout-mode fields change independently.
- Closeout snapshot evidence fields apply deterministic redaction/allowlist rules so sensitive runtime details are masked while diagnostics remain actionable; machine-readable JSON contracts (including `ask repo status --json`) use schema-preserving redaction that never removes required contract keys.
- Rollout-state artifact and closeout output remain synchronized across mode transitions and rollback.
- Required-check enforcement parity validator fails when workflow jobs and `.harness/ci-required-checks.json` diverge for runtime-pivot-owned scoped checks (local mode); dedicated CI live-parity workflow steps additionally fail when active merge-gate enforcement diverges for the same scoped checks.
- Required-check live parity is source-verifiable: `required-check-enforcement.live.json` includes provider snapshot fields that tie parity claims to fetched GitHub enforcement state, and missing/unverifiable source fields block.
- Required-check bootstrap guard checks remain mandatory even if declarative required-check artifacts are modified, and fail closed before derived parity checks execute.
- Required-check enforcement parity emits `required-check-enforcement.local.json` as the mandatory deterministic local closeout evidence artifact; `required-check-enforcement.live.json` is non-authoritative for local deterministic pass/fail but mandatory for promotion-ready declarations and P6 enforce activation handoff.
- `required-check-enforcement.live.json` freshness is explicit and test-enforced: `generated_at <= now <= fresh_until`, `parity_mode=live`, and `scope_hash` parity with the current scoped declaration set are required for promotion-ready and P6 handoff.
- `required-check-derived-scoped.json` is schema-valid, versioned, and consumed as the single source for downstream severity mapping; `verify_selection_gate_severity.py` cannot derive required-check scope independently.
- Required-check derivation precedence remains deterministic and test-covered in P4 (`derive scoped` -> `severity mapping`), and any declaration/mapping conflict blocks.
- Full-set required-check preservation is deterministic and test-covered: pivot-scoped derivation cannot remove or rename unrelated pre-existing required checks in declaration or workflow/ruleset enforcement layers.
- Required-check declaration/mapping policy (`required-check-scope.yaml`) fails closed on schema/provenance/policy-bundle validation failure in P4; once introduced in P5, privacy normalization policy (`privacy-required-check-normalization.yaml`) must also fail closed under the same validation guarantees.

**Failure stop conditions:**

- Promotion can succeed despite drift or incomplete blocker metadata.
- Rollback path cannot restore prior promotion semantics without introducing ambiguous blocker state.
- Live `shadow -> warn_visible` transition cannot be established deterministically with writer authz/replay/concurrency guarantees.

**Exit criteria:** AC5, AC6

- [ ] **P5 / Unit 6: Privacy and Operational Hardening for Wiki Ingestion Lane**

**Goal:** Enforce privacy classification/redaction prerequisites and document operational ownership for sustained closeout hygiene.

**Requirements:** R17-R18, R13

**Dependencies:** P4

**Files:**

- Modify: `Infrastructure/scripts/validate_wiki_privacy_gate.py` (dedicated privacy gate validator for sensitive-source ingestion/promotion)
- Modify: `Infrastructure/scripts/validate_all.sh` (wire dedicated privacy gate with scoped applicability)
- Modify: `Infrastructure/scripts/validation-and-linting/verify-work.sh` (surface dedicated privacy-gate outcome)
- Modify: `Infrastructure/scripts/validation-and-linting/verify_selection_gate_severity.py` (required-check status normalization for lane-scoped `not_applicable` outcomes)
- Modify: `Infrastructure/scripts/set_runtime_rollout_state.py` (persist `privacy_rollout_mode` transitions introduced in P5)
- Modify: `.harness/ci-required-checks.json` (register privacy gate required-check context name only)
- Modify: `GOVERNANCE/runtime-separation/required-check-scope.yaml` (append-only privacy gate declaration mapping/workflow ownership entries only; no rewrites of existing non-privacy mappings and no privacy status semantics)
- Modify: `GOVERNANCE/runtime-separation/privacy-required-check-normalization.yaml` (declare lane-scoped `not_applicable` pass-equivalent mapping rules)
- Modify: `GOVERNANCE/runtime-separation/privacy-required-check-normalization.schema.json`
- Modify: `.github/workflows/pr-pipeline.yml` (emit privacy gate check)
- Modify: `docs/agents/04-validation.md`
- Modify: `docs/agents/07b-agent-governance.md`
- Modify: `GOVERNANCE/runtime-separation/path-consumers.yaml` (when consumer metadata surfaces change)
- Modify: `GOVERNANCE/runtime-separation/sensitivity-classification-policy.yaml`
- Modify: `GOVERNANCE/runtime-separation/privacy-gate-evidence.schema.json`
- Modify: `GOVERNANCE/runtime-separation/privacy-sidecar-contract.yaml` (decrypt authority, key custody, audit, retention, and failure-mode semantics)
- Modify: `GOVERNANCE/runtime-separation/privacy-sidecar-contract.schema.json`
- Modify: `Infrastructure/scripts/verify_privacy_sidecar_contract.py` (enforce sidecar linkage/access/audit/retention contract preconditions)
- Generate: `GOVERNANCE/runtime-separation/privacy-gate-evidence.json` (generated-only canonical privacy classification/provenance evidence artifact)
- Modify: `docs/agents/14-path-ownership-boundaries.md`
- Modify: `docs/agents/13-workflow-and-safety-guidance.md`
- Test: `Infrastructure/scripts/testing/test_validate_all_runtime_separation.py`
- Test: `tests/test_ask_plugins_state.py` (if output contracts or safety messaging are surfaced through shared command status)

**Approach:**

- Add explicit classification/redaction gate checks before sensitive-source repo persistence (including raw-plane ingest) and before promotion.
- Require dual independent non-sensitive corroboration before any raw-plane persistence decision is treated as non-sensitive: trusted classifier result plus independent content scan path (`source-inventory + deterministic pattern/DLP scan`) under separate policy owner; disagreement is blocking and routes to sensitive handling.
- Require dual-control approval for sensitive-source raw-plane ingest decisions: classifier/scan evidence producer and privacy owner attestation must both be present before append-only ingest is permitted.
- Dual-control principal separation is mandatory: classifier/scan attester and privacy-owner attester must be distinct principals mapped to different trust-policy role sets; single-principal self-approval is always blocking.
- Decrypt authority is a separate control plane from ingest attestations: sidecar decrypt principals must be distinct from ingest dual-control principals, and ingest approval does not imply decrypt permission.
- For sensitive-source scope, keep unredacted payloads outside git-backed repo storage and allow only redacted payloads plus non-linkable digest envelope metadata into `docs/skill-ops-wiki/raw/`; sensitive provenance/token details remain in restricted encrypted sidecar storage.
- Keep privacy-gate scope lane-specific: evaluate only sensitive-source ingestion/promotion evidence and return `not_applicable` only when deterministic dual corroboration records both trusted classifier `sensitivity_scope=non_sensitive` and independent non-sensitive corroboration from an immutable-trust-root-attested source-inventory snapshot; `sensitivity_scope=unknown` is blocking.
- Keep privacy-gate required-check semantics centralized in `privacy-required-check-normalization.yaml` (separate owner/scope from CI declaration mapping); `.harness/ci-required-checks.json` and `required-check-scope.yaml` remain declaration/mapping-only.
- P5 introduces required-check normalization precedence (after P4 declaration derivation): `derive scoped` -> `apply privacy-required-check-normalization` -> `severity mapping`; unknown contexts or conflicting rewrites are blocking.
- Require `sensitivity_scope` evidence to originate from trusted classifiers declared in `sensitivity-classification-policy.yaml`; unsigned/untrusted provenance is blocking.
- Bind each ingested sensitive-source evidence record to tenant/run/rotation-scoped source-inventory keyed-HMAC binding tokens and trusted provenance metadata before downstream lane evaluators consume it.
- Persist git-backed `privacy-gate-evidence.json` as a schema-validated non-linkable digest envelope (classification result, attestation refs, replay-safe pointers) so promotion decisions and closeout can replay outcomes deterministically without exposing linkable sensitive metadata.
- Persist sensitive provenance/token details in restricted encrypted sidecar storage outside git-backed artifacts; promotion checks require attested linkage between envelope and sidecar, and repo-only evidence is insufficient for sensitive-scope pass decisions.
- Sidecar security boundary is explicit and fail-closed: `privacy-sidecar-contract.yaml` defines permitted decrypt authorities (runtime service role + break-glass dual-approval role), key custody requirements (KMS-managed key alias and rotation policy), mandatory immutable audit events (encrypt/decrypt/link/retention-expiry), retention windows, and hard failure semantics (`sidecar_unavailable`, `sidecar_attestation_missing`, `decrypt_authority_denied`) that block persistence/promotion. Decrypt-time authorization is mandatory on every sidecar access; unauthorized or unverifiable decrypt attempts are denied before data release.
- Sidecar retention/revocation semantics are access-time and promotion-authoritative: expired retention windows, revoked attestations, or stale key-rotation evidence must trigger decrypt denial at read time and force re-attestation before promotion.
- Break-glass decrypt authority is incident-scoped and bounded: requires dual approval from distinct break-glass principals, explicit incident/ticket binding, fixed TTL, immutable audit evidence, and automatic revocation at expiry.
- Update operational docs to align ownership, escalation, and recovery expectations with implemented gate behavior.
- Introduce `privacy_rollout_mode` in two steps:
  1. `privacy_rollout_mode=observe` (record privacy violations and ownership metadata, and keep sensitive-source promotion blocked),
  2. `privacy_rollout_mode=enforce` (privacy violations block promotion).
- Persist privacy-rollout transitions through `set_runtime_rollout_state.py`; policy introduction and state mutation are owned in this phase, while P6 owns final pivot enforce cutover only.
- Keep rollback target explicit: `privacy_rollout_mode=enforce` can revert to `privacy_rollout_mode=observe` only when diagnostics remain intact and unresolved violations stay visible.
- Keep rollout axes operationally independent: privacy-rollout transitions do not mutate pivot-rollout state directly; promotion gating evaluates both axes together and blocks on any incompatible combination.
- P5 may end with `privacy_rollout_mode=observe` only for non-sensitive-scope runs proven by dual corroboration; for sensitive-scope runs, P5 exit requires `privacy_rollout_mode=enforce` plus a signed `observe -> enforce` transition record in canonical rollout-state history.

**Patterns to follow:**

- Existing fail-closed safety checks and metadata validation style in governance scripts.

**Test scenarios:**

- Sensitive-source ingestion without classification metadata blocks repo persistence and promotion.
- Classification-complete flow passes while preserving actionable diagnostics.
- Non-sensitive lane-scoped runs emit pass-equivalent required-check status only when dual corroboration evidence includes immutable-trust-root-attested source-inventory proof (with explicit `not_applicable` diagnostics) so required-check parity remains satisfiable without fail-open classification.
- Raw-plane ingest fails closed when trusted classifier and independent scan disagree, when second-owner approval is missing, or when sidecar linkage/decrypt-authority checks fail.
- Raw-plane ingest fails closed when required dual-control attestations are produced by the same principal identity.

**Verification:**

- Privacy contract is enforced by default and reflected in operational docs.

**Verification oracles:**

- Sensitive-source repo persistence and promotion both require classification/redaction evidence before ready state.
- Dedicated privacy gate remains lane-scoped and returns `not_applicable` only when dual corroboration evidence exists (`sensitivity_scope=non_sensitive` + immutable-trust-root-attested independent non-sensitive source-inventory corroboration); it cannot fail unrelated repo-validation paths.
- Canonical git-backed privacy evidence envelope (`privacy-gate-evidence.json`) is schema-valid and replayable for every evaluated sensitive-source decision, and required sidecar linkage proofs are present/attested for sensitive-scope evaluations.
- Privacy gate `not_applicable` outcomes map to pass-equivalent required-check status for non-sensitive scope only through schema-validated `privacy-required-check-normalization.yaml` rules and only when dual corroboration evidence is present.
- Required-check normalization precedence is deterministic in P5 (`derive scoped` -> `apply privacy normalization` -> `severity mapping`) and fails closed on unknown context or conflicting rewrite outcomes.
- Operational docs map ownership and escalation to implemented gate behavior with no conflicting guidance.
- Observe-to-enforce transition preserves deterministic privacy findings and does not downgrade unresolved violations to informational-only state.
- Observe mode still enforces fail-closed behavior for sensitive-source promotion and cannot be used to bypass privacy gating.
- Observe mode emits explicit deterministic result `blocked_sensitive_scope` for sensitive-source promotions; this state is mandatory until `privacy_rollout_mode=enforce` preconditions are satisfied.
- Unknown or absent sensitivity classification is always blocking for promotion.
- Privacy rollback from `enforce` cannot produce a promotion-ready state for sensitive-source runs unless privacy preconditions are re-satisfied.
- Classification provenance checks fail closed when evidence is self-attested or produced by a non-authorized classifier.
- Independent non-sensitive corroboration checks fail closed when source-inventory proof is mutable-repo-only and not anchored to immutable trust-root attestation.
- Sidecar boundary checks fail closed when decrypt authority is outside contract, key custody/rotation attestations are stale, required audit events are missing, or retention policy metadata is absent.
- Sidecar evidence reuse fails closed when retention is expired, attestation is revoked, or freshness constraints are not met; promotion requires fresh sidecar re-attestation.
- Break-glass decrypt use fails closed when incident binding, dual-approval provenance, TTL bounds, or automatic revocation evidence are missing.
- Classification/provenance records are bound to exact tenant/run/rotation-scoped source-inventory keyed-HMAC tokens for the evaluated promotion payload; cross-run stable token reuse is forbidden in git-backed artifacts.
- Raw evidence writer-boundary controls fail closed when any non-ingest process attempts to mutate `docs/skill-ops-wiki/raw/`.
- `validate_all.sh` restore/rollback manifest for P5 explicitly includes all P5-owned privacy/normalization assets and mutators (`Infrastructure/scripts/validate_wiki_privacy_gate.py`, `Infrastructure/scripts/validation-and-linting/verify_selection_gate_severity.py`, `Infrastructure/scripts/set_runtime_rollout_state.py`, `Infrastructure/scripts/verify_privacy_sidecar_contract.py`, `GOVERNANCE/runtime-separation/privacy-required-check-normalization.yaml`, `GOVERNANCE/runtime-separation/privacy-required-check-normalization.schema.json`, `GOVERNANCE/runtime-separation/privacy-gate-evidence.json`, `GOVERNANCE/runtime-separation/privacy-gate-evidence.schema.json`, `GOVERNANCE/runtime-separation/sensitivity-classification-policy.yaml`, `GOVERNANCE/runtime-separation/privacy-sidecar-contract.yaml`, `GOVERNANCE/runtime-separation/privacy-sidecar-contract.schema.json`, plus any P5-mutated required-check declaration/mapping surfaces) with rollback-integrity checks.

**Failure stop conditions:**

- Any path permits sensitive-source repo persistence or promotion without privacy gate evidence.
- Enforce-to-observe rollback hides unresolved privacy violations from closeout reporting.
- Any path permits `not_applicable` without dual corroboration (`sensitivity_scope=non_sensitive` + immutable-trust-root-attested independent non-sensitive source-inventory corroboration).
- Any path accepts untrusted classification provenance for `sensitivity_scope`.
- Any path accepts dual-control attestations from a single principal for sensitive-source ingest decisions.
- Any path treats expired or revoked sidecar evidence as promotion-authoritative.

**Exit criteria:** AC8, plus sensitive-scope exit gate (`privacy_rollout_mode=enforce` with signed `observe -> enforce` transition history record); non-sensitive-scope runs may exit in `observe` only when dual-corroborated `not_applicable` evidence is present.

- [ ] **P6 / Unit 7: Enforce Activation Handoff and Final Gate Cutover**

**Goal:** Perform a deterministic post-P5 handoff that activates `pivot_rollout_mode=enforce` only after privacy and closeout preconditions are fully satisfied.

**Requirements:** R11-R13, R15, R17-R18

**Dependencies:** P4, P5

**Files:**

- Modify: `Infrastructure/scripts/validate_all.sh`
- Modify: `Infrastructure/scripts/set_runtime_rollout_state.py` (state-transition writer already established in P0; P6 adds final handoff logic and rollback safeguards)
- Modify: `Infrastructure/scripts/runtime-separation/build_runtime_separation_current.py`
- Test: `tests/test_runtime_rollout_state_contract.py`

**Approach:**

- Treat P6 mode-handoff checks as implementation rollout controls only; normative delivery contract acceptance remains AC-based and spec-locked.
- Evaluate final activation preconditions after P5 completion:
  1. sensitive-scope precondition requires signed rollout-state history containing an authorized `privacy_rollout_mode: observe -> enforce` transition (with replay/concurrency checks satisfied),
  2. privacy gate activation-eligible outcome is either:
     - `enforce_pass` with `privacy_rollout_mode=enforce` when sensitive-source ingestion/promotion evidence is in scope,
     - `not_applicable` only when deterministic dual corroboration proves non-sensitive scope (`sensitivity_scope=non_sensitive` + immutable-trust-root-attested independent non-sensitive source-inventory corroboration),
  3. privacy gate non-activation hold state remains explicit:
     - `blocked_sensitive_scope` for sensitive-source scope while `privacy_rollout_mode=observe`,
  4. `pivot_rollout_mode=warn_visible` in canonical rollout-state artifact,
  5. no blocked lane obligations,
  6. drift gate passing,
  7. blocker metadata completeness and evidence redaction contracts passing,
  8. rollout-state artifact and closeout output report the same mode-state tuple,
  9. state-transition write authorization and artifact-provenance checks pass,
  10. lane-owner/freshness policy contracts are schema-valid and pass `verify_runtime_policy_contracts.py`,
  11. reader-compatibility gate passes for all independently versioned closeout surfaces (`current.json`, `CloseoutHealthSnapshot`, `closeout_health_reported`) with schema-valid `reader-compatibility.json`,
  12. live required-check parity evidence is passing and fresh for runtime-pivot-owned scoped checks (`required-check-enforcement.live.json`) using the explicit age rule (`evidence_age_hours <= required_check_live_parity_max_age_hours`, `now_utc <= fresh_until_utc`, and `fresh_until_utc` derived from `generated_at_utc` using `required_check_live_parity_max_age_hours` with bounded `required_check_live_parity_clock_skew_minutes` tolerance) validated by `Infrastructure/scripts/verify_required_check_enforcement.py --live` and rechecked by `Infrastructure/scripts/validate_all.sh`,
  13. rollout-state transition history contains one signed/attested live `shadow -> warn_visible` transition record produced by `set_runtime_rollout_state.py` with replay/concurrency checks satisfied.
- Apply one explicit handoff transition from `pivot_rollout_mode=warn_visible` to `pivot_rollout_mode=enforce`.
- Define the reverse transition contract for operator rollback (`pivot_rollout_mode=enforce` -> `pivot_rollout_mode=warn_visible`) with the same authorization, parity, and evidence-preservation checks.
- If any precondition fails, remain in `pivot_rollout_mode=warn_visible` and emit deterministic blocker diagnostics.

**Verification oracles:**

- `pivot_rollout_mode=enforce` becomes reachable only through this post-P5 activation handoff.
- Failed preconditions do not partially activate enforce mode.
- Privacy-mode transitions do not implicitly mutate pivot mode; incompatible tuples are handled by deterministic blocking decisions.
- Sensitive-source runs cannot activate `pivot_rollout_mode=enforce` while privacy gate outcome is `observe` or unresolved.
- Enforce activation fails closed when reader-compatibility records are missing/stale/incompatible for any independently versioned closeout surface.
- Enforce activation fails closed when live required-check parity evidence for runtime-pivot-owned scoped checks is missing, stale, or failing.
- Rollback from `pivot_rollout_mode=enforce` to `pivot_rollout_mode=warn_visible` preserves blocker evidence continuity and artifact parity across operator surfaces.

**Failure stop conditions:**

- Enforce activation occurs without all listed preconditions.
- Activation handoff can produce mixed mode state between artifacts and operator surfaces.

**Exit criteria:** AC5, AC6, AC8

## System-Wide Impact

- **Interaction graph:** Runtime validators feed the current artifact builder; comparator and wrapper gates consume normalized outputs; `ask` surfaces expose the same decision envelope for operators.
- **Error propagation:** Lane-specific blocker codes propagate into comparator results, then into promotion decision and closeout reporting. Missing blocker metadata is itself blocking.
- **State lifecycle risks:** Partial rollout of artifact schema, comparator rules, or wrapper interpretations can create split-brain decisions; each phase must update producer and consumer contracts together.
- **API surface parity:** `ask repo validate` and `ask repo doctor-catalog --strict` remain operator-facing contract surfaces and must reflect the same blocker precedence semantics as script-level enforcement.
- **Integration coverage:** Cross-script behavior must be proven with integration tests in addition to unit coverage because correctness depends on handoff between validator, artifact, comparator, and reporting layers.
- **Operational feedback loop:** Closeout snapshots become the canonical anti-stall signal; compatibility findings remain visible in degraded mode but non-blocking unless mapped to normative exception entries.

## Risks & Dependencies

- Risk: comparator/reader drift if schema changes land without synchronized consumer updates.
  - Mitigation: pair producer/consumer changes in one phase and keep fixture coverage in the same PR scope.
  - Owner lane: runtime-separation owner.
- Risk: false blocking from freshness-state inference or missing freshness provenance.
  - Mitigation: enforce explicit freshness defaults and block unknown freshness deterministically with actionable diagnostics.
  - Owner lane: skill-family certification owner.
- Risk: compatibility noise over-blocks degraded mode.
  - Mitigation: block only on normative exception-registry matches and keep all non-matching compatibility findings degraded-visible.
  - Owner lane: ask-contract owner.
- Risk: partial adoption of fail-closed installation governance causes silent promotion escapes.
  - Mitigation: enforce skill-stack/inspector checks before promotion decision computation and test both success and failure envelopes.
  - Owner lane: repo-standards owner.
- Risk: closeout gate rollout introduces abrupt hard-stop behavior before shadow/warn evidence stabilizes.
  - Mitigation: require staged rollout (`pivot_rollout_mode=shadow -> pivot_rollout_mode=warn_visible -> pivot_rollout_mode=enforce`) with explicit promotion-readiness review between stages.
  - Owner lane: runtime-separation owner.
- Risk: mode-state split brain between canonical state artifact and reported closeout output.
  - Mitigation: single canonical `rollout-state.json` owner plus parity tests that fail on state divergence.
  - Owner lane: runtime-separation owner.
- Risk: rollback from enforce mode suppresses blocker visibility and creates false confidence.
  - Mitigation: rollback is valid only if blocker evidence continuity and schema parity remain intact in the target mode; promotion decisions block on incompatible pivot/privacy mode tuples without implicit cross-axis mutation.
  - Owner lane: repo-standards owner.
- Dependency: runtime-separation inventory and manifest contracts (`readers.yaml`, `path-consumers.yaml`, `slices.yaml`) remain authoritative.
- Dependency: existing `ask` wrappers remain canonical operator entrypoints and must not diverge from script-level enforcement outcomes.
- Dependency: `Infrastructure/scripts/validate_all.sh` is the canonical enforcement entrypoint; `verify-work.sh` and `ask` surfaces must delegate to or consume its outputs without independent gate semantics.
- Dependency: blocker owner-role taxonomy from the pivot spec remains stable while this plan executes.

## Documentation / Operational Notes

- Implementation must update operational docs only where contracts change; avoid duplicating policy logic across documents.
- Closeout reporting should keep one canonical artifact source and avoid parallel, conflicting status outputs.
- Operational runbooks should explicitly separate:
  - promotion blockers (hard stop),
  - compatibility findings in degraded visibility state (visible but non-blocking unless registry-matched),
  - informational diagnostics (non-gating).
- Operational runbooks should include rollout-state annotations for each gate family (`pivot_rollout_mode=shadow|warn_visible|enforce`, `privacy_rollout_mode=observe|enforce`) so operators can interpret promotion outcomes correctly.
- Closeout reporting runbooks must document mandatory evidence redaction and allowlist rules for sensitive fields.
- Recovery sequencing from spec must be retained in operational guidance:
  1. lane 1 freshness blockers,
  2. lane 2 parity blockers,
  3. lane 4 contract blockers,
  4. compatibility findings in degraded visibility state.

## Execution Ledger (Planning Mode)

| STEP_ID | status (pending | in_progress | completed)                                           | owner | evidence |
| ------- | --------------- | ----------- | ---------------------------------------------------- | ----- | -------- |
| P0      | pending         | codex       | Artifact/schema wiring not yet implemented           |
| P1      | pending         | codex       | Fail-closed installation gate wiring pending         |
| P2      | pending         | codex       | Lane 1/2/4 obligation evaluator pending              |
| P3      | pending         | codex       | Ask parity + compatibility exception updates pending |
| P4      | pending         | codex       | Closeout snapshot + drift gate integration pending   |
| P5      | pending         | codex       | Privacy gate + operational hardening pending         |
| P6      | pending         | codex       | Post-P5 enforce activation handoff pending           |

## Sources & References

- Origin requirements: `docs/brainstorms/2026-04-13-llm-wiki-runtime-pivot-requirements.md`
- Governing spec: `docs/specs/2026-04-13-feat-llm-wiki-runtime-pivot-spec.md`
- Related plan baseline: `docs/plans/2026-04-12-feat-product-factory-runtime-separation-plan.md`
- Existing governance scripts:
  - `Infrastructure/scripts/validate_all.sh`
  - `Infrastructure/scripts/validation-and-linting/verify-work.sh`
  - `Infrastructure/scripts/runtime-separation/build_runtime_separation_current.py`
  - `Infrastructure/scripts/runtime-separation/compare_runtime_separation_baseline.py`
  - `Infrastructure/scripts/validation-and-linting/verify_skill_catalog_freshness.py`
- Existing command surface:
  - `bin/ask`
