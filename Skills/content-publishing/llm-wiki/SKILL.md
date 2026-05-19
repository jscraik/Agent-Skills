---
name: llm-wiki
description: Create or validate a persistent markdown wiki for LLM-managed knowledge. Use this skill when ingest, query, lint, schema, or governance workflows are needed.
metadata:
  skill-type: scaffolding_templates
---

# LLM Wiki

## Philosophy
Knowledge should compound: raw sources stay stable, wiki pages evolve with citations, and governance records how updates happen.

## When To Use
- The user wants a persistent markdown wiki rather than one-off document Q&A.
- A corpus needs raw-source, curated-wiki, and governance layers.
- The work involves ingest, query, lint, citations, contradiction handling, or privacy rules.

## Avoid
- Do not build vector infrastructure first unless explicitly requested.
- Do not process confidential attachments into shared wiki pages before classification and redaction policy.
- Do not bulk reorganize wiki pages without opt-in.

## Inputs
- User request and target repo or artifact.
- Evidence source such as files, diffs, issues, releases, or existing workflow state.
- Any safety, privacy, compliance, or approval constraints.

## Outputs
- Schema-bound outputs include `schema_version`.
- Wiki architecture or update plan.
- Seed files or page updates.
- Privacy, citation, and lint status.

## Workflow
1. Confirm domain, corpus path, sensitivity, workspace path, and governance expectations.
2. Define raw source, editable wiki, and schema/governance layers.
3. Seed or validate `index.md`, `log.md`, and one focused category before expanding.
4. Run privacy classification before ingest and preserve citations.
5. Ingest incrementally and append parseable log entries.
6. Lint for orphan pages, contradictions, stale claims, and unsupported assertions.

## Constraints
- Redact secrets and sensitive source content by default.
- Keep raw sources read-only.
- Do not write confidential media into shared wiki pages without approval.
- Fail fast at the first unresolved privacy or provenance blocker.

## Execution Boundaries
- Write only the requested wiki pages, indexes, logs, or governance files inside the approved corpus workspace.
- Do not ingest private attachments, publish pages, create vector infrastructure, or reorganize the corpus broadly without explicit approval.

## Failure Mode
- If source provenance, sensitivity, citation policy, or lint ownership is unclear, stop with the missing evidence and the smallest safe next action.

## Gotchas
- Raw source capture, editable wiki pages, and governance schema are separate layers.
- Bulk import without privacy classification can turn a useful wiki into an unsafe artifact.

## Validation
- Run Plugin Eval and strict skill audit after editing this skill.
- Report exact validation commands and pass/fail outcomes.
- Fail fast: stop at the first failed gate, fix it, and rerun before continuing.

## Anti-Patterns
- Do not build vector infrastructure first unless explicitly requested.
- Do not process confidential attachments into shared wiki pages before classification and redaction policy.
- Do not bulk reorganize wiki pages without opt-in.

## Examples
- "Set up a markdown wiki for this research folder."
- "The corpus has confidential notes and no redaction policy."

## Progressive Disclosure
- Archived full context: `Infrastructure/references/deferred-skill-context/content-publishing-llm-wiki/`.
- Use `Infrastructure/references/software-literature-expert-lens-pack.md` and `Infrastructure/references/software-literature-skill-expertise-map.md` for knowledge-boundary and source-of-truth lenses.
- Load archived references only when the active workflow needs that exact detail.
- Keep the active path compact; do not remove important context for budget trimming.

## See Also

| Skill | When to use together |
|---|---|
| [[verification-before-completion]] | Confirm gate outcomes and report deterministic pass/fail evidence before closeout |
| [[project-brain]] | Capture durable repo learnings and route updates into the canonical memory surface |
