---
name: frontend-ui-design
description: Design or implement production-ready frontend UI components and screens with strong visual direction, layout rhythm, spacing hierarchy, accessibility, and reusable structure. Use when the user wants standard UI build or redesign work, including fixing crowded or structurally weak layouts, not design-system governance or post-direction polish only.
metadata:
  skill-type: scaffolding_templates
---

# Frontend UI Design

## Table of Contents
- [Standards snapshot](#standards-snapshot)
- [Design-system integration](#design-system-integration)
- [When to use](#when-to-use)
- [When not to use](#when-not-to-use)
- [Routing boundary contract](#routing-boundary-contract)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Design Context Minimum](#design-context-minimum)
- [Copy and Tone](#copy-and-tone)
- [Intensity Tuning](#intensity-tuning)
- [Philosophy](#philosophy)
- [Variation](#variation)
- [Workflow](#workflow)
- [Cross-Context Adaptation](#cross-context-adaptation)
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

## Design-system integration
- Apply `frontend/ui/references/design-system-integration-contract.md` to keep typography, spacing, iconography, and semantic token usage consistent.
- Route token architecture, aliasing, and theme-slot governance changes to `design-system`; keep this skill focused on screen and component implementation.
- Use `frontend/ui/references/skill-routing-matrix-2026.md` to resolve overlap with `frontend-design`, `design-system`, and `ui-ux-creative-coding`.

## When to use
- Design or review standard product UI systems and components.
- Specify accessible screens, flows, states, and design-system changes.
- Plan or patch production UI for React, Apps SDK widgets, or Tauri web UI when the work is standard product design rather than experimental creative coding.
- Adapt an existing interface across mobile, tablet, desktop, print, or email contexts while keeping behavior and information architecture coherent.
- Shape visually led landing pages, websites, prototypes, or demos when art direction matters but the result still needs production-ready hierarchy and accessibility.
- Audit existing UI for accessibility, token use, state coverage, or implementation readiness.

## When not to use
- Motion-first or experimental creative-coding work. Use [`ui-ux-creative-coding`](/Users/jamiecraik/dev/agent-skills/frontend/ui/ui-ux-creative-coding/SKILL.md).
- Backend or infra-only work with no UI surface.
- Brand-only exploration with no product UI deliverable.
- Broad ambiguous frontend-design requests that do not yet declare implementation intent. Start with [`frontend-design`](/Users/jamiecraik/dev/agent-skills/frontend/ui/frontend-design/SKILL.md).

## Routing boundary contract
- Own requests with explicit implementation or redesign intent, including verbs like `build`, `implement`, `redesign`, `fix layout`, and `create screen`.
- Route to `design-system` when the primary outcome is shared token/alias/theme governance.
- Route to `ui-ux-creative-coding` when the visual direction is already set and the ask is motion polish only.
- Defer broad ambiguous asks to `frontend-design`, then accept handoff once scope is implementation-ready.

## Required inputs
- Target surface and stack.
- User goal, task-critical path, and constraints.
- Existing token, component, and layout conventions.
- Source assumptions and target-context constraints when adaptation is requested:
  - device class and orientation,
  - input model (touch, keyboard, pointer),
  - connectivity/performance expectations,
  - non-screen outputs like print/email when relevant.
- Visual direction inputs when relevant: brand posture, imagery constraints, and whether the surface is utility-first product UI or a visually led marketing/demo surface.
- Definition of done: accessibility, performance, visual review, or implementation depth.

## Deliverables
- UI brief and scope.
- For visually led surfaces: one visual thesis, one content plan, and one interaction thesis before component planning.
- Component or screen plan with states and accessibility behavior.
- Token-referenced implementation guidance.
- For adaptation work: a compact adaptation matrix covering what to keep, adapt, or redesign for each target context (layout, interaction, content density, and navigation).
- For recursive-learning runs: rubric-bound observations recorded against `references/learning-rubric.yaml` before any lesson is considered promotable.
- Verification checklist covering a11y, responsiveness, and state completeness.
- File plan or handoff path when code changes are in scope.

## Design Context Minimum
- Before proposing a visual direction, confirm three things:
  - who the interface is for,
  - what job they are trying to complete,
  - how the interface should feel while they do it.
- Treat existing code as evidence of current implementation, not definitive evidence of audience or brand intent.
- If the user request or repo docs already establish these points, proceed without extra questions.
- If not, ask only the smallest missing set of questions needed to avoid inventing the wrong tone or hierarchy.
- For recurring design work, suggest persisting a short design-context note in the repo's normal docs or instructions path when that would reduce repeated clarification.

## Copy and Tone
- Treat UX copy as part of the interface, not post-hoc decoration.
- Labels, buttons, errors, empty states, and success/loading text should all answer the user's immediate question:
  - what is this,
  - what happened,
  - what do I do next.
- Prefer object-action phrasing for actions and controls.
- Do not use placeholders as the only label.
- Avoid jargon unless the audience clearly expects it; when domain language is necessary, make the surrounding context plain.
- Error copy should explain the issue and the next step without blaming the user.

## Intensity Tuning
- When a surface feels bland, make one or two core elements more distinctive instead of turning everything up at once.
- When a surface feels loud, reduce intensity selectively:
  - desaturate secondary elements,
  - reduce competing weights,
  - remove decorative noise before muting the core signal.
- Quiet design should still have anchors. Bold design should still preserve hierarchy.
- Avoid the trap of making everything equally colorful, equally muted, equally large, or equally emphatic.

## Philosophy
- Design is a system: tokens to components to patterns to verification.
- Clarity and accessibility are default quality bars, not optional polish.
- Favor production-ready structure over abstract inspiration.
- Distinctive design is welcome, but trust and usability win ties.
- Use a practical framework: define task-critical states first, then tune visual expression.
- Make tradeoff calls explicit so we understand why usability decisions win under delivery pressure.
- Ask: "Why would this hierarchy help the user complete the core task faster?"
- Ask: "Can we implement this with existing patterns before inventing a new structure?"
- Ask: "What would break for keyboard and reduced-motion users if this choice is wrong?"

## Variation
- Vary output depth by request type:
  - implementation request: prioritize concrete component and state contracts;
  - redesign request: prioritize hierarchy, composition rhythm, and trust cues first.
- Adapt recommendations to context-specific constraints:
  - existing system: preserve token and component conventions unless there is a clear defect;
  - new surface: explore different hierarchy anchors before locking implementation details.
- Avoid repetitive templates; use different framing for utility-first product surfaces and visually led landing pages.

## Workflow
1. Frame the surface, user task, success condition, and design-context minimum.
2. If the surface is visually led, write three things before components:
   - visual thesis: one sentence for mood, material, and energy;
   - content plan: hero, support, detail, final CTA;
   - interaction thesis: 2-3 motions that materially change the feel of the page.
3. Map the key states: default, loading, empty, error, permission, and edge cases that matter.
4. If the task is adaptation-focused, run the cross-context pass in `references/cross-context-adaptation.md`:
   - capture source assumptions,
   - map target constraints,
   - decide what to keep, adapt, or redesign.
5. Anchor measurements to tokens instead of ad hoc values.
6. Define focus order, keyboard behavior, labels, contrast, and reduced-motion handling explicitly.
7. Align implementation guidance to the host stack: React 19 patterns, Next.js 16 where relevant, Tailwind v4 utilities/tokens, and Tauri/App SDK constraints when present.
8. For redesign requests, run the anti-generic audit pass in `references/redesign-audit-lens.md` before proposing visual polish.
9. Reuse bundled `references/`, `scripts/`, and `assets/FEATURE_DESIGN.template.md` when producing handoff structure or audit output.
10. Verify the proposed UI is implementable, accessible, and stable before calling it done.

## Cross-Context Adaptation
- Adaptation is not simple scaling. Treat it as a context shift in device constraints, interaction model, and user intent.
- Preserve core information architecture and primary actions across contexts; adapt presentation and interaction patterning, not product meaning.
- For adaptation-heavy requests, use `references/cross-context-adaptation.md` to build a source-to-target matrix covering:
  - layout strategy,
  - interaction/touch strategy,
  - content-priority strategy,
  - navigation strategy,
  - verification requirements on real devices and orientations.

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
- Confirm the audience, job to be done, and intended feel are explicit before visual-direction recommendations.
- Confirm primary-flow copy is specific, actionable, and tone-appropriate instead of generic filler.
- Confirm accessibility coverage includes focus, keyboard behavior, semantic naming, contrast, and reduced-motion parity.
- Confirm measurements and spacing decisions map back to tokens or documented exceptions.
- Confirm layout-first requests include explicit spacing/hierarchy/rhythm/density findings instead of generic "looks cleaner" statements.
- Confirm UI states are complete enough for real implementation, not just the happy path.
- Confirm adaptation requests include source assumptions, target constraints, and explicit keep/adapt/redesign decisions rather than a generic "make it responsive" answer.
- Confirm visually led work distinguishes branded landing pages from utility-first product UI and does not collapse both into the same layout language.
- Confirm the first viewport has a clear dominant visual or hierarchy anchor and that any card treatment is justified instead of habitual.
- Confirm intensity tuning preserves a small number of clear anchors rather than making the whole surface uniformly loud or uniformly flat.
- Confirm Storybook or equivalent visual review coverage is called out when components change materially.
- Confirm generated examples avoid generic AI fingerprints (placeholder copy/data, dead actions, repetitive card-grid defaults) unless explicitly requested by the user.
- Confirm typography, spacing, and icon usage decisions stay compliant with `frontend/ui/references/design-system-integration-contract.md`.
- Confirm routing decisions remain aligned with `frontend/ui/references/skill-routing-matrix-2026.md`.

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
- "Adapt this desktop analytics workspace for mobile and tablet while preserving core tasks and avoiding hover-only interactions."
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
