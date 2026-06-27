---
type: moc
name: product-strategy
description: "Skills for product thinking, spec writing, user research, ideation, and project improvement — covering the full arc from idea to implementation-ready brief."
covers:
  - product-planning
  - spec-writing
  - user-research
  - ideation
  - project-analysis
---

# Product Strategy

> Skills for product thinking, spec writing, user research, ideation, and project improvement.

## Table of Contents
- [Ideation & Exploration](#ideation--exploration)
- [Specification & Planning](#specification--planning)
- [Research & Interviews](#research--interviews)
- [Knowledge Systems](#knowledge-systems)
- [Project Improvement](#project-improvement)

---

## Ideation & Exploration

- [[he-brainstorm]] — Pre-planning exploration for ambiguous requests: clarify what to build, compare 2-3 approaches, recommend a direction.

## Specification & Planning

- [[he-plan]] — Create execution-ready implementation plans with sequencing, validation, and rollout guidance.
- [[architecture-interview]] — Plan and review architecture decisions via structured interview with ADR output.
- [[chatgpt-apps]] — Design and implement ChatGPT Apps SDK workflows (tool + UI architecture, CSP, metadata, bridge wiring).

## Research & Interviews

- [[interview-me]] — Interactive, multiple-choice interview for requirements discovery; turns underspecified ideas into execution-ready specs.
- [[deep-interview]] — Deep, gap-filling interview that enhances existing docs/specs or explores a topic; updates docs in-place with insights and an approval gate.
- [[context7]] — Extract current library documentation via Context7 for up-to-date API details and versioning.

## Knowledge Systems

- [[technical-writer]] — Keep strategy docs, runbooks, and README surfaces aligned with live behavior.
- [[llm-wiki]] — Persist strategy knowledge in a queryable markdown wiki with incremental updates.

---

## Pipelines

- New feature idea → [[he-brainstorm]] → [[interview-me]] → [[architecture-interview]] → [[he-plan]].
- Improve existing project → [[deep-interview]] → [[architecture-interview]] → [[he-plan]].
- Research and document → [[context7]] / [[llm-wiki]] → [[technical-writer]].

## Cross-links

- Ready to build? Hand off to [[agent-ops]] (skill/automation), [[frontend-ui]] (UI), or [[backend-platform]] (API/infra).
- Need security analysis? Hand off to [[security-ops]].
- Topic maps: [[frontend-ui]] | [[backend-platform]] | [[agent-ops]] | [[security-ops]] | [[content-publishing]]
