---
title: feat: Skill Graph Recursive Loop Parity Pass (Canonical, Governance, Telemetry)
type: feat
date: 2026-02-23
deepened_on: 2026-02-23
deepened_source: manual_parallel_research_and_agent_feedback
brainstorm: docs/brainstorms/2026-02-23-skill-graph-recursive-loop-parity-pass-brainstorm.md
status: completed
affected_features:
  - recursive skill loop
  - promotion governance
  - canonical lesson graph
  - shadow telemetry
---

# feat: Skill Graph Recursive Loop Parity Pass (Canonical, Governance, Telemetry)

## Enhancement Summary

**Deepened on:** 2026-02-23
**Sections enhanced:** 6
**Research provenance:** manual review against plan/spec/docs + local validation pass (no external agent runs).

### Key improvements
1. Expanded plan with explicit state-machine contracts, blocked/rollback semantics, and kill-switch pre-emption rules.
2. Added data/telemetry controls for canonical lesson persistence and mandatory observability artifacts with privacy- and reliability-focused edge-case handling.
3. Added security + governance hardening paths (CAS, reviewer policy, ownership checks, immutable artifacts) plus measurable verification criteria.

### New considerations discovered
- The highest-impact gap is not just missing outputs; it is untrusted mutation surfaces (canonical writes and approvals) lacking proof-of-authority controls.
- Recovery and idempotency need to be designed as primary plan constraints, not optional hardening tasks.
- Daily telemetry should be treated as compliance-grade output, with retention, masking, and schema checks aligned to CI gate quality.

## Section manifest

- **Section 0**: Outcome → opportunities → solution (clarify target state and control model)
- **Section 1**: Scope and boundaries (include explicit non-goals and compatibility posture)
- **Section 2**: Plan epics and tasks (map by execution risk and dependency criticality)
- **Section 3**: Acceptance criteria (make assertions machine-checkable)
- **Section 4**: Risks and checks (add incident/rollback and abuse-case matrix)
- **Section 5**: Execution order and dependencies (serialize controls before automation)
- **Section 6**: Verification command set (add preflight and postflight checks)

## Table of Contents

