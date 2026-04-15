# Frontend UI Design Intervention: Accessibility Before Polish

Documentation-stage Ars Contexta intervention note for stabilizing `frontend-ui-design` before promoting any pattern into a reusable skill or hook.

## Table of Contents
- [When to retrieve](#when-to-retrieve)
- [Intervention summary](#intervention-summary)
- [Guidance](#guidance)
- [Checkpoints](#checkpoints)
- [Seed evidence](#seed-evidence)
- [Promotion boundary](#promotion-boundary)

## When to retrieve

Retrieve this note before iteration 1 when the active profile is `frontend-ui-design` and the objective asks for production-ready screen guidance with explicit states, accessibility behavior, and restrained composition.

## Intervention summary

Front-load accessibility and state coverage before decorative polish. Reuse restraint and composition wins only after the guidance explicitly restates keyboard focus, contrast, reduced-motion behavior, and the full default/loading/empty/error/disabled state matrix.

## Guidance

- Start with one primary action and a complete state matrix before adding secondary visual differentiation.
- Name keyboard focus order, contrast expectations, and reduced-motion behavior explicitly instead of implying them.
- Keep composition restrained; do not introduce decorative complexity until the accessibility contract is already complete.
- Prefer file-path-specific implementation guidance and measurable verification steps over generic design language.

## Checkpoints

- Did the guidance restate default, loading, empty, error, and disabled states?
- Did the guidance define keyboard focus, contrast, and reduced-motion requirements?
- Did the proposed visual polish preserve clarity and avoid reopening accessibility regressions?

## Seed evidence

- [/Infrastructure/artifacts/skill-graphs/runs/run_20260331T143101180026Z_2ac1a9_bffd74d5/run.json](/Users/jamiecraik/dev/agent-skills/Infrastructure/artifacts/skill-graphs/runs/run_20260331T143101180026Z_2ac1a9_bffd74d5/run.json)
- [/Infrastructure/artifacts/skill-graphs/runs/run_20260331T141226543802Z_fc9894_15c48010/run.json](/Users/jamiecraik/dev/agent-skills/Infrastructure/artifacts/skill-graphs/runs/run_20260331T141226543802Z_fc9894_15c48010/run.json)
- [/Infrastructure/artifacts/skill-graphs/runs/run_20260331T141225956402Z_bb9acb_15c37bdd/run.json](/Users/jamiecraik/dev/agent-skills/Infrastructure/artifacts/skill-graphs/runs/run_20260331T141225956402Z_bb9acb_15c37bdd/run.json)

## Promotion boundary

- Keep this intervention at `documentation` stage until it repeats cleanly without reopening accessibility, clarity, or safety regressions.
- Promote to a reusable skill reference only after the shadow cycle shows the guidance helping runs stay clean throughout the loop, not just recover by the end.
