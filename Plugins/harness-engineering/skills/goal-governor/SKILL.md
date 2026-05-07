---
name: goal-governor
description: Create, continue, and audit Codex persistent-goal work with repo-visible goal boards, native goal reconciliation, scoped agent tasks, receipts, and verification freshness gates. Use when a user wants durable `/goal` workflows, long-running Codex goal governance, or safe continuation of stalled goal work.
metadata:
  skill-type: team_automation
  triggers:
    - goal governor
    - /goal workflows
    - goal workflows
    - durable goal governance
  lifecycle_state: active
  maturity: experimental
  owner: Harness Engineering Team
  review_cadence: quarterly
  metadata_source: frontmatter
  quality_target: plugin-eval-a
---

# Goal Governor

## Philosophy

Use this skill to turn Codex's native `/goal` feature into an auditable operating loop. Native goals persist a thread objective and runtime status; this skill governs the repo-visible plan, active task, receipts, and completion audit.

Treat goal work as a state machine. Know the native status, board status, active task, write scope, and required evidence before continuing.

## When To Use

Use when the user asks to create, continue, repair, audit, or operationalize a long-running Codex goal, especially when work is broad, stale, blocked, multi-agent, high-risk, or likely to span sessions.

Do not use for ordinary one-file fixes, quick questions, or implementation tasks where the user has not asked for durable `/goal` governance.

## Modes

- `create`: scaffold a goal board, verify native goal support, and print `/goal Follow <goal.md>`.
- `continue`: read native goal state and the board, reconcile drift, and select the next safe action before implementation.
- `doctor`: check installation, Codex goal enablement, objective fit, agent runtime depth, board validity, and verification freshness.
- `check`: validate a goal board and receipts without changing files.
- `repair`: propose or apply low-risk board repairs only after reporting the exact drift.
- `import`: convert an existing spec, plan, or issue into a goal board without losing its original source path.

## Required Inputs

- Target repository path.
- Goal intent, existing goal path, or artifact to import.
- Editable boundary for any write-capable task.
- Verification command contract from the target repo.
- Stop condition, such as owner input, red validation, scope expansion, or completion audit.

## Outputs

- Board health report with native/board reconciliation.
- Created or repaired board files when the mode allows edits.
- Next safe action classification.
- Machine-checkable validation evidence.
- `blackboard_delta` and `slack_policy` for long-running continuation.
- Residual risks or owner-input blockers.

## Workflow

1. Read the nearest project instructions first. In `~/dev/codex`, read `instructions/CODESTYLE.md` when present before technical edits.
2. Run `doctor` checks before `create` or `continue`:
   - `[features].goals = true` is configured or the user accepts a blocked setup.
   - Native objective is non-empty and no more than 4,000 characters; keep bulk instructions in `goal.md`.
   - Agent config supports the intended delegation depth; for Jamie's Codex harness, require `max_depth >= 2`.
   - The selected validation commands exist and are repo-canonical.
   - Existing board files pass `python3 scripts/check_goal_board.py <goal-directory>`.
3. Reconcile native and board state, including `active`, `paused`, `budgetLimited`, and `complete` (normalize native `budgetLimited` to output `budget_limited`).
4. Treat token budget, tokens used, elapsed seconds, lifecycle updates, and budget-limited transitions as evidence, not completion proof.
5. Ensure exactly one active task unless the user explicitly requested parallel Workers with disjoint `allowed_files`.
6. Refuse write-capable work until the active Worker task declares `allowed_files`, `verify`, and `stop_if`.
7. If verification is missing, red, stale, blocked, or from a different dirty fingerprint, recover verification before feature work.
8. After each task, append a machine-checkable receipt and select the next safe task.
9. Mark a goal complete only after a final Judge or PM audit receipt with `decision: complete`; then update the native goal status.

## Goal Directory

Default layout:

```text
docs/goals/<slug>/
  goal.md
  state.yaml
  receipts.jsonl
  notes/
```

`state.yaml` owns current state. `goal.md` explains intent. `receipts.jsonl` is append-only evidence. `notes/` is for bulky supporting material only.

## Safety Rules

