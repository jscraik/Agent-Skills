# DevRel Role And Audience

Frame developer advocate and developer relations writing as a two-way community interface with explicit reader benefit, product feedback, role ownership, and business-value boundaries.

Pack id: pack.developer-advocate-writing
Facet id: devrel_role_and_audience
Runtime dependency: none; this slice is generated from a KnowledgeOS pack export.
Lifecycle status: draft

## Claim Cards

### claim.creator-writing.devrel-docs-bridge-community-and-company: DevRel Docs Bridge Community And Company

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

DevRel documentation is a two-way interface: it helps developers succeed while also bringing community evidence back to product, engineering, marketing, and documentation owners.

Interpretation notes:
- Public docs and trust docs should not collapse community usefulness into company messaging.

### claim.creator-writing.devrel-role-boundaries-shape-doc-ownership: DevRel Role Boundaries Shape Doc Ownership

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

DevRel documentation reviews should classify whether the work belongs to technical writing, advocacy, evangelism, program engineering, community organizing, product feedback, or marketing.

Interpretation notes:
- Role classification reduces false fixes where docs are asked to solve product, community, or marketing ownership gaps alone.

### claim.creator-writing.positioning-sets-document-context: Positioning Sets Document Context

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Documentation should set context by naming the category, alternatives, audience, differentiated value, and why-now frame that readers need to interpret the material correctly.

Interpretation notes:
- When docs omit context, readers invent one that may misclassify the product, workflow, or risk.

### claim.creator-writing.user-need-defines-content: User Need Defines Content

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Documentation content should start from reader jobs, vocabulary, mental models, journeys, and likely actions rather than from what the organization wants to publish.

Interpretation notes:
- Treat reader need as evidence to inspect, not a persona label to assert.

### claim.creator-writing.answer-first-structure-supports-review: Answer First Structure Supports Review

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Documents become easier to review when they answer the reader's live question first and then group supporting reasons under that answer.

Interpretation notes:
- Use this for design docs, runbooks, PR explanations, and trust-surface docs that bury the decision or recovery path.

### claim.creator-writing.content-lifecycle-needs-evidence: Content Lifecycle Needs Evidence

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Documentation quality depends on lifecycle evidence: goals, acceptance criteria, prioritization, maintenance cost, and measured reader behavior.

Interpretation notes:
- A doc can be well written and still fail if no owner can maintain or measure it.

## Principles

### principle.creator-writing.devrel-docs-are-community-interface: DevRel Docs Are Community Interface

- Type: principle
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.creator-writing.devrel-docs-bridge-community-and-company, claim.creator-writing.devrel-role-boundaries-shape-doc-ownership

DevRel documentation should be reviewed as a community interface with explicit outbound help, inbound feedback, role ownership, and business-value boundaries.

Rationale: DevRel sources define the work as cross-functional and two-way; docs-expert should preserve that operating shape instead of reducing DevRel docs to marketing copy or static reference.

Application notes:
- Identify which DevRel role owns the document and which roles provide evidence.
- Preserve developer usefulness even when the business goal is conversion, adoption, or retention.
- Route product gaps and feedback-loop gaps outside the doc-only lane when needed.

## Heuristics

### heuristic.creator-writing.route-devrel-feedback: Route DevRel Feedback

- Type: heuristic
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.creator-writing.devrel-docs-bridge-community-and-company, claim.creator-writing.devrel-role-boundaries-shape-doc-ownership

When a docs defect reflects community feedback, product confusion, or role ambiguity, record the doc fix separately from the non-doc owner and feedback loop.

Use when:
- A public doc exposes repeated developer confusion.
- Documentation is being asked to compensate for missing product behavior.
- DevRel, marketing, product, and engineering all touch the same artifact.

Avoid when:
- The defect is a purely local typo or broken path with one obvious owner.

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

## Rubrics

### rubric.creator-writing.docs-expert-capsule-readiness: Docs Expert Capsule Readiness

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

### lens.creator-writing.docs-as-community-interface: Docs As Community Interface

- Type: lens
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.creator-writing.devrel-docs-bridge-community-and-company, claim.creator-writing.user-need-defines-content, claim.creator-writing.content-lifecycle-needs-evidence

- Identify the developer community need and the organization goal as separate lanes.
- Check whether the doc sends useful help out and captures feedback back to an owner.
- Distinguish documentation defects from product behavior, marketing positioning, and DevRel program gaps.
- Prefer evidence from actual reader behavior over internal assumptions about what developers need.
- Treat public trust-surface docs as both reader support and relationship infrastructure.
