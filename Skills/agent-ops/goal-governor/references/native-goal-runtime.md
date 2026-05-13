# Native Goal Runtime

Read when reconciling Goal Governor boards with the live Codex `/goal` runtime.

This reference was refreshed from `/Users/jamiecraik/dev/codex` on 2026-05-06 after the pull ending at merge commit `1487d2405`.

## Live Codex Surfaces

- `/Users/jamiecraik/dev/codex/codex-rs/protocol/src/protocol.rs` defines native goal create/update/get request and response types.
- `/Users/jamiecraik/dev/codex/codex-rs/core/src/goals.rs` owns goal state, lifecycle transitions, token budget accounting, and completion updates.
- `/Users/jamiecraik/dev/codex/codex-rs/tui/src/chatwidget/goal_validation.rs` validates `/goal` objectives before native creation.
- `/Users/jamiecraik/dev/codex/codex-rs/app-server/src/request_processors/thread_goal_processor.rs` exposes app-server thread goal operations.

## Runtime Facts

- Use this skill to turn Codex's native `/goal` feature into an auditable operating loop. Native goals persist an objective; this skill governs the repo-visible plan, current task, verification evidence, and completion audit that keep the objective from drifting.
- Native objective text must be non-empty and no more than 4,000 characters.
- Native goal status uses `active`, `paused`, `budgetLimited`, and `complete`.
- Goal Governor output normalizes native `budgetLimited` to `budget_limited`.
- Native token budget, tokens used, elapsed seconds, and lifecycle timing are steering evidence, not completion proof.
- Native completion is not enough to mark a board complete. The board still requires a final PM or Judge audit receipt with `decision: complete`.

## Reconciliation Rules

1. If native goal state is unavailable, report `native_goal_status: unknown` or `blocked` and continue only with board-safe read-only checks.
2. If native status is `paused`, stop Worker implementation and ask for owner or PM direction.
3. If native status is `budgetLimited`, classify scope, verification, and owner decision before Worker work.
4. If native status is `complete` while board work remains active, route to PM or Judge reconciliation before editing implementation files.
5. If board status is done while native status remains active, require a completion audit before updating the native goal.

## Board Metadata

When available, preserve native runtime metadata in `state.yaml`:

```yaml
goal:
  native_objective: "/goal Follow docs/goals/example/goal.md"
  native_status: active
  token_budget: null
  tokens_used: 0
  time_used_seconds: 0
```

Treat changes to `native_status`, `token_budget`, `tokens_used`, or `time_used_seconds` as stale verification until a new reconciliation receipt records the decision.

## Preserved Root Context

Keep these root-instruction details discoverable after root compression:

- Treat goal work as a state machine, not a vibe. The agent should always know the native goal status, the board status, the active task, the write scope, and the exact evidence required to continue.
- Use when the user asks to create, continue, repair, audit, or operationalize a long-running Codex goal, especially when the work is broad, stale, blocked, multi-agent, high-risk, or likely to span more than one session.
- In `create` mode, scaffold a goal board, verify the local Codex runtime can support goals, and print the `/goal Follow <goal.md>` command.
- In `doctor` mode, check installation, Codex goal enablement, agent runtime depth, board validity, and verification freshness.
- Inputs may include goal intent, an existing goal path, or a source artifact to import.
- Outputs include a goal board health report with native/board reconciliation status and created or repaired board files when the selected mode allows edits.
- Reconcile native goal state with board state. Treat mismatches as PM or Judge work before Worker implementation.
- Ensure exactly one active task unless the user explicitly requested parallel Workers with disjoint `allowed_files`.
- Refuse write-capable work until the active Worker task declares `allowed_files`, `verify`, and `stop_if`.
- If verification is missing, red, stale, blocked, or from a different dirty fingerprint, recover verification before feature work.
- After each task, append a machine-checkable receipt and select the next safe task.
- Mark a goal complete only after a final Judge or PM audit receipt with `decision: complete`; then update the native goal status.
- Apply the context-disposition policy: move important still-valid context to references and index it when meaningful; intentionally discard stale, duplicated, unsafe, superseded, or low-signal text.
- Previous examples included creating a board for Codex config cleanup, continuing `docs/goals/codex-goal-governance/goal.md` after a branch switch, and doctoring goal enablement, worker scope, and Scout/Judge/Worker runtime health before harness execution.
