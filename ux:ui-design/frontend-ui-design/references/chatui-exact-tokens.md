# ChatUI Exact Tokens + Layout Rules (Authoritative)

Last verified: 2026-01-04

Use this reference when the task targets `/Users/jamiecraik/chatui` and you
must quote exact values for colors, typography, spacing, iconography, and
layout rules. These values are generated from the DTCG token source and the
ChatUI icon system; do not edit tokens directly.

Primary sources:
- Tokens source of truth: `packages/tokens/src/tokens/index.dtcg.json`
- Generated token exports: `packages/tokens/src/colors.ts`,
  `packages/tokens/src/typography.ts`, `packages/tokens/src/spacing.ts`,
  `packages/tokens/src/sizes.ts`
- Audit-only CSS vars: `packages/tokens/src/foundations.css`
- Tailwind preset: `packages/tokens/tailwind.preset.ts`
- Icon system: `packages/ui/src/icons/ICON_SYSTEM.md`
- Layout rules: `docs/guides/DESIGN_GUIDELINES.md`,
  `docs/guides/PAGES_QUICK_START.md`

Note: For production UI, prefer Apps SDK UI components and `@chatui/ui`
wrappers. This reference is for audits/specs or when explicitly asked for
exact values.

## Colors (exact values)

background.light:
- primary #FFFFFF
- secondary #E8E8E8
- tertiary #F3F3F3

background.dark:
- primary #212121
- secondary #303030
- tertiary #414141

text.light:
- primary #0D0D0D
- secondary #5D5D5D
- tertiary #8F8F8F
- inverted #FFFFFF

text.dark:
- primary #FFFFFF
- secondary #CDCDCD
- tertiary #AFAFAF
- inverted #0D0D0D

icon.light:
- primary #0D0D0D
- secondary #5D5D5D
- tertiary #8F8F8F
- inverted #FFFFFF
- accent #0285FF
- statusError #E02E2A
- statusWarning #E25507
- statusSuccess #008635

icon.dark:
- primary #FFFFFF
- secondary #CDCDCD
- tertiary #AFAFAF
- inverted #0D0D0D
- accent #48AAFF
- statusError #FF8583
- statusWarning #FF9E6C
- statusSuccess #40C977

border.light:
- light #0D0D0D0D
- heavy #0D0D0D26

border.dark:
- default #FFFFFF26
- light #FFFFFF0D

accent.light:
- gray #8F8F8F
- red #E02E2A
- orange #E25507
- yellow #C08C00
- green #008635
- blue #0285FF
- purple #934FF2
- pink #E3008D
- foreground #FFFFFF

accent.dark:
- gray #ABABAB
- red #FF8583
- orange #FF9E6C
- yellow #FFD666
- green #40C977
- blue #5A9FF5
- purple #BA8FF7
- pink #FF6BC7
- foreground #FFFFFF

interactive:
- ring #0285FF (light and dark)

## Typography (exact values)

fontFamily (token): "SF Pro"
fontFamily (CSS stack): "SF Pro", "SF Pro Text", -apple-system,
  BlinkMacSystemFont, "Segoe UI", sans-serif

heading1: size 36, lineHeight 40, weight 600, tracking -0.1
heading2: size 24, lineHeight 28, weight 600, tracking -0.25
heading3: size 18, lineHeight 26, weight 600, tracking -0.45
body: size 16, lineHeight 26, weight 400, emphasisWeight 600, tracking -0.4
bodySmall: size 14, lineHeight 18, weight 400, emphasisWeight 600, tracking -0.3
caption: size 12, lineHeight 16, weight 400, emphasisWeight 600, tracking -0.1
cardTitle: size 17, lineHeight 23, weight 500, tracking -0.43
listTitle: size 17, lineHeight 24, weight 400, tracking -0.4
listSubtitle: size 14, lineHeight 20, weight 400, tracking -0.18
buttonLabel: size 15, lineHeight 24, weight 500, tracking -0.24
buttonLabelSmall: size 14, lineHeight 20, weight 600, tracking -0.3

## Spacing + sizes (exact values)

Spacing scale (px): 128, 64, 48, 40, 32, 24, 16, 12, 8, 4, 2, 0

Size tokens (px):
- controlHeight 44
- cardHeaderHeight 56
- hitTarget 44

## Iconography (exact system)

Authoritative system:
- `packages/ui/src/icons/ICON_SYSTEM.md`
- Components: `packages/ui/src/icons/ChatGPTIcons.ts`
- Visual catalog: `packages/ui/src/icons/ChatGPTIconCatalog.tsx`

Sizes (px):
- xs 12
- sm 16
- md 20
- lg 24 (default)
- key 32
- toggle 44x24

Rules:
- Use the icons adapter in `packages/ui/src/icons`.
- Do not import `lucide-react` directly.
- Provide accessible names for icon-only controls.

## Layout rules (ChatUI)

From `docs/guides/DESIGN_GUIDELINES.md`:
- Use layout components (`Card`, `SectionHeader`, `CollapsibleSection`)
  before writing custom containers.
- Keep layouts simple: one primary column, consistent padding,
  predictable section breaks.
- Prefer `flex` and `grid` via Tailwind utilities.
- Avoid absolute positioning unless required.

From `docs/guides/PAGES_QUICK_START.md` (starter layout pattern):
- Header with `p-4`, simple back action, title.
- Content container: `mx-auto max-w-4xl p-6`
- Content sections wrapped in `Card` with `p-6`
