# Jhey Tompkins — CSS Micro‑Interaction Notes (Jan 2026)

Use these notes when the goal is playful, performant, CSS‑first interaction work.

## Core principles
- **CSS-first creativity**: start with transforms, masks, gradients, filters, and variables before JS.
- **Tiny systems**: a micro‑interaction is a state machine (default/hover/active/focus/disabled).
- **Performance by default**: avoid layout thrash; prefer transform/opacity.
- **Accessible delight**: semantic elements + reduced‑motion parity.

## Practical heuristics
- Prototype in isolation (Storybook or a minimal sandbox) to validate timing + state logic.
- Use **`data-*` state hooks** (e.g., Radix) to avoid JS state explosion.
- Keep **interaction loops short**; if it runs continuously, it must be visually quiet.
- Prefer **composable primitives** (utility classes + small CSS blocks) over bespoke components.

## Pattern ideas
- Masked reveals with `mask-image` or `clip-path`.
- Dynamic gradients on hover/focus using CSS variables.
- Spring‑like feel using timing + cubic‑bezier (or motion tokens) rather than heavy JS.
- “Depth hints” with subtle `translateZ/rotateX`—use sparingly.

## Checklist for reviews
- Are all interactive states covered (hover/focus/active/disabled/loading)?
- Does the animation rely on GPU‑friendly properties?
- Is reduced‑motion supported with equivalent feedback?
- Can this be done with CSS utilities + a small custom layer instead of a JS library?
