# Strategy Output Contract

Use this reference after `he-strategy` selects a mode. Keep the entrypoint
compact; this file carries the mode-specific output contract.

## Modes

- `intent`: write `.harness/features/YYYY-MM-DD-JSC-###-<slug>-intent.md`
  when Linear context is known, otherwise
  `.harness/features/YYYY-MM-DD-<repo-name>-intent.md` unless the user gives a
  narrower slug. This mode preserves the Repository Intent Extraction +
  Strategic Review workflow: stated and implied intent, direction, leverage,
  accidental complexity, drift boundaries, moat, and future-agent guidance.
- `architecture-review`: write
  `.harness/review/YYYY-MM-DD-JSC-###-<slug>-architecture-review.md` or the
  no-Linear equivalent. This mode preserves the Multi-Disciplinary
  Architecture & Skill Review workflow: whole-repo inspection, reference lenses
  as evaluators, deep/shallow module analysis, domain integrity, agent-native
  capability, moat pressure, direct strategic critique, and evidence-backed
  traceability.
- `triage`: write `.harness/triage/YYYY-MM-DD-JSC-###-<slug>-triage.md` or the
  no-Linear equivalent. This mode preserves the Structural Triage & Execution
  Prioritization workflow: consume fresh intent/review artifacts, compress
  findings instead of repeating them, separate leverage from noise, identify
  false sophistication and deletion candidates, and route only justified work.
- `repo-cognition-pipeline`: write one intent, one architecture review, and one
  triage artifact in a single routed pass. Use this only when the user asks for
  all three outputs together; intent and review must feed triage.
- `strategic-compression`: write
  `.harness/strategy/YYYY-MM-DD-JSC-###-<slug>-strategy.md` or the no-Linear
  equivalent. This mode preserves the Strategic Compression & Direction
  workflow: compress intent, review, and triage into durable direction,
  identify actual and false moat, preserve non-negotiables, choose deletions
  and core investments, define safe rewrite zones, and avoid roadmap repeat.
- `decision-compression`: write only high-value ADRs under
  `.harness/decisions/ADR-###-<slug>.md`; scan existing ADR numbers first.
  This mode preserves the Architectural Decision Compression workflow: create
  a decision record only when durable disagreement, rejected alternatives, or
  future review avoidance justify ADR weight. Keep ADRs sparse by default: a
  short title plus one to three sentences stating context, decision, and why.
  Add status, considered options, or consequences only when they add real value.
- `core-compression`: update or create stable living invariant files under
  `.harness/core/**`. This mode preserves the Core Knowledge Compression &
  Architectural Invariants workflow: record only non-negotiable system truths,
  drift boundaries, preserved concepts, and future-agent operating constraints
  that should outlive a single review or project.
- `source-prompt-equivalence` (cross-cutting overlay): when asked to compare a
  prior prompt or method, include a coverage verdict, covered requirements,
  missing requirements, evidence depth, source prompt family, and downstream
  confidence limits.

## Required Output Contract

Every output must include:

- `schema_version: 1`
- source artifacts read and inspection method
- hard evidence, interpretation, and assumptions
- affected systems or modules
- confidence level for major conclusions
- authority limits
- validation outcomes (`pass`/`fail`/`blocked` with reason)
- clarification status and ambiguity impact
- assumption risk and confidence limits
- post-artifact review status
- smallest feedback-producing next slice
- stop or pivot condition for the next slice
- drift or moat impact where relevant
- future-agent guidance
- evidence and traceability matrix
- `he-strategy`
- `subagent_policy`
- `roles_used`, `roles_recommended`, and `roles_missing`

Repo intent outputs must additionally include:

- `Modern Standards Assessment (May 2026)` covering agent-native architecture,
  workflow ergonomics, repository cognition, deterministic execution,
  validation, observability, typed boundaries, context management,
  multi-agent coordination, memory architecture, DX/UX, security, CI/CD,
  testing realism, harness quality, prompt/skill composability, portability,
  modularity, and dependency discipline. Use bounded current-source checks when
  claims are likely to drift; otherwise mark current-standards evidence
  unavailable or internal-canon.
- `Direct Strategic Critique` answering coherence, pragmatism, complexity
  justification, real versus performative agent-native design, leverage, drag,
  deletion candidates, core investments, moat, commercial/adoption risk,
  smallest compelling version, likely false assumptions, and failure mode.
- `Drift Detection Signals` with why it matters, likely cause, operational
  impact, severity, corrective action, merge/release blocking stance, and
  measurable indicators where possible.
