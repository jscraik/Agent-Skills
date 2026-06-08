# Pragmatic Programmer Review Contract

Use this reference only when a Harness Engineering stage is doing architecture
review, code review, skill/plugin hardening, or an explicit Pragmatic Programmer
review. Do not load it for routine execution.

## Review Lenses

- DRY: one authoritative place for each policy, enum, route, template, or
  repeated operational rule.
- Orthogonality: entrypoints route, references preserve depth, scripts validate,
  and fixtures remain historical evidence.
- Tracer bullets: every lifecycle stage should have one narrow realistic path
  from user request to selected route, artifact, and validation proof.
- Design by contract: machine-readable contracts should drive templates,
  validators, and tests where values must stay synchronized.
- Automation: repeatable validators should catch stale routing, packaging
  clutter, missing sections, and unrealistic eval cases before release.
- Ruthless testing: tests should include realistic golden fixtures, not only
  synthetic happy paths.
- Broken windows: ignored clutter, repeated warnings, stale snapshots, and
  tolerated false positives should either be fixed or explicitly quarantined.
- Decoupling: avoid hidden dependency between a skill's prose, a reference file,
  and a validator script when a shared contract can carry the rule.

## Finding Format

For each actionable finding include:

- priority: `P1`, `P2`, or `P3`
- evidence path and line when available
- Pragmatic lens
- operational impact
- smallest durable fix
- validation or eval that would prove the fix

## Guardrails

- Do not turn the book lens into process theater.
- Do not quote or summarize the book at length.
- Do not add a new artifact when an existing contract can be extended.
- Prefer subtraction, consolidation, and validation over more prose.
