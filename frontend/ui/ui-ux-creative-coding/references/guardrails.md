# Implementation Guardrails

## Accessibility (minimum bar)
- Keyboard navigation for all controls
- Visible focus states
- Semantic structure (headings, landmarks)
- Reduced motion (`prefers-reduced-motion`) behavior
- Color contrast checks (use `scripts/contrast_check.mjs` if you have tokens)

## Performance (minimum bar)
- Avoid long main-thread tasks (especially with continuous animation)
- Don’t animate layout; prefer transforms/opacity
- Avoid re-render storms; memoize where needed
- For WebGL: avoid always-on high-FPS backgrounds; throttle/idle

## Quality (minimum bar)
- Storybook story for each new/changed component
- Argos snapshots for key variants
- Biome/TypeScript clean
- Document any non-obvious behavior (especially keyboard/focus)

## Example requests
- "Design a new settings panel for a Tauri app with a glassmorphism feel, but keep it accessible."
- "Refine this onboarding flow for React + Tailwind v4; add micro-interactions and a11y checks."
- "Prototype a dashboard layout with a subtle WebGL accent and a Storybook story."
