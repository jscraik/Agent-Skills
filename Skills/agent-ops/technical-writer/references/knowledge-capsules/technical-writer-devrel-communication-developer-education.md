# Developer Education

Turn technical ideas into tutorials, explanations, examples, visuals, and learning aids matched to the reader's goal and current understanding.

Pack id: pack.developer-advocate-writing
Facet id: developer_education
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

### claim.creator-writing.explanations-lower-understanding-cost: Explanations Lower Understanding Cost

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

A useful explanation packages facts with context, cause, consequence, and why-it-matters so readers can understand and apply the information.

Interpretation notes:
- For technical-writer, missing context is a reader-blocking defect, not only a style issue.

### claim.creator-writing.sticky-docs-beat-curse-of-knowledge: Sticky Docs Beat Curse Of Knowledge

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Expert documentation should counter the curse of knowledge by making the core concrete, credible, memorable, and action-shaped for readers who lack the author's context.

Interpretation notes:
- Simplicity means core plus useful compression, not vague shortness.

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

## Principles

### principle.creator-writing.context-before-detail: Context Before Detail

- Type: principle
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.creator-writing.explanations-lower-understanding-cost, claim.creator-writing.sticky-docs-beat-curse-of-knowledge, claim.creator-writing.audience-gap-defines-document

Give readers enough context to care, orient, and apply details before asking them to process dense facts.

Rationale: Explanation and sticky-idea sources both warn that expert context does not transfer automatically; documents must package why, category, concrete examples, and reader confidence before details carry value.

Application notes:
- Put why-this-matters before long command, API, or architecture detail.
- Replace expert shorthand with concrete examples when the audience may lack the frame.
- Check whether the document answers the reader's first likely question.

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
- Derived from claims: claim.creator-writing.revision-needs-separate-passes, claim.creator-writing.large-docs-need-navigable-structure, claim.creator-writing.examples-and-visuals-teach-use, claim.creator-writing.llms-assist-not-own-judgment, claim.creator-writing.audience-gap-defines-document

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
