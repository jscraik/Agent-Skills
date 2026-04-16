# Extended guidance

## Workflow A — Code-first UI (Tailwind v4 + Radix)
Use when you need to ship UI quickly and validate in real code.

1. Pick or create tokens (semantic first).
2. Implement layout with Tailwind utilities.
3. Wrap behavior with Radix primitives.
4. Style states via `data-*` and CSS variables.
5. Add Storybook story and cover:
   - default, hover/focus, disabled
   - loading/error/empty where applicable
6. Add motion (enter/exit/feedback), respecting reduced motion.

Deliverables:
- Component file(s)
- Storybook story
- Updated tokens/theme (if needed)
- Notes on states + keyboard behavior

## Workflow B — Figma-first UI (Make → Dev Mode → Code)
Use when a Figma file exists or you can generate a first draft.

1. Generate or review a first draft (Figma Make / design file).
2. Identify:
   - tokens/variables (colors, type scale, spacing, radii)
   - components (buttons, inputs, dialogs)
   - key states (loading/error/empty)
3. Map design → code:
   - tokens → Tailwind `@theme` variables
   - components → Radix-based primitives
4. Implement the UI in code and re-check in the running app/Storybook.

If MCP tooling is available, prefer “extract real values” over guessing.

Deliverables:
- Token mapping table (Figma variable → CSS var/Tailwind token)
- Component spec(s)
- Implemented components + Storybook stories

### Figma Make best practices (from transcripts)
See `Infrastructure/references/figma-make.md`.

## Workflow C — Micro-interactions & motion pass
Use when UI is functional but feels flat.

1. Identify 1–2 key moments (hover, submit, success, error recovery).
2. Add motion for:
   - feedback (press, hover, drag)
   - transition (enter/exit)
   - continuity (reorder, expand/collapse)
3. Keep motion fast; reduce friction; never block completion.
4. Ensure:
   - keyboard focus remains stable
   - reduced-motion fallback exists
   - performance stays smooth

Deliverables:
- Motion spec update
- Implementation + Storybook story showing interactions

## Workflow D — Three.js/WebGL accent (optional)
Use for subtle delight (hero accent, background, celebratory moment), not core UI.

Rules:
- Gate with feature flag / visibility heuristics.
- Provide fallback (static image/CSS) and respect reduced motion.
- Keep GPU cost bounded; prefer “accent” not “always animating”.

Deliverables:
- Small isolated scene component
- Performance notes + fallback behavior
- Toggle/flag and Storybook story

## Workflow E — ChatGPT app UI (OpenAI Apps SDK)
Use when building within the Apps SDK. Align to its UI patterns (cards, carousel, fullscreen).

Deliverables:
- View selection (inline vs fullscreen)
- UX flow aligned to tool results and loading/error states
- Components consistent with Apps SDK UI guidelines

---

# Implementation guardrails (summary)

Accessibility, performance, and quality baselines are mandatory.
See `Infrastructure/references/guardrails.md` for the full checklists and examples.

---

# Assets, references, and scripts (summary)

- Templates live in `assets/` (briefs, component specs, motion specs, tokens, acceptance checklists, prompt flows).
- Deep guidance lives in `Infrastructure/references/` (influences, token architecture, stack, handoff, gradients).
- Useful scripts: `Infrastructure/scripts/skill_lint.mjs`, `Infrastructure/scripts/tokens_to_tailwind_theme.mjs`, `Infrastructure/scripts/contrast_check.mjs`, `Infrastructure/scripts/scaffold_component.mjs`.

## Remember

The agent is capable of extraordinary work in this domain. These guidelines unlock that potential—they don't constrain it.
Use judgment, adapt to context, and push boundaries when appropriate.

---

# Invocation examples

See `Infrastructure/references/invocation-examples.md`.

---

## Remember
The agent is capable of extraordinary work in this domain. Use judgment, adapt to context, and push boundaries when appropriate.

## Scripts
- `Infrastructure/scripts/contrast_check.mjs`
- `Infrastructure/scripts/scaffold_component.mjs`
- `Infrastructure/scripts/skill_lint.mjs`
- `Infrastructure/scripts/tokens_to_tailwind_theme.mjs`

---

## Remember
The agent is capable of extraordinary work in this domain. Use judgment, adapt to context, and push boundaries when appropriate.

## Scripts
- `Infrastructure/scripts/contrast_check.mjs`
- `Infrastructure/scripts/scaffold_component.mjs`
- `Infrastructure/scripts/skill_lint.mjs`
- `Infrastructure/scripts/tokens_to_tailwind_theme.mjs`

---

## Remember
The agent is capable of extraordinary work in this domain. Use judgment, adapt to context, and push boundaries when appropriate.

## Scripts
- `Infrastructure/scripts/contrast_check.mjs`
- `Infrastructure/scripts/scaffold_component.mjs`
- `Infrastructure/scripts/skill_lint.mjs`
- `Infrastructure/scripts/tokens_to_tailwind_theme.mjs`
