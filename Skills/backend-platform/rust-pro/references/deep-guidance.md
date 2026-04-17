# Rust Deep Guidance

Read when: Borrow checker constraints, error taxonomy, or performance-sensitive paths are involved.

## Ownership and borrowing
- Model ownership transfer intentionally.
- Minimize clone-heavy adapters in hot loops.
- Keep lifetimes local when possible.

## Error design
- Prefer typed domain errors over generic strings.
- Add context at boundaries where observability is required.
