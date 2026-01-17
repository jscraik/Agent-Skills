# Design Guidelines (canonical, all projects)
Last updated: 2026-01-12  
Audience: Developers (beginner–intermediate)  
Scope: Task-focused instructions; applies to ChatGPT widgets and standalone apps across *all* projects.  
Owner/Review cadence: TBD

> Use this as the canonical reference. Load when working on shared UI/UX or aligning any project to the common token/system. For a quick summary see `design-guidelines-summary.md`.

## Table of contents
- Core principles
- Component usage
- Layout and spacing
- Colors and typography
- Icons and imagery
- Accessibility checklist
- Review standard
- Verify
- Related docs
- Appendix A–J (Patterns, Anti-Patterns, Decisions, Sharp Edges, Branding)
- Tokens (DTCG) — see `index.dtcg.json`

## Core principles
- **Use Apps SDK UI first.** Prefer `@openai/apps-sdk-ui` components and your shared UI wrappers.
- **Avoid raw tokens in production UI.** Tokens packages are for audits and extensions only.
- **Match the system defaults.** Stick to component defaults before adding custom styling.
- **Accessibility is non-negotiable.** Every interactive control must be usable by keyboard and assistive tech.

## Component usage
- Use the UI library exports:
  ```tsx
  import { Button, Card, IconButton } from "@your/ui";
  ```
- For tree-shaking:
  ```tsx
  import { Button, SectionHeader } from "@your/ui/base";
  ```
- Avoid direct imports from underlying libraries:
  - Do **not** import `@radix-ui/*` outside primitives.
  - Do **not** import `lucide-react` directly; use the shared icons adapter.

## Layout and spacing
- Use layout components (`Card`, `SectionHeader`, `CollapsibleSection`) before custom containers.
- Keep layouts simple: one primary column, consistent padding, predictable section breaks.
- Prefer `flex`/`grid` with Tailwind utilities; avoid absolute positioning unless required.

## Colors and typography
- Use component defaults and semantic classes from Apps SDK UI.
- Do **not** hardcode hex colors or raw CSS variables in new UI code.
- If you need a token, add it to the shared UI layer/Apps SDK UI, not directly in the page.

## Icons and imagery
- Use existing icons from the adapter before adding new SVGs.
- Provide accessible names for icon-only controls (aria-label, title, or visually hidden text).

## Accessibility checklist
Every new UI surface should pass:
- All interactive elements reachable by keyboard.
- Visible focus styles (not color-only).
- Icon-only buttons have accessible labels.
- Dialogs and menus announced correctly by screen readers.

Tests:
- `pnpm test:a11y:widgets`
- `docs/KEYBOARD_NAVIGATION_TESTS.md`

## Review standard
- Component/styling choices align with Apps SDK UI.
- No raw tokens/hex colors introduced.
- A11y checks satisfied; tests updated if needed.

## Verify
- `pnpm lint:compliance` catches forbidden imports/token misuse.
- `pnpm test:a11y:widgets` confirms keyboard and screen reader paths for widgets.

## Related docs
- `packages/ui/README.md`
- `docs/guides/PAGES_QUICK_START.md`
- `docs/KEYBOARD_NAVIGATION_TESTS.md`

## Appendices
Appendix A–J contain UI/UX/Brand patterns, anti-patterns, decisions, and sharp edges. Apply them in SwiftUI surfaces too.

