# Apps-in-ChatGPT Brand Components (Baseline Specs)

Last verified: 2026-01-01

Use these specs as defaults across web, SwiftUI, UIKit, and AppKit. All
measurements must reference tokens (see `token-mapping-dtcg.md`).

## 1) Buttons

### Primary (pill)
- Height: 44
- Radius: radius.round
- Background: color.text.primary (light) / color.text.primary (dark)
- Label: color.text.inverted
- Typography (Web): 15/24 Medium, tracking -0.24
- Typography (iOS): map to `body` with Medium emphasis (SwiftUI `.body.weight(.medium)`)
- Typography (Android): map to `body` with Medium emphasis (Material bodyLarge/Medium)
- Icon (optional): size.icon.20, gap space.6

### Secondary (pill)
- Height: 44
- Radius: radius.round
- Background: color.bg.tertiary
- Label: color.text.primary
- Border: none

### Small
- Height: 40
- Radius: radius.round
- Typography (Web): 14/20 Semibold, tracking -0.3
- Typography (iOS): map to `body-small` with Semibold emphasis
- Typography (Android): map to `body-small` with Semibold emphasis (Material bodyMedium/SemiBold)

### States
- Default / hover / pressed / disabled / focus must all meet contrast minimums.
- Focus: visible outline using color.border.light or accent depending on theme.

## 2) Inputs

### Text field
- Height: 44
- Radius: radius.round
- Background: color.bg.primary
- Border: 1px color.border.light
- Placeholder: color.text.tertiary (do not use placeholder-only labels)
- Label: persistent label above or inline floating label
- Helper/error: bodySmall; error uses color.icon.status.error
 - Typography (Web): body / body-small from brand guide
- Typography (iOS): map to body scales in the iOS table of the brand guide
- Typography (Android): map to body scales in the Android table of the brand guide
  - Example: `MaterialTheme.typography.bodyLarge` or `bodyMedium` with weight override

### Search field
- Height: 44
- Leading icon: size.icon.20
- Clear button: 32x32 hit area within a 44x44 target

## 3) Tabs
- Height: 44
- Radius: radius.round (for segmented)
- Background: color.bg.tertiary
- Active indicator: bottom line or filled pill; use color.text.primary for text
- Label (Web): 14/20 Semibold
- Label (iOS): map to body-small Semibold
- Label (Android): map to body-small Semibold (Material bodyMedium/SemiBold)
- Hit area: >=44x44 for each tab

## 4) Toggles
- Use platform-native toggles where possible.
- If custom:
  - Track height: 24
  - Track radius: radius.round
  - Thumb: 20, radius.round
  - On: color.icon.accent; Off: color.bg.tertiary
  - Ensure 44x44 hit target

## 5) Chips
- Height: 32 (compact) or 36 (default)
- Radius: radius.round
- Background: color.bg.tertiary
- Text (Web): 14/20 Regular or Medium
- Text (iOS): map to body-small Regular/Medium
- Text (Android): map to body-small Regular/Medium (Material bodySmall/Regular)
- Icon: size.icon.16 or size.icon.20

## 6) Icon buttons
- Hit area: 44x44 (standard), 40x40 (compact)
- Background: color.bg.tertiary
- Radius: radius.round
- Icon: size.icon.24
