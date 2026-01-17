# Web mapping (CSS vars + Tailwind v4 + Apps SDK UI)

## CSS var naming
- `color.text.primary` -> `--color-text-primary`
- `space.3` -> `--space-3`
- `radius.md` -> `--radius-md`

## Required files
- `tokens.css`: raw vars for each mode selector
- `theme.css`: mode selectors:
  - `[data-theme="light"]`, `[data-theme="dark"]`
  - `[data-contrast="more"]` (optional)
  - `[data-density="compact|comfortable"]`

## Apps SDK UI integration
Global stylesheet must include:
- Tailwind import
- Apps SDK UI CSS import
- `@source` directive so Tailwind sees class usage in node_modules

(Keep Apps SDK widget constraints from the adapter in effect.)
