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
- Use labels and views by default for repo slices, maintenance queues, security
  backlog, roadmap lanes, issue triage, operational filtering, backlog review,
  missing project review, and active work by repo.
- Assign a project only when the issue contributes to a concrete bounded
  deliverable with a clear completion state.
- Leave `project` empty for speculative ideas, isolated backlog items,
  maintenance work, exploratory tasks, operational debt, or repo-owned work not
  yet part of an active deliverable.
- Do not create a project simply because a repository, subsystem, or domain
  exists.
- Use `cycle` only for work actively being committed to now.
- Keep speculative and future work lightweight: repo/location label, type label
  when clear, roadmap lane when clear, and no project or cycle until justified.
- Prefer updating an existing issue over creating a duplicate.

## Escalation Rules

Projects should emerge from multiple related issues, a clearly defined outcome,
active coordination needs, meaningful delivery tracking, or execution spanning
multiple work items. Remain in labels and views until the work proves stronger
structure is necessary.

Use initiatives only for top-level strategic grouping. `Dev Portfolio` may be
used as a portfolio-level rollup, but it must not replace useful project
boundaries or become a dumping ground for unrelated work. Leave initiative
empty when it does not improve review, prioritization, or sequencing.

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
`links`, `state`, `priority`, and `delegate` fields. If required labels are
missing from the live workspace, return `label_status: blocked` with a
ready-to-create reusable label payload instead of silently weakening the filing
rule.
