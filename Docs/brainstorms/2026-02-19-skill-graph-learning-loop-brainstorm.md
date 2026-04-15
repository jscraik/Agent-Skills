---
date: 2026-02-19
topic: skill-graph-learning-loop
---

# Skill Graph Learning Loop (v1)

## What We're Building
We are defining a generic skill-learning framework that starts with UI/UX-oriented skills and can later expand to all skills in the repository. The core goal is to make agents measurably better over time by reducing repeated mistakes and reusing proven decisions.

In v1, each relevant skill run emits structured lesson drafts (what worked, what failed, constraints, confidence, evidence). Drafts are reviewed quickly by a human and promoted into canonical knowledge only when they meet quality criteria. Promoted lessons become graph nodes linked to related skills, patterns, and prior lessons.

## Why This Approach
We selected a two-tier model (Drafts → Canonical Graph) as the best balance between learning speed and signal quality. Fully automatic memory risks noisy or contradictory guidance, while manual-only capture is too slow and easy to skip.

This hybrid model gives immediate learning velocity while keeping the canonical graph trustworthy, creating a practical path from a lightweight v1 to a richer graph-native system (v2/v3).

## Key Decisions
- **Scope:** Build a generic framework that starts with UI skills, then expands repo-wide.
- **Primary outcome:** Fewer repeated mistakes and better output quality over time.
- **Capture model:** Hybrid—auto-generate lesson drafts, require human promotion for canonical inclusion.
- **Architecture direction:** Implement Approach A now, intentionally design toward eventual Approach C.
- **YAGNI guardrail:** Keep v1 minimal (capture, review, promote, retrieve) and avoid full graph complexity until value is proven.
- **Rollout shape:** Run as a pilot with a small initial UI-skill set before generalization.

## Out of Scope (v1)
- Fully autonomous canonical updates with no human gate.
- Full graph ontology/governance framework across every domain.
- Complex ranking/reasoning pipelines beyond basic relevance retrieval.

## Open Questions
- What promotion rubric is required (confidence threshold, evidence requirements, staleness rules)?
- Where should canonical memory live first (repo markdown graph vs structured store vs dual-write)?
- Which retrieval hooks run first (skill load-time only, or also mid-task on failure patterns)?
- What minimum telemetry proves quality improvement with low operational overhead?

## Next Steps
→ `/prompts:workflows-plan` to define implementation strategy, data model, and rollout sequence.
