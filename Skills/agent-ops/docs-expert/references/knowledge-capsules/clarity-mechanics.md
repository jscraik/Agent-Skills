# Clarity Mechanics

Make writing understandable through consistent terms, explicit actors, focused sentences, useful lists, scoped documents, and audience-fit language.

Pack id: pack.creator-writing
Facet id: clarity_mechanics
Runtime dependency: none; this slice is generated from a KnowledgeOS pack export.
Lifecycle status: draft

## Claim Cards

### claim.creator-writing.terms-must-be-defined-consistently: Terms Must Be Defined Consistently

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Technical writing should define unfamiliar terms, introduce acronyms deliberately, and use the same term consistently once chosen.

Interpretation notes:
- Treat terminology variety as reader risk when precision matters.

### claim.creator-writing.active-voice-clarifies-actors: Active Voice Clarifies Actors

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Active voice usually improves technical writing because it names who is acting and what they act on.

Interpretation notes:
- Passive voice can still be acceptable when the actor is unknown, irrelevant, or intentionally de-emphasized.

### claim.creator-writing.one-idea-per-unit: One Idea Per Unit

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Sentences and paragraphs become clearer when each unit carries one main idea and moves extra structure into lists or separate paragraphs.

Interpretation notes:
- Apply this rule at sentence, paragraph, section, and checklist levels.

### claim.creator-writing.audience-gap-defines-document: Audience Gap Defines Document

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

A useful document is shaped by what its audience already knows, what they need to learn, and what task or decision the document supports.

Interpretation notes:
- Scope, prerequisites, and key points should appear early enough to orient busy readers.

### claim.creator-writing.docs-should-minimize-parsing-tax: Docs Should Minimize Parsing Tax

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Documentation should reduce the reader's parsing burden with simple, unambiguous, consistent sentences that do not require unnecessary memory juggling.

Interpretation notes:
- Prefer a slightly longer sentence if it removes a parsing hitch.

### claim.creator-writing.accessible-docs-benefit-everyone: Accessible Docs Benefit Everyone

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Accessible documentation helps readers with permanent, temporary, situational, visible, and invisible disabilities, and often improves usability for everyone.

Interpretation notes:
- Apply accessibility expectations to docs, comments, UI copy, CLI help, and error messages.

### claim.creator-writing.error-messages-enable-recovery: Error Messages Enable Recovery

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Error messages should report failures, preserve root cause, identify the cause or invalid input, state relevant constraints, and tell users how to recover.

Interpretation notes:
- Treat error text as recovery writing, not merely notification text.

## Principles

### principle.creator-writing.reader-clarity-before-style: Reader Clarity Before Style

- Type: principle
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.creator-writing.terms-must-be-defined-consistently, claim.creator-writing.active-voice-clarifies-actors, claim.creator-writing.one-idea-per-unit, claim.creator-writing.audience-gap-defines-document

Prefer wording and structure that make the reader's task easier over stylistic variety, cleverness, or author convenience.

Rationale: The Technical Writing One source material repeatedly treats clarity as the central goal across words, sentences, paragraphs, lists, audience, and document openings.

Application notes:
- Define terms before using them heavily.
- Name actors and actions when ambiguity would slow the reader.
- Break overloaded units into sentences, lists, paragraphs, or sections.

## Heuristics

### heuristic.creator-writing.one-idea-one-unit: One Idea One Unit

- Type: heuristic
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.creator-writing.one-idea-per-unit

If a sentence, paragraph, or section tries to do multiple jobs, split it until each unit has one clear job.

Use when:
- A sentence has several clauses, exceptions, or embedded items.
- A paragraph changes topics halfway through.
- A section feels correct but hard to scan.

Avoid when:
- Splitting would destroy necessary comparison or rhythm without improving reader comprehension.

## Checklists

### checklist.creator-writing.clarity-editing-pass: Clarity Editing Pass

- Type: checklist
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.creator-writing.terms-must-be-defined-consistently, claim.creator-writing.active-voice-clarifies-actors, claim.creator-writing.one-idea-per-unit, claim.creator-writing.audience-gap-defines-document

- [ ] Define unfamiliar terms before relying on them.
- [ ] Use one term for one concept within the same document or product area.
- [ ] Replace ambiguous pronouns with explicit nouns when readers could guess wrong.
- [ ] Prefer active voice when the actor matters.
- [ ] Choose specific verbs over weak generic constructions.
- [ ] Keep each sentence focused on one idea.
- [ ] Convert embedded lists into bulleted or numbered lists.
- [ ] Keep list items parallel.
- [ ] Start paragraphs with the central point when reader orientation matters.
- [ ] Keep each paragraph focused on one topic.
- [ ] State audience, scope, prerequisites, and key points early.

## Lenses

### lens.creator-writing.reader-access-and-recovery: Reader Access And Recovery Lens

- Type: lens
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.creator-writing.audience-gap-defines-document, claim.creator-writing.accessible-docs-benefit-everyone, claim.creator-writing.error-messages-enable-recovery

- Start from the reader's goal, prior knowledge, constraints, and access needs.
- Treat clarity, accessibility, and recoverability as writing quality, not afterthoughts.
- Preserve the information a reader needs to act: scope, cause, actual value, expected constraint, example, or next step.
- Check whether meaning survives without color, perfect context, expert vocabulary, or visual inspection.
- Keep generated or AI-assisted wording accountable to audience fit, correctness, and final human judgment.
