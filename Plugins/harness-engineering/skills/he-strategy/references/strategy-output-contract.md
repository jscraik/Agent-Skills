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

Intent artifacts should cover project intent, stated intent from docs/prompts,
implied intent from implementation reality, stated vs implied alignment or
contradiction, core thesis, stable interfaces, evidence sufficiency,
not-inspected surfaces, sources of leverage, drift risks, what future agents
should preserve, open questions, and an evidence matrix.

Architecture reviews should cover risk, cognition, complexity, deep versus
shallow modules, domain integrity, agent-native capability, governance,
anti-patterns, moat analysis, and evidence matrix.

Triage artifacts should compress findings into strategic, architectural,
operational, governance, agent-native, technical debt, false sophistication,
deletion, refactor, anti-drift, Linear, ADR, and future-agent risks.

Strategic compression artifacts should define core thesis, actual moat, false
moat signals, contradictions, deletion candidates, non-negotiables, safe rewrite
zones, risks, direction, priorities, future-agent guidance, and evidence matrix.
