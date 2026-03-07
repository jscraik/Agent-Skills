# Transcript-informed guidance (Jan 2026)

## Delight (beyond “sparkle”)
- Delight = **exceeding expectations**, not just visuals.
- Keep it purposeful: never block the main path.

## Design‑to‑dev handoff (non‑negotiables)
- Don’t assume developers infer interactions; **spell them out**.
- Provide **edge cases** and **state behavior** (loading/error/empty/disabled).
- Prefer explicit **accessibility semantics** (labels, focus, ARIA intent) over layout notes.

## Responsive component audit
- Most components **don’t need mobile variants**; only those with structural changes.
- Use “jumper” variables to map spacing between breakpoints.

## Token architecture (design systems)
- Prefer **Brand → Alias → Maps** (three‑tier) for scalability.
- Keep raw values in Brand; apply meaning in Alias/Maps.
- For heavy gradient use, add a **Gradients + Opacity** collection.
  - Name gradients by **stop direction** (top/right/left/bottom).
  - Maintain **inverse + overlay** variants for light/dark and overlays.

## AI usage reality check
- AI cannot reliably build production‑ready components or fully correct token systems.
- Use AI to **scaffold docs** and **accelerate exploration**, then audit.

## Production‑ready craft (Jh3yy signal)
- Avoid `<div role=button>` shortcuts; use semantic elements + real focus states.
- Treat accessibility as first‑class; don’t offload it to AI.

## Documentation pipeline (recommended)
- Start with a **skeleton** and map in real components via MCP/Figma selection.
- Keep docs concise: purpose, when to use, when not to use, states, a11y.
