# Go Deep Guidance

Read when: You are shaping package APIs, concurrency behavior, or production error boundaries.

## API surface
- Keep package exports minimal and stable.
- Prefer constructor validation over deferred runtime failures.

## Concurrency
- Use context propagation consistently.
- Guard shared mutable state explicitly.
