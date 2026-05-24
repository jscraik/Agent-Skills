# Discovery interview

## When to use this reference

Use this when an LLM Wiki request is promising but underspecified:

- the user wants a wiki restored, built, or migrated but has not named the source corpus;
- the privacy/redaction policy is unclear;
- Obsidian compatibility is implied but not explicit;
- the user has not said whether the next move is ingest, query, lint, or architecture repair.

## How to run the interview

Default behavior:

- ask one round at a time;
- start with one plain-language question;
- add one short `Why this matters:` line;
- avoid dumping the full interview plan at once;
- stop once vault root, raw sources, privacy rules, browsing surface, and first workflow are clear enough to act safely.

## Request user input mini-templates

Intuitive round-1 question:
- `What should this skill help you do?`
- `What folder should be the wiki root, and where are the raw sources I should treat as source of truth?`

### Round 1 template: source and boundaries

Chat intro:
- `Let's pin down the source boundary first.`

Good tool question shape:
- `Header:` `Source`
- `Question:` `Which source boundary should the LLM Wiki use first?`
- `Options:`
  - `Existing vault (Recommended)` - Best when Obsidian pages already exist and need restoration or linting.
  - `Raw corpus` - Best when the wiki should be created from source articles, transcripts, PDFs, or notes.
  - `Mixed vault and corpus` - Best when existing pages and raw sources both need reconciliation.

Follow-up prompt if needed:
- `What privacy or redaction rule should I apply before creating or updating pages?`

### Round 2 template: Obsidian behavior

Chat intro:
- `Next I need to know how human browsing should work.`

Good tool question shape:
- `Header:` `Browse`
- `Question:` `How should the wiki be browsed after the LLM updates it?`
- `Options:`
  - `Obsidian (Recommended)` - Use wikilinks, backlinks, local graph, attachments, and YAML frontmatter.
  - `Git markdown` - Keep simple markdown pages and logs without Obsidian-specific conventions.
  - `Static export` - Optimize page structure for generated documentation or publishing.

## Copy paste payload examples

### Round 1 example

```json
{
  "questions": [
    {
      "header": "Source",
      "id": "wiki_source_boundary",
      "question": "Which source boundary should the LLM Wiki use first?",
      "options": [
        {
          "label": "Existing vault (Recommended)",
          "description": "Best when Obsidian pages already exist and need restoration or linting."
        },
        {
          "label": "Raw corpus",
          "description": "Best when the wiki should be created from source articles, transcripts, PDFs, or notes."
        },
        {
          "label": "Mixed vault and corpus",
          "description": "Best when existing pages and raw sources both need reconciliation."
        }
      ]
    }
  ]
}
```

Suggested follow-up in chat:
- `What should this wiki help you do every week: ingest new sources, answer questions, surface contradictions, or maintain graph health?`

## Round 1: Source boundary

**Why this matters:** LLM Wikis break down when generated pages, raw sources, and human notes blur together.

Ask:
- Which folder is the wiki or vault root?
- Which folder contains raw sources?
- Are any sources private, confidential, or unredacted?
- Should unresolved wikilinks create useful stubs or be treated as lint findings?

Friendly opener:
- `What folder should be the wiki root, and where are the raw sources I should treat as source of truth?`

## Round 2: Browsing and workflow

**Why this matters:** Obsidian-friendly structure changes page names, links, attachments, frontmatter, and graph-health checks.

Ask:
- Will the human browse the result in Obsidian?
- Should the first workflow be ingest, query, lint, or architecture restoration?
- Should high-value query syntheses be filed back into the wiki by default?

Friendly opener:
- `Should I optimize this for Obsidian browsing, git-first markdown, or a static/published surface?`

## Confirmation

**Why this matters:** a small confirmation catches source-boundary and privacy mistakes before the LLM edits a durable knowledge base.

Summarize:
- wiki root and raw-source root;
- privacy/redaction rules;
- Obsidian compatibility target;
- first workflow;
- validation plan;
- open assumptions.

End with one compact confirmation question:
- `Does this capture the LLM Wiki shape well enough for me to implement?`
- `Anything to add or change before I update the wiki?`
