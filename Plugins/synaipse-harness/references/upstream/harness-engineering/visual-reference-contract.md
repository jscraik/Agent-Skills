# Visual Reference Contract

Read when: a Harness Engineering artifact may need a diagram, table, screenshot,
generated image, or visual proof reference.

Visual references are review aids, not decoration. Add a visual only when it
answers a question faster than prose: what flows where, what depends on what,
where the boundary is, what state can exist, what proves completion, what must
not be touched, or where the work can fail.

## Required When

Include a `Visual References / Diagrams` section, or the closest mode-specific
equivalent, for non-trivial artifacts that include any of these:

- three or more dependent work units, issues, surfaces, actors, roles, states,
  systems, or variants
- state machines, lifecycles, retries, queues, handoffs, or reconciliation
  flows
- service, safety, permission, workspace, tool, tracker, or data-boundary
  decisions
- data/domain models, generated-file contracts, ledger/manifest schemas, API or
  protocol relationships, or consumer behavior rules
- rollout phases, review lanes, validation gates, rollback paths, or evidence
  chains
- UI, accessibility, media, screenshot, rendered-document, or visual-regression
  behavior
- source-of-truth conflicts across repo, tracker, PR, validation, session, or
  `.harness` artifacts

If no visual is useful, write a compact `Not needed` line with the reason. Do
not leave readers guessing whether the section was forgotten.

## Preferred Formats

- Use Mermaid for flows, dependencies, state transitions, boundaries, issue
  trees, evidence chains, rollback paths, and agent/human handoff.
- Use markdown tables for comparisons, matrices, field contracts, gate status,
  severity maps, Now/Next/Later decisions, and pass/fail/blocked proof.
- Use ASCII maps only when Mermaid would be too heavy or the artifact must stay
  maximally portable.
- Use screenshots, rendered images, or generated bitmap media only when visual
  output itself is the reviewed behavior or proof.

Mermaid and tables are the default because humans can scan them and agents can
parse them. Generated bitmap images are exceptional.

## Generated Media Rules

Review-only generated media belongs under `.harness/media/`, not inside the
skill package. A generated image, screenshot, or rendered asset may be cited as
proof only when the artifact records:

- repository media path
- purpose of the visual
- source prompt or capture command when applicable
- sidecar metadata path when generated
- linked source artifact or validation context
- file-existence verification
- whether the media is review-only or closure evidence

Prompt-only, cache-only, or visible-only media is not persisted proof.

## Artifact Guidance

Use these defaults unless a local artifact contract is stricter:

- Specs: diagram state, lifecycle, domain model, interface, safety boundary, UI
  flow, or generated-file contract.
- Plans: diagram work-unit dependencies, sequencing, validation gates, rollback
  path, review lanes, and handoff.
- Linear plans: diagram parent/sub-issue trees, dependency maps, Now/Next/Later
  sets, eval gates, and human-versus-agent routes.
- Brainstorm or ideation: use option maps, comparison tables, decision trees,
  or workflow sketches only when they sharpen survivor selection.
- Strategy, intent, triage, or architecture review: use strategy maps,
  boundary diagrams, drift maps, priority ladders, or thesis-risk matrices.
- Refactor programs: diagram before/after boundaries, migration phases, blast
  radius, coexistence, rollback, and eval closure.
- Code reviews: use risk-surface, attack-path, causality, or severity maps only
  when a normal findings list would hide the failure path.
- Eval reports: prefer evidence/gate matrices; use diagrams for non-linear
  proof chains and media files only when visual output is proof.
- Reconcile artifacts: diagram source-of-truth conflicts and the route from
  stale/missing evidence to the next stage.
- Reinforce or solution artifacts: use tiny causal diagrams only for recurring
  operational patterns that future agents must recognize quickly.

## Authority Rule

Prose, stable IDs, validation gates, and acceptance criteria remain
authoritative. If a visual disagrees with the surrounding text, fix or remove
the visual before handoff.

## Anti-Patterns

- decorative hero images, generic infographics, or visual filler
- diagrams that duplicate a simple paragraph
- method-name, SQL, API-field, or speculative architecture diagrams without
  source evidence
- image-only evidence with no text equivalent
- generated media cited as proof without `.harness/media/` persistence and
  file-existence verification
- visuals that make the artifact harder to diff, validate, or parse
