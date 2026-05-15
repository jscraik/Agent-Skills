---
name: he-reconcile
description: "Analyze repo, tracker, PR, validation, session, and .harness evidence. Use when multi-stage Harness Engineering work needs safe resume routing."
metadata:
  version: 1.0.0
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
retained references, coverage, repeated-failure state, validation, Codex
provenance, PR safety trace status, and handoff.

## Preconditions
Resolve canonical repo/source and cited evidence before treating it as fact.
Classify side effects before acting. Learning capture is out of scope and must
hand off to `he-reinforce`.
Start with 2-3 focused surfaces before widening.

## Procedure
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
- See references/hot-path-folded-context.md for folded procedure detail.

## Validation
Fail fast. Check routing, stage artifacts, source-prompt coverage, tracker/PR
links, Project Brain freshness, validation evidence, and handoff authority.
Report gates as `pass`, `fail`, or `blocked`. Treat stale tracker, validation,
PR, or artifact evidence as degraded, not closure proof.
When session evidence is cited, check Codex provenance source, redaction status,
proof limits, and PR-safe trace fields; raw local identifiers or transcript/
rollout paths in public text are blockers.
- See references/hot-path-folded-context.md for folded validation detail.

## Safety Boundaries
`he-reconcile` reconstructs state and routes the next stage. Do not collapse
multi-stage work into execution, write user/global config, update external
systems, refresh Project Brain, create learnings, or perform destructive
actions without explicit authority. A route or `safe_to_continue` status cannot
authorize implementation, tracker mutation, sync/install, destructive cleanup,
- See references/hot-path-folded-context.md for folded safety boundaries detail.
Redact secrets, credentials, API keys, tokens, PII, and sensitive local data by
default.

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
`codex_provenance`, `pr_safety_trace`, `handoff`, and `blocked_reason`.

## Examples
- When the user asks to inspect `.harness/session-evidence/latest.md` and it
  conflicts with `.harness/plan/JSC-246-plan.md`, route to the earliest
  incomplete stage and mark stale plan evidence as degraded.
- When the user asks to validate closure from implementation status alone, route
  to `he-eval-report` instead of declaring completion.

## Gotchas
- State reconstruction and routing only; not implementation.
- `he-reinforce` owns new or refreshed `.harness/solutions/**` and Project Brain
  learning synchronization.
- Repeated failures may need both Linear tracking and durable learning capture.
- Apply the context-disposition policy: move important still-valid context to references, and intentionally discard stale, duplicated, unsafe, superseded, or low-signal text.

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
- See references/hot-path-folded-context.md for folded references detail.
- ../../references/deferred-context-index.md for folded/discarded context.
- ../../references/closure-mutation-contract.md for closure proof vs live mutation boundaries.
- Apply the context-disposition policy: move important still-valid context to references, and intentionally discard stale, duplicated, unsafe, superseded, or low-signal text.
