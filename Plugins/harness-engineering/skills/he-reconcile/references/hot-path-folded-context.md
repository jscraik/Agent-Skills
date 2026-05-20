# Hot-Path Folded Context

## Purpose
Preserve detailed context folded out of SKILL.md so the active he-reconcile entrypoint stays below the hot-path soft budget without losing usable guidance.

## 2026-05-15 Soft-Warning Cleanup

Disposition:
- moved-to-reference: bulky examples, extended output fields, repeated evidence detail, and long procedure tails.
- superseded: repeated headings whose active entrypoint now points to shared contracts.
- intentionally-discarded: none in this file; prompt rot is tracked in shared folded context when removed.

## Folded Procedure

1. Reconstruct lifecycle state from live repo, tracker, PR, validation, session,
   and `.harness` evidence.
2. When session evidence is in scope, read session-collector public provenance
   first and report Codex provenance as found, not_found, blocked, or
   not_applicable before raw transcript or rollout fallback.
3. Resolve only enough context to identify the earliest incomplete, stale, or
   conflicted stage.
4. If an original prompt, external workflow, manual method, or plugin comparison
   is the baseline, apply source-prompt coverage before routing. Preserve source
   status, evidence depth, gaps, not-inspected evidence classes, repo drift
   signals, confidence, and route.
5. Start with 2-3 focused surfaces before loading broader repo/session evidence.
6. Ask before choosing when earliest stage, resume target, refresh route, or
   source-prompt coverage conflicts. In headless mode, record assumptions and
   block irreversible routing.
7. Report Project Brain freshness when repo context changed; do not write
   Project Brain from reconcile mode.
8. Use UI plan routing only when UI-plan artifacts are present, then hand off to
   `he-plan`, `he-work`, or `he-code-review`.
9. Route product-compression blockers such as
   `active_stage: spec_refresh_required` to `he-spec` instead of approving
   another additive implementation pass.
10. Treat plugin-hook output as runtime evidence only; it cannot replace missing
   specs, plans, evals, or traceability.
11. For repeated review/validation failures, reconstruct the pattern in
    `repeated_failure_state` and route repair tracking to `he-linear-plan`,
    live Linear, or `he-reinforce`.
12. Apply the BLUF review contract to non-trivial durable reconcile artifacts so
    the earliest incomplete stage, blocker, next action, and confidence impact
    are visible before evidence detail.
13. Apply the visual reference contract when repo, tracker, PR, validation,
    session, and `.harness` sources disagree; prefer source-of-truth comparison
    maps and route diagrams.

## Folded Validation

Fail fast. Check routing, stage artifacts, source-prompt coverage, tracker/PR
links, Project Brain freshness, validation evidence, and handoff authority.
Report gates as `pass`, `fail`, or `blocked`. Treat stale tracker, validation,
PR, or artifact evidence as degraded, not closure proof.
When session evidence is cited, check Codex provenance source, redaction status,
proof limits, and PR-safe trace fields; raw local identifiers or transcript/
rollout paths in public text are blockers.
For non-trivial generated reconcile artifacts, run or block
`python3 Plugins/harness-engineering/scripts/check_bluf_structure.py
<reconcile-artifact-path> --json`.

## Folded Safety Boundaries

`he-reconcile` reconstructs state and routes the next stage. Do not collapse
multi-stage work into execution, write user/global config, update external
systems, refresh Project Brain, create learnings, or perform destructive
actions without explicit authority. A route or `safe_to_continue` status cannot
authorize implementation, tracker mutation, sync/install, destructive cleanup,
or closure by itself. Redact secrets and private transcripts.

## Folded Confidence Reporting

Tie confidence to source freshness, artifact traceability, tracker/PR validity,
validation evidence, source-prompt coverage depth, and unresolved assumptions.
Do not claim runtime availability, Project Brain freshness, Linear state,
release readiness, or closure safety without direct evidence.

## Folded Examples

- User says: "Inspect this repo and reconcile JSC-246 from
  `.harness/linear/JSC-246-plan.md`, PR #153, latest validation output, and
  Linear state before deciding whether to resume at `he-spec`, `he-work`, or
  `he-eval-report`."
- User says: "Inspect why the same CodeRabbit feedback failed across PR #153
  and #154; use `artifacts/reviews/he-code-review.md`, validation output, and
  tracker state to route repair tracking without writing a solved-problem
  learning yet."

## Folded References

Read `references/contract.yaml` for the full reconcile contract and
`references/evals.yaml` for validation scenarios. Use shared HE references only
when active: stage context, coding-harness bridge, source-prompt coverage,
plugin-hook capability, UI plan routing, artifact routing, agent-native
compression, pragmatic invariants, and XP operating contract. Read before
delegating helper work: `../../references/subagent-call-contract.md`.
Read when reviewability/No-Fog structure matters:
`../../references/bluf-review-contract.md`.
Read when source-of-truth conflicts or route decisions need diagrams:
`../../references/visual-reference-contract.md`.
Read when session collector, Codex provenance, trace IDs, or PR safety traces
matter: `../../references/codex-provenance-contract.md` and
`../../references/pr-safety-trace-contract.md`.
Read when local proof and live tracker mutation state might be conflated:
`../../references/closure-mutation-contract.md`.

Deferred context index: `../../references/deferred-context-index.md`.
