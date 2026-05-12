# Repository Cognition Pipeline

Use this reference when the user asks for the full repo-intent, architecture
review, and structural triage workflow, or says the current `he-strategy`
contract does not capture their long-form prompt deeply enough.

This is a multi-artifact strategy pipeline, not a generic documentation task.
It exists to turn implementation reality into durable cognition surfaces that
future humans and coding agents can use without rereading the whole repo.

## Pipeline Mode

Select `repo-cognition-pipeline` only when the user explicitly asks for more
than one of these artifacts in sequence:

- repository intent under `.harness/features/`
- architecture cognition review under `.harness/review/`
- structural triage under `.harness/triage/`

When only one artifact is requested, use the matching single mode from
`strategy-output-contract.md`.

## Required Artifact Sequence

1. Intent artifact:
   - path: `.harness/features/YYYY-MM-DD-<repo-name>-intent.md`
   - purpose: explain what the repository is trying to become, what must stay
     stable, what must never drift, what is intentional leverage, and what is
     accidental complexity.
2. Architecture review:
   - path: `.harness/review/YYYY-MM-DD-<repo-name>-architecture-review.md`
   - purpose: pressure-test coherence, modularity, domain integrity,
     agent-native architecture, governance, complexity, and moat claims through
     pragmatic engineering lenses.
3. Structural triage:
   - path: `.harness/triage/YYYY-MM-DD-<repo-name>-triage.md`
   - purpose: compress the intent and review into execution priorities,
     deletion candidates, anti-drift protections, ADR candidates, refactor
     programs, Linear initiatives, and work that should explicitly not become
     a work item.

Do not skip directly to triage unless current intent and review artifacts are
fresh enough to support it. If they are stale, sampled, or absent, either
refresh them or mark triage authority limited.

## Evidence Depth

Inspect implementation reality before strategic claims. Relevant surfaces
include source code, configs, manifests, scripts, CI/CD, tests, docs, prompts,
skills, workflows, hooks, agent harness files, architecture boundaries,
telemetry, observability, infrastructure assumptions, validation loops,
orchestration logic, MCP integrations, memory/context systems, product language,
roadmap signals, TODO clusters, dead code, repeated abstractions, and coupling
patterns.

Use bounded sampling only when repo size or time makes full inspection
impractical. When sampling, record:

- inspected surfaces
- not-inspected surfaces
- why the sample is sufficient or insufficient
- confidence downgrade
- follow-up refresh needed before using the artifact as repo-wide authority

## Required Analysis Stance

Every major conclusion must separate:

- hard evidence from repo files, validation output, or generated artifacts
- strong inference from repeated implementation patterns
- weak assumption or speculation

Do not infer capabilities from README language, skill names, or architectural
aspiration alone. Strategy must be grounded in behavior, contracts, validators,
runtime paths, or repeated implementation shape.

## Strategic Lenses

Apply these lenses when the artifact asks for architecture review, moat review,
or strategic critique:

- Pragmatic Programmer: entropy, DRY, orthogonality, reversibility, tracer
  bullets, automation maturity, operational friction, broken windows.
- Philosophy of Software Design: deep versus shallow modules, change
  amplification, information leakage, hidden dependencies, pass-through
  abstractions, cognitive load.
- Domain-Driven Design: ubiquitous language, bounded contexts, context leakage,
  model integrity, anti-corruption boundaries, strategic domain cohesion.
- Extreme Programming: feedback loops, CI quality, humane iteration,
  pairability, sustainable cadence, test realism, incremental safety.
- Structural refactoring: giant orchestrators, hidden temporal coupling, mixed
  abstraction levels, brittle conditionals, mechanical simplification seams.
- Agent-native architecture: discoverability, context loading, deterministic
  execution, machine-readable boundaries, eval integration, memory architecture,
  prompt composability, local reasoning, and token cost.

Do not summarize these schools. Use them as pressure systems for judging this
repository.

## Mandatory Sections For The Full Pipeline

Intent artifacts must include:

