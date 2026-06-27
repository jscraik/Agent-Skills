# Downstream Skill Routing

Route creator-writing output to technical-writer for proof-backed documentation work and x-content-writer for Jamie-style X content while preserving source and publication boundaries.

Pack id: pack.creator-writing
Facet id: downstream_skill_routing
Runtime dependency: none; this slice is generated from a KnowledgeOS pack export.
Lifecycle status: draft

## Claim Cards

### claim.creator-writing.docs-expert-fits-proof-backed-docs: Technical Writer Fits Proof Backed Docs

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Docs-expert is the best downstream skill when the writing task is a proof-backed documentation audit, rewrite, or validation against live repository evidence.

Interpretation notes:
- Use technical-writer when accuracy against repo truth is the job, not when the output is mainly public social copy.

### claim.creator-writing.x-content-writer-fits-public-x-content: X Content Writer Fits Public X Content

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

X-writer's x-content-writer skill is the best local skill for Jamie-style X.com content tied to OpenAI, Codex, project updates, expertise capture, Articles, threads, proof clips, and visuals.

Interpretation notes:
- This is a draft and packaging skill, not permission to publish or mutate X.com.

### claim.creator-writing.x-writer-separates-creative-and-trust-loops: X-writer Separates Creative And Trust Loops

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

X-writer separates rough creative drafting from trust, proof, packaging, export, and metrics work, and stops before automated X.com publication.

Interpretation notes:
- Do not demand claim cards from fragments, but require proof before publishable packages.

### claim.creator-writing.communication-corpus-supports-specialized-passes: Communication Corpus Supports Specialized Passes

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

The local X-writer communication book corpus can support specialized writing passes for content design, stickiness, plain prose, analytical reading, pyramid reasoning, positioning, explanation, and public work-sharing.

Interpretation notes:
- Treat the corpus as a source queue unless a specific book has been inspected and extracted.

## Principles

### principle.creator-writing.route-by-reader-job-and-proof: Route By Reader Job And Proof

- Type: principle
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.creator-writing.docs-expert-fits-proof-backed-docs, claim.creator-writing.x-content-writer-fits-public-x-content, claim.creator-writing.x-writer-separates-creative-and-trust-loops

Choose the downstream writing skill by the reader job and proof requirement: technical-writer for repo-truth documentation, x-content-writer for public X content, and both when evidence-backed work becomes public copy.

Rationale: The inspected skill and repo guidance separate proof-backed documentation correction from X.com content drafting and publication-boundary packaging.

Application notes:
- Start with technical-writer when commands, paths, configs, or validation claims can be stale.
- Move to x-content-writer when the artifact becomes an X post, thread, Article, visual, or handoff.
- Preserve the proof boundary when translating docs evidence into public content.

## Heuristics

### heuristic.creator-writing.docs-to-x-routing: Docs To X Routing

- Type: heuristic
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.creator-writing.docs-expert-fits-proof-backed-docs, claim.creator-writing.x-content-writer-fits-public-x-content, claim.creator-writing.x-writer-separates-creative-and-trust-loops

If the artifact must be accurate against repo truth, start with technical-writer; if it must become Jamie-style X content, hand the proof-shaped material to x-content-writer.

Use when:
- A README, runbook, skill doc, or trust-surface doc might feed public content.
- A technical result needs both validation proof and public framing.
- A draft risks mixing rough creative material with publishable claim authority.

Avoid when:
- The task is purely private ideation with no repo-truth or public-content output.

## Checklists

### checklist.creator-writing.skill-routing-pass: Skill Routing Pass

- Type: checklist
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.creator-writing.docs-expert-fits-proof-backed-docs, claim.creator-writing.x-content-writer-fits-public-x-content, claim.creator-writing.x-writer-separates-creative-and-trust-loops, claim.creator-writing.communication-corpus-supports-specialized-passes

- [ ] Identify whether the reader job is documentation correction, public content drafting, or both.
- [ ] Use technical-writer when the task needs live repo evidence, command/path checks, or documentation validation.
- [ ] Use x-content-writer when the task needs Jamie-style X posts, threads, Articles, proof clips, visuals, or content packaging.
- [ ] Keep X-writer draft and package work inside the operator publish boundary.
- [ ] Keep Writing Lab rough material separate from Publication Lab claim authority.
- [ ] Select the communication book/source lane only after naming the writing pass it should improve.
- [ ] Mark unread or unextracted book sources as source inventory, not evidence for detailed claims.
