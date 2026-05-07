# he-spec Artifact Contract

Read when: writing or reviewing a Harness Engineering spec artifact.

Durable spec markdown is written under `.harness/specs/**.md`. Legacy `Specs/`
or docs paths may be read as source evidence, but replacement specs should move
to the Harness artifact root.

## Standard Spec

Frontmatter: `schema_version: 1`, title/type/status/date/origin/risk/depth/UI flags; add Linear fields and `traceability_required: true` for tracked work.

Sections: mode decision, problem, goals, non-goals, Linear contract when tracked, boundary, baseline, domain model, lifecycle, interfaces, invariants, failure/recovery, observability, acceptance matrix with `SA` IDs, Linear traceability, first slice, questions, done, `he-plan` handoff.

## Dedicated UI Spec

Frontmatter: standard fields plus `origin` or `parent_spec`, Linear fields, `traceability_required: true`, and `wcag_level`.

Sections: overview, components, states, tokens, flows, accessibility, responsive behavior, telemetry, `VAC` IDs, Linear traceability, out of scope, questions, decision log.

## Verification

Verify required frontmatter and sections, stable `SA` or `VAC` IDs, tracked-work Linear traceability, and `python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py <spec-path>` for tracked specs.
