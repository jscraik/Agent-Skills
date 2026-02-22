# Design-System Canonical Map

## Table of Contents
- [Token architecture](#token-architecture)
- [Typography](#typography)
- [Spacing and sizing](#spacing-and-sizing)
- [Color and semantic theming](#color-and-semantic-theming)
- [Iconography](#iconography)
- [Validation and policy](#validation-and-policy)
- [Fast retrieval commands](#fast-retrieval-commands)

## Token architecture
- **Brand source of truth (DTCG):** `packages/tokens/src/tokens/index.dtcg.json`
- **Generated foundations:** `packages/tokens/src/foundations.css`
- **Semantic aliases:** `packages/tokens/src/aliases.css`
- **Tailwind mapping:** `packages/tokens/tailwind.preset.ts`
- **Runtime mapped slots:** `packages/ui/src/styles/theme.css`
- **Governance contract:** `docs/design-system/CONTRACT.md`

## Typography
- DTCG keys: `type.fontFamily`, `type.web.*`
- Generated CSS vars: `--foundation-*-size`, `--foundation-*-line`, `--foundation-*-tracking`
- Tailwind utilities: `text-hero`, `text-h1`…`text-caption`, `text-body*`
- Storybook references:
  - `packages/ui/src/storybook/design-system/04_Typography/Typography.stories.tsx`
  - `packages/ui/src/design-system/showcase/TypographyShowcase.tsx`

## Spacing and sizing
- DTCG keys: `space.*`, `size.*`, `radius.*`
- Generated CSS vars: `--foundation-space-*`, `--foundation-size-*`, `--foundation-radius-*`
- Tailwind mappings:
  - `theme.extend.spacing`
  - `theme.extend.borderRadius`
  - `theme.extend.boxShadow`
- Storybook references:
  - `packages/ui/src/storybook/design-system/05_Spacing/Spacing.stories.tsx`
  - `packages/ui/src/storybook/design-system/06_Radius/Radius.stories.tsx`
  - `packages/ui/src/storybook/design-system/07_Sizes/Sizes.stories.tsx`
  - `packages/ui/src/storybook/design-system/08_Elevation/Elevation.stories.tsx`

## Color and semantic theming
- DTCG color groups: `color.background`, `color.text`, `color.icon`, `color.border`, `color.accent`, `color.interactive`
- Semantic alias variables: `--ds-*` in `packages/tokens/src/aliases.css`
- Runtime mapped variables: `--background`, `--foreground`, `--text-*`, `--color-*` in `packages/ui/src/styles/theme.css`
- Storybook references:
  - `packages/ui/src/storybook/design-system/03_Colors/Colors.stories.tsx`
  - `packages/ui/src/storybook/design-system/10_InteractiveStates/InteractiveStates.stories.tsx`

## Iconography
- Canonical import path: `@design-studio/ui/icons`
- Canonical index: `packages/ui/src/icons/index.ts`
- Consolidation notes: `docs/design-system/ICON_CONSOLIDATION.md`
- Storybook reference: `packages/ui/src/storybook/design-system/12_Iconography/Iconography.stories.tsx`

## Validation and policy
- Token validation: `pnpm validate:tokens`
- Coverage policy: `pnpm ds:matrix:check`
- Design-system governance docs:
  - `docs/design-system/collections/brand-collection-rules.md`
  - `docs/design-system/collections/alias-collection-rules.md`
  - `docs/design-system/collections/mapped-collection-rules.md`
  - `docs/design-system/collections/responsive-collection-rules.md`

## Fast retrieval commands
```bash
jq 'keys' packages/tokens/src/tokens/index.dtcg.json
jq '.type.web | keys' packages/tokens/src/tokens/index.dtcg.json
jq '.space | keys' packages/tokens/src/tokens/index.dtcg.json
jq '.radius | keys' packages/tokens/src/tokens/index.dtcg.json

rg -n "--foundation-|--ds-|--color-" packages/tokens packages/ui/src/styles
rg -n "@design-studio/ui/icons|@design-studio/astudio-icons" packages/ui/src
rg -n "Brand|Alias|Mapped" docs/design-system/CONTRACT.md docs/design-system/collections/*.md
```
