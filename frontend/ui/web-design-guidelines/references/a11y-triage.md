# Accessibility Triage (Fast Pass)

Goal: identify critical blockers quickly. This is additive; always run the full guideline pass afterward.

## Priority 1: accessible names
- Every interactive control must have an accessible name.
- Icon-only buttons must have `aria-label` or `aria-labelledby`.
- Inputs/selects/textareas must be labeled.
- Decorative icons should be `aria-hidden`.

## Priority 2: keyboard access
- No div/span as buttons without full keyboard support.
- All interactive elements are reachable via Tab.
- Focus is visible for keyboard users.
- Do not use `tabindex` greater than 0.

## Priority 3: focus + dialogs
- Modals trap focus and restore focus on close.
- Set initial focus inside dialogs.
- Escape closes dialogs/overlays when applicable.
