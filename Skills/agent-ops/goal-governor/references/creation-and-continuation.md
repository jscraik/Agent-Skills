# Creation And Continuation

Read when selecting the next Goal Governor action.

## Create

1. Discover project instructions and validation wrappers.
2. Verify the native `goals` feature is enabled and goal tools are exposed for a materialized, non-ephemeral thread, or classify setup as blocked.
3. Confirm the native objective will fit the current Codex limit: non-empty and at most 4,000 characters.
4. Choose a slug and create `docs/goals/<slug>/`.
5. Write `goal.md` with objective, constraints, stop rules, and exit criteria.
6. Write `state.yaml` with one active Scout task unless the starting evidence is already complete.
7. Create an empty `receipts.jsonl` and `notes/`.
8. Run `python3 scripts/check_goal_board.py <goal-directory>`.
9. Print the exact command:

```text
/goal Follow docs/goals/<slug>/goal.md
```

Also state that this is a prompt convention and Codex must read the file.

## Continue

1. Read `goal.md`, `state.yaml`, and recent receipts.
2. Inspect native goal state when tools or app-server access is available, including `goal_id`, objective, status, token budget, tokens used, elapsed seconds, and update timestamps.
3. Reconcile native state and board state.
4. If the board is invalid, route to repair.
5. If native status is `budgetLimited`, route to PM or Judge classification before Worker work.
6. If `/goal edit` or `objective_updated` changed the objective, route to PM or Judge reconciliation before continuing old work.
7. If verification is stale or red, route to Scout/Judge recovery.
8. If active task is Scout or Judge, keep work read-only and write a receipt.
9. If active task is Worker, enforce `allowed_files`, `verify`, and `stop_if`.
10. After task completion, append a receipt before selecting the next task.

## Doctor

Doctor should report:

- Skill package present.
- Native `goals` feature configured.
- Goal tools exposed for the current turn, with a materialized thread and state database when native inspection is required.
- Native objective non-empty and within the current 4,000-character limit.
- Native `goal_id`, objective, status, token budget, tokens used, elapsed seconds, and update timestamps captured when available.
- Agent depth compatible with the task.
- Scout/Judge/Worker roles installed or projected.
- Goal board schema valid.
- Receipt log parseable.
- Verification evidence fresh.
- Exactly one write-capable active task.

Archived active-skill line preserved for context migration only; current Goal
Governor checks use `python3 scripts/check_goal_board.py <goal-directory>`.

   - Agent-driven runs append `--robot` to `./bin/ask check_goal_board <goal-directory>` for stable parsing.

## Repair

Safe repairs:

- Fill missing optional arrays as `[]`.
- Move bulky unexpected files into `notes/` after reporting the move.
- Add a queued PM task to reconcile state drift.
- Mark verification unknown when dirty fingerprint cannot be trusted.

Unsafe repairs requiring owner confirmation:

- Marking a goal complete.
- Deleting tasks or receipts.
- Broadening Worker `allowed_files`.
- Changing native goal state.
- Writing into `~/.codex`.

## Import

When importing a spec, plan, or issue:

- Keep the original source path in `goal.md`.
- Preserve acceptance criteria as exit criteria.
- Seed a Scout task to validate current repo state before Worker work.
- Do not convert speculative notes into done receipts.