- [0) Outcome → opportunities → solution](#0-outcome--opportunities--solution)
- [1) Scope and boundaries](#1-scope-and-boundaries)
- [2) Plan epics and tasks](#2-plan-epics-and-tasks)
  - [Epic A — Canonical lesson registry + deterministic lesson lifecycle](#epic-a--canonical-lesson-registry--deterministic-lesson-lifecycle)
  - [Epic B — Always-on telemetry + daily outputs](#epic-b--always-on-telemetry--daily-outputs)
  - [Epic C — Governance and control correctness](#epic-c--governance-and-control-correctness)
  - [Epic D — Validation and rollout](#epic-d--validation-and-rollout)
- [3) Acceptance criteria](#3-acceptance-criteria)
- [4) Risks and checks](#4-risks-and-checks)
- [5) Execution order and dependencies](#5-execution-order-and-dependencies)
- [6) Verification command set](#6-verification-command-set)
- [7) Remediation closeout status (2026-02-26)](#7-remediation-closeout-status-2026-02-26)

## 0) Outcome → opportunities → solution

### Outcome
Bring implementation to parity with documented recursive skill-graph contracts by adding (1) canonical lesson persistence, (2) required daily telemetry outputs, (3) run/operator control invariants (idempotency, ownership, recovery), (4) real adversarial judge paths, and (5) reviewer authorization enforcement.

### Key opportunities
- Improve auditability and safety before Phase-4 retrieval rollout.
- Make governance automatable in CI and human review.
- Reduce uncertainty between docs and runtime behavior.

### Chosen solution
Execute one consolidated implementation pass with a small rollout sequence:
- establish canonical registry + promotion write path,
- harden event/telemetry always-on outputs,
- enforce lock/idempotency/adversarial controls,
- strengthen reviewer checks and version CAS,
- add docs + verification updates.

### Execution-loop and control architecture (agent-native-architecture focus)
**schema_version: 1.0**

- **Objective:** Ensure every run is resumable, safely abortable, and auditable with deterministic completion semantics.
- **Constraints:** No silent failures, no hidden side effects, and operator control must always outrank normal loop progress.
- **Failure cost if wrong:** accidental duplicate promotions, incomplete audit trail, and unauthorized canonical graph mutation.

#### Parity and control map (high priority paths)
| User action | Agent capability path | Current gap |
|---|---|---|
| Trigger loop run | `recursive_skill_loop.py` CLI options + run directory contracts | Partial: kill/abort behavior is currently secondary to normal terminal transitions |
| Resume/replay after interruption | run-id + resume path + deterministic journals | Partial: stale/replay duplicate handling exists but needs explicit blocked + rollback state |
| Emergency stop run | No explicit kill-switch contract | **Gap (high):** no authoritative kill behavior for incident control |
| Approve canonical lesson | `human_promote_recursive_run.sh` + validator | Needs explicit version-locked rollback semantics |
| Roll back/undo bad run mutation | Not explicitly modeled | **Gap (high):** need terminal rollback and artifact cleanup contract |

#### Execution-loop contract additions
- **Start:** run enters `run_initialized` and must emit `run_state_changed` before any judge step.
- **Continue:** each meaningful transition must emit `run_state_changed`; loops stop only on terminal states.
- **Public contract compatibility:** existing public contract is `terminal_status ∈ {passed|failed|escalated|aborted}` and `stop_reason ∈ {pass|budget_exhausted|escalated|aborted|policy_failed|evaluator_conflict|dependency_missing}` from `docs/skill-graphs/index.md`; implementation must normalize control states through event fields (not through custom status fields):
  - `run_completed` -> `terminal_status=passed`, `stop_reason=pass`
  - `run_failed` -> `terminal_status=failed`, `stop_reason=policy_failed`
  - `run_aborted` -> `terminal_status=aborted`, `stop_reason=aborted`
  - `run_rollforward_blocked` -> `terminal_status=failed`, `stop_reason=policy_failed`, blocker event `blocker_code=run_rollforward_blocked`
  - `run_rollback_required` -> `terminal_status=failed`, `stop_reason=dependency_missing`, blocker event `blocker_code=run_rollback_required`
- **Partial completion:** non-terminal checkpoints (`run_judgment_wait`, `run_adversarial_wait`, `run_operator_approval_required`) are explicit and must persist outputs for operator handoff.
- **Blocked state behavior:** duplicate run lock, stale resume token, CAS mismatch, or reviewer-policy rejection must transition to explicit blocked/rollback states, not implicit exits.
- **Kill-switch:** add a high-priority `--kill-switch-file` (or env-equivalent) checked before/after state transitions:
  - writes `run_state_changed` reason `kill_switch_activated`
  - emits terminal event `run_aborted`
  - releases run lock and persists a rollback recommendation record.
- **Rollback:** canonical lesson writes and promotion files must include lineage so rollback/replay can be reasoned from artifacts alone (version, predecessor id, expected-version origin, and operator).
- **Migration guard:** document this mapping as an explicit contract extension with explicit removal criteria in `docs/skill-graphs/schemas/gate-contract.schema.md` before Phase-4 enablement.

#### Rollback / recovery invariants
- **Idempotency key + state lock** must gate duplicate processing attempts.
- **Expected-version CAS** is the normal path for safe re-promote; mismatch enters `run_rollforward_blocked` and emits explicit blocker event.
- **Recovery policy:** stale terminal output retries must be no-op, while non-terminal stale resumes must fail closed into `run_rollback_required`.
- **Operator controls:** kill-switch and allowlisted approve path are highest priority control planes and must preempt normal judge flow.

### Research Insights

**Best practices:**
- Treat the loop as a deterministic state machine with an explicit terminal-state enum and transitions validated by schema; every non-idempotent write should be keyed by run id.
- Apply two-level concurrency model: process-level mutex first, then artifact-level optimistic lock (CAS) before any canonical mutation.
- Separate “control plane” events (approval, lock, kill, rollback) from “candidate outcomes” events to simplify audit review.

**Performance considerations:**
- Keep state writes append-only and periodic flushes frequent; avoid locking across long judge calls.
- Pre-create lock files with atomic rename to reduce races under concurrent starts.

**Implementation details:**
- Consider explicit transition table in JSON Schema for allowed edges, with tests for illegal transitions.
- Add an invariant that blocked/rollback states must include a human-readable blocker plus machine-readable code.

**Edge cases:**
- Concurrent starts with same run_id should be rejected before evaluation begins.
- Kill-switch asserted during active write should force immediate flush and avoid partial mutation; prefer two-phase commit style for canonical writes.
- Replay of a completed run should never re-open approval path.

**References:**
- Python process locking and atomic file write patterns (temp-file rename semantics)
- GitHub Actions artifact conventions and matrix-safe upload ordering

## 1) Scope and boundaries

### In scope
- `Skills/skill-builder/Infrastructure/scripts/recursive_skill_loop.py`
- `Skills/skill-builder/Infrastructure/scripts/validate_recursive_promotion.py`
- `Skills/skill-builder/Infrastructure/scripts/build_recursive_skill_shadow_report.py`
- `Infrastructure/scripts/human_promote_recursive_run.sh`
- `Infrastructure/scripts/run_recursive_skill_shadow_cycle.sh`
- `Infrastructure/scripts/validate_recursive_promotions.sh`
- `.github/workflows/recursive-skill-shadow.yml`
- docs under `docs/skill-graphs/**`

### Out of scope
- Retrieval-time lesson injection in run loop (still post-v1),
- full multi-judge jury architecture,
- UI-facing operator portal and role federation.

### Research Insights

**Best practices:**
- Bound the scope by interface rather than file list: only surfaces that own canonical state and governance should be modified; avoid touching retrieval and evaluation prompt tuning unless directly blocked by dependency.
- Out-of-scope guardrail: freeze any behavior changes to non-loop docs unless they are strictly required to keep contracts honest.

**Performance considerations:**
- Minimize blast radius by adding feature-flag-like arguments first for telemetry/locking paths.
- Avoid broad workflow edits that increase cycle runtime (e.g., adding expensive graph scans in every job by default).

**Implementation details:**
- Add a canonical output contract file (append-only schema doc + validation script) before touching core orchestration.

**Edge cases:**
- If docs become stale mid-change, treat stale docs as out-of-scope debt only if it blocks correctness; otherwise file a follow-up plan task.
- If upstream scripts call these loops from legacy wrappers, preserve CLI compatibility by adding defaulted optional flags.

**References:**
- Internal repo `README` and docs map in `Docs/agents/` for governance patterns
- AGENTS requirement: canonical-only compatibility posture

## 2) Plan epics and tasks

### Epic A — Canonical lesson registry + deterministic lesson lifecycle

1. **A1** Add canonical lesson store and lock metadata (`Infrastructure/artifacts/skill-graphs/lessons/`):
   - files: `canonical-lessons.jsonl`, `canonical-lesson-index.json`
   - fields aligned to `docs/skill-graphs/schemas/canonical-lesson.schema.md`
   - active lesson overlap checks by `{scope_skill, scope_profile}` + status conflict guard.
   - verification: create/update helper script test that writes, supersedes, and rejects overlapping `active` entries.

2. **A2** Add canonical lesson writer in `human_promote_recursive_run.sh` (approved path only):
   - require `--expected-version` in optimistic compare-and-swap against `promoted` lesson version row,
   - mark previous active as `superseded`, append new `active` with provenance + SHA,
   - idempotent behavior when same `(run_id, lesson_id)` replayed.
   - verification: script run with same payload twice returns same resulting status and same version lineage.

3. **A3** Add explicit promotion artifact version fields and lifecycle transition fields in `promotion_decision.json`:
   - include `lesson_status`/`lesson_effective_to` when approved,
   - preserve immutable decision hash for audit.
   - verification: `validate_recursive_promotion.py` requires these fields for approved state.

### Epic A Research Insights

**Best practices:**
- Model canonical lesson as a write-ahead log with immutable entries and compacted index; treat index as a cache, not source of truth.
- CAS should validate expected version and also include source fingerprint (run hash + artifact hash).
- Keep status transitions deterministic (`pending` -> `active` -> `superseded`/`revoked`) and version monotonic.

**Performance considerations:**
- Use index file for O(1) lookup and conflict checks; keep JSONL append path for auditability.
- Keep retention policy separate from active runtime index to avoid heavy rewrite operations.

**Edge cases:**
- Replayed approval requests with identical payload: must be no-op once canonical version matches.
- Replay with changed timestamps but same logical content should not create duplicate active lessons.
- If hash lineage fails, fail closed and require human recovery review, not overwrite.

**Implementation details:**
- Add a lock file per skill graph canonical file and validate before each canonical mutation.
- Include `predecessor_lesson_id` and `decision_hash` fields to support rollback trace.

**References:**
- Immutable ledger-style data modeling patterns (append-only event logs + snapshot/index)

### Epic B — Always-on telemetry + daily outputs

1. **B1** Make event trail mandatory in loop run:
   - move event writes from debug-optional to always-on (`run/events.jsonl`),
   - include `promotion_approved` emission in `human_promote_recursive_run.sh` without requiring `--emit-debug-artifacts`.
   - emit immutable `run_blocked` events for `run_rollforward_blocked` and `run_rollback_required` so control failures are machine-readable.
   - verification: successful run must contain at least `run_initialized`, `run_state_changed` (with normalized terminal status/reason), and `failure_event` when non-pass.

2. **B2** Add daily outputs generation in `build_recursive_skill_shadow_report.py`:
   - generate `docs/skill-graphs/telemetry/daily-skill-health.md`,
     `Infrastructure/artifacts/skill-graphs/telemetry/failure-pattern-candidates.jsonl`,
     `Infrastructure/artifacts/skill-graphs/telemetry/promotion-queue.md`.
   - preserve existing `shadow-dashboard.json` + pilot readouts as compatibility.
   - verification: run script with synthetic `run_*` dirs and assert output files are present and parseable.

3. **B3** Add CI upload path for new telemetry outputs in `.github/workflows/recursive-skill-shadow.yml`.
   - verification: workflow payload includes required file paths.

4. **B4** Extend canonical event schema before implementation:
   - update `docs/skill-graphs/schemas/gate-contract.schema.md` with explicit envelope fields required by plan:
     `run_id`, `event_id`, `skill_name`, `task_profile`, `event_type`, `terminal_status`, `stop_reason`, `blocker_code`, `severity`.
   - require `run_state_changed`, `promotion_approved`, and `run_blocked` field semantics + versioned schema version.
   - enforce this schema in `build_recursive_skill_shadow_report.py` before artifact emission.

### Epic B Research Insights

**Best practices:**
- Emit telemetry as write-once JSONL events with schema checks so one parser can read both successful and failed runs.
- Include UTC normalized timestamps and explicit event ids for dedupe across reruns.
- Separate report generation from report publication; generator should be idempotent and resumable.

**Performance considerations:**
- `build_recursive_skill_shadow_report.py` should avoid scanning unchanged files twice; cache parsed windows by manifest list.
- Keep `daily-skill-health.md` lightweight and deterministic to enable meaningful diffs.

**Security considerations:**
- Redact/omit reviewer names, emails, or secrets in telemetry by default. Keep reviewer identity as allowed hash or allowlist id where policy permits.
- Validate output location and ownership to avoid symlink traversal and artifact exfiltration.

**Edge cases:**
- Empty run window should still generate all required output files with explicit `no-data` states.
- Partial runs should generate `run_rollforward_blocked`-specific sections instead of silent omission.

**Implementation details:**
- Add strict JSON schema check after report generation to fail the job early on malformed telemetry output.

**References:**
- GitHub Actions artifact upload semantics for optional paths; choose required output paths to avoid false-green jobs.

### Epic C — Governance and control correctness

1. **C1** Add run recovery/concurrency/idempotency:
   - add run lock state (`--run-owner`, `--run-lock`, `--idempotency-key`) in `recursive_skill_loop.py`,
   - define terminal states explicitly and reject stale resume attempts / duplicate terminal transitions.
   - verification: reproduce duplicate execution command and confirm stable non-duplicating outputs.

2. **C2** Implement adversarial check path:
   - separate `evaluate_candidate_adversarial(...)` invoked on checkpoint conditions,
   - enforce metadata fields: `judge_mode: adversarial` and checkpoint reason trail,
   - escalate/hold if adversarial path fails while standard passes.
   - verification: crafted profile forcing adversarial failure causes terminal reason `evaluator_conflict` or configured escalation.

3. **C3** Enforce reviewer allowlist/rbac with ownership and rotation:
   - define single source-of-truth policy file + signature at `docs/skill-graphs/governance/recursive-loop-approvers.yaml` and `docs/skill-graphs/governance/recursive-loop-approvers.sig`.
   - load allowlist with `source_type` (`ops`, `build`, `robotic`) and minimum role/permission required for `approve` actions; reject any approvals without role match.
   - validator and approver script must verify policy signature/key freshness before any approval mutation.
   - stale cache guard: cached allowlist must be refreshed in each invocation if mtime is older than 2 minutes or hash changed on disk.
   - verification: wrong-role review attempt hard-fails with blocker artifact and no canonical/write mutation.

4. **C4** Add explicit kill-switch and rollback semantics:
   - add configurable kill-switch input (`--kill-switch-file`/`SKILL_GRAPH_KILL_SWITCH_PATH`) in `recursive_skill_loop.py`;
   - define rollback-required terminal state and evidence outputs (`run_rollback_required`, `rollback_recommendation.json`);
   - require lock cleanup + state finalization when kill-switch, duplicate terminal transition, or CAS mismatch occurs.
   - verification: simulate kill-switch activation mid-run and assert lock release, terminal state emission, and non-approval side effects.

### Epic C Research Insights

**Best practices:**
- Use least privilege for operator commands: require explicit policy check and audit record before any mutation beyond logs.
- Split adversarial evaluation into explicit route with traceable rationale and reason codes.
- Run adversarial checks before optimistic auto-advance transitions but after baseline standard checks.

**Performance considerations:**
- Keep adversarial checks deterministic and cached per iteration key where safe; avoid duplicate expensive computations.
- Kill-switch checks should be constant-time and in-loop (before and after expensive operations).

**Security considerations:**
- Approver policy source is file-backed and signature-verified; signature must rotate with the same cadence as role changes.
- Policy updates must occur via reviewed change with `min_approvers` and immutable signer identity list.
- Ensure expected-version CAS requires both candidate version and run hash to reduce replay collisions.

**Edge cases:**
- Approval script run from untrusted shell environment should still fail closed if policy file missing/empty.
- Kill-switch in same filesystem as run lock should not create deadlocks on partial writes.
- Duplicate terminal transitions should write blocker artifact only once.

**Implementation details:**
- Add machine-parseable `run_blocker` object with `code`, `message`, `remediation_owner`.
- Define rollback recommendation schema and include a minimum owner field.

### Epic D — Validation and rollout

1. **D1** Add/extend validation checks:
   - `Infrastructure/scripts/validate_recursive_promotions.sh` includes canonical store validation and reviewer policy checks.
   - add failure-mode unit-like checks for idempotency and expected_version.
   - verification: CI command passes zero errors on healthy fixture set.

2. **D2** Update docs to reflect runtime behavior and remove stale claims in:
   - `docs/skill-graphs/index.md`, `docs/guides/recursive-skill-loop.md`, `docs/guides/recursive-promotion-gate.md`, `docs/skill-graphs/pilots/ui-skills-shadow-results.md`,
   - add explicit contract extension section in `docs/skill-graphs/schemas/gate-contract.schema.md` and align terminal status/stop-reason mapping for `run_rollforward_blocked`, `run_rollback_required`, `run_aborted`.
   - add mandatory event envelope requirements in `docs/skill-graphs/telemetry/daily-outputs.md` (`run_state_changed`, `promotion_approved`, `run_blocked`, blocker_code contract).
   - mention canonical store locations and the migration guard before Phase-4 event enum promotion.

### Epic D Research Insights

**Best practices:**
- Co-locate validation commands with their failure policy (warning vs hard-fail).
- Validate both structure and intent: schema-valid files with semantic invariants.

**Performance considerations:**
- Keep CI fixtures small and targeted for quick checks.
- Cache expensive validation outputs only when running on pull request changes (optional diff mode).

**Edge cases:**
- Validation script may run outside canonical environment; fail fast with explicit dependency checks.
- Dual-mode docs (planned vs implemented) should avoid implying hidden behavior.

**Implementation details:**
- Add golden fixture sets for: lock contention, CAS miss, missing allowlist, and kill-switch during finalization.

## Phase-to-Task Execution Map
| Phase | Task IDs | Exit Gate |
|---|---|---|
| Phase 1 | T1, T2, T3, T4 | Canonical lifecycle + telemetry schema contracts approved |
| Phase 2 | T5, T6, T7, T8 | Runtime governance controls implemented and validated |
| Phase 3 | T9, T10, T11, T12, T13 | Validation + docs parity checks passing |

## Task Graph (id / depends_on)
```yaml
tasks:
  - id: T1
    title: Implement canonical lesson store and lifecycle index
    depends_on: []
  - id: T2
    title: Implement approved-path canonical writer with CAS safeguards
    depends_on: [T1]
  - id: T3
    title: Enforce mandatory event envelope and always-on events.jsonl emission
    depends_on: []
  - id: T4
    title: Extend schema contracts for blocker and terminal compatibility mappings
    depends_on: [T3]
  - id: T5
    title: Add run recovery, lock ownership, and idempotency controls
    depends_on: [T1, T3]
  - id: T6
    title: Add kill-switch and rollback-required blocking semantics
    depends_on: [T5]
  - id: T7
    title: Enforce reviewer allowlist policy and signed governance checks
    depends_on: [T2]
  - id: T8
    title: Implement adversarial checkpoint gating and conflict escalation
    depends_on: [T3]
  - id: T9
    title: Generate required daily telemetry outputs and promotion queue artifacts
    depends_on: [T3, T4]
  - id: T10
    title: Wire CI workflows to validate and publish governance/telemetry artifacts
    depends_on: [T7, T9]
  - id: T11
    title: Extend promotion validation to enforce policy, provenance, and event evidence
    depends_on: [T2, T7, T10]
  - id: T12
    title: Update guides and schema docs to match implemented runtime behavior
    depends_on: [T4, T6, T9, T11]
  - id: T13
    title: Execute verification suite and publish rollout readiness evidence
    depends_on: [T8, T10, T11, T12]
```

## 3) Acceptance criteria
- A v1 run always writes events to a canonical location.
- `run_*/run.json`, `iteration_journal.jsonl`, and `promotion_decision.json` remain emitted and schema-valid.
- Canonical lesson decisions are persisted, versioned, and enforced via expected-version CAS.
- Non-allowlisted reviewers cannot approve.
- `build_recursive_skill_shadow_report.py` always produces required daily telemetry outputs.
- `--emit-debug-artifacts` only controls extra verbose artifacts, not core telemetry.
- Kill-switch activation at any checkpoint immediately transitions to terminal abort output with explicit rollback recommendation and lock release.
- Duplicate terminal transitions or stale resumes produce explicit blocked/rollback artifacts instead of silent exit.
- Blocked duplicate promotion attempt (CAS fail, lock contention, policy reject) leaves `canonical-lessons.jsonl` and `canonical-lesson-index.json` unchanged.
- Replay with wrong reviewer must hard-fail, emit immutable `run_blocked` artifact, and produce a non-zero exit code.
- Kill-switch observed after approval decision but before state finalization still releases lock and finalizes only terminal state + blocker evidence.

### Research Insights

**Best practices:**
- Convert criteria into machine-checkable assertions (e.g., schema checks + grep of event reasons + lock state asserts).
- Add one acceptance criterion per critical invariant to prevent partial pass with drift.

**Performance considerations:**
- Track runtime of critical commands (loop start-to-completion and report generation) and add thresholds.

**Validation additions:**
- Add assertions for telemetry file presence in both normal and failure mode.
- Add fixture-driven checks for `run_state_changed` transitions, blocked duplicate promotion, wrong-reviewer replay, and stale-resume hard-fail behavior.
- Add event-envelope schema fixture (`docs/skill-graphs/schemas/gate-contract.schema.md`) validation for `promotion_approved`, `run_state_changed`, and `run_blocked` fields.

**Edge cases:**
- Must require explicit evidence file when run is blocked by policy; absence should fail acceptance.
- Approval criteria should include policy check before idempotent replay success to avoid “stale success” illusions.
- Duplicate blocked replay with mismatched reviewer identity must never mutate canonical files and must emit `run_blocked` with immutable evidence.

## 4) Risks and checks
| Risk | Impact | Mitigation |
|---|---|---|
| Scope creep into non-v1 retrieval rollout | delays | gate tasks explicitly and defer all retrieval injection |
| Policy drift between docs and scripts | rework and CI confusion | plan requires docs sync immediately after each behavior change |
| Duplicate canonical writes under concurrent runs | inconsistent lesson graph | add idempotency key + CAS + lock/state transition checks |
| Validator false negatives from strict checks | blocked approvals | keep warning vs error distinction; stage check rollouts |
| Kill-switch unavailable during incident | unsafe continuation of bad runs | define kill-switch as highest-priority control input with terminal preemption |

### Risk Register Enhancements

| Risk | Signal | Detection | Containment |
|---|---|---|---|
| Reviewer allowlist compromise | unauthorized approver attempts or stale policy cache | alert when signer hash changes outside review window or role set does not meet minimum role | lock + reject + immediate operator alert + require signed allowlist refresh + key rotation review |
| Canonical hash mismatch | tampered lesson metadata | validator compares signed hashes, emits rollback required | stop promotions until manual resolution |
| Telemetry leakage | accidental user or secret data in events | static scan on telemetry fields | masking + schema allowlist |
| Run lock deadlock | interrupted cleanup | heartbeat + stale-lock timeout + safe release hook | automated recovery job |

## 5) Execution order and dependencies
- A1 -> A2 -> A3
- B1/B2/B3/B4 in parallel after A1 foundation decisions finalized
- C1/C2/C3/C4 after A1, before D1
- D1 after all core tasks, D2 final pass

### Execution plan enhancements

- **Critical path first:** A1, C1, A2, C3, C4.
- **Canary gates:** after A1/C1, run one short synthetic run and validate transitions before proceeding to B2 report changes.
- **Rollback-ready milestones:** create checkpoints after each milestone with artifact snapshots for easier partial rollback.

## 6) Verification command set
- `python3 Skills/skill-builder/Infrastructure/scripts/recursive_skill_loop.py --help`
- `bash Infrastructure/scripts/run_recursive_skill_shadow_cycle.sh --runs-per-profile 1 --window-days 3`
- `python3 Skills/skill-builder/Infrastructure/scripts/build_recursive_skill_shadow_report.py --runs-root Infrastructure/artifacts/skill-graphs/runs --window-days 3`
- `bash Infrastructure/scripts/validate_recursive_promotions.sh --changed-only --base-sha HEAD~1 --head-sha HEAD`
- `python3 ~/.codex/Infrastructure/scripts/plan-graph-lint.py .agent/PLANS.md`
- `bash ~/.codex/Infrastructure/scripts/verify-work.sh`

### Enhanced Verification matrix (added)

**Preflight checks:**
- Environment readiness: python + shell deps, write permissions for artifacts and docs directories.
- Policy presence: reviewer allowlist file exists and is not empty.
- Schema files exist for new canonical and event structures.

**In-run checks:**
- State transition validity + terminal-status compatibility checks against existing `terminal_status`/`stop_reason` enums.
- Canonical CAS success and lock acquisition/release.
- Mandatory telemetry event presence, including required `run_state_changed`, `promotion_approved` (if applicable), and `run_blocked`.

**Postflight checks:**
- Daily outputs exist and parse.
- Validation script returns strict-mode pass.
- Evidence bundle produced (event + report + promotion decision).
- Replay/blocked fixture checks confirm no canonical mutation on reject paths and hard-fail on wrong reviewer.

## 7) Remediation closeout status (2026-02-26)

- [x] T1: Baseline parity manifest collection added (`Infrastructure/scripts/verify_recursive_skill_graph_artifacts.py`) and run directory classification implemented.
- [x] T2: Canonical control/lesson roots are initialized and tracked in-repo with deterministic defaults and schema metadata.
- [x] T3: Non-destructive verifier/repair tooling added (`--dry-run`, `--prune-empty`) with quarantine semantics for legacy/empty run dirs.
- [x] T4: Validation layer hardened for mandatory telemetry artifacts, blocker-state checks, and schema-specific error codes.
- [x] T5: CI gate wiring updated for strict per-run artifact checks, including promotion + parity report emission.
- [x] T6: Shadow reporting now enforces required telemetry output files and validates JSON/JSONL payloads.
- [x] T7: Docs updated for required control and lesson artifact paths; new closeout status appended to this plan.
- [x] T8: Regression coverage expanded for bootstrap/parity verification and required-file validation.
- [x] T9: Closeout execution path completed (dry-run manifest, strict mode smoke checks, and command set execution).
