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
- ADR / Decision Artifact Readiness
- Core / Invariant Artifact Readiness
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
- `source_prompt_family_status`: required when the request references an
  original prompt method, source-prompt coverage, or upstream artifacts produced
  from source-prompt preservation. Include covered prompt family, authority
  limits, and downstream confidence.
- `subagent_policy`
- `roles_used`
- `roles_recommended`
- `roles_missing`
- `linear_mutation_status`: one of `not_requested`,
  `confirmation_required`, `blocked`, `created`, `updated`, or
  `not_applicable`
- `live_linear_blocker` when live tracking is expected but not completed
- `required_confirmation` when mutation approval is missing
- `decision_artifact_status`: one of `present`, `missing`, `blocked`,
  `upstream_required`, or `not_applicable`
- `core_artifact_status`: one of `present`, `missing`, `blocked`,
  `upstream_required`, or `not_applicable`
- `existing_project_match`: project name, live evidence source, status,
  duplicate/canceled alternatives, and mutation safety
- `live_linear_setup_status`: one of `verified`, `blocked`, `partial`,
  `unavailable`, or `not_applicable`; include team, initiative, repo project,
  Portfolio Ops, duplicate, canceled, archived, trashed, and mutation-safety
  evidence when the connector is available or requested
- `label_status`: one of `verified`, `blocked`, `partial`, `unavailable`, or
  `not_applicable`; distinguish issue labels, project labels, repo/location
  labels, type labels, roadmap labels, policy labels, and tags
- `template_status`: one of `selected`, `blocked`, `unavailable`, or
  `not_applicable`; identify the chosen template or the blocker preventing
  template-safe creation
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

If no template fits, ask before creating the issue. If the live Linear tool
surface cannot verify template names or template IDs, set `template_status: blocked`
or `template_status: unavailable`, include the closest intended
template type, and keep `linear_mutation_status: blocked` or
`confirmation_required`. Do not silently create an untemplated issue.

## Label Policy

Use existing labels first. Prefer already-live labels such as Developer
Experience, Reliability, Governance, Automation, type labels, roadmap labels,
repo/location labels, and policy labels when they preserve routing value. Linear
"tags" in user prompts map to the live label surface unless the connector
exposes a distinct tag object. Distinguish issue labels from project labels; a
project label match is not proof that the issue label can be applied. Propose
new labels only when the same missing label would be reused across multiple
future work items; explain why existing labels are insufficient and avoid
one-off labels.

For every non-triage issue, apply the following exact mapping while keeping one
Type label and one Roadmap label:

- Bug -> Type > Bug
- Feature -> Type > Feature + Roadmap > Roadmap: Next
- Research -> Type > Research + Roadmap > Roadmap: Next
- Release -> Release + Reliability + Type > Docs + Roadmap > Roadmap: Now
- Governance / Policy -> Policy + Governance + Type > Docs + Roadmap > Roadmap: Next

Use the exact live label names/IDs from Linear when they differ in display form
from this conceptual mapping, for example `Bug` with parent `Type (workspace)`
instead of inventing a literal `Type > Bug` label.

If classification is unclear, keep the issue in Triage and ask. Prefer updating an
existing issue over creating a duplicate.

When the live workspace lacks a required mapped label, set `label_status: blocked`
or `partial` and include a reusable ready-to-create label payload. Do
not silently weaken the mapping by dropping type, roadmap, repo/location, policy,
or operating labels.

## Filing Model

Repo identity belongs in labels and project routing must follow live evidence.
Every issue payload must include a repo/location label, preferably `Repo › ...`;
legacy plain repo labels remain valid only until migrated.

In the JSC Dev Portfolio model, existing repo control projects are valid
project-level destinations for repo-specific execution. Do not create duplicate
repo projects. Leave `project` empty for speculative ideas, isolated backlog
items, maintenance, exploratory tasks, operational debt, and repo-owned work
that is not part of active execution. Use `cycle` only for current execution
commitment.

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
- Repo-specific execution routes to the matching live repo control project when
  available and verified.
- Repo-specific work must not create or assume a new matching repo project when
  an existing canonical project is available.
- Cross-repo workflow, reporting, shared governance, labels, or portfolio
  hygiene routes to `Portfolio Ops` when live evidence confirms it and the work
  needs project-level coordination; otherwise keep it as plan-only or
  needs-human-triage.
- Portfolio-level operating model work may attach to `Dev Portfolio` only when
  the initiative improves review, prioritization, or sequencing.
- Do not create new initiatives, projects, labels, issues, comments, or status
  changes without explicit user confirmation after plan review.
- When the Linear connector is available or the user asks to check the actual
  `@linear` setup, verify profile/team, `Dev Portfolio`, matching repo project,
  `Portfolio Ops`, duplicate projects, canceled/archived/trashed state, issue
  labels, project labels, statuses, cycles/milestones when relevant, and issue
  template availability before recommending mutation.
- If live state is contradictory, for example a canonical repo project is both
  the intended destination and `trashed:true`, set `live_linear_setup_status: blocked`,
  preserve the evidence, and keep mutation blocked until the user
  confirms the intended target.
- If exact project lookup is tool-sensitive, prefer stable IDs from list results
  and mark the ambiguity instead of creating or selecting by approximate name.
- If destination cannot be proven, mark `needs_human_triage` and ask once when
  interactive steering is available.
- User pressure to create one issue per observation must preserve the filter:
  request the source observations and selected slice, then collapse work into
  the smallest useful milestone, parent issue, or `Do Not Create` classification.
- If artifacts came from an original prompt comparison or sampled upstream
  review, inherit evidence depth, coverage gaps, not-inspected surfaces,
  repo-specific drift signals, authority limits, and downstream confidence into
  the Linear plan before recommending active work.
- If source artifacts imply architecture-shaping, governance-defining,
  moat-critical, routing, or expensive-to-reverse decisions, require
  `.harness/decisions/**` readiness or mark `decision_artifact_status:
  upstream_required`; do not convert missing ADR reasoning into extra Linear
  objects.
- If the request is to create compressed architecture, routing, execution,
  governance, cognition, moat, anti-drift, or future-agent invariants under
  `.harness/core/**`, mark `core_artifact_status: upstream_required` or
  `blocked` and route upstream to `he-strategy` or `he-reframe`. This skill may
  consume `.harness/core/**` as execution constraints after the artifacts exist,
  but it must not generate the core cognition layer or turn missing invariant
  reasoning into Linear backlog.

## JSC Dev Portfolio Defaults

Use these defaults only when the request, artifacts, or live Linear evidence
confirms Jamie/JSC portfolio work:

- Workspace/team `Jscraik`; team key `JSC`.
- Top-level initiative `Dev Portfolio`.
- Cross-repo project `Portfolio Ops`.
- Repo-specific work routes to the matching live repo control project.
- Query issue labels in the JSC team scope and project labels separately.
- Treat project labels, issue labels, and user-facing "tags" as separate
  compatibility checks even when names overlap.
- Use the matching issue template for each ready-to-create payload; if template
  names or IDs are not available from the active tool surface, mark template
  creation blocked or confirmation-gated.

Do not create a new initiative or project unless the existing Dev Portfolio,
Portfolio Ops, and repo-project structure cannot represent the work cleanly and
the user approves the new object.

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
`Plugins/synaipse-harness/references/upstream/harness-engineering/visual-reference-contract.md`.
