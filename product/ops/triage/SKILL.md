---
name: triage
description: Triage file-based `todos/` findings into ready, skipped, or revised states before execution. Use when the repo already uses the file-based todo workflow and the user wants approval-style triage, not tracker triage or todo execution.
metadata:
  skill-type: team_automation
---

# Triage

Use a focused file-based todo triage workflow that sits between finding generation and implementation. Preserve the imported compound-engineering todo-approval flow, but keep routing narrow so generic issue triage, review, and execution stay with their correct owners.

## Table of Contents
- [Standards snapshot](#standards-snapshot)
- [When to use](#when-to-use)
- [When not to use](#when-not-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Workflow](#workflow)
- [Decision outcomes](#decision-outcomes)
- [Routing map](#routing-map)
- [Upstream preservation](#upstream-preservation)
- [Validation](#validation)
- [Constraints](#constraints)
- [Examples](#examples)
- [Remember](#remember)
- [Gotchas](#gotchas)
- [Failure mode](#failure-mode)

## Standards snapshot
- Treat `todos/` artifacts as the source of truth for this workflow.
- Triage is a decision stage, not an implementation stage. Do not code fixes here.
- Default review-created findings start `pending`; triage decides whether they become `ready`, get skipped, or need light edits before approval.
- Keep one item in focus at a time unless the user explicitly wants a batch summary.
- Preserve exact status transitions in both filename and frontmatter so downstream execution can trust the backlog.

## When to use
- The repo already has file-based `todos/` items and the user wants pending findings triaged before work begins.
- The user wants review findings approved, skipped, or lightly adjusted before they enter the execution queue.
- A review or audit produced findings that should be converted into actionable todo state without implementing them yet.
- The user wants the missing approval bridge between `ce-review` and `resolve-todo-parallel`.

## When not to use
- Do not use for generic product or issue-tracker triage. Use [`linear`](/Users/jamiecraik/dev/Agent-Skills/product/ops/linear/SKILL.md).
- Do not use to create findings from a review. Use [`ce-review`](/Users/jamiecraik/dev/Agent-Skills/product/ops/ce-review/SKILL.md).
- Do not use to execute approved todo work. Use [`resolve-todo-parallel`](/Users/jamiecraik/dev/Agent-Skills/product/ops/resolve-todo-parallel/SKILL.md) or `ce-work` for single-item execution.
- Do not use for local `tasks/TASKS.md` workflows. Use [`simple-tasks`](/Users/jamiecraik/dev/Agent-Skills/utilities/simple-tasks/SKILL.md).
- Do not use when the repo has no `todos/` workflow and the user is asking for generic prioritization advice.

## Required inputs
- A repo with a `todos/` directory or a supplied findings list that should enter that workflow.
- Optional selector:
  - all pending todos
  - specific todo IDs
  - specific finding list
- Any preference for:
  - prompt-per-item interactive triage
  - bulk summary first
  - default skip behavior when evidence is weak

## Deliverables
- A discovered set of candidate findings or pending todo items.
- Per-item triage outcomes:
  - `ready`
  - `skipped`
  - `customized`
  - `blocked`
- Renamed todo files and updated frontmatter for approved items.
- Deleted or intentionally preserved skipped items, depending on the repo workflow and user intent.
- A final summary with counts, affected files, and the next recommended workflow step.
- If requested, a structured status report matching [`references/contract.yaml`](/Users/jamiecraik/dev/Agent-Skills/product/ops/triage/references/contract.yaml) with `schema_version: 1`.

## Workflow
1. Discover the triage source.
   - Prefer existing `todos/*-pending-*.md` items when the repo already uses the file-based workflow.
   - If the user supplied a findings list instead, use it to create or update pending todo entries before approval.
2. Read each candidate item fully before deciding.
   - Capture status, priority, issue ID, dependencies, findings, proposed solutions, and acceptance criteria.
3. Present one item at a time unless the user explicitly asks for a bulk review.
   - Include title, severity, category, location, problem scenario, proposed solution, and effort.
   - Offer the triage decision set: `yes`, `next`, or `custom`.
4. Apply the decision without coding.
   - `yes`: promote `pending` to `ready` and update the filename/frontmatter.
   - `next`: skip the item and remove it from the pending queue according to the local file-todo workflow.
   - `custom`: adjust priority, description, or details, then confirm again before promotion.
5. Continue until all items are processed.
6. Return a final summary and route cleanly to the next stage.
   - Approved work -> `resolve-todo-parallel`
   - New findings needed -> `ce-review`
   - Tracker-level triage -> `linear`

## Decision outcomes
- `yes`
  - Rename `{id}-pending-{priority}-{desc}.md` to `{id}-ready-{priority}-{desc}.md`.
  - Update frontmatter `status: pending` -> `status: ready`.
  - Add or update the work-log entry that records triage approval.
- `next`
  - Remove the item from the active triage queue.
  - When the repo uses the CE file-todo lifecycle, delete the skipped pending file rather than leaving stale backlog noise.
- `custom`
  - Adjust the minimum needed details such as priority, short description, tags, or recommended action.
  - Re-present the revised item before promoting it to `ready`.
- `blocked`
  - Keep the item pending when user intent, evidence, or dependencies are not strong enough for approval.

## Routing map
- Read [`references/overlap-matrix.md`](/Users/jamiecraik/dev/Agent-Skills/product/ops/triage/references/overlap-matrix.md) before widening this skill's trigger wording.
- Use [`ce-review`](/Users/jamiecraik/dev/Agent-Skills/product/ops/ce-review/SKILL.md) to generate findings and initial pending todo artifacts.
- Use [`resolve-todo-parallel`](/Users/jamiecraik/dev/Agent-Skills/product/ops/resolve-todo-parallel/SKILL.md) once approved items are `ready`.
- Use [`linear`](/Users/jamiecraik/dev/Agent-Skills/product/ops/linear/SKILL.md) for team tracker triage and issue updates.
- Use [`simple-tasks`](/Users/jamiecraik/dev/Agent-Skills/utilities/simple-tasks/SKILL.md) for lightweight `tasks/TASKS.md` flows instead of file-based `todos/`.

## Upstream preservation
- The imported compound-engineering source is preserved in [`references/upstream-triage.md`](/Users/jamiecraik/dev/Agent-Skills/product/ops/triage/references/upstream-triage.md).
- The local install keeps the core upstream flow:
  - present findings one by one
  - decide `yes | next | custom`
  - update todo state without coding
  - summarize approved and skipped work
- The local adaptation narrows the routing to file-based `todos/`, aligns the lifecycle with `ce-review` and `resolve-todo-parallel`, and removes legacy tool/runtime assumptions like `/model Haiku`.

## Validation
- Verify the repo actually has a `todos/` workflow before using this skill as the primary lane.
- Verify each approved item updates both filename and frontmatter status consistently.
- Verify no code implementation happened during triage.
- Verify skipped items were handled according to the repo's file-todo lifecycle instead of being left as silent backlog drift.
- Verify the final summary names the correct next workflow stage.
- Fail fast at the first broken gate.

## Constraints
- Do not implement fixes or code changes during triage.
- Do not silently convert generic tracker triage into file-based todo mutations.
- Do not promote an item to `ready` without enough evidence to make it actionable.
- Do not leave filename/frontmatter drift after a status change.
- Redact secrets, credentials, and sensitive data from todo artifacts and summaries.

## Examples
- "Triage the pending todo findings in this repo and tell me which ones are ready for work."
- "Go through these review findings one by one and approve the ones that should enter the todo queue."
- "Review all `todos/*-pending-*.md` items, let me skip weak ones, and move the good ones to `ready`."
- "Use triage after code review, but do not implement anything yet."

## Remember
- Triage is a decision checkpoint, not a coding checkpoint.
- The whole point is to leave the backlog cleaner and more executable than it was before.

## Gotchas
- The upstream skill name is broader than the actual workflow. Locally, treat it as file-based todo triage, not universal issue triage.
- This repo already has `resolve-todo-parallel`, so triage should stop after approval rather than drifting into execution.
- If the repo has no `todos/` directory, this skill should usually route elsewhere instead of inventing a file-based workflow.

## Failure mode
- If there is no usable `todos/` workflow or findings source, stop and name the smallest missing input.
- If the request is really tracker triage, review generation, or execution, route to the correct skill instead of stretching this one.
- If candidate items are too underspecified to approve safely, keep them pending and say exactly what is missing.

## See Also
| Skill | When to use |
|---|---|
| [[ce-work]] | Execute the approved work once triage decisions are made |
| [[resolve-todo-parallel]] | Resolve a batch of approved todo items in parallel rather than triaging them |
| [[systematic-debugging]] | Diagnose unclear or flaky findings before deciding whether they belong in the queue |
| [[linear]] | Route to tracker-first triage when the work lives in Linear instead of repo todo files |

**Topic map:** [[agent-ops]]
