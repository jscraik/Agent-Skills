# LLM Wiki v2 Production Notes

This reference extends the baseline LLM wiki pattern with production lessons for long-running, high-volume knowledge bases.

## Memory lifecycle model

- Treat knowledge as a lifecycle, not a static page set.
- Score confidence per claim using:
  - number of supporting sources;
  - recency of confirmation;
  - contradictions and unresolved conflicts.
- Support explicit supersession:
  - keep stale claims as historical context;
  - mark them as superseded by newer claims with timestamps and links.
- Apply retention curves:
  - fast decay for transient incidents and stale troubleshooting notes;
  - slow decay for architectural decisions and durable domain models.
- Use consolidation tiers:
  - working memory: fresh, high-volume observations;
  - episodic memory: compressed session summaries;
  - semantic memory: cross-session facts;
  - procedural memory: repeatable playbooks and workflows.

## Knowledge graph overlay

- Keep markdown pages for human-readable context.
- Add structured entities and typed relations for machine navigation.
- Recommended relation verbs:
  - `uses`
  - `depends_on`
  - `caused`
  - `fixed`
  - `contradicts`
  - `supersedes`
- For impact analysis, traverse graph edges from a seed entity before writing conclusions.

## Search beyond flat index

- Keep `index.md` as canonical human catalog.
- At larger scale, combine retrieval channels:
  - BM25/keyword search for exact terms;
  - vector similarity for semantic neighbors;
  - graph traversal for dependency/impact context.
- Fuse rankings via reciprocal rank fusion so one retrieval weakness does not dominate result quality.

## Event-driven automation

- Move repetitive operations to hooks where possible:
  - on new source: ingest + entity extraction + index update;
  - on session start: preload relevant wiki context;
  - on session end: summarize and file learnings;
  - on query: file high-value answers back into durable pages;
  - on schedule: lint, retention decay, and consolidation sweeps.

## Quality and contradiction handling

- Score generated content for structure, citation quality, and policy compliance.
- Use self-healing lint passes for low-risk repairs:
  - broken links;
  - obvious orphaning;
  - stale markers.
- Route contradictions through a deterministic policy:
  - compare source recency;
  - compare source authority;
  - compare corroboration count;
  - escalate uncertain conflicts for human resolution.

## Collaboration and governance

- Separate private and shared knowledge scopes.
- Allow private observations to promote into shared knowledge only with explicit policy.
- Keep an audit trail for ingest/edit/delete/query operations.
- Redact sensitive values on ingest by default:
  - credentials, tokens, keys, PII, and confidential conversation excerpts.

## Crystallization workflow

- Treat completed investigations as first-class sources.
- Distill each completed thread into:
  - initial question;
  - findings and evidence;
  - impacted files/entities;
  - reusable lessons.
- Write crystallized outputs back into the wiki and link to impacted entities and claims.
