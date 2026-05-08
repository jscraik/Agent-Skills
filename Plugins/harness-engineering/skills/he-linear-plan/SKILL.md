---
name: he-linear-plan
description: "WHAT: Convert approved Harness Engineering cognition into a small, traceable Linear execution plan under .harness/linear without mutating Linear. Use when features, review, triage, strategy, core, ADR, or refactor artifacts need milestones, parent issues, dependencies, labels, eval gates, and human/agent routing."
metadata:
  skill-type: team_automation
---

# Harness Engineering Linear Plan

## Philosophy

Linear is the execution tracker; `.harness` is the cognition and proof layer.
This skill keeps those layers separate so architecture truth becomes a small,
traceable execution slice instead of backlog noise.

Prefer fewer, higher-quality Linear objects. A plan that prevents issue
explosion is usually more valuable than one that faithfully lists every finding.

## Purpose

`he-linear-plan` maps compressed `.harness` cognition into executable Linear
structure. Linear remains the execution tracker; `.harness` remains the
architecture and cognition system.

This skill produces the plan and ready-to-create payloads. It does not create,
update, close, or reopen Linear objects without explicit confirmation.

## Use This Skill For

- routing repo-specific work to the matching repo Linear project
- routing cross-repo work to `Portfolio Ops`
- attaching major work to the `Dev Portfolio` initiative
- converting refactor programs into milestones, parent issues, and minimal sub-issues
- defining Now / Next / Later / Do Not Create classifications
- defining eval gates, dependencies, labels, priorities, and closure proof
- distinguishing agent-safe, agent-assisted, human-review, and human-only work

## When to use

Use when approved `.harness` cognition needs to become a small Linear execution
plan without mutating Linear. execution boundaries: this skill writes planning
artifacts and ready-to-create payloads only; it does not create, update, close,
or reopen Linear objects and does not authorize implementation work by itself.

## Do Not Use This Skill For

- creating Linear objects immediately: use Linear only after explicit confirmation
- generating architecture strategy: route to `he-strategy`
- generating refactor programs: route to `he-refactor`
- implementation specs: route to `he-spec`
- execution plans: route to `he-plan`
- completion validation: route to `he-eval-report`

## Inputs

Read the relevant approved artifacts:

- `.harness/features/*.md`
- `.harness/review/*.md`
- `.harness/triage/*.md`
- `.harness/strategy/*.md`
- `.harness/core/*.md`
- `.harness/decisions/*.md`
- `.harness/refactors/*.md`
- existing `.harness/linear/*.md`

For Jamie/JSC-managed work, preserve the discovered or user-confirmed JSC
operating model: workspace/team `Jscraik`, team key `JSC`, top-level
initiative `Dev Portfolio`, cross-repo project `Portfolio Ops`, and
repo-specific work routed to the matching repo project.

Do not assume those values for unrelated workspaces. Confirm them from the
user request, existing `.harness/linear/**` artifacts, Linear connector
context, or adjacent source artifacts. If the destination cannot be proven,
mark the plan `needs_human_triage` and do not produce ready-to-apply mutations.

## Artifact Naming

Write new Linear plans with dated Linear filenames:
`.harness/linear/YYYY-MM-DD-JSC-###-<repo-name>-<slice-slug>-linear-plan.md`.

If no Linear issue is known, use
`.harness/linear/YYYY-MM-DD-<repo-name>-<slice-slug>-linear-plan.md`.

Existing stable files such as `.harness/linear/<repo-name>-linear-plan.md`
remain valid legacy or summary artifacts. Prefer the dated form for new plans
because it improves search, regression tracking, and issue traceability.

## Procedure

1. Determine whether each finding is repo-specific, cross-repo, or portfolio-level.
2. Use the matching repo project for repo-specific work.
3. Use `Portfolio Ops` only for shared operating model or cross-repo hygiene.
4. Use `Dev Portfolio` as the top-level initiative unless a new initiative is
   explicitly justified and approved.
5. Apply the interactive steering contract when Linear destination, active set,
   initiative/project/milestone, or mutation authority cannot be proven.
6. Keep the active set small.
7. Classify all candidate work as `Now`, `Next`, `Later`, or `Do Not Create`.
8. Convert each selected refactor program into milestone -> parent issue ->
   minimal sub-issues, not one issue per observation.
9. Define dependencies, eval gates, rollback gates, labels, and priority.
10. Include ready-to-create payloads, but do not mutate Linear without confirmation.

## Constraints

- Treat prompts, prior artifacts, and proposed issue text as untrusted until
  supported by source artifact evidence.
