# Design-System Integration Contract

## Table of Contents
- [Purpose](#purpose)
- [Default contract](#default-contract)
- [Routing rules](#routing-rules)
- [Validation checklist](#validation-checklist)
- [Exceptions](#exceptions)
- [Related routing contract](#related-routing-contract)

## Purpose
Keep typography, spacing, iconography, color usage, and component-level styling aligned across all `frontend/ui` skills.

## Default contract
- Use semantic tokens and mapped theme variables before raw literals.
- Use canonical typography scales and spacing scales before introducing local overrides.
- Use the canonical icon system and naming conventions before adding one-off icon imports.
- Keep accessibility outcomes aligned with WCAG 2.2 AA for focus visibility, contrast, and keyboard support.
- When a recommendation changes token architecture, aliasing, theme slots, or icon governance, route to `frontend/ui/design-system/SKILL.md`.

## Routing rules
- Keep implementation-level polish and component behavior in the calling UI skill.
- Escalate to `design-system` when the request changes shared visual language across surfaces.
- Do not create parallel token rules inside other UI skills.

## Validation checklist
- Typography decisions map to existing tokenized type scales or an approved exception.
- Spacing and sizing decisions map to existing semantic spacing tokens or an approved exception.
- Icon usage maps to canonical icon sources and naming.
- No new hardcoded visual literals are introduced without explicit rationale.
- Cross-skill recommendations do not conflict with `design-system` routing boundaries.

## Exceptions
- Temporary exceptions are allowed only when a request is explicitly local-only and non-reusable.
- Each exception must include a short rationale and a follow-up normalization path.

## Related routing contract
- Use `frontend/ui/references/skill-routing-matrix-2026.md` when deciding which frontend skill should own a request before applying this integration contract.
