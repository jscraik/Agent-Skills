# Drift Taxonomy

Use this taxonomy inside the `Drift Validation` section. Classify each area as
`Improved`, `Neutral`, `Regressed`, or `Unknown`.

## Architecture Drift

Check for hidden coupling, duplicated abstractions, new orchestration layers,
pass-through modules, boundary ambiguity, framework leakage, and shallow
abstraction. A regression blocks closure when it changes an accepted boundary,
adds unowned orchestration, or makes future changes less deterministic.

## Routing Drift

Check for duplicated routes, hidden execution paths, unclear skill/plugin
selection, non-deterministic routing, and loss of local discoverability. A
regression blocks closure when an agent cannot reliably pick the right stage or
when two paths claim the same responsibility without an explicit fold rule.

## Context Drift

Check for increased first-contact context load, prompt growth, repeated context
fragments, unclear context ownership, loss of compression, and token-expensive
workflows. A regression blocks closure when the golden path requires loading
large inactive context or hides required evidence outside a routed reference.

## Governance Drift

Check for process overhead, review steps without enforcement, duplicated
governance files, policy that does not affect execution, and Linear issue
explosion. A regression blocks closure when governance becomes heavier without
changing routing, validation, or completion safety.

## Agent-Native Drift

Check for reduced discoverability, less deterministic execution, worse local
reasoning, hidden assumptions, missing machine-readable contracts, fragile prompt
dependency, and unsafe autonomous execution paths. A regression blocks closure
when a future agent cannot reproduce the intended flow from local artifacts.

Use the agent-native scorecard when the slice changes skills, plugins, CLIs,
agent-facing docs, evals, routing, or generated projections:

```text
Action Parity:
Capability Discovery:
Context Injection:
Shared Workspace / Truth Surface:
Explicit Completion Or Resume Signal:
Status: pass | fail | partial | not-run
Evidence:
Blocks Closure: yes | no
```

Do not make this a separate review stage. Fold it into `Agent-Native Check`,
`Agent Discoverability`, `Routing Determinism`, or `Moat Protection` gates only
when those gates are relevant to the evaluated slice.

## Moat Drift

Check for weakened eval quality, weaker operational reliability, weaker
cognition quality, easy-to-copy complexity, sophistication without
defensibility, slower execution velocity, and weakened governance simplicity. A
regression blocks closure when the work makes the system look more sophisticated
while reducing proof, speed, reliability, or hard-to-copy operating quality.
