# Tailwind Best Practices (Dec 2025)

Last verified: 2026-01-01

Use when Tailwind is part of the stack.

## Tokens first
- All colors/spacing/typography map to CSS vars backed by tokens.
- No ad-hoc color literals or spacing classes that bypass tokens.
- Use `@layer base` to map tokens to CSS vars and `@layer components` for reusable patterns.

## Class organization
- Prefer component classes for repeated patterns.
- Group related utilities (layout > spacing > typography > color > effects).

## State coverage
- Provide hover/focus/pressed/disabled states via tokenized utilities.

## Theming
- Use theme selectors for light/dark/contrast/density.
- Avoid per-component theme logic; keep in theme layer.
- Provide `prefers-reduced-motion` and `prefers-contrast` variants where needed.

## Accessibility
- Ensure focus-visible styles are present and visible.
- Avoid color-only state indication.
- Ensure disabled states remain perceivable (contrast + non-color cues).
