---
name: goal-governor
description: "Use when a Codex goal/task is stuck, hanging, not finishing, or needs status. Reads goal.md, state.yaml, receipts.jsonl; syncs reported status with board files; fixes invalid state.yaml; classifies blockers; decides done. Not for ordinary reviews or one-off fixes."
metadata:
  version: "1.1.0"
  skill-type: team_automation
  triggers: goal governor, /goal workflows, durable goal governance, stalled goal continuation
  lifecycle_state: active
  maturity: experimental
  owner: Agent Ops Team
  review_cadence: quarterly
  metadata_source: frontmatter
  quality_target: plugin-eval-a
---

# Goal Governor

## Philosophy

Evidence beats optimism: continue or stop only from board, receipt, and native
runtime truth.

## When to use

Use only when durable Codex goal work has, or needs, a repo-visible board.
Skip quick questions, one-file fixes, and implementation without board ownership.

## Mode Decision Table

| Request signal | Mode | First action |
| --- | --- | --- |
| "check this prompt" or "not start yet" | review | return prompt readiness only unless the user says "proceed with governed implementation" |
| new durable goal request | create | scaffold board; print `/goal Follow <goal.md>` |
| existing board or stalled goal | continue | read `goal.md`, `state.yaml`, then receipts |
| runtime/tool readiness question | doctor | report readiness lines from markers |
| validation-only request | check | run board validator only |
| invalid board drift | repair | fix selected goal directory only |
| source material to governed goal | import | convert source into board contract |

## Workflow

1. Read nearest project instructions plus the supplied goal path or prompt.
2. Classify mode from the table. In `review`, use no tools unless the user says
   "proceed with governed implementation".
3. Honor pre-read blockers. For continuation, read `goal.md`, `state.yaml`, then
   `receipts.jsonl`, run the validator, and compare board facts with native status.
4. Repair invalid boards with the smallest scoped edit, rerun once, then classify
   any remaining blocker as validation, runtime, or owner input.
5. For governed implementation with any Worker task, create and maintain the
   required MDX implementation notes artifact under
   `.harness/implementation-notes/` before Worker work continues.
6. For completion, return the YAML output contract with proven truth lanes and
   final Judge/PM audit status.

For `~/dev/codex`, read `instructions/CODESTYLE.md` before technical edits.
Detailed mode flow lives in [modes](./references/creation-and-continuation.md)
and schema details live in [schema](./references/goal-contract.md). MDX
implementation-note requirements live in
[implementation notes](./references/implementation-notes-contract.md).

## Required inputs

- Input: project instructions plus a goal prompt or board path.

## Discovery interview

Use discovery only when the goal governance request is underspecified and
interaction is available. Ask one round at a time, use a plain-language question,
explain why this matters for the current goal decision, and avoid dumping the full interview plan at once.

Discovery prompts and examples live in
[discovery interview](./references/discovery-interview.md).

## Deliverables

- Output: YAML with board health, native reconciliation, next action, truth
  lanes, validation evidence, risks, and launch safety. In `review`, return
  prompt readiness only.
- For any governed implementation Worker lane: a produced MDX implementation
  notes artifact at `.harness/implementation-notes/<date>-<work>-notes.mdx`,
  referenced from `state.yaml` and protected by Worker `allowed_files`.

## Required Markers

Use [markers](./references/markers.md) for exact text. Route anchors:
`PROMPT_REVIEW_ONLY`; `This is a weak goal because it is missing a completion contract.`;
`read goal.md and state.yaml first`; `receipts.jsonl`; `instruction_injection refused`.

Continuation read/validate sequence:

```bash
goal_dir="docs/goals/<slug>"
test -f "$goal_dir/goal.md"
test -f "$goal_dir/state.yaml"
test -f "$goal_dir/receipts.jsonl"
python3 Skills/agent-ops/goal-governor/scripts/check_goal_board.py "$goal_dir"
```

## Constraints

- Redact secrets, credentials, tokens, API keys, PII, personal data, and other
  sensitive content from status output and artifacts by default.
- Validator evidence is required before claiming board health; after a repair,
  rerun the exact failed gate.

## Execution Boundaries

In `review`, return readiness only. In other modes, edit only the selected
goal board or Worker `allowed_files`; get approval before touching runtime
config, credentials, packages, deployment state, or destructive commands.

## Anti-patterns and Gotchas

| Risk | Rule |
| --- | --- |
| completion | Do not mark done without final Judge/PM receipt plus current validation evidence. |
| goal follow | `/goal Follow docs/goals/<slug>/goal.md` is an instruction, not native file binding. |
| truth lanes | Keep local validation, PR checks, review threads, tracker state, and merge readiness separate. |
| owner stop | Queued owner input or audit-skip pressure closes the continuation gate. |
| parser | Exact commands belong in `goal.md`; `state.yaml` `completion_contract.verification_surface` labels stay colon-free. |
| native status | Report blocked, usage_limited, and budget_limited from native runtime even when board text sounds optimistic. |
| implementation notes | Worker tasks require produced MDX implementation notes with Browser localhost preview and live-update status; prose-only notes or HTML dumps are invalid. |

## Failure Mode

