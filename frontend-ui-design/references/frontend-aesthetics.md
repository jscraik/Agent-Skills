# Frontend Aesthetics (Web/React)

Last verified: 2026-01-01

Use this when building web UI or Apps SDK UI layouts to avoid generic design.

## Aesthetic commitment
- Choose a clear, specific aesthetic direction and execute it consistently.
- Ensure the UI is memorable through a distinctive visual choice (type, layout,
  palette, or motion) that fits the context.

## Typography
- Avoid generic fonts (Inter, Roboto, Arial, system).
- Pair a characterful display font with a readable body font.
- Ensure readability at small sizes and support scaling.

## Color and theme
- Use CSS variables for all colors.
- Prefer a cohesive palette with bold accents over evenly balanced colors.
- Avoid purple-on-white defaults unless explicitly requested.

## Layout and composition
- Use deliberate asymmetry, overlapping layers, or intentional grid breaks where
  appropriate.
- Balance negative space and density to match the aesthetic.

## Motion
- Provide one high-impact animation moment (e.g., page-load staggered reveal).
- Always include a reduced-motion alternative.
- Keep micro-interactions purposeful; avoid noisy motion.

## Backgrounds and texture
- Use gradients, subtle noise, or patterning to add depth.
- Avoid flat, single-color backgrounds when a richer atmosphere is needed.

## Anti-patterns to avoid
- Reusing the same layout or color scheme across unrelated tasks.
- Overused font families or predictable component patterns.
- Color-only state differentiation.
- Placeholder-only forms.
