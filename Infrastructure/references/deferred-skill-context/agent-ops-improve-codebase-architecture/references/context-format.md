# CONTEXT.md Format

Use `CONTEXT.md` to capture project-specific language for a bounded context. This is not a generic programming glossary.

## Single vs Multiple Contexts

**Single context**:
Use one `CONTEXT.md` at the repo root.

**Multiple contexts**:
Use a root `CONTEXT-MAP.md` that lists every context, where each `CONTEXT.md` lives, and how contexts relate.

When multiple contexts exist, infer the current topic from files, docs, branch, or Linear issue. If it is unclear, ask one focused question before writing.

## CONTEXT.md Template

```md
# {Context Name}

{One or two sentence description of what this context is and why it exists.}

## Language

**Order**:
A customer's request to purchase one or more items.
_Avoid_: Purchase, transaction

**Invoice**:
A request for payment sent to a customer after delivery.
_Avoid_: Bill, payment request

## Relationships

- An **Order** produces one or more **Invoices**
- An **Invoice** belongs to exactly one **Customer**

## Example dialogue

> **Dev:** "When a **Customer** places an **Order**, do we create the **Invoice** immediately?"
> **Domain expert:** "No - an **Invoice** is only generated once a **Fulfillment** is confirmed."

## Flagged ambiguities

- "account" was used to mean both **Customer** and **User** - resolved: these are distinct concepts.
```

## CONTEXT-MAP.md Template

```md
# Context Map

## Contexts

- [Ordering](./src/ordering/CONTEXT.md) - receives and tracks customer orders
- [Billing](./src/billing/CONTEXT.md) - generates invoices and processes payments
- [Fulfillment](./src/fulfillment/CONTEXT.md) - manages warehouse picking and shipping

## Relationships

- **Ordering -> Fulfillment**: Ordering emits `OrderPlaced` events; Fulfillment consumes them to start picking
- **Fulfillment -> Billing**: Fulfillment emits `ShipmentDispatched` events; Billing consumes them to generate invoices
- **Ordering <-> Billing**: Shared types for `CustomerId` and `Money`
```

## Rules

- Be opinionated: pick the best term and list aliases to avoid.
- Flag conflicts explicitly and resolve them when evidence supports a resolution.
- Keep definitions to one sentence.
- Define what a term is, not what it does.
- Show relationships and cardinality where obvious.
- Include only project-specific context terms.
- Exclude generic programming concepts such as timeout, utility, adapter, error, service, or repository unless the project gives them domain-specific meaning.
- Group terms under subheadings when natural clusters emerge.
- Write example dialogue that clarifies boundaries between related concepts.
- Create `CONTEXT.md` lazily only when the first term is resolved.
