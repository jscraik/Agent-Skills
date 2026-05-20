---
name: ubiquitous-language
description: Build shared project vocabulary, glossary terms, aliases, prompt translations, and agent instruction links when wording is fuzzy or overloaded.
metadata:
  skill-type: team_automation
---

# Ubiquitous Language

Create or update a project vocabulary so users, domain experts, and agents mean the same thing without forcing the user to know specialist terms.

## Philosophy

Make the user's natural language more powerful instead of making the user sound more technical.

## When To Use

- User mentions glossary, naming, vocabulary, terminology, DDD, domain model, or shared language.
- User says they do not know the technical term.
- A repo has overloaded phrases that agents keep interpreting inconsistently.

Do not use for ordinary symbol renaming, generic copyediting, or broad docs rewrites without reusable terminology.

## Required inputs

- Current conversation and the user's natural wording.
- Existing `UBIQUITOUS-MAP.md`, `UBIQUITOUS.md`, or legacy `UBIQUITOUS_LANGUAGE.md`, if present.
- Nearby project guidance such as `AGENTS.md`, `README.md`, `docs/**`, `instructions/**`, or handoff files.
- Session logs only when the user explicitly asks for history-backed vocabulary.

## Workflow

1. Determine scope and output path.
2. Infer the repository structure:
   - If `UBIQUITOUS-MAP.md` exists, read it to find the relevant context glossary.
   - If a root `UBIQUITOUS.md` or legacy `UBIQUITOUS_LANGUAGE.md` exists, treat the repo as a single context unless sources prove otherwise.
   - If neither exists, create a root `UBIQUITOUS.md` lazily when the first term is resolved.
   - When multiple contexts exist and the current topic is unclear, ask which context to update.
3. Read any existing glossary first and preserve intentional choices.
4. Extract domain nouns, workflow verbs, actor names, lifecycle states, aliases, and overloaded phrases.
5. Choose canonical terms that improve execution; keep natural-language aliases when useful.
6. Write or update the active ubiquitous-language file.
7. Add a concise pointer in the nearest active agent instruction surface.
8. Report the highest-value terms, prompt translations, sources, and skipped evidence.

## UBIQUITOUS.md Format

For new glossaries, prefer this structure:

```md
# {Context Name}

{One or two sentence description of what this context is and why it exists.}

## Language

**Order**:
{A one or two sentence description of the term}
_Avoid_: Purchase, transaction

**Invoice**:
A request for payment sent to a customer after delivery.
_Avoid_: Bill, payment request

**Customer**:
A person or organization that places orders.
_Avoid_: Client, buyer, account
```

If automation or an existing repo contract already consumes `UBIQUITOUS_LANGUAGE.md`, preserve that filename and existing required sections while aligning new term entries to the `## Language` style.

For multi-context repositories, create or update a root `UBIQUITOUS-MAP.md`:

```md
# Ubiquitous Map

## Contexts

- [Ordering](./src/ordering/UBIQUITOUS.md) - receives and tracks customer orders
- [Billing](./src/billing/UBIQUITOUS.md) - generates invoices and processes payments
- [Fulfillment](./src/fulfillment/UBIQUITOUS.md) - manages warehouse picking and shipping

## Relationships

- **Ordering -> Fulfillment**: Ordering emits `OrderPlaced` events; Fulfillment consumes them to start picking
- **Fulfillment -> Billing**: Fulfillment emits `ShipmentDispatched` events; Billing consumes them to generate invoices
- **Ordering <-> Billing**: Shared types for `CustomerId` and `Money`
```

## Term Rules

- Be opinionated. When multiple words exist for the same concept, pick one canonical term and list the others as aliases to avoid.
- Flag conflicts explicitly. If a term is ambiguous, add it to `Flagged Ambiguities` with a clear resolution.
- Keep definitions tight: one or two sentences, defining what the term is rather than what it does.
- Show relationships. Use bold term names and express cardinality where obvious.
- Include only concepts specific to this project's context. General programming concepts do not belong just because the project uses them.
- Group terms under subheadings when natural clusters emerge. Use a flat list when all terms belong to one cohesive area.
- Write an example dialogue between a developer and a domain expert that demonstrates how terms interact and clarifies boundaries between related concepts.

## Deliverables

The glossary should include context description, canonical language entries, aliases to avoid, relationships, example dialogue, flagged ambiguities, and source notes. Include prompt translations when informal user wording needs to map to repo-native actions. Structured output should include `schema_version: 1` when automation consumes it.

## Safety

- Do not copy raw private transcripts, secrets, tokens, or unnecessary personal data.
- Do not overwrite an existing glossary wholesale.
- Ask before finalizing a material policy or scope decision that cannot be inferred.
- Mark low-confidence terminology choices.

## Execution Boundaries

- Read only the current conversation, active instruction files, existing ubiquitous-language files, and directly relevant project docs unless the user asks for history-backed vocabulary.
- Write only the active ubiquitous-language file, context map, and the smallest necessary agent-instruction pointer.
- Do not run network commands, publish artifacts, change runtime projections, or edit unrelated docs for a terminology-only update.
- Do not infer domain authority from generic code symbols; require project-specific source evidence or user wording before adding a term.

## Anti-Patterns

- Turning the glossary into a generic programming dictionary.
- Copying private transcripts or secrets into vocabulary docs.
- Choosing impressive terms that make future prompts less clear.

## Examples

- "User says make it available, but in this repo that means workspace sync, user sync, and runtime-link verification; convert that wording into the glossary."
- "Inspect how the word skill means source package, generated handle, and active runtime capability in different places; define the canonical terms and flag the ambiguity."
- "Validate whether billing and fulfillment language belong in one root UBIQUITOUS.md or need a UBIQUITOUS-MAP.md."

## Failure mode

If the scope, source glossary, or authority for a terminology change is unclear, stop with one missing input rather than rewriting vocabulary by guesswork.

## Gotchas

- Natural user wording is evidence; do not erase it when choosing canonical terms.
- Avoid broad docs rewrites when a glossary pointer would solve the routing problem.

## Progressive Disclosure

Never drop required context for brevity; move it into references or deferred context and link it here.

- Local contract, evals, and task profile: `references/`
- Output template: `Infrastructure/references/deferred-skill-context/agent-ops-ubiquitous-language/references/output-format.md`
- Archived long-form workflow: `Infrastructure/references/deferred-skill-context/agent-ops-ubiquitous-language/`

## Validation

Confirm the active glossary exists, every canonical term has a one- or two-sentence definition, aliases to avoid are listed for terms with competing names, flagged ambiguities include a resolution, prompt translations include at least one user phrase when informal wording exists, and the agent instruction pointer references the active ubiquitous-language file. Fail fast: stop at the first failed gate and do not proceed until the blocker is fixed.