- Project Intent
- Core Thesis
- Strategic Direction
- Intended Users
- Non-Goals
- System Philosophy
- Architectural Patterns
- Agent-Native Design Assumptions
- Harness/Governance Model
- Critical Constraints
- Stable Interfaces
- Sources of Complexity
- Sources of Leverage
- Probable Moat
- Drift Risks
- What Future Agents Should Preserve
- What Future Agents Should Challenge
- Open Questions
- Recommended Decisions
- Strategic Contradictions
- Suggested Simplifications
- Missing Capabilities
- Long-Term Scalability Concerns
- Drift Detection Signals
- Evidence & Traceability Matrix

Architecture reviews must include:

- Executive Summary
- Architectural Risk Assessment
- Repository Cognition Review
- Complexity Audit
- Deep vs Shallow Module Analysis
- Domain Integrity Review
- Skill/Plugin Architecture Review
- Agent-Native Capability Review
- Governance & Workflow Review
- Refactor Recommendations
- Anti-Patterns Identified
- Drift Risks
- Technical Debt Hotspots
- Strategic Review
- Recommended Simplifications
- Recommended Deletions
- Recommended Core Investments
- Long-Term Scalability Risks
- Moat Analysis
- Competitive Replication Risk
- Evidence & Traceability Matrix

Triage artifacts must include:

- Executive Triage Summary
- Immediate Architectural Risks
- Strategic Findings
- Architectural Findings
- Operational Findings
- Governance Findings
- Agent-Native Findings
- Complexity Without Leverage
- Moat-Critical Systems
- Fake Sophistication Signals
- Recommended Deletions
- Refactor Candidates
- Anti-Drift Priorities
- Execution Priority Matrix
- Recommended Linear Initiatives
- Recommended ADRs
- Recommended Refactor Programs
- Future Agent Operational Risks
- Recommended Compression Opportunities
- Evidence & Traceability Matrix

## Drift Detection Signals

For every intent or architecture review, define explicit drift indicators. Use
measurable thresholds where possible:

- duplicated orchestration logic exceeds one canonical owner per workflow
- prompt/context grows without eval or outcome improvement
- skills become undiscoverable or generated handles drift from source
- governance rules are not enforced by CI or local validation
- runtime paths sidestep validation loops
- memory/context systems become non-deterministic
- compatibility layers survive past their decision deadline
- framework/tool proliferation grows without capability consolidation
- onboarding or repo discovery requires broad transcript archaeology
- PR validation time increases without stronger safety evidence
- unresolved TODO or dead-workflow debt exceeds the repo's chosen threshold

For each signal include why it matters, likely root cause, operational impact,
severity, corrective action, and whether it should block merges or releases.

## Moat Pressure Test

Do not treat sophistication as moat. Explicitly decide whether defensibility
comes from data, workflow discipline, eval quality, orchestration reliability,
governance, repository cognition, trust, switching cost, developer habit, or
distribution.

Answer directly:

- what is actually hard to copy
- what only feels sophisticated
- what should be protected
- what should be simplified because it weakens the moat
- what assumptions are likely false
- whether the moat survives simplification
- why competitors would or would not catch up quickly

If no real moat exists, say so.

## Clarification Loop

Ask focused clarification questions only when the answer materially changes
architecture direction, product intent, moat, governance, agent workflows,
scalability, UX philosophy, or commercial positioning.

Use `request_user_input` when available. If it is unavailable in the current
runtime, ask directly or record the ambiguity as an explicit open question and
continue with the safest evidence-backed assumption.

## Authority And Handoff

Intent, review, and triage artifacts are durable secondary context. They do not
authorize implementation by themselves.

After triage, route execution candidates to the smallest appropriate artifact:

- ADR for policy or architectural decisions
- refactor program for structural migrations
- Linear initiative/project/issue for execution tracking
- eval program for behavior proof
- governance change for anti-drift enforcement
- `Do Not Create` for findings that sound sophisticated but should not become
  work

End with a short strategic assessment that is direct enough to be useful:
coherence, complexity justification, real leverage, drag, deletion candidates,
smallest compelling version, biggest failure mode, and the single best next
strategic move.
