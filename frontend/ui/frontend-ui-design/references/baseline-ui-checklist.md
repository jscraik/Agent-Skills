# Baseline UI Guardrails (Fast Pass)

Purpose: prevent low-quality UI output. Apply these defaults unless the brief or brand explicitly overrides them.

## Stack + primitives
- Use Tailwind CSS defaults; only add custom values if already present or explicitly requested.
- Use existing primitives first (Radix UI in this stack). Use Base UI only if it already exists or is explicitly requested.
- Use the repo’s `cn` utility for class merging when present.
- Icon-only buttons must include `aria-label` or `aria-labelledby`.

## Interaction + layout
- Use `h-dvh` instead of `h-screen`.
- Respect `env(safe-area-inset-*)` for fixed elements.
- Use `AlertDialog` for destructive actions.
- Show errors next to the action/field; avoid global-only errors.
- Never block paste in inputs/textarea elements.

## Typography + data
- Headings: `text-balance`. Body: `text-pretty`.
- Data: `tabular-nums`.
- Dense UI: `truncate` or `line-clamp` where needed.
- Avoid `tracking-*` unless explicitly requested.

## Layout + z-index
- Use a fixed z-index scale (no arbitrary `z-*`).
- Use `size-*` for square elements instead of `w-*` + `h-*`.

## Motion + performance
- If JS animation is required, use `motion/react` (stack default).
- Prefer Tailwind utilities for micro-animations; use `tw-animate-css` only if already installed.
- Animate only `transform` and `opacity`.
- Avoid layout/size animation on large surfaces.
- Interaction feedback <= 200ms; use `ease-out` for entrances.
- Pause looping animations off-screen; respect `prefers-reduced-motion`.
- Avoid large `blur()`/`backdrop-filter` animations; never use `will-change` outside active animation.
- Avoid `useEffect` for logic that can be expressed as render logic.

## Visual style (defaults)
- Avoid gradients or glow effects unless explicitly requested.
- Limit accent color usage to one per view by default.
