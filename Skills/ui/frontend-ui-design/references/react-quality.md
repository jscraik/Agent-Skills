# React Quality Standards (Dec 2025)

Last verified: 2026-01-01

Use when writing React for Apps SDK UI or web.

## Primary docs
- https://react.dev/learn

## State colocation
- Keep state as local as possible; avoid global state unless needed.
- Prefer derived state over duplicated state.

## Rendering performance
- Avoid heavy work in render; move to memoized helpers.
- Use memoization only when profiling indicates re-render cost.
- Prefer `useMemo`/`useCallback` only when props are stable and dependencies are correct.
- Avoid deep prop comparison; restructure data instead.

## Accessibility
- Prefer semantic HTML elements.
- Ensure labeled controls and correct roles.
- Keyboard behavior matches ARIA APG patterns.
- Respect `prefers-reduced-motion` and `prefers-contrast` in motion/color.
- Ensure focus-visible rings are keyboard-only.
- Support RTL layout mirroring when directional UI is present.

## Composition
- Favor small, focused components.
- Avoid prop-drilling by using context only when shared across deep trees.

## Error handling
- Handle loading/empty/error states explicitly.
- Use error boundaries for non-trivial trees (per-route or per-widget).
