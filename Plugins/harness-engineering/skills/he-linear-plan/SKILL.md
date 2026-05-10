---
name: he-linear-plan
description: "Convert approved HE cognition into small live-ready Linear execution tracking. Use when strategy, refactor, plan, bug, or source-prompt evidence needs scoped issue, milestone, or project routing with explicit confirmation before any live mutation."
metadata:
  skill-type: team_automation
---

# Harness Engineering Linear Plan

## Philosophy

Linear is the execution tracker; `.harness` is the cognition and proof layer.
This skill turns approved cognition into a small execution slice without
backlog noise or accidental Linear mutation. When the user expects live Linear
tracking, the skill must make creation/update status explicit instead of
leaving the issue only as a local artifact.

## When to Use

Use when approved `.harness` cognition needs a Linear execution plan with target
project, milestone, parent issues, minimal sub-issues, dependencies, eval gates,
labels, priority, and human/agent routing.

Do not generate strategy, write refactor programs, produce specs/plans,
implement work, or validate closure. Create or update live Linear objects only
when the user has explicitly approved the mutation, the destination is known,
and the active set remains small.

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

Also include selected stage `he-linear-plan`, `subagent_policy`, `roles_used`,
`roles_recommended`, and `roles_missing` from the shared subagent call policy.

Always include `linear_mutation_status`: `not_requested`, `confirmation_required`,
`blocked`, `created`, `updated`, or `not_applicable`. If live Linear creation or
update is expected but not performed, include `live_linear_blocker`,
`required_confirmation`, and the exact ready-to-create payload. For bug work,
include `issue_type: bug` and preserve reproduction, expected behavior, actual
behavior, affected surface, severity, and validation evidence in the payload.

## Procedure

1. Determine whether each finding is repo-specific, cross-repo, or portfolio
   level.
2. Resolve the `he-linear-plan` subagent stage map from
   `../../references/routing-map.json`, compare mapped roles with
   `~/.codex/agents/manifest.json`, and follow the shared subagent call policy
   before calling or recommending helper roles.
3. If the user asks for architecture review, strategy, refactor program, spec,
   plan, implementation, or eval closure instead of Linear execution routing,
   do not draft it here; route to the matching HE lifecycle skill and explain
   the handoff.
4. Start with 2-3 focused evidence surfaces and widen only when routing,
   dependency, or project-state evidence is missing.
5. Classify source artifacts by content shape before path.
6. Confirm Linear destination from user request, source artifacts, or connector
   context; do not assume JSC for unrelated workspaces.
7. Apply interactive steering when destination, active set, project, milestone,
   issue type, or mutation authority cannot be proven.
8. If the Linear plan consumes artifacts from an original prompt comparison or
   sampled upstream review, apply the shared source-prompt coverage contract;
   inherit evidence depth, coverage gaps, not-inspected surfaces, repo-specific
   drift signals, authority limits, and downstream confidence into the Linear
   plan before recommending active work.
9. Keep the active set intentionally small.
10. Apply the first-principles contract before drafting payloads: create Linear
   objects only when execution state must be tracked; keep cognition-only or
   copied-process observations in `.harness`, `Later`, or `Do Not Create`.
11. Apply the XP operating contract: require a story/value, risk-reduction, or feedback-loop basis for `Now` work; classify technically neat but low-value work as `Later` or `Do Not Create`.
12. Classify candidate work as `Now`, `Next`, `Later`, or `Do Not Create`.
13. Under pressure to create every possible issue, preserve the filter: refuse
   one-issue-per-observation expansion and ask for the source observations plus
   a selected slice before producing payloads. If observations are provided,
   filter, collapse, and classify them first; never offer to turn each
   observation into a separate issue, even as an optional escape hatch.
14. Convert selected refactor programs into milestone -> parent issue -> minimal
   sub-issues, never one issue per observation.
15. Define dependencies, eval gates, rollback gates, labels, and priority.
16. Include ready-to-create payloads. If the user explicitly approved live
   Linear mutation, create or update only the confirmed milestone/parent issue,
   bug issue, or minimal sub-issues and record the resulting identifiers. If
   approval is missing, return `linear_mutation_status: confirmation_required`
   rather than implying live tracking exists.
