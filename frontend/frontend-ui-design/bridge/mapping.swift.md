# Swift mapping (SwiftUI + UIKit + AppKit)

## Generated API shape (recommended)
- `enum TokenColor { case textPrimary, surfaceDefault, ... }`
- `struct Tokens { static func color(_:) -> Color; static func uiColor(_:) -> UIColor; ... }`
- `struct Spacing { static let s0: CGFloat ... }`
- `struct Radius { ... }`
- `struct Motion { static let short: Double ... }`

## Theme application
- SwiftUI: Environment theme + dynamic type scaling
- UIKit/AppKit: shared token access layer, no hard-coded values in components

## Accessibility requirements
- Ensure Dynamic Type support (system text styles preferred)
- Provide reduce-motion gating for animations
- macOS: keyboard focus order and shortcuts must be explicit in FEATURE_DESIGN
