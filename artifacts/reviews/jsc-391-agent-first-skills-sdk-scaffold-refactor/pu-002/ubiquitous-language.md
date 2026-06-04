# Ubiquitous Language Review: JSC-391 PU-002

## Findings

No terminology blockers.

The ADR and maps use the repo's canonical vocabulary consistently:

- `Agent Skills Kit`
- `ask CLI`
- `Canonical Skill Source`
- `Runtime Projection`
- `Generated Command Handle`
- `Agent Skills package shape`
- `Manifest-declared project skill source`

The key overloaded phrase, "runtime projection", is bounded in the ADR as a
generated surface rather than source. The selected path names also avoid
inventing a second term for existing concepts: `Docs/reference` is treated as
the repo-native canonical reference surface instead of introducing
`Docs/canon`.

## Residual Risk

PU-003 should keep `manifest`, `receipts`, `risk`, `install`, `sandbox`,
`refs`, `evals`, `signing`, `runtime`, and `packaging` as module names in
both prose and machine-readable maps. Renaming them later would make future
agent routing weaker.

WROTE: artifacts/reviews/jsc-391-agent-first-skills-sdk-scaffold-refactor/pu-002/ubiquitous-language.md
