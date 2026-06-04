# JSC-391 Agent-First Skills SDK Scaffold Refactor Governed Goal

## Mode

`GOVERNED_IMPLEMENTATION`

This board is the repo-visible control plane for implementing the JSC-391
agent-first Skills SDK scaffold and deep module refactor plan.

## Objective

Implement JSC-391 from the canonical plan while keeping future Skills SDK work
inside accepted agent-first deep modules rather than old CLI glue.

The implementation must proceed one bounded plan unit at a time. Each unit
must preserve current `./bin/ask` compatibility, avoid hand-edited runtime
projections, and leave feature behavior honestly blocked or deferred where the
plan does not authorize implementation.

## Canonical Inputs

- Plan: `.harness/plan/2026-06-03-jsc-391-agent-first-skills-sdk-scaffold-refactor-plan.md`
- Spec: `.harness/specs/2026-06-03-jsc-391-agent-first-skills-sdk-scaffold-refactor-spec.md`
- Linear issue: `JSC-391`
- Feature branch: `codex/jsc-391-governed-implementation`
- Feature worktree: `/private/tmp/agent-skills-jsc-391-governed-implementation`

## Native Prompt

```text
/goal Follow Docs/goals/jsc-391-agent-first-skills-sdk-scaffold-refactor/goal.md
```

This is a prompt convention, not a native file binding. Codex must read this
file, `state.yaml`, and `receipts.jsonl` before acting.

## Completion Contract

`outcome`

JSC-391 is complete only when the Skills SDK scaffold path map, module
contracts, fixtures, executable scaffold tests, compatibility receipts, parent
acceptance crosswalk, and closeout package have been implemented or honestly
blocked according to the plan.

`verification_surface`

- Goal board validator output.
- PU-001 baseline CLI and SDK compatibility receipts.
- PU-002 path-map ADR and parseable module ownership map.
- PU-003 deep module contract and ownership checks.
- PU-004 fixture and placeholder parser checks.
- PU-005 scaffold, routing, dependency, feature-leak, and path ownership tests.
- PU-006 post-change compatibility receipts and parent V1 acceptance crosswalk.
- PU-007 closeout evidence with local validation, generated artifacts, review
  state, GitHub PR and CI state, Linear tracker state, and merge readiness kept
  separate.
- Per-slice review artifacts from `$simplify`,
  `$improve-codebase-architecture`, `$testing`,
  `$ubiquitous-language`, `@agent-native-reviewer`, and
  `@architecture-strategist`.
- `$pr-green-sweep` triage artifacts after review and delivery packaging.

`constraints`

- Work only from the dedicated feature worktree and branch.
- Govern one plan unit at a time.
- Start with Scout verification of PU-001 baseline evidence before Worker
  implementation.
- Use canonical source paths and repo wrappers.
- Do not hand-edit runtime projections, plugin caches, or user/global runtime
  mirrors.
- Do not add user-facing CLI behavior, signing execution, sandbox execution,
  eval execution, install writes, registry behavior, or publish behavior unless
  a later approved plan authorizes it.
- Do not mutate Linear, create or update PRs, merge, or claim CI/review/tracker
  readiness without current evidence and explicit authority for that lane.

`boundaries`

- Target repository: `/private/tmp/agent-skills-jsc-391-governed-implementation`.
- Primary checkout `/Users/jamiecraik/dev/agent-skills` stays clean unless
  explicitly redirected.
- Canonical Agent Skills Kit terms come from `UBIQUITOUS_LANGUAGE.md`.
- Runtime Projection paths such as `.agents/**`, `.skillsets/**`,
  `skills-codex/**`, `Plugins/cache/**`, `~/.agents/skills/**`, and
  `~/.codex/skills/**` are denied as source edits.
- Implementation notes live at
  `.harness/implementation-notes/2026-06-03-jsc-391-agent-first-skills-sdk-scaffold-refactor-notes.mdx`.
- Review artifacts live under
  `artifacts/reviews/jsc-391-agent-first-skills-sdk-scaffold-refactor/<slice>/`.

`iteration_policy`

For each slice: validate the board, refresh the slice boundary, implement only
the governed files, run focused validation, run the four named skill reviews,
fix accepted findings, run the two requested subagent reviews, verify review
artifacts, update receipts and implementation notes, then run `$pr-green-sweep`
for git and PR triage when delivery packaging exists.

`blocked_stop_condition`

Stop and classify the blocker if the board validator fails, baseline evidence
cannot be captured, path ownership is ambiguous, a placeholder implies runtime
readiness, current CLI compatibility regresses without classification, review
artifacts are missing, parent acceptance rows remain blocked while feature
planning is requested, or any truth lane cannot be freshly verified for a
delivery claim.

## Slice Map

| Slice | Purpose | Required first proof |
| --- | --- | --- |
| PU-001 | Capture baseline compatibility and path evidence | Comparable CLI and SDK receipts exist |
| PU-002 | Create path-map ADR and existing SDK inventory | Selected ADR and module ownership map parse |
| PU-003 | Define deep module contracts and minimal landing zones | Required module contracts are documented and parseable |
| PU-004 | Add fixtures, examples, and placeholder contracts | Created fixtures/placeholders parse without false readiness |
| PU-005 | Add executable scaffold, routing, dependency, and path tests | Contract tests fail unsafe paths and feature leaks |
| PU-006 | Capture post-change receipts and parent V1 crosswalk | Baseline/post-change receipts compare by fields |
| PU-007 | Closeout, review, and handoff package | Local proof, PR/CI, review, tracker, artifact, and merge lanes are separate |

## First Action

Validate this board, then run the active Scout task in `state.yaml` to record
PU-001 baseline commands, current worktree state, allowed files, and stop
conditions before any implementation edit.
