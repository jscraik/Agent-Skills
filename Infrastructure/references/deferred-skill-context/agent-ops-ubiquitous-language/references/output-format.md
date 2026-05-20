# Ubiquitous Language Output Format

Use this template when creating or updating `UBIQUITOUS.md`. If a repository already has `UBIQUITOUS_LANGUAGE.md` or automation consumes that filename, preserve the existing filename and align the content to this structure.

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

- "Account" is used for both **Customer** and user login identity. Resolution: use **Customer** for the ordering actor and **User Account** for login identity.

## Example Dialogue

> **Dev:** "When I say purchase, do I mean **Order**?"
>
> **Domain expert:** "Yes. Use **Order** for the customer's requested goods. Purchase is an alias to avoid."
>
> **Dev:** "Is an **Invoice** the same as a payment?"
>
> **Domain expert:** "No. An **Invoice** is the request for payment. A payment is the settlement event."

## Sources

- Current conversation
- AGENTS.md
- README.md
```

## Single vs Multi-Context Repos

For a single-context repo, use one root `UBIQUITOUS.md`.

For a multi-context repo, use a root `UBIQUITOUS-MAP.md` to list contexts, where they live, and how they relate:

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

Infer structure before writing:

- If `UBIQUITOUS-MAP.md` exists, read it to find contexts.
- If only a root `UBIQUITOUS.md` or `UBIQUITOUS_LANGUAGE.md` exists, treat it as a single context.
- If neither exists, create a root `UBIQUITOUS.md` lazily when the first term is resolved.
- When multiple contexts exist and the current topic is unclear, ask.

## Optional Repo Extensions

Keep these sections when an existing repo contract already uses them, or when the user's wording makes them useful:

- `## Prompt Translations` for mapping informal user phrases to canonical agent instructions.
- `## Agent Integration` for noting which instruction surface points agents at the glossary.
- `## Decisions` for durable naming decisions.
- `## Open Questions` for unresolved terminology choices.

## Quality Bar

- The glossary should help future agents act correctly without asking the user for technical vocabulary.
- Be opinionated: pick one canonical term and list competing words in `_Avoid_`.
- Keep definitions tight: one or two sentences defining what the term is, not what it does.
- Only include terms specific to this project's context; general programming concepts do not belong.
- Show relationships with bold term names and cardinality where obvious.
- Prompt translations should be copy-pasteable when present.
- Ambiguities should be visible enough that future agents do not silently choose the wrong meaning.
- Agent integration should be short, operational, and attached to a high-traffic instruction surface when present.
