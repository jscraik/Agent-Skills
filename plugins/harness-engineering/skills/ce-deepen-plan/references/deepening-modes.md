# CE Deepen Plan Modes

Read when: you need to choose between targeted-confidence and max-coverage, decide whether artifact-backed execution is warranted, or score which plan sections deserve intervention.

## Table of Contents
- [Purpose](#purpose)
- [Deepening modes](#deepening-modes)
- [Plan depth and risk](#plan-depth-and-risk)
- [Section scoring](#section-scoring)
- [Agent mapping](#agent-mapping)
- [Execution modes](#execution-modes)
- [Legacy coverage preservation](#legacy-coverage-preservation)

## Purpose
This reference preserves the behavior of both `deepen-plan` and `deepen-plan-beta` while making the modern default explicit.

## Deepening modes
### `targeted-confidence`
Use by default.

Best for:
- standard or deep plans with 2-5 weak sections
- high-risk plans where stronger rationale, sequencing, verification, or risk treatment matters more than full exhaust
- users who want a safer second pass without massive context growth

Rules:
- choose only the top 2-5 sections by score
- use at most 1-3 agents per section
- usually keep the total research fan-out to 8 agents or fewer
- rewrite only the selected weak sections

### `max-coverage`
Use only when the user explicitly asks for exhaustive coverage or when preserving the legacy prompt's broad fan-out is clearly the right call.

Best for:
- explicit "run everything" requests
- existentially risky or politically sensitive work where multiple reviewer lenses are wanted
- preserving the original deepen-plan workflow's broad coverage strengths

Rules:
- still build a section manifest first
- discover skills, agents, and learnings from the current platform, project, and installed registries when available
- apply clearly relevant skills
- scan deeper learnings under `docs/solutions/`
- run a broader reviewer sweep
- synthesize findings back into the plan instead of pasting raw agent output

## Plan depth and risk
### Plan depth
- `lightweight`: small, bounded, low ambiguity, usually 2-4 implementation units
- `standard`: moderate complexity, some technical decisions, usually 3-6 units
- `deep`: cross-cutting, high-risk, or strategically important, usually 4-8 units or phased delivery

### High-risk signals
- authentication or authorization
- payments, billing, or financial flows
- migrations, backfills, or persistent data changes
- external APIs or third-party integrations
- privacy, compliance, or user-data handling
- cross-interface parity
- rollout, monitoring, or operational safety concerns

## Section scoring
Use a checklist-first, risk-weighted scoring pass.

For each section:
- trigger count = number of checklist problems that apply
- risk bonus = +1 when the topic is high risk and the section materially affects that risk
- critical-section bonus = +1 for `Key Technical Decisions`, `Implementation Units`, `System-Wide Impact`, `Risks & Dependencies`, or `Open Questions` in `standard` or `deep` plans

Treat a section as a candidate if:
- it scores 2 or more total points, or
- it scores 1 or more point in a high-risk domain and is materially important

Checklist triggers:
- `Requirements Trace`
  - requirements are vague or disconnected from units
  - success criteria do not flow downstream
  - origin requirements are not clearly carried forward
- `Context & Research / Sources & References`
  - cited research never affects decisions or units
  - high-risk work lacks repo or external grounding
  - research is generic instead of plan-specific
- `Key Technical Decisions`
  - decisions lack rationale or tradeoffs
  - obvious forks are not explained
- `Open Questions`
  - product blockers are hidden as assumptions
  - planning-owned questions are incorrectly deferred
- `High-Level Technical Design`
  - wrong medium, too prescriptive, or absent where it would materially help
- `Implementation Units`
  - dependency order is weak
  - file paths or test paths are missing
  - units are too vague or too granular
  - verification outcomes are thin
- `System-Wide Impact`
  - affected interfaces, parity surfaces, or failure propagation are underexplored
  - data integrity, caching, or integration scenarios are missing
- `Risks & Dependencies / Operational Notes`
  - risks lack mitigation
  - rollout, monitoring, migration, privacy, or security concerns are missing when relevant

## Agent mapping
Use `references/sub-agent-map.md` as the canonical lane map.

Default lanes:
- `repo-research-analyst`
- `learnings-researcher`

Then add only the specialist lanes that match selected weak sections (for example `feasibility-reviewer`, `scope-guardian-reviewer`, `security-lens-reviewer`, `reliability-reviewer`, `deployment-verification-agent`, `api-contract-reviewer`).

## Execution modes
### `direct`
Default.

Use when:
- the selected research scope is small
- inline findings will not create avoidable context pressure

### `artifact-backed`
Use only when:
- more than 5 agents are likely to return meaningful findings
- long section excerpts would be repeated wastefully
- the topic is high risk and bulky research output is likely

Scratch path:
- `.context/compound-engineering/ce-deepen-plan/<run-id-or-plan-stem>/`

Artifact rules:
- one compact artifact per section or reviewer cluster
- findings only, no implementation code, no command recipes
- clean up unless the user asked to inspect them

## Legacy coverage preservation
The original `deepen-plan` prompt was intentionally broad:
- dynamic skill discovery
- learning discovery under `docs/solutions/`
- per-section research fan-out
- broad review-agent coverage

The migrated skill preserves those behaviors inside `max-coverage` mode rather than forcing them on every deepening run.