## Tailwind preset (bind tokens to Tailwind)
Use this preset to wire DTCG-derived CSS variables into Tailwind (adapt package names as needed):
```ts
import type { Config } from "tailwindcss";

const preset: Config = {
  theme: {
    extend: {
      colors: {
        foundation: {
          "bg-dark-1": "var(--foundation-bg-dark-1)",
          "bg-dark-2": "var(--foundation-bg-dark-2)",
          "bg-dark-3": "var(--foundation-bg-dark-3)",
          "bg-light-1": "var(--foundation-bg-light-1)",
          "bg-light-2": "var(--foundation-bg-light-2)",
          "bg-light-3": "var(--foundation-bg-light-3)",
          "text-dark-primary": "var(--foundation-text-dark-primary)",
          "text-dark-secondary": "var(--foundation-text-dark-secondary)",
          "text-dark-tertiary": "var(--foundation-text-dark-tertiary)",
          "text-light-primary": "var(--foundation-text-light-primary)",
          "text-light-secondary": "var(--foundation-text-light-secondary)",
          "text-light-tertiary": "var(--foundation-text-light-tertiary)",
          "icon-dark-primary": "var(--foundation-icon-dark-primary)",
          "icon-dark-secondary": "var(--foundation-icon-dark-secondary)",
          "icon-dark-tertiary": "var(--foundation-icon-dark-tertiary)",
          "icon-dark-inverted": "var(--foundation-icon-dark-inverted)",
          "icon-dark-accent": "var(--foundation-icon-dark-accent)",
          "icon-dark-status-error": "var(--foundation-icon-dark-status-error)",
          "icon-dark-status-warning": "var(--foundation-icon-dark-status-warning)",
          "icon-dark-status-success": "var(--foundation-icon-dark-status-success)",
          "icon-light-primary": "var(--foundation-icon-light-primary)",
          "icon-light-secondary": "var(--foundation-icon-light-secondary)",
          "icon-light-tertiary": "var(--foundation-icon-light-tertiary)",
          "icon-light-inverted": "var(--foundation-icon-light-inverted)",
          "icon-light-accent": "var(--foundation-icon-light-accent)",
          "icon-light-status-error": "var(--foundation-icon-light-status-error)",
          "icon-light-status-warning": "var(--foundation-icon-light-status-warning)",
          "icon-light-status-success": "var(--foundation-icon-light-status-success)",
          "border-light": "var(--foundation-border-light)",
          "border-heavy": "var(--foundation-border-heavy)",
          "border-dark-default": "var(--foundation-border-dark-default)",
          "border-dark-light": "var(--foundation-border-dark-light)",
          "accent-gray": "var(--foundation-accent-gray)",
          "accent-red": "var(--foundation-accent-red)",
          "accent-orange": "var(--foundation-accent-orange)",
          "accent-yellow": "var(--foundation-accent-yellow)",
          "accent-green": "var(--foundation-accent-green)",
          "accent-blue": "var(--foundation-accent-blue)",
          "accent-purple": "var(--foundation-accent-purple)",
          "accent-pink": "var(--foundation-accent-pink)",
          "accent-gray-light": "var(--foundation-accent-gray-light)",
          "accent-red-light": "var(--foundation-accent-red-light)",
          "accent-orange-light": "var(--foundation-accent-orange-light)",
          "accent-yellow-light": "var(--foundation-accent-yellow-light)",
          "accent-green-light": "var(--foundation-accent-green-light)",
          "accent-blue-light": "var(--foundation-accent-blue-light)",
          "accent-purple-light": "var(--foundation-accent-purple-light)",
          "accent-pink-light": "var(--foundation-accent-pink-light)",
        },
      },
      spacing: {
        "128": "128px",
        "64": "64px",
        "48": "48px",
        "40": "40px",
        "32": "32px",
        "24": "24px",
        "16": "16px",
        "12": "12px",
        "8": "8px",
        "4": "4px",
        "2": "2px",
        "0": "0px",
      },
      fontSize: {
        "heading-1": [
          "var(--foundation-heading-1-size)",
          { lineHeight: "var(--foundation-heading-1-line)", letterSpacing: "var(--foundation-heading-1-tracking)", fontWeight: "var(--foundation-heading-1-weight)" },
        ],
        "heading-2": [
          "var(--foundation-heading-2-size)",
          { lineHeight: "var(--foundation-heading-2-line)", letterSpacing: "var(--foundation-heading-2-tracking)", fontWeight: "var(--foundation-heading-2-weight)" },
        ],
        "heading-3": [
          "var(--foundation-heading-3-size)",
          { lineHeight: "var(--foundation-heading-3-line)", letterSpacing: "var(--foundation-heading-3-tracking)", fontWeight: "var(--foundation-heading-3-weight)" },
        ],
        body: [
          "var(--foundation-body-size)",
          { lineHeight: "var(--foundation-body-line)", letterSpacing: "var(--foundation-body-tracking)", fontWeight: "var(--foundation-body-weight-regular)" },
        ],
        "body-emphasis": [
          "var(--foundation-body-size)",
          { lineHeight: "var(--foundation-body-line)", letterSpacing: "var(--foundation-body-tracking)", fontWeight: "var(--foundation-body-weight-emphasis)" },
        ],
        "body-small": [
          "var(--foundation-body-small-size)",
          { lineHeight: "var(--foundation-body-small-line)", letterSpacing: "var(--foundation-body-small-tracking)", fontWeight: "var(--foundation-body-small-weight-regular)" },
        ],
        "body-small-emphasis": [
          "var(--foundation-body-small-size)",
          { lineHeight: "var(--foundation-body-small-line)", letterSpacing: "var(--foundation-body-small-tracking)", fontWeight: "var(--foundation-body-small-weight-emphasis)" },
        ],
        caption: [
          "var(--foundation-caption-size)",
          { lineHeight: "var(--foundation-caption-line)", letterSpacing: "var(--foundation-caption-tracking)", fontWeight: "var(--foundation-caption-weight-regular)" },
        ],
        "caption-emphasis": [
          "var(--foundation-caption-size)",
          { lineHeight: "var(--foundation-caption-line)", letterSpacing: "var(--foundation-caption-tracking)", fontWeight: "var(--foundation-caption-weight-emphasis)" },
        ],
        "card-title": [
          "var(--foundation-card-title-size)",
          { lineHeight: "var(--foundation-card-title-line)", letterSpacing: "var(--foundation-card-title-tracking)", fontWeight: "var(--foundation-card-title-weight)" },
        ],
        "list-title": [
          "var(--foundation-list-title-size)",
          { lineHeight: "var(--foundation-list-title-line)", letterSpacing: "var(--foundation-list-title-tracking)", fontWeight: "var(--foundation-list-title-weight)" },
        ],
        "list-subtitle": [
          "var(--foundation-list-subtitle-size)",
          { lineHeight: "var(--foundation-list-subtitle-line)", letterSpacing: "var(--foundation-list-subtitle-tracking)", fontWeight: "var(--foundation-list-subtitle-weight)" },
        ],
        "button-label": [
          "var(--foundation-button-label-size)",
          { lineHeight: "var(--foundation-button-label-line)", letterSpacing: "var(--foundation-button-label-tracking)", fontWeight: "var(--foundation-button-label-weight)" },
        ],
        "button-label-small": [
          "var(--foundation-button-label-small-size)",
          { lineHeight: "var(--foundation-button-label-small-line)", letterSpacing: "var(--foundation-button-label-small-tracking)", fontWeight: "var(--foundation-button-label-small-weight)" },
        ],
      },
      fontFamily: {
        foundation: ["var(--foundation-font-family)", "sans-serif"],
      },
      letterSpacing: {
        "heading-1": "var(--foundation-heading-1-tracking)",
        "heading-2": "var(--foundation-heading-2-tracking)",
        "heading-3": "var(--foundation-heading-3-tracking)",
        body: "var(--foundation-body-tracking)",
        "body-small": "var(--foundation-body-small-tracking)",
        caption: "var(--foundation-caption-tracking)",
        "card-title": "var(--foundation-card-title-tracking)",
        "list-title": "var(--foundation-list-title-tracking)",
        "list-subtitle": "var(--foundation-list-subtitle-tracking)",
        "button-label": "var(--foundation-button-label-tracking)",
        "button-label-small": "var(--foundation-button-label-small-tracking)",
      },
      lineHeight: {
        "heading-1": "var(--foundation-heading-1-line)",
        "heading-2": "var(--foundation-heading-2-line)",
        "heading-3": "var(--foundation-heading-3-line)",
        body: "var(--foundation-body-line)",
        "body-small": "var(--foundation-body-small-line)",
        caption: "var(--foundation-caption-line)",
        "card-title": "var(--foundation-card-title-line)",
        "list-title": "var(--foundation-list-title-line)",
        "list-subtitle": "var(--foundation-list-subtitle-line)",
        "button-label": "var(--foundation-button-label-line)",
        "button-label-small": "var(--foundation-button-label-small-line)",
      },
      borderRadius: {
        6: "var(--foundation-radius-6)",
        8: "var(--foundation-radius-8)",
        10: "var(--foundation-radius-10)",
        12: "var(--foundation-radius-12)",
        16: "var(--foundation-radius-16)",
        18: "var(--foundation-radius-18)",
        21: "var(--foundation-radius-21)",
        24: "var(--foundation-radius-24)",
        30: "var(--foundation-radius-30)",
        round: "var(--foundation-radius-round)",
      },
      boxShadow: {
        "foundation-card": "var(--foundation-shadow-card)",
        "foundation-pip": "var(--foundation-shadow-pip)",
        "foundation-pill": "var(--foundation-shadow-pill)",
        "foundation-close": "var(--foundation-shadow-close)",
      },
    },
  },
};

export default preset;
```

## Tokens
- Canonical DTCG token source: `references/index.dtcg.json`.
- Do **not** copy raw values; consume semantic tokens via platform adapters.