- post-artifact review loop status. When `request_user_input` is available,
  use it to ask focused review questions before finalizing. When unavailable or
  headless, record `post_artifact_review_status: blocked` with the reason and
  continue only with explicit assumption risk.

Architecture-review outputs must additionally include:

- Explicit source prompt family status for Multi-Disciplinary Architecture &
  Skill Review.
- Reference lens status for Pragmatic Programmer, Philosophy of Software
  Design, Extreme Programming, Domain-Driven Design, Five Lines of Code,
  agent-native architecture, and moat pressure. Use supplied materials as
  evaluative lenses, not summaries. When attachments are unavailable, use the
  internal lens canon and mark the evidence status.
- Whole-repo inspection coverage across source, configs, scripts, CI/CD, tests,
  docs, prompts, skills, workflows, hooks, harness files, architecture
  boundaries, validation loops, memory/context systems, MCP integrations,
  observability, dependency graph, dead code, TODO clusters, repeated
  abstractions, hidden coupling, and naming conventions. Record sampling limits
  rather than implying full coverage when only sampled.
- Lens-specific findings for pragmatic engineering, deep versus shallow
  modules, domain-driven design, XP/feedback loops, refactoring and structural
  complexity, agent-native architecture, governance/workflow, and moat.
- Direct strategic review that answers coherence, pragmatism, justified
  complexity, real versus performative agent-native design, leverage, drag,
  deletion candidates, core investments, adoption risk, smallest compelling
  version, likely failure mode, and likely success reason.
- Moat analysis that explicitly answers what is difficult to copy, whether the
  moat is durable and measurable, whether it is merely complexity, whether a
  smaller competitor could rebuild it quickly, what should be protected, what
  should be simplified, and which moat assumptions are likely false.
- Evidence & Traceability Matrix mapping every major conclusion to evidence
  type, file paths, symbols or components, runtime behavior observed, confidence
  level, why the evidence matters, and fact/interpretation/speculation status.
- post-artifact review loop status using `request_user_input` when available,
  or `post_artifact_review_status: blocked` with concrete reason and
  assumption risk.

Triage outputs must additionally include:

- Explicit source prompt family status for Structural Triage & Execution
  Prioritization.
- Freshness and authority status for consumed `.harness/features/*.md` and
  `.harness/review/*.md`. The triage artifact should summarize only the deltas,
  routing choices, and execution pressure; implementation specs and backlog
  dumps are out of scope for this mode.
- Signal/noise filtering into `high_leverage`, `medium_leverage`,
  `low_leverage`, and `false_sophistication`, including findings that should
  not become work.
- Classification of every major finding into strategic, architectural,
  operational, agent-native, governance, and technical-debt buckets.
- Immediate Architectural Risks with severity, likelihood, blast radius, why it
  matters, and recommended response.
- Complexity Without Leverage entries explaining why each item exists, why it
  survived, why it is harmful now, and whether to remove, collapse, merge,
  simplify, defer, or preserve it.
- Moat-Critical Systems and fake moat systems, including whether complexity
  strengthens or weakens each system.
- Recommended Deletions with survival reason and expected architectural impact.
- Execution Priority Matrix with impact, complexity, strategic importance, risk,
  route, and whether the item should become work.
- Anti-Drift Classification and Future Agent Operational Impact sections that
  identify cognition cost, ambiguous orchestration, misleading abstractions,
  local-reasoning failures, determinism gaps, discoverability failures, and
  token-expensive workflows.
- post-artifact review loop status using `request_user_input` when available,
  or `post_artifact_review_status: blocked` with concrete reason and
  assumption risk.

Strategic-compression outputs must additionally include:

- Explicit source prompt family status for Strategic Compression & Direction.
- Inputs consumed and freshness status for intent, review, triage, ADR, core,
  and strategy artifacts used as evidence.
- Irreducible core, actual moat, false moat, strategic contradictions,
  non-negotiables, deletion candidates, core investments, safe rewrite zones,
  risk register, future-agent guidance, and smallest feedback-producing next
  slice.
- Evidence-backed priority choices that change direction, routing, deletion,
  investment, or anti-drift behavior. Routine local fixes and speculative
  governance are out of scope.
- Evidence & Traceability Matrix and authority limits, especially when source
  artifacts are sampled, stale, or partial.

Decision-compression outputs must additionally include:

