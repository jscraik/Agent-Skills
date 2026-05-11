# he-spec Artifact Contract

Read when: writing or reviewing a Harness Engineering spec artifact.

Durable spec markdown is written under `.harness/specs/**.md`. Read legacy
`Specs/` or docs paths as source evidence only; write replacement specs to the
Harness artifact root.

Use the shared Artifact Identity contract in
`Plugins/harness-engineering/references/artifact-routing-contract.md`. Tracked
specs may use dated and issue-prefixed filenames such as
`.harness/specs/YYYY-MM-DD-jsc-283-packaged-skill-behavior-assurance-spec.md`;
the stable chain key is `canonical_slug:
jsc-283-packaged-skill-behavior-assurance`.

## Standard Spec

Frontmatter: `schema_version: 1`, `artifact_id`, `artifact_type`, `canonical_slug`, title/status/date/origin/risk/depth/UI flags; add Linear fields and `traceability_required: true` for tracked work.

Sections: mode decision, problem, goals, non-goals, Linear contract when tracked, boundary, baseline, domain model, lifecycle, interfaces, invariants, failure/recovery, observability, acceptance matrix with `SA` IDs, Linear traceability, first slice, questions, done, `he-plan` handoff.

Status metadata: every tracked spec output must expose `linear_mutation_status` as `not_needed`, `confirmation_required`, `blocked`, `created`, `updated`, or `deferred_to_he-linear-plan`. If live Linear tracking is missing, include `linear_action_required` with target project, issue type, proposed title, ready-to-create/update payload, required confirmation, and blocker. A local `.harness` artifact is not proof that live Linear state exists.

## Dedicated UI Spec

Frontmatter: standard fields plus `origin` or `parent_spec`, Linear fields, `traceability_required: true`, and `wcag_level`.

Sections: overview, components, states, tokens, flows, accessibility, responsive behavior, telemetry, `VAC` IDs, Linear traceability, out of scope, questions, decision log.

## Verification

Verify required frontmatter and sections, stable `SA` or `VAC` IDs, tracked-work Linear traceability, explicit `linear_mutation_status`, `python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py <spec-path>`, and `python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py <spec-path>` for tracked specs.
