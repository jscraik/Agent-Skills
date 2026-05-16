# Drift Taxonomy

Classify each area as `Improved`, `Neutral`, `Regressed`, or `Unknown`.

- Architecture: hidden coupling, duplicated abstractions, pass-through modules,
  boundary ambiguity, framework leakage, shallow abstraction.
- Routing: duplicated routes, hidden execution paths, unclear skill/plugin
  selection, nondeterminism, lost local discoverability.
- Context: prompt growth, repeated context, unclear ownership, lost compression,
  token-expensive workflows.
- Governance: unenforced process, duplicated policy, review steps without value,
  Linear issue explosion.
- Agent-Native: reduced discoverability, hidden assumptions, missing
  machine-readable contracts, fragile prompt dependency, unsafe autonomy.
- Moat: weaker eval quality, reliability, cognition, speed, governance
  simplicity, or hard-to-copy operating quality.

Any `Regressed` classification must state whether it blocks closure, the
required correction, and whether a follow-up Linear issue is justified.
