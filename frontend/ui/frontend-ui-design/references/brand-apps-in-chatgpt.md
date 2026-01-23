# Brand Design Guide -- "Apps-in-ChatGPT" Style (Replication Spec)

Last verified: 2026-01-04

This guide consolidates the visual system and component rules observed across
Figma nodes (Foundations + Inline Cards + Inline Carousel + Full Screen + PiP)
into a single, implementation-ready style guide.

Source of truth PDFs (prefer these if any values conflict here):
- `/Users/jamiecraik/chatui/docs/foundations/chatgpt-apps/Apps in ChatGPT • Colours.pdf`
- `/Users/jamiecraik/chatui/docs/foundations/chatgpt-apps/Apps in ChatGPT • Typeography.pdf`
- `/Users/jamiecraik/chatui/docs/foundations/chatgpt-apps/Apps in ChatGPT • spacing.pdf`
- `/Users/jamiecraik/chatui/docs/foundations/chatgpt-apps/Apps in ChatGPT • Iconography.pdf`

## 1) Brand DNA

### Design intent
- Content-first, neutral, "quiet" UI.
- Soft separation (very light borders), restrained elevation (subtle shadows).
- Rounded geometry everywhere (cards, pills, media).
- Dense clarity: modest typography sizes with tight tracking and consistent
  line-heights.

### Core look
- Surfaces are flat + bordered, with occasional elevation for emphasis.
- Interactive controls default to pill geometry and 44px minimum height.

## 2) Foundations

### 2.1 Color tokens

#### Light theme
| Token | Value | Usage |
| --- | ---: | --- |
| --bg/primary | #FFFFFF | primary surfaces, app canvas |
| --bg/secondary | #E8E8E8 | secondary surfaces |
| --bg/tertiary | #F3F3F3 | tertiary surfaces, secondary buttons, icon-chip backgrounds |
| --text/primary | #0D0D0D | primary text |
| --text/secondary | #5D5D5D | secondary text |
| --text/tertiary | #8F8F8F | tertiary/placeholder text |
| --text/inverted | #FFFFFF | text on inverted surfaces |
| --icon/primary | #0D0D0D | primary icons |
| --icon/secondary | #5D5D5D | secondary icons |
| --icon/tertiary | #8F8F8F | tertiary icons |
| --icon/inverted | #FFFFFF | icons on inverted surfaces |
| --icon/accent | #0285FF | accent/brand action |
| --icon/status/error | #E02E2A | error |
| --icon/status/warning | #E25507 | warning |
| --icon/status/success | #008635 | success |

#### Dark theme
| Token | Value | Usage |
| --- | ---: | --- |
| --bg/primary | #212121 | primary dark canvas/surfaces |
| --bg/secondary | #303030 | secondary surface |
| --bg/tertiary | #414141 | tertiary surface |
| --text/primary | #FFFFFF | primary text |
| --text/secondary | #CDCDCD | secondary text |
| --text/tertiary | #AFAFAF | tertiary text |
| --text/inverted | #0D0D0D | text on inverted surfaces |
| --icon/primary | #FFFFFF | primary icons |
| --icon/secondary | #CDCDCD | secondary icons |
| --icon/tertiary | #AFAFAF | tertiary icons |
| --icon/inverted | #0D0D0D | icons on inverted surfaces |
| --icon/accent | #0285FF | accent/brand action |
| --icon/status/error | #FF8583 | error |
| --icon/status/warning | #FF9E6C | warning |
| --icon/status/success | #40C977 | success |

### 2.2 Border tokens
| Token | Value | Notes |
| --- | ---: | --- |
| --border/light (light) | rgba(13,13,13,0.05) | dividers, light outlines |
| --border/heavy (light) | rgba(13,13,13,0.15) | card outline (0.5px) |
| --border/default (dark) | rgba(255,255,255,0.15) | dark outlines |
| --border/light (dark) | rgba(255,255,255,0.05) | subtle dividers |

#### Stroke widths
- Cards: 0.5px with --border/heavy
- General outlines/dividers: 1px with --border/light

### 2.3 Elevation (shadows)
Use sparingly; the system is intentionally low-elevation.

| Use | Shadow |
| --- | --- |
| Card / Primary containers | 0 4px 16px rgba(0,0,0,0.05) |
| PiP frame | 0 4px 16px rgba(0,0,0,0.05) |
| Floating pill (inside PiP) | 0 10px 22px rgba(0,0,0,0.04) |
| Floating close button | 0 4px 8px rgba(0,0,0,0.16) |

### 2.4 Radius system (observed values)
Use rounded corners consistently; avoid sharp edges.

