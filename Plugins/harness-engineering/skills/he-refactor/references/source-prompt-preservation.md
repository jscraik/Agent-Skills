# Source Prompt Preservation

This reference preserves the behavior of the original user-proposed Refactor
Program Generation & Architectural Migration prompt.

## Preserved Requirements

- read `.harness/features`, `.harness/review`, `.harness/triage`,
  `.harness/strategy`, `.harness/decisions`, and `.harness/core`
- generate only high-leverage refactor programs under `.harness/refactors/`
- prefer dated Linear filenames for new programs
- avoid cosmetic cleanup, tiny tactical fixes, rewrite fantasies, generic
  best-practice advice, and backlog dumping
- explain structural problem, root cause, operational cost, cognition cost,
  drift risk, moat risk, migration path, rollback path, eval proof, and
  future-agent constraints
- define staged migration phases with risk, validation, rollback, Linear
  mapping, agent-safety, and human-review fields
- map to the JSC Linear operating model without creating Linear objects when
  the request or source artifacts confirm Jamie/JSC-managed work; otherwise
  mark Linear mapping as `needs_human_triage`
- require eval proof before recommending closure
- optimize for incremental execution, reversibility, low blast radius,
  deterministic evolution, and reduced architectural entropy

## Real Output Patterns Observed

Existing repos use phase-rich refactor documents:

- `.harness/refactors/ask-control-plane-decomposition.md`
- `.harness/refactors/packaged-skill-behavior-assurance.md`
- `.harness/refactors/governance-contract-memory-simplification.md`

For new generated refactor programs, prefer:

- `.harness/refactors/YYYY-MM-DD-JSC-###-<refactor-slug>.md`
- `.harness/refactors/YYYY-MM-DD-<repo-name>-<refactor-slug>.md`

## Boundary From Skill Refactoring

`he-refactor` is for repository architecture migration programs. It should not
replace `skill-factory`, `skill-builder`, or a future `skill-refactor` skill for
changing the internals of an individual skill package.

## Prevent Refactor Theater

If the proposed program cannot identify measurable architectural improvement,
eval proof, rollback safety, and downstream execution value, classify it as
`Do Not Create`.
