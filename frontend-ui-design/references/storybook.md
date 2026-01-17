# Storybook (ChatUI)

Last verified: 2026-01-01

## Purpose
Storybook is the primary surface for component documentation, interaction testing, accessibility checks, and visual regression.

## Where it lives
- App: `apps/storybook`
- Guide: `packages/ui/STORYBOOK_GUIDE.md`

## Standard commands
- `pnpm storybook:dev`
- `pnpm storybook:build`
- `pnpm storybook:test`
- `pnpm test:visual:storybook`
- `pnpm test:visual:storybook:update`

## Story conventions
- Prefer `@storybook/react-vite` for typings in `*.stories.tsx` files.
- Add stories for new or changed UI components.
- Include interaction tests via `play` where meaningful.
- Use the a11y addon to validate labels, contrast, and keyboard behavior.

## Tool-output alignment
- When relevant, add stories that mirror tool output payloads to keep UI aligned with runtime schemas.

## Stricter checklist (required for new or changed UI)
- Add stories for: default, hover (if applicable), focus, pressed, disabled, empty, error.
- Include at least one interaction test for critical behaviors (`play` with assertions).
- Verify keyboard navigation in Storybook (tab order, activation, focus ring).
- Run a11y addon checks and fix violations for each state.
- If visuals change, update visual regression baselines.
- Use docs blocks (MDX or CSF docs) for usage notes and prop intent.
- Avoid ad-hoc styling in stories; use tokens and real component props.

## External docs
- https://storybook.js.org/docs/
