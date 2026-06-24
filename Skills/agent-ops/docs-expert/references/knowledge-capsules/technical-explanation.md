# Technical Explanation

Choose the right document type and teaching aids for the reader's goal, from tutorials and explanations to sample code and visuals.

Pack id: pack.creator-writing
Facet id: technical_explanation
Runtime dependency: none; this slice is generated from a KnowledgeOS pack export.
Lifecycle status: draft

## Claim Cards

### claim.creator-writing.audience-gap-defines-document: Audience Gap Defines Document

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

A useful document is shaped by what its audience already knows, what they need to learn, and what task or decision the document supports.

Interpretation notes:
- Scope, prerequisites, and key points should appear early enough to orient busy readers.

### claim.creator-writing.examples-and-visuals-teach-use: Examples And Visuals Teach Use

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Technical explanation improves when examples, sample code, visuals, captions, and document type match the reader's goal and knowledge level.

Interpretation notes:
- Examples should demonstrate the point without adding accidental complexity.

### claim.creator-writing.large-docs-need-navigable-structure: Large Docs Need Navigable Structure

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Large documents need explicit organization, scope, prerequisites, and sections that let readers navigate by need.

Interpretation notes:
- Long-form public writing also benefits from these technical-document structure rules when it grows beyond essay scale.

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

## Heuristics

### heuristic.creator-writing.choose-doc-type-by-reader-goal: Choose Doc Type By Reader Goal

- Type: heuristic
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.creator-writing.examples-and-visuals-teach-use, claim.creator-writing.audience-gap-defines-document

Choose tutorial, how-to, explanation, reference, design note, or error text based on what the reader is trying to accomplish.

Use when:
- A document mixes teaching, reference, decision support, and task steps.
- A beginner audience needs guided context before details.
- Sample code or visuals may be doing the wrong explanatory job.

Avoid when:
- The document type is fixed by an external template or compliance requirement.

## Checklists

### checklist.creator-writing.revision-structure-pass: Revision Structure Pass

- Type: checklist
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference, article_source_note_paraphrase
- Derived from claims: claim.creator-writing.revision-needs-separate-passes, claim.creator-writing.large-docs-need-navigable-structure, claim.creator-writing.examples-and-visuals-teach-use, claim.creator-writing.llms-assist-not-own-judgment

- [ ] Separate drafting from self-editing.
- [ ] Review document structure before sentence polish.
- [ ] Confirm the introduction states scope, prerequisites, audience, and key points.
- [ ] Break large topics into sections that match reader goals.
- [ ] Check whether examples and sample code demonstrate the intended concept without distracting complexity.
- [ ] Confirm visuals have useful captions and the right information density.
- [ ] Match document type to reader goal.
- [ ] Use LLM output only after checking accuracy, audience fit, and final judgment.

## Rubrics

### rubric.creator-writing.technical-explanation-readiness: Technical Explanation Readiness

- Type: rubric
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.creator-writing.audience-gap-defines-document, claim.creator-writing.examples-and-visuals-teach-use, claim.creator-writing.large-docs-need-navigable-structure

- audience-fit: Does the explanation match what the reader already knows and needs to learn?
  - pass: The document names or implies the reader's role, goal, prerequisites, and knowledge gap.
  - fail: The explanation assumes the author's context without orienting the reader.
- structure: Is the document organized for navigation and use?
  - pass: Scope, sections, examples, and key points help readers find what they need.
  - fail: The document is a pile of correct facts with weak order.
- examples: Do examples, code, and visuals teach the intended point?
  - pass: Examples and visuals demonstrate the concept without accidental distracting complexity.
  - fail: Examples are absent, too abstract, or more complex than the concept being taught.
- beginner-empathy: Does the explanation avoid the curse of knowledge?
  - pass: The writer explains prerequisite concepts or links to them before using them heavily.
  - fail: The writer uses expert shortcuts that a target beginner cannot decode.
