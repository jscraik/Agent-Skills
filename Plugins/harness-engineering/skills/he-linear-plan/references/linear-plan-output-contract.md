# Linear Plan Output Contract

Use this reference after `he-linear-plan` is selected. The plan converts
approved `.harness` cognition into a small execution slice without mutating
Linear.

## Naming

- With Linear context:
  `.harness/linear/YYYY-MM-DD-JSC-###-<repo-name>-<slice-slug>-linear-plan.md`
- Without Linear context:
  `.harness/linear/YYYY-MM-DD-<repo-name>-<slice-slug>-linear-plan.md`
- Legacy summary files such as `.harness/linear/<repo-name>-linear-plan.md`
  remain readable, but dated Linear style is preferred for new plans.

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
- Story / Value Basis
- Recommended Labels
- Priority Mapping
- Project Reactivation Recommendation
- Portfolio Ops Items
- Dev Portfolio Impact
- Evidence & Traceability Matrix

## Required Fields

- `schema_version: 1`
- `selected_stage: he-linear-plan`
- `subagent_policy`
- `roles_used`
- `roles_recommended`
- `roles_missing`
- `linear_mutation_status`: one of `not_requested`,
  `confirmation_required`, `blocked`, `created`, `updated`, or
  `not_applicable`
- `live_linear_blocker` when live tracking is expected but not completed
- `required_confirmation` when mutation approval is missing
- ready-to-create payloads when a live object is expected but unapplied

Bug payloads must include `issue_type: bug`, reproduction, expected behavior,
actual behavior, affected surface, severity, and validation evidence.

## Issue Shape

Use this template for proposed issues. Do not create them during the plan.

```text
## Objective
## Source Artifacts
## Why This Matters
## Scope
## Out of Scope
## Execution Notes
## Validation Gates
## Rollback Conditions
## Linear Routing
```

## Routing Rules

- Repo-specific work routes to the matching repo project.
- Cross-repo workflow, reporting, shared governance, labels, or portfolio
  hygiene routes to `Portfolio Ops`.
- Portfolio-level operating model work may attach to `Dev Portfolio`.
- Do not create new initiatives, projects, labels, issues, comments, or status
  changes without explicit user confirmation after plan review.
- If destination cannot be proven, mark `needs_human_triage` and ask once when
  interactive steering is available.
- User pressure to create one issue per observation must preserve the filter:
  request the source observations and selected slice, then collapse work into
  the smallest useful milestone, parent issue, or `Do Not Create` classification.
- If artifacts came from an original prompt comparison or sampled upstream
  review, inherit evidence depth, coverage gaps, not-inspected surfaces,
  repo-specific drift signals, authority limits, and downstream confidence into
  the Linear plan before recommending active work.

## Priority Rules

- `1` Urgent: active execution blocker or serious safety/regression issue.
- `2` High: moat-critical, migration blocker, architecture risk, eval or
  reliability gap.
- `3` Normal: useful work with clear value but no immediate blocker.
- `4` Low: cleanup or non-blocking documentation support.
- `0` No priority: backlog placeholder only.

## XP Value Filter

Every proposed `Now` item must state its story or value basis, expected feedback
signal, and risk-reduction reason. Work that is technically tidy but cannot
name a user/operator value, feedback loop, or risk reduction must be classified
as `Later` or `Do Not Create`.

## Side-Effect Classes

Before any action, classify the strongest side effect:

- read-only analysis
- artifact write
- repo edit
- external Linear update
- destructive action
- completion-gating recommendation

Only external Linear updates are owned by this skill, and only after explicit
post-plan approval with known destination and a small confirmed object set.
