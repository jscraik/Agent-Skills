# Deepening Playbook

Use this guide to decide whether code should be deepened, collapsed, or left alone.

## Deletion Test

Ask what happens if the module disappears and callers inline its behavior.

- If callers become clearer, the module is shallow.
- If callers become noisier and must learn many details, the module is doing useful hiding.
- If callers become coupled to storage, transport, lifecycle, or policy details, the module is likely a real boundary.

## Dependency Categories

**In-process dependency**:
Ordinary local code in the same runtime. Prefer direct use unless a deeper interface hides meaningful complexity.

**Local-substitutable dependency**:
A dependency that can be replaced locally for tests or variants. A seam may be useful when there are real alternate implementations.

**Remote but owned dependency**:
A service, queue, database, or API owned by the same organization. Ports and adapters can be useful when transport concerns would otherwise leak into domain logic.

**True external dependency**:
A vendor, partner API, or external system. Use a boundary that protects the core module from vendor vocabulary, retries, auth, and failure shapes.

## Common Smells

- "Utils" directories that force readers to assemble the concept themselves.
- Thin classes or functions that only forward arguments.
- Many tests for small helpers but few tests for the behavior users rely on.
- Public types that expose persistence tables or remote API payloads as domain concepts.
- Feature code that repeats lifecycle checks because no module owns the lifecycle.
- Multiple modules that must be edited together for one domain change.

## Testing Strategy

- Replace tests at shallow helper boundaries with tests at the deeper module interface when coverage is equivalent.
- Test observable behavior, not private implementation steps.
- Keep focused unit tests for dense algorithms hidden inside a module when they carry real complexity.
- Prefer contract tests at seams with real adapters.
- Do not add mocks around in-process helpers just to make a shallow seam look testable.

## Recommendation Shape

A deepening recommendation should identify:

- the concept that deserves ownership;
- the callers that would become simpler;
- the complexity hidden behind the proposed interface;
- the tests that move to the deeper interface;
- the risk of over-centralizing behavior;
- the validation gate that proves behavior did not change.
