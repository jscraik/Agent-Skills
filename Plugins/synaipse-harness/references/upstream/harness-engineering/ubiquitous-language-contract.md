# Ubiquitous Language Contract

Read when: a Harness Engineering stage resolves project terminology, runs a
domain interview, detects glossary drift, updates ubiquitous language files, or
decides whether a domain boundary needs an ADR.

## Core Rule

`UBIQUITOUS_LANGUAGE.md` is the canonical glossary and nothing else. It records project-specific
language so later specs, plans, code, reviews, and tracker updates use the same
terms. It must not become a specification, scratch pad, implementation decision
log, schema note, API contract, or task list.

## File Selection

- If `UBIQUITOUS-MAP.md` exists, read it and update the context-specific
  ubiquitous language file for the current topic.
- If a root `UBIQUITOUS_LANGUAGE.md` exists, treat the repo as single-context
  unless the topic clearly spans multiple bounded contexts.
- If only `UBIQUITOUS.md` exists, treat it as a compatibility alias for
  `UBIQUITOUS_LANGUAGE.md`.
- If neither exists, create a root `UBIQUITOUS_LANGUAGE.md` lazily only after the
  first project-specific term is resolved.
- Read legacy `CONTEXT.md` or `CONTEXT-MAP.md` as compatibility evidence, but do
  not create new legacy context files.

## Interview Loop

In `he-brainstorm` `domain_interview` mode:

1. Inspect the repo before asking: existing ubiquitous language files, legacy
   context files, `.harness/decisions/**`, specs, plans, tests, and code names.
2. Challenge glossary conflicts immediately. If a file defines one meaning and
   the user appears to mean another, ask which meaning should survive.
3. Sharpen fuzzy or overloaded terms by proposing one canonical term and avoided
   aliases.
4. Stress-test relationships with concrete scenarios before recording a term
   boundary.
5. Use `request_user_input` when available for bounded branch decisions. Ask one
   question at a time, put the recommended answer first, and wait for feedback
   before continuing.
6. Update the owning ubiquitous language file immediately after a term is
   resolved.

## Format

Single-context files use:

```md
# {Context Name}

{One or two sentence description of what this context is and why it exists.}

## Language

**Order**:
{A one or two sentence description of the term}
_Avoid_: Purchase, transaction
```

Include only project-context terms. Keep definitions to one or two sentences.
List avoided aliases. Show relationships and cardinality where obvious. Add
`## Flagged Ambiguities` when a conflict was resolved or intentionally left
open. Add a short `## Example Dialogue` that demonstrates how the terms interact
when the file has enough resolved language to make the dialogue useful.

Multi-context repos use a root `UBIQUITOUS-MAP.md` with context links and
relationships between contexts.

## ADR Boundary

Glossary choices belong in `UBIQUITOUS_LANGUAGE.md` or its compatibility alias
`UBIQUITOUS.md`. Durable architectural or domain
boundary decisions belong under `.harness/decisions/ADR-###-<slug>.md` only when
all three ADR criteria are true:

- hard to reverse;
- surprising without context;
- the result of a real trade-off.

Skip ADR creation when any criterion is missing. If an ADR is warranted, route
or hand off to `he-strategy` `decision-compression` unless the current artifact
explicitly authorizes ADR creation.
