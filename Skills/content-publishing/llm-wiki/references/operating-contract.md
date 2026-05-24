# LLM Wiki Operating Contract

Use this reference before writing wiki pages, schemas, governance, indexes, or
logs. It preserves the source-of-truth, safety, and validation details that the
active skill intentionally keeps compact.

## Required Inputs

- Domain and goal: personal knowledge, research, book companion, team wiki, etc.
- Source corpus path and source formats.
- Sensitivity profile: public, internal, confidential, or highly sensitive.
- Wiki workspace path and whether Obsidian compatibility matters.
- Governance target: `AGENTS.md`, `CLAUDE.md`, `GOVERNANCE.md`, or equivalent.
- Workflow preference: supervised one-source ingest, bounded batch ingest,
  query-first exploration, lint sweep, or restoration of an existing vault.
- Citation style, attachment policy, and whether query outputs should be filed
  back into the wiki by default.

If domain, source path, sensitivity, or governance expectations are missing,
ask direct questions before prescribing concrete file layout or writing pages.

## Architecture Layers

Maintain three separate layers:

- **Raw sources:** immutable source-of-truth files such as articles, PDFs,
  transcripts, notes, images, datasets, or clipped web pages.
- **Wiki:** mutable LLM-maintained markdown pages such as source summaries,
  entities, concepts, comparisons, syntheses, timelines, indexes, and MOCs.
- **Schema/governance:** instructions that tell future agents the page formats,
  naming rules, wikilink conventions, citation rules, privacy policy, and
  ingest/query/lint procedures.

Starter layout:

```text
knowledge-base/
  raw/
    sources/
    assets/
  wiki/
    index.md
    log.md
    entities/
    concepts/
    syntheses/
    sources/
  AGENTS.md
```

## Control Files

- `wiki/index.md` is content-oriented. It catalogs pages by category with a
  link, one-line summary, and useful metadata such as date, status, or source
  count.
- `wiki/log.md` is chronological and append-only. It records ingests, queries,
  lint passes, and high-value maintenance events.
- Use parseable log headings:

```md
## [YYYY-MM-DD] ingest | Source Title
## [YYYY-MM-DD] query | Question Summary
## [YYYY-MM-DD] lint | Health Sweep
```

## Validation Checkpoints

- After source summary writes, verify cited claims can be rechecked against the
  raw source or source summary.
- After downstream page updates, verify affected entity, concept, timeline,
  comparison, and synthesis pages still agree with source evidence.
- After link work, sample wikilinks, backlinks, attachments, and index entries.
- After lint fixes, classify each finding as fixed, needs human judgment,
  blocked, or skipped.
- After any page write, update `wiki/index.md` and append `wiki/log.md` when
  the change is durable.

## Failure Mode

Fail closed and report the smallest safe next action when:

- source provenance is unclear;
- sensitivity or redaction policy is unresolved;
- citation policy is missing;
- the user asks to ingest private media into shared pages without approval;
- bulk reorganization is implied but not explicitly authorized;
- page ownership or sync/collaboration rules are ambiguous.

## Gotchas

- Raw-source, editable wiki, and governance layers must stay separate even when
  they live in one git repo.
- Obsidian uses filenames as identity, so duplicate names and casual renames can
  break links or collaboration expectations.
- Unresolved wikilinks can be useful stubs; do not automatically delete them
  during lint.
- Query results are first-class knowledge artifacts when they synthesize
  multiple pages.
