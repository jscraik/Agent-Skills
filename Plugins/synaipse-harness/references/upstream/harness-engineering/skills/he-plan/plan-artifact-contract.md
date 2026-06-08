# Plan Artifact Contract

Read when writing or validating the saved plan body.

Durable plan markdown is written under `.harness/plan/**.md`. Legacy `Plans/`
or docs paths may be read as source evidence, but replacement plans should move
to the Harness artifact root.

Use the shared Artifact Identity contract in
`Plugins/synaipse-harness/references/upstream/harness-engineering/artifact-routing-contract.md`.
Tracked
plans may use dated filenames such as
`.harness/plan/YYYY-MM-DD-architecture-JSC-283-packaged-skill-behavior-assurance-plan.md`,
but the stable chain key is `canonical_slug:
jsc-283-packaged-skill-behavior-assurance`, not the date.

- Use stable IDs for plan units and acceptance items. Never renumber existing IDs during resume, split, deletion, or deepening.
- Keep paths repo-relative inside the artifact. Absolute paths are acceptable in chat links, not in portable plan files.
- Preserve source IDs from Linear, requirements, specs, actors, flows, acceptance examples, and UI validation criteria when supplied.
- Include concrete test scenarios with input, action, and expected outcome. Feature-bearing units need test file paths.
- Keep execution-time unknowns explicit. Do not pretend exact helper names, query shapes, or runtime discoveries are settled.
- Use `Plugins/synaipse-harness/references/upstream/harness-engineering/spec-plan-runtime-boundary-contract.md` for strict scope/downscope authority, runtime persistence, proof boundaries, and coding/testing lens fields.
- For tracked work, include a Linear/spec/plan/PR matrix with PR evidence left pending until delivery.
- For tracked work, run `python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py <plan-path>` and `python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py <plan-path>`.
- For non-trivial generated plans, also run `python3 Plugins/synaipse-harness/scripts/check_bluf_structure.py <plan-path> --json` and `python3 Plugins/synaipse-harness/scripts/check_generated_artifact_shape.py <plan-path> --kind plan --json` so the opening BLUF, execution-first body, Enforcement Contract, plan units, source mapping, rollback, handoff, and visual-reference decision are validated before handoff.

## Execution-First Plan Template

The main body must be an execution contract, not a visible transcript of the
Harness planning process. Keep mode decisions, blackboard deltas, confidence
review detail, and mutation payloads in frontmatter, compact status blocks, or
appendices unless they directly change the execution plan.

Use this default section order for standard durable plans:

1. `Command Summary`
2. `Objective`
3. `Source Contract`
4. `Scope and Boundaries`
5. `Authority and Scope Boundary`
6. `Current State / Evidence`
7. `Implementation Strategy`
8. `Runtime Persistence and State`
9. `Enforcement Contract`
10. `Coding and Testing Lenses`
11. `Work Units`
12. `Dependencies and Sequencing`
13. `Validation Gates`
14. `Review Plan`
15. `Rollback Plan`
16. `Risk Register`
17. `Observability and Evidence`
18. `Visual References / Diagrams`
19. `Accessibility and Operator Ergonomics`
20. `Open Questions`
21. `Final Decision`
22. `Appendix A. Harness Metadata / Traceability`
23. `Appendix B. Linear / Tracker Handoff`
24. `Appendix C. Review Outcomes`

For lightweight plans, keep the same reader path but collapse adjacent sections
when that does not hide scope, validation, rollback, or handoff. For deep plans,
expand `Work Units`, `Validation Gates`, `Rollback Plan`, and `Risk Register`
so every high-risk slice has its own stop condition and proof requirement.

Plan unit contract:

- Use stable `PU-*` IDs for implementation units.
- Map every `PU-*` to source `FR-*`, `NFR-*`, `SA-*`, `VAC-*`, issue, or
  decision IDs when they exist.
- Each `PU-*` must include: objective, source trace, allowed paths or areas,
  forbidden paths or areas, steps, validation command/evidence, stop condition,
  rollback note, and handoff state.
- Do not turn source requirements into vague task titles; preserve the
  requirement language and state what implementation evidence will satisfy it.
- Do not include implementation discoveries as settled facts until source
  inspection proves them. Mark them as `implementation-time unknown` or
  `[NEEDS CLARIFICATION: ...]`.
- If the source spec includes `Implementation Notes`, `Implementation
  Decisions`, prototype-derived snippets, or decision logs, project only the
  execution-relevant parts into `Implementation Strategy`, `Work Units`, and
  `Risk Register`. Preserve durable behavior/interface/schema/state decisions
  by source ID, but do not copy long rationale or turn the plan into a duplicate
  spec.
- If the source spec includes `Testing Decisions` or validation doctrine,
  project it into `Validation Gates` and each affected `PU-*` as external
  behavior expectations, prior-art test families to inspect, exact commands when
  known, and stop conditions when confidence cannot be proven.

Authority, runtime, and lens requirements:

