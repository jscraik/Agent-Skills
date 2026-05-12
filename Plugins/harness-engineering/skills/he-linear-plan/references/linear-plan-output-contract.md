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
- Repo / Location Label
- Priority Mapping
- Project / Cycle Justification
- Project Reactivation Recommendation
- Portfolio Ops Items
- Dev Portfolio Impact
- GitHub PR Tracking
- Delivery Evidence
- Evidence & Traceability Matrix
- Visual References / Diagrams

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
- `repo_location_label` for every issue payload, preferably `Repo › ...`
- `project_assignment_reason`: bounded deliverable reason or `empty`
- `cycle_assignment_reason`: current execution commitment reason or `empty`
- `github_tracking_rule`
- `delivery_evidence_rule`
- ready-to-create payloads when a live object is expected but unapplied
- `template` for each proposed issue payload, selected from `Bug`, `Feature`,
  `Research`, `Release`, or `Governance / Policy`; ask before creating when no
  template fits

Bug payloads must include `issue_type: bug`, reproduction, expected behavior,
actual behavior, affected surface, severity, and validation evidence.

## Template Rules

Always use a Linear issue template when creating an issue. Use the closest
matching template:

- `Bug`: defects or regressions.
- `Feature`: net-new capability.
- `Research`: investigation or discovery.
- `Release`: release planning, validation, or cut work.
- `Governance / Policy`: policy, control, or process-rule changes.

If no template fits, ask before creating the issue. Do not silently create an
untemplated issue.

## Label Policy

For every non-triage issue, apply the following exact mapping while keeping one
Type label and one Roadmap label:

- Bug -> Type > Bug
- Feature -> Type > Feature + Roadmap > Roadmap: Next
- Research -> Type > Research + Roadmap > Roadmap: Next
- Release -> Release + Reliability + Type > Docs + Roadmap > Roadmap: Now
- Governance / Policy -> Policy + Governance + Type > Docs + Roadmap > Roadmap: Next

If classification is unclear, keep the issue in Triage and ask. Prefer updating an
existing issue over creating a duplicate.

## Filing Model

Repo identity belongs in labels, not projects. Every issue payload must include
a repo/location label, preferably `Repo › ...`; legacy plain repo labels remain
valid only until migrated.

Projects are bounded deliverables, not permanent repo containers. Leave
`project` empty for speculative ideas, isolated backlog items, maintenance,
exploratory tasks, operational debt, and repo-owned work that is not part of an
active deliverable. Use `cycle` only for current execution commitment.

Prefer labels and views for repo slices, triage, maintenance queues, backlog
review, roadmap lanes, missing-project review, and active work by repo. Escalate
to projects only when coordination, delivery tracking, or bounded execution
requires it.

Delegate to Codex only when the issue has clear scope, a repo/location label,
acceptance criteria, validation command or proof expectation, enough structure
to execute safely, and active-execution intent.

Implementation PRs should be traceable to one primary Linear issue where
possible. Include the Linear issue identifier in branch, commit, or PR context.
Do not treat a merged PR as shipped evidence; use Linear Releases when
available, otherwise tags, deployments, changelog entries, package versions, or
manual release notes.

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

- Repo-specific identity routes through a repo/location label, preferably
  `Repo › ...`; legacy plain repo labels remain valid until migrated.
- Repo-specific work must not create or assume a matching repo-container
  project.
- Cross-repo workflow, reporting, shared governance, labels, or portfolio
  hygiene remains label/view organized unless it belongs to a bounded
  deliverable requiring project-level coordination.
- Portfolio-level operating model work may attach to `Dev Portfolio` only when
  the initiative improves review, prioritization, or sequencing.
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

## Visual References / Diagrams

Include this section for non-trivial Linear plans. Use it to make the active
set, dependency chain, eval gates, and human/agent route visible before payload
detail.

Required when any of these are true:

- three or more proposed Linear objects
- parent plus sub-issue structure
- dependency or blocker relationships
- Now / Next / Later / Do Not Create classification across multiple items
- human-versus-agent execution split
- eval gates or delivery evidence differ by issue

Preferred formats:

- Mermaid issue tree for milestone, parent, and sub-issue shape
- Mermaid dependency map for blockers and execution order
- markdown table for Now / Next / Later / Do Not Create
- markdown table for eval gates and delivery evidence

If no visual adds value, write `Not needed` and say why. Apply the shared
generated-media and proof rules from
`Plugins/harness-engineering/references/visual-reference-contract.md`.
