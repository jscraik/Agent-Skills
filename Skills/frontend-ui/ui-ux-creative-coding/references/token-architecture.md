# Token architecture (UI Collective distilled)

Use this when defining or auditing a token system.

## Recommended structures
- **Three‑tier (scales best):** Brand → Alias → Maps.
- **Two‑tier (acceptable):** Primitive → Semantic.

## Core rules
- Keep **Brand** values raw (color scales, sizes, weights).
- Use **Alias** to attach meaning (e.g., text/primary, surface/secondary).
- Use **Maps** to bind alias tokens to component states (hover/active/disabled).

## Scaling patterns
- Prefer a consistent **number scale** for spacing and type (4/8‑based or 100‑scale for colors).
- Don’t invent spacing; **audit existing files** and codify the real patterns.

## AI‑assisted tokens (Cursor/Figma MCP/Token Studio)
- AI is good for **drafts**, not final systems.
- Provide explicit rules for each collection before generation.
- Expect at least one **manual audit pass** for typography + mapped tokens.

## Validation checklist
- Are raw values separate from semantic usage?
- Are component states mapped and consistent?
- Do tokens prevent one‑off styling?
