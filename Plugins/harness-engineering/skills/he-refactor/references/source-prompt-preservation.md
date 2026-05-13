# Source Prompt Preservation

This reference preserves the behavior of the original user-proposed Refactor
Program Generation & Architectural Migration prompt, plus the adjacent
architecture-evolution compression prompts that now shape `he-refactor`
routing.

When a refactor candidate comes from an HE strategy/review that was compared
against an original prompt method, also load
`Plugins/harness-engineering/references/source-prompt-coverage-contract.md`.
The refactor program must inherit upstream evidence depth and coverage gaps
instead of converting sampled cognition into repo-wide migration authority.

## Preserved Prompt Families

`he-refactor` owns deterministic architecture-evolution programs. It must not
become a generic review, roadmap, or skill-package refactoring prompt. Preserve
these lane boundaries:

| Prompt family | `he-refactor` responsibility |
| --- | --- |
| Strategic Compression & Direction | Treat `.harness/strategy/**` as upstream input. If strategy is missing and required, route formal strategy authoring to `he-strategy` or mark `Blocked: strategy missing`; `he-refactor` may produce only a transient strategic intake summary during explicit combined workflows. |
| Refactor Program Generation & Architectural Migration | Own this lane. Generate only high-leverage, evidence-backed, rollback-safe migration programs in `.harness/refactors/**`. |
| Architectural Decision Compression | Generate compact ADR candidates only when a selected migration needs durable architectural memory. Return `Do Not Create` for tactical, reversible, or low-impact decisions. |
| Core Knowledge Compression & Architectural Invariants | Generate compact invariant candidates only when a selected migration needs durable future-agent operating rules. Exclude tactical detail, onboarding prose, and generic principles. |

## Preserved Refactor Requirements

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
- preserve upstream source-prompt coverage status, not-inspected surfaces,
  repo-specific drift signals, authority limits, and downstream confidence

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

If upstream source-prompt coverage is sampled, partial, weak, inferred, or
unknown, generate only a scope-limited refactor program or return `Blocked`
pending deeper strategy/review refresh. Do not claim the selected migration is
the highest repo-wide priority unless the source prompt coverage supports that
claim.
