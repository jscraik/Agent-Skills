# UI Spec Guide (Gold Standard, Jan 2026)

## Design system source of truth (aStudio)
Absolute root: `/Users/jamiecraik/dev/aStudio`

## Token source map (required)

| Category | Source | Notes |
| --- | --- | --- |
| Colors | `packages/tokens/src/tokens/index.dtcg.json` | Canonical token set |
| Typography scale | `packages/tokens/src/typography.ts` | Scale + weights |
| Spacing scale | `packages/tokens/src/spacing.ts` | 4px base scale |
| Sizes | `packages/tokens/src/sizes.ts` | Component sizes |
| Radii | `packages/tokens/src/radius.ts` | Corner radius tokens |
| Shadows | `packages/tokens/src/shadows.ts` | Elevation tokens |
| CSS vars | `packages/tokens/src/foundations.css`, `packages/tokens/src/tokens.css` | Runtime CSS variables |
| Tailwind preset | `packages/tokens/tailwind.preset.ts` | Preset for UI build |
| Icons | `packages/astudio-icons/src/Icon.tsx`, `packages/astudio-icons/src/registry.ts` | Icon registry and component |
| UI components | `packages/ui/README.md`, `packages/ui/src/` | Component registry |
| Brand | `brand/` | Logos and marks |
| Guidelines | `docs/guides/DESIGN_GUIDELINES.md` | UI rules and constraints |

## Gold UI Standard (Jan 2026)
- Accessibility baseline: WCAG 2.2 AA, keyboard-first, visible focus, icon labels.
- Contrast targets: text 4.5:1 (normal) / 3:1 (large); UI controls 3:1 minimum.
- Touch targets: 44x44px (mobile), 32x32px minimum (desktop).
- Hit-area spacing: minimum 8px between adjacent interactive targets.
- Layout: 4px spacing scale, consistent padding, avoid absolute positioning unless necessary.
- Responsive breakpoints: define token-based breakpoints and layout shifts.
- Grid sizes: define token-based grid (columns, gutters, margins) per breakpoint.
- Hit-area rules: document min target sizes (44x44 mobile, 32x32 desktop) and 8px spacing between adjacent targets.
- Typography: use aStudio type scale and semantic hierarchy; no ad-hoc sizes.
- Type rhythm: baseline grid and line-height rules; avoid orphans/widows.
- Color: use semantic tokens; avoid raw hex; contrast checked for text + UI.
- States: include empty/loading/success/partial/error plus disabled/hover/focus/pressed.
- Motion: define duration bands + easing; provide reduced-motion fallback; avoid motion-only meaning.
- Density modes: compact/cozy/comfortable rules with spacing deltas and usage guidance.
- Iconography: define grid size, stroke weight, alignment baseline, and naming conventions.

## Component registry check (required)
- Prefer `@astudio/ui` components and Apps SDK UI defaults.
- If a component is not in the registry, record the gap and proposed addition.

## State machine diagram style (required)
- Single vertical spine for the main happy path.
- Branch alternates to the sides.
- Label every transition with trigger/guard.
- Show timing hooks (e.g., periodic re-check).
- Use uppercase state names; concise trigger labels; avoid crossing lines.

## Evidence rules (required)
- Every section ends with `Evidence:` or `Evidence gap:`.
- Token references must include file path + token name.

## UI review gate (pass/fail)
- All UI values map to aStudio tokens, or explicit Evidence gaps are listed.
- Typography scale mapping table is complete.
- Icon usage rules are explicit and sourced.
- Spacing uses 4px scale with documented exceptions.
- State machine diagram exists for every component or view.
- WCAG 2.2 AA checklist completed (keyboard, focus, contrast, icon labels).
- No raw hex values.
- Contrast targets stated and verified for key text and controls.
- Touch target minimums documented for interactive elements.
- Hit-area spacing documented for adjacent controls.
- Motion system rules + reduced-motion fallback documented.
- Component states include disabled/hover/focus/pressed where applicable.
- Responsive breakpoints and grid sizes documented per layout.
