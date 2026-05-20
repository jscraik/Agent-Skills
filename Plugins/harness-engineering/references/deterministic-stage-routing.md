# Deterministic Stage Routing

Use this policy when `he-router` must choose one Harness Engineering stage. Apply the highest-priority matching rule from `routing-map.json`; return exactly one next skill invocation.

## Decision Order

1. Direct valid `he-*` stage mention wins unless the user asks whether it is correct.
2. Multiple named stages or "which stage" questions stay in `he-router`.
3. Heartbeat, monitor, wake-up, poll, until-green/merged/done language routes to `he-heartbeat`.
4. Stale branch cleanup routes through the folded `he-prune-branches` compatibility mode.
5. Implemented branch, PR, merge, review comments, readiness, or go/no-go language routes to review before more work.
6. Eval report, drift validation, closure proof, safe-to-close, Linear completion recommendation, Definition of Done, or `.harness/evals` language routes to `he-eval-report`.
7. Failing tests, errors, regressions, reproduction, or root-cause language routes to `he-fix-bugs` unless test-first is explicit.
8. RED/GREEN, TDD, failing-test-first, or regression-first language routes through folded `he-tdd`.
9. Browser polish, accessibility, visual refinement, or dev-server loops route through folded `he-refine`.
10. Benchmark, tune, experiment, or measured optimization routes to `he-improve`.
11. Prior sessions, archived sessions, session collector, repeated failures, or coverage gaps route to `he-improve`, `he-reconcile`, `he-reinforce`, `he-heartbeat`, `he-work`, or `he-fix-bugs` by intended outcome.
12. Repo intent, architecture review, structural triage, strategic direction, ADR compression, or core invariant compression routes to `he-strategy`.
13. High-leverage architectural migration/reframe program generation routes to `he-reframe`; legacy `he-refactor` prompts route there for compatibility.
14. Linear execution orchestration, milestone/parent issue mapping, Now/Next/Later/Do Not Create classification, or Portfolio Ops routing routes to `he-linear-plan`.
15. Approved phase-loop continuation, 10 minute heartbeat scheduling, phase gates before scoped `git add`, Linear phase updates, collector stale-evidence stop rules, or keeping `he-work` moving until review routes to `he-phase-work`.
16. Harden/deepen an existing spec or plan routes through folded deepen modes.
17. New lifecycle work flows `he-brainstorm` -> `he-strategy` or `he-reframe` when cognition/migration is needed -> `he-linear-plan` when tracker routing is needed -> `he-spec` -> `he-plan` -> `he-work`; approved recurring execution continues through `he-phase-work`.
18. QA intake routes by expected-behavior clarity: clear bugs to `he-fix-bugs`, unclear behavior to `he-brainstorm`/`he-spec`, sequencing to `he-plan`.
19. If still ambiguous, apply `interactive-steering-contract.md` and ask once
    for the missing source artifact or lifecycle state.

## Compatibility Modes

Folded names remain router aliases and modes, not first-class packaged skills:

- `he-ideate` -> `he-brainstorm`
- `he-deepen-spec` -> `he-spec`
- `he-deepen-plan` -> `he-plan`
- `he-tdd` -> `he-work`
- `he-technical-review` / `he-reliability-review` -> `he-code-review`
- `he-refine` -> `he-improve`
- `he-refactor` -> `he-reframe`
- lifecycle state refresh -> `he-reconcile`
- old compound-learning, `he-compound`, or `he-compound-refresh` solved-problem capture -> `he-reinforce`
- `he-prune-branches` -> `he-router` branch-hygiene handoff
- `he-phase-heartbeat` -> `he-phase-work`

## Examples

- "Should we use `he-work` or `he-code-review` next?" -> `he-router`.
- "The branch is implemented, please check it" -> `he-code-review`.
- "Generate the eval and drift validation report before closing the Linear milestone" -> `he-eval-report`.
- "Start by writing the failing regression" -> `he-work mode:tdd`.
- "Wake this thread every 10m until PR 137 is green" -> `he-heartbeat`.
- "Use archived sessions to find HE improvements" -> `he-improve`.
- "Write the repo intent, architecture review, and triage artifacts" -> `he-strategy`.
- "Create a staged migration program for the routing cleanup" -> `he-reframe`.
- "Map the reframe programs into a small Linear execution plan" -> `he-linear-plan`.
- "Keep the approved phase moving, but stop if collector evidence goes stale" -> `he-phase-work`.
