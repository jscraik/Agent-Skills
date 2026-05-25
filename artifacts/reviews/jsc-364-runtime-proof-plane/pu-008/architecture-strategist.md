# Architecture Review - JSC-364 PU-008 Runtime Proof Plane

## 1) Architecture Overview

The implemented PU-001..PU-007 lane preserves the intended control-plane layering from spec and plan:

- Contracts first: runtime proof schemas and validator surfaces exist under Infrastructure/config/schemas/* and Infrastructure/scripts/validation-and-linting/*, matching spec intent to make proof claims schema-gated before orchestration expansion (/.harness/specs/2026-05-24-agent-skills-codex-runtime-proof-plane-spec.md:45, /.harness/specs/2026-05-24-agent-skills-codex-runtime-proof-plane-spec.md:47, /Infrastructure/config/schemas/runtime-card.v1.schema.json:1).
- Runtime-closeout integration is kept inside repo command implementation, not spread across unrelated modules, and truth boundaries are explicitly encoded in output (/Infrastructure/scripts/lib/ask/commands/repo_impl.py:1344, /Infrastructure/bin/ask:1069).
- Goal/state contract still frames PU-008 as final validation/docs/delivery sweep, consistent with architectural closure posture (/docs/goals/jsc-364-agent-skills-codex-runtime-proof-plane/goal.md:83, /docs/goals/jsc-364-agent-skills-codex-runtime-proof-plane/state.yaml:428).

## 2) Change Assessment

How changes fit the architecture:

- Good fit: closeout now distinguishes changed_scope vs workspace_scope for runtime evidence, addressing prior stale-state contamination risk and maintaining patch-local decision surfaces (/Infrastructure/scripts/lib/ask/commands/repo_impl.py:1376, /Infrastructure/scripts/lib/ask/commands/repo_impl.py:1388).
- Good fit: invalid changed runtime evidence is now a closeout blocker (runtime_evidence_invalid), preventing false commit-readiness for malformed proof artifacts (/Infrastructure/scripts/lib/ask/commands/repo_impl.py:1436).
- Good fit: path normalization helper localizes runtime evidence path matching, reducing coupling to changed-file source format (/Infrastructure/scripts/lib/ask/commands/repo_impl.py:1249, /Infrastructure/scripts/lib/ask/commands/repo_impl.py:1259).

## 3) Compliance Check

Upheld:

- Separation of concerns between schema contracts, command orchestration, and human-readable rendering is maintained.
- Boundary transparency is explicit: runtime evidence output marks command/schema/PR/tracker/docs truth boundaries as checked vs unchecked, preventing hidden authority shifts (/Infrastructure/scripts/lib/ask/commands/repo_impl.py:1393, /Infrastructure/bin/ask:1070).
- No evidence of new circular dependency introduction in the reviewed surfaces; changes remain within expected command + schema + tests boundaries.

Violations / gaps:

- No Type-1 architectural boundary violation found in reviewed PU-007/PU-008 evidence.
- Remaining issues are Type-2 operational/completion gaps (delivery state and broad-gate drift), not architecture-shape drift.

## 4) Risk Analysis (Severity Ranked)

Medium - Delivery-state closure risk (not architecture drift, but completion integrity risk)

- Evidence: PR 206 still has unresolved check state (pr-template fail, security checks pending at snapshot), and merge state was UNSTABLE in the recorded sweep artifact (/artifacts/reviews/jsc-364-runtime-proof-plane/pu-007/pr-green-sweep-pr206.md:8, :15, :46).
- Architectural implication: proof-plane design is coherent, but closure claims can outrun live delivery truth unless PU-008 explicitly re-verifies PR/CI state at finish time.

Low - Focused validation trigger remains path-shape sensitive (residual)

- Evidence: prior reviewer highlighted changed-file normalization dependency for runtime-evidence focused validation trigger (/artifacts/reviews/jsc-364-runtime-proof-plane/pu-007/he-code-reviewer.md:7).
- Current posture: helper normalization exists and materially reduces risk (/Infrastructure/scripts/lib/ask/commands/repo_impl.py:1249), so this is now a residual test-hardening gap, not a boundary failure.

## 5) Recommendations

1. Keep PU-008 as a strict delivery-truth sweep: rerun green-sweep evidence for PR 206 and only mark completion when PR/check/review/tracker state is freshly aligned.
2. Add one narrow regression test for changed-file path variants (./, absolute) feeding runtime-evidence trigger logic to retire the remaining low-severity normalization risk.
3. Preserve current layering: keep schema evolution in Infrastructure/config/schemas/*, closeout/runtime decision logic in repo_impl.py, and presentation-only summaries in Infrastructure/bin/ask.

## Harness Eval Report Fields

- eval_report_status: pass_with_residual_risk
- architecture_drift: none_detected
- boundary_changes: none_unapproved
- unresolved_type1_decisions: []
- recommended_completion_state: proceed_after_live_delivery_truth_recheck
- confidence: high
- residual_risk:
  - delivery_state_not_yet_green_at_snapshot
  - low_severity_path_variant_trigger_test_gap

WROTE: artifacts/reviews/jsc-364-runtime-proof-plane/pu-008/architecture-strategist.md
