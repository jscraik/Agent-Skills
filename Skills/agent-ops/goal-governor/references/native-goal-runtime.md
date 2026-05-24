# Native Goal Runtime

Read when reconciling Goal Governor boards with the live Codex `/goal` runtime.

This reference was refreshed from `openai/codex@main` through the codex-repo MCP on 2026-05-24.

## Current Evidence Surfaces

- `/Users/jamiecraik/dev/codex/codex-rs/features/src/lib.rs` defines `Feature::Goals` as an experimental feature with config key `goals`; it is disabled by default.
- `/Users/jamiecraik/dev/codex/codex-rs/tools/src/tool_config.rs` exposes `goal_tools` only when `Feature::Goals` is enabled, then filters that exposure through `with_goal_tools_allowed`.
- `/Users/jamiecraik/dev/codex/codex-rs/core/src/session/turn_context.rs` allows goal tools only for non-ephemeral turns with an available state database.
- `/Users/jamiecraik/dev/codex/codex-rs/state/src/model/thread_goal.rs` defines persistent goal fields: `goal_id`, `objective`, `status`, `token_budget`, `tokens_used`, `time_used_seconds`, `created_at`, and `updated_at`.
- `/Users/jamiecraik/dev/codex/codex-rs/state/src/runtime/goals.rs` owns state transitions, expected-goal-id guarded updates, token accounting, and budget-limit behavior.
- `/Users/jamiecraik/dev/codex/codex-rs/core/src/context/goal_context.rs` wraps runtime-owned goal steering prompts in `<goal_context>` user-context fragments.
- `/Users/jamiecraik/dev/codex/codex-rs/core/src/tools/handlers/goal_spec.rs` exposes `update_goal` only for `complete` and `blocked`; `blocked` requires a strict repeated-blocker audit.
- `/Users/jamiecraik/dev/codex/codex-rs/core/templates/goals/continuation.md` tells agents to preserve the original scope, audit every requirement against current evidence, and use `blocked` only after the same blocker repeats for at least three consecutive goal turns.
- `/Users/jamiecraik/dev/codex/codex-rs/core/templates/goals/budget_limit.md` tells agents not to start new substantive work once the system marks a goal `budget_limited`.
- `/Users/jamiecraik/dev/codex/codex-rs/core/templates/goals/objective_updated.md` tells the model that edited objectives are user-provided data, supersede the previous objective, and do not justify `update_goal` unless the updated goal is actually complete.
- `/Users/jamiecraik/dev/codex/codex-rs/tui/src/chatwidget/goal_validation.rs` enforces the native objective limit and instructs users to put longer instructions in a file.
- `/Users/jamiecraik/dev/codex/codex-rs/tui/src/chatwidget/slash_dispatch.rs` handles `/goal edit`, `/goal pause`, `/goal resume`, `/goal clear`, and objective creation when the `goals` feature is enabled.
- `/Users/jamiecraik/dev/codex/codex-rs/tui/src/chatwidget/goal_menu.rs` displays goal status, usage, and command hints; editing a `budgetLimited` or `complete` goal sets the edited status to `active` in the TUI path.
- `/Users/jamiecraik/dev/codex/codex-rs/app-server/README.md` documents `thread/goal/set` and says clients can set `budgetLimited`; app-server tests show ephemeral threads reject goals and same-objective set calls can preserve `budgetLimited`.

## Runtime Facts

- Native goals are feature-gated. Check the `goals` feature and current-turn tool exposure before assuming goal tools exist.
- Ephemeral threads do not support goals because goal tools require a materialized thread and state database.
- Native objective text must be non-empty and no more than 4,000 characters.
- Native persistent storage uses status strings `active`, `paused`, `blocked`, `usage_limited`, `budget_limited`, and `complete`.
- App-server JSON can expose the budget-limited state as `budgetLimited`. Goal Governor output normalizes either spelling to `budget_limited`.
- `update_goal` can mark a native goal `complete` or `blocked`; pause, resume, budget-limit, and usage-limit are user/system controlled.
- `blocked` is not a generic validation failure. Use it only when the same blocking condition has repeated for at least three consecutive goal turns and no meaningful progress is possible without owner input or external-state change.
- `usage_limited` is a system usage stop state. Treat it like a native stop-state signal that pauses Worker implementation until owner or PM/Judge recovery.
- Native `goal_id`, `created_at`, and `updated_at` identify the live objective version and help detect stale board reconciliation.
- Native token budget, tokens used, elapsed seconds, and lifecycle timing are steering evidence, not completion proof.
- `budget_limited` is terminal in the native status model, but runtime accounting can still include budget-limited goals for in-flight usage depending on the accounting mode.
- `/goal edit` is not just prose. The TUI path opens an editor and can reactivate a budget-limited or complete goal after the user changes the objective.
- App-server set/update behavior can preserve `budgetLimited` for the same objective, so the board must inspect the resulting native status instead of assuming an edit resumes work.
- Goal-context prompts and `objective_updated.md` treat objectives as user-provided data. They steer the task while remaining subordinate to system, developer, repository, and safety instructions.
- Native completion is not enough to mark a board complete. The board still requires a final PM or Judge audit receipt with `decision: complete`.

