---
name: ui-ux-creative-coding
description: Use this skill to build and polish an existing React or Tauri UI with purposeful animation, transitions, micro-interactions, stronger interaction rhythm, and accessibility refinements when the visual direction is already set and the user wants targeted implementation-ready polish, not a full redesign.
metadata:
  skill-type: scaffolding_templates
  short-description: UI polish workflow for React/Tauri with motion, accessibility, and implementation-ready validation guidance.
---

# UI/UX Creative Coding

## Table of Contents
- [Standards snapshot](#standards-snapshot)
- [Design-system integration](#design-system-integration)
- [When to use](#when-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Procedure](#procedure)
- [High-Ambition Mode](#high-ambition-mode)
- [Validation](#validation)
- [Anti-patterns](#anti-patterns)
- [Constraints](#constraints)
- [Philosophy](#philosophy)
- [Examples](#examples)
- [Failure mode](#failure-mode)
- [Variation](#variation)
- [References](#references)
- [Gotchas](#gotchas)
- [See Also](#see-also)

## Standards snapshot
- Treat React 19 as the default interaction baseline for stateful UI polish work.
- Treat Next.js 16 as the default rendering/routing baseline when the target surface is a Next.js app.
- Treat Tailwind CSS v4 and semantic design tokens as the default styling and spacing baseline.
- Hold polish recommendations to WCAG 2.2 AA outcomes, including keyboard support, focus visibility, contrast, and clear reduced-motion parity.
- Route token architecture or system-level visual changes to `design-system`; keep this skill focused on implementation-level interaction quality.

## Design-system integration
- Apply `frontend/ui/Infrastructure/references/design-system-integration-contract.md` before recommending typography, spacing, iconography, or token changes during polish work.
- Keep this skill focused on interaction quality while delegating shared visual-language governance to `design-system`.
- Use `frontend/ui/Infrastructure/references/skill-routing-matrix-2026.md` when deciding whether an ask is polish-only or should route to `frontend-ui-design`.

## When to use
- Improve motion systems, interaction rhythm, and UI polish for product surfaces.
- Add or refine purposeful animation, transitions, hover feedback, and micro-interactions so the UI feels more responsive and alive.
- Produce implementation notes for React/Tauri interfaces using Tailwind v4 and motion patterns.
- Refine visually led marketing or demo surfaces after visual hierarchy, content structure, and brand direction are already defined.
- Prefer this skill over brand-only or logo work when behavior and interaction quality are the target.

## Required inputs
- Product context and target interface scope (2-3 screens or sections maximum).
- Performance and accessibility constraints.
- Persona references or style constraints (for example `@benjitaylor`, `@jenny_wen`).
- For visually led work, the existing visual thesis/content plan/interaction thesis or enough context to derive them safely.
- Animation intent boundaries: where motion should guide understanding vs where the UI should stay still.
- Required assets, existing component library, and design source of truth.
- Deployment risk tolerance and review cadence.

## Deliverables
- Bounded design recommendation with:
  - proposed interaction approach,
  - concrete motion system,
  - animation strategy map (hero moment, feedback layer, transition layer, delight layer),
  - implementation sequence,
  - validation checkpoints (accessibility, responsiveness, performance).
- For visually led work: motion guidance that sharpens an already chosen visual anchor instead of compensating for weak structure.
- Clear "why this way" rationale and tradeoffs.
- Suggested fallback for constraints or blocked motion/runtime conditions.
- Include `schema_version` in output contracts for machine-checkable notes.

## Procedure
### 1) Scope narrowing
- Start with the smallest viable surface: one screen and up to 3 interaction clusters.
- Add one variant per cycle only after the first set is validated.

### 2) Assess motion opportunities
- Identify static friction first: missing feedback, abrupt state changes, unclear relationships, or attention issues.
- Mark each candidate animation as required feedback, transition smoothing, guidance, or optional delight.
- Keep one signature motion moment per surface before adding secondary effects.

### 3) Build recommendation
- Select persona guidance from available references.
- For visually led work, preserve one dominant visual anchor and one job per section before proposing motion.
- Define component-level behavior, motion levels, and visual hierarchy.
- Use `Infrastructure/references/motion-guidelines.md` for timing/easing defaults and reduced-motion parity.
- Add explicit tradeoffs for performance and maintainability.

### 4) Validate
- Run accessibility and clarity checks before recommending final motion intensity.
- Flag any unsupported claims and replace with conservative alternatives.

## High-Ambition Mode
- Use this mode only when the user explicitly wants a "wow", "push it further", "go all out", or unusually ambitious interaction result.
- Before proposing implementation, think through 2-3 directions with different ambition and complexity levels.
- Present those directions with tradeoffs first:
  - what it would feel like,
  - performance and maintenance cost,
  - browser or device constraints,
  - fallback posture.
- Do not jump straight into code for high-ambition work until one direction is chosen.
- Progressive enhancement is non-negotiable:
  - the baseline non-enhanced path must still be good,
  - reduced-motion parity must still feel intentional,
  - any advanced API or heavy visual path must have a functional fallback.
- When implementing or recommending ambitious motion, require browser-based visual iteration rather than trusting the first pass.
- Use these quick checks before calling the result done:
  - removal test: if the effect is removed, does the experience clearly lose something;
  - device test: does it still feel smooth on ordinary hardware;
  - context test: does the flourish fit the product instead of embarrassing it.

## Validation
- Must include explicit verification language for layout, motion, and accessibility.
- Validate with concrete acceptance checks (for example reduced cognitive load, no accessibility violations, no expensive motion on low-end paths).
- Confirm motion choices are purposeful (feedback, transition, guidance, or delight) and not decorative filler.
- Confirm reduced-motion behavior has a clear parity path, not just disabled UX.
- In high-ambition mode, confirm at least two candidate directions were considered before implementation guidance was chosen.
- In high-ambition mode, confirm browser-based visual verification or an explicit blocked note is part of the completion contract.
- Confirm typography, spacing, icon usage, and token-level recommendations remain compliant with `frontend/ui/Infrastructure/references/design-system-integration-contract.md`.
- If checks are incomplete, return a partial result and ask for missing constraints.
- Validation is fail-fast: if a required check fails, stop and only continue after user confirmation.

## Anti-patterns
- Design without user constraints (scope drift).
- Converting every page to a bespoke system instead of extending current components.
- Overusing heavy motion before proving baseline clarity.
- Using motion to hide weak composition, weak imagery, or cluttered section structure.
- Treating this as brand identity work.

## Constraints
- Redact sensitive references or credentials if any are shared.
- Keep recommendations executable within the repo's stack and avoid impossible dependencies.
- Preserve low-motion and reduced-motion behavior when appropriate.

## Philosophy
- Keep recommendations concrete, specific, and implementation-ready.
- Prefer fewer, higher-quality interactions over many speculative ideas.
- Use motion to heighten hierarchy and atmosphere, not to rescue generic layout decisions.
- Stay focused on user outcomes, not decorative novelty.

## Examples
- "Can you inspect the settings panel in this Tauri app and use one motion pattern with a low-motion fallback?"
- "I need a practical redesign for the dashboard loading and error states so users can tell what's happening at a glance."
- "How can I tune the interactions on this three-tab settings screen and validate that it still feels responsive?"
- "Can you add micro-interactions and transition polish to this dashboard so it feels alive without harming performance?"

## Failure mode
- If no source constraints or target screen are provided, request scope before proposing a design approach.
- If the surface still lacks a clear visual thesis or content structure, route back to `frontend-ui-design` before deep motion recommendations.
- If required persona references are unavailable, proceed with neutral defaults and state the assumption.

## Variation
- Vary output depth by context: start with a small, explicit interaction area and then offer one optional expansion pass for broader screen polish if the user wants more breadth.

## References
- Reference contracts and examples are in `Infrastructure/references/contract.yaml`, `Infrastructure/references/evals.yaml`, `Infrastructure/references/benjitaylor-persona.md`, `Infrastructure/references/emilkowalski-persona.md`, and `Infrastructure/references/design-taste-overlay.md`.
- Motion opportunity mapping, timing defaults, and reduced-motion strategy live in `Infrastructure/references/motion-guidelines.md`.
- Runtime or benchmark examples live in `Infrastructure/references/examples.md`.
- Execution helpers: `Infrastructure/scripts/` (validation scripts), `assets/` (reference imagery and patterns).
- Policy notes and task routing: `Infrastructure/references/task-profile.json`, `task-profile` links in `Infrastructure/references/project-review-mode.md`.

## Gotchas
- High-ambition motion without a user-approved direction usually wastes time. Slow down first, choose the right ambition level, then build.

## See Also
| Skill | When to use |
|---|---|
| [[frontend-ui-design]] | Establish the structural UI direction before layering in motion and polish |
| [[baseline-ui]] | Keep animation timing, typography, and accessibility aligned with the baseline system |
| [[design-system]] | Route token, palette, and alias-level system work to the design-system owner |
| [[react-ui-patterns]] | Ground the creative layer in maintainable React composition patterns |

**Topic map:** [[frontend-ui]]
