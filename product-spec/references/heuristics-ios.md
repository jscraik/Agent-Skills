# iOS Heuristics and Criteria (Concise)

Use this reference for iOS-specific UX reviews (SwiftUI/UIKit apps).

## Usability Heuristics
- Follow iOS navigation patterns (tab bars, navigation stacks, sheets).
- Consistent gesture behaviors; avoid hidden gestures without cues.
- Clear feedback for taps, long operations, and success/failure states.

## Accessibility (Apple AX + WCAG 2.2 AA oriented)
- Dynamic Type support; avoid truncation at larger sizes.
- VoiceOver labels, hints, and traits on interactive elements.
- Focus order matches visual order; no inaccessible custom controls.
- Sufficient contrast and color-independent meaning.
- Respect Reduce Motion and Reduce Transparency.
- Target sizes and spacing meet touch guidelines.

## Content and Microcopy
- Use system terminology and familiar labels.
- Avoid dense text; prefer progressive disclosure.
- Make destructive actions explicit and confirm.

## Trust and Safety
- Explain permission prompts; request just-in-time.
- Show clear data handling cues for sensitive inputs.

## Performance and Resilience
- Use system loading indicators or skeletons where appropriate.
- Graceful offline and error states; preserve user input.
