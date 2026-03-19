---
name: ui-ux-creative-coding
description: Analyze and run focused UI polishing for React/Tauri screens when motion, interaction rhythm, and accessibility refinements are needed in Tailwind v4; use this when users need implementation-ready recommendations before changing interface code.
metadata:
  skill-type: scaffolding_templates
  short-description: UI polish workflow for React/Tauri with motion, accessibility, and implementation-ready validation guidance.
---

# UI/UX Creative Coding

## When to use
- Improve motion systems, interaction rhythm, and UI polish for product surfaces.
- Produce implementation notes for React/Tauri interfaces using Tailwind v4 and motion patterns.
- Prefer this skill over brand-only or logo work when behavior and interaction quality are the target.

## Required inputs
- Product context and target interface scope (2-3 screens or sections maximum).
- Performance and accessibility constraints.
- Persona references or style constraints (for example `@benjitaylor`, `@jenny_wen`).
- Required assets, existing component library, and design source of truth.
- Deployment risk tolerance and review cadence.

## Deliverables
- Bounded design recommendation with:
  - proposed interaction approach,
  - concrete motion system,
  - implementation sequence,
  - validation checkpoints (accessibility, responsiveness, performance).
- Clear "why this way" rationale and tradeoffs.
- Suggested fallback for constraints or blocked motion/runtime conditions.
- Include `schema_version` in output contracts for machine-checkable notes.

## Procedure
### 1) Scope narrowing
- Start with the smallest viable surface: one screen and up to 3 interaction clusters.
- Add one variant per cycle only after the first set is validated.

### 2) Build recommendation
- Select persona guidance from available references.
- Define component-level behavior, motion levels, and visual hierarchy.
- Add explicit tradeoffs for performance and maintainability.

### 3) Validate
- Run accessibility and clarity checks before recommending final motion intensity.
- Flag any unsupported claims and replace with conservative alternatives.

## Validation
- Must include explicit verification language for layout, motion, and accessibility.
- Validate with concrete acceptance checks (for example reduced cognitive load, no accessibility violations, no expensive motion on low-end paths).
- If checks are incomplete, return a partial result and ask for missing constraints.
- Validation is fail-fast: if a required check fails, stop and only continue after user confirmation.

## Anti-patterns
- Design without user constraints (scope drift).
- Converting every page to a bespoke system instead of extending current components.
- Overusing heavy motion before proving baseline clarity.
- Treating this as brand identity work.

## Constraints
- Redact sensitive references or credentials if any are shared.
- Keep recommendations executable within the repo's stack and avoid impossible dependencies.
- Preserve low-motion and reduced-motion behavior when appropriate.

## Philosophy
- Keep recommendations concrete, specific, and implementation-ready.
- Prefer fewer, higher-quality interactions over many speculative ideas.
- Stay focused on user outcomes, not decorative novelty.

## Examples
- "Can you inspect the settings panel in this Tauri app and use one motion pattern with a low-motion fallback?"
- "I need a practical redesign for the dashboard loading and error states so users can tell what's happening at a glance."
- "How can I tune the interactions on this three-tab settings screen and validate that it still feels responsive?"

## Failure mode
- If no source constraints or target screen are provided, request scope before proposing a design approach.
- If required persona references are unavailable, proceed with neutral defaults and state the assumption.

## Variation
- Vary output depth by context: start with a small, explicit interaction area and then offer one optional expansion pass for broader screen polish if the user wants more breadth.

## References
- Reference contracts and examples are in `references/contract.yaml`, `references/evals.yaml`, `references/benjitaylor-persona.md`, `references/emilkowalski-persona.md`, and `references/design-taste-overlay.md`.
- Runtime or benchmark examples live in `references/motion-guidelines.md` and `references/examples.md`.
- Execution helpers: `scripts/` (validation scripts), `assets/` (reference imagery and patterns).
- Policy notes and task routing: `references/task-profile.json`, `task-profile` links in `references/project-review-mode.md`.

## Gotchas
- None yet. Capture recurring failures here as symptom -> cause -> do instead -> check.
