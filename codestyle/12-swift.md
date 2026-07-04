# Swift Standards

## Table of Contents
- [Scope](#scope)
- [Language and API design](#language-and-api-design)
- [Concurrency](#concurrency)
- [Error handling and state](#error-handling-and-state)
- [Testing and formatting](#testing-and-formatting)
- [Enforcement](#enforcement)

## Scope
- This module defines Swift coding standards for Apple-platform projects and utilities.

## Language and API design
- Implementations SHOULD prefer value semantics and protocol-oriented composition for shared logic.
- API surfaces MUST remain explicit and readable at call sites.
- Hidden global state in core logic MUST be avoided.

## Concurrency
- Implementations SHOULD prefer structured concurrency (`async/await`, task groups) over unmanaged thread patterns.
- Mutable shared state MUST use actor, `MainActor`, or explicit synchronization boundaries.
- UI-affecting updates MUST stay on the appropriate main-thread or actor context.
- Swift 6-era projects SHOULD enable strict concurrency checking where the project can support it; exceptions around `Sendable`, actor isolation, or unchecked concurrency MUST be justified with waiver metadata.
- Escaping closures that can run concurrently SHOULD be `@Sendable` and MUST NOT capture mutable non-isolated state without an actor or synchronization boundary.

## Error handling and state
- Typed errors MUST be propagated with actionable context.
- Async flows MUST NOT swallow errors.
- State transitions MUST remain explicit and testable.

## Testing and formatting
- Unit tests MUST remain deterministic and focused on behavior contracts.
- Heavier integration/UI tests SHOULD be separated from fast unit suites.
- New Swift package code SHOULD prefer Swift Testing (`@Test`, `#expect`) when the project has adopted it; XCTest remains acceptable for existing XCTest suites and Apple-platform integration tests.
- Repo formatting/lint tooling MUST be applied consistently for Swift codepaths.

## Enforcement
- Swift changes MUST pass repository baseline gates:
  - `pnpm lint`
  - `pnpm typecheck`
  - `pnpm test`
  - `pnpm audit`
  - `pnpm check`
  - `bash scripts/validate-codestyle.sh`
  - `bash scripts/verify-work.sh --fast`
- Swift projects SHOULD also run native gates where available:
  - `swift test`
  - `xcodebuild test` (or project-defined equivalent)
- Swift projects with strict concurrency enabled SHOULD include that compiler mode in CI or document why it remains advisory.
- Concurrency and actor-boundary exceptions require explicit waiver metadata with rule ID or section, reason, tracking ticket, and expiry or ADR reference.
