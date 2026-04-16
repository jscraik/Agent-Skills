# TypeScript Deep Guidance

Read when: You are handling complex type modeling, shared API contracts, or difficult narrowing issues.

## Contract modeling
- Prefer discriminated unions for state machines.
- Keep domain types separate from transport types.
- Validate external input at boundaries before casting.

## Error-prone patterns
- Avoid `as unknown as` in production code.
- Avoid `any` except as a temporary migration step with explicit TODO ownership.
- Avoid broad utility types that erase important constraints.
