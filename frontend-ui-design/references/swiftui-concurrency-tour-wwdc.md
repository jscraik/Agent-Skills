# SwiftUI Concurrency Tour (Summary)

Last verified: 2026-01-01

Use when SwiftUI code intersects with concurrency and Sendable rules.

## Main-actor default
- `View` is `@MainActor` isolated by default; `body` inherits isolation.
- Swift 6.2 can infer `@MainActor` for a module (opt-in setting).

## Where SwiftUI runs off-main
Some SwiftUI APIs evaluate work off the main thread; closures may need to be
`Sendable` and must not capture main-actor state unsafely.
Examples include:
- `Shape` path generation
- `Layout` methods
- `visualEffect` closures
- `onGeometryChange` closures

## Sendable guidance
- Avoid capturing `self` when a Sendable closure only needs a value snapshot.
- Prefer explicit value captures in the capture list.

## Async work in SwiftUI
- Keep UI callbacks synchronous, then bridge to async with `Task`.
- Update state in async work; UI reacts synchronously.

## Performance
- Offload expensive work from the main actor.
- Keep time-sensitive UI logic synchronous.
