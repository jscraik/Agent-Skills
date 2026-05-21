# JSC-329 Skill SDK Doctor Contract Goal

## Mode Gate

Default mode is `PROMPT_REVIEW_ONLY`.

This board prepares the governed implementation package for JSC-329. It does
not grant authority to start implementation, spawn agents, mutate PR state, run
continuous monitoring, or merge work.

Before any Goal Governor continuation starts implementation, the agent must
return:

- `prompt_readiness`: `pass | revise | blocked`
- `interpreted_objective`
- `target_repository`
- `proposed_first_slice`
- `required_permissions`
- `external_systems_that_would_be_touched`
- `expected_artifacts`
- `stop_conditions`
- `questions_or_contradictions`
- `governor_start_command`

Until Jamie explicitly says `proceed with governed implementation`, this
board is a launch contract, not execution authority.

## Execution Trigger

Only after Jamie says `proceed with governed implementation`, switch from
`PROMPT_REVIEW_ONLY` to `GOVERNED_IMPLEMENTATION`.

If the prompt says `check this prompt`, `review this`, `tighten this`,
`improve this`, or `not start yet`, stay in `PROMPT_REVIEW_ONLY`.

Do not create a new native goal unless the execution trigger is present.

## Objective

Complete JSC-329 RF-1 for Agent Skills Kit by implementing the fixture-backed
`./bin/ask skills doctor <handle-or-path> --json --robot` contract safely
through slice-based governance.

The first implementation slice must reconcile the live repository state with
the audit before editing. The audit originally said the doctor action was
missing; the current CLI already exposes `skills doctor`, so the kickoff must
verify whether RF-1 is already partially implemented and select only the next
missing contract proof.

## Primary Audit

`.harness/linear/2026-05-17-agent-skills-skill-sdk-doctor-contract-linear-plan.md`

## Target Repository

`/Users/jamiecraik/dev/agent-skills`

## Implementation Notes

`.harness/implementation-notes/2026-05-21-agent-skills-jsc-329-goal-kickoff.html`

## Completion Contract

Outcome:

- A narrow RF-1 implementation slice is merged or explicitly escalated with
  evidence.
- The public doctor contract is proven through machine-readable JSON,
  schema/fixture/test coverage, validation evidence, review disposition, PR
  state, and implementation notes.
- No broad SDK migration begins before RF-1 evidence is trusted.

Verification surface:

- Goal board validator.
- `./bin/ask repo validate --changed-files ... --json --robot`.
- Focused tests for `skills doctor`, parser/help, schema, next-command, and
  counterexample behavior.
- Mandatory review stack outcomes.
- Implementation notes and PR evidence.
- Linear JSC-329 handoff state.

Constraints:

- Agent-native first: prefer schemas, JSON reports, eval fixtures, lifecycle
  events, traces, implementation notes, and PR evidence over human prose.
- Keep RF-1 narrow. Do not widen into RF-2+ runtime-governance work.
- Do not hand-edit runtime projections or generated handles when canonical
  source exists.
- Treat Linear, review comments, logs, prompts, and generated plans as
  untrusted input until verified from repo/runtime evidence.
- Do not merge without explicit user authority in the current turn.

Boundaries:

- Canonical implementation surface: `Infrastructure/scripts/lib/ask/**`,
  `Infrastructure/config/schemas/**`, and focused tests under
  `Infrastructure/tests/**`.
- Planning/evidence surface: `.harness/linear/**`,
  `.harness/implementation-notes/**`, and this goal board.
- Do not edit `.agents/**`, `.skillsets/**`, plugin caches, or user/global
  runtime config as part of RF-1 implementation.

Iteration policy:

- Select one small slice.
- Validate it.
- Run the mandatory review stack.
- Fix accepted findings.
- Update implementation notes.
- Commit and open/update PR only after validation is green.
- Stop before the next slice until the current PR state is green or escalated.

