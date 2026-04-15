---
date: 2026-02-24
topic: skill-graph-live-auto-learning
---

# Skill Graph Live Auto-Learning (Phase 4 Activation Brainstorm)

## Table of Contents
- [What We're Building](#what-were-building)
- [Why This Approach](#why-this-approach)
- [Approaches Considered](#approaches-considered)
- [Success Criteria](#success-criteria)
- [Scope Boundaries](#scope-boundaries)
- [Key Decisions](#key-decisions)
- [Resolved Questions](#resolved-questions)
- [Open Questions](#open-questions)
- [Next Steps](#next-steps)

## What We're Building
We will complete the remaining gap between existing recursive-loop automation and true end-to-end learning from normal skill usage. The new scope adds two missing behaviors: (1) automatic post-use capture after every skill invocation, and (2) runtime lesson retrieval/injection so approved lessons can influence future runs.

This work builds on what already exists from the 2026-02-19 and 2026-02-23 plans: shadow runs/reporting, scheduled workflow execution, and promotion queue artifact generation. The new target is to make daily skill usage itself produce learning signals and safely apply trusted lessons in live execution.

## Why This Approach
We chose a best-effort evidence model with confidence scoring because it balances learning velocity and safety. Strict-only evidence would miss too many real-world runs; fully unfiltered auto-application risks noisy guidance.

The design also keeps YAGNI discipline: start with single injection at run start, simple one-tap feedback, and strong kill-switch controls. This reduces rollout risk while still delivering meaningful autonomous improvement.

## Approaches Considered
### Approach A: Strict evidence-only learning
Capture only when high-confidence proof exists (for example diff + checks + trace/log corroboration).

**Pros:** high trust, low noise, simpler governance review.
**Cons:** misses many real sessions, slower learning loop, weaker coverage across skills.
**Best when:** safety/compliance risk dominates over learning velocity.

### Approach B: Best-effort capture + confidence scoring (selected)
Capture every run, score evidence quality, and prioritize stronger evidence during ranking and promotion.

**Pros:** broad coverage, faster feedback loop, still safety-aware via confidence weighting and kill switches.
**Cons:** requires confidence calibration and periodic quality tuning.
**Best when:** you want continuous learning without waiting for perfect telemetry every time.

### Approach C: Fully implicit autonomous learning
Capture and apply broadly with minimal user prompts or confidence gating.

**Pros:** fastest loop, lowest user friction.
**Cons:** highest drift risk, weakest explainability, harder to audit incorrect guidance.
**Best when:** experimentation speed matters more than reliability/auditability.

## Success Criteria
- Every skill invocation produces a capture record (system + user one-tap outcome).
- Evidence confidence is attached to each candidate lesson.
- Runtime applies relevant lessons at start-of-run and logs which lessons were injected.
- Low-confidence lessons are visible but down-ranked.
- Global and per-skill kill switches can immediately disable auto-capture and/or auto-apply.

## Scope Boundaries
**In scope (this phase):** post-run capture prompt, confidence-scored lesson candidates, start-of-run retrieval/injection, safety controls.

**Out of scope (defer to later phase):** continuous mid-run re-injection, fully autonomous promotion with no human gate, broad runtime orchestration redesign.

## Key Decisions
- Trigger capture on **every skill invocation**.
- Show prompt **immediately after each run**.
- Use **best-effort evidence scoring** (logs/traces/sessions/diffs/checks) rather than strict-only capture.
- Use **one-tap review UX**: Worked / Partly / Didn’t work (+ optional note).
- Auto-apply lessons at **start-of-run only** in v1.
- Roll out with **pilot-first kill switches** (global and per-skill disable).
- **Low-confidence lessons are still injectable** but ranked lower and flagged.

## Resolved Questions
- Should learning trigger for all skills or pilots only? → **All skills**.
- Prompt timing? → **Immediate post-run**.
- Evidence policy? → **Best-effort with confidence**.
- Runtime injection timing? → **Start-of-run only**.
- Rollout safety model? → **Pilot-first with kill switches**.
- Low-confidence handling? → **Inject with lower rank + warning**.

## Open Questions
None for brainstorming scope. Implementation sequencing, schema deltas, and rollout checks move to planning.

## Next Steps
→ `/workflows:plan` to define architecture changes, event/schema additions, confidence computation contract, retrieval ranking policy, and staged rollout verification.
