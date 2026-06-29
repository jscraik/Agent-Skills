# Technical Documentation

Write proof-backed, skimmable, reader-centered technical docs that reduce search time, parsing effort, setup friction, and unsafe guesswork.

Pack id: pack.developer-advocate-writing
Facet id: technical_documentation
Runtime dependency: none; this slice is generated from a KnowledgeOS pack export.
Lifecycle status: draft

## Claim Cards

### claim.creator-writing.docs-must-be-skimmable: Docs Must Be Skimmable

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Useful documentation should be easy to skim because many readers jump through a document looking for the part that solves their problem.

Interpretation notes:
- Skimmability is not shallow formatting; it is a reader time-saving mechanism.

### claim.creator-writing.docs-should-minimize-parsing-tax: Docs Should Minimize Parsing Tax

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Documentation should reduce the reader's parsing burden with simple, unambiguous, consistent sentences that do not require unnecessary memory juggling.

Interpretation notes:
- Prefer a slightly longer sentence if it removes a parsing hitch.

### claim.creator-writing.docs-should-be-broadly-helpful: Docs Should Be Broadly Helpful

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Documentation should help readers with varied expertise and language comfort by explaining likely blockers, choosing specific accessible terms, prioritizing common needs, and using safe self-contained examples.

Interpretation notes:
- Experts can skim extra help; beginners may abandon a document when expected help is absent.

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

### principle.creator-writing.documentation-is-reader-empathy: Documentation Is Reader Empathy

- Type: principle
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.creator-writing.docs-must-be-skimmable, claim.creator-writing.docs-should-minimize-parsing-tax, claim.creator-writing.docs-should-be-broadly-helpful, claim.creator-writing.audience-gap-defines-document

Good documentation reduces reader search time, parsing effort, setup friction, and unsafe guesswork.

Rationale: The documentation-quality source treats docs as useful information transferred into other people's heads, with empathy as the reason to break or follow writing rules.

Application notes:
- Front-load the point when readers are likely to skim.
- Explain common blockers even when experts already know them.
- Avoid examples that work only in the author's local context or teach unsafe habits.

## Heuristics

### heuristic.creator-writing.front-load-takeaways: Front Load Takeaways

- Type: heuristic
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.creator-writing.docs-must-be-skimmable

Put the most useful takeaway at the start of a document, section, paragraph, title, or table when readers are likely to skim.

Use when:
- The document is long, operational, or used for problem solving.
- A section title could be a useful sentence rather than an abstract noun.
- The opening builds suspense before giving the result.

Avoid when:
- The piece intentionally uses narrative suspense and the reader has opted into that form.

## Checklists

### checklist.creator-writing.documentation-quality-pass: Documentation Quality Pass

- Type: checklist
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.creator-writing.docs-must-be-skimmable, claim.creator-writing.docs-should-minimize-parsing-tax, claim.creator-writing.docs-should-be-broadly-helpful

- [ ] Use informative section titles that help readers decide whether to keep reading.
- [ ] Add a table of contents when the document is long enough to need lookup.
- [ ] Keep paragraphs short enough to skim.
- [ ] Start sections and paragraphs with standalone topic sentences.
- [ ] Put topic words near the beginning of topic sentences.
- [ ] Put important takeaways before supporting buildup.
- [ ] Use bullets and tables when they reduce search time.
- [ ] Remove ambiguous parses, avoid memory-heavy sentence structure, and replace vague demonstrative pronouns.
- [ ] Expand abbreviations or choose more specific terms when beginners might otherwise be blocked.
- [ ] Explain likely setup or usage blockers where omission would stop readers.
- [ ] Keep code examples self-contained, low-dependency, and safe.
- [ ] Prioritize common reader problems over rare edge-case content.

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
