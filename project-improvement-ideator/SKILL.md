---
name: project-improvement-ideator
description: Generate 30 pragmatic improvement ideas for the current project, weigh feasibility/impact/user perception, then winnow to the best 5 with rationale. Use when asked for “best ideas”, “improvements”, “roadmap”, or “top 5”/“winnow” prioritization. Not for full product specs or LLM design reviews; use product-spec or llm-design-review.
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
