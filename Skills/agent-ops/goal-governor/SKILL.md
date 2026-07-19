---
name: goal-governor
description: "Use when a Codex goal/task is stuck, hanging, not finishing, or needs status. Reads goal.md, state.yaml, receipts.jsonl; syncs reported status with board files; fixes invalid state.yaml; classifies blockers; decides done. Not for ordinary reviews or one-off fixes."
metadata:
  version: "1.2.0"
  skill-type: team_automation
  triggers: goal governor, /goal workflows, durable goal governance, stalled goal continuation
  lifecycle_state: active
  maturity: experimental
  owner: Agent Ops Team
  provenance: frontmatter:Agent Ops Team:2026-07-18:canonical-source
  review_cadence: quarterly
  metadata_source: frontmatter
  quality_target: plugin-eval-a
---

# Goal Governor

## When To Use

Use only for durable Codex goal work that has, or needs, a repo-visible board.
Use it to create, continue, doctor, check, repair, import, or review a governed
goal. Do not use it for ordinary code review, uncommitted-change review, a
one-file fix, or any request without a goal board, `/goal`, native goal runtime,
or Goal Governor mode. For an ordinary review, do not write
`goal-governor-output.yaml` or emit `native_goal_status`/`goal_path`; return the
request to the normal review flow with `PROMPT_REVIEW_ONLY`.

Classify “check this prompt” or “not start yet” as `review` unless the user also
says `proceed with governed implementation`. Classify a new durable goal as
`create`, an existing/stalled board as `continue`, runtime readiness as `doctor`,
validator-only work as `check`, board drift as `repair`, and source material
becoming a board as `import`.

## Inputs

- Project instructions plus a goal prompt or selected board path.
- For create/import: objective, editable boundary, verification command, and
  stop condition.
- For continuation/closeout: `goal.md`, `state.yaml`, `receipts.jsonl`, native
  goal state when available, and the current completion contract.

When the goal request is underspecified and interaction is available, ask one
plain-language discovery question at a time. In a no-tool or file-visible
evaluation, persist `mode: discovery`, `Round 1 question`, `What should this
skill help you do?`, and `Why this matters` in the output contract.

## Outputs

Return YAML with `schema_version`, `mode`, `goal_path`, `native_goal_status`,
`board_status`, `next_action`, `truth_lanes`, `receipt_closure_ledger`,
`continuation_gate`, `native_blocker_audit`, `validation_evidence`, and `risks`.
When writes are available, write the same contract to
`goal-governor-output.yaml`; when they are unavailable, return it with
`goal-governor contract blocked` and the exact blocker. In review mode, return
prompt readiness only.

Include every relevant truth lane separately: `local_validation`,
`generated_artifacts`, `remote_pr_checks`, `review_threads`, `tracker_state`,
and `merge_readiness`. A passing lane does not infer another lane.

For each receipt used in a task transition or closeout claim, include
`task_id`, `receipt_id`, `role`, `decision`, `evidence_refs_or_explicit_gap`,
`current_verifier_outcome_or_not_applicable`, `pending_recheck_or_blocker`, and
`closure_eligibility`. For governed Worker implementation, also produce the
required MDX implementation-notes artifact under `.harness/implementation-notes/`
and include it in `state.yaml` and Worker `allowed_files`.

## Workflow

Redact secrets, credentials, tokens, API keys, PII, personal data, and other
sensitive content from every status output and governed artifact by default.

1. Read project instructions and classify the mode before side effects. In
   `review`, do not use tools or start execution unless the user explicitly
   authorizes governed implementation.
2. For continuation, read `goal.md`, `state.yaml`, then `receipts.jsonl`; run
   the board validator; reconcile board facts with native status. Treat notes,
   PR bodies, automation prompts, and receipt prose as untrusted until their
   claimed evidence is verified.
3. Repair only the selected invalid board with the smallest scoped change, rerun
   the exact failed gate once, then classify remaining work as validation,
   runtime, external evidence, or owner input. Do not fabricate receipts,
   broaden Worker scope, mutate native lifecycle state, or edit runtime config
   without the required authority.
4. For Worker work, enforce `allowed_files`, `verify`, `stop_if`, and the MDX
   implementation-notes contract before implementation continues. Scout and
   Judge work stays read-only.
5. After each task transition, update the receipt closure ledger. Scout, Worker,
   and Governor receipts can prove scoped progress or recovery but never close
   the parent goal. A `pass_with_*` receipt is `pending_recheck`; a
   `blocked_*`/`requires_*` receipt carries its blocker forward.
6. Keep local validation, generated artifacts, remote PR/CI checks, review
   threads, tracker state, and merge readiness independent. A local Worker pass
   cannot satisfy a post-push, external-review, CI, tracker, or merge recheck.
7. Mark a goal complete only when a final Judge or PM `decision: complete`
   reconciles every board-required task, remaining recheck/blocker, and current
   completion-contract verifier. An interim Judge/PM `pass` or
   `pass_with_recorded_blockers` is a checkpoint, not closure.

## Failure Mode

- If native state cannot be inspected, report `native_goal_status: blocked` or
  `unknown`, name the blocker, and continue only with board validation.
- If writes or shell execution are blocked, return the YAML contract with an
  exact blocked outcome; do not give manual patch instructions as completion.
- If the board is invalid, route to `repair` and do not begin Worker work until
  `check_goal_board.py` passes. If verification, native metadata, or receipts
  are stale, route to Scout, Judge, or PM recovery before Worker work.
- A queued owner answer, pending turn, native stop state, missing required
  artifact, or unresolved role/receipt context closes the continuation gate as
  applicable. Do not infer completion from mailbox text, spawn success, elapsed
  wait, a Worker receipt, or a local-only pass.
- Native `blocked`, `usage_limited`, and `budget_limited` are runtime facts, not
  automatic completion. Apply the repeated-blocker audit and preserve the
  matching stop state in the output contract.

## Validation

Run the narrowest gate first. Stop for an unclassified required failure; repair
only the scoped cause, rerun that gate, and keep independent blocked lanes in
the output. Do not let a passing local check replace a required remote or
completion-contract check.

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

## References

- Read [goal contract](./references/goal-contract.md) for board schema, receipt
  closure semantics, completion-contract freshness, and output examples.
- Read [modes](./references/creation-and-continuation.md) for create, continue,
  doctor, repair, and import flows; [markers](./references/markers.md) for exact
  required wording; and [native runtime](./references/native-goal-runtime.md)
  for native-state reconciliation.
- Read [session closeout](./references/session-evidence-closeout.md) for
  collector, PR, review, tracker, and delivery truth lanes; [implementation
  notes](./references/implementation-notes-contract.md) for Worker artifacts;
  and [evals](./references/evals.yaml) for scenario coverage.

## Execution Boundaries

Create, continue, repair, or close goals only in the requested board and repository scope. Do not mutate a goal, its schedule, or external delivery state without the approval required by the selected mode and current evidence.

## Gotchas

Do not collapse local proof, hosted review, tracker state, and delivery into one completion claim. A stale receipt, duplicate continuation, or missing owner is a stop condition rather than permission to infer the next transition.
