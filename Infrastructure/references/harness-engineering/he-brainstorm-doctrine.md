# Harness Engineering Brainstorm Doctrine

This is the retained long-form doctrine for `he-brainstorm`. Keep active `SKILL.md` and skill-local references compact; use this file when a brainstorm needs full facilitation, requirements capture, synthesis, visual communication, or handoff detail.

## Role

Be a thinking partner, not an answer machine. The user is exploring, stuck, or aligning stakeholders. Understand before generating; ask what they already think, what they tried, what they rejected, and what would make the work not worth doing.

## Scope Tiers

- `lightweight`: clear topic, small uncertainty, 1-3 decisions, often no durable artifact.
- `standard`: several unknowns, meaningful tradeoffs, likely requirements artifact.
- `deep-feature`: user behavior, success criteria, boundaries, and expected behavior need shaping.
- `deep-product`: strategy, audience, positioning, onboarding promise, or cross-workstream decisions.

Universal and non-software tasks still use HE stage names and output discipline, but use native domain language rather than forcing software categories.

## Discovery

Ask one focused question per turn. Prefer a blocking question tool when the choices are bounded; include free text when available. Use prose only when options would bias the answer, the answer is narrative, or choices would be padded.

If the subject is missing, ask what to explore. Do not invent a subject unless the user explicitly asks to be surprised. When the user represents a team, surface whose preferences matter and where they diverge.

When repo, Linear, transcript, strategy, spec, plan, or QA evidence is relevant, inspect it before stating what exists. If inspection is impossible, label the claim as an assumption and keep it out of requirements until confirmed.

## Divergence And Warrants

Separate generation from evaluation. Generate many internal candidates across first principles, inversion, constraints, analogy transfer, stakeholder impact, and rejection criteria. Critique them before showing the strongest 2-5 survivors.

Each survivor needs a warrant:
- `direct`: user asked for it or reacted positively.
- `repo`: supported by code, docs, Linear, specs, plans, telemetry, or artifacts.
- `external`: supported by current external research.
- `reasoned`: plausible first-principles argument or analogy, clearly labeled.

## Synthesis Checkpoint

Before writing a durable artifact, present a scope checkpoint with:
- `Stated`: direct user or artifact claims.
- `Inferred`: agent bets that need correction.
- `Out of scope`: deliberate exclusions.

The synthesis is not a requirements draft. Keep bullets scope-level and affirmable without reading code. Do not include file paths, schemas, APIs, exact labels, or implementation details unless the brainstorm is explicitly technical. If the user revises anything, re-present the synthesis and wait for confirmation again.

In headless mode, compose the synthesis for auditability but do not ask for confirmation. Route unconfirmed `Inferred` items to `## Assumptions`, never requirements or key decisions.

## Requirements Artifact

Default path: `docs/brainstorms/YYYY-MM-DD-<topic>-requirements.md`. Use repo-relative paths inside artifacts.

Frontmatter: `schema_version`, `source: he-brainstorm`, `created`, `mode`, `scope_tier`, `spec_required`, `risk_level`, `complexity`, and `next_stage`.

Sections:
- `## Summary`: 1-3 lines describing the destination.
- `## Problem Frame`: why current state is insufficient.
- `## Requirements`: stable IDs when traceability matters.
- `## Success Criteria`: observable acceptance.
- `## Key Decisions`: accepted choices.
- `## Scope Boundaries`: included and excluded work.
- `## Dependencies and Assumptions`: confirmed assumptions only, except headless `## Assumptions`.
- `## Resolve Before Planning`: blockers.
- `## Deferred to Planning`: HOW questions safe to defer.
- `## Next Stage`: HE route and rationale.

Use `R`, `A`, `F`, and `AE` IDs for requirements, assumptions, flows, and acceptance examples when later traceability matters. Lightweight artifacts may omit IDs.

## Visual Communication

Use visuals only when they improve comprehension:
- Workflow or process: Mermaid or ASCII flow.
- Three or more states or variants: comparison table.
- Three or more roles, systems, or services: relationship diagram.
- Competing approaches: comparison table.

Keep visuals conceptual. Implementation architecture, schemas, code structure, and data models belong in `he-plan` unless the brainstorm is specifically about that contract. Prose governs if a visual disagrees with surrounding text.

## Handoff

Offer only valid next routes:
- `he-spec`: default for non-trivial clarified work needing a contract.
- `he-plan`: only when requirements are contract-grade and no WHAT ambiguity remains.
- `he-work`: tiny, low-risk work with no behavior ambiguity.
- `he-review`: critique the artifact before proceeding.
- Done: when the conversation itself was the value.

Hide plan/build when `Resolve Before Planning` has blockers. Do not proceed if the next stage would need to invent user-facing behavior.

## Review Pass

Before handoff, verify subject, audience, value, expected behavior, mode, scope tier, spec requirement, risk, complexity, traceable requirements, true blockers, canonical domain terms, evidence-tied recommendation, and visual/prose agreement.
