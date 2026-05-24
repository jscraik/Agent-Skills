# Obsidian Vault Contract

Use this reference when an LLM Wiki will be browsed or maintained as an
Obsidian vault. Keep the contract local to the vault in `AGENTS.md`,
`GOVERNANCE.md`, or an equivalent control file before broad ingest.

## Page Types

- `source-summary`: one page per raw source, citing the immutable source path.
- `entity`: people, organizations, projects, tools, places, or named systems.
- `concept`: reusable ideas, patterns, principles, terms, or open questions.
- `synthesis`: cross-source conclusions, comparisons, timelines, and decisions.
- `index`: curated navigation pages, maps of content, and starting points.
- `log`: append-only maintenance, ingest, query, and lint events.

## Optional Frontmatter

Use frontmatter only when it powers navigation, review, Dataview, automation, or
validation. Do not add decorative metadata.

```yaml
type: concept
status: draft
sources:
  - "[[sources/source-title]]"
aliases:
  - Alternate Name
confidence: medium
reviewed: 2026-05-24
supersedes:
  - "[[older-page]]"
```

Allowed values should stay small and explicit:

- `type`: `source-summary`, `entity`, `concept`, `synthesis`, `index`, `log`
- `status`: `seed`, `draft`, `reviewed`, `needs-source`, `superseded`
- `confidence`: `low`, `medium`, `high`, `contested`

## Page Templates

### Source Summary

```md
---
type: source-summary
status: draft
sources:
  - raw/sources/source-file.ext
---

# Source Title

## Source
- Path: `raw/sources/source-file.ext`
- Provenance:
- Sensitivity:

## Claims
- Claim with citation to source location.

## Entities and Concepts
- [[Entity Name]]
- [[Concept Name]]

## Follow-ups
- Open question or missing source.
```

### Concept or Entity

```md
---
type: concept
status: draft
aliases: []
confidence: medium
---

# Concept Name

## Summary
One durable paragraph.

## Evidence
- Claim, with citation to source summary or raw source.

## Links
- Related: [[Related Concept]]
- Contrasts: [[Different Concept]]

## Open Questions
- Question that needs more evidence.
```

### Synthesis

```md
---
type: synthesis
status: draft
confidence: medium
sources: []
---

# Synthesis Title

## Question
The question this synthesis answers.

## Answer
The reusable conclusion.

## Evidence
- Cited evidence from multiple pages or raw sources.

## Implications
- How this changes future navigation, ingest, or decisions.
```

## Naming And Alias Policy

- Prefer stable, human-readable filenames that match the canonical page title.
- Add aliases for common alternate names instead of renaming pages casually.
- Before renaming or merging pages, check backlinks, embeds, aliases, and git
  history; bulk rename or merge work requires explicit user approval.
- Treat duplicate filenames, near-duplicate titles, and alias collisions as lint
  findings before making changes.
- Use unresolved wikilinks only for important pages that should exist soon; do
  not create large forests of low-signal stubs.

## Graph And Link Health

- Prefer wiki-internal Obsidian wikilinks for durable concepts:
  `[[Concept Name]]`.
- Use heading or block links only when exact context matters more than page-level
  navigation.
- Treat backlinks and local graph as health and discovery surfaces: they reveal
  isolated concepts, over-central pages, duplicates, and useful clusters.
- Treat full graph view as a comprehension surface; day-to-day navigation should
  still work through local graph, backlinks, search, and index pages.

## Citation Syntax

- Cite source-summary pages when they accurately point back to raw material.
- Cite raw source paths when the claim depends on exact wording, an attachment,
  or uncompressed evidence.
- Preserve enough location detail for re-checking: heading, page number,
  timestamp, line number, or quoted snippet when available.
- Mark unsupported assertions as `status: needs-source` or as lint findings
  instead of smoothing over missing evidence.

## Attachments

- Keep local copies under `raw/assets/` or a vault-approved equivalent.
- Use relative markdown links or Obsidian embeds only after confirming the asset
  is local and intentionally part of the vault.
- Treat external-only images, PDFs, and videos as brittle attachment findings
  unless the user wants external dependency tracking.

## Done Criteria

- Raw sources, wiki pages, and governance remain separate.
- Index and log are updated for the operation.
- New or changed claims have citations or are marked as needing sources.
- Wikilinks improve navigation without destructive renames.
- Sensitive material follows the vault redaction policy.
