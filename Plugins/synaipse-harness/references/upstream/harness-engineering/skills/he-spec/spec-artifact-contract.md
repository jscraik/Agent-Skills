# he-spec Artifact Contract

Read when: writing or reviewing a Harness Engineering spec artifact.

Durable spec markdown is written under `.harness/specs/**.md`. Read legacy
`Specs/` or docs paths as source evidence only; write replacement specs to the
Harness artifact root.

Use the shared Artifact Identity contract in
`Plugins/synaipse-harness/references/upstream/harness-engineering/artifact-routing-contract.md`.
Tracked
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

1. `Command Summary`
2. `Purpose`
3. `Problem Statement`
4. `User / Operator Scenarios`
5. `Goals`
6. `Non-Goals`
7. `Current State / Evidence`
8. `Authority and Scope Boundary`
9. `Proposed Behavior`
10. `Requirements`
   - `Functional Requirements` with stable `FR-*` IDs
   - `Non-Functional Requirements` with stable `NFR-*` IDs when relevant
11. `Interfaces`
12. `Data / Domain Contract`
13. `Enforcement Contract`
14. `Proof and Runtime Boundary`
15. `Coding and Testing Lenses`
16. `Security, Privacy, and Safety`
17. `Accessibility and Operator Ergonomics`
18. `Failure and Recovery`
19. `Validation Plan`
20. `Acceptance Criteria` with stable `SA-*` IDs
21. `Visual References / Diagrams`
22. `Implementation Notes`
23. `Open Questions`
24. `Decision`
25. `Evidence and References`
26. `Appendix A. Harness Metadata / Traceability`
27. `Appendix B. Review Outcomes`
28. `Appendix C. he-plan Handoff`

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
- Use `Plugins/synaipse-harness/references/upstream/harness-engineering/spec-plan-runtime-boundary-contract.md`
  for strict scope, proof, runtime persistence, and coding/testing lens fields.

Scenario and conformance requirements:

- `Problem Statement` must describe the problem from the user, operator, or
  affected stakeholder perspective. Avoid restating the implementation task as
  the problem.
- `Proposed Behavior` must include the user-facing solution before internal
  mechanics. Use a `User-Facing Solution` subsection when the source material
  provides a separate `Solution` statement.
- `User / Operator Scenarios` must describe independently testable journeys,
  ordered by priority when there is more than one user-visible path.
- When source material asks for user stories, preserve them as a numbered
  `User Stories` subsection using `As a <role>, I want <capability>, so that
  <outcome>`. Keep the list extensive enough to cover the feature surface, but
  do not invent unapproved actors, capabilities, or outcomes. Map story groups
  to `FR-*` and `SA-*` IDs rather than leaving the stories as untraceable
  prose.
- Treat `extensive` user stories as coverage, not volume theater. Cover the
  relevant actor roles, happy paths, alternate paths, permissions, data states,
  failure/recovery behavior, accessibility/operator ergonomics, and
  observability/admin workflows when those dimensions apply. If source evidence
  does not support one of those dimensions, mark it out of scope or as a needed
  clarification instead of inventing it.
- Preserve stated intent and implied intent separately. Stated intent comes from
  the user's words, approved tracker text, or approved source artifact. Implied
  intent may be included only when it follows from source evidence; label it as
  inferred or assumption, tie it to the evidence that implies it, and keep it out
  of binding `FR-*` or `SA-*` IDs until approved.
- Data formats, ledgers, manifests, APIs, CLIs, protocols, or generated files
  must include a conformance contract: required fields, optional fields, enum
  values, unknown-field behavior, compatibility/versioning behavior, and error
  handling.
- Services, daemons, state machines, agent runners, and concurrency-heavy
  systems must include domain model, state/lifecycle, observability, recovery,
  and safety invariants.
- UI specs must use `Dedicated UI Spec` instead of forcing visual behavior into
  this standard template.

Authority and scope boundary requirements:

- Every standard spec must include `requested_depth`,
  `approved_execution_boundary`, `downscope_authority`,
  `external_mutation_boundary`, `freshness_required`, and
  `human_acceptance_boundary` under `Authority and Scope Boundary`, or an
  explicit `not_applicable` reason for each field.
- If `requested_depth` is `full_implementation`, the spec must preserve all
  known unfinished surfaces. Downscope is valid only when
  `downscope_authority` records explicit user approval or an approved source
  artifact.
- The section must distinguish live tracker/source truth from local artifacts,
  session summaries, and inferred chat context.

Enforcement Contract requirements:

- Every standard spec must include an `Enforcement Contract` section using the
  Skills SDK apparatus lens:
  `Infrastructure/references/skills-sdk-apparatus-lens.md`.
- The section must explicitly name `essential_decisions`,
  `fillable_gaps`, `guardrails`, `refusal_triggers`,
  `durable_memory`, and `professional_output`.
