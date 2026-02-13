# Tool Design for Agent-Native Systems

## Principle

Model tools as **capabilities**, not pre-baked workflows.

## Design rules

1. Keep tools atomic.
2. Keep inputs data-centric.
3. Keep outputs verifiable.
4. Preserve composability.
5. Avoid hiding business decisions in tool internals.

## Good vs risky shapes

### Risky
- `process_and_prioritize_feedback`
- `organize_all_project_docs`

These encode strategy and policy that should usually remain in prompts and architecture policy.

### Better
- `read_resource`
- `write_resource`
- `list_resources`
- `update_metadata`
- `delete_resource`

These let agents compose behavior while preserving auditability.

## CRUD completeness

For each entity, verify whether product semantics require full lifecycle support:

- create
- read
- update
- delete/archive

If deletion is intentionally unsupported, document rationale and safe alternative.

## Validation posture

- Validate for safety and schema integrity.
- Avoid over-constraining possible values where upstream systems already validate dynamic domains.
- Return enough context in outputs for recovery after errors.

## Error handling guidance

Return errors that support next-step decisions:

- What failed.
- Why (actionable cause when known).
- Recovery hints.

Avoid opaque generic failures that force blind retries.
