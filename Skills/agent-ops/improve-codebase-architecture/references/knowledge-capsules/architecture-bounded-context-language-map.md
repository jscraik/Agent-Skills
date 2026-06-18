# Bounded Context Language Map

Map user, repo, runtime, generated, and external-tool terminology before renaming or merging architecture concepts.

Pack id: pack.codebase-architecture
Facet id: bounded_context_language_map
Runtime dependency: none; this slice is generated from a KnowledgeOS pack export.
Lifecycle status: draft

## Claim Cards

### claim.arch.language-bounds-context: Language Bounds Context

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Architecture review should treat domain language as a boundary signal: overloaded terms, mixed vocabularies, and ownerless names often reveal unclear model ownership.

Interpretation notes:
- This claim supports mapping user wording to canonical repo terms before renaming.
- It should preserve useful bounded-context distinctions instead of flattening them.

## Checklists

### checklist.arch.bounded-context-language-map: Bounded Context Language Map Checklist

- Type: checklist
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.arch.language-bounds-context

- [ ] Capture the user phrase, repo canonical term, runtime or generated term, and source owner before renaming.
- [ ] Check whether the same word names different concepts in code, docs, tests, CLI output, or generated artifacts.
- [ ] Keep bounded contexts separate when merging terms would erase useful ownership or policy distinctions.
- [ ] Add an anti-corruption translation when an external tool or plugin vocabulary should not leak into canonical repo language.
- [ ] Rename only through the owner that can safely change the source and its projections.
- [ ] Add an eval, schema rule, or glossary entry when repeated language drift causes agent mistakes.
