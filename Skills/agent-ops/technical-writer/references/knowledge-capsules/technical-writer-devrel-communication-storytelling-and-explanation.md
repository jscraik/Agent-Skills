# Storytelling And Explanation

Make complex technical ideas concrete, memorable, credible, and action-shaped while avoiding the curse of knowledge.

Pack id: pack.developer-advocate-writing
Facet id: storytelling_and_explanation
Runtime dependency: none; this slice is generated from a KnowledgeOS pack export.
Lifecycle status: draft

## Claim Cards

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

### claim.creator-writing.positioning-sets-document-context: Positioning Sets Document Context

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Documentation should set context by naming the category, alternatives, audience, differentiated value, and why-now frame that readers need to interpret the material correctly.

Interpretation notes:
- When docs omit context, readers invent one that may misclassify the product, workflow, or risk.

### claim.creator-writing.audience-gap-defines-document: Audience Gap Defines Document

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

A useful document is shaped by what its audience already knows, what they need to learn, and what task or decision the document supports.

Interpretation notes:
- Scope, prerequisites, and key points should appear early enough to orient busy readers.

### claim.creator-writing.answer-first-structure-supports-review: Answer First Structure Supports Review

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Documents become easier to review when they answer the reader's live question first and then group supporting reasons under that answer.

Interpretation notes:
- Use this for design docs, runbooks, PR explanations, and trust-surface docs that bury the decision or recovery path.

### claim.creator-writing.visual-documents-need-standalone-architecture: Visual Documents Need Standalone Architecture

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Visual documents must be architected to stand alone when the presenter is absent, with one idea, hierarchy, diagrams, captions, and white space carrying the meaning.

Interpretation notes:
- Do not review a slidedoc like a talk deck; check whether it works as a document.

### claim.creator-writing.user-need-defines-content: User Need Defines Content

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Documentation content should start from reader jobs, vocabulary, mental models, journeys, and likely actions rather than from what the organization wants to publish.

Interpretation notes:
- Treat reader need as evidence to inspect, not a persona label to assert.

### claim.creator-writing.devrel-docs-bridge-community-and-company: DevRel Docs Bridge Community And Company

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

DevRel documentation is a two-way interface: it helps developers succeed while also bringing community evidence back to product, engineering, marketing, and documentation owners.

Interpretation notes:
- Public docs and trust docs should not collapse community usefulness into company messaging.

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

### principle.creator-writing.documents-need-argument-architecture: Documents Need Argument Architecture

- Type: principle
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.creator-writing.answer-first-structure-supports-review, claim.creator-writing.visual-documents-need-standalone-architecture

Important documents need visible argument architecture: answer, support, sequence, visual hierarchy, and standalone evidence must align.

Rationale: Minto's question-answer logic and Duarte's slidedoc rules both treat structure as a way to reduce reader work and preserve meaning across handoff.

Application notes:
- Review structure before sentence polish.
- Ask what question each section answers.
- Check whether visuals and headings preserve the document's logic when skimmed.

## Heuristics

### heuristic.creator-writing.answer-then-support: Answer Then Support

- Type: heuristic
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.creator-writing.answer-first-structure-supports-review

Put the answer, decision, or recovery path before the supporting reasoning when the reader is trying to act or review.

Use when:
- A runbook, README, trust doc, or design note buries its decision.
- Sections answer questions the reader has not been prepared to ask.
- The document contains correct facts but weak review flow.

Avoid when:
- The document is intentionally exploratory and the reader has opted into discovery rather than action.

### heuristic.creator-writing.frame-by-category-alternatives-value: Frame By Category Alternatives Value

- Type: heuristic
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.creator-writing.positioning-sets-document-context

When readers may misclassify a product, workflow, or risk, name the category, alternatives, unique value, audience, and why-now context early.

Use when:
- Docs assume readers already know what kind of thing they are looking at.
- The product or workflow is novel, cross-category, or easily compared with the wrong alternative.
- Public docs need to explain why a capability matters now.

Avoid when:
- The doc is pure API reference and an adjacent overview already supplies the frame.

## Checklists

### checklist.creator-writing.argument-visual-doc-pass: Argument Visual Doc Pass

- Type: checklist
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.creator-writing.answer-first-structure-supports-review, claim.creator-writing.visual-documents-need-standalone-architecture, claim.creator-writing.positioning-sets-document-context

- [ ] State the answer, recommendation, or recovery path before detailed support.
- [ ] Check that each section answers a question raised by the prior section or heading.
- [ ] Name the category, alternatives, value, and audience when context affects interpretation.
- [ ] Use headings that preserve the argument when skimmed.
- [ ] Confirm visuals have standalone captions and support the adjacent claim.
- [ ] Use diagrams or tables only when they reduce reader work.
- [ ] Check that white space, hierarchy, and grouping guide the eye to the most important point.
- [ ] Confirm the document still works when forwarded without the author present.

## Rubrics

### rubric.creator-writing.technical-writer-capsule-readiness: Technical Writer Capsule Readiness

- Type: rubric
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.creator-writing.user-need-defines-content, claim.creator-writing.answer-first-structure-supports-review, claim.creator-writing.devrel-docs-bridge-community-and-company

- reader-job: Does the document serve a named reader job or decision?
  - pass: The document identifies the reader's task, question, or decision and orders content around it.
  - fail: The document presents author-owned information without a clear reader job.
- evidence-and-maintenance: Is the document grounded in evidence and maintainable over time?
  - pass: Claims, commands, ownership, and update triggers are tied to inspected evidence.
  - fail: The document relies on assumptions, stale examples, or unowned lifecycle claims.
- structure: Does the structure answer reader questions in a reviewable order?
  - pass: The answer or recovery path appears early and support is grouped under the questions it answers.
  - fail: The reader must reconstruct the point from scattered facts.
- devrel-boundary: Are community usefulness and business value kept distinct?
  - pass: Developer benefit, feedback route, product owner, and organization goal are named without conflation.
  - fail: Public docs become marketing claims or hide product/community feedback gaps.
