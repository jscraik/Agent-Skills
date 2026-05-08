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
11. Prior sessions, archived sessions, session collector, repeated failures, or coverage gaps route to `he-improve`, `he-compound`, `he-heartbeat`, `he-work`, or `he-fix-bugs` by intended outcome.
12. Repo intent, architecture review, structural triage, strategic direction, ADR compression, or core invariant compression routes to `he-strategy`.
13. High-leverage architectural migration/refactor program generation routes to `he-refactor`.
14. Linear execution orchestration, milestone/parent issue mapping, Now/Next/Later/Do Not Create classification, or Portfolio Ops routing routes to `he-linear-plan`.
15. Harden/deepen an existing spec or plan routes through folded deepen modes.
16. New lifecycle work flows `he-brainstorm` -> `he-strategy` or `he-refactor` when cognition/migration is needed -> `he-linear-plan` when tracker routing is needed -> `he-spec` -> `he-plan` -> `he-work`.
17. QA intake routes by expected-behavior clarity: clear bugs to `he-fix-bugs`, unclear behavior to `he-brainstorm`/`he-spec`, sequencing to `he-plan`.
18. If still ambiguous, apply `interactive-steering-contract.md` and ask once
    for the missing source artifact or lifecycle state.

## Compatibility Modes

Folded names remain router aliases and modes, not first-class packaged skills:

- `he-ideate` -> `he-brainstorm`
- `he-deepen-spec` -> `he-spec`
- `he-deepen-plan` -> `he-plan`
- `he-tdd` -> `he-work`
- `he-technical-review` / `he-reliability-review` -> `he-code-review`
- `he-refine` -> `he-improve`
- `he-compound-refresh` -> `he-compound`
- `he-prune-branches` -> `he-router` branch-hygiene handoff

## Examples

- "Should we use `he-work` or `he-code-review` next?" -> `he-router`.
- "The branch is implemented, please check it" -> `he-code-review`.
- "Generate the eval and drift validation report before closing the Linear milestone" -> `he-eval-report`.
- "Start by writing the failing regression" -> `he-work mode:tdd`.
- "Wake this thread every 10m until PR 137 is green" -> `he-heartbeat`.
- "Use archived sessions to find HE improvements" -> `he-improve`.
- "Write the repo intent, architecture review, and triage artifacts" -> `he-strategy`.
- "Create a staged migration program for the routing cleanup" -> `he-refactor`.
- "Map the refactor programs into a small Linear execution plan" -> `he-linear-plan`.