| Token idea | Value | Typical usage |
| --- | ---: | --- |
| radius-6 | 6px | small inner previews |
| radius-8 | 8px | generic frames/containers |
| radius-10 | 10px | list images |
| radius-12 | 12px | swatches, small panels |
| radius-16 | 16px | media tiles, carousel image |
| radius-18 | 18px | PiP frame |
| radius-21 | 21px | floating pill |
| radius-24 | 24px | cards + entity cards |
| radius-30 | 30px | floating round buttons |
| round | 999px | pills, chips, buttons |

### 2.5 Spacing scale (tokens)
| Token | px |
| --- | ---: |
| space-0 | 0 |
| space-1 | 2 |
| space-2 | 4 |
| space-4 | 8 |
| space-6 | 12 |
| space-8 | 16 |
| space-12 | 24 |
| space-16 | 32 |
| space-20 | 40 |
| space-24 | 48 |
| space-32 | 64 |
| space-64 | 128 |

Pattern: layouts cluster around 8 / 12 / 16 / 24 / 32.

### 2.6 Typography

#### Font families
- Primary: SF Pro (Regular 400, Medium 500, Semibold 600)
- Monospace: SF Mono Medium (for hex values, technical labels)

#### Text styles (Web set)
| Style | Size / Line | Weight | Tracking |
| --- | ---: | ---: | ---: |
| heading1 | 36 / 40 | 600 | -0.1 |
| heading2 | 24 / 28 | 600 | -0.25 |
| heading3 | 18 / 26 | 600 | -0.45 |
| body | 16 / 26 | 400 (emphasis 600) | -0.4 |
| body-small | 14 / 18 | 400 (emphasis 600) | -0.3 |
| caption | 12 / 16 | 400 (emphasis 600) | -0.1 |

#### Component-specific typography (key rules)
- Card header title: 17 / 23, Medium, tracking -0.43
- List item title: 17 / 24, Regular, tracking -0.4
- List item subtitle: 14 / 20, Regular, tracking -0.18
- Button label (common): 15 / 24, Medium, tracking -0.24
- Button label (small): 14 / 20, Semibold, tracking -0.3

#### Text styles (Android set)
| Style | Size / Line | Weight | Tracking |
| --- | ---: | ---: | ---: |
| heading1 | 32 / 40 | 600 | -0.1 |
| heading2 | 24 / 28 | 600 | -0.25 |
| heading3 | 16 / 26 | 600 | 0 |
| body | 16 / 26 | 400 (emphasis 600) | 0 |
| body-small | 14 / 18 | 400 (emphasis 600) | 0 |
| caption | 12 / 16 | 400 (emphasis 600) | 0 |

## 3) Core Components

### 3.1 Primary Card
Purpose: main "app content" container in inline responses.

Spec:
- Width: 361px (web examples)
- Background: --bg/primary
- Border: 0.5px --border/heavy
- Radius: 24px
- Shadow: 0 4px 16px rgba(0,0,0,0.05)
- Overflow: clip (rounded media + internal rows)

Card header:
- Height: 56px
- Padding: left 16, right 8
- Title: 17/23 Medium
- Right action: 44x44 hit-area, icon 20px

Card footer (CTA):
- Outer padding: 16
- Button: 44px height, pill radius (999px)
- Primary: bg #0D0D0D, label white
- Secondary: bg --bg/tertiary, label --text/primary

### 3.2 List Rows (inside cards)
Row:
- Padding: 16px horizontal, 12px vertical
- Gap: 12px vertical internal grouping
- Divider: bottom border --border/light (when used)

Left media:
- Image: 44x44, radius 10px

Text:
- Title: 17/24 Regular
- Subtitle: 14/20 Regular, --text/secondary

Right action:
- Icon button chip: 44x44, bg --bg/tertiary, pill radius, icon 24px

### 3.3 Entity Card (Simple)
Purpose: hero tile entity (product, location) with image-first style.

Spec:
- Size: 345x345
- Background: --bg/primary
- Border: 0.5px --border/heavy
- Radius: 24px
- Shadow: 0 4px 16px rgba(0,0,0,0.05)
- Image: full-bleed
- Overlay gradient (bottom legibility):
  - linear-gradient(179.9deg, rgba(255,255,255,0) 21.7%, rgba(13,13,13,0.5) 99.9%)

Footer:
- Padding: 20
- Title: 17/23 Medium, white
- Subtitle: 14/20 Regular, white at ~70% opacity
- Action: 40px pill inside 44px hit-area; bg #EFEFF0

### 3.4 Carousel Card
Purpose: compact item tile in horizontal scrollers.

Spec:
- Image: 260x260, radius 16px, border --border/light
- Content block spacing: gap 16
- Body copy: 14/20, --text/secondary, clamped (~2 lines)

CTA:
- Button: 44px height, pill
- Label: 14/20 Semibold (white) or 15/24 Medium depending on context

### 3.5 PiP Frame
Purpose: picture-in-picture interactive surface inside the conversation.

Spec:
- Size: 768x420
- Border: 1px --border/light
- Radius: 18px
- Shadow: 0 4px 16px rgba(0,0,0,0.05)

