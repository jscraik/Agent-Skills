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
- For non-trivial generated plans, also run `python3 Plugins/harness-engineering/scripts/check_bluf_structure.py <plan-path> --json` and `python3 Plugins/harness-engineering/scripts/check_generated_artifact_shape.py <plan-path> --kind plan --json` so the opening BLUF, execution-first body, plan units, source mapping, rollback, handoff, and visual-reference decision are validated before handoff.

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
5. `Current State / Evidence`
6. `Implementation Strategy`
7. `Work Units`
8. `Dependencies and Sequencing`
9. `Validation Gates`
10. `Review Plan`
11. `Rollback Plan`
12. `Risk Register`
13. `Observability and Evidence`
14. `Visual References / Diagrams`
15. `Accessibility and Operator Ergonomics`
16. `Open Questions`
17. `Final Decision`
18. `Appendix A. Harness Metadata / Traceability`
19. `Appendix B. Linear / Tracker Handoff`
20. `Appendix C. Review Outcomes`

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
  ownership, or source traceability are missing.

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
  `Plugins/harness-engineering/references/visual-reference-contract.md`.

## BLUF Review Surface

For non-trivial durable plans, apply
`Plugins/harness-engineering/references/bluf-review-contract.md`.

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

Full retained notes: `Plugins/harness-engineering/references/he-plan-doctrine.md`.
