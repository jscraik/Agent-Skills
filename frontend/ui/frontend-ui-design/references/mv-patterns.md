# MV Patterns (SwiftUI)

Last verified: 2026-01-04

Source notes:
- Community perspective (user-provided summary from a 2024 SwiftUI article).
- Align with Apple SwiftUI data-flow guidance (see Apple Developer videos):
  - https://developer.apple.com/videos/play/wwdc2019/226/
  - https://developer.apple.com/videos/play/wwdc2023/10149/
  - https://developer.apple.com/documentation/swiftui
  - https://developer.apple.com/documentation/swift

## Guidance
Use this when deciding whether to introduce a view model in SwiftUI.

Key points:
- Default to MV when possible: views are lightweight state expressions and orchestrate UI flow.
- Prefer `@State`, `@Environment`, `@Query`, `task`, and `onChange` for local state and side effects.
- Inject services and shared models via `@Environment`; keep business logic in services/models.
- Split large views into smaller views before adding a view model.
- Avoid manual data fetching that duplicates SwiftUI/SwiftData observation.
- Test models/services and business logic; keep views simple and declarative.

When to introduce a view model:
- Shared state spans many views and becomes hard to reason about.
- Complex orchestration or caching would clutter view code.
- Testability improves meaningfully with a dedicated observable object.
