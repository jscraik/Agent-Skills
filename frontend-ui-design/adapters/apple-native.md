# Adapter: Apple-native (SwiftUI / UIKit / AppKit)

## A) Platform conventions
- SwiftUI is preferred for new work; UIKit/AppKit for deep platform integration or legacy surfaces.
- Respect each platform's navigation idioms:
  - iOS: NavigationStack, sheets, grouped lists, bottom sheets where appropriate
  - macOS: sidebar + toolbar patterns, window resizing, keyboard shortcuts

## B) Token binding rules
- Do not hardcode "magic numbers" for spacing/typography/color.
- Bind to token-backed values via a Theme layer:
  - SwiftUI: Environment-driven theme (Color/Font/Spacing)
  - UIKit: UIColor/UIFont/metrics wrappers
  - AppKit: NSColor/NSFont wrappers

## C) Accessibility (Apple AX)
- Prefer system text styles to support Dynamic Type.
- Expose meaningful accessibility labels/hints only when needed.
- Ensure predictable focus order for keyboard users on macOS.
- Reduce motion:
  - SwiftUI: gate animations with Environment reduce motion flags
  - UIKit/AppKit: gate animations using platform accessibility settings

## D) Performance and feedback
- Ensure <=100ms feedback on taps/clicks:
  - pressed state immediately
  - optimistic UI where safe
  - show progress affordance for operations >250ms

## E) Neuroinclusive defaults
- Chunked layouts, progressive disclosure, persistent labels.
- Optional density modes implemented via spacing/type tokens.

## F) Implementation snippet requirements (when asked to implement)
When producing Swift code:
- Provide SwiftUI component + configuration
- Provide UIKit/AppKit variant if in scope
- Include previews (SwiftUI) and basic unit tests stubs if requested
