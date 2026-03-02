# Separation of Concerns

Solve one design question at a time using the minimum fidelity needed to validate that question.

---

## Table of Contents
- [When to Use](#when-to-use)
- [Core Principle](#core-principle)
- [Workflow](#workflow)
- [Fidelity Guidance](#fidelity-guidance)
- [Output Format](#output-format)

## When to Use

Use when users ask to:
- prototype an interaction quickly
- avoid overbuilding too early
- focus only on one concern (motion, layout, copy, information flow, etc.)
- plan a staged design/build workflow

## Core Principle

Do not solve everything in one pass.
Pick one question, build the smallest artifact that answers it, then decide what to do next.

## Workflow

1. **Define the concern**
   - What exact question are we resolving?

2. **Choose fidelity intentionally**
   - wireframe, toy prototype, interactive shell, or production-like slice

3. **Build a breakable toy**
   - minimal surface area
   - only elements needed to evaluate the concern
   - avoid full production styling unless it is part of the concern

4. **Evaluate outcome**
   - did this de-risk the concern?
   - continue depth, or return to range?

5. **Escalate fidelity only when justified**
   - move to richer visuals/content only after concern is validated

This pairs naturally with [recreate-everything.md](recreate-everything.md) for rapid learning loops.

## Fidelity Guidance

- **Low fidelity**: early concept confidence checks
- **Mid fidelity**: interaction and behavior confidence
- **High fidelity**: final polish and implementation confidence

Match artifact fidelity to decision stakes and audience needs.

## Output Format

```md
## Concern to Resolve
[single question]

## Minimal Artifact
[what to build and what to exclude]

## Success Criteria
[signals that concern is resolved]

## Next Decision
[go deeper / explore new range / change concern]
```
