# SwiftUI Design Guidelines (summary, canonical across projects)

Last updated: 2026-01-12
Owner: TBD
Review cadence: TBD
Audience: SwiftUI developers (beginner–intermediate)
Scope: task-focused guidance for shared UI used across ChatGPT widgets and standalone apps.
Non-scope: full architecture reference.

## Core principles
- Use Apps SDK UI first; prefer `@openai/apps-sdk-ui` and shared UI wrappers.
- Avoid raw tokens in production UI; tokens packages are for audits/extension.
- Match component defaults before custom styling.
- Accessibility is non-negotiable (keyboard + assistive tech for every control).

## Component usage
- Import via your shared UI package (or `/base` subpaths for tree-shaking).
- No direct `@radix-ui/*` imports outside primitives; do not import `lucide-react` directly—use the icons adapter.

## Layout & spacing
- Prefer `Card`, `SectionHeader`, `CollapsibleSection` before custom containers.
- Simple layouts: primary column, consistent padding, predictable breaks.
- Use flex/grid; avoid absolute positioning unless required.

## Colors & typography
- Use component defaults and semantic classes from Apps SDK UI.
- Never hardcode hex/CSS vars; add tokens in the shared UI layer (not in-page).

## Icons & imagery
- Use existing icons from the adapter; add labels for icon-only controls (aria-label/title/visually-hidden).

## Accessibility checklist
- All controls keyboard reachable; visible focus; icon-only buttons labeled; dialogs/menus announced.
- Run `pnpm test:a11y:widgets`; see `docs/KEYBOARD_NAVIGATION_TESTS.md`.

## Review standard
- Choices align with Apps SDK UI; no raw tokens/hex; a11y checks/tests updated.

## Verify commands
- `pnpm lint:compliance` (forbidden imports/token misuse)
- `pnpm test:a11y:widgets`

## Related docs
- Component usage: `packages/ui/README.md`
- Page patterns: `docs/guides/PAGES_QUICK_START.md`
- A11y tests: `docs/KEYBOARD_NAVIGATION_TESTS.md`

## Appendices (UI/UX/Brand)
See `swiftui-ui-patterns` skill appendices for patterns, anti-patterns, decisions, and sharp edges. Apply the same principles in SwiftUI surfaces.

## Tokens
- Use the canonical DTCG token source of truth: `references/index.dtcg.json`.
- Do not copy raw values; consume semantic tokens exposed via platform adapters.
