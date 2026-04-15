---
name: llm-wiki
description: "Create and maintain an LLM-managed markdown wiki that incrementally compiles source material into a persistent, queryable knowledge base; use this skill when users ask for persistent wiki architecture, ingest/query/lint workflows, or schema governance."
metadata:
  skill-type: scaffolding_templates
  lifecycle_state: incubating
  maturity: experimental
  owner: agent-skills
  review_cadence: monthly
  last_reviewed: 2026-04-13
  metadata_source: frontmatter
---

# LLM Wiki

Build and maintain a persistent, LLM-written markdown wiki that compounds knowledge over time instead of re-deriving it from raw sources on every query.

## When to use

- Use this skill when the user wants to set up or improve a "persistent wiki" workflow for personal research, team knowledge, course notes, due diligence, or similar long-running analysis.
- Use this skill when the user wants schema guidance (`AGENTS.md`/`CLAUDE.md` conventions), ingest/query/lint routines, or file layout for an LLM-maintained knowledge base.
- Use this skill when the user wants to convert a pile of documents into a curated, interlinked markdown knowledge system.
- Do not use this skill for one-off Q&A over a small static document set; route to normal summarization/research workflows.
- Do not use this skill when the user wants vector-database infrastructure first; route to backend/search implementation lanes.

## Required inputs

- User goal and domain: personal knowledge, team wiki, research project, etc.
- Source corpus location and format expectations.
- Source sensitivity profile: public, internal, confidential, or highly sensitive.
- Preferred wiki workspace path and repository layout.
- Operational preferences: supervised ingest vs batch ingest, citation style, and lint cadence.
- Mixed-media handling preference: text-only or text plus image/attachment review.
- Existing governance docs if present (`AGENTS.md`, `CLAUDE.md`, runbooks).
- If domain, source path, or governance expectations are missing, ask direct clarifying questions before prescribing concrete file layout or command steps.

## Deliverables

- A recommended 3-layer architecture:
  - immutable raw source layer
  - editable LLM-maintained wiki layer
  - explicit schema/governance layer
- Concrete ingest/query/lint playbook with command-level or step-level procedures.
- Initial seed files (`index.md`, `log.md`, and category pages) or upgrade guidance for existing wikis.
- Append-only, parseable `log.md` event format guidance (for example `## [YYYY-MM-DD] <kind> | <summary>`, where `<kind>` is `ingest`, `query`, or `lint`).
- Risk notes (contradictions, stale claims, orphan pages, unsupported assertions) and mitigation workflow.
- Include `schema_version` in schema-bound output contracts.
- A privacy-controls plan covering classification, minimization, and redaction rules for sensitive corpora.
- When requested, an advanced operating profile that includes lifecycle controls (confidence, supersession, retention), typed knowledge graph expectations, hybrid search strategy, event hooks, and quality/self-healing controls.

## Failure mode

- Stale-source drift: wiki pages diverge from raw source intent when ingest cadence outruns review cadence.
- Citation erosion: claims lose traceable provenance when edits skip source anchors.
- Structure debt: index and category pages fall out of sync, making high-value pages undiscoverable.
- Contradiction accumulation: overlapping pages evolve independently and begin to disagree.
- Over-automation: unsupervised batch ingest introduces low-signal pages and noisy links.
- Privacy spill: sensitive source fragments are copied verbatim into public or broad-access wiki pages.

## Constraints and safety

- Preserve source-of-truth discipline: raw sources are read-only.
- Require citation-backed updates when modifying existing wiki claims.
- Redact sensitive data in wiki output by default.
- Run a pre-ingest privacy gate for sensitive sources (health notes, meeting transcripts, customer calls):
  - classify corpus sensitivity before processing;
  - define minimization/redaction policy before writing wiki pages;
  - avoid verbatim confidential excerpts unless explicitly approved.
- Prefer local/offline workflows unless the user explicitly asks for network retrieval.
- For mixed-media corpora, process markdown text first and inspect referenced images selectively with explicit purpose.
- Never process confidential media attachments into shared wiki pages until classification and redaction policy are confirmed.
- Treat destructive reorganization (bulk delete/rename) as opt-in and require confirmation.

## Principles

- Compounding over retrieval: synthesize once, maintain continuously.
- File useful answers back into the wiki as durable pages.
- Keep navigation explicit with strong linking, index hygiene, and chronological logs.
- Separate configuration policy (schema) from content pages.

## Advanced extension (v2)

- Add lifecycle semantics when the wiki must remain accurate at scale:
  - confidence scoring per claim with support/recency/contradiction signals;
  - explicit supersession links for stale claims;
  - retention decay and consolidation tiers (working, episodic, semantic, procedural).
- Add structural semantics when flat pages are insufficient:
  - entity extraction with typed attributes;
  - typed relations (example, non-exhaustive): `uses`, `depends_on`, `caused`, `fixed`, `contradicts`, `supersedes`;
  - graph traversal for impact analysis.
- Add retrieval semantics when `index.md` no longer scales:
  - combine keyword (BM25), vector similarity, and graph traversal;
  - fuse candidate rankings with reciprocal rank fusion.