## Doctor Checks

Report each check as `pass`, `fail`, `blocked`, or `not applicable`:

- `goals` feature configured or explicitly blocked.
- Goal tools exposed for the current turn; non-ephemeral thread and state database are available when native tools are required.
- Native objective is non-empty and no more than 4,000 characters.
- Native status is reconciled from the actual runtime result, not inferred from requested command text.
- Native `goal_id`, `created_at`, `updated_at`, token budget, tokens used, and elapsed seconds are captured when available.
- App-server or tool path used for goal inspection is named in the receipt.
- Repo board passes `python3 Skills/agent-ops/goal-governor/scripts/check_goal_board.py <goal-directory>`.

## Reconciliation Rules

1. If native goal state is unavailable, report `native_goal_status: unknown` or `blocked` and continue only with board-safe read-only checks.
2. If goal tools are unavailable because the thread is ephemeral or state storage is absent, classify native inspection as blocked rather than assuming runtime absence.
3. If native status is `paused`, stop Worker implementation and ask for owner or PM direction.
4. If native status is `blocked`, verify the strict repeated-blocker audit and ask owner or PM/Judge direction before Worker work.
5. If native status is `usage_limited`, classify system usage stop-state evidence and ask owner or PM/Judge direction before Worker work.
6. If native status is `budgetLimited` or `budget_limited`, classify scope, verification, and owner decision before Worker work.
7. If native status is `complete` while board work remains active, route to PM or Judge reconciliation before editing implementation files.
8. If board status is done while native status remains active, require a completion audit before updating the native goal.
9. If `goal_id` changed since the last board receipt, treat verification as stale until a reconciliation receipt explains whether the objective changed intentionally.
10. If `/goal edit` or `objective_updated` context appears, re-read the board objective and native objective before continuing previous work.

## Board Metadata

When available, preserve native runtime metadata in `state.yaml`:

```yaml
goal:
  native_goal_id: goal_opaque_id
  native_objective: "/goal Follow docs/goals/example/goal.md"
  native_status: active
  token_budget: null
  tokens_used: 0
  time_used_seconds: 0
  native_created_at: "2026-05-13T10:00:00Z"
  native_updated_at: "2026-05-13T10:00:00Z"
```

Treat changes to `native_goal_id`, `native_objective`, `native_status`, `token_budget`, `tokens_used`, `time_used_seconds`, or native timestamps as stale verification until a new reconciliation receipt records the decision.

## Preserved Root Context

Keep these root-instruction details discoverable after root compression:

- Treat goal work as a state machine, not a vibe. The agent should always know the native goal status, the board status, the active task, the write scope, and the exact evidence required to continue.
- Use when the user asks to create, continue, repair, audit, or operationalize a long-running Codex goal, especially when the work is broad, stale, blocked, multi-agent, high-risk, or likely to span more than one session.
- In `create` mode, scaffold a goal board, verify the local Codex runtime can support goals, and print the `/goal Follow <goal.md>` command.
- In `doctor` mode, check installation, Codex goal enablement, agent runtime depth, board validity, and verification freshness.
- Reconcile native goal state with board state. Treat mismatches as PM or Judge work before Worker implementation.
- Ensure exactly one active task unless the user explicitly requested parallel Workers with disjoint `allowed_files`.
- Refuse write-capable work until the active Worker task declares `allowed_files`, `verify`, and `stop_if`.
- If verification is missing, red, stale, blocked, or from a different dirty fingerprint, recover verification before feature work.
- Mark a goal complete only after a final Judge or PM audit receipt with `decision: complete`; then update the native goal status.
- Apply the context-disposition policy: move important still-valid context to references and index it when meaningful; intentionally discard stale, duplicated, unsafe, superseded, or low-signal text.
