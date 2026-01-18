# Component QA Recipes

Last verified: 2026-01-01

Use these checks when validating components.

## Button
- States: default/hover/pressed/disabled/focus
- Keyboard: Enter/Space activates; focus-visible ring
- A11y: aria-label if no text; contrast meets minimums

## Input
- Label: persistent label present
- Error: programmatic + visible message
- Keyboard: tab order correct; escape clears (search)
- A11y: role, name, and description set

## Modal/Sheet
- Focus trap, initial focus, and restore focus on close
- Escape closes unless destructive flow
- Screen reader: dialog role with label

## List/Row
- Row click target >=44x44
- Divider contrast + spacing consistent
- Text truncation does not hide critical info

## Carousel
- Keyboard navigation (left/right) and focusable controls
- Visible pagination/position indicator
- Reduced motion alternative

## Tabs
- Arrow-key navigation and roving tabindex
- Selected state announced
- Focus-visible ring on active tab
