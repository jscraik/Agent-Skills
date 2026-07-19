# Creation And Continuation

Read when selecting the next Goal Governor action.

## Create

1. Discover project instructions and validation wrappers.
2. Verify the native `goals` feature is enabled and goal tools are exposed for a materialized, non-ephemeral thread, or classify setup as blocked.
3. Confirm the native objective will fit the current Codex limit: non-empty and at most 4,000 characters.
4. Choose a slug and create `docs/goals/<slug>/`.
5. Write `goal.md` with a visible completion contract section that uses these
   exact field names in this order: `outcome`, `verification_surface`,
   `constraints`, `boundaries`, `iteration_policy`, and
   `blocked_stop_condition`. Avoid replacing these schema-backed terms with
   loose headings such as Stop Rules or Verification Command only.
6. Write `state.yaml` with one active Scout task unless the starting evidence is already complete.
7. For governed implementation goals that will include Worker tasks, create the
   required MDX implementation notes artifact at
   `.harness/implementation-notes/<date>-<work>-notes.mdx`, reference it from
   `artifacts.implementation_notes`, record Browser localhost preview and
   live-update metadata, and include it in Worker `allowed_files`.
8. Create an empty `receipts.jsonl` and `notes/`.
9. Run `python3 scripts/check_goal_board.py <goal-directory>`.
10. Print the exact command:

```text
/goal Follow docs/goals/<slug>/goal.md
```

Also state that this is a prompt convention and Codex must read the file.

## Continue

1. Read `goal.md`, `state.yaml`, and recent receipts, then record
   `read goal.md and state.yaml first` and `receipts.jsonl` in the output
   contract.
2. Inspect native goal state when tools or app-server access is available, including `goal_id`, objective, status, token budget, tokens used, elapsed seconds, and update timestamps.
3. Reconcile native state and board state.
4. If the board is invalid, route to repair.
5. If native status is `blocked`, verify the repeated-blocker audit. When the
   audit has not reached the required repeated-turn threshold, continue or
   report an audit mismatch with `worker_must_pause: false` and
   `work_should_pause: false`; route to owner or PM/Judge only after the gate is
   met or another owner-stop gate is present.
6. If native status is `usage_limited`, classify system usage stop-state
   evidence and route to owner or PM/Judge recovery before Worker work.
7. If native status is `budgetLimited` or `budget_limited`, route to PM or
   Judge classification before Worker work.
8. If `/goal edit` or `objective_updated` changed the objective, route to PM or Judge reconciliation before continuing old work.
9. If verification is stale or red, route to Scout/Judge recovery.
10. If active task is Scout or Judge, keep work read-only and write a receipt.
11. If active task is Worker, enforce `allowed_files`, `verify`,
    `stop_if`, and the required MDX implementation notes artifact before
    implementation work continues.
12. After task completion, append a receipt and update the receipt closure
    ledger before selecting the next task. Keep task completion separate from
    goal closure: Scout, Worker, and Governor receipts are never final closure;
    `pass_with_*`, `blocked_*`, and `requires_*` decisions retain their named
    recheck or blocker.
13. For closeout, report local validation, generated artifacts, remote PR
    checks, review threads, tracker state, and merge readiness as separate truth
    lanes when those surfaces are involved. Permit `decision: complete` only for
    a final Judge or PM receipt that accounts for every board-required task,
    pending recheck, and current verifier required by the completion contract.

## Doctor

Doctor should report:

- Skill package present.
- Native `goals` feature configured.
- Goal tools exposed for the current turn, with a materialized thread and state database when native inspection is required.
- Native objective non-empty and within the current 4,000-character limit.
- Native `goal_id`, objective, status, token budget, tokens used, elapsed seconds, and update timestamps captured when available.
- Native stopped states `blocked`, `usage_limited`, and `budget_limited`
  classified separately from validation failures and environment blockers.
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

Before changing a board, write or return an output contract that says
`board drift detected before repair`, names the invalid surface, and states
`no fabricated receipts` plus
`owner approval required before completion or scope broadening`.

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
