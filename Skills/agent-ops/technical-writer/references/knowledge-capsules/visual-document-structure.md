# Visual Document Structure

Evaluate decks, slidedocs, screenshots, diagrams, and visual docs as standalone information architecture rather than decorative presentation assets.

Pack id: pack.creator-writing
Facet id: visual_document_structure
Runtime dependency: none; this slice is generated from a KnowledgeOS pack export.
Lifecycle status: draft

## Claim Cards

### claim.creator-writing.visual-documents-need-standalone-architecture: Visual Documents Need Standalone Architecture

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Visual documents must be architected to stand alone when the presenter is absent, with one idea, hierarchy, diagrams, captions, and white space carrying the meaning.

Interpretation notes:
- Do not review a slidedoc like a talk deck; check whether it works as a document.

### claim.creator-writing.examples-and-visuals-teach-use: Examples And Visuals Teach Use

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Technical explanation improves when examples, sample code, visuals, captions, and document type match the reader's goal and knowledge level.

Interpretation notes:
- Examples should demonstrate the point without adding accidental complexity.

### claim.creator-writing.visual-meaning-needs-nonvisual-support: Visual Meaning Needs Nonvisual Support

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Important meaning should not depend on image visibility, color, shape, position, or styling alone; text, labels, alt text, and measured contrast should carry the meaning too.

Interpretation notes:
- If color disappears, the reader should still know what the document means.

### claim.creator-writing.answer-first-structure-supports-review: Answer First Structure Supports Review

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Documents become easier to review when they answer the reader's live question first and then group supporting reasons under that answer.

Interpretation notes:
- Use this for design docs, runbooks, PR explanations, and trust-surface docs that bury the decision or recovery path.

### claim.creator-writing.positioning-sets-document-context: Positioning Sets Document Context

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Documentation should set context by naming the category, alternatives, audience, differentiated value, and why-now frame that readers need to interpret the material correctly.

Interpretation notes:
- When docs omit context, readers invent one that may misclassify the product, workflow, or risk.

### claim.creator-writing.accessible-docs-benefit-everyone: Accessible Docs Benefit Everyone

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Accessible documentation helps readers with permanent, temporary, situational, visible, and invisible disabilities, and often improves usability for everyone.

Interpretation notes:
- Apply accessibility expectations to docs, comments, UI copy, CLI help, and error messages.

### claim.creator-writing.inclusive-language-centers-readers: Inclusive Language Centers Readers

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Accessible writing should avoid patronizing, euphemistic, or dehumanizing language and should respect community naming preferences.

Interpretation notes:
- Prefer reader dignity and community self-description over house-style cleverness.

## Principles

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

### heuristic.creator-writing.choose-visual-document-intentionally: Choose Visual Document Intentionally

- Type: heuristic
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.creator-writing.visual-documents-need-standalone-architecture

Use a visual document when the material must travel, support consensus, or combine prose and diagrams around standalone ideas.

Use when:
- A dense deck is being used as a document.
- A long doc would benefit from visual hierarchy and diagrams.
- The reader may receive the material without a presenter.

Avoid when:
- The output is a sparse talk deck whose meaning depends on live delivery.

### heuristic.creator-writing.describe-purpose-not-appearance: Describe Purpose Not Appearance

- Type: heuristic
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.creator-writing.visual-meaning-needs-nonvisual-support

For alt text and visual descriptions, describe what the reader needs from the image in context rather than cataloging every visible detail.

Use when:
- An image, diagram, chart, or screenshot carries information needed by the reader.
- A generated pack, README, or UI flow includes visual-only explanation.
- A diagram uses color, position, or shape to carry meaning.

Avoid when:
- The image is decorative and should be hidden from assistive technology instead of described.

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

### checklist.creator-writing.accessibility-editing-pass: Accessibility Editing Pass

- Type: checklist
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.creator-writing.accessible-docs-benefit-everyone, claim.creator-writing.visual-meaning-needs-nonvisual-support, claim.creator-writing.inclusive-language-centers-readers

- [ ] Check whether the document works for permanent, temporary, and situational access needs.
- [ ] Add useful alt text for images that carry information.
- [ ] Verify text and image contrast with a contrast checker when color choices matter.
- [ ] Do not rely on color, shape, position, or styling alone to convey meaning.
- [ ] Add labels, text, symbols, or patterns where visual cues carry meaning.
- [ ] Use inclusive language that respects people and community preferences.
- [ ] Check headings, links, UI text, CLI help, and error messages for reader barriers.

## Rubrics

### rubric.creator-writing.accessible-document-readiness: Accessible Document Readiness

- Type: rubric
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.creator-writing.accessible-docs-benefit-everyone, claim.creator-writing.visual-meaning-needs-nonvisual-support, claim.creator-writing.inclusive-language-centers-readers

- perceivable: Can readers perceive the document's meaning without relying on one sensory channel?
  - pass: Images, visual cues, color, labels, and contrast have text or structural support.
  - fail: Meaning depends on color, position, or image visibility alone.
- understandable: Does the language reduce unnecessary reader barriers?
  - pass: The document uses clear language, defines needed terms, and avoids dehumanizing wording.
  - fail: The document assumes perfect context or uses biased, patronizing, or unclear language.
- usable: Does accessibility apply across the actual writing surface?
  - pass: The pass covers docs, comments, UI text, CLI help, links, headings, and error messages as relevant.
  - fail: Accessibility is limited to body text while surrounding writing surfaces remain inaccessible.
