# TOML Deep Guidance

Read when: You need schema-safe edits across large config files or you are debugging parser validity failures.

## TOML 1.0 validity rules (spec-backed)

- A key/value pair must stay on one line and include a concrete typed value.
- Defining the same key more than once is invalid.
- Bare and quoted forms of the same key are equivalent, so using both is also a redefinition.
- Once a path is created as a table (or array-of-tables), it cannot be redefined as the other kind.
- Dotted keys cannot later reinterpret a scalar as a table.

## Editing implications

- Before adding a key, scan for existing equivalent keys (quoted and unquoted).
- Keep object path ownership consistent: either table blocks or dotted path expansion, not conflicting mixes.
- Treat parser errors about redefinition as structure conflicts first, not syntax typos.
