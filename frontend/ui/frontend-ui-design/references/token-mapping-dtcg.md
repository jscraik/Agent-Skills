# DTCG Token Mapping (Web + Swift)

Last verified: 2026-01-01

This guide normalizes the Apps-in-ChatGPT brand tokens into DTCG-compliant
names and provides platform mapping rules for web and Swift.

## 1) Canonical token naming (DTCG)
Use nested groups (no dots in token or group names). Favor semantic names over
raw values. Dot notation is reserved for references/exports only.

Spec reference: https://www.designtokens.org/TR/2025.10/format/

### Color (nested groups)
- color/bg/primary
- color/bg/secondary
- color/bg/tertiary
- color/text/primary
- color/text/secondary
- color/text/tertiary
- color/text/inverted
- color/icon/primary
- color/icon/secondary
- color/icon/tertiary
- color/icon/accent
- color/icon/status/error
- color/icon/status/warning
- color/icon/status/success
- color/border/light
- color/border/heavy
- color/border/default (dark only)

### Radius
- radius/6
- radius/8
- radius/10
- radius/12
- radius/16
- radius/18
- radius/21
- radius/24
- radius/30
- radius/round

### Space
- space/0
- space/1
- space/2
- space/4
- space/6
- space/8
- space/12
- space/16
- space/20
- space/24
- space/32
- space/64

### Typography
- type/heading1/size
- type/heading1/lineHeight
- type/heading1/weight
- type/heading1/tracking
- type/heading2/size
- type/heading2/lineHeight
- type/heading2/weight
- type/heading2/tracking
- type/heading3/size
- type/heading3/lineHeight
- type/heading3/weight
- type/heading3/tracking
- type/body/size
- type/body/lineHeight
- type/body/weight
- type/body/tracking
- type/bodySmall/size
- type/bodySmall/lineHeight
- type/bodySmall/weight
- type/bodySmall/tracking
- type/caption/size
- type/caption/lineHeight
- type/caption/weight
- type/caption/tracking

### Component sizes
- size/control/height/44
- size/control/height/40
- size/icon/20
- size/icon/24
- size/media/44

### Motion
- motion/duration/fast
- motion/duration/base
- motion/duration/slow
- motion/easing/standard
- motion/easing/emphasized

### Naming rules (DTCG 2025.10)
- Token and group names MUST NOT start with `$`.
- Token and group names MUST NOT contain `.`, `{`, or `}`.
- Token names are case-sensitive, but avoid names that differ only by case.

## 2) Value mapping rules
- Store values in px (dimensions) and ms (durations).
- Derive rem: 1rem = 16px unless project overrides.
- Apple mapping uses pt = px unless overridden by platform scaling rules.

## 3) Theme strategy
- DTCG themes: `themes/light.json`, `themes/dark.json`
- Use aliasing rather than duplication when values are shared.
- Dark-only tokens should exist only in the dark theme unless required for
  contrast comparisons.

## 4) Web mapping
- Export CSS variables in kebab-case derived from group paths:
  - color/bg/primary -> --color-bg-primary
  - space/12 -> --space-12
  - radius/24 -> --radius-24
- Use CSS variables in React/App SDK UI components. Never hardcode raw values.

## 5) Swift mapping
- Export to Swift structs derived from the same semantic groups:
  - `Tokens.Color.Bg.primary`
  - `Tokens.Space.s12`
  - `Tokens.Radius.r24`
  - `Tokens.Type.body.size`
- Provide light/dark values via `ColorAsset` or `Color` initializers based on
  dynamic color providers.
- Keep iOS/macOS/AppKit mapping parity. Avoid platform drift.

## 6) Validation checklist
- No raw hex values in component styles.
- No magic numbers for spacing or radius.
- All tokens referenced in `packages/tokens` and mapped by the bridge.
