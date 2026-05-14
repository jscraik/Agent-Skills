# Linear Filing Rule

Use this reference when `he-linear-plan` drafts, creates, updates, or validates
Linear issues, projects, cycles, labels, views, initiatives, PR linkage, or
delivery evidence.

## Core Model

| Concept | Responsibility |
| --- | --- |
| Issue | Atomic unit of work |
| Project | Bounded deliverable |
| Cycle | Current execution commitment |
| View | Dynamic operational lens |
| Label | Repo / type / priority / theme |
| Initiative | Strategic multi-project grouping |

## Filing Rules

- Every issue must have a repo/location label that identifies its repository,
  codebase, or operational surface.
- Prefer repo/location labels in the format `Repo › ...`.
- Legacy plain repo labels remain valid only until migrated.
- Use labels and views by default for intake, maintenance queues, security
  backlog, roadmap lanes, issue triage, operational filtering, backlog review,
  missing project review, and work not yet part of active execution.
- When the JSC Dev Portfolio model is confirmed and a matching live repo control
  project exists, repo-specific execution belongs in that project as the control
  surface, with milestones or parent issues carrying the bounded slice.
- Assign a project only when live evidence proves the destination and the issue
  contributes to active repo execution, a concrete bounded deliverable, or
  cross-repo coordination with a clear completion state.
- Leave `project` empty for speculative ideas, isolated backlog items,
  maintenance work, exploratory tasks, operational debt, or repo-owned work not
  yet part of an active deliverable.
- Do not create a new project simply because a repository, subsystem, or domain
  exists. Existing repo control projects may be used; duplicate repo projects
  must not be created.
- Use `cycle` only for work actively being committed to now.
- Keep speculative and future work lightweight: repo/location label, type label
  when clear, roadmap lane when clear, and no project or cycle until justified.
- Prefer updating an existing issue over creating a duplicate.

## Escalation Rules

Projects should emerge from multiple related issues, a clearly defined outcome,
active coordination needs, meaningful delivery tracking, or execution spanning
multiple work items. In the JSC Dev Portfolio model, existing repo control
projects are the durable project-level route for repo-specific execution; new
projects still require explicit justification and approval.

Use initiatives only for top-level strategic grouping. `Dev Portfolio` is the
default top-level initiative for Jamie/JSC portfolio work when live evidence
confirms the setup, but it must not replace useful project boundaries or become
a dumping ground for unrelated work. Leave initiative empty when it does not
improve review, prioritization, or sequencing.

## Repo Labels

Preferred repo/location examples:

- `Repo › agent-skills`
- `Repo › coding-harness`
- `Repo › X-writer`
- `Repo › design-system`
- `Repo › diagram-cli`
- `Repo › codex-updates`

Legacy examples that remain valid until migrated:

- `agent-skills`
- `diagram-cli`
- `X-writer`
- `design-system`
- `codex-updates`
- `recon-workbench`

## Delegation Rule

Delegate to Codex only when the issue has clear scope, the correct repo/location
label, acceptance criteria, validation command or proof expectation, enough
structure to execute safely, and belongs to active execution rather than vague
backlog parking.

## GitHub Tracking Rule

Every implementation PR should be traceable to one primary Linear issue where
possible. Include the Linear issue identifier in the branch name, commit
history, or PR context so Linear can associate the PR with the issue. Keep the
Linear issue updated instead of letting the PR become the only source of truth.

Preferred branch pattern:

- `jsc-123-short-description`

Minimum rule:

- the Linear issue identifier appears somewhere reliable in the implementation
  flow.

## Delivery Evidence Rule

Do not assume a merged PR means the work reached users.

- Done = implementation accepted.
- Merged = PR merged.
- Released/Shipped = backed by Linear Release, deployment, package, tag, or
  changelog evidence.

When Linear Releases are available, use them as preferred shipped evidence and
ensure issue identifiers appear in commits, branches, or PRs. When Linear
Releases are unavailable, use GitHub merge, tags, deployment records, changelog
entries, package versions, or manual release notes, and record that evidence in
Linear when the distinction matters.

## Recommended Views

- `Intake · Missing Repo`
- `Intake · Missing project`
- `Template Enforcement · Missing Type`
- `Intake · Missing Roadmap`
- `Repo · Needs grouping`
- `Repo · Backlog parking lot`
- `Flow · Active deliverables`

## Live Linear Validation

Linear tool capability confirms issues support `labels`, `project`, `cycle`,
`links`, `state`, `priority`, and `delegate` fields. Before recommending live
mutation, reconcile the actual Linear setup with the plan:

- profile and OAuth connectivity
- JSC team and `JSC` key
- `Dev Portfolio` initiative
- matching repo project and duplicate/canceled/archived/trashed alternatives
- `Portfolio Ops` for cross-repo work
- issue statuses and current execution states
- project labels and issue labels as separate surfaces
- repo/location, type, roadmap, policy, and operating labels/tags
- milestones and cycles when proposed
- issue template names or IDs for the selected issue kind

User-facing "tags" map to Linear labels unless the active connector exposes a
distinct tag object. If required labels/tags are missing from the live
workspace, return `label_status: blocked` with a ready-to-create reusable label
payload instead of silently weakening the filing rule. If the correct issue
template cannot be verified, return `template_status: blocked` or
`template_status: unavailable` and do not create untemplated issues.

## JSC Portfolio Setup Evidence

When the user asks to use the JSC portfolio setup, verify live state where
tools allow it before planning mutation.

Observed live model evidence from 2026-05-14 plugin reads:

- The authenticated user was available through the Linear app, and the `JSC`
  team resolved to `Jscraik`.
- `Dev Portfolio` resolved as the top-level initiative.
- `agent-skills` resolved to a canonical repo control project plus a canceled
  duplicate. The canonical result also reported `trashed:true`, which blocks
  mutation until the intended live destination is confirmed.
- `Portfolio Ops` resolved for cross-repo coordination, but name lookup can be
  tool-sensitive; prefer stable IDs from list results and block mutation on
  trashed/backlog contradictions until confirmed.
- Common operating project labels and team-scoped issue labels exist for
  Developer Experience, Reliability, Governance, and Automation.
- The JSC issue-label surface includes `agent-skills` under `Repo`, Roadmap
  lanes, and type labels such as `Bug`, `Feature`, `Research`, `Docs`, and
  `Refactor`; use exact live label names/IDs rather than inventing display-only
  labels.
- Template availability was evidenced from Linear documentation, but the active
  app tool surface did not expose a template listing call in this session. Treat
  exact template IDs/names as `template_status: blocked` or
  `confirmation_required` unless the user or tool context supplies them.