- Add event automation and quality governance:
  - hooks for ingest/session-start/session-end/query/scheduled lint;
  - contradiction resolution policy and self-healing lint behavior;
  - shared/private scope boundaries for multi-agent collaboration.

## Workflow

1. Confirm required inputs:
   - Ask direct clarifying questions when domain, corpus path, sensitivity profile, or governance context is missing.
   - Defer prescriptive folder/file recommendations until missing required inputs are answered.
2. Model the workspace:
   - Keep first pass tight: start with 2-3 focused surfaces (`index.md`, `log.md`, and one category folder) before broad expansion.
   - Confirm `raw/`, `wiki/`, and `schema` ownership boundaries.
   - Create or validate `wiki/index.md` and `wiki/log.md`.
   - Keep `index.md` entries structured as link + one-line summary (optional metadata such as date or source count).
3. Define schema rules:
   - Capture ingest/query/lint procedures in `AGENTS.md` or `CLAUDE.md`.
   - Specify citation, page naming, and cross-linking conventions.
   - If operating at scale, define lifecycle controls (confidence/supersession/retention), typed relations, and contradiction-resolution policy.
4. Run privacy gate before ingest:
   - Classify source sensitivity and decide whether to redact, summarize, or block sensitive details.
   - For mixed-media inputs, define text-first processing and selective image-review criteria.
   - Record privacy decisions in governance notes so behavior is consistent across sessions.
5. Ingest sources incrementally:
   - Read one source (or a bounded batch).
   - Create/update source summary page.
   - Update affected entity/concept/synthesis pages.
   - Append an ingest event to `log.md` with parseable heading format: `## [YYYY-MM-DD] ingest | source`.
6. Query and compound:
   - Start from `index.md` to locate relevant pages.
   - Synthesize an answer with citations.
   - For impact-oriented questions, prefer graph traversal over keyword-only lookup.
   - Persist high-value outputs back into wiki pages.
   - Append a query event to `log.md` with parseable heading format: `## [YYYY-MM-DD] query | scope`.
7. Lint regularly:
   - Check contradictions, stale claims, orphan pages, missing concepts, and weak cross-links.
   - Resolve contradictions with recency + source-support + authority weighting, with human override.
   - Create follow-up questions and source-acquisition suggestions.
   - Append a lint event to `log.md` with parseable heading format: `## [YYYY-MM-DD] lint | focus`.

Detailed guidance: `Infrastructure/references/llm-wiki-pattern.md` and `Infrastructure/references/llm-wiki-v2-production-notes.md`.

## Validation

- `python3 Plugins/skill-factory/skills/skill-creator/Infrastructure/scripts/quick_validate.py product/docs/llm-wiki`
- `./bin/ask skills audit product/docs/llm-wiki --level strict --robot`
- `python3 Plugins/skill-factory/skills/skill-builder/Infrastructure/scripts/run_skill_evals.py product/docs/llm-wiki --eval-mode smoke --runner codex --timeout-profile codex-heavy --format text`
- `python3 Plugins/skill-factory/skills/skill-builder/Infrastructure/scripts/run_skill_evals.py product/docs/llm-wiki --eval-mode release --runner codex --timeout-profile codex-heavy --format text`
- If eval runner execution is unavailable (timeouts/auth/tooling), record the step as blocked and include scorecard/report paths plus blocker text.
- Fail fast: stop on first failing gate, fix, and rerun the full validation set.

## Gotchas

- Leaving `log.md` ingest-only causes provenance drift; log query and lint events too.
- Free-form `log.md` headings break timeline parsing; keep append-only `## [YYYY-MM-DD] kind | summary` entries.
- Treating privacy gates as optional leads to sensitive-detail leakage in shared wiki pages.
- Skipping clarification on missing domain/path/governance inputs causes brittle or mis-scoped layouts.

## Anti-patterns

- Treating the wiki as static output from a single ingest pass.
- Skipping `index.md` maintenance and relying on memory-only navigation.
- Leaving query insights in chat history instead of writing durable pages.
- Allowing raw-source edits that blur provenance.
- Running unsupervised large ingest without post-ingest lint.
- Prescribing concrete folder/file operations before collecting missing domain, path, sensitivity, and governance inputs.
- Copying confidential text or media verbatim into shared wiki pages without a redaction policy.

## Examples

- "Set up an LLM wiki for my AI safety reading backlog with ingest and weekly lint workflows."
- "Convert this folder of policy PDFs into a persistent wiki with entity pages and a thesis page."
- "Design schema rules for a team wiki where meeting transcripts are ingested daily."

## See Also

| Skill | When to use |
|---|---|
| [[docs-expert]] | Improve surrounding repository docs and runbooks once the workflow is chosen. |
| [[project-brain]] | Operate project memory systems when the ask is broader than a single wiki pattern. |
| [[context7]] | Pull current external API/library docs to enrich wiki source material. |

**Topic map:** [[knowledge-ops]]

## References and assets

- Pattern primer and operating model: `Infrastructure/references/llm-wiki-pattern.md`
- Machine-checkable contract: `Infrastructure/references/contract.yaml`
- Behavioral eval coverage: `Infrastructure/references/evals.yaml`
- OpenAI Apps metadata: `agents/openai.yaml`
