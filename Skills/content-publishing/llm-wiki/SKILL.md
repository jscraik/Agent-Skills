---
name: llm-wiki
description: Create or update an Obsidian-friendly local markdown knowledge base. Use when the user wants LLM-maintained notes, wikilinks/backlinks, frontmatter, citations, local attachments, vault cleanup, or reusable research synthesis.
metadata:
  skill-type: scaffolding_templates
  version: "2.0.0"
---

# LLM Wiki

## Philosophy
Cited local files beat remembered answers.

## When To Use
Use when durable local markdown should change.

## Anti-Patterns
Avoid one-off answers, uncited summaries, and broad vault reorganization.

## Inputs
Confirm domain, vault/workspace path, raw-source path, source sensitivity (`public`, `internal`, `confidential`, or `restricted`), workflow (`ingest`, `query`, `lint`, or `repair`), citation style, attachment path, and whether reusable answers should be filed back into the wiki.

## Discovery Interview
Ask one round at a time: one plain-language question plus `Why this matters:`; avoid dumping the full interview plan at once.

## Constraints
Redact sensitive content by default. Keep raw sources read-only. Preserve citations.

## Execution Boundaries
Write only approved pages, indexes, logs, schemas, governance files, or narrow helpers. Require explicit approval for private attachments, network retrieval, sync/sharing, publishing, vector infrastructure, bulk renames, merges, or reorganization.

## Workflows
Ingest: classify each source, read one source or bounded batch, extract path/page/heading evidence, create or update source summaries, update affected concept/entity/synthesis pages, strengthen wikilinks, then update index and log.

Query: start with index/log and linked pages, read raw sources only when needed, answer with citations, mark uncertainty, and file reusable synthesis back into the wiki when it will compound.

Lint: check contradictions, stale claims, orphan pages, missing concepts, weak links, duplicate aliases, unsupported assertions, brittle attachments, and data gaps. Formal sweeps return `schema_version: lint-report/v1` with severity, evidence, status, and owner.

## Concrete Output Shapes
Use these compact patterns: index rows `- [[concepts/local-first-knowledge]] - claim area`; source summaries with optional frontmatter `type`, `status`, `sources`, `aliases`, `confidence`, `reviewed`, and `supersedes`; citations like `[raw/articles/source.pdf#p4]`; log rows like `2026-05-24: added [[sources/x]], updated [[concepts/y]], no bulk renames`.

Complete ingest example:
```markdown
# wiki/sources/2026-05-24-smith-local-wikis.md
---
type: source-summary
status: active
sources: ["raw/articles/smith-local-wikis.pdf"]
aliases: ["Smith local wikis"]
confidence: medium
reviewed: 2026-05-24
---
## Summary
Local markdown wikis stay auditable when claims cite raw evidence. [raw/articles/smith-local-wikis.pdf#p4]

# wiki/concepts/local-first-knowledge.md
Local-first knowledge keeps raw sources stable while wiki pages evolve through cited updates. See [[sources/2026-05-24-smith-local-wikis]].

# wiki/index.md
- [[concepts/local-first-knowledge]] - local markdown as auditable knowledge base

# wiki/log.md
- 2026-05-24: added [[sources/2026-05-24-smith-local-wikis]] and updated [[concepts/local-first-knowledge]]; no bulk renames.
```

## Update Gates
A wiki update passes when every changed claim has a source citation or explicit uncertainty marker, new wikilinks resolve or are intentional stubs, aliases do not create duplicate identities, attachments stay under the approved local asset path, index/log entries name the change, and no broad rename/reorganization happened. Fail fast: stop at the first failed gate; do not proceed. Optional local checks: `rg -n "\\[\\[[^]]+\\]\\]" wiki/` for wikilinks and `find raw/assets -type f` for attachments.

## Outputs
Return changed pages, index/log updates, lint/schema outputs, privacy/citation status, and command outcomes. Schema-bound outputs include `schema_version`.

## Failure Mode
Fail closed when provenance, sensitivity, citation policy, page ownership, or bulk-reorganization authority is unclear. Report the smallest safe next action.

## Gotchas
Obsidian filenames are identities; preserve them unless a rename is explicit.

## Progressive Disclosure
This file is self-contained for ordinary work. Use `references/` only for multi-user operations, scheduled maintenance, confidence/supersession policy, typed relations, hybrid retrieval, or consolidation.

## Validation
For vault work, run Update Gates plus user-provided checks. For skill edits, run strict audit and the closest smoke/external review. Fail fast: stop at the first failed gate; do not proceed. Report exact pass/fail/blocker outcomes.

## Examples
- User says: "Create an Obsidian vault from raw/articles with source summaries, concept pages, frontmatter, wikilinks, and a log."
- User says: "Audit the team-notes vault for orphan pages, weak links, stale claims, duplicate aliases, and unsupported assertions."
- User says: "The customer-call corpus is confidential and has no redaction policy yet; diagnose the safe next step."
