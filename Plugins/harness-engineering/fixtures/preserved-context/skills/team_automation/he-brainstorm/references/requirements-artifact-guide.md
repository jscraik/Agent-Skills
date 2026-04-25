# Requirements Artifact Guide

Read when: you are writing or updating the durable output from `he-brainstorm` and need the full requirements-doc template or blocker-handling rules.

## Default path

For new substantial work, write:
- `docs/brainstorms/YYYY-MM-DD-<topic>-requirements.md`

Compatibility:
- if resuming an existing legacy `docs/brainstorms/YYYY-MM-DD-<topic>-brainstorm.md` document, update it in place unless the user explicitly wants to rename it

## Frontmatter

```yaml
---
title: <requirements title>
date: YYYY-MM-DD
status: draft
spec_required: none|lite|full
risk_level: low|medium|high
complexity: small|medium|large
---
```

## Recommended structure

```markdown
# <Requirements Title>

## Problem Frame
[Who is affected, what is changing, and why it matters]

## Requirements
**[Group Header]**
- R1. [Concrete requirement in this group]
- R2. [Concrete requirement in this group]

## Success Criteria
- [How we will know this solved the right problem]

## Scope Boundaries
- [Deliberate non-goal or exclusion]

## Key Decisions
- [Decision]: [Rationale]

## Dependencies / Assumptions
- [Only include if material]

## Outstanding Questions
### Resolve Before Planning
- [Affects R1][User decision] [Question that must be answered before planning can proceed]

### Deferred to Planning
- [Affects R2][Technical] [Question that should be answered during planning or codebase exploration]
- [Affects R2][Needs research] [Question that likely requires research during planning]

## Next Steps
[If `Resolve Before Planning` is empty: `-> /he:plan` or `-> /he:spec`, depending on `spec_required`]
[If `Resolve Before Planning` is not empty: `-> Resume /he:brainstorm` to resolve blocking questions before planning]
```

## Visual aids

Add a visual aid when it will materially improve understanding.

Preferred formats:
- Mermaid or ASCII for user flows or multi-party interactions
- tables for mode, variant, or approach comparisons

Keep visuals conceptual rather than implementation-specific, and treat prose as authoritative when prose and diagrams disagree.

## Blocker handling

- Keep `Resolve Before Planning` limited to questions that truly block the next stage.
- Move answered items into decisions or assumptions instead of leaving them open.
- Keep implementation details out unless they are themselves part of the product or architecture decision being brainstormed.
