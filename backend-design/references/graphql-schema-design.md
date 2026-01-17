# GraphQL Schema Design Patterns

## Schema Organization
- Modular schema files per domain
- Schema-first development

## Type Design
- Non-null for required fields
- Interfaces for polymorphism
- Unions for heterogeneous results
- Custom scalars for domain types

## Pagination
- Prefer Relay-style connections for large datasets
- Offset pagination for simple lists

## Mutations
- Input + payload pattern
- Include errors in payload
- Consider idempotency keys

## Performance
- DataLoader for relationships
- Depth and complexity limits
- Persisted queries when needed

## Deprecation
- Use @deprecated directive
- Avoid breaking changes; add new fields instead
