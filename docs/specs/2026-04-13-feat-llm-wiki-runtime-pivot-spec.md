---
title: LLM Wiki Runtime Pivot and Scaffold Contract Specification
type: feat
status: draft
date: 2026-04-13
origin: docs/brainstorms/2026-04-13-llm-wiki-runtime-pivot-requirements.md
risk: high
spec_depth: full
ui_required: false
deepened: 2026-04-13
---

# LLM Wiki Runtime Pivot and Scaffold Contract Specification

## Table of Contents

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
- [Open Questions](#open-questions)
- [Definition of Done](#definition-of-done)

## Enhancement Summary

**Deepened on:** 2026-04-13  
**Mode:** targeted-confidence  
**Key areas improved:** lifecycle states, blocker precedence, observability gates, acceptance precision

- Added explicit lifecycle state model for mode initialization, installation governance, lane obligation evaluation, and promotion readiness.
- Tightened failure and recovery semantics with deterministic blocker precedence and evidence freshness handling.
- Expanded observability contract to require lane-level health counters, skill-stack coverage, inspector-resolution reporting, and blocker metadata completeness.
- Extended acceptance matrix without renumbering existing IDs so planning can validate lifecycle and readiness behavior directly.

## Problem Statement

The current operating lane repeatedly reaches implementation progress but fails closeout reliability because three blocker families remain unresolved at contract level:

- certification/readiness evidence remains blocked by skill-graph envelope or parity issues;
- runtime-separation control-plane state remains degraded;
- ask contract parity still carries at least one contract-grade gap in reachable deterministic behavior.

This spec defines a new contract that makes `llm-wiki` the primary knowledge operating model, degrades skill-graph to a bounded compatibility lane, and enforces fail-closed installation governance so closeout cannot silently drift again.

## Goals

- Establish one explicit primary operating mode: `llm_wiki_primary`.
- Define `degraded_compatibility` behavior for skill-graph surfaces with explicit blocking exceptions.
- Keep Obsidian as graph-view consumer only, never canonical source-of-truth.
- Reorganize scaffold authority so canonical sources, factory mechanics, and runtime projections are unambiguous.
- Absorb blocked lanes 1, 2, and 4 into one contract family without split ownership.
- Enforce installation governance with a required skill stack: `llm-wiki`, `coderabbit:simplify`, `uv-python-project-setup`, `baseline-ui`.
- Enforce inspection-role checks (`skill-inspector`, `plugin-inspector`) with deterministic fallback and fail-closed gating.
- Make blocker taxonomy, ownership, and closeout health reporting deterministic and machine-checkable.
- **Governance Contract Coupling Justification**: OperatingModeContract, InstallationOrchestrationContract, and BlockedLaneObligation content are explicitly coupled to the autoresearch hardening effort because autoresearch operations depend on deterministic mode-switching, fail-closed skill-stack verification, and lane-obligation evaluation for certification/runtime-separation/ask-contract parity; without these governance primitives, autoresearch cannot reliably determine when research operations are safe to promote or when they must remain blocked due to upstream blocker families.

## Non-Goals

- Task sequencing, migration runbooks, or phase-by-phase implementation mechanics.
- Broad product feature additions unrelated to this pivot.
- Hard deletion of all skill-graph artifacts in this stage.
- Marketplace protocol redesign.
- UI screen/component contract work (`ui_required: false`).

## System Boundary

Owned by this spec:

- Operating mode contract (`llm_wiki_primary`, `degraded_compatibility`).
- Source-of-truth and writer/reader authority contract for wiki, factory, and runtime surfaces.
- Installation orchestration contract (required skill stack + inspector-role checks + fallback semantics).
- Cross-lane blocker contract for certification, runtime-separation, and ask-contract parity.
- Closeout health contract and blocker taxonomy for promotion gating.

Not owned by this spec:

- Detailed execution plan and migration choreography (`ce-plan` concern).
- Script-level implementation details for validators and wrappers.
- Dedicated UI interaction contracts.

## Core Domain Model

- `OperatingModeContract`
  - Fields: `primary_mode`, `compatibility_mode`, `blocking_exceptions`, `mode_owner`.
  - Required values: `primary_mode=llm_wiki_primary`, `compatibility_mode=degraded_compatibility`.

- `KnowledgeAuthorityMap`
  - Fields: `canonical_wiki_root`, `raw_source_roots`, `schema_root`, `projection_roots`, `authoritative_writers`, `authoritative_readers`.
  - Rule: canonical wiki defaults to `wiki/` unless repo policy declares an explicit alternate root.

- `InstallationOrchestrationContract`
  - Fields: `required_skills[]`, `inspector_roles[]`, `fallback_roles[]`, `fail_closed`, `evidence_requirements[]`.
  - Required skills: `llm-wiki`, `coderabbit:simplify`, `uv-python-project-setup`, `baseline-ui`.
  - Required inspector roles: `skill-inspector`, `plugin-inspector`.
  - Canonical fallback roles when a required inspector role is temporarily unavailable: `repo-research-analyst`, `project-standards-reviewer`.
  - Additional fields: `role_resolution_policy`, `role_resolution_evidence`, `skill_coverage_ratio`.

- `BlockedLaneObligation`
  - Fields: `lane_id`, `contract_reference`, `required_outcome`, `blocking_condition`.
  - Required lane bindings:
  - `lane_id=1` certification/readiness.
  - `lane_id=2` runtime-separation control-plane health.
  - `lane_id=4` ask deterministic contract parity.

- `CloseoutHealthSnapshot`
  - Fields: `schema_version`, `timestamp`, `mode_state`, `lane_obligations`, `blockers[]`, `degraded_findings[]`, `owner_assignments`, `promotion_decision`.

- `LifecycleStateRecord`
  - Fields: `lifecycle_state`, `entered_at`, `exit_condition`, `blocking_context`.
  - Allowed states: `contract_declared`, `preflight_ready`, `governance_running`, `lane_evaluated`, `promotion_blocked`, `promotion_ready`.

- `BlockerRecord`
  - Fields: `blocker_code`, `lane_id`, `severity`, `owner`, `escalation_window`, `evidence_ref`, `first_seen_at`, `last_seen_at`, `status`.
  - Status values: `active`, `mitigating`, `cleared`, `accepted_with_expiry`.

## Main Flow / Lifecycle

### 1. Mode Initialization

1. Load `OperatingModeContract`.
2. Assert `primary_mode=llm_wiki_primary`.
3. Assert skill-graph surfaces are tagged `degraded_compatibility` with explicit blocking exceptions.
4. If mode contract is missing or contradictory, emit blocking status and stop promotion.
5. Emit `LifecycleStateRecord` transition: `contract_declared -> preflight_ready`.

### 2. Knowledge Operation Lifecycle

1. Ingest/query/lint workflows run against canonical wiki roots and governance rules.
2. Obsidian reads markdown link graph as inspection/view layer only.
3. Skill-graph compatibility outputs are monitorable but non-blocking unless they match declared blocking exceptions.

### 3. Installation Governance Lifecycle

1. Preflight role availability for `skill-inspector` and `plugin-inspector`.
2. Resolve missing inspectors through canonical fallback roles.
3. Verify all required skills are active in the installation lane.
4. Execute installation or migration only after governance preconditions pass.
5. Persist evidence of skill-stack usage, role availability, fallback decisions, and gate outcomes.
6. Transition lifecycle state:
- `preflight_ready -> governance_running` when required skills and role resolution pass.
- `preflight_ready -> promotion_blocked` when either condition fails.

### 4. Lane-Obligation Lifecycle (1, 2, 4)

1. Evaluate lane obligations in deterministic order:
- lane 1: certification evidence freshness and readiness parity.
- lane 2: runtime-separation comparator/parity health.
- lane 4: ask deterministic contract parity (including error-code reachability obligations).
1. Any failed obligation blocks promotion.
1. Degraded-only findings remain visible and must carry owner plus escalation window.
1. Lane-level transition rules:
- if any lane emits a blocker, `governance_running -> promotion_blocked`;
- if all lanes are ready and degraded findings are non-blocking, `governance_running -> lane_evaluated`;
- only `lane_evaluated` can advance to `promotion_ready`.

### 5. Closeout and Promotion Lifecycle

1. Build `CloseoutHealthSnapshot`.
2. Apply precedence: `blocked` over `degraded` over `ready`, and `lane 1` over `lane 2` over `lane 4` when multiple blockers co-occur in one run.
3. Promotion is allowed only when no blocked obligations remain and required evidence is current.
4. Evidence freshness policy:
- lane-1 certification telemetry evidence is stale when older than 24 hours;
- lane-2 and lane-4 freshness windows are policy-defined and must be explicit in closeout output;
- unknown freshness values are treated as blocked.

## Interfaces and Dependencies

Normative source artifacts:

- `docs/brainstorms/2026-04-13-llm-wiki-runtime-pivot-requirements.md`
- `docs/plans/2026-04-06-feat-skill-authoring-family-certification-plan.md`
- `docs/plans/2026-04-12-feat-product-factory-runtime-separation-plan.md`
- `docs/cli-specs/2026-04-06-unreachable-functionality-audit.md`

Governance and validation dependencies:

- `bin/ask repo doctor-catalog --strict --json`
- `bin/ask repo validate --json` (degraded/allowed when invoked from `recursive_validation_guard` context; recorded as skipped-OK with explicit guard provenance)
- `bash scripts/verify-work.sh --project-governance`
- `python3 scripts/verify_skill_catalog_freshness.py --strict`
- runtime-separation comparator pipeline defined in `docs/plans/2026-04-12-feat-product-factory-runtime-separation-plan.md`

Skill dependencies for installation lane:

- `llm-wiki`
- `coderabbit:simplify`
- `uv-python-project-setup`
- `baseline-ui`

## Invariants / Safety Requirements

- Canonical-source invariant:
  - wiki markdown remains the only primary human+agent knowledge source for this lane.

- Viewer-boundary invariant:
  - Obsidian is read-only viewer context; no canonical ownership transfer to Obsidian-managed state.

- Installation-governance invariant:
  - installation/migration runs are invalid unless the required skill stack is evidenced.

- Inspector-availability invariant:
  - missing required inspector roles must either resolve via canonical fallback roles or block promotion.

- Fail-closed invariant:
  - missing governance evidence is treated as blocked, not best-effort pass.

- Blocker-taxonomy invariant:
  - every blocking decision includes explicit blocker code, owner, and escalation window.

- State-transition invariant:
  - lifecycle transitions cannot skip `preflight_ready` or `lane_evaluated` states.

- Acceptance-ID invariant:
  - existing `SA` identifiers remain stable; new acceptance criteria append without renumbering prior IDs.

- Privacy invariant:
  - sensitive-source ingestion requires classification and redaction policy before persistence.

- Projection-authority invariant:
  - runtime/projection surfaces remain derived and single-writer governed.

## Failure Model and Recovery

| Failure class | Trigger | Required behavior | Recovery exit condition |
| --- | --- | --- | --- |
| `BLOCKER_MODE_CONTRACT_MISSING` | `OperatingModeContract` absent or contradictory | Stop promotion; emit blocking diagnostics with owner assignment | Mode contract is present, valid, and parity-checked |
| `BLOCKER_SKILL_STACK_INCOMPLETE` | one or more required skills missing from installation run evidence | Fail installation gate; do not continue execution | Required skill set is complete and evidenced |
| `BLOCKER_INSPECTOR_UNAVAILABLE` | required inspector roles unavailable and fallback unresolved | Block promotion; emit role-resolution blocker | Required or fallback roles are available and recorded |
| `BLOCKER_CERTIFICATION_EVIDENCE_STALE` | readiness evidence freshness/parity fails lane-1 obligations | Block closeout and mark certification lane unhealthy | Fresh evidence passes declared lane-1 acceptance checks |
| `BLOCKER_RUNTIME_SEPARATION_DRIFT` | runtime-separation parity/comparator emits blocking regressions | Block promotion; preserve rollback-ready status | Comparator shows no undeclared blocker regressions |
| `BLOCKER_ASK_CONTRACT_DRIFT` | ask contract parity indicates unresolved deterministic gap | Block lane-4 closeout | Contract gap is resolved with deterministic evidence |
| `DEGRADED_COMPATIBILITY_SIGNAL` | skill-graph compatibility findings not in blocking exception set | Keep lane degraded-visible; continue with owner/escalation metadata | Finding resolved or explicitly accepted with expiry |
| `BLOCKER_EVIDENCE_FRESHNESS_UNKNOWN` | required lane evidence exists but freshness window is missing or non-evaluable | Treat lane as blocked and prevent promotion | Freshness window is declared and evidence age is evaluable |

Recovery policy:

- Recovery must be idempotent and safe to rerun.
- Any rollback must preserve canonical authority boundaries and evidence continuity.
- Promotion resumes only after the failed lane re-enters `ready`.
- Recovery ordering rule:
- resolve lane-1 freshness blockers first;
- then lane-2 parity blockers;
- then lane-4 contract parity blockers;
- then degraded-only compatibility findings.

## Observability

Required events and artifacts for this contract:

- `mode_contract_evaluated`
  - fields: `primary_mode`, `compatibility_mode`, `result`, `blocker_code?`.
- `installation_contract_evaluated`
  - fields: `required_skills`, `skills_present`, `inspectors_present`, `fallback_used`, `result`.
- `lane_obligation_evaluated`
  - fields: `lane_id`, `result`, `blocker_code?`, `evidence_ref`.
- `closeout_health_reported`
  - fields: `schema_version`, `overall_state`, `blocked_count`, `degraded_count`, `promotion_decision`.

Required health counters:

- `lane_ready_count`, `lane_degraded_count`, `lane_blocked_count`.
- `installation_skill_coverage_ratio` (required skills present / required skills total).
- `inspector_resolution_ratio` (resolved inspector roles / required inspector roles).
- `blocker_metadata_completeness_ratio` (blockers with code+owner+window+evidence / total blockers).

Closeout reporting requirements:

- every report must preserve lane-level outcomes for 1, 2, and 4;
- every blocker must be traceable to command evidence;
- status/checklist drift across requirements/spec/plan artifacts is itself a validation failure.
- every lane must include `freshness_state` and `freshness_age_hours` (or explicit `unknown` state that blocks promotion).

## Acceptance and Test Matrix

| ID | Area | Contract requirement | Verification target |
| --- | --- | --- | --- |
| SA1 | Mode contract | `llm_wiki_primary` is the only primary operating mode and `degraded_compatibility` is explicitly defined for skill-graph | Spec/frontmatter and governance contract show explicit mode ownership and blocking exceptions |
| SA2 | Source of truth | Canonical wiki root is explicit and source ownership split (raw/wiki/schema/projection) is unambiguous | Authority map and ownership documentation expose single-writer policy per surface |
| SA3 | Obsidian boundary | Obsidian is defined as viewer-only and cannot become canonical writer | Contract text and validation checks reject source-of-truth ambiguity |
| SA4 | Installation stack | Installation/migration contract requires `llm-wiki`, `coderabbit:simplify`, `uv-python-project-setup`, `baseline-ui` | Installation gate evidence includes all required skills or blocks with explicit reason |
| SA5 | Inspector roles | `skill-inspector` and `plugin-inspector` are checked before execution with deterministic fallback behavior | Gate evidence records inspector presence, fallback mapping, and decision path |
| SA6 | Fail-closed governance | Missing required skills, missing inspector coverage, or missing lane evidence blocks promotion | Blocking precedence is exercised in closeout report and promotion denied |
| SA7 | Lane-1 absorption | Certification/readiness obligations are owned by this pivot contract and cannot remain orphan blockers | Lane-1 evaluation recorded in closeout health with explicit pass/block result |
| SA8 | Lane-2 absorption | Runtime-separation recovery obligations are mandatory and parity regressions block closeout | Runtime-separation comparator/parity evidence is required for ready state |
| SA9 | Lane-4 absorption | Ask deterministic contract parity obligations are mandatory and unresolved contract-grade gaps block closeout | Ask-contract evidence shows no unresolved deterministic blocker classes |
| SA10 | Blocker taxonomy | Every blocker has deterministic code, owner, escalation window, and evidence path | Closeout report includes complete blocker metadata without null ownership |
| SA11 | Privacy and safety | Sensitive-source ingestion requires classification and redaction policy before persistence | Privacy gate evidence exists before ingest operations are promoted |
| SA12 | Anti-stall health loop | Recurring closeout health output prevents status/checklist drift across requirements/spec/plan | Health report includes drift check and fails when artifacts diverge |
| SA13 | Compatibility continuity | Required command/path compatibility remains explicit while compatibility mode is active | Compatibility checks pass for declared mandatory command surfaces |
| SA14 | Lifecycle determinism | Contract enforces explicit lifecycle states and legal transitions from declaration through promotion | Closeout outputs show state transitions without skipped intermediate states |
| SA15 | Evidence freshness gating | Lane outputs include freshness state and freshness age; unknown freshness is blocking | Closeout report shows freshness per lane and blocks when freshness cannot be evaluated |
| SA16 | Inspector quality coverage | Inspector-role resolution is measurable and fail-closed when unresolved | Inspector resolution ratio is present and unresolved coverage blocks promotion |
| SA17 | Blocker metadata completeness | Every active blocker includes code, owner, escalation window, and evidence reference | Blocker completeness ratio is 100% whenever promotion is attempted |
| SA18 | Governance contract traceability | OperatingModeContract, InstallationOrchestrationContract, and BlockedLaneObligation content are traceable to autoresearch hardening validation evidence | Validation pointers exist showing how governance contracts gate autoresearch promotion decisions and blocker resolution paths |

## Open Questions

- Should this pivot mandate one fixed canonical wiki root (`wiki/`) for all lanes, or allow policy-defined alternatives per bounded domain?
- What is the exact owner mapping and escalation SLA for lane-4 ask contract obligations in release windows?

## Definition of Done

- The pivot contract is written and accepted as canonical source for WHAT-level behavior.
- Mode, boundary, failure, and observability semantics are explicit enough that planning does not invent core behavior.
- Installation governance is fail-closed with required skill stack and inspector-role policy.
- Blocked lanes 1, 2, and 4 are integrated as explicit obligations in one contract.
- Acceptance matrix provides stable `SA` IDs that planning can reference directly.