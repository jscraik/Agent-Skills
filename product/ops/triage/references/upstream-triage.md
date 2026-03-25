# Upstream Triage

Pinned source:
- `https://github.com/EveryInc/compound-engineering-plugin/blob/0fdc25a36cabea4ce9e2ae47ff69c1a9a2de8f0b/plugins/compound-engineering/skills/triage/SKILL.md`

Read when:
- You need the full imported compound-engineering wording rather than the tighter local routing layer.
- You are checking whether a local cleanup accidentally dropped useful status-transition detail.

## Preserved upstream frontmatter
- `name: triage`
- `description: Triage and categorize findings for the CLI todo system`
- `argument-hint: "[findings list or source type]"`
- `disable-model-invocation: true`

## Preserved upstream core behavior
- Read all pending todos in the `todos/` directory.
- Present findings one by one with:
  - issue title
  - severity
  - category
  - description
  - location
  - problem scenario
  - proposed solution
  - estimated effort
- Ask for the triage decision:
  - `yes`
  - `next`
  - `custom`

## Preserved upstream status transitions
- `yes`
  - rename `{id}-pending-{priority}-{desc}.md` -> `{id}-ready-{priority}-{desc}.md`
  - update frontmatter `status: pending` -> `status: ready`
  - add the work-log approval entry
- `next`
  - delete the todo file and move on
- `custom`
  - adjust the triage details and re-present the item

## Preserved upstream final summary shape
- total items
- todos approved
- skipped items
- summary of status changes
- next-step options including `resolve-todo-parallel`

## Local adaptation notes
- The local skill narrows the scope to the repo's file-based `todos/` lifecycle and routes generic issue triage to `linear`.
- The local skill removes the legacy `/model Haiku` runtime assumption and does not inherit the old "keep moving without approval" phrasing where it conflicts with Codex-style interaction.
- The local skill treats `ce-review` as the primary source of pending todo findings and `resolve-todo-parallel` as the primary execution stage after approval.