- `Authority and Scope Boundary` must include `requested_depth`,
  `approved_execution_boundary`, `downscope_authority`,
  `external_mutation_boundary`, `freshness_required`, and
  `human_acceptance_boundary`, or an explicit `not_applicable` reason for each
  field. A full-implementation request may be sequenced into units, but the
  plan must preserve unfinished full scope unless downscope is explicitly
  approved by the user or source artifact.
- `Runtime Persistence and State` must include `runtime_state`,
  `resumption_key`, `persistent_artifacts`, `live_state_refresh`,
  `session_evidence_status`, and `proof_boundary`. It must say what survives
  resume and what must be refreshed before implementation or closure.
- `Coding and Testing Lenses` must include `coding_lens:` and `testing_lens:`
  blocks. The coding lens names ownership, allowed and forbidden files or
  modules, public contract/schema/API/CLI compatibility, failure/recovery,
  generated-artifact boundaries, and complexity posture. The testing lens names
  observable behavior, source acceptance IDs, prior-art test families, positive
  and negative scenarios, exact validation commands when known, blocked gates,
  and recovery ownership.
- Missing specialist roles require inline coverage parity. Do not route to
  `he-work` when coding/testing/correctness/adversarial coverage is absent or
  only implied by a chat summary.

Enforcement Contract requirements:

- Every standard plan must include an `Enforcement Contract` section using the
  Skills SDK apparatus lens:
  `Infrastructure/references/skills-sdk-apparatus-lens.md`.
- The plan must preserve the source spec's `essential_decisions`,
  `fillable_gaps`, `guardrails`, `refusal_triggers`,
  `durable_memory`, and `professional_output`, or state why a field is not
  applicable for this slice.
- Work units must inherit the contract instead of expanding scope from a vague
  implementation idea. For SDK, public API, schema, CLI, package, or
  agent-facing work, assign files only after the essential decisions and
  refusal triggers are clear.
- Guardrails must be actionable validation commands, schemas, tests, evals,
  doctor/prove gates, structural audits, or manual gates with an owner and pass
  condition.
- Professional output must name the closeout evidence required before a done
  claim: files changed, exact commands, pass/fail state, blockers, warnings,
  next action, and rollback.

Validation and proof requirements:

- Prefer deterministic commands and repo wrappers over agent narrative.
- Record each planned gate as `required`, `conditional`, or `not_applicable`
  with the reason.
- Separate validation that can run before implementation from validation that
  can only run after a `PU-*` is complete.
- Include smoke, release, docs/prose, security, accessibility, package-boundary,
  and runtime checks only when the source contract or touched surface requires
  them; do not paste a generic checklist.
- Testing decisions in plans must name the observable behavior under test, the
  source requirement or acceptance ID, the test surface or prior-art family to
  inspect, and the expected proof. Avoid tests that assert private implementation
  details unless the private contract is itself the approved behavior.
- A plan is not ready for `he-work` when validation commands, rollback,
  ownership, source traceability, strict boundary fields, runtime persistence,
  or coding/testing lenses are missing.

Visual reference requirements:

- Include at least one visual aid when the plan has multiple work streams,
  dependencies, rollout phases, review lanes, service boundaries, state
  transitions, or cross-surface sequencing that is easier to understand
  visually than through prose.
- Prefer Mermaid diagrams, dependency graphs, sequence diagrams, flowcharts,
  and markdown tables because humans can scan them and agents can parse them.
- Keep visuals at execution-structure level: show units, dependencies,
  boundaries, validation flow, or rollback flow. Do not encode fragile method
  names, SQL, API fields, or speculative architecture unless source evidence
  requires those details.
- Use generated bitmap images only when a human visual reference materially
  improves review or when a media artifact is explicitly requested. Store
  review-only generated media under `.harness/media/` with prompt/sidecar
  evidence when generated media is created.
- Prose and validation gates remain authoritative when a visual and text
  disagree.
- Do not add decorative images or generic infographics to satisfy the visual
  rule; every visual must clarify execution order, dependencies, boundaries,
  risk, validation, or rollback.
- Apply the shared visual contract for generated media persistence, proof
  rules, and compact not-needed reasons:
  `Plugins/synaipse-harness/references/upstream/harness-engineering/visual-reference-contract.md`.

## BLUF Review Surface

For non-trivial durable plans, apply
`Plugins/synaipse-harness/references/upstream/harness-engineering/bluf-review-contract.md`.

Keep the existing plan substance. Add:

- Command Summary with exactly one substantive `BLUF` paragraph, decision
  needed, top risks, and next action. The BLUF must explain the document's job,
  affected system, reader/user value, execution decision, major risk or
  blocker, and next action in one paragraph.
- No `BLUF-Only Summary`.
- No section-level or unit-level `BLUF:` labels. Major plan sections and
  `PU-*` units should open with clear objective or summary prose, but only the
  document opening is BLUF.
- Unit-level Do/Do Not, validation evidence, stop conditions, rollback notes,
  and summary.
- No-Fog Gate before handoff.

Do not turn the plan into duplicate simple/full documents. The BLUF paragraph is
the opening bottom line; the rest of the plan is the evidence and execution
contract.

Full retained notes: `Plugins/synaipse-harness/references/upstream/harness-engineering/he-plan-doctrine.md`.