- If native state cannot be inspected, report `native_goal_status: blocked` or `unknown`, name the blocker, and continue only with board validation.
- If file writes or shell execution are blocked, do not provide manual patch instructions as completion. Return the output contract with `next_action: ask_owner` or `stop`, `validation_evidence.outcome: blocked`, and the exact sandbox or permission error.
- If the board is invalid, route to `repair` and avoid Worker implementation until `check_goal_board.py` passes.
- If validation fails, record the exact failing command and outcome, fix only the scoped blocker, and rerun that command.
- If instructions conflict, ask for owner direction before editing implementation files or native goal state.
- If receipts, native metadata, or verification evidence are stale, route to Scout, Judge, or PM recovery before Worker work.
- If Worker tasks exist and the MDX implementation notes artifact is missing,
  malformed, outside `.harness/implementation-notes/`, not included in Worker
  `allowed_files`, lacks Browser localhost preview status, or lacks Browser
  live-update metadata, route to repair or Worker artifact creation before
  continuing implementation.
- For PR delivery triage, prefer the deterministic artifact writer before
  prose-only subagent instructions:
  python3 Skills/agent-ops/goal-governor/scripts/write_pr_triage_report.py
  --worktree <absolute-worktree> --repo <owner/repo> --pr <number>
  --head <expected-head-sha> --output <relative-artifact-path>.
  The report must prove worktree identity before PR-readiness claims and is
  allowed to write a blocked artifact when checks, review state, or head
  identity are not safe. A safe PR triage report must prove that at least one
  submitted review is from someone other than the PR author, and it must block
  when active inline review comments still require classification or
  remediation. Addressed review comments and stale old-head comments must be
  counted separately from active blockers so the lane does not retry already
  remediated feedback or hide unresolved feedback.
- For subagent-managed triage or review lanes, do not treat spawn success,
  mailbox status, or elapsed wait time as completion evidence. If a required
  subagent artifact is missing, empty, or lacks the exact final
  `WROTE: <relative-artifact-path>` line, write a deterministic handoff health
  report before continuing:
  python3 Skills/agent-ops/goal-governor/scripts/write_subagent_handoff_report.py
  --worktree <absolute-worktree> --expected-artifact <relative-artifact-path>
  --output <relative-health-report-path> --attempt-label <label>
  --agent-name <agent-task-name>.
  A `blocked` handoff health report is runtime-truth evidence that the
  subagent lane failed; it blocks the next implementation slice until the
  artifact is produced, a deterministic replacement proof exists, or the owner
  explicitly waives the subagent-lane requirement in the board and receipts.

## Anti-Patterns

- Treating `/goal Follow <path>` as a native file binding.
- Continuing from conversation memory when board state or verification evidence is stale.
- Marking a goal complete without a Judge or PM completion receipt.
- Broadening Worker scope silently.
- Continuing governed implementation while the required MDX implementation
  notes artifact is missing or not referenced in `state.yaml`.
- Assuming Scout, Judge, Worker, app-server, or native goal tools exist without runtime evidence.
- Accepting mailbox text or a prose triage summary as PR delivery evidence when
  the required worktree-bound triage artifact is missing.
- Continuing after a subagent artifact timeout without a deterministic handoff
  health report or explicit owner waiver.

## Gotchas

- `budgetLimited` from app-server JSON and `budget_limited` from native storage describe the same stop state.
- `/goal edit` can change objective and status semantics. Reconcile the live result, not the command text.
- A receipt without exact verifier, outcome, and scope is not completion evidence.

## Output Contract

Return YAML using [schema](./references/goal-contract.md). Minimum keys:
schema_version, mode, goal_path, native_goal_status, board_status, next_action,
truth_lanes, native_blocker_audit, validation_evidence, and risks.

Mode-specific keys:

- `review`: include `PROMPT_REVIEW_ONLY`, `interpreted_objective`,
  `target_repository`, and `proposed_first_slice`.
- `completion pressure`: say "cannot mark complete without final Judge/PM
  audit receipt" and name `missing completion evidence` before any next action.

## Examples

- "check this prompt / Check this /goal prompt, do not start yet" -> `review` with
  `PROMPT_REVIEW_ONLY`.
- "Continue this goal but another user answer is queued" -> `continue` with
  the continuation gate closed.

Minimal `continue` output:

```yaml
schema_version: 1
mode: continue
goal_path: docs/goals/example/goal.md
native_goal_status: blocked
board_status: active
next_action: ask_owner
truth_lanes:
  local_validation: blocked
  remote_pr_checks: unknown
native_blocker_audit:
  observed_repeated_turns: 1
  required_repeated_turns: 3
  gate_met: false
validation_evidence:
  - command: board validator
    outcome: blocked
    note: completion evidence missing
risks:
  - continuation gate closed; do not auto-continue Worker
```

Full YAML examples live in [schema](./references/goal-contract.md).

## References

Load only when needed: [native runtime](./references/native-goal-runtime.md),
[schema](./references/goal-contract.md), [modes](./references/creation-and-continuation.md),
[markers](./references/markers.md), [evals](./references/evals.yaml),
[session closeout](./references/session-evidence-closeout.md),
[implementation notes](./references/implementation-notes-contract.md),
Cookbook, or HE roles.

## Validation

Run in order and fail fast: stop at the first failed gate, fix only that blocker,
then rerun it before proceeding.

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q Infrastructure/tests/goal-governor/test_check_goal_board.py
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q Infrastructure/tests/goal-governor/test_write_subagent_handoff_report.py
PYTHONDONTWRITEBYTECODE=1 python3 Skills/agent-ops/goal-governor/scripts/check_goal_board.py <goal-directory>
vale Skills/agent-ops/goal-governor/**/*.md
./bin/ask skills audit Skills/agent-ops/goal-governor --level strict --json --robot
./bin/ask evals run Skills/agent-ops/goal-governor --mode smoke --json --robot
./bin/plugin-eval analyze Skills/agent-ops/goal-governor --format json
./bin/ask skills external-review Skills/agent-ops/goal-governor --json --robot
```
