# Data Grid Virtualization

## Intent
Render large datasets with stable performance while preserving usability.

## Minimal pattern
- Use row virtualization with fixed row height when possible.
- Virtualize rows and columns separately for very wide grids.
- Keep column headers and selection controls sticky.

## Pitfalls
- Avoid dynamic row heights without a measurement strategy.
- Avoid virtualized grids without a fallback for screen readers.

## Accessibility
- Provide keyboard navigation across rows/columns.
- Offer a non-virtualized export/view mode for screen readers when required.
