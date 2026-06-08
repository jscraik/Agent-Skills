# Domain Model Routing

Read when: a Harness Engineering request mentions project terminology,
ubiquitous language, `UBIQUITOUS.md`, `UBIQUITOUS-MAP.md`, legacy
`CONTEXT.md`, glossary, naming conflicts, domain-model drift, production-grade
behavior, or a Linear issue whose wording changes product meaning.

Harness Engineering treats domain language as part of the delivery contract. Resolve project-specific terms before downstream stages harden behavior, but keep the active `SKILL.md` files as concise maps and use this reference for the deeper workflow. Use `domain-model-production-contract.md` when product behavior, workflow state, integration, persistence, or closure confidence depends on the model.

## Routing

- Use `he-brainstorm` when language is still fuzzy, several words may name the same concept, or the team needs one focused question at a time before picking direction. Use `domain_interview` mode when the user asks to be interviewed through the design tree or to update ubiquitous language inline.
- Use `he-spec` when the work needs its first implementation-grade behavior contract and domain terms shape acceptance criteria.
- Use folded `he-deepen-spec` mode through `he-spec` when an existing spec, code path, or Linear issue disagrees with `UBIQUITOUS.md`, or when two concepts overlap and need scenario testing before planning.
- Use `he-plan` only after canonical terms, relationships, and required context updates are stable enough for task decomposition.
- Use `he-work` when approved execution uncovers domain drift; stop and update the governing artifact or linked Linear issue before coding past the drift.
- Use `he-fix-bugs` when tracker wording may be using the wrong project term; reproduce only after confirming the issue meaning matches the domain model.
- Use `he-code-review` or folded `he-technical-review` mode when a diff, PR, spec, or plan introduces new terms, renamed concepts, or code/document mismatches.

## Ubiquitous Language Files

Single-context repos use one root `UBIQUITOUS.md`. Multi-context repos use a
root `UBIQUITOUS-MAP.md` that points to each context-specific ubiquitous
language file. Legacy `CONTEXT.md` or `CONTEXT-MAP.md` files are read as
compatibility evidence only; do not create new legacy context files.

When a relevant context file exists:

- prefer its canonical term names in specs, plans, code review findings, and Linear comments;
- list avoided aliases when they explain user or issue wording;
- flag conflicts explicitly instead of smoothing them over;
- update or request an update to the relevant context file when a term, relationship, or boundary is resolved.

When no ubiquitous language file exists, create or request a root
`UBIQUITOUS.md` lazily only after the first project-specific term is resolved.
Do not add general programming concepts just because the code uses them.

## Decision Capture

Use `.harness/decisions/ADR-###-<slug>.md` for durable architectural or domain
boundary decisions when all ADR criteria are met. Scan existing ADR numbers
first. Keep ADRs sparse: one short title and one to three context/decision/why
sentences by default, with optional status, considered options, and consequences
only when they add value.

Offer or route to an ADR only when all three are true:

- hard to reverse;
- surprising without context;
- the result of a real trade-off.

Skip the ADR when any criterion is missing. Capture only the glossary term in
the owning ubiquitous-language artifact when the decision is vocabulary-only.

For tracked work, a Linear issue comment may summarize the same settled domain
decision when live tracker readers need it. Capture the note when all of these
are true:

- the decision changes product meaning or a cross-context boundary;
- a future implementer would otherwise wonder why a term, alias, or relationship was chosen;
- there were genuine alternatives or ambiguous issue wording.

Keep the note short: state the canonical term, avoided aliases, the boundary
scenario that settled it, and the affected ubiquitous language file or artifact.

## Output Shape

When domain modeling matters, include:

- canonical terms and avoided aliases;
- relationships with cardinality where obvious;
- one scenario or dialogue that tests the boundary between related concepts;
- unresolved ambiguities and the stage that should resolve them;
- whether `UBIQUITOUS.md`, `UBIQUITOUS-MAP.md`,
  `.harness/decisions/**`, or a Linear issue comment needs updating.
