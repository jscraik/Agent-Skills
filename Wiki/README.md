# Skill Ops Wiki

Structured, compounding wiki workflow for `Agent-Skills` maintenance and operator learning.

## Table of Contents
- [Goal](#goal)
- [Directory Layout](#directory-layout)
- [Page Contract](#page-contract)
- [Operations](#operations)
- [CLI Shortcuts](#cli-shortcuts)
- [Definition of Done](#definition-of-done)

## Goal

The Skill Ops Wiki captures recurring maintenance knowledge so each incident becomes reusable guidance instead of one-off chat context.

## Directory Layout

- `Wiki/skill-ops-wiki/raw/`
- `Wiki/skill-ops-wiki/raw/assets/`
- `Wiki/skill-ops-wiki/wiki/index.md`
- `Wiki/skill-ops-wiki/wiki/log.md`
- `Wiki/skill-ops-wiki/wiki/failures/`
- `Wiki/skill-ops-wiki/wiki/playbooks/`
- `Wiki/skill-ops-wiki/wiki/assets/ui/`
- `Wiki/skill-ops-wiki/wiki/learnings/`

`raw/` is immutable evidence input. `wiki/` is LLM-maintained synthesis.

## Page Contract

Each wiki page under `wiki/failures/`, `wiki/playbooks/`, `wiki/assets/ui/`, and `wiki/learnings/` should include frontmatter:

- `title`: human-friendly title
- `type`: `failure` or `playbook`
- `status`: `active`, `draft`, or `stale`
- `last_reviewed`: ISO date (`YYYY-MM-DD`)
- `sources`: list of repo paths and/or issue/PR URLs

## Operations

1. Ingest
- Add source artifacts to `raw/` when needed.
- Update affected wiki pages.
- Update `wiki/index.md` with links and one-line summaries.
- Append a new entry to `wiki/log.md`.

2. Query
- Start from `wiki/index.md`.
- Read relevant pages.
- Answer with linked citations to wiki pages and source artifacts.
- Persist high-value answers as new pages.

3. Lint
- Run `python3 Infrastructure/scripts/validation-and-linting/wiki_lint.py`.
- Fix missing links, orphan pages, stale review dates, and index gaps.

## CLI Shortcuts

- `ask wiki lint`
- `ask wiki ingest "<title>" --summary "<summary>" --source "<source>"`
- `ask wiki add --interactive` (triage questionnaire: intent, status, destination)
- `ask wiki query "<keywords>"`
- `ask wiki add-asset /path/to/screenshot.png --title "<title>" --summary "<summary>"`

## Definition of Done

A wiki update is complete when:

- Pages are linked from `wiki/index.md`.
- `wiki/log.md` has a dated record.
- `Infrastructure/scripts/validation-and-linting/wiki_lint.py` passes.
- Sources are traceable in page frontmatter.