Close control:
- Floating, overlaps container (negative offset)
- Size: 32x32
- Background: #0D0D0D, icon white
- Radius: 30px
- Shadow: 0 4px 8px rgba(0,0,0,0.16)

Floating pill CTA:
- Background: white
- Border: rgba(0,0,0,0.08)
- Radius: 21px
- Shadow: 0 10px 22px rgba(0,0,0,0.04)
- Padding: 16x6
- Label: 17/22 Semibold, blue-tinted text (observed #2979C4)

## 4) Layout Patterns

### 4.1 Conversation Inline Card (desktop)
Observed structure (key constraints):
- Chat content column: 768px
- Typical inset inside column: 20px, yielding 728px working width for app blocks
- App attribution row: 38px tall
- Gap between attribution and card: ~4px
- Vertical rhythm between user message and response: ~24px

Rule: design app content to fit gracefully in 728px width without horizontal scroll.

### 4.3 Inline Carousel
- Small-screen carousel row consumes the full working width and sets a fixed row height
  (~330-447 depending on whether model response/actions are visible below).
- Desktop carousel commonly shows 3 tiles across in a 728px region, with explicit
  next/prev button (40x40) when needed.

Rule: carousel cards must read as complete units (image + title + 1-2 lines + CTA).

### 4.4 Full Screen Modal
Observed composition emphasizes:
- Fixed top bar: 52px
- Left list column: 360px
- Primary canvas (e.g., map): ~1020px
- Optional inspector panel: 356px (overlay/right)
- Bottom composer/footer: 88px when present

Rule: full-screen mode uses the same token system; do not introduce new
surfaces or heavy shadows.

## 5) Iconography Rules
- Base icon size: 24x24
- Common hit targets:
  - 44x44 (standard)
  - 40x40 (secondary/compact)
- Default icon color uses semantic tokens:
  - Light: --icon/primary / secondary / tertiary
  - Dark: --text/primary-equivalent whites/greys
- Icons are monochrome; avoid multi-color icons except status and illustrative media.

Official icon set and categories:
- `iconography-apps-in-chatgpt.md`

## 6) Copy & Content Style
- Titles: short, noun-first ("Pepperoni", "Header title")
- CTAs: concise verbs ("Order", "Place order", "View all ...")
- Descriptions: 1-2 lines max in compact surfaces (carousel body is clamped)
- Numbers/time: shown as secondary text (14px, --text/secondary)

## 7) Accessibility & Interaction Requirements (implied by the system)
- Minimum target size: 44x44 for interactive controls.
- Preserve text contrast by theme:
  - Light: #0D0D0D on white; secondary #5D5D5D
  - Dark: white/greys on #212121-#414141
- Media overlays (entity cards) must use gradient darkening to keep white text readable.

## 8) Implementation Starter (tokens)
Note: these CSS variables mirror the legacy token naming used in the spec for
readability. For implementation, map to DTCG tokens and export to kebab-case
CSS vars as defined in `token-mapping-dtcg.md`.

```css
:root {
  /* Light */
  --bg/primary: #ffffff;
  --bg/secondary: #e8e8e8;
  --bg/tertiary: #f3f3f3;

  --text/primary: #0d0d0d;
  --text/secondary: #5d5d5d;
  --text/tertiary: #8f8f8f;
  --text/inverted: #ffffff;

  --icon/primary: #0d0d0d;
  --icon/secondary: #5d5d5d;
  --icon/tertiary: #8f8f8f;
  --icon/inverted: #ffffff;
  --icon/accent: #0285ff;
  --icon/status/error: #e02e2a;
  --icon/status/warning: #e25507;
  --icon/status/success: #008635;

  --border/light: rgba(13,13,13,0.05);
  --border/heavy: rgba(13,13,13,0.15);

  --space-0: 0px;
  --space-1: 2px;
  --space-2: 4px;
  --space-4: 8px;
  --space-6: 12px;
  --space-8: 16px;
  --space-12: 24px;
  --space-16: 32px;
  --space-20: 40px;
  --space-24: 48px;
  --space-32: 64px;
  --space-64: 128px;

  --round: 999px;
}

[data-theme="dark"] {
  --bg/primary: #212121;
  --bg/secondary: #303030;
  --bg/tertiary: #414141;

  --text/primary: #ffffff;
  --text/secondary: #cdcdcd;
  --text/tertiary: #afafaf;
  --text/inverted: #0d0d0d;

  --icon/primary: #ffffff;
  --icon/secondary: #cdcdcd;
  --icon/tertiary: #afafaf;
  --icon/inverted: #0d0d0d;
  --icon/accent: #0285ff;
  --icon/status/error: #ff8583;
  --icon/status/warning: #ff9e6c;
  --icon/status/success: #40c977;

  --border/default: rgba(255,255,255,0.15);
  --border/light: rgba(255,255,255,0.05);
}
```
