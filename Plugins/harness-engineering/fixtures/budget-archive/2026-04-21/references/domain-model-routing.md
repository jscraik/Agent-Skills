# Domain Model Routing

Read when: a Harness Engineering request mentions project terminology, ubiquitous language, `CONTEXT.md`, `CONTEXT-MAP.md`, glossary, naming conflicts, domain-model drift, or a Linear issue whose wording changes product meaning.

Harness Engineering treats domain language as part of the delivery contract. Resolve project-specific terms before downstream stages harden behavior, but keep the active `SKILL.md` files as concise maps and use this reference for the deeper workflow.

## Routing

- Use `he-brainstorm` when language is still fuzzy, several words may name the same concept, or the team needs one focused question at a time before picking direction.
- Use `he-spec` when the work needs its first implementation-grade behavior contract and domain terms shape acceptance criteria.
- Use `he-deepen-spec` when an existing spec, code path, or Linear issue disagrees with `CONTEXT.md`, or when two concepts overlap and need scenario testing before planning.
- Use `he-plan` only after canonical terms, relationships, and required context updates are stable enough for task decomposition.
- Use `he-work` when approved execution uncovers domain drift; stop and update the governing artifact or linked Linear issue before coding past the drift.
- Use `he-fix-bugs` when tracker wording may be using the wrong project term; reproduce only after confirming the issue meaning matches the domain model.
- Use `he-code-review` or `he-technical-review` when a diff, PR, spec, or plan introduces new terms, renamed concepts, or code/document mismatches.

## Context Files

Single-context repos should use one root `CONTEXT.md`. Multi-context repos should use a root `CONTEXT-MAP.md` that points to each context-specific `CONTEXT.md`.

When a relevant context file exists:

- prefer its canonical term names in specs, plans, code review findings, and Linear comments;
- list avoided aliases when they explain user or issue wording;
- flag conflicts explicitly instead of smoothing them over;
- update or request an update to the relevant context file when a term, relationship, or boundary is resolved.

When no context file exists, create or request a root `CONTEXT.md` lazily only after the first project-specific term is resolved. Do not add general programming concepts just because the code uses them.

## Linear Decision Capture

These projects use Linear issue comments for durable domain decisions, not ADRs. Capture a Linear note when all of these are true:

- the decision changes product meaning or a cross-context boundary;
- a future implementer would otherwise wonder why a term, alias, or relationship was chosen;
- there were genuine alternatives or ambiguous issue wording.

Keep the note short: state the canonical term, avoided aliases, the boundary scenario that settled it, and the affected context file or artifact.

## Output Shape

When domain modeling matters, include:

- canonical terms and avoided aliases;
- relationships with cardinality where obvious;
- one scenario or dialogue that tests the boundary between related concepts;
- unresolved ambiguities and the stage that should resolve them;
- whether `CONTEXT.md`, `CONTEXT-MAP.md`, or a Linear issue comment needs updating.
