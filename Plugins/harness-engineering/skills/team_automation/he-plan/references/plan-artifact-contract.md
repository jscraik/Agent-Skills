# Plan Artifact Contract

Read when writing or validating the saved plan body.

- Use stable IDs for plan units and acceptance items. Never renumber existing IDs during resume, split, deletion, or deepening.
- Keep paths repo-relative inside the artifact. Absolute paths are acceptable in chat links, not in portable plan files.
- Preserve source IDs from Linear, requirements, specs, actors, flows, acceptance examples, and UI validation criteria when supplied.
- Include concrete test scenarios with input, action, and expected outcome. Feature-bearing units need test file paths.
- Keep execution-time unknowns explicit. Do not pretend exact helper names, query shapes, or runtime discoveries are settled.
- For tracked work, include a Linear/spec/plan/PR matrix with PR evidence left pending until delivery.

Full retained notes: `Plugins/harness-engineering/references/he-plan-doctrine.md`.
