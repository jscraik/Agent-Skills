# Repository Cognition Pipeline

Use when the user asks for the full repo-intent, architecture-review, and
structural-triage workflow, or says `he-strategy` does not capture the long-form
prompt deeply enough. This is a multi-artifact strategy pipeline, not generic
documentation.

The source prompt family `Repository Intent Extraction + Strategic Review` maps
to `intent` mode when only one artifact is requested, and to this full pipeline
when intent, architecture review, and triage are requested together. Do not
downgrade this request to generic architecture documentation.

The source prompt family `Multi-Disciplinary Architecture & Skill Review` maps
to `architecture-review` mode when only the review artifact is requested, and
to this full pipeline when the review should feed structural triage. Preserve it
as a durable architecture cognition audit, not a generic code review.

The source prompt family `Structural Triage & Execution Prioritization` maps
to `triage` mode when only the triage artifact is requested, and to this full
pipeline when it follows fresh intent/review outputs. Preserve it as the
operational compression layer between architecture cognition and execution, not
as a backlog dump.

## Select This Mode

Select `repo-cognition-pipeline` only when more than one of these is requested
as a sequence: repo intent under `.harness/features/`, architecture cognition
review under `.harness/review/`, structural triage under `.harness/triage/`.
Use a single mode from `strategy-output-contract.md` when only one artifact is
requested.

## Artifact Sequence

1. Intent: `.harness/features/YYYY-MM-DD-JSC-###-<slug>-intent.md` when Linear
   is known, otherwise `.harness/features/YYYY-MM-DD-<repo-name>-intent.md`.
   Explain direction, stability, drift risk, leverage, and accidental complexity.
2. Architecture review: `.harness/review/YYYY-MM-DD-JSC-###-<slug>-architecture-review.md`
   or repo-name equivalent. Pressure-test coherence, modularity, domain
   integrity, agent-native design, governance, complexity, and moat claims.
3. Triage: `.harness/triage/YYYY-MM-DD-JSC-###-<slug>-triage.md` or repo-name
   equivalent. Compress intent/review into routing, deletions, anti-drift
   protections, ADR/refactor/eval/governance candidates, and `Do Not Create`.

Do not skip directly to triage unless intent and review are fresh enough. If
stale, sampled, or absent, refresh them or mark triage authority limited.

## Evidence and Stance

Inspect implementation reality before strategic claims: source, configs,
scripts, CI/CD, tests, docs, prompts, skills, workflows, hooks, harness files,
boundaries, telemetry, validation, orchestration, MCP, memory/context, product
language, roadmap/TODO/dead code, repeated abstractions, and coupling. Record
sampling limits, sufficiency, confidence downgrade, and refresh needs.

For repo intent, compare stated intent from docs/prompts/product language with
implied intent from code, command surfaces, validation, tests, runtime paths,
naming, generated artifacts, and coupling. Call out alignment, contradiction,
missing proof, and code that reveals a different strategy than prose.

Every major conclusion must separate hard evidence, strong inference, and weak
assumption/speculation. Do not infer capability from README language, skill
names, or aspiration alone.

## Modern Standards Assessment (May 2026)

Intent and architecture-review artifacts must evaluate the repository against
current May 2026 expectations where relevant: agent-native architecture, AI
workflow ergonomics, repository cognition/discoverability, governance,
deterministic execution, validation loops, observability, typed boundaries,
context management, multi-agent coordination, memory architecture, DX/UX,
security posture, CI/CD maturity, testing realism, harness quality, prompt/skill
composability, operational resilience, portability, modularity, dependency
discipline, maintainability, and scalability. Classify each major area as ahead,
aligned, lagging, overbuilt, underbuilt, wrong-problem, or unusually
differentiated. Use bounded current-source checks when claims are likely to
drift; otherwise record evidence status as `internal-canon`, `unavailable`, or
`not inspected`.

## Lenses

Apply pragmatic engineering, Philosophy of Software Design, DDD, XP/feedback,
structural refactoring, agent-native architecture, and moat pressure lenses. Do
not summarize books. Use supplied reference material when present; otherwise load
`architecture-lens-canon.md` and mark `Reference Lens Status` as
`internal-canon`. Attached material status values: `inspected`, `sampled`,
`unavailable`, `not needed`, `internal-canon`.

Architecture review must use the lenses as pressure systems:

- Pragmatic Programmer: DRY, orthogonality, reversibility, tracer bullets,
  automation, entropy, broken windows, tooling, and maintainability.
- Philosophy of Software Design: deep/shallow modules, cognitive load, change
  amplification, information leakage, pass-through abstractions, interface
  quality, obviousness, strategic versus tactical design, and mixed abstraction
  levels.
- Domain-Driven Design: ubiquitous language, bounded context integrity,
  anti-corruption seams, domain cohesion, context maps, naming stability, and
  model drift.
- XP/feedback: feedback loops, CI, test realism, sustainable iteration,
  pairability, observability, deployability, and safe incremental change.
- Refactoring and structural complexity: giant orchestrators, hidden temporal
  coupling, nested branching, mixed abstraction levels, mutation, choke points,
  and high-risk modules.
- Agent-native architecture: skill/plugin discoverability, prompt
  composability, deterministic execution, context efficiency, machine-readable
  boundaries, eval integration, memory architecture, observability, and
  workflow reproducibility.
- Moat pressure: actual difficulty to copy, measurable compounding leverage,
  operational discipline, governance, cognition systems, trust, eval quality,
  switching costs, distribution, and whether simplification strengthens or
  weakens defensibility.

