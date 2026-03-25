---
name: frontend-design
description: Route broad frontend design requests to the correct local UI skill after classifying intent and maturity. Use when the user asks for frontend design generally and the specific design owner is not yet clear.
metadata:
  skill-type: scaffolding_templates
---

# Frontend Design

Install a broad, deconflicted frontend design entrypoint that preserves the upstream compound-engineering `frontend-design` doctrine while routing to stronger local skills where they already exist.

## Table of Contents
- [When to use](#when-to-use)
- [When not to use](#when-not-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Workflow](#workflow)
- [Routing map](#routing-map)
- [Overlap matrix](#overlap-matrix)
- [Upstream preservation](#upstream-preservation)
- [Validation](#validation)
- [Constraints](#constraints)
- [Examples](#examples)
- [Failure mode](#failure-mode)
- [Gotchas](#gotchas)

## When to use
- Use when the user asks broadly for "frontend design" and the right local frontend skill is not yet obvious.
- Use when the first job is to classify the request as existing-system extension, partial-system extension, or greenfield before deciding who should own implementation guidance.
- Use for ambiguous landing pages, dashboards, app screens, admin surfaces, and design-led component work that need a coherent design plan before implementation and before a narrower skill can be chosen confidently.
- Use when you need the upstream compound-engineering `frontend-design` workflow, but adapted to this repository's richer local frontend skill graph.
- Use when context detection matters: existing design system versus partial system versus greenfield.

## When not to use
- Do not use when the request already names or clearly implies the correct narrower skill.
- Do not use for backend-only work with no UI surface.
- Do not use for token-layer or design-system changes as the primary task. Use [`design-system`](/Users/jamiecraik/dev/Agent-Skills/frontend/ui/design-system/SKILL.md).
- Do not use for motion-only or polish-only refinement after the visual direction is already set. Use [`ui-ux-creative-coding`](/Users/jamiecraik/dev/Agent-Skills/frontend/ui/ui-ux-creative-coding/SKILL.md).
- Do not use for straightforward production UI planning or implementation when the request is already clearly standard product UI. Use [`frontend-ui-design`](/Users/jamiecraik/dev/Agent-Skills/frontend/ui/frontend-ui-design/SKILL.md).
- Do not use when the user already wants an accessible screen flow, a concrete component plan, or a visually led surface with production-ready structure. Use [`frontend-ui-design`](/Users/jamiecraik/dev/Agent-Skills/frontend/ui/frontend-ui-design/SKILL.md).

## Required inputs
- Target UI surface and stack.
- Whether the work is in an existing codebase or greenfield.
- User goal, primary audience, and the critical path the interface must support.
- Any design-system, branding, accessibility, or performance constraints already known.

## Deliverables
- Mode decision: existing-system extension, partial-system extension, or greenfield.
- Ownership decision: stay in `frontend-design` only long enough to choose the right downstream skill and planning frame.
- One visual thesis, one content plan, and one interaction plan before implementation begins.
- Explicit routing to the narrower local skill when the task is better served by `frontend-ui-design`, `ui-ux-creative-coding`, or `design-system`.
- Visual verification notes and screenshot-first review expectation before calling the work done.
- Preserved upstream doctrine in references so none of the imported guidance is lost.

## Workflow
1. Detect context first.
   - Look for design tokens, CSS variables, typography, component libraries, motion libraries, spacing scales, and existing composition patterns.
   - Classify the surface as existing-system, partial-system, or greenfield.
2. Decide whether this skill should continue to own the request.
   - If the request is already standard product UI with clear deliverables, route immediately to `frontend-ui-design`.
   - If the main job is token, theme, alias, or design-system structure, route immediately to `design-system`.
   - If the visual direction is already chosen and the request is mainly about motion, rhythm, or polish, route immediately to `ui-ux-creative-coding`.
3. Write the pre-build plan.
   - Visual thesis: one sentence covering mood, material, and energy.
   - Content plan: the main information order for the page, screen, or component.
   - Interaction plan: 2-3 motions or interaction beats that materially shape the feel.
4. Route to the right implementation skill.
   - Standard product UI or redesign work: `frontend-ui-design`.
   - Motion, rhythm, and polish after direction is set: `ui-ux-creative-coding`.
   - Token architecture or design-system work: `design-system`.
5. Verify visually before completion.
   - Prefer existing browser tooling, then browser MCPs, then agent-browser, then explicit mental-review fallback.
   - Fix only glaring issues in the first verification pass unless the user asks for iteration.

## Routing map
- `frontend-design` is the umbrella and compatibility entrypoint.
- Treat it as a front door, not a long-term owner, unless the ambiguity itself is the core job.
- Use [`frontend-ui-design`](/Users/jamiecraik/dev/Agent-Skills/frontend/ui/frontend-ui-design/SKILL.md) when the work is standard product UI, accessible component planning, or a visually led surface that still needs production-ready structure.
- Use [`ui-ux-creative-coding`](/Users/jamiecraik/dev/Agent-Skills/frontend/ui/ui-ux-creative-coding/SKILL.md) when the visual thesis already exists and the main task is motion, interaction rhythm, or refinement.
- Use [`design-system`](/Users/jamiecraik/dev/Agent-Skills/frontend/ui/design-system/SKILL.md) when tokens, aliases, mapped variables, or theme structure are the center of gravity.
- If the user already asks for one of the narrower skills by name or unmistakable scope, skip this wrapper and use the narrower skill directly.
- Read [`references/upstream-frontend-design.md`](/Users/jamiecraik/dev/Agent-Skills/frontend/ui/frontend-design/references/upstream-frontend-design.md) when you need the full imported compound-engineering design doctrine, module breakdown, and litmus checks.

## Overlap matrix
- Read [`references/overlap-matrix.md`](/Users/jamiecraik/dev/Agent-Skills/frontend/ui/frontend-design/references/overlap-matrix.md) before widening this skill's trigger wording.
- The matrix documents the boundary between this wrapper and `frontend-ui-design`, `ui-ux-creative-coding`, and `design-system`, with examples of when to route immediately instead of triggering this umbrella.

## Upstream preservation
- This skill intentionally does not flatten the upstream CE `frontend-design` skill into a weaker summary.
- The full upstream guidance is preserved in [`references/upstream-frontend-design.md`](/Users/jamiecraik/dev/Agent-Skills/frontend/ui/frontend-design/references/upstream-frontend-design.md).
- The local wrapper changes only two things:
  - deconflict broad triggering against stronger local frontend skills;
  - route broad asks into the local frontend skill graph instead of duplicating overlapping procedures.

## Validation
- Confirm the skill first decides whether this is existing-system, partial-system, or greenfield work.
- Confirm the skill does not stay in control once a narrower local owner is obvious.
- Confirm a visual thesis, content plan, and interaction plan exist before implementation recommendations begin.
- Confirm the narrower local skill is named explicitly when routing is appropriate.
- Confirm visual verification is part of the completion contract.
- Confirm trigger coverage in [`references/evals.yaml`](/Users/jamiecraik/dev/Agent-Skills/frontend/ui/frontend-design/references/evals.yaml) still distinguishes this wrapper from nearby skills.
- Confirm [`references/overlap-matrix.md`](/Users/jamiecraik/dev/Agent-Skills/frontend/ui/frontend-design/references/overlap-matrix.md) still matches the nearby skill descriptions after any local-skill updates.

## Constraints
- Respect existing design systems and explicit user instructions over skill defaults.
- Do not introduce a competing design language into an established application unless the user explicitly asks for a redesign.
- Keep the wrapper install additive and deconflicted; do not weaken or duplicate existing frontend skills.
- Do not claim visual completion without a verification pass or an explicit note that verification was blocked.

## Examples
- "Design the frontend for this new SaaS landing page."
- "I want a strong visual direction for this dashboard, but I'm not sure which UI skill should drive it."
- "Can you improve the design of this existing React screen without ignoring the current design system?"
- "Build a frontend with real design quality, not a generic card grid."

## Failure mode
- If the request is actually design-system work, motion-only polish, or straightforward production UI implementation, stop routing through this umbrella skill and hand off to the narrower local skill instead.
- If the request is already concrete enough to name the downstream owner immediately, skip the wrapper and route without adding an extra planning layer.
- If the codebase context is ambiguous and the mode cannot be inferred safely, ask whether to follow the existing patterns or pursue a more distinctive visual direction.

## Gotchas
- Broad frontend design requests can false-positive into overlapping skills. Recheck `references/evals.yaml` before widening the description.
- If a request says "frontend design" but also asks for explicit states, accessibility behavior, component structure, or token changes, that narrower scope wins.
- Preserve the upstream doctrine in references when refining this wrapper. Do not compress away useful modules, litmus checks, or verification guidance.

## See Also

| Skill | When to use together |
|---|---|
| [[frontend-ui-design]] | Hand off once the request clearly becomes standard UI build or redesign work |
| [[design-system]] | Route token, alias, or system-governance work to the dedicated owner |
| [[ui-ux-creative-coding]] | Route post-direction polish and motion refinement to the narrower owner |
| [[figma]] | Pull design context from Figma before choosing the downstream implementation skill |

**Topic map:** [[frontend-ui]]
