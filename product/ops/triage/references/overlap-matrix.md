# Triage Overlap Matrix

Use this matrix to keep `triage` focused on file-based todo approval and status transitions, not review generation, tracker triage, or execution.

## Table of Contents
- [Boundary rule](#boundary-rule)
- [Matrix](#matrix)
- [Notes](#notes)

## Boundary rule
- Trigger `triage` when the repo uses a file-based `todos/` workflow and the main job is deciding whether pending findings should become `ready`, get skipped, or be lightly adjusted before approval.
- If the user wants to generate findings, manage an external tracker, or execute work, route to the narrower owner instead.

## Matrix

| Request shape | Primary outcome | Owner |
|---|---|---|
| "Triage the pending todo findings and approve the good ones." | File-based todo approval | `triage` |
| "Walk these pending todo files one by one and move the actionable ones to ready." | Pending -> ready decision stage | `triage` |
| "Review this branch and create todo findings." | Review generation and todo creation | `ce-review` |
| "Resolve all ready todos in parallel." | Todo execution | `resolve-todo-parallel` |
| "Triage our Linear backlog." | External tracker triage | `linear` |
| "Set up tasks/TASKS.md for this repo." | Lightweight task tooling | `ce-work` |

## Notes
- `triage` is the approval bridge between `ce-review` and `resolve-todo-parallel`.
- The upstream skill name is broader than the local scope; do not broaden it into generic issue management.
