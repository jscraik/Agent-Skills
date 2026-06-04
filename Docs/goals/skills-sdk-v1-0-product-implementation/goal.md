# Skills SDK V1.0 Product Implementation Governed Goal

## Mode

`GOVERNED_IMPLEMENTATION`

This board is the repo-visible control plane for implementing the bounded
Skills SDK V1.0 product implementation plan.

## Objective

Implement the Skills SDK V1.0 plan one bounded slice at a time while preserving
the JSC-391 scaffold boundary, keeping `./bin/ask` as the repo control plane,
and introducing `skills-sdk` only as the approved product CLI facade.

Each slice must run in its own isolated `codex/` feature branch and worktree
from freshly pulled `main`. Do not continue to the next slice until the current
slice is implemented, reviewed, validated, pushed, passed through the full
`$pr-green-sweep` cycle, merged, and pulled back into the project.

## Canonical Inputs

- Plan: `.harness/plan/2026-06-04-skills-sdk-v1-0-product-implementation-plan.md`
- Spec: `.harness/specs/2026-06-03-skills-sdk-v1-product-spec.md`
- Scaffold evidence: PR #221, `c3ff670f3 feat(skills-sdk): add agent-first scaffold gate (#221)`
- Current linked Linear issue: `JSC-390`
- Required tracker action: create or promote a V1.0 parent issue before implementation, unless explicitly waived

## Native Prompt

```text
/goal Follow docs/goals/skills-sdk-v1-0-product-implementation/goal.md
```

This is a prompt convention, not a native file binding. Codex must read this
file, `state.yaml`, and `receipts.jsonl` before acting.

## Completion Contract

`outcome`

The goal is complete only when PU-001 through PU-007 from the canonical plan are
implemented or honestly blocked, each slice has its own review and delivery
evidence, every slice PR has merged, and local `main` has pulled the merged
state back before the next slice starts.

`verification_surface`

- Goal board validator output.
- Fresh `main` status and pulled head before each slice.
- Per-slice branch and worktree identity.
- Per-slice implementation receipts and implementation notes.
- Browser-visible implementation notes HTML for non-plan decisions, changes, tradeoffs, and deviations.
- Per-slice focused validation commands and outcomes.
- Per-slice review artifacts from `$simplify`, `$improve-codebase-architecture`, `$codex-review`, `$testing`, and `$ubiquitous-language`.
- Per-slice validator artifacts from `@adversarial-reviewer` and `@agent-native-reviewer`.
- Deterministic handoff health report for any missing reviewer artifact.
- `@git-project-triage` artifact before delivery handoff.
- Full `$pr-green-sweep` evidence for PR checks, review threads, merge state, branch/worktree safety, and pulled-main state.

`constraints`

- Govern one plan slice at a time.
- Start every slice from clean, pulled `main`.
- Use an isolated `codex/` feature branch and worktree for each slice.
- Preserve `./bin/ask` as the repo control plane.
- Keep `skills-sdk` as the product CLI facade.
- Do not hand-edit runtime projections, plugin caches, generated mirrors, user/global runtime roots, or global installs.
- Do not implement marketplace, registry, hosted docs publishing, real install writes, real sandbox execution, package signing, or required Tessl unless a later approved slice authorizes it.
- Do not continue after a missing required reviewer artifact unless deterministic blocked-runtime evidence exists and the owner explicitly waives that lane.
- Keep local validation, generated artifacts, review artifacts, PR/CI truth, tracker truth, merge readiness, and pulled-main truth separate.

`boundaries`

- Primary project checkout: `/Users/jamiecraik/dev/agent-skills`
- Per-slice worktrees: `/private/tmp/agent-skills-skills-sdk-v1-0-<slice>`
- Per-slice branches: `codex/skills-sdk-v1-0-<slice>`
- Review artifacts: `artifacts/reviews/skills-sdk-v1-0-product-implementation/<slice>/`
- Implementation notes: `.harness/implementation-notes/2026-06-04-skills-sdk-v1-0-product-implementation-notes.mdx`
- Browser notes: `.harness/implementation-notes/2026-06-04-skills-sdk-v1-0-product-implementation-notes.html`
- Goal board: `docs/goals/skills-sdk-v1-0-product-implementation/`

`iteration_policy`

For each slice: validate the board, refresh `main`, create or reuse only the
slice-owned worktree and branch, implement the bounded files, run focused
validation, run the five required skill reviews, fix accepted findings, run the
two required subagent validators, verify required artifacts, run
`@git-project-triage`, push the PR, complete `$pr-green-sweep`, wait for merge,
pull `main`, update receipts and state, then continue to the next slice.

`blocked_stop_condition`

Stop and classify the blocker if the board validator fails, parent tracker
authority is missing and not waived, `main` is dirty or not pulled, worktree
identity is ambiguous, a required review artifact is missing, a PR is unmerged,
`main` has not pulled the merged slice, or any truth lane cannot be freshly
verified for a delivery claim.

## Slice Map

| Slice | Purpose | Required first proof |
| --- | --- | --- |
| PU-001 | Baseline refresh and parent tracker gate | Clean pulled main, tracker action/waiver, and slice worktree identity |
| PU-002 | Schema spine for manifest, receipt, risk, and preview | Versioned schema fixtures and validation route selected |
| PU-003 | `skills-sdk check` command facade | `./bin/ask` and facade command contract cannot drift |
| PU-004 | Risk tier classifier and sensor placement | Risk and sensor metadata fixtures pass |
| PU-005 | Install preview and lockfile model stub | Preview emits delta without writing live state |
| PU-006 | Honest placeholder lifecycle receipts | Refs/evals/signing/sandbox/explorer placeholders never report pass |
| PU-007 | Evidence packaging, reviews, and closeout | Local, PR, CI, review, tracker, merge, and pulled-main lanes are separate |

## First Action

Validate this board, then run PU-001 as Scout/PM work: refresh local state,
resolve or waive the V1.0 parent tracker requirement, and prepare the first
slice worktree and branch before any implementation edit.
