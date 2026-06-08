# Planning Depth And Synthesis

Read when choosing plan depth, source handling, or a scope checkpoint.

- Lightweight: small, low ambiguity, usually a compact plan with two to four units.
- Standard: normal feature, bug fix, or refactor with decisions, dependencies, validation, and risk notes.
- Deep: cross-cutting, high-risk, strategic, external-contract, migration, security, or unclear implementation work.
- Reclassify lightweight work to standard when research finds external contract surfaces: env vars, exported APIs, CLI flags, CI, shared types, or docs consumed by other systems.
- Use a synthesis checkpoint when the agent has made important inferences. Split it into Stated, Inferred, and Out of scope; route unconfirmed inferred bets to Assumptions in headless artifacts.

Full retained notes: `Plugins/synaipse-harness/references/upstream/harness-engineering/he-plan-doctrine.md`.
