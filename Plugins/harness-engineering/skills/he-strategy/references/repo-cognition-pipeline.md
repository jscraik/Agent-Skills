# Repository Cognition Pipeline

Use when the user asks for the full repo-intent, architecture-review, and
structural-triage workflow, or says `he-strategy` does not capture the long-form
prompt deeply enough. This is a multi-artifact strategy pipeline, not generic
documentation.

## Select This Mode

Select `repo-cognition-pipeline` only when more than one of these is requested
as a sequence: repo intent under `.harness/features/`, architecture cognition
review under `.harness/review/`, structural triage under `.harness/triage/`.
Use a single mode from `strategy-output-contract.md` when only one artifact is
requested.

## Artifact Sequence

1. Intent: `.harness/features/YYYY-MM-DD-JSC-###-<slug>-intent.md` when Linear
   context is known, otherwise `.harness/features/YYYY-MM-DD-<repo-name>-intent.md`.
   Explain what the repo is trying to become, what must stay stable, what must
   not drift, what is leverage, and what is accidental complexity.
2. Architecture review: `.harness/review/YYYY-MM-DD-JSC-###-<slug>-architecture-review.md`
   or `.harness/review/YYYY-MM-DD-<repo-name>-architecture-review.md`. Pressure-test
   coherence, modularity, domain integrity, agent-native architecture,
   governance, complexity, and moat claims.
3. Triage: `.harness/triage/YYYY-MM-DD-JSC-###-<slug>-triage.md` or
   `.harness/triage/YYYY-MM-DD-<repo-name>-triage.md`. Compress intent and review
   into execution routing, deletions, anti-drift protections, ADR/refactor/eval/
   governance candidates, and findings that should not become work.

Do not skip directly to triage unless intent and review are fresh enough. If
stale, sampled, or absent, refresh them or mark triage authority limited.

## Evidence and Stance

Inspect implementation reality before strategic claims: source, configs,
manifests, scripts, CI/CD, tests, docs, prompts, skills, workflows, hooks,
harness files, architecture boundaries, telemetry/observability, validation
loops, orchestration, MCP integrations, memory/context systems, product language,
roadmap/TODO/dead code, repeated abstractions, and coupling. Use bounded sampling
only when necessary; record inspected, not inspected, sufficiency, confidence
downgrade, and refresh needs.

Every major conclusion must separate hard evidence, strong inference, and weak
assumption/speculation. Do not infer capability from README language, skill
names, or aspiration alone.

## Lenses

Apply pragmatic engineering, Philosophy of Software Design, DDD, XP/feedback,
structural refactoring, agent-native architecture, and moat pressure lenses. Do
not summarize books. Use supplied reference material when present; otherwise load
`architecture-lens-canon.md` and mark `Reference Lens Status` as
`internal-canon`. Attached material status values: `inspected`, `sampled`,
`unavailable`, `not needed`, `internal-canon`.

## Required Sections

Intent must include: Project Intent, Core Thesis, Strategic Direction, Intended
Users, Non-Goals, System Philosophy, Architectural Patterns, Agent-Native Design
Assumptions, Harness/Governance Model, Critical Constraints, Stable Interfaces,
Sources of Complexity, Sources of Leverage, Probable Moat, Drift Risks, What
Future Agents Should Preserve/Challenge, Open Questions, Recommended Decisions,
Strategic Contradictions, Suggested Simplifications, Missing Capabilities,
Long-Term Scalability Concerns, Drift Detection Signals, Evidence & Traceability
Matrix.

Architecture review must include: Executive Summary, Reference Lens Status,
Architectural Risk Assessment, Repository Cognition Review, Complexity Audit,
Deep vs Shallow Module Analysis, Domain Integrity Review, Skill/Plugin
Architecture Review, Agent-Native Capability Review, Governance & Workflow
Review, Refactor Recommendations, Anti-Patterns, Drift Risks, Technical Debt,
Strategic Review, Simplifications, Deletions, Core Investments, Scalability
Risks, Moat Analysis, Competitive Replication Risk, Evidence Matrix.

Triage must include: Executive Triage Summary, Immediate Architectural Risks,
Strategic/Architectural/Operational/Governance/Agent-Native Findings, Complexity
Without Leverage, Moat-Critical Systems, Fake Sophistication, Deletions,
Refactor Candidates, Anti-Drift Priorities, Execution Priority Matrix,
`Execution Routing Decisions (Linear | ADR | Refactor | Eval | Governance | Do
Not Create)`, Recommended Eval Programs, Recommended Governance Changes,
Recommended ADRs, Recommended Reframe Programs, Future Agent Risks,
Compression Opportunities, Evidence Matrix.

## Drift, Moat, Clarification, Handoff

Drift signals should include measurable indicators where possible, why they
matter, likely cause, operational impact, severity, corrective action, and
whether they block merges/releases.

Moat analysis must decide what is hard to copy, what only feels sophisticated,
what to protect, what to simplify, what assumptions are likely false, whether the
moat survives simplification, and whether competitors could catch up quickly. If
no real moat exists, say so.

Ask focused clarification questions only when the answer materially changes
architecture direction, product intent, moat, governance, agent workflows,
scalability, UX philosophy, or commercial positioning. Use `request_user_input`
when available; otherwise ask directly or record an open question and continue
with the safest evidence-backed assumption. Record `clarification_status`,
`ambiguity_impact`, and `assumption_risk`.

Intent, review, and triage are durable secondary context. They do not authorize
implementation. Route candidates to ADR, reframe program, Linear, eval program,
governance change, or `Do Not Create`. Write `No Linear items` when no Linear
work is justified.

End with `Direct Strategic Critique`: coherence, complexity justification, real
leverage, drag, deletion candidates, smallest compelling version, biggest failure
mode, and the single best next strategic move.
