# Revision And Structure

Move drafts from raw material to usable documents with separate revision passes, navigable large-document structure, examples, visuals, and AI-assisted judgment.

Pack id: pack.creator-writing
Facet id: revision_and_structure
Runtime dependency: none; this slice is generated from a KnowledgeOS pack export.
Lifecycle status: draft

## Claim Cards

### claim.creator-writing.revision-needs-separate-passes: Revision Needs Separate Passes

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Good drafts need deliberate revision passes and mistake-detection tactics rather than a single all-purpose editing sweep.

Interpretation notes:
- Separate structural, clarity, correctness, accessibility, and polish passes when the document is important.

### claim.creator-writing.large-docs-need-navigable-structure: Large Docs Need Navigable Structure

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Large documents need explicit organization, scope, prerequisites, and sections that let readers navigate by need.

Interpretation notes:
- Long-form public writing also benefits from these technical-document structure rules when it grows beyond essay scale.

### claim.creator-writing.llms-assist-not-own-judgment: LLMs Assist Not Own Judgment

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference, article_source_note_paraphrase

LLMs can accelerate drafting, editing, formatting, and summarization, but the writer remains responsible for accuracy, audience fit, taste, and final judgment.

Interpretation notes:
- Treat AI as a writing instrument, not as the owner of truth, taste, or acceptance criteria.

### claim.creator-writing.examples-and-visuals-teach-use: Examples And Visuals Teach Use

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Technical explanation improves when examples, sample code, visuals, captions, and document type match the reader's goal and knowledge level.

Interpretation notes:
- Examples should demonstrate the point without adding accidental complexity.

### claim.creator-writing.audience-gap-defines-document: Audience Gap Defines Document

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

A useful document is shaped by what its audience already knows, what they need to learn, and what task or decision the document supports.

Interpretation notes:
- Scope, prerequisites, and key points should appear early enough to orient busy readers.

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

### principle.creator-writing.revision-is-a-separate-mode: Revision Is A Separate Mode

- Type: principle
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.creator-writing.revision-needs-separate-passes, claim.creator-writing.large-docs-need-navigable-structure, claim.creator-writing.examples-and-visuals-teach-use

Treat revision as a separate operating mode that tests structure, reader fit, examples, visuals, accessibility, and prose after drafting.

Rationale: Technical Writing Two separates drafting from self-editing, large-document organization, illustrations, sample code, tutorials, and other second-pass concerns.

Application notes:
- Do not ask one editing pass to catch every problem.
- Start revision with document structure before polishing sentences.
- Re-check examples and visuals against the reader's goal.

## Heuristics

### heuristic.creator-writing.edit-in-passes: Edit In Passes

- Type: heuristic
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.creator-writing.revision-needs-separate-passes

Run separate editing passes for structure, audience fit, correctness, clarity, accessibility, and final polish.

Use when:
- The document is long, consequential, or hard to reason about.
- A first draft has useful material but weak order.
- Review feedback keeps mixing structural and sentence-level concerns.

Avoid when:
- The artifact is a tiny note where a full pass stack would slow delivery without reducing risk.

## Checklists

### checklist.creator-writing.revision-structure-pass: Revision Structure Pass

- Type: checklist
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference, article_source_note_paraphrase
- Derived from claims: claim.creator-writing.revision-needs-separate-passes, claim.creator-writing.large-docs-need-navigable-structure, claim.creator-writing.examples-and-visuals-teach-use, claim.creator-writing.llms-assist-not-own-judgment, claim.creator-writing.audience-gap-defines-document

- [ ] Separate drafting from self-editing.
- [ ] Review document structure before sentence polish.
- [ ] Confirm the introduction states scope, prerequisites, audience, and key points.
- [ ] Break large topics into sections that match reader goals.
- [ ] Check whether examples and sample code demonstrate the intended concept without distracting complexity.
- [ ] Confirm visuals have useful captions and the right information density.
- [ ] Match document type to reader goal.
- [ ] Use LLM output only after checking accuracy, audience fit, and final judgment.

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
