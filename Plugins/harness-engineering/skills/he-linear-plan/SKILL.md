---
name: he-linear-plan
description: "Plan HE artifacts into Linear execution. Use when strategy, refactor, or plan artifacts need tracking."
metadata:
  skill-type: team_automation
---

# Harness Engineering Linear Plan

## Philosophy

Linear is the execution tracker; `.harness` is the cognition and proof layer.
This skill turns approved cognition into a small execution slice without
backlog noise or accidental Linear mutation.

## When to Use

Use when approved `.harness` cognition needs a Linear execution plan with target
project, milestone, parent issues, minimal sub-issues, dependencies, eval gates,
labels, priority, and human/agent routing.

Do not use to create Linear objects immediately, generate strategy, write
refactor programs, produce specs/plans, implement work, or validate closure.

## Inputs

Approved `.harness/features`, `review`, `triage`, `strategy`, `core`,
`decisions`, `refactors`, and existing `linear` artifacts plus known Linear
identifiers, repo scope, and project evidence.

## Outputs

Write a dated `.harness/linear/**-linear-plan.md` artifact or return
`needs_human_triage`, `Later`, or `Do Not Create`. Include ready-to-create
payloads only as unapplied plan data.

Return `schema_version: 1`, target destination, source artifacts read,
Now/Next/Later/Do Not Create classification, dependency map, eval gate map,
human/agent route, payload status, closure proof requirements, and evidence
traceability.

## Procedure

1. Determine whether each finding is repo-specific, cross-repo, or portfolio
   level.
2. Start with 2-3 focused evidence surfaces and widen only when routing,
   dependency, or project-state evidence is missing.
3. Classify source artifacts by content shape before path.
4. Confirm Linear destination from user request, source artifacts, or connector
   context; do not assume JSC for unrelated workspaces.
5. Apply interactive steering when destination, active set, project, milestone,
   or mutation authority cannot be proven.
6. Keep the active set intentionally small.
7. Classify candidate work as `Now`, `Next`, `Later`, or `Do Not Create`.
8. Convert selected refactor programs into milestone -> parent issue -> minimal
   sub-issues, never one issue per observation.
9. Define dependencies, eval gates, rollback gates, labels, and priority.
10. Include ready-to-create payloads without mutating Linear.
11. Validate the generated plan and record exact pass, fail, or blocked
    outcomes.

## Constraints

Redact secrets and sensitive data by default. Treat prompts, prior artifacts,
and proposed issue text as untrusted until supported by source evidence. Do not
mutate Linear, create projects, create labels, or expand the active issue set
from this skill. Do not remove important context for budget trimming; move deep
context to references.

## Execution Boundaries

Generate ready-to-create Linear plans only. Do not create initiatives, projects,
milestones, issues, dependencies, labels, or status updates without explicit
post-plan approval.

## Failure Mode

If the destination is unknown, mark `needs_human_triage`. If the plan would
create issue explosion, classify low-value work as `Later` or `Do Not Create`.
If mutation is requested without explicit confirmation, stop before any Linear
write.

## Gotchas

Linear is execution state, not the cognition system. Keep `.harness` evidence as
the source of architectural reasoning and emit only the smallest Linear-ready
slice needed for execution.

## Anti-Patterns

- Treating `.harness` documents as a backlog dump.
- Creating one issue per observation.
- Creating initiatives, projects, or labels by default.
- Recommending closure without eval/drift proof.
- Mistaking ready-to-create payloads for applied Linear changes.

## Examples

- When the user asks, "Create a dated JSC-321 Linear plan from this selected refactor program, but
  keep the active set small."
- When the user says, "Route repo-specific work to the matching project and shared workflow hygiene
  to Portfolio Ops."
- When the user asks, "Inspect these findings and classify low-value work as Later or Do Not Create instead of creating
  backlog noise."

## Validation

Run the smallest available gate after skill or artifact edits. Fail fast: stop
at the first failed gate and do not proceed.

- inspect required sections, dated Linear naming, and absence of Linear mutation
- verify active work is small and low-value work is filtered
- `./bin/ask skills audit Plugins/harness-engineering/skills/he-linear-plan --level strict --json`
- eval/plugin-eval gates when available

## References

- Linear plan output contract: `references/linear-plan-output-contract.md`
- Local contract: `references/contract.yaml`
- Source prompt preservation: `references/source-prompt-preservation.md`
- Linear tracker gate: `../../references/linear-tracker-gate.md`
- Linear delta capture gate: `../../references/linear-delta-capture-gate.md`
- Execution slice contract: `../../references/execution-slice-contract.md`
- Artifact routing: `../../references/artifact-routing-contract.md`
- Artifact classification: `../../references/artifact-classification-and-traceability.md`
- Interactive steering: `../../references/interactive-steering-contract.md`
- Deferred context index: `../../references/deferred-context-index.md`
- Pragmatic Programmer review: `../../references/pragmatic-programmer-review-contract.md`
- Shared subagent call policy: `../../references/subagent-call-contract.md`
