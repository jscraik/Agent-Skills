# JavaScript Deep Guidance

Read when: You are debugging async behavior, event loop ordering, or cross-runtime compatibility.

## Async behavior
- Keep async workflows explicit with awaited branches.
- Use `Promise.allSettled` when partial failure is acceptable.
- Surface upstream context on thrown errors.

## Runtime compatibility
- Confirm API availability by runtime (Node, browser, edge).
- Avoid environment-specific globals unless guarded.
