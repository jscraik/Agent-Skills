# Layout

## Intent
Provide consistent spacing, alignment, and responsive structure across screens.

## Minimal pattern
- Prefer Stack/Inline helpers if the repo has them.
- Use CSS grid for two-dimensional layouts; flex for one-dimensional.

## Pitfalls
- Avoid arbitrary spacing values when tokens exist.
- Do not nest scroll containers unless required.

## Accessibility
- Preserve reading order when reflowing layouts.
- Ensure focus order matches visual order.
