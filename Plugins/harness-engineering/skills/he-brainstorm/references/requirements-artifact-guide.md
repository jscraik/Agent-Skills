# Requirements Artifact Guide

Load full doctrine when needed: `Infrastructure/references/harness-engineering/he-brainstorm-doctrine.md`.

Default path: `.harness/brainstorm/YYYY-MM-DD-<topic>-requirements.md`.
For explicit folded `he-ideate` mode, use
`.harness/ideate/YYYY-MM-DD-<topic>-options.md`. Use repo-relative paths inside
artifacts.

Frontmatter: `schema_version`, `source: he-brainstorm`, `created`, `mode`, `scope_tier`, `spec_required`, `risk_level`, `complexity`, `next_stage`.

Sections: `Summary`, `Problem Frame`, `Requirements`, `Success Criteria`, `Key Decisions`, `Scope Boundaries`, `Dependencies and Assumptions`, `Resolve Before Planning`, `Deferred to Planning`, `Next Stage`.

Use `R`, `A`, `F`, and `AE` IDs when later traceability matters. Lightweight work may omit IDs.

Before writing interactively, present `Stated`, `Inferred`, and `Out of scope`. Write only after explicit confirmation. In headless mode, put unconfirmed `Inferred` bets in `## Assumptions`, never requirements or key decisions.
