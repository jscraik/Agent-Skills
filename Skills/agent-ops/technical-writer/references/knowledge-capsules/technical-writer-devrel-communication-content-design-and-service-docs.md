# Content Design And Service Docs

Treat docs and help content as maintained service interfaces shaped by reader jobs, evidence, vocabulary, acceptance criteria, and lifecycle cost.

Pack id: pack.developer-advocate-writing
Facet id: content_design_and_service_docs
Runtime dependency: none; this slice is generated from a KnowledgeOS pack export.
Lifecycle status: draft

## Claim Cards

### claim.creator-writing.user-need-defines-content: User Need Defines Content

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Documentation content should start from reader jobs, vocabulary, mental models, journeys, and likely actions rather than from what the organization wants to publish.

Interpretation notes:
- Treat reader need as evidence to inspect, not a persona label to assert.

### claim.creator-writing.content-lifecycle-needs-evidence: Content Lifecycle Needs Evidence

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Documentation quality depends on lifecycle evidence: goals, acceptance criteria, prioritization, maintenance cost, and measured reader behavior.

Interpretation notes:
- A doc can be well written and still fail if no owner can maintain or measure it.

### claim.creator-writing.clear-writing-requires-revision: Clear Writing Requires Revision

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Clear documentation requires revision passes that remove clutter, expose fuzzy thinking, and check whether the text says what the writer means.

Interpretation notes:
- Treat unclear prose as a thinking or evidence problem before treating it as tone polish.

### claim.creator-writing.answer-first-structure-supports-review: Answer First Structure Supports Review

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Documents become easier to review when they answer the reader's live question first and then group supporting reasons under that answer.

Interpretation notes:
- Use this for design docs, runbooks, PR explanations, and trust-surface docs that bury the decision or recovery path.

### claim.creator-writing.devrel-docs-bridge-community-and-company: DevRel Docs Bridge Community And Company

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

DevRel documentation is a two-way interface: it helps developers succeed while also bringing community evidence back to product, engineering, marketing, and documentation owners.

Interpretation notes:
- Public docs and trust docs should not collapse community usefulness into company messaging.

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

### principle.creator-writing.docs-are-service-interface: Docs Are Service Interface

- Type: principle
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.creator-writing.user-need-defines-content, claim.creator-writing.content-lifecycle-needs-evidence

Treat documentation as a service interface whose quality is proven by reader need, successful action, and maintainable lifecycle evidence.

Rationale: Content design connects words to user journeys, evidence, acceptance criteria, and maintenance cost, so technical-writer should review operational usefulness before prose polish.

Application notes:
- Start audits by identifying the reader job and the evidence that this job exists.
- Check whether the document has an owner, update path, and measurable success condition.
- Prefer fewer maintained documents over more stale surfaces.

## Heuristics

### heuristic.creator-writing.start-from-reader-job: Start From Reader Job

- Type: heuristic
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.creator-writing.user-need-defines-content

Before rewriting a document, name the reader job, decision, vocabulary, evidence source, and success condition it serves.

Use when:
- A document feels accurate but mis-scoped.
- The audience is described only as a broad persona.
- The doc mixes organization messaging with reader tasks.

Avoid when:
- A legal, compliance, or template owner has fixed the exact wording and only evidence annotation is possible.

## Checklists

### checklist.creator-writing.content-design-service-docs-pass: Content Design Service Docs Pass

- Type: checklist
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.creator-writing.user-need-defines-content, claim.creator-writing.content-lifecycle-needs-evidence, claim.creator-writing.clear-writing-requires-revision

- [ ] Name the reader job or decision the document supports.
- [ ] Cite the evidence source for that reader need, such as analytics, support tickets, forums, research, or repeated review feedback.
- [ ] Put the most common reader need first while keeping less common needs findable.
- [ ] Check that vocabulary matches the terms readers use when searching or asking for help.
- [ ] Define acceptance criteria for the document's useful outcome.
- [ ] Identify the maintainer and update trigger.
- [ ] Separate content strategy, product gap, and prose fix responsibilities.
- [ ] Run a revision pass for clutter after structure and evidence are correct.

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
