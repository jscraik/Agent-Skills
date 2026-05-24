# Harness Engineering Adversarial Review: Spec/Plan Gap Hardening

## Severity-ranked findings

### 1) P0 - Route nondeterminism can misroute repeated-failure evidence into advisory loops instead of implementation repair
- Evidence:
  - `Plugins/harness-engineering/references/deterministic-stage-routing.md:17` allows prior-session/collector/repeated-failure inputs to route across six distinct stages "by intended outcome" with no deterministic tie-break.
  - `Plugins/harness-engineering/skills/he-router/SKILL.md:63-65` requires deterministic routing but only blocks when "still ambiguous"; this leaves room for arbitrary "intended outcome" interpretation.
  - `/private/tmp/he-session-collector-14d-bundle/harness-engineering-evidence.json:83-220` shows recurring `lint_failure` repeatedly routed to `he-fix-bugs`, while similar repeated-failure contexts elsewhere route to planning/spec paths.
- Failure scenario:
  1. Collector evidence contains the same recurring blocker class over many sessions.
  2. Router matches rule 11 and "intended outcome" is interpreted as plan/refine/reinforce instead of fix.
  3. Downstream stage produces valid local artifact quality but no blocker elimination.
  4. The next run ingests unchanged blocker signal and repeats the same advisory path.
  5. Team accumulates artifacts while runtime failure remains unresolved.
- Hardening target:
  - Add deterministic tie-break order for rule 11 in `deterministic-stage-routing.md` keyed by blocker taxonomy (`test_failure|lint_failure|git_state|permission|network`) and freshness.
  - Add validator that rejects rule-11 routes without explicit blocker-to-stage mapping evidence.

### 2) P0 - Full-implementation requests can still be silently downscoped through plan composition
- Evidence:
  - `Plugins/harness-engineering/skills/he-plan/SKILL.md:84-85` instructs "smallest proof-producing implementation units first."
  - `Plugins/harness-engineering/skills/he-plan/SKILL.md:149-151` blocks for missing evidence/authority but not for user-requested full-scope versus slice-scope mismatch.
  - `/Users/jamiecraik/dev/coding-harness/.harness/implementation-notes/2026-05-21-full-implementation-downscope-steering-admission.md:28-33` records this exact failure class in production behavior.
- Failure scenario:
  1. User requests full implementation.
  2. Plan stage interprets execution safety as smallest slice.
  3. Plan artifact passes shape/BLUF gates and remains internally consistent.
  4. Work stage executes only the slice and emits positive validation evidence for that slice.
  5. Closure language drifts toward "done enough" despite unmet full-scope intent.
- Hardening target:
  - Introduce mandatory `scope_authority` contract fields in plan/spec templates: `requested_scope`, `accepted_scope`, `downscope_reason`, `owner_acknowledged_downscope`.
  - Add lint gate failing any tracked plan with `requested_scope=full` and missing explicit downscope acknowledgment.

### 3) P1 - Missing specialist-role fallback enforcement drops coding/testing persona coverage under runtime role drift
- Evidence:
  - `Plugins/harness-engineering/references/subagent-routing.md:40-43` says to continue inline when mapped roles are missing.
  - `Plugins/harness-engineering/references/subagent-routing.md:55-62` asks stages to include role usage details, but no hard gate ties this to artifact completeness.
  - `Plugins/harness-engineering/skills/he-plan/SKILL.md:82-83` says specialist references are loaded only when trigger is "proved," which can be skipped in degraded runs.
- Failure scenario:
  1. Runtime manifest lacks one or more specialist reviewer roles (testing/correctness/adversarial lenses).
  2. Stage continues inline by contract.
  3. Inline operator omits persona-equivalent coverage and still produces structurally valid output.
  4. Plan/spec reaches execution without critical coding/testing challenge pass.
- Hardening target:
  - Require a `coverage_parity` section whenever any mapped role is missing, including inline replacement checklist per missing role.
  - Add artifact lint to fail if missing-role output lacks explicit testing/correctness/adversarial parity evidence.

### 4) P1 - Runtime persistence telemetry is effectively blind, enabling false confidence in "agent-native" behavior claims
- Evidence:
  - `/private/tmp/he-session-collector-14d-bundle/skill-invocation-summary.json:2-6` reports `analytics_status: unavailable_or_legacy` and `invocation_count: 0`.
  - `Plugins/harness-engineering/skills/he-router/SKILL.md:117-118` already warns quality checks do not prove runtime behavior, but no mandatory fallback metric is required in outputs.
- Failure scenario:
  1. Validation gates pass on package shape and references.
  2. Runtime invocation telemetry remains unavailable.
  3. Operators infer adoption/behavior quality from artifact production alone.
  4. Regressions in live agent invocation patterns are missed until user escalation.
- Hardening target:
  - Add required "runtime evidence status" block to HE outputs: `invocation_telemetry_status`, `collector_freshness`, `fallback_runtime_probe`.
  - Add guard: when telemetry is unavailable, block "runtime persistent" claims unless an explicit probe command/result is recorded.

### 5) P1 - Closure-state separation exists as policy but is not uniformly enforced as stage output schema
- Evidence:
  - `Plugins/harness-engineering/references/closure-mutation-contract.md:7-19` defines six independent closure/mutation states.
  - `Plugins/harness-engineering/skills/he-plan/SKILL.md:54-59` and neighboring stage contracts include overlapping but not complete state fields.
- Failure scenario:
  1. Plan/eval stage emits partial closure fields (for example mutation authority and recommendation).
  2. Live read/readback statuses are omitted.
  3. Human reads "ready/complete" language without visibility that readback verification never happened.
  4. External system diverges from local artifact assumptions.
- Hardening target:
  - Promote closure-mutation fields to a shared required output contract across `he-plan`, `he-work`, `he-eval-report`, and `he-linear-plan`.
  - Add one validator that fails artifacts claiming closure recommendation without explicit state for all six fields.

### 6) P2 - Collector evidence freshness is not a hard precondition in router handoffs, enabling stale-boundary decisions
- Evidence:
  - `Plugins/harness-engineering/skills/he-router/SKILL.md:35-37` treats session evidence as optional input.
  - `Plugins/harness-engineering/skills/he-router/SKILL.md:61-69` prescribes minimal inspection/handoff but does not require evidence age checks.
  - `deterministic-stage-routing.md:21` mentions stale-evidence stop rules only in `he-phase-work`, not as router precondition.
- Failure scenario:
  1. Router consumes old collector bundle after repo/runtime state changes.
  2. Stage decision is made from stale blockers and stale lifecycle context.
  3. Downstream stages execute correctly against wrong premise.
  4. Execution churn increases while current blocker remains unaddressed.
- Hardening target:
  - Add router-level freshness gate (`collector_age`, `repo_head_match`, `tracker_snapshot_age`).
  - If freshness fails, force blocker route with single recovery action before stage selection.

## Cross-cutting hardening gaps (templates/references/spec-plan)
1. Add shared "Agent-Native Runtime Persistence Contract" reference consumed by spec/plan/work/eval stages.
2. Add explicit "strict-boundary proof" template sections: canonical source boundary, external mutation boundary, readback boundary, and runtime projection boundary.
3. Add mandatory "persona-lens coverage matrix" template row set (coding, testing, correctness, adversarial) with evidence links.
4. Add a dedicated validator for scope-authority mismatch and downscope acknowledgement.
5. Add a dedicated validator for runtime telemetry blind mode to prevent unsupported confidence claims.

WROTE: /Users/jamiecraik/dev/agent-skills/artifacts/reviews/he-spec-plan-gap-hardening/adversarial-reviewer.md
