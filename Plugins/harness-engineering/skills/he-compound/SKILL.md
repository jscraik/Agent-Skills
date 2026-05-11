---
name: he-compound
description: "Analyze session, repo, Linear, and harness evidence to refresh HE lifecycle state. Use when multi-stage HE work needs source-prompt coverage, resume routing, or earliest-stage recovery."
metadata:
  skill-type: team_automation
---
# Harness Engineering Compound

## Philosophy

Coordinate state, not ceremony. Compound identifies the earliest incomplete HE
stage and preserves the evidence chain that lets the next agent act immediately.
Local `AGENTS.md`, rules, hooks, command boundaries, and approval gates outrank
this skill.

## When to Use

Use when work spans brainstorm, spec, plan, work, review, Linear, PRs, Project
Brain, or `.harness` memory and needs refresh, resume control, source-prompt
coverage, repeated-failure reconstruction, or solved-problem capture.

## When Not to Use

Do not use for a single selected implementation slice, plain code fix, isolated
docs edit, or unverified learning capture. Route direct execution to the active
stage skill or implementation workflow.

## Inputs

Goal, repo path, Linear/Project Brain state, specs, plans, PRs, validation,
session evidence, source-prompt baseline, repeated-failure evidence, or
solved-problem proof.

## Outputs

Return mode, stage map, earliest stage, owner, blockers, next action,
references, source-prompt coverage, repeated-failure state, blackboard delta,
solution-capture status, Project Brain status, validation, and handoff.

## Preconditions

Resolve the canonical repo and cited evidence before treating it as fact.
Classify side effects before acting: read-only, `.harness` artifact write,
repo-write, user-config-write, external-write, or destructive. Learning capture
requires solved and verified evidence.

## Procedure

1. Reconstruct lifecycle state from live repo evidence, Linear, specs, plans,
   PRs, validation, session evidence, and Project Brain.
2. Resolve only enough stage context to identify the earliest incomplete, stale,
   or conflicted stage.
3. If an original prompt, external workflow, manual method, or plugin comparison
   is the baseline, apply source-prompt coverage before routing. Preserve source
   status, evidence depth, gaps, not-inspected evidence classes, repo drift
   signals, confidence, route.
4. Keep scope tight: start with 2-3 focused surfaces that prove lifecycle state
   before loading broader repo or session evidence.
5. Ask before choosing when earliest stage, resume target, refresh route, or
   source-prompt coverage conflicts. In headless mode, record assumptions and
   block irreversible routing.
6. Preserve HE lifecycle state in coding-harness-managed repos and refresh or
   explicitly block Project Brain only when repository context changed.
7. Use solution capture only for solved-problem evidence; write new captures
   under `.harness/solutions/**`, not legacy `docs/solutions/**`.
8. Use UI plan routing only when UI-plan artifacts are present, then hand off to
   `he-plan`, `he-work`, or `he-code-review`.
9. Route product-compression blockers such as
   `active_stage: spec_refresh_required` to `he-spec` instead of approving
   another additive implementation pass.
10. Treat plugin-hook output as runtime evidence only. It can inform `.harness`
    artifacts but cannot replace missing specs, plans, evals, or traceability.
11. When `he-code-review` reports `repeated_failure_route`,
    `repeated_failure`, or context-feedback recurrence, reconstruct the pattern
    from review, validation, session, Linear, and `.harness` evidence. Preserve
    it in `repeated_failure_state`, decide whether `.harness/solutions/**`
    capture is warranted, and route repair tracking to `he-linear-plan` or live
    Linear when missing.

## Validation

Fail fast. Check routing, stage artifacts, source-prompt coverage, Linear/PR
links, Project Brain status, solution-capture eligibility, validation evidence,
and handoff authority. Report each gate as `pass`, `fail`, or `blocked`.

## Safety Boundaries

Compound reconstructs lifecycle state and routes the next stage. Do not collapse
multi-stage work into execution, refresh Project Brain without source evidence,
write user/global config, update external systems, or perform destructive
actions without explicit authority. Redact secrets and private transcripts.

## Failure Handling

If required evidence, Linear linkage, source-prompt baseline, route, destination,
or authority is missing, stop with `blocked_reason` and the smallest recovery
step. Chat summaries cannot replace source, tracker, artifact, PR, validation,
or trace evidence.

## Handoff Rules

Route brainstorm gaps to `he-brainstorm`, acceptance/behavior gaps to `he-spec`,
execution strategy gaps to `he-plan`, implementation to `he-work`, review to
`he-code-review`, repeated repair tracking to `he-linear-plan` or live Linear,
and completed solved-problem capture to `.harness/solutions/**`.

## Output Format

Structured output: `schema_version`, `mode`, `stage_map`,
`earliest_incomplete_stage`, `active_owner`, `blockers`, `next_action`,
`source_prompt_coverage`, `repeated_failure_state`, `blackboard_delta`,
`retained_references`, `solution_capture_status`, `project_brain_status`,
`validation`, `handoff`, and `blocked_reason`.

## Confidence Reporting

Tie confidence to source freshness, artifact traceability, tracker/PR validity,
validation evidence, source-prompt coverage depth, and unresolved assumptions.
Do not claim runtime availability, Project Brain freshness, Linear state,
solution capture, or release readiness without direct evidence.

## Gotchas

- State reconstruction and routing only; not implementation.
- New captures go under `.harness/solutions/**`; legacy docs are evidence.
- Repeated failures may need both Linear tracking and lifecycle memory.
- Do not remove important context for budget trimming; move deep context to
  references with a clear route.

## Examples

- "Inspect and resume the coding-harness run for JSC-246; map Linear, spec,
  plan, PR, Project Brain, north-star evidence, and tell me the exact next HE
  stage."
- "Inspect the HE compound state after PR 154 merged, update Project Brain if
  `.harness` changed, and capture any solved-problem doc now warranted."

## Assets

Reference `assets/` only for skill packaging and browseability; lifecycle state
belongs in structured handoff evidence.

## References

Read `references/contract.yaml` for the full mode contract, `references/evals.yaml`
for validation scenarios, and `assets/resolution-template.md` only when writing
solution captures. Use shared HE references only when active: stage context,
coding-harness bridge, solution capture, source-prompt coverage, plugin-hook
capability, UI plan routing, artifact routing, agent-native compression,
pragmatic invariants, and XP operating contract.
Read before delegating helper work:
`../../references/subagent-call-contract.md`.

Deferred context index: `../../references/deferred-context-index.md`.