- Essential decisions are the choices the implementation agent must not invent:
  public API shape, status enums, error taxonomy, persistence model, security
  boundary, package ownership, data schema, or lifecycle semantics.
- Fillable gaps are the low-risk code or documentation areas an agent may
  generate inside those locked decisions.
- Guardrails must be independent checks, preferably commands, schemas, tests,
  evals, doctor/prove gates, or structural audits that fail when the generated
  output crosses the boundary.
- Refusal triggers must describe when the downstream agent stops instead of
  filling a gap, such as a new public API decision, ambiguous data model,
  missing validator, risky migration, or auth/security uncertainty.
- Durable memory must name where transferable feedback is recorded so the same
  correction does not need to be given twice.
- Professional output must name the closeout evidence required before a done
  claim: files changed, exact commands, pass/fail state, blockers, warnings,
  next action, and rollback.

Proof, runtime, and lens requirements:

- `Proof and Runtime Boundary` must include `proof_boundary`,
  `non_proof_sources`, `runtime_state`, `resumption_key`,
  `persistent_artifacts`, `live_state_refresh`, and
  `session_evidence_status` or an explicit `not_applicable` reason. Session or
  collector evidence can support history and correlation, but it cannot prove
  current tests, tracker state, PR state, runtime availability, or
  implementation correctness without fresh evidence.
- `Coding and Testing Lenses` must include compact `coding_lens:` and
  `testing_lens:` blocks. The coding lens names ownership, allowed surfaces,
  public contract/schema/API/CLI compatibility, failure/recovery paths,
  generated-artifact boundaries, and complexity posture. The testing lens names
  observable behavior, source acceptance IDs, prior-art test families, positive
  and negative scenarios, exact validation commands when known, blocked gates,
  and ownership of recovery.
- Missing specialist reviewers do not make the lens optional. If no subagent is
  available, record inline coverage parity and unresolved residual risk.

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
  `Plugins/synaipse-harness/references/upstream/harness-engineering/visual-reference-contract.md`.

Status metadata: every tracked spec output must expose `linear_mutation_status` as
`not_needed`, `confirmation_required`, `blocked`, `created`, `updated`, or
`deferred_to_he-linear-plan`. If live Linear tracking is missing, include
`linear_action_required` with target project, issue type, proposed title,
ready-to-create/update payload, required confirmation, and blocker. A local
`.harness` artifact is not proof that live Linear state exists.

## Decision Placement

`Implementation Notes` is the spec home for durable implementation decisions
that affect behavior, interfaces, schema, state, compatibility, architecture, or
specific interactions. Do not put fragile file paths, task order, helper names,
or code snippets here unless a prototype produced a compact decision artifact
that is more precise than prose, such as a state machine, reducer shape, schema,
or type shape. Trim prototype snippets to the decision-rich part and label them
as prototype-derived.

When the source provides an `Implementation Decisions` list, preserve the
decision intent but normalize it into durable decision categories:
modules/surfaces affected, interfaces/contracts, schema/domain changes,
technical clarifications, architecture decisions, interaction rules, and
prototype-derived decision snippets. Mark implementation-time discoveries as
unknowns instead of making them binding spec facts.

`Validation Plan` is the spec home for testing decisions that define confidence:
external behavior to verify, acceptance evidence, module or surface categories,
test quality rules, and relevant prior-art test families. Prefer statements like
"test externally observable behavior, not implementation detail" over brittle
assertions about private helpers. Concrete test file paths, exact command
sequencing, and implementation-time prior-art lookups belong in `he-plan`.

When the source provides a `Testing Decisions` list, preserve what makes a good
test, which modules or surfaces need evidence, and prior-art test families to
inspect. Keep assertions tied to external behavior and acceptance IDs. If
coverage depends on implementation discovery, mark the exact discovery as a
`he-plan` handoff.

## BLUF Review Surface

For non-trivial durable specs, apply
`Plugins/synaipse-harness/references/upstream/harness-engineering/bluf-review-contract.md`.

Keep the existing spec substance. Add:

- Command Summary with exactly one substantive `BLUF` paragraph, decision
  needed, top risks, and next action. The BLUF must explain the document's job,
  affected system, reader/user value, decision or recommendation, major risk or
  blocker, and next action in one paragraph.
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

Verify required frontmatter and sections, stable `SA` or `VAC` IDs, tracked-work
Linear traceability, and explicit `linear_mutation_status`.

For tracked specs, run:

- `python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py <spec-path>`
- `python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py <spec-path>`

For non-trivial generated specs, also run:

- `python3 Plugins/synaipse-harness/scripts/check_bluf_structure.py <spec-path> --json`
- `python3 Plugins/synaipse-harness/scripts/check_generated_artifact_shape.py <spec-path> --kind spec --json`

These checks validate reader-first structure, IDs, conformance rules,
authority/scope fields, proof/runtime persistence, coding/testing lenses, the
Enforcement Contract, and visual-reference decisions before handoff.
