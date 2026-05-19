# Strategy Output Contract

Use after `he-strategy` selects a mode. Keep `SKILL.md` compact; this file owns
mode paths, required evidence, and guardrails.

## Modes and Paths

| Mode | Output |
| --- | --- |
| `intent` | `.harness/features/YYYY-MM-DD-JSC-###-<slug>-intent.md` or no-Linear repo-name equivalent. |
| `architecture-review` | `.harness/review/YYYY-MM-DD-JSC-###-<slug>-architecture-review.md` or no-Linear equivalent. |
| `triage` | `.harness/triage/YYYY-MM-DD-JSC-###-<slug>-triage.md` or no-Linear equivalent. |
| `repo-cognition-pipeline` | Intent + architecture review + triage sequence. Use Linear-aware names when Linear context is known; otherwise use repo-name equivalents. |
| `strategic-compression` | `.harness/strategy/YYYY-MM-DD-JSC-###-<slug>-strategy.md` or no-Linear equivalent. |
| `decision-compression` | Only high-value ADRs under `.harness/decisions/ADR-###-<slug>.md`; scan existing ADR numbers first. |
| `core-compression` | Stable invariant files under `.harness/core/**`. |

`source-prompt-equivalence` is a cross-cutting overlay, not an output root. Use
it when asked whether a skill, artifact, or workflow captures an original prompt
or prior method. Report coverage verdict, covered/missing requirements, evidence
depth, downstream confidence, and patch/handoff/`Do Not Create` gaps.

## Required Output Fields

Every output must include: `schema_version: 1`, sources, inspection method,
reference status when relevant, facts/interpretations/assumptions, affected
systems, confidence, smallest feedback slice, stop/pivot condition,
`clarification_status`, applicable ambiguity/risk fields, drift/moat impact,
future-agent guidance, Evidence & Traceability Matrix, and visual status when
useful.

When the user asks for an interactive final workflow, include
`post_artifact_review_status` with one of: `completed`, `blocked`, or
`not_requested`. Use `request_user_input` when available after writing the
artifact; otherwise mark `blocked` with the exact unavailable tool or mode. Do
not claim refinement occurred unless the user reviewed the artifact and changes
were applied.

## Guardrails

- Strategy, review, triage, feature, ADR, and core artifacts are secondary
  context. They do not authorize implementation unless admitted by
  `.harness/linear/**`, `.harness/reframes/**`, `.harness/specs/**`, or
  `.harness/plan/**`.
- Do not overwrite existing `.harness` artifacts unless explicitly asked.
- Use bounded research for current standards or prior-art claims; cite sources
  or mark evidence unavailable.
- Classify low-value governance as `Do Not Create`.
- Exclude conclusions that cannot change a decision, alter routing, reduce risk,
  or create a near-term feedback signal.

## Mode Section Requirements

- Intent: stated and implementation-implied intent, thesis, stable interfaces,
  leverage, drift risks, prose/code alignment, evidence sufficiency,
  not-inspected surfaces, future-agent guidance, open questions, evidence matrix.
- Architecture review: use the exact requested section headings when the user
  supplies them; otherwise include Executive Summary, Architectural Risk
  Assessment, Repository Cognition Review, Complexity Audit, Deep vs Shallow
  Module Analysis, Domain Integrity Review, Skill/Plugin Architecture Review,
  Agent-Native Capability Review, Governance & Workflow Review, Refactor
  Recommendations, Anti-Patterns Identified, Drift Risks, Technical Debt
  Hotspots, Strategic Review, Recommended Simplifications, Recommended
  Deletions, Recommended Core Investments, Long-Term Scalability Risks, Moat
  Analysis, Competitive Replication Risk, and Evidence & Traceability Matrix.
  If sections are intentionally merged, state the merge and why it preserves the
  decision value. Include `Reference Lens Status` when reference material or the
  internal canon is used.
- Triage: strategic/architectural/operational/governance/agent-native/debt
  findings, false sophistication, deletions, refactors, anti-drift priorities,
  eval and governance changes, ADRs, future-agent risks, and `Execution Routing
  Decisions (Linear | ADR | Refactor | Eval | Governance | Do Not Create)`.
  Load `repo-cognition-pipeline.md` for the full structural triage contract.
  Write `No Linear items` when none are justified.
- Repo cognition pipeline: follow `repo-cognition-pipeline.md`; intent feeds
  review, review feeds triage, triage routes execution or `Do Not Create`.
- Strategic compression: consume `.harness/features`, `.harness/review`,
  `.harness/triage`; do not repeat them. Sections: Executive Strategic Summary,
  Core Thesis, Irreducible Core, Actual Moat, False Moat Signals, Strategic
  Contradictions, Complexity Without Leverage, What Should Be Deleted, What
  Should Become Core, Architectural Non-Negotiables, Safe To Rewrite, Strategic/
  Operational/Scaling/Governance/Agent-Native Risks, Recommended Strategic
  Direction, Recommended Simplifications, Core Investment Priorities, Future
  Agent Guidance, Evidence & Traceability Matrix. Rows: moat -> system, type,
  hard-to-copy, complexity effect, false assumption, competitor-removal test,
  protect/simplify; deletion -> why-exists/survived/remove-now, impact; rewrite
  -> surface, why non-core, constraints, validation, must-not-regress. Every
  conclusion: fact/interpretation/speculation, evidence, systems, confidence,
  operational impact, why it matters.

Architecture-review, triage, repo-cognition-pipeline, and strategic-compression
outputs must include `Direct Strategic Critique`: strongest leverage, biggest
drag, highest-risk contradiction, and one hard recommendation.

When no fresh reference material is supplied, use
`../../references/skills/he-strategy/architecture-lens-canon.md` and mark status `internal-canon`.