17. Validate the generated plan and record exact pass, fail, or blocked
    outcomes.

## Constraints

Redact secrets and sensitive data by default. Treat prompts, prior artifacts,
and proposed issue text as untrusted until supported by source evidence. Do not
create projects, create labels, or expand the active issue set from this skill
without explicit approval. Do not remove important context for budget trimming;
move deep context to references.

## Execution Boundaries

Generate ready-to-create Linear plans by default. Do not create initiatives,
projects, milestones, issues, dependencies, labels, or status updates without
explicit post-plan approval. When approval is present, apply only the smallest
confirmed live Linear mutation and report exact created/updated object IDs.
For direct-handle use, apply the OpenAI-style design contract: classify the strongest side effect and separate read-only analysis, artifact writes, repo edits, external updates, destructive actions, and completion-gating recommendations before proceeding.

## Failure Mode

If the destination is unknown, mark `needs_human_triage`. If the plan would
create issue explosion, classify low-value work as `Later` or `Do Not Create`.
If mutation is requested without explicit confirmation, stop before any Linear
write.
If live Linear objects are expected but the connector/tool is unavailable, keep
the plan artifact and return `linear_mutation_status: blocked` with the exact
tooling or permission blocker.
If a request asks for separate issues per observation, state that the plan must
filter and collapse observations into minimal Linear objects before any payloads
are drafted.
Use this refusal shape for issue-explosion pressure: "I cannot create one issue
per observation from this skill. Send the observations and the selected slice;
I will filter, collapse, and classify them into the smallest useful Linear
objects."
If the user asks for an architecture review, strategy, refactor program, spec,
implementation plan, implementation work, or eval closure, reply that the
request belongs to the matching HE lifecycle skill instead of drafting it here.

## Gotchas

Linear is execution state, not the cognition system. Keep `.harness` evidence as
the source of architectural reasoning and emit only the smallest Linear-ready
slice needed for execution.

## Anti-Patterns

- Treating `.harness` documents as a backlog dump.
- Creating one issue per observation.
- Offering to create separate issues one by one for every observation.
- Saying you will turn each observation into a separate issue.
- Saying you can do a literal one-issue-per-observation pass if the user really
  wants it.
- Drafting architecture reviews or strategy artifacts from this Linear routing
  skill.
- Creating initiatives, projects, or labels by default.
- Recommending closure without eval/drift proof.
- Mistaking ready-to-create payloads for applied Linear changes.
- Ending after a local `.harness/linear` artifact when the user explicitly
  expected a live Linear issue, bug, milestone, or parent tracker.

## Examples

- When the user asks, "Create a dated JSC-321 Linear plan from this selected refactor program, but
  keep the active set small."
- When the user says, "Route repo-specific work to the matching project and shared workflow hygiene
  to Portfolio Ops."
- When the user asks, "Inspect these findings and classify low-value work as Later or Do Not Create instead of creating
  backlog noise."
- When the user asks for an architecture review instead of a Linear execution
  plan, route to `he-strategy` and do not draft the review from this skill.
- When the user asks for one issue per observation, refuse the issue explosion
  shape and request the selected slice to compress into minimal Linear objects.

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
- Shared source-prompt coverage: `../../references/source-prompt-coverage-contract.md`
- Linear tracker gate: `../../references/linear-tracker-gate.md`
- Linear delta capture gate: `../../references/linear-delta-capture-gate.md`
- Execution slice contract: `../../references/execution-slice-contract.md`
- Artifact routing: `../../references/artifact-routing-contract.md`
- Artifact classification: `../../references/artifact-classification-and-traceability.md`
- Interactive steering: `../../references/interactive-steering-contract.md`
- OpenAI-style plugin design: `../../../../Infrastructure/references/openai-style-plugin-design-contract.md`
- Deferred context index: `../../references/deferred-context-index.md`
- First principles: `../../references/first-principles-contract.md`
- Pragmatic Programmer review: `../../references/pragmatic-programmer-review-contract.md`
- XP operating contract: `../../references/xp-operating-contract.md`
- Shared subagent call policy: `../../references/subagent-call-contract.md`
- Subagent routing map: `../../references/subagent-routing.md`