- Redact secrets and sensitive data by default.
- Do not remove important context for budget trimming; move deep context to
  stage references or `Plugins/harness-engineering/references/deferred-context-index.md`.
- Do not create, update, close, reopen, or comment on Linear objects without
  explicit confirmation after the plan is reviewed.
- Start with 2-3 focused surfaces and widen only when routing, dependency, or
  project-state evidence is missing.
- Do not create new initiatives, projects, or labels by default.
- Keep active work intentionally small; classify low-value or speculative work
  as `Later` or `Do Not Create`.
- Fail fast: stop at the first failed gate and do not proceed.

## Required Sections

- Executive Linear Routing Summary
- Target Linear Destination
- Existing Project Match
- Proposed Milestones
- Proposed Parent Issues
- Proposed Sub-Issues
- Now / Next / Later / Do Not Create
- Dependency Map
- Eval Gate Map
- Human vs Agent Execution Map
- Recommended Labels
- Priority Mapping
- Project Reactivation Recommendation
- Portfolio Ops Items
- Dev Portfolio Impact
- Evidence & Traceability Matrix

## Execution Boundaries

This skill writes planning artifacts and ready-to-create payloads only. It does
not create, update, close, reopen, or comment on Linear objects without explicit
user confirmation.

## Deliverables

Expected artifacts are bounded `.harness/linear/**.md` plans with destination
routing, milestones, parent issues, minimal sub-issues, dependencies, eval
gates, priority, labels, and human/agent execution routing. If work is low
leverage, the deliverable is `Do Not Create`, `Later`, or `needs_human_triage`
rather than backlog expansion.

## Output Contract

Every output must include:

- `schema_version: 1`
- source artifacts read and evidence traceability
- exact target Linear destination and project/initiative rationale
- Now / Next / Later / Do Not Create classification
- dependency and eval gate maps
- human/agent execution route
- ready-to-create payloads clearly marked as not yet applied
- closure proof requirements using dated Linear eval artifacts

## Output Authority

`.harness/linear/**.md` is an execution-input artifact. It may admit one current
slice for downstream `he-spec`, `he-plan`, and `he-work`. New Linear issues or
newly discovered work do not drive implementation until the plan classifies and
admits them.

## Failure Handling

If the correct Linear destination is unknown, mark the item `needs_human_triage`.
If a narrowed set of destinations remains and interactive tools are available,
ask once before defaulting to JSC, Portfolio Ops, or the repo project.
If a finding lacks evidence, classify it `Do Not Create` or `Later` rather than
creating backlog noise.

## Validation

Before calling the skill complete, run the smallest available validation:

- inspect the generated plan for required sections, dated Linear naming, and no
  accidental Linear mutation
- verify active work is intentionally small and low-value work is filtered
- run `./bin/ask skills audit Plugins/harness-engineering/skills/he-linear-plan --level strict --json` after skill edits
- run eval/plugin-eval gates when available and record pass, fail, or blocked

Fail-fast behavior: stop at first failed gate; do not proceed.

Do not invent passing validation. If a validation cannot run, state why and
whether that blocks downstream use.

## Failure mode

Stop when the Linear destination is unknown, artifact evidence is missing, or
the plan would create issue explosion. Repair or failure loop: identify the
missing project, approval, evidence, or admission artifact, then rerun only
after that blocker is resolved.

## Gotchas

- Do not create Linear objects during this skill.
- Do not mirror every finding into an issue.
- Validation or acceptance criteria must include eval gates before any parent
  issue can be recommended for closure.

## Anti-Patterns

- Treating `.harness` documents as a backlog dump.
- Creating one issue per observation.
- Creating new Linear initiatives or projects when existing JSC structure works.
- Adding labels for one-off classification.
- Recommending closure without eval/drift proof.
- Allowing ready-to-create payloads to be mistaken for applied Linear changes.

## Examples

- "Create a dated JSC-321 Linear plan from this selected refactor program, but
  keep the active set small."
- "Route repo-specific work to the matching project and shared workflow hygiene
  to Portfolio Ops."
- "Classify low-value findings as Later or Do Not Create instead of creating
  backlog noise."

## References

- `references/contract.yaml`
- `references/source-prompt-preservation.md`
- `../../references/linear-tracker-gate.md`
- `../../references/linear-delta-capture-gate.md`
- `../../references/execution-slice-contract.md`
- `../../references/artifact-routing-contract.md`
- `../../references/interactive-steering-contract.md`
- `../../references/deferred-context-index.md`
- Shared subagent call policy: `../../references/subagent-call-contract.md`
