# Accessible And Inclusive Writing

Make technical and public writing perceivable, understandable, inclusive, and usable across permanent, temporary, situational, visible, and invisible access needs.

Pack id: pack.developer-advocate-writing
Facet id: accessible_and_inclusive_writing
Runtime dependency: none; this slice is generated from a KnowledgeOS pack export.
Lifecycle status: draft

## Claim Cards

### claim.creator-writing.accessible-docs-benefit-everyone: Accessible Docs Benefit Everyone

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Accessible documentation helps readers with permanent, temporary, situational, visible, and invisible disabilities, and often improves usability for everyone.

Interpretation notes:
- Apply accessibility expectations to docs, comments, UI copy, CLI help, and error messages.

### claim.creator-writing.visual-meaning-needs-nonvisual-support: Visual Meaning Needs Nonvisual Support

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Important meaning should not depend on image visibility, color, shape, position, or styling alone; text, labels, alt text, and measured contrast should carry the meaning too.

Interpretation notes:
- If color disappears, the reader should still know what the document means.

### claim.creator-writing.inclusive-language-centers-readers: Inclusive Language Centers Readers

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Accessible writing should avoid patronizing, euphemistic, or dehumanizing language and should respect community naming preferences.

Interpretation notes:
- Prefer reader dignity and community self-description over house-style cleverness.

### claim.creator-writing.audience-gap-defines-document: Audience Gap Defines Document

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

A useful document is shaped by what its audience already knows, what they need to learn, and what task or decision the document supports.

Interpretation notes:
- Scope, prerequisites, and key points should appear early enough to orient busy readers.

### claim.creator-writing.error-messages-enable-recovery: Error Messages Enable Recovery

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Error messages should report failures, preserve root cause, identify the cause or invalid input, state relevant constraints, and tell users how to recover.

Interpretation notes:
- Treat error text as recovery writing, not merely notification text.

## Principles

### principle.creator-writing.accessibility-is-writing-quality: Accessibility Is Writing Quality

- Type: principle
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.creator-writing.accessible-docs-benefit-everyone, claim.creator-writing.visual-meaning-needs-nonvisual-support, claim.creator-writing.inclusive-language-centers-readers

Accessibility is part of whether writing works, not a decorative compliance pass after the content is otherwise complete.

Rationale: The accessibility source material applies access principles to docs, comments, UI text, CLI help, error messages, visuals, contrast, and language.

Application notes:
- Check whether meaning survives without color, sight, perfect context, or specialized vocabulary.
- Use measured contrast and useful alt text for visual information.
- Keep inclusive language connected to reader dignity, not only style rules.

## Heuristics

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
