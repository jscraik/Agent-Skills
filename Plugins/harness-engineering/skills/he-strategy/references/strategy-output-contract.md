# Strategy Output Contract

Use this reference after `he-strategy` selects a mode. Keep the entrypoint
compact; this file carries the mode-specific output contract.

## Modes

- `intent`: write `.harness/features/YYYY-MM-DD-JSC-###-<slug>-intent.md`
  when Linear context is known, otherwise
  `.harness/features/YYYY-MM-DD-<repo-name>-<slug>-intent.md`.
- `architecture-review`: write
  `.harness/review/YYYY-MM-DD-JSC-###-<slug>-architecture-review.md` or the
  no-Linear equivalent.
- `triage`: write `.harness/triage/YYYY-MM-DD-JSC-###-<slug>-triage.md` or the
  no-Linear equivalent.
- `repo-cognition-pipeline`: write the explicit sequence
  `.harness/features/YYYY-MM-DD-<repo-name>-intent.md`,
  `.harness/review/YYYY-MM-DD-<repo-name>-architecture-review.md`, and
  `.harness/triage/YYYY-MM-DD-<repo-name>-triage.md` when the user asks for the
  full intent + architecture review + triage workflow.
- `strategic-compression`: write
  `.harness/strategy/YYYY-MM-DD-JSC-###-<slug>-strategy.md` or the no-Linear
  equivalent.
- `decision-compression`: write only high-value ADRs under
  `.harness/decisions/ADR-###-<slug>.md`; scan existing ADR numbers first.
- `core-compression`: update or create stable living invariant files under
  `.harness/core/**`.

## Required Output Contract

Every output must include:

- `schema_version: 1`
- source artifacts read and inspection method
- hard evidence, interpretation, and assumptions
- affected systems or modules
- confidence level for major conclusions
- smallest feedback-producing next slice
- stop or pivot condition for the next slice
- drift or moat impact where relevant
- future-agent guidance
- evidence and traceability matrix
- visual references or diagrams when strategy, architecture, triage, or intent
  relationships are easier to review as a map, matrix, or Mermaid diagram

## Mode Guardrails

- Strategy, review, triage, feature, ADR, and core artifacts do not authorize
  implementation unless admitted by `.harness/linear/**`,
  `.harness/refactors/**`, `.harness/specs/**`, or `.harness/plan/**`.
- Do not overwrite existing `.harness` artifacts unless the user explicitly
  asks for that exact artifact to be updated.
- Use bounded web research for current standards, competitive/prior-art claims,
  or any fact likely to have changed; cite sources or mark evidence unavailable.
- Classify low-value governance as `Do Not Create` instead of writing another
  document.
- Exclude strategic conclusions that cannot change a decision, alter routing,
  reduce risk, or create a near-term feedback signal.

## Required Sections By Common Mode

Intent artifacts should cover project intent, core thesis, stable interfaces,
sources of leverage, drift risks, what future agents should preserve, open
questions, and an evidence matrix.

Architecture reviews should cover risk, cognition, complexity, deep versus
shallow modules, domain integrity, agent-native capability, governance,
anti-patterns, moat analysis, and evidence matrix.

Triage artifacts should compress findings into strategic, architectural,
operational, governance, agent-native, technical debt, false sophistication,
deletion, refactor, anti-drift, Linear, ADR, and future-agent risks.

Full repo cognition pipeline artifacts should follow
`repo-cognition-pipeline.md`. The intent artifact establishes durable thesis and
drift signals, the architecture review pressure-tests coherence and moat, and
the triage artifact decides what should become execution, ADRs, refactor
programs, eval programs, governance changes, or `Do Not Create`.

Strategic compression artifacts should define core thesis, actual moat, false
moat signals, contradictions, deletion candidates, non-negotiables, safe rewrite
zones, risks, direction, priorities, future-agent guidance, and evidence matrix.

## Visual References / Diagrams

Use visuals only when they sharpen the strategy decision:

- intent artifacts: project thesis map, stable-interface map, drift-risk map
- architecture reviews: boundary diagram, risk surface, or module interaction map
- triage artifacts: issue cluster map, priority ladder, or deletion/refactor map
- strategic compression: thesis-risk matrix, moat/drift map, or route map
- ADR/core compression: decision consequence map only when dependencies matter

Prefer Mermaid and markdown tables. If no visual adds value, write `Not needed`
and say why. Apply the shared generated-media and proof rules from
`Plugins/harness-engineering/references/visual-reference-contract.md`.
