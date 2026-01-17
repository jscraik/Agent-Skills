# Docs mapping (token -> web -> swift)

## Goal
Provide an always-current, human-readable reference that prevents cross-platform drift.

## Output file
- `docs/theming/token-reference.md`

## Structure (required headings)
1) Overview
2) Modes (light/dark/contrast/density)
3) Token tables (by domain)
4) Component consumption rules (React + Swift)
5) Drift prevention checklist

## Required columns (tables)
Each token row MUST include:

- Token path (DTCG): e.g., `color.text.primary`
- Type: `color | dimension | duration | cubicBezier | fontFamily | ...`
- Canonical value(s): per mode if applicable
- CSS var: e.g., `--color-text-primary`
- Tailwind usage: e.g., `text-[color:var(--color-text-primary)]` or preferred alias if you define one
- React consumption: class or component prop convention
- Swift API: e.g., `Tokens.color(.textPrimary)` / `Spacing.s3` / `Motion.short`
- Notes: a11y/perf constraints (hit target, contrast, reduced motion)

## Required domains
- Color (semantic first; palette optionally appended)
- Spacing
- Typography
- Radius
- Sizing (hit targets, control heights)
- Motion (duration + easing)
- Shadow/elevation (if used)

## Derived values
Docs must include:
- px and rem (1rem=16px unless overridden)
- pt mapping note for Apple (default 1:1 unless overridden)

## "Generated section" rule
If you want to allow manual prose around the tables, the generated tables must be wrapped:

<!-- GENERATED:tokens:start -->
(tables)
<!-- GENERATED:tokens:end -->

CI rule: only content inside GENERATED blocks may change during regen.
