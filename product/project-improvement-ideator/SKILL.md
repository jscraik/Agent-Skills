---
name: project-improvement-ideator
description: "Generate and winnow project improvement ideas to a top 5. Use when asked for roadmap/improvement ideas."
---

# Project Improvement Ideator

Concise workflow to brainstorm broadly (30 ideas) and converge to the top 5 that are impactful, feasible, and aligned.

- Check against GOLD Industry Standards guide in ~/.codex/AGENTS.override.md.
- Keep outputs concise and decision-oriented; avoid boilerplate.

## Quick mental model
- Axes: Impact × Feasibility × Alignment × Time-to-value × Risk.
- Audience lenses: developers, ops/sec, users/stakeholders.
- Favor ideas that are incremental yet defensible (“gold standard” ready).

## Steps (high freedom)
1) Clarify context (if missing: stack, user goals, constraints). Assume current repo state otherwise.
2) Generate 30 ideas rapidly (bullets, 1 line each). Cover breadth: reliability, performance, security, DX, UX, governance, observability.
3) Expand each idea briefly: user perception, how it works, implementation sketch, risk/mitigation (1–2 lines).
4) Score each idea (1–5) on: Impact, Feasibility, Alignment, Time-to-value. Note major risks if any.
5) Winnow: sort by composite score (tie-breaker = lower risk / faster value). Select top 5.
6) Present the 5 in rank order with: title, why it helps (1–2 sentences), how to implement (1–3 bullets), risks/mitigations (1 bullet).
7) (Optional) Provide a short next-step plan (MVP slice) if requested.

## Output format
- Section “Top 5 (ranked)” with the details above.
- Section “Scoring summary” (table or bullets with scores).
- Keep the full 30 ideas list concise; include it after the top 5.

## Guardrails
- No new deps unless explicitly justified and low risk.
- Prefer incremental changes; call out when an idea is a larger initiative.
- Note if any idea depends on unpublished/private assets or policies.
- Keep assumptions explicit (dates, environments, platforms).

## References
- Contract: references/contract.yaml
- Evals: references/evals.yaml

## When to use
- Use this skill when the task matches its description and triggers.
- If the request is outside scope, route to the referenced skill.


## Inputs
- User request details and any relevant files/links.


## Outputs
- A structured response or artifact appropriate to the skill.
- Include `schema_version: 1` if outputs are contract-bound.


## Constraints
- Redact secrets/PII by default.
- Avoid destructive operations without explicit user direction.


## Validation
- Run any relevant checks or scripts when available.
- Fail fast and report errors before proceeding.


## Philosophy
- Favor clarity, explicit tradeoffs, and verifiable outputs.


## Anti-patterns
- Avoid vague guidance without concrete steps.
- Do not invent results or commands.
## Procedure
1) Clarify scope and inputs.
2) Execute the core workflow.
3) Summarize outputs and next steps.

## Antipatterns
- Do not add features outside the agreed scope.
