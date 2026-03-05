---
date: 2026-03-04
topic: skill-router
---

# Skill Router (Intent-First) Brainstorm

## What We’re Building
A v1 skill-router that maps ambiguous user requests to the most likely skills before execution. The router should support both humans and AI coding agents by returning a deterministic, auditable result: top 3 candidate skills, confidence scores, and short rationale. The first version stays lightweight and CLI/report-first (no heavy interactive UI).

Primary goal: improve first-choice routing quality so users and agents start with the correct skill more often, with less corrective back-and-forth.

## Why This Approach
We considered three options: deterministic scorecard routing, deterministic routing with confirmation prompts on uncertainty, and hybrid rules+LLM tie-breaking. We selected deterministic scorecard routing for v1 because it is the simplest useful slice (YAGNI), easiest to audit/govern, and most aligned with current repo governance posture.

This also reduces operational risk: no model dependency for core routing, clearer failure modes, and easier baseline measurement of first-hit accuracy before adding complexity.

## Key Decisions
- **User target**: Optimize for both humans and agents in the same output contract.
- **Success metric**: First-hit routing accuracy is the primary v1 KPI.
- **Routing strategy**: Rule-first deterministic scorecard, not LLM-first.
- **Output shape**: Top 3 skills + confidence + rationale.
- **Surface**: CLI/report-first for faster adoption and lower implementation overhead.
- **Complexity posture**: Defer hybrid/model tie-breakers until deterministic baseline is proven.

## Resolved Questions
- **Who is v1 for?** Both humans and agents.
- **What matters most?** Higher first-hit accuracy.
- **How should routing work first?** Rule-first deterministic scoring.
- **How should v1 be delivered?** CLI/report output first.

## Open Questions
- None for current v1 scope.

## Next Steps
Proceed to planning to define the implementation shape, data sources for scoring, evaluation harness, and acceptance checks.
