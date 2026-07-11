# Program design enforcement

## Decision

This repository treats architecture and program design as separate review
axes. Architecture describes component ownership and system boundaries.
Program design describes the decisions inside those boundaries: function
responsibility and abstraction level, data movement, side effects, failure
handling, interface size, state ownership, and test seams.

The repository already had useful program-design guidance in `CODESTYLE.md`
and a narrow `ask-cli-modularity` AST ratchet. The missing durable mechanism
was a named gate that covered the highest-signal low-level smells without
pretending that a syntax tree can judge every abstraction.

## Enforced baseline

`Infrastructure/scripts/validation-and-linting/verify_program_design.py` is a
changed-file ratchet for Python production code under `Infrastructure/`,
`Plugins/`, and `skills-system/` (generated `Plugins/cache/` projections are
excluded). It rejects new or worsened:

- public functions with more than five parameters;
- boolean default arguments used as behavior switches;
- bare or broad `except Exception`/`except BaseException` handlers;
- explicit `global` statements; and
- lower-case module-level mutable state.

The existing `ask-cli-modularity` gate remains responsible for entrypoint
size, changed-file function length, and complexity. The two gates are
intentionally complementary. Existing findings are ratcheted rather than
re-litigated on every unrelated patch; a new exception needs a documented,
time-boxed owner waiver in `PROGRAM_DESIGN_WAIVERS` with owner, rule ID,
ticket, reason, and expiry. Expired or incomplete waiver metadata fails the
gate.

The gate is wired into `Infrastructure/scripts/validate_all_impl.sh` as a
required `program-design` check for `all`, `lint`, and `typecheck` scopes and
as a required input to the selection-gate-severity artifact.

## Review checklist

For each non-trivial implementation change, reviewers should answer these
questions before discussing architecture-level diagrams:

1. Does each changed function have one responsibility and one abstraction
   level, or is a caller now coordinating hidden steps?
2. Did the change add tramp data, a flag argument, a train-wreck access chain,
   feature envy, or a leaky abstraction?
3. Are commands and queries separate, and are side effects explicit in names
   and boundaries?
4. Is error handling separated from the normal path, contextualized for the
   caller, and covered at the boundary where it matters?
5. Is state owned by one module/object rather than a mutable global?
6. Does a focused behavior test prove the public boundary and the important
   negative path?

The first five questions remain human review concerns where deterministic
static checks would be noisy. When a finding repeats, the next ratchet should
be a focused fixture-backed validator or a repository-specific design rule,
not another reminder in prose.

## Source and evidence boundary

The heuristics were cross-checked against the attached *Clean Code: A
Handbook of Agile Software Craftsmanship* PDF at
`/Users/jamiecraik/dev/knowledge-OS/sources/books/Software Architecture & Design/Clean Code A Handbook of Agile Software Craftsmanship.pdf`.
That book is a design lens, not a contemporary universal threshold; the
five-parameter and ratchet limits are repository policy chosen for low-noise
change detection.

The KnowledgeOS `scripts/plan-source-extraction.sh` wrapper was inspected but
not run for this change because it writes a source slice and extraction
worksheet outside this repository. Its output would support source
provenance, not prove code quality or downstream Skills SDK readiness.

## Not proved by this gate

Passing this gate does not prove architectural correctness, API compatibility,
security, runtime readiness, independent review, hosted CI, Tessl registry
status, or publish/install readiness. Those remain separate evidence lanes.
