---
name: frontend-ui-design
description: Create and review production-ready UI systems/components with tokens and accessibility. Use for standard UI implementation or redesign (not creative-coding polish). Use when the user requests this capability.
---

# Frontend UI Design

## Table of Contents
- [Standards snapshot](#standards-snapshot)
- [When to use](#when-to-use)
- [When not to use](#when-not-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Philosophy](#philosophy)
- [Workflow](#workflow)
- [Validation](#validation)
- [Constraints](#constraints)
- [Anti-patterns](#anti-patterns)
- [Examples](#examples)
- [Remember](#remember)

## Standards snapshot (March 2026)
- Use React 19 guidance for client UI patterns and Next.js 16 guidance when the surface is a Next.js app.
- Treat Tailwind CSS v4 tokens and utilities as the baseline styling system unless the host project says otherwise.
- Hold web UI work to WCAG 2.2 AA, explicit focus behavior, and token-referenced measurements.
- Keep design-system outputs grounded in DTCG/W3C token structure and repo-native component conventions.

## When to use
- Design or review standard product UI systems and components.
- Specify accessible screens, flows, states, and design-system changes.
- Plan or patch production UI for React, Apps SDK widgets, or Tauri web UI when the work is standard product design rather than experimental creative coding.
- Audit existing UI for accessibility, token use, state coverage, or implementation readiness.

## When not to use
- Motion-first or experimental creative-coding work. Use [`ui-ux-creative-coding`](/Users/jamiecraik/dev/agent-skills/frontend/ui/ui-ux-creative-coding/SKILL.md).
- Backend or infra-only work with no UI surface.
- Brand-only exploration with no product UI deliverable.

## Required inputs
- Target surface and stack.
- User goal, task-critical path, and constraints.
- Existing token, component, and layout conventions.
- Definition of done: accessibility, performance, visual review, or implementation depth.

## Deliverables
- UI brief and scope.
- Component or screen plan with states and accessibility behavior.
- Token-referenced implementation guidance.
- Verification checklist covering a11y, responsiveness, and state completeness.
- File plan or handoff path when code changes are in scope.

## Philosophy
- Design is a system: tokens to components to patterns to verification.
- Clarity and accessibility are default quality bars, not optional polish.
- Favor production-ready structure over abstract inspiration.
- Distinctive design is welcome, but trust and usability win ties.

## Workflow
1. Frame the surface, user task, and success condition.
2. Map the key states: default, loading, empty, error, permission, and edge cases that matter.
3. Anchor measurements to tokens instead of ad hoc values.
4. Define focus order, keyboard behavior, labels, contrast, and reduced-motion handling explicitly.
5. Align implementation guidance to the host stack: React 19 patterns, Next.js 16 where relevant, Tailwind v4 utilities/tokens, and Tauri/App SDK constraints when present.
6. Reuse bundled `references/`, `scripts/`, and `assets/FEATURE_DESIGN.template.md` when producing handoff structure or audit output.
7. Verify the proposed UI is implementable, accessible, and stable before calling it done.

## Validation
- Confirm responses begin with `## When to use`, `## Inputs`, and `## Outputs` when the skill is used interactively.
- Confirm accessibility coverage includes focus, keyboard behavior, semantic naming, contrast, and reduced-motion parity.
- Confirm measurements and spacing decisions map back to tokens or documented exceptions.
- Confirm UI states are complete enough for real implementation, not just the happy path.
- Confirm Storybook or equivalent visual review coverage is called out when components change materially.

## Constraints
- Do not add new heavy UI dependencies without approval.
- Do not trade away accessibility or reduced-motion parity for novelty.
- Keep outputs frontend-scoped unless the user explicitly asks for backend wiring that is necessary for UI state.
- Never expose secrets, private URLs, or internal tokens in examples or handoff artifacts.

## Anti-patterns
- Designing only the default state and leaving failure states implicit.
- Using raw ad hoc spacing, radius, or color values when tokens should exist.
- Treating accessibility as a QA afterthought instead of part of the design contract.
- Returning generic “nice UI” advice with no state model or implementation path.

## Examples
- "Design a settings flow for a React app with accessible tabs and inline validation."
- "Review this component set for token drift, focus behavior, and responsive gaps."

## Remember
- Standard UI design work should feel production-ready, not pitch-deck-ready.
- A complete state model is part of quality.
- The best output makes implementation easier and regressions less likely.
