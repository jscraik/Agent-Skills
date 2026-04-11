# YAML Deep Guidance

Read when: YAML scalar coercion, indentation sensitivity, or cross-tool schema compatibility is risky.

## YAML 1.2 safety rules (spec-backed)

- Indentation (spaces) defines structure; inconsistent indentation changes document meaning.
- Plain scalars have context-sensitive character constraints (especially `:`, `#`, flow indicators).
- For JSON-compatible schema behavior, canonical booleans are `true` and `false`; canonical null is `null` (or empty in some contexts).
- Values such as `True`, `Null`, `on`, `off`, or unquoted date-like strings can resolve differently across parsers and schema modes.

## Editing implications

- Quote ambiguous scalars when interoperability matters.
- Prefer block style for complex mappings/lists to reduce parse ambiguity.
- Avoid mixed flow/block style in the same logical section unless the host tool requires it.