- `/goal Follow docs/goals/<slug>/goal.md` is a prompt convention, not a native file binding. Always read `goal.md` and `state.yaml` before acting.
- Native `/goal` objective text is validated by Codex. Long plans belong in repo files.
- Redact secrets, credentials, tokens, private keys, and sensitive personal data by default in receipts, notes, examples, and chat output.
- Do not edit implementation files until board health, native-goal reconciliation, and verification freshness are known.
- Do not write outside `allowed_files` for an active Worker task.
- Do not treat generated templates as proof that agents are installed; verify runtime config and role availability.
- Do not install or mutate `~/.codex` directly unless the user asks for a direct runtime install. Prefer canonical repo projection paths.
- If native goal state and board state conflict, stop implementation and classify the mismatch.
- Do not remove important context for budget trimming; move deep context to references instead of deleting it.

## Anti-Patterns

- Treating `/goal Follow <path>` as a native file binding instead of a prompt convention.
- Starting Worker implementation before reading `goal.md`, `state.yaml`, and recent receipts.
- Marking a goal complete without a Judge or PM completion receipt.
- Broadening Worker scope silently when files outside `allowed_files` are needed.
- Installing directly into `~/.codex` when the project has a canonical projection layer.
- Continuing from conversation memory when board state or verification evidence is stale.

## Gotchas

- Native `/goal` state and repo-visible board state can drift. Reconcile both before choosing Worker work.
- A receipt is only useful when it names the exact verifier and outcome; vague "tested" notes are not completion evidence.
- `budgetLimited` is a native stop/steering state that maps to normalized output status `budget_limited`. Classify scope, verification, and owner decision before Worker work.
- Delegation still follows the shared HE subagent call contract; do not assume Scout, Judge, or Worker roles exist until runtime config proves they are available.

## Output Contract

Return:

```yaml
schema_version: 1
mode: create|continue|doctor|check|repair|import
goal_path: path-or-null
native_goal_status: active|paused|budget_limited|complete|missing|unknown|blocked
board_status: active|paused|done|blocked|invalid|missing
next_action: continue|scout|judge|worker|repair|ask_owner|stop
validation_evidence:
  - command: exact command
    outcome: pass|fail|blocked
    note: short evidence
risks:
  - short residual risk
```

## Progressive Disclosure

- Read [references/deferred-context-index.md](../../references/deferred-context-index.md) when preserving or recovering context moved out of active skill text.
- Read [references/subagent-call-contract.md](../../references/subagent-call-contract.md) before delegating Scout, Judge, PM, or Worker tasks.
- Read [references/native-goal-runtime.md](./references/native-goal-runtime.md) when reconciling with current `~/dev/codex` native goal behavior.
- Read [references/goal-contract.md](./references/goal-contract.md) when creating or validating `goal.md`, `state.yaml`, or `receipts.jsonl`.
- Read [references/creation-and-continuation.md](./references/creation-and-continuation.md) when choosing create, continue, repair, or import behavior.
- Read [references/evals.yaml](./references/evals.yaml) when testing this skill with binary trigger and behavior checks.
- Read [../../references/pragmatic-operating-invariants.md](../../references/pragmatic-operating-invariants.md) when continuation exposes repeated drift, stale state, or broken-window cleanup.
- Read [../../references/xp-operating-contract.md](../../references/xp-operating-contract.md) when emitting blackboard deltas, slack policy, red signals, or repeated-failure learning.

## Validation

Validate the skill package:

```bash
python3 scripts/check_goal_board.py <goal-directory>
./bin/ask skills audit <skill-directory> --level strict --robot
```

Fail fast: stop at the first failed gate, fix the blocker, and rerun the exact failed command before proceeding.

When changing this skill, use an Autoresearch-style loop: baseline first, patch one hypothesis, run the smallest verifier and guard, then keep or discard with evidence.

## Examples

- "Create a `/goal` board for `JSC-190` in `coding-harness`; tomorrow's run must start with `bash scripts/run-harness-setup-checks.sh`."
- "Continue `docs/goals/codex-goal-governance/goal.md`; I moved from `main` to `feature/jscraik-agent-first-golden-path-spec-plan`, so verify before editing."
- "Doctor the overnight Codex config cleanup goal before it runs; check native goals, worker scope, and Scout/Judge/Worker availability."
