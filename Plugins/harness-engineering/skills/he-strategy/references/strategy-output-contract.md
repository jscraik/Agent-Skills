# Strategy Output Contract

Use after `he-strategy` selects a mode. Keep `SKILL.md` compact; this file owns
mode paths, required evidence, and guardrails.

## Modes and Paths

| Mode | Output |
| --- | --- |
| `intent` | `.harness/features/YYYY-MM-DD-JSC-###-<slug>-intent.md` when Linear is known, otherwise `.harness/features/YYYY-MM-DD-<repo-name>-<slug>-intent.md`. |
| `architecture-review` | `.harness/review/YYYY-MM-DD-JSC-###-<slug>-architecture-review.md` or no-Linear repo-name equivalent. |
| `triage` | `.harness/triage/YYYY-MM-DD-JSC-###-<slug>-triage.md` or no-Linear repo-name equivalent. |
| `repo-cognition-pipeline` | Intent + architecture review + triage sequence. Use Linear-aware names when Linear context is known; otherwise use repo-name equivalents. |
| `strategic-compression` | `.harness/strategy/YYYY-MM-DD-JSC-###-<slug>-strategy.md` or no-Linear equivalent. |
| `decision-compression` | Only high-value ADRs under `.harness/decisions/ADR-###-<slug>.md`; scan existing ADR numbers first. |
| `core-compression` | Stable invariant files under `.harness/core/**`. |

`source-prompt-equivalence` is a cross-cutting overlay, not an output root. Use
it when asked whether a skill, artifact, or workflow captures an original prompt
or prior method. Report coverage verdict, covered/missing requirements, evidence
depth, downstream confidence, and patch/handoff/`Do Not Create` gaps.

## Required Output Fields

Every output must include: `schema_version: 1`, source artifacts and inspection
method, reference material status when relevant, facts/interpretations/
assumptions, affected systems, confidence, smallest feedback-producing next
slice, stop/pivot condition, `clarification_status` (`asked`, `not_needed`, or
`assumed`), `ambiguity_impact` and `assumption_risk` when applicable,
drift/moat impact, future-agent guidance, evidence matrix, and visual reference
status when a map or diagram would reduce review effort.

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

- Intent: project intent, thesis, stable interfaces, leverage, drift risks,
  future-agent preservation/challenge guidance, open questions, evidence matrix.
- Architecture review: risk, cognition, complexity, deep/shallow modules, domain
  integrity, agent-native capability, governance, anti-patterns, moat analysis,
  evidence matrix, and `Reference Lens Status` when reference material or the
  internal canon is used.
- Triage: strategic/architectural/operational/governance/agent-native/debt
  findings, false sophistication, deletions, refactors, anti-drift priorities,
  eval and governance changes, ADRs, future-agent risks, and `Execution Routing
  Decisions (Linear | ADR | Refactor | Eval | Governance | Do Not Create)`.
  Write `No Linear items` when none are justified.
- Repo cognition pipeline: follow `repo-cognition-pipeline.md`; intent feeds
  review, review feeds triage, triage routes execution or `Do Not Create`.
- Strategic compression: thesis, actual moat, false moat, contradictions,
  deletions, non-negotiables, safe rewrite zones, risks, priorities, evidence.

Architecture-review, triage, repo-cognition-pipeline, and strategic-compression
outputs must include `Direct Strategic Critique`: strongest leverage, biggest
drag, highest-risk contradiction, and one hard recommendation.

When no fresh reference material is supplied, use
`references/architecture-lens-canon.md` and mark status `internal-canon`.
