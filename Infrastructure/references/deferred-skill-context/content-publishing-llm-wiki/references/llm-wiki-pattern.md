# LLM Wiki Pattern

This reference documents the operating pattern for building a persistent, LLM-maintained markdown wiki.

## Core idea

Classic RAG repeatedly retrieves and synthesizes from raw documents at query time. The LLM wiki pattern compiles knowledge into persistent markdown pages and continuously updates that corpus as new sources arrive.

## Three-layer architecture

1. Raw sources (immutable):
   - Articles, PDFs, notes, transcripts, images, and datasets.
   - Read-only for provenance and reproducibility.
2. Wiki (mutable, LLM-maintained):
   - Source summaries, entities, concepts, comparisons, synthesis pages.
   - Cross-links and updates are managed by the LLM.
3. Schema (governance contract):
   - `AGENTS.md` or `AGENTS.md` rules for ingest/query/lint behavior.
   - Naming rules, citation requirements, update policy, and safety bounds.

## Core operations

### Ingest

- Accept a new source.
- Extract major claims, entities, and supporting evidence.
- Create/update summary and related concept pages.
- Update `index.md` and append an ingest event to `log.md`.

### Query

- Navigate through `index.md` first, then read relevant pages.
- Synthesize an answer with page-level citations.
- Persist high-value analyses back into wiki pages.
- Append a query event in `log.md` with question scope, pages consulted, and artifacts produced.

### Lint

- Detect contradictions between pages.
- Flag stale claims superseded by newer sources.
- Detect orphan pages and missing cross-links.
- Identify high-frequency concepts lacking dedicated pages.
- Suggest follow-up questions or missing source types.
- Append a lint event in `log.md` with findings severity and follow-up tasks.

## Required control files

- `wiki/index.md`: structured catalog by category with short summaries.
- `wiki/log.md`: chronological append-only operations log.

Recommended log heading format:

```md
## [YYYY-MM-DD] ingest | Source Title
## [YYYY-MM-DD] query | Question Summary
## [YYYY-MM-DD] lint | Health Sweep
```

## Suggested directory layout

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

## Practical scaling notes

- Start with index-driven retrieval at small/medium scale.
- Introduce local search tooling only when navigation friction appears.
- Keep edits incremental and reviewable to preserve trust.

## Human and LLM roles

- Human: curate sources, steer analysis, ask high-value questions.
- LLM: summarize, cross-link, reconcile, and maintain wiki consistency.

## Non-goals

- Replacing primary-source storage with generated summaries.
- Treating generated content as truth without citations.
- Building full retrieval infrastructure before validating the workflow.
