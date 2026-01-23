# Form Validation

## Intent
Provide clear, immediate feedback without interrupting task flow.

## Minimal pattern
- Validate on blur or submit depending on context.
- Show errors near fields and a summary for long forms.

## Pitfalls
- Avoid blocking the user with too-early validation.

## Accessibility
- Use aria-describedby to link errors to fields.