- Explicit source prompt family status for Architectural Decision Compression.
- ADR necessity test: hard to reverse, surprising without context, real
  trade-off, consequence of forgetting, future re-suggestion risk, and why a
  lighter artifact is insufficient.
- Existing ADR scan, next-number evidence, decision status, context, options
  considered, decision, consequences, rejected alternatives, authority limits,
  and evidence traceability.
- Do Not Create classification when the issue is ephemeral, self-evident,
  already decided, better handled by implementation notes, or lacks enough
  evidence for durable policy.

Core-compression outputs must additionally include:

- Explicit source prompt family status for Core Knowledge Compression &
  Architectural Invariants.
- Invariant necessity test: long-lived system truth, repeated drift risk,
  stable vocabulary, enforcement surface, owner, and consequence of breaking
  the invariant.
- Scope boundaries, non-goals, allowed variation, prohibited drift, validation
  or hook linkage, future-agent guidance, and evidence traceability.
- Do Not Create classification when the candidate is local preference,
  temporary process, single-ticket context, or unproven architecture theory.

Keep this list aligned with the required output contract in
`Plugins/harness-engineering/skills/he-strategy/SKILL.md`.

## Mode Guardrails

- Strategy, review, triage, feature, ADR, and core artifacts do not authorize
  implementation unless admitted by `.harness/linear/**`,
  `.harness/reframes/**`, `.harness/specs/**`, or `.harness/plan/**`.
- Do not overwrite existing `.harness` artifacts unless the user explicitly
  asks for that exact artifact to be updated.
- When network access is approved by active rules, use bounded web research for
  current standards, competitive/prior-art claims, or any fact likely to have
  changed; cite sources or mark evidence unavailable.
- Classify low-value governance as `Do Not Create` instead of writing another
  document.
- Exclude strategic conclusions that cannot change a decision, alter routing,
  reduce risk, or create a near-term feedback signal.

## Required Sections By Common Mode

Intent artifacts should cover project intent, stated intent from docs/prompts,
implied intent from implementation reality, stated vs implied alignment or
contradiction, core thesis, strategic direction, intended users, non-goals,
system philosophy, architectural patterns, agent-native assumptions,
harness/governance model, critical constraints, stable interfaces, sources of
complexity, sources of leverage, probable moat, drift risks, technical debt
signals, UX philosophy, what future agents should preserve and challenge, open
questions, recommended decisions, strategic contradictions, suggested
simplifications, missing capabilities, long-term scalability concerns, `Modern
Standards Assessment (May 2026)`, `Direct Strategic Critique`, `Drift Detection
Signals`, and `Evidence & Traceability Matrix`.

Architecture reviews must include Executive Summary, Architectural Risk
Assessment, Repository Cognition Review, Complexity Audit, Deep vs Shallow
Module Analysis, Domain Integrity Review, Skill/Plugin Architecture Review,
Agent-Native Capability Review, Governance & Workflow Review, Refactor
Recommendations, Anti-Patterns Identified, Drift Risks, Technical Debt
Hotspots, Strategic Review, Recommended Simplifications, Recommended
Deletions, Recommended Core Investments, Long-Term Scalability Risks, Moat
Analysis, Competitive Replication Risk, Evidence & Traceability Matrix, and
`post_artifact_review_status`.

Triage artifacts must include Executive Triage Summary, Immediate Architectural
Risks, Strategic Findings, Architectural Findings, Operational Findings,
Governance Findings, Agent-Native Findings, Complexity Without Leverage,
Moat-Critical Systems, Fake Sophistication Signals, Recommended Deletions,
Refactor Candidates, Anti-Drift Priorities, Execution Priority Matrix,
Recommended Linear Initiatives, Recommended ADRs, Recommended Refactor Programs,
Future Agent Operational Risks, Recommended Compression Opportunities, Evidence
& Traceability Matrix, and `post_artifact_review_status`.

Strategic compression artifacts should define core thesis, actual moat, false
moat signals, contradictions, deletion candidates, non-negotiables, safe rewrite
zones, risks, direction, priorities, future-agent guidance, Evidence &
Traceability Matrix, and authority limits.

Decision compression artifacts must include source prompt family status, ADR
necessity test, existing ADR scan, selected ADR path or Do Not Create,
decision, alternatives, consequences, future re-suggestion risk, authority
limits, and Evidence & Traceability Matrix.

Core compression artifacts must include source prompt family status, invariant
necessity test, invariant statement, scope, non-goals, drift boundary,
enforcement or validation linkage, owner or review surface, future-agent
guidance, and Evidence & Traceability Matrix.
