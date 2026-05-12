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

The main body must be reader-first and implementation-grade. Keep Harness
lifecycle metadata, mode decisions, blackboard deltas, review outcomes, and
handoff payloads in frontmatter, compact status blocks, or appendices so the
spec itself reads like a software specification rather than an agent process
transcript.

Use this default section order for standard specs:

1. `Purpose`
2. `Problem Statement`
3. `User / Operator Scenarios`
4. `Goals`
5. `Non-Goals`
6. `Current State / Evidence`
7. `Proposed Behavior`
8. `Requirements`
   - `Functional Requirements` with stable `FR-*` IDs
   - `Non-Functional Requirements` with stable `NFR-*` IDs when relevant
9. `Interfaces`
10. `Data / Domain Contract`
11. `Security, Privacy, and Safety`
12. `Accessibility and Operator Ergonomics`
13. `Failure and Recovery`
14. `Validation Plan`
15. `Acceptance Criteria` with stable `SA-*` IDs
16. `Visual References / Diagrams`
17. `Implementation Notes`
18. `Open Questions`
19. `Decision`
20. `Evidence and References`
21. `Appendix A. Harness Metadata / Traceability`
22. `Appendix B. Review Outcomes`
23. `Appendix C. he-plan Handoff`

For `spec_depth: lite`, keep the same order but collapse adjacent sections when
that does not hide requirements, risk, or validation. For `spec_depth: full`,
expand `Data / Domain Contract`, `Interfaces`, `Failure and Recovery`, and
`Validation Plan` into subsections comparable to a service or format
specification.

Normative language:

- Use `MUST`, `MUST NOT`, `SHOULD`, and `MAY` only for requirements that are
  intended to be binding for implementation or validation.
- Mark unknowns as `[NEEDS CLARIFICATION: ...]` when the answer cannot be
  discovered from repo, tracker, source, or approved external evidence.
- Do not bury binding requirements in explanatory prose; give them stable
  `FR-*`, `NFR-*`, or `SA-*` IDs.
- Do not mix implementation task sequencing into the spec body; put likely
  execution ordering in `Implementation Notes` or the `he-plan` handoff.

Scenario and conformance requirements:

- `User / Operator Scenarios` must describe independently testable journeys,
  ordered by priority when there is more than one user-visible path.
- Data formats, ledgers, manifests, APIs, CLIs, protocols, or generated files
  must include a conformance contract: required fields, optional fields, enum
  values, unknown-field behavior, compatibility/versioning behavior, and error
  handling.
- Services, daemons, state machines, agent runners, and concurrency-heavy
  systems must include domain model, state/lifecycle, observability, recovery,
  and safety invariants.
- UI specs must use `Dedicated UI Spec` instead of forcing visual behavior into
  this standard template.

Visual reference requirements:

- Include at least one visual aid when the spec has a state machine, lifecycle,
  data/domain model, multi-surface workflow, UI flow, service boundary, or
  safety boundary that is easier to understand visually than through prose.
- Prefer Mermaid diagrams, markdown tables, and ASCII maps because they are
  reviewable by humans and parseable by agents.
- Use generated bitmap images only when the spec is UI/design/media-heavy or
  when a human visual reference materially reduces ambiguity. Store review-only
  generated media under `.harness/media/` and include source prompt/sidecar
  evidence when generated media is created.
- Prose requirements remain authoritative when a visual and text disagree.
- Do not add a decorative image or generic infographic to satisfy the visual
  rule; every visual must clarify a concrete behavior, boundary, flow, or
  acceptance decision.
- Apply the shared visual contract for generated media persistence, proof
  rules, and compact not-needed reasons:
  `Plugins/harness-engineering/references/visual-reference-contract.md`.

Status metadata: every tracked spec output must expose `linear_mutation_status` as `not_needed`, `confirmation_required`, `blocked`, `created`, `updated`, or `deferred_to_he-linear-plan`. If live Linear tracking is missing, include `linear_action_required` with target project, issue type, proposed title, ready-to-create/update payload, required confirmation, and blocker. A local `.harness` artifact is not proof that live Linear state exists.

## BLUF Review Surface

For non-trivial durable specs, apply
`Plugins/harness-engineering/references/bluf-review-contract.md`.

Keep the existing spec substance. Add:

- Command Summary with exactly one `BLUF` paragraph, decision needed, top risks,
  and next action.
- No `BLUF-Only Summary`.
- No section-level `BLUF:` labels. Major spec sections should open with clear
  prose, tables, examples, or diagrams, but only the document opening is BLUF.
- Do/Do Not boundaries where scope, requirements, risk, or validation could
  drift.
- No-Fog Gate before handoff.

Small replacement sections may include a brief `Summary:` line when useful, but
do not call it BLUF. Do not duplicate the whole spec into a second simplified
spec.

## Dedicated UI Spec

Frontmatter: standard fields plus `origin` or `parent_spec`, Linear fields, `traceability_required: true`, and `wcag_level`.

Sections: overview, components, states, tokens, flows, accessibility, responsive behavior, telemetry, `VAC` IDs, Linear traceability, out of scope, questions, decision log.

## Verification

Verify required frontmatter and sections, stable `SA` or `VAC` IDs, tracked-work Linear traceability, explicit `linear_mutation_status`, `python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py <spec-path>`, and `python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py <spec-path>` for tracked specs.
