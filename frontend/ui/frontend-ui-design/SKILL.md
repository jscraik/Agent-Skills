---
name: frontend-ui-design
description: Design or implement production-ready frontend UI components and screens with strong visual direction, accessibility, and reusable structure. Use when the user wants standard UI build or redesign work, not design-system governance or post-direction polish only.
metadata:
  skill-type: scaffolding_templates
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
- [Visually Led Surfaces](#visually-led-surfaces)
- [Redesign Audit Lens](#redesign-audit-lens)
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
- Shape visually led landing pages, websites, prototypes, or demos when art direction matters but the result still needs production-ready hierarchy and accessibility.
- Audit existing UI for accessibility, token use, state coverage, or implementation readiness.

## When not to use
- Motion-first or experimental creative-coding work. Use [`ui-ux-creative-coding`](/Users/jamiecraik/dev/agent-skills/frontend/ui/ui-ux-creative-coding/SKILL.md).
- Backend or infra-only work with no UI surface.
- Brand-only exploration with no product UI deliverable.

## Required inputs
- Target surface and stack.
- User goal, task-critical path, and constraints.
- Existing token, component, and layout conventions.
- Visual direction inputs when relevant: brand posture, imagery constraints, and whether the surface is utility-first product UI or a visually led marketing/demo surface.
- Definition of done: accessibility, performance, visual review, or implementation depth.

## Deliverables
- UI brief and scope.
- For visually led surfaces: one visual thesis, one content plan, and one interaction thesis before component planning.
- Component or screen plan with states and accessibility behavior.
- Token-referenced implementation guidance.
- For recursive-learning runs: rubric-bound observations recorded against `references/learning-rubric.yaml` before any lesson is considered promotable.
- Verification checklist covering a11y, responsiveness, and state completeness.
- File plan or handoff path when code changes are in scope.

## Philosophy
- Design is a system: tokens to components to patterns to verification.
- Clarity and accessibility are default quality bars, not optional polish.
- Favor production-ready structure over abstract inspiration.
- Distinctive design is welcome, but trust and usability win ties.

## Workflow
1. Frame the surface, user task, and success condition.
2. If the surface is visually led, write three things before components:
   - visual thesis: one sentence for mood, material, and energy;
   - content plan: hero, support, detail, final CTA;
   - interaction thesis: 2-3 motions that materially change the feel of the page.
3. Map the key states: default, loading, empty, error, permission, and edge cases that matter.
4. Anchor measurements to tokens instead of ad hoc values.
5. Define focus order, keyboard behavior, labels, contrast, and reduced-motion handling explicitly.
6. Align implementation guidance to the host stack: React 19 patterns, Next.js 16 where relevant, Tailwind v4 utilities/tokens, and Tauri/App SDK constraints when present.
7. For redesign requests, run the anti-generic audit pass in `references/redesign-audit-lens.md` before proposing visual polish.
8. Reuse bundled `references/`, `scripts/`, and `assets/FEATURE_DESIGN.template.md` when producing handoff structure or audit output.
9. Verify the proposed UI is implementable, accessible, and stable before calling it done.

## Visually Led Surfaces
- Use this track for branded landing pages, websites, prototypes, and demos where hierarchy, imagery, and restraint matter as much as correctness.
- Start with composition, not components. The first viewport should feel like a poster, not a document.
- Prefer one dominant visual anchor per section and one primary takeaway or action.
- Keep the brand or product name unmistakable in the first screen on branded surfaces.
- Use sparse copy, strong spacing, and image-led hierarchy before adding cards, badges, or decorative chrome.
- Distinguish branded surfaces from product surfaces:
  - branded landing pages may justify a full-bleed hero and stronger atmosphere;
  - utility-first product UI should default to orientation, status, and action rather than mood-setting copy.
- Treat cards as opt-in, not default. If a layout still works without the card treatment, remove it unless the card itself is the interaction.
- Motion should reinforce presence, hierarchy, or affordance. Do not add motion that only decorates.
- If imagery is present, it must do narrative work and leave a calm region for text. Decorative texture alone is not enough.

## Redesign Audit Lens
- Use this lens when modernizing an existing product surface that feels generic or inconsistent.
- Prioritize structural fixes before polish: hierarchy, state coverage, trust cues, and interaction clarity.
- Enforce realism in example content: avoid placeholder names, fake round metrics, and dead actions that point to `#`.
- Reference: `references/redesign-audit-lens.md`.

## Validation
- Confirm responses begin with `## When to use`, `## Inputs`, and `## Outputs` when the skill is used interactively.
- Confirm recursive-learning reviews record structured observations in `lesson_observations.json` and do not rewrite the skill from a single run.
- Confirm accessibility coverage includes focus, keyboard behavior, semantic naming, contrast, and reduced-motion parity.
- Confirm measurements and spacing decisions map back to tokens or documented exceptions.
- Confirm UI states are complete enough for real implementation, not just the happy path.
- Confirm visually led work distinguishes branded landing pages from utility-first product UI and does not collapse both into the same layout language.
- Confirm the first viewport has a clear dominant visual or hierarchy anchor and that any card treatment is justified instead of habitual.
- Confirm Storybook or equivalent visual review coverage is called out when components change materially.
- Confirm generated examples avoid generic AI fingerprints (placeholder copy/data, dead actions, repetitive card-grid defaults) unless explicitly requested by the user.

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
- Using hero-card mosaics, logo-cloud filler, or split attention layouts when one strong composition would communicate more clearly.
- Letting a headline overpower the brand on branded surfaces or using weak imagery that could be removed without changing the page.
- Polishing visuals while leaving core redesign issues unresolved (weak hierarchy, unclear primary action, missing edge states, or trust-critical context buried).

## Examples
- "Design a settings flow for a React app with accessible tabs and inline validation."
- "Design a visually strong landing page for a product launch with one dominant hero composition and restrained motion."
- "Review this component set for token drift, focus behavior, and responsive gaps."
- "Redesign this existing settings page to remove generic patterns while preserving stack constraints and accessibility."

## See Also

| Skill | When to use together |
|---|---|
| [[design-system]] | Ground component design in the token layer |
| [[baseline-ui]] | Validate components against baseline UI rules after design |
| [[figma]] | Use Figma designs as reference for implementation |
| [[fixing-accessibility]] | Apply accessibility fixes during component design |
| [[ui-ux-creative-coding]] | Add motion and creative polish to designed components |

**Topic map:** [[frontend-ui]]

## Remember
- Standard UI design work should feel production-ready, not pitch-deck-ready.
- A complete state model is part of quality.
- The best output makes implementation easier and regressions less likely.
- If the skill is running in learning mode, preserve repeated good and bad signals as structured observations first, then let `skill-builder` decide what is safe to promote.

## Gotchas
- None yet. Capture recurring failures here as symptom -> cause -> do instead -> check.

## Failure mode
- If the target surface, design constraints, or implementation boundaries are unclear, stop, surface the missing context, and fall back to a narrower component review before editing UI code.
