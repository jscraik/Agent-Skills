# Plan Artifact Contract

Read when writing or validating the saved plan body.

Durable plan markdown is written under `.harness/plan/**.md`. Legacy `Plans/`
or docs paths may be read as source evidence, but replacement plans should move
to the Harness artifact root.

Use the shared Artifact Identity contract in
`Plugins/harness-engineering/references/artifact-routing-contract.md`. Tracked
plans may use dated filenames such as
`.harness/plan/YYYY-MM-DD-architecture-JSC-283-packaged-skill-behavior-assurance-plan.md`,
but the stable chain key is `canonical_slug:
jsc-283-packaged-skill-behavior-assurance`, not the date.

- Use stable IDs for plan units and acceptance items. Never renumber existing IDs during resume, split, deletion, or deepening.
- Keep paths repo-relative inside the artifact. Absolute paths are acceptable in chat links, not in portable plan files.
- Preserve source IDs from Linear, requirements, specs, actors, flows, acceptance examples, and UI validation criteria when supplied.
- Include concrete test scenarios with input, action, and expected outcome. Feature-bearing units need test file paths.
- Keep execution-time unknowns explicit. Do not pretend exact helper names, query shapes, or runtime discoveries are settled.
- For tracked work, include a Linear/spec/plan/PR matrix with PR evidence left pending until delivery.
- For tracked work, run `python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py <plan-path>` and `python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py <plan-path>`.

Full retained notes: `Plugins/harness-engineering/references/he-plan-doctrine.md`.
