---
name: he-reconcile
description: "Analyze repo, tracker, PR, validation, session, and .harness evidence. Use when multi-stage Harness Engineering work needs safe resume routing."
metadata:
  skill-type: team_automation
---
# Skill: Harness Engineering Reconcile

## Philosophy

Coordinate state, not ceremony. `he-reconcile` identifies the earliest
incomplete HE stage and preserves the evidence chain that lets the next agent
act immediately. Local `AGENTS.md`, rules, hooks, command boundaries, and
approval gates outrank this skill.

## When to Use

Use when HE work spans stages or evidence surfaces and needs refresh, resume
control, source-prompt coverage, repeated-failure reconstruction, or conflict
resolution.

## When Not to Use

Do not use for a single selected implementation slice, plain code fix, isolated
docs edit, or solved-problem capture. Route direct execution to the active
stage skill and durable learning refresh to `he-reinforce`.

## Inputs

Goal, repo path, tracker state, specs, plans, PRs, validation, session evidence,
source-prompt baseline, repeated-failure evidence, or artifact conflict.

## Outputs

Return mode, stage map, earliest incomplete stage, owner, blockers, next action,
retained references, coverage, repeated-failure state, validation, and handoff.

## Preconditions

Resolve canonical repo/source and cited evidence before treating it as fact.
Classify side effects before acting. Learning capture is out of scope and must
hand off to `he-reinforce`.

## Procedure

1. Reconstruct lifecycle state from live repo, tracker, PR, validation, session,
   and `.harness` evidence.
2. Resolve only enough context to identify the earliest incomplete, stale, or
   conflicted stage.
3. If an original prompt, external workflow, manual method, or plugin comparison
   is the baseline, apply source-prompt coverage before routing. Preserve source
   status, evidence depth, gaps, not-inspected evidence classes, repo drift
   signals, confidence, and route.
4. Start with 2-3 focused surfaces before loading broader repo/session evidence.
5. Ask before choosing when earliest stage, resume target, refresh route, or
   source-prompt coverage conflicts. In headless mode, record assumptions and
   block irreversible routing.
6. Report Project Brain freshness when repo context changed; do not write
   Project Brain from reconcile mode.
7. Use UI plan routing only when UI-plan artifacts are present, then hand off to
   `he-plan`, `he-work`, or `he-code-review`.
8. Route product-compression blockers such as
   `active_stage: spec_refresh_required` to `he-spec` instead of approving
   another additive implementation pass.
9. Treat plugin-hook output as runtime evidence only; it cannot replace missing
   specs, plans, evals, or traceability.
10. For repeated review/validation failures, reconstruct the pattern in
    `repeated_failure_state` and route repair tracking to `he-linear-plan`,
    live Linear, or `he-reinforce`.
11. Apply the BLUF review contract to non-trivial durable reconcile artifacts so
    the earliest incomplete stage, blocker, next action, and confidence impact
    are visible before evidence detail.
12. Apply the visual reference contract when repo, tracker, PR, validation,
    session, and `.harness` sources disagree; prefer source-of-truth comparison
    maps and route diagrams.

## Validation

Fail fast. Check routing, stage artifacts, source-prompt coverage, tracker/PR
links, Project Brain freshness, validation evidence, and handoff authority.
Report gates as `pass`, `fail`, or `blocked`. Treat stale tracker, validation,
PR, or artifact evidence as degraded, not closure proof.
For non-trivial generated reconcile artifacts, run or block
`python3 Plugins/harness-engineering/scripts/check_bluf_structure.py
<reconcile-artifact-path> --json`.

## Safety Boundaries

`he-reconcile` reconstructs state and routes the next stage. Do not collapse
multi-stage work into execution, write user/global config, update external
systems, refresh Project Brain, create learnings, or perform destructive
actions without explicit authority. A route or `safe_to_continue` status cannot
authorize implementation, tracker mutation, sync/install, destructive cleanup,
or closure by itself. Redact secrets and private transcripts.

## Failure Handling

If evidence, tracker linkage, source baseline, route, destination, or authority
is missing, stop with `blocked_reason` and the smallest recovery step. Chat
summaries cannot replace source, tracker, artifact, PR, validation, or trace
evidence. If local proof is strong but tracker state is stale/unavailable, route
to closure evidence recovery instead of declaring done.

## Handoff Rules

Route brainstorm gaps to `he-brainstorm`, acceptance gaps to `he-spec`,
strategy gaps to `he-plan`, implementation to `he-work`, review to
`he-code-review`, repeated repair tracking to `he-linear-plan`/Linear, closure
proof to `he-eval-report`, and solved-problem capture to `he-reinforce`.

## Output Format

Structured output: `schema_version`, `mode`, `stage_map`,
`earliest_incomplete_stage`, `active_owner`, `blockers`, `next_action`,
`source_prompt_coverage`, `repeated_failure_state`, `blackboard_delta`,
`retained_references`, `validation`, `git_staging_status`, `staged_paths`,
`handoff`, and `blocked_reason`.

## Confidence Reporting

Tie confidence to source freshness, artifact traceability, tracker/PR validity,
validation evidence, source-prompt coverage depth, and unresolved assumptions.
Do not claim runtime availability, Project Brain freshness, Linear state,
release readiness, or closure safety without direct evidence.

## Gotchas

- State reconstruction and routing only; not implementation.
- `he-reinforce` owns new or refreshed `.harness/solutions/**` and Project Brain
  learning synchronization.
- Repeated failures may need both Linear tracking and durable learning capture.
- Apply the context-disposition policy: move important still-valid context to references, and intentionally discard stale, duplicated, unsafe, superseded, or low-signal text.

## Examples

- User says: "Inspect this repo and reconcile JSC-246 from
  `.harness/linear/JSC-246-plan.md`, PR #153, latest validation output, and
  Linear state before deciding whether to resume at `he-spec`, `he-work`, or
  `he-eval-report`."
- User says: "Inspect why the same CodeRabbit feedback failed across PR #153
  and #154; use `artifacts/reviews/he-code-review.md`, validation output, and
  tracker state to route repair tracking without writing a solved-problem
  learning yet."

## References

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

Deferred context index: `../../references/deferred-context-index.md`.
