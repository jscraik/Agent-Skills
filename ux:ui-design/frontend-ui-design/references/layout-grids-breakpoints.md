# Layout Grids + Breakpoints (Web, iOS, macOS)

Last verified: 2026-01-01

Use these grids as defaults for the Apps-in-ChatGPT brand unless the product
requires a different system. Always validate against platform constraints.

## 1) Web (ChatGPT widget + standalone React)

### Container widths
- Inline conversation column: 768 (content width)
- Inline working width: 728 (20px inset each side)

### Breakpoints
- xs: 0-479
- sm: 480-767
- md: 768-1023
- lg: 1024-1439
- xl: 1440+

### Grid
- 12-column grid for md+; 4-column grid for xs-sm
- Gutter: 16 (md+), 12 (sm), 8 (xs)
- Margin: 20 (md+), 16 (sm), 12 (xs)

## 2) iOS (SwiftUI/UIKit)

### Device widths (reference)
- iPhone 14/15: 390-393
- iPhone Plus/Max: 428-430
- iPad portrait: 768

### Insets
- Default horizontal inset: 20 (phone), 24 (iPad)
- Safe area insets always respected

### Grid
- 4-column grid on phone
- 8-column grid on iPad
- Gutter: 12 (phone), 16 (iPad)

## 3) macOS (AppKit/SwiftUI)

### Window widths (reference)
- Compact: 960
- Regular: 1200
- Wide: 1440+

### Grid
- 12-column grid
- Gutter: 20
- Margin: 24 (compact), 32 (regular), 40 (wide)

## 4) Component scaling rules
- Primary cards must fit 353 width on iOS and 728 width on web.
- Carousels should show 1 full card + peeks on mobile; 3 across on desktop.
- Fullscreen layouts align to top bars and bottom composer heights from the
  brand guide.