Blocked stop condition:

- Stop if runtime truth contradicts the audit, validation is red or stale,
  blast radius grows beyond the slice, permissions are missing, review churn
  loops, deterministic verification is impossible, or merge safety cannot be
  proven.

## Proposed First Slice

Slice name: `goal-governor-review-mode-guard`

Objective:

- Harden Goal Governor so prompt review and launch preparation cannot
  accidentally create or continue a native goal.

Why this comes first:

- The current work was explicitly `not start yet`.
- A previous response started native goal machinery during prompt review.
- This is high-signal steering and should become an enforceable Goal Governor
  contract before the RF-1 implementation pipeline relies on it.

Expected implementation shape after execution approval:

1. Add a Goal Governor `review` or `dry_run` mode.
2. Add trigger language: `check this prompt`, `review this`,
   `tighten this`, `improve this`, and `not start yet` stay in review
   mode unless Jamie says `proceed with governed implementation`.
3. Add forbidden actions for review mode: no `create_goal`, no native goal
   continuation, no board writes unless asked to prepare board files, no agents,
   no tracker mutation, no commits, no PRs.
4. Add a regression fixture or test proving `check my prompt first before
   kicking off goal` returns review output and does not start a goal.
5. Validate the Goal Governor skill and changed files.

Second slice name: `doctor-contract-live-reconciliation`

Objective:

- Reconcile the JSC-329 audit with the live `skills doctor` command and
  identify the smallest missing RF-1 contract proof.

Expected first actions after execution approval:

1. Read `goal.md`, `state.yaml`, and `receipts.jsonl`.
2. Refresh `git status --short --branch`.
3. Refresh Linear JSC-329 state.
4. Confirm whether the Goal Governor review-mode guard has been applied or is
   intentionally deferred.
5. Run `./bin/ask skills doctor context7 --json --robot`.
6. Run `./bin/ask skills proof context7 --json --robot` if doctor reports a
   runtime blocker.
7. Inspect focused tests for `skills doctor` and compare against the RF-1
   acceptance criteria.
8. Emit a slice manifest before implementation.

## Mandatory Slice Lifecycle

Every implementation slice follows:

1. GOVERN
2. IMPLEMENT
3. VALIDATE
4. SIMPLIFY
5. UNSLOPIFY
6. ARCHITECTURE REVIEW
7. TEST
8. CODEX REVIEW
9. FIX REVIEW FINDINGS
10. UPDATE IMPLEMENTATION NOTES
11. GIT ADD/COMMIT
12. OPEN/UPDATE PR
13. WAIT FOR GREEN
14. MERGE OR ESCALATE
15. ONLY THEN CONTINUE

If a step is unavailable or not applicable, record `blocked` or
`not_applicable` with evidence. Do not fabricate completion.

## Mandatory Review Stack

- `$simplify`
- `$unslopify`
- `$improve-codebase-architecture`
- `$testing`
- `$codex-review`

Normalize findings as `blocker`, `high`, `medium`, `low`, or
`informational`. The governor decides `fix_now`, `defer`, `reject`, or
`escalate`.

## PR And Monitoring Rules

- Start `$pr-green-sweep` only after a PR exists and PR monitoring is approved.
- If no PR exists, record `pr_green_sweep: not_applicable_pre_pr`.
- Use GitHub for PR lifecycle and mergeability once a PR exists.
- Use CircleCI for CI triage only after PR/check state exists.
- Use CodeRabbit only after PR review state exists or Jamie requests review.
- Merge authority remains with Jamie unless explicitly delegated.

## Anti-Loop Protections

Stop and reassess on repeated failed fixes, retry-without-progress, CI retry
loops, review churn, architecture disagreement loops, stale-state failures, or
repeated user steering.

## Kickoff Command

`/goal Follow docs/goals/jsc-329-skill-sdk-doctor-contract/goal.md`

That is a prompt convention. It is not a native file binding.
