# Style and Operating Guidance

Read when: you need standards rationale, planning philosophy, or variation guidance beyond route-critical behavior in `SKILL.md`.

## Table of Contents
- [April 2026 standards snapshot](#april-2026-standards-snapshot)
- [Planning philosophy](#planning-philosophy)
- [Guiding questions](#guiding-questions)
- [Variation guidance](#variation-guidance)

## April 2026 standards snapshot
- Keep each skill scoped to one reusable job and make the description say what it does and when to use it.
- Prefer explicit routing, realistic examples, and validation over prompt-only procedures.
- Use repo guidance, origin context, and prior learnings before external research.
- Plan workflows, keep one current step in focus, and use bounded research by default.

## Planning philosophy
- Plan quality comes from decisions and rationale, not task-count inflation.
- Preserve portability: plans should travel cleanly across machines, worktrees, and collaborators.
- Keep planning and execution separate: resolve planning-time unknowns, defer runtime unknowns.
- Right-size depth to risk: lightweight plans stay compact; high-risk plans earn richer structure.
- Use optional sections only when they materially improve confidence, not as boilerplate.

## Guiding questions
- Can an implementer start confidently without inventing missing architecture?
- Does each acceptance item clearly map back to a governing source?
- Are dependencies and exit criteria explicit enough to prevent sequencing churn?
- Would a reviewer understand tradeoffs and blast radius without extra meetings?

## Variation guidance
Outputs should vary with source quality, scope, and risk profile.
- Well-scoped bug fixes should produce compact, direct plans.
- Cross-boundary or externally coupled work should surface stronger risk and contract checks.
- UI-heavy work should show clearer prototype and visual-validation planning.
- Low-signal requests should carry lower confidence and tighter assumptions.
- High-signal source docs should reduce planning speculation and increase traceability density.
