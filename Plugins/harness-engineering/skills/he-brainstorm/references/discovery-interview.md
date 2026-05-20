# Discovery Interview

Load full doctrine when needed:
`Infrastructure/references/harness-engineering/he-brainstorm-doctrine.md`.

Ask one question at a time. Prefer a blocking question tool when choices are
bounded; include free text when possible. Use prose when options would bias the
answer or choices would be padded.

For `domain_interview` mode, interview relentlessly but sequentially: walk the
design tree one unresolved branch at a time, state the recommended answer first,
and wait for feedback before moving to the next branch. Use `request_user_input`
when available for bounded branch decisions, with one short question and two or
three mutually exclusive choices. Ask in prose only when fixed choices would
distort the domain answer.

Before asking, explore what the repository can answer: inspect
`UBIQUITOUS-MAP.md`, relevant `UBIQUITOUS.md` files, legacy `CONTEXT.md`
files, `.harness/decisions/**`, specs, plans, tests, and code names. Do not ask
the user for file paths, existing glossary facts, or behavior the codebase can
settle safely.

When a term is resolved, update the owning ubiquitous language file immediately.
Keep that file as a glossary only: canonical term, tight definition, avoided
aliases, relationships where obvious, flagged ambiguities, and example dialogue.
Do not add implementation details, specifications, API contracts, schemas,
technical decisions, scratch notes, or unresolved guesses.

Useful openers: desired change, ruled-out ideas, most important constraint,
needed approvers, and what would make the work not worth doing.

If the subject is missing, ask what domain, product, problem, or opportunity to
explore. Do not invent one unless the user asks to be surprised.

When the user points at an artifact, inspect it before stating what exists;
otherwise label assumptions and keep them out of requirements until confirmed.
