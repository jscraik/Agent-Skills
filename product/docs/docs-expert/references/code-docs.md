# In-code Documentation Guidance

## TS/JS and React (JSDoc/TSDoc)

Document public APIs (exports), non-obvious utilities, hooks, and any function or component with constraints.

Required content for public symbols:

- One-line summary starting with a verb (for example, "Creates...", "Renders...").
- `@param` for non-trivial params (include units, allowed values, defaults).
- `@returns` (or React render contract if it returns JSX).
- `@throws` for thrown errors (name plus condition).
- `@example` for anything with more than one "correct" usage.
- `@deprecated` when applicable (include migration hint).

React-specific:

- Document props contract (required/optional, default behavior, controlled/uncontrolled).
- Document accessibility contract: keyboard behavior, focus management, ARIA expectations.
- For hooks: document dependencies, side effects, and SSR constraints.

Rules:

- For public symbols, explain what the code does (behavior and contract), not just why.
- Inline comments explain why or constraints, not what the code already says.
- Do not invent; docs must match implementation and tests.

## Config files (JSON, TOML, YAML)

Goal: readers can safely edit config without guessing.

- Prefer a schema and docs:
  - JSON: `.schema.json` plus examples (JSON cannot have comments).
  - YAML or TOML: inline comments are allowed, but still link to schema or spec.
- Document:
  - Each key's meaning, type, defaults, allowed values
  - Security-sensitive keys (tokens, paths, network endpoints)
  - Migration notes when keys change
- Provide at least one minimal example and one full example.

Validation rule:

- Config docs must reference the validating mechanism (Zod schema, JSON Schema, or typed config loader).
