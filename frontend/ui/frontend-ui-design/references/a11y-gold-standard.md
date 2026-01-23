# Accessibility Gold Standard (Dec 2025)

Last verified: 2026-01-01

Use this checklist as the minimum bar for accessibility and platform alignment.
Prefer authoritative sources (W3C + Apple) and keep the output verifiable.

## Web (WCAG 2.2 AA)
- Meet WCAG 2.2 AA success criteria for all critical flows.
- Keyboard support for all interactive elements (no traps).
- Visible focus indicators with sufficient contrast.
- Sufficient color contrast for text and interactive states.
- Form labels are persistent (no placeholder-only).
- Error messaging is perceivable and programmatic.
- Text spacing and reflow: no clipping at large text sizes and narrow widths.
- Target size: meet WCAG 2.2 target size minimums for pointer inputs.
- Dragging alternatives: provide non-drag controls where dragging is required.
- Focus appearance: meet WCAG 2.2 focus appearance guidance for visibility.

## ARIA + Patterns
- Use WAI-ARIA Authoring Practices for component behavior.
- Map roles/states/properties correctly.
- Prefer native elements; use ARIA only when needed.
- Align with the WAI-ARIA 1.2 recommendation when specifying roles/states.

## Apple (iOS/macOS)
- VoiceOver: correct labels, hints (if needed), and rotor behavior.
- Dynamic Type: scalable text without clipping.
- Reduce Motion and Reduce Transparency respected.
- Hit targets sized for touch and accessibility.
  - Use Apple’s App Store Connect evaluation criteria for VoiceOver and
    Reduced Motion when validating support.
- High Contrast / Increase Contrast respected.
- RTL layout correctness where applicable.

## Testing checklist (minimum)
- Keyboard navigation across all states.
- Screen reader (VoiceOver) for primary flows.
- Reduced Motion and Reduced Transparency.
- High contrast and color-blind safe states.
- Dynamic Type / Larger Text.
- Reflow / text spacing checks.
- Target size checks for primary controls.
