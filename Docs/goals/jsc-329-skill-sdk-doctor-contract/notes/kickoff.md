# JSC-329 Goal Kickoff Notes

## Current State

- The goal board is intentionally paused.
- The continuation gate blocks auto-continue until Jamie explicitly says
  `proceed with governed implementation`.
- A paused native goal already exists in this thread from an earlier false
  start. Do not continue or replace it automatically.
- The audit says `skills doctor` was missing as of 2026-05-20, but the live
  repository now exposes `./bin/ask skills doctor`. Kickoff must reconcile
  that drift before selecting implementation work.

## First Kickoff Question

When Jamie is ready, use:

`/goal Follow docs/goals/jsc-329-skill-sdk-doctor-contract/goal.md`

Then start with read-only reconciliation and emit a slice manifest before any
Worker task.

## Included Goal Governor Hardening

This launch package now includes a Goal Governor pre-slice:

`goal-governor-review-mode-guard`

Purpose:

- Add explicit `review` or `dry_run` mode to Goal Governor.
- Keep `check this prompt`, `review this`, `tighten this`, `improve this`,
  and `not start yet` out of native goal creation or continuation.
- Add regression evidence so prompt-review requests cannot accidentally start
  goal machinery again.

This should run before the JSC-329 RF-1 implementation slice unless Jamie
explicitly defers it.

## Known Evidence

- Primary audit:
  `.harness/linear/2026-05-17-agent-skills-skill-sdk-doctor-contract-linear-plan.md`
- Goal Governor source:
  `Skills/agent-ops/goal-governor/SKILL.md`
- Implementation notes:
  `.harness/implementation-notes/2026-05-21-agent-skills-jsc-329-goal-kickoff.html`
- Linear issue:
  `JSC-329`
- Target repo:
  `/Users/jamiecraik/dev/agent-skills`

## Do Not Start Yet

Do not create a native goal, spawn agents, write implementation code, commit,
push, open a PR, start PR monitoring, or merge until Jamie explicitly approves
governed implementation.
