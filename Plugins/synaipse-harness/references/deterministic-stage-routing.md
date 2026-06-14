# Deterministic Stage Routing

Use this policy when `sy-reframe` must choose one SynAIpse Harness stage. Apply the highest-priority matching rule from `routing-map.json`; return exactly one next skill invocation.

## Decision Order

1. Direct valid `sy-*` stage mention wins unless the user asks whether it is correct.
2. Multiple named stages or "which stage" questions stay in `sy-reframe`.
3. Heartbeat, monitor, wake-up, poll, until-green/merged/done language routes to `sy-reconcile`.
4. Stale branch cleanup routes through the folded `sy-prune-branches` compatibility mode.
5. Implemented branch, PR, merge, review comments, readiness, or go/no-go language routes to review before more work.
6. Eval report, drift validation, closure proof, safe-to-close, Linear completion recommendation, Definition of Done, or `.harness/evals` language routes to `sy-eval-report`.
7. Failing tests, errors, regressions, reproduction, or root-cause language routes to `sy-review` unless test-first is explicit.
8. RED/GREEN, TDD, failing-test-first, or regression-first language routes through folded `sy-tdd`.
9. Browser polish, accessibility, visual refinement, or dev-server loops route through folded `sy-refine`.
10. Benchmark, tune, experiment, or measured optimization routes to `sy-review`.
11. Prior sessions, archived sessions, session collector, repeated failures, or coverage gaps route by blocker taxonomy and freshness before intended outcome:
    - stale collector, stale repo head, stale tracker, or missing live-state refresh -> `sy-reconcile` or `sy-work` with a blocked freshness handoff;
    - test failure, lint failure, runtime error, reproduction, or regression -> `sy-review` unless failing-test-first is explicit;
    - missing validation, weak proof, false completion, or closure uncertainty -> `sy-eval-report`;
    - missing durable guardrail after repeated steering -> `sy-reinforce`;
    - approved implementation repair with current plan/spec boundary -> `sy-work`;
    - scheduled continuation or until-green/merged/done monitoring -> `sy-reconcile`;
    - broad pattern improvement without a selected implementation slice -> `sy-review`.
    If multiple bullets match, choose the first bullet with fresh evidence. If freshness is unknown, block for one live refresh step instead of guessing.
12. Repo intent, architecture review, structural triage, strategic direction, ADR compression, or core invariant compression routes to `sy-reframe`.
13. High-leverage architectural migration/reframe program generation routes to `sy-reframe`; legacy `sy-refactor` prompts route there for compatibility.
14. Linear execution orchestration, milestone/parent issue mapping, Now/Next/Later/Do Not Create classification, or Portfolio Ops routing routes to `sy-tracker-plan`.
15. Approved phase-loop continuation, 10 minute heartbeat scheduling, phase gates before scoped `git add`, Linear phase updates, collector stale-evidence stop rules, or keeping `sy-work` moving until review routes to `sy-work`.
16. Harden/deepen an existing spec or plan routes through folded deepen modes.
17. New lifecycle work follows the canonical stage order: `sy-reframe` -> `sy-reframe` -> `sy-brainstorm` -> `sy-trace-plan` -> `sy-tracker-plan` -> `sy-slice-spec` -> `sy-execution-plan` -> `sy-work` -> `sy-review` -> `sy-eval-report` -> `sy-reconcile` -> `sy-reinforce`.
18. QA intake routes by expected-behavior clarity: clear bugs to `sy-review`, unclear behavior to `sy-brainstorm`/`sy-slice-spec`, sequencing to `sy-execution-plan`.
19. If still ambiguous, apply `interactive-steering-contract.md` and ask once
    for the missing source artifact or lifecycle state.

## Compatibility Modes

Folded names remain router aliases and modes, not first-class packaged skills:

- `sy-ideate` -> `sy-brainstorm`
- `sy-deepen-spec` -> `sy-slice-spec`
- `sy-execution-plan` -> `sy-execution-plan`
- `sy-tdd` -> `sy-work`
- `sy-technical-review` / `sy-reliability-review` -> `sy-review`
- `sy-refine` -> `sy-review`
- `sy-refactor` -> `sy-reframe`
- lifecycle state refresh -> `sy-reconcile`
- old compound-learning, `sy-compound`, or `sy-compound-refresh` solved-problem capture -> `sy-reinforce`
- `sy-prune-branches` -> `sy-reframe` branch-hygiene handoff
- `sy-work` -> `sy-work`

## Examples

- "Should we use `sy-work` or `sy-review` next?" -> `sy-reframe`.
- "The branch is implemented, please check it" -> `sy-review`.
- "Generate the eval and drift validation report before closing the Linear milestone" -> `sy-eval-report`.
- "Start by writing the failing regression" -> `sy-work mode:tdd`.
- "Wake this thread every 10m until PR 137 is green" -> `sy-reconcile`.
- "Use archived sessions to find SynAIpse improvements" -> `sy-review`.
- "Write the repo intent, architecture review, and triage artifacts" -> `sy-reframe`.
- "Create a staged migration program for the routing cleanup" -> `sy-reframe`.
- "Map the reframe programs into a small Linear execution plan" -> `sy-tracker-plan`.
- "Keep the approved phase moving, but stop if collector evidence goes stale" -> `sy-work`.
