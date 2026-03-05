# Progressive doc split patterns

## Table of Contents
- [Purpose](#purpose)
- [Core pattern](#core-pattern)
- [Pattern by document type](#pattern-by-document-type)
  - [README](#readme)
  - [Runbook](#runbook)
  - [Spec or design doc](#spec-or-design-doc)
  - [Operations index](#operations-index)
- [What stays vs what moves](#what-stays-vs-what-moves)
- [Validation checklist](#validation-checklist)

## Purpose
Use this file when the main document feels overloaded. The goal is not more docs; it is faster orientation plus stable detail links.

## Core pattern
1. Keep one front door doc.
2. Make the first screen answer: what is this, who is it for, where do I start?
3. Move deep examples, exhaustive options, edge cases, and volatile details into companion docs.
4. Add a small "read this next" section after each major decision point.
5. Keep link depth shallow: one hop from the front door doc whenever possible.

## Pattern by document type

### README
Keep inline:
- project purpose
- quick start
- top 3 commands
- repo map
- links to deep docs

Move out:
- long troubleshooting
- architecture deep dives
- release notes
- benchmark tables
- full API details

### Runbook
Keep inline:
- incident purpose
- when to use the runbook
- first 3 stabilizing actions
- escalation links

Move out:
- per-service deep procedures
- historical context
- uncommon edge cases
- verbose screenshots

### Spec or design doc
Keep inline:
- problem
- goal
- scope
- decisions
- rollout summary

Move out:
- research appendix
- long alternative analysis
- raw interview notes
- implementation checklists that belong in execution docs

### Operations index
Keep inline:
- system map
- critical paths
- top-level ownership and links

Move out:
- service-specific procedures
- metrics dashboards
- generated reports
- one-off migration notes

## What stays vs what moves
Keep content inline when it is:
- needed by almost every reader
- stable over time
- critical to first action
- short enough to scan quickly

Move content when it is:
- volatile
- highly specific
- long-form reference material
- for a narrower audience
- repeated elsewhere

## Validation checklist
- The top doc is scannable in about two minutes.
- The table of contents matches real headings.
- Commands and paths are verified.
- Links point to existing docs.
- Contradictions are called out, not buried.
- No second docs tree was introduced without a reason.