## Required Sections

Intent must include: Project Intent, Stated Intent, Implied Intent, Alignment,
Core Thesis, Strategic Direction, Intended Users, Non-Goals, System Philosophy,
Architectural Patterns, Agent-Native Assumptions, Harness/Governance Model,
Critical Constraints, Stable Interfaces, Complexity, Leverage, Probable Moat,
Drift Risks, Future-Agent Preserve/Challenge, Open Questions, Recommended
Decisions, Strategic Contradictions, Simplifications, Missing Capabilities,
Scalability Concerns, Modern Standards Assessment (May 2026), Drift Detection
Signals, Direct Strategic Critique, Evidence & Traceability Matrix, and
post_artifact_review_status.

Architecture review must include: Executive Summary, Reference Lens Status,
Architectural Risk Assessment, Repository Cognition Review, Complexity Audit,
Deep vs Shallow Module Analysis, Domain Integrity Review, Skill/Plugin
Architecture Review, Agent-Native Capability Review, Governance & Workflow
Review, Refactor Recommendations, Anti-Patterns Identified, Drift Risks,
Technical Debt Hotspots, Strategic Review, Recommended Simplifications/
Deletions/Core Investments, Long-Term Scalability Risks, Moat Analysis,
Competitive Replication Risk, Evidence & Traceability Matrix, and
post_artifact_review_status.

Triage must include: Executive Triage Summary, Immediate Architectural Risks,
Strategic Findings, Architectural Findings, Operational Findings, Governance
Findings, Agent-Native Findings, Complexity Without Leverage, Moat-Critical
Systems, Fake Sophistication Signals, Recommended Deletions, Refactor
Candidates, Anti-Drift Priorities, Execution Priority Matrix, Recommended Linear
Initiatives, Recommended ADRs, Recommended Refactor Programs, Future Agent
Operational Risks, Recommended Compression Opportunities, Evidence &
Traceability Matrix, and post_artifact_review_status.

## Architecture Review Contract

The review must inspect implementation reality before claims and distinguish
facts, strong inferences, and weak/speculative assumptions. It must not rely on
README positioning, marketing language, skill names, or aspiration alone.

For every major conclusion, include evidence, affected files or modules,
architectural impact, confidence level, and why it matters. Use evidence
categories such as source code, prompts, orchestration flows, skills, plugins,
CI/CD, runtime paths, naming patterns, tests, dependency graph, architecture
boundaries, telemetry, governance, and developer workflows.

The moat section must explicitly answer: actual moat, durability,
measurability, whether it is merely complexity, whether a smaller competitor
could rebuild it quickly, strategically defensible parts, sophisticated-looking
but non-defensible parts, what to protect, what to simplify, false moat
assumptions, and why competitors would or would not catch up.

The strategic review must be direct: coherence, complexity justification,
pragmatism, abstraction quality, overbuild, real problem fit, governance drag or
help, leverage, deletions, core investments, likely wrong assumptions, smallest
compelling version, operational scalability, developer adoption, cognition
quality, fragility, failure mode, and success reason.

## Structural Triage Contract

Structural triage consumes fresh-enough `.harness/features/*.md` and
`.harness/review/*.md`; it classifies and routes instead of repeating,
specifying, or backlog-dumping.

It must explicitly separate signal from noise: high leverage, medium leverage,
low leverage, and false sophistication. It must identify which findings should
not become work items.

Per finding: buckets strategic/architectural/operational/agent-native/
governance/technical-debt; leverage `high|medium|low|false_sophistication`;
route `Linear initiative|project|issue|ADR|refactor program|eval program|
governance change|routing change|anti-drift enforcement|Do Not Create`;
`should_become_work`; fact/interpretation/speculation; files/modules;
confidence; operational/strategic impact; why it matters.

Risk rows: severity, likelihood, blast radius, response. Complexity/deletion
rows: why-exists, why-survived, why-harmful/removable, action
`remove|collapse|merge|simplify|ignore|preserve`. Matrix columns:
impact `critical|high|medium|low`; complexity `trivial|moderate|difficult|migration-risk`;
importance `moat-critical|operational|architectural|cosmetic`; risk
`drift|migration|regression|governance|cognition`; route; `should_become_work`.

Anti-drift rows: determinism, cognition, local reasoning, hidden coupling,
execution simplicity, future-agent reasoning. Future-agent risks: context cost,
orchestration ambiguity, misleading abstractions, local reasoning, determinism,
discoverability, token cost.

Recommended Linear initiatives, ADRs, refactor programs, eval programs,
governance changes, routing changes, and anti-drift protections must be routed
only when the finding survives the leverage filter. Otherwise mark it
`Do Not Create`.

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

For repo intent, architecture-review, and triage artifacts, save the artifact,
use `request_user_input` for a focused review loop when available, apply
material corrections, and record `post_artifact_review_status`. If
`request_user_input` is unavailable or the run is headless, mark the review
loop `blocked` with the concrete reason and record assumption risk instead of
pretending the shared review happened.

Intent, review, and triage are durable secondary context. They do not authorize
implementation. Route candidates to ADR, reframe program, Linear, eval program,
governance change, or `Do Not Create`. Write `No Linear items` when no Linear
work is justified.

End with `Direct Strategic Critique`: coherence, complexity justification, real
leverage, drag, deletion candidates, smallest compelling version, biggest failure
mode, and the single best next strategic move.
