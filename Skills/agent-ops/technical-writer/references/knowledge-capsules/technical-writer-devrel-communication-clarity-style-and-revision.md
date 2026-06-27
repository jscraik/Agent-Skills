# Clarity Style And Revision

Control writing style through consistent terms, active actors, one idea per unit, separate revision passes, and AI-assisted but human-owned judgment.

Pack id: pack.developer-advocate-writing
Facet id: clarity_style_and_revision
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

### claim.creator-writing.revision-needs-separate-passes: Revision Needs Separate Passes

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Good drafts need deliberate revision passes and mistake-detection tactics rather than a single all-purpose editing sweep.

Interpretation notes:
- Separate structural, clarity, correctness, accessibility, and polish passes when the document is important.

### claim.creator-writing.llms-assist-not-own-judgment: LLMs Assist Not Own Judgment

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference, article_source_note_paraphrase

LLMs can accelerate drafting, editing, formatting, and summarization, but the writer remains responsible for accuracy, audience fit, taste, and final judgment.

Interpretation notes:
- Treat AI as a writing instrument, not as the owner of truth, taste, or acceptance criteria.

### claim.creator-writing.audience-gap-defines-document: Audience Gap Defines Document

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

A useful document is shaped by what its audience already knows, what they need to learn, and what task or decision the document supports.

Interpretation notes:
- Scope, prerequisites, and key points should appear early enough to orient busy readers.

### claim.creator-writing.large-docs-need-navigable-structure: Large Docs Need Navigable Structure

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Large documents need explicit organization, scope, prerequisites, and sections that let readers navigate by need.

Interpretation notes:
- Long-form public writing also benefits from these technical-document structure rules when it grows beyond essay scale.

### claim.creator-writing.examples-and-visuals-teach-use: Examples And Visuals Teach Use

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Technical explanation improves when examples, sample code, visuals, captions, and document type match the reader's goal and knowledge level.

Interpretation notes:
- Examples should demonstrate the point without adding accidental complexity.

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
