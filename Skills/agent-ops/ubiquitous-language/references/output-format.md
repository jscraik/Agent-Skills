# Ubiquitous Language Output Format

Use this template when creating or updating `UBIQUITOUS.md`. If a repository
already has `UBIQUITOUS_LANGUAGE.md` or automation consumes that filename,
preserve the existing filename and align the content to this structure.

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

## Relationships

- **Customer** places zero or more **Orders**.
- **Order** may produce one **Invoice** after delivery.

## Flagged Ambiguities

- "Account" is used for both **Customer** and user login identity. Resolution:
  use **Customer** for the ordering actor and **User Account** for login identity.

## Example Dialogue

> **Dev:** "When I say purchase, do I mean **Order**?"
>
> **Domain expert:** "Yes. Use **Order** for the customer's requested goods.
> Purchase is an alias to avoid."

## Sources

- Current conversation
- AGENTS.md
- README.md
```

## Single vs Multi-Context Repositories

For a single-context repository, use one root `UBIQUITOUS.md`.

For a multi-context repository, use a root `UBIQUITOUS-MAP.md` to list
contexts, where they live, and how they relate:

```md
# Ubiquitous Map

## Contexts

- **Ordering** — `src/ordering/UBIQUITOUS.md` — receives and tracks customer orders
- **Billing** — `src/billing/UBIQUITOUS.md` — generates invoices and processes payments
- **Fulfillment** — `src/fulfillment/UBIQUITOUS.md` — manages warehouse picking and shipping

## Relationships

- **Ordering -> Fulfillment**: Ordering emits `OrderPlaced`; Fulfillment consumes it.
- **Fulfillment -> Billing**: Fulfillment emits `ShipmentDispatched`; Billing consumes it.
```

Infer structure before writing:

- If `UBIQUITOUS-MAP.md` exists, read it to find contexts.
- If only a root `UBIQUITOUS.md` or `UBIQUITOUS_LANGUAGE.md` exists, treat it
  as a single context.
- If neither exists, create a root `UBIQUITOUS.md` lazily when the first term
  is resolved.
- When multiple contexts exist and the current topic is unclear, ask.

## Optional Repository Extensions

- `## Prompt Translations` maps informal phrases to canonical agent actions.
- `## Agent Integration` records the instruction surface that points here.
- `## Decisions` records durable naming decisions.
- `## Open Questions` records unresolved terminology choices.

## Quality Bar

- Help future agents act correctly without requiring specialist vocabulary.
- Pick one canonical term and list competing words in `_Avoid_`.
- Keep definitions to one or two sentences.
- Include only project-specific concepts.
- Show relationships and cardinality where useful.
- Make prompt translations copy-pasteable.
- Make ambiguities and their resolutions explicit.
