# Layout Grids + Breakpoints (Web + Desktop)

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

## 2) Desktop (macOS/Windows/Linux)

### Window widths (reference)
- Compact: 960
- Regular: 1200
- Wide: 1440+

### Grid
- 12-column grid
- Gutter: 20
- Margin: 24 (compact), 32 (regular), 40 (wide)

## 3) Component scaling rules
- Primary cards must fit 728 width on web.
- Carousels should show 1 full card + peeks on small screens; 3 across on desktop.
- Fullscreen layouts align to top bars and bottom composer heights from the
  brand guide.
