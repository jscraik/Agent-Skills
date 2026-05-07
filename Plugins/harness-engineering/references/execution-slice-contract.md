# Execution Slice Contract

Use this when `he-spec`, `he-plan`, or `he-work` translates Harness artifacts into implementation work. The selected execution slice is the authority; surrounding review, strategy, and feature material is context until admitted by that slice.

## Authority Order

1. Current user request when it explicitly selects one bounded slice.
2. `.harness/linear/<repo-name>-linear-plan.md` for the approved Linear destination, milestone, parent issue, dependencies, priority, labels, and agent/human execution route.
3. `.harness/refactors/<selected-refactor>.md` when the selected route is a refactor or migration.
4. `.harness/decisions/*.md` for architectural decisions and tradeoffs the slice must not violate.
5. `.harness/core/*.md` for invariants, routing rules, execution rules, moat constraints, and other non-negotiables.
6. `.harness/brainstorm/*.md` for source context that explains intent without overriding the approved slice.

The spec stage must consume one approved execution slice, not the whole review stack. A valid slice is exactly one of:

- one milestone
- one parent issue
- one refactor phase
- one execution slice

## Required Inputs

For tracked implementation, the stage must resolve the selected Linear slice before writing requirements:

- Linear project
- Linear milestone
- Linear parent issue
- Linear sub-issues when present
- labels
- priority
- dependencies
- agent/human execution route

For refactor or migration work, the selected `.harness/refactors/<selected-refactor>.md` is required and must provide safe migration path, desired end state, anti-regression constraints, and rollback rules.

## Secondary Inputs

Use these only for evidence, context, or risk notes:

- `.harness/strategy/*.md`
- `.harness/triage/*.md`
- `.harness/review/*.md`
- `.harness/features/*.md`

Secondary inputs must not create implementation requirements by themselves. If secondary material conflicts with the approved Linear/refactor slice, record it as evidence or a blocker rather than expanding scope.

## Stop Rules

Stop and return the smallest recovery step when:

- no selected milestone, parent issue, refactor phase, or execution slice can be identified
- tracked implementation lacks `.harness/linear/<repo-name>-linear-plan.md` or equivalent explicit Linear fields
- a refactor or migration route lacks the selected `.harness/refactors/<selected-refactor>.md`
- `.harness/decisions/*.md` or `.harness/core/*.md` conflict with the selected slice
- secondary review, strategy, triage, or feature material attempts to drive implementation directly

## Output Boundary

`he-spec` outputs a bounded implementation spec for the selected slice. It must include:

- selected slice type and source path
- approved Linear routing fields or blocker
- refactor source when applicable
- decision/core invariants that constrain the slice
- explicit `In Scope` and `Out of Scope` sections
- acceptance IDs and validation tied only to the selected slice
- handoff to implementation, eval, or drift validation

Do not write a giant programme spec. If the work is larger than one slice, route back to Linear/refactor planning before specifying implementation.
