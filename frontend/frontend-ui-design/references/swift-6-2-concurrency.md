# Swift 6.2 Concurrency (Summary)

Last verified: 2026-01-01

Use this when reviewing or implementing concurrency in Swift 6.2+.
Prefer authoritative sources for exact compiler settings and behavior.

## Key updates
- Approachable Concurrency: async functions run on the caller's executor by
  default, reducing unintended hops.
- Default Actor Isolation can infer `@MainActor` for app targets.
- `@concurrent` explicitly offloads work to the concurrent thread pool.
- Isolated conformances allow main-actor types to conform safely.

## Practices
- UI-bound types: prefer `@MainActor`.
- Global/shared state: protect with `@MainActor` or move into an `actor`.
- Use `@concurrent` only for CPU-heavy background work.
- Avoid `@unchecked Sendable` unless you can prove safety.

## References
- Swift 6.2 release notes and concurrency overview:
  https://www.swift.org/blog/swift-6.2-released/
- Swift Forums (Approachable Concurrency discussions):
  https://forums.swift.org/c/swift-evolution/concurrency/29
