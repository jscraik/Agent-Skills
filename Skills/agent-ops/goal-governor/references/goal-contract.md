# Goal Contract

Read when creating, validating, repairing, or reviewing a Goal Governor board.

## Native Goal Versus Board

Codex native goals persist an objective for a thread. They do not natively create a repo board, parse a goal file, enforce scoped workers, or require receipts.

Goal Governor adds a repo-visible board that agents must read before acting. The two sources must be reconciled:

- `native_goal_missing`: board exists but native goal is absent.
- `native_goal_paused`: board is active but native goal is paused.
- `native_goal_budget_limited`: native goal exhausted its token budget while board work remains active.
- `native_goal_complete_but_board_active`: native goal says complete while board has active work.
- `board_done_but_native_active`: board is done while native goal is still active.
- `objective_mismatch`: native objective does not point at or match the selected `goal.md`.

Any mismatch is PM or Judge work before Worker implementation.

## Directory Layout

```text
docs/goals/<slug>/
  goal.md
  state.yaml
  receipts.jsonl
  notes/
```

Only these root entries are allowed. Keep supporting bulk evidence in `notes/`.

## state.yaml Schema

```yaml
version: 2
goal:
  slug: example-goal
  status: active
  objective: "Make the Codex goal workflow auditable."
  native_goal_id: goal_opaque_id
  native_objective: "/goal Follow docs/goals/example-goal/goal.md"
  native_status: active
  token_budget: null
  tokens_used: 0
  time_used_seconds: 0
  native_created_at: "2026-05-13T10:00:00Z"
  native_updated_at: "2026-05-13T10:00:00Z"
rules:
  one_active_task: true
  require_fresh_verification: true
  require_final_audit: true
checks:
  dirty_fingerprint: unknown
  last_verification:
    command: null
    outcome: unknown
    checked_at: null
tasks:
  - id: T001
    type: scout
    assignee: Scout
    status: active
    objective: "Find canonical validation commands."
    inputs: []
    constraints:
      - "Read-only."
    expected_output: "Evidence receipt."
    allowed_files: []
    verify: []
    stop_if:
      - "Needs write access."
    receipt_id: null
```

## Task Rules

- Task IDs use `T###`.
- Task type is `scout`, `judge`, `worker`, or `pm`.
- Assignee is `Scout`, `Judge`, `Worker`, or `PM`.
- Status is `queued`, `active`, `blocked`, or `done`.
- Exactly one task is active unless the user explicitly requests parallel Workers and each active Worker has disjoint `allowed_files`.
- Worker tasks require non-empty `allowed_files`, `verify`, and `stop_if`.
- Scout and Judge tasks are read-only; their `allowed_files` should be empty.

## Receipt Rules

Use append-only JSON Lines:

```json
{"id":"R001","task_id":"T001","assignee":"Scout","decision":"pass","summary":"Found validation commands.","changed_files":[],"commands":[{"command":"bash scripts/verify-work.sh --fast","outcome":"pass"}],"created_at":"2026-05-04T12:00:00Z"}
```

Worker receipts require:

- `task_id`
- `summary`
- `changed_files`
- `commands`

Judge receipts require:

- `task_id`
- `decision`
- `summary`
- `evidence`

Goal completion requires a final Judge or PM receipt with:

```json
{"decision":"complete"}
```

## Verification Freshness

Treat verification as stale when:

- No verification command has run.
- Last outcome is not `pass`.
- Dirty fingerprint changed since verification.
- The configured verification command no longer exists.
- The board was resumed after a branch switch or long idle interval.
- Native goal identity, objective, status, budget, token usage, elapsed-time fields, or native timestamps changed since the last reconciliation receipt.
- `/goal edit` or `objective_updated` context changed the live objective and the board has not recorded a reconciliation receipt.

Stale verification routes to Scout, Judge, or PM recovery before Worker implementation.

## Output Example

```yaml
schema_version: 1
mode: continue
goal_path: docs/goals/checkout-latency/goal.md
native_goal_status: active
board_status: blocked
next_action: stop
truth_lanes:
  local_validation: blocked
  generated_artifacts: unknown
  remote_pr_checks: unknown
  review_threads: unknown
  tracker_state: unknown
  merge_readiness: unknown
native_blocker_audit:
  observed_repeated_turns: 1
  required_repeated_turns: 3
  gate_met: false
validation_evidence:
  - command: python3 Skills/agent-ops/goal-governor/scripts/check_goal_board.py docs/goals/checkout-latency
    outcome: blocked
    note: state.yaml invalid
risks:
  - continuation gate closed; do not auto-continue Worker
```
