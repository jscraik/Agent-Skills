# Motion Performance Guardrails (Fast Pass)

Apply when adding or refactoring motion. Prioritize compositor-friendly updates.

## Never patterns (critical)
- Do not interleave layout reads and writes in the same frame.
- Do not animate layout continuously on large surfaces.
- Do not drive animation from `scrollTop`, `scrollY`, or scroll events.
- No `requestAnimationFrame` loops without a stop condition.
- Do not mix multiple animation systems that each measure or mutate layout.

## Mechanism choice
- Prefer `transform` and `opacity` for motion.
- Use JS-driven animation only when interaction requires it.
- Paint/layout animation only on small, isolated elements.

## Measurement
- Measure once, then animate via transform/opacity.
- Batch all DOM reads before writes.
- Avoid repeated measurement during an animation.

## Scroll + visibility
- Prefer Scroll/View Timelines where available.
- Use `IntersectionObserver` to pause when off-screen.

## Paint + layers
- Avoid animating paint-heavy properties on large surfaces.
- Use `will-change` temporarily and surgically.

## Blur + filters
- Avoid continuous blur. If used, keep <= 8px and short-lived.
- Never animate blur on large surfaces.
