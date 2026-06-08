# Compound Learning Migration

Use this reference before deleting, replacing, or validating old
`he-compound` learning behavior. `he-reinforce` is now the owning stage for
solved-problem capture, stale learning refresh, Project Brain sync, and
continuity learning. `he-compound` must not remain an active package or picker
target once these obligations are covered.

## Migrated Responsibilities

| Old compound behavior | `he-reinforce` behavior |
| --- | --- |
| `learning-capture` mode | `capture_solved_problem` mode |
| `full` mode | `capture_depth: full`; helper evidence may be gathered, but only the orchestrator writes |
| `compact-safe` mode | `capture_depth: compact_safe`; only when explicitly requested or context pressure makes full capture wasteful |
| One `docs/solutions/**` artifact | One primary artifact under the repo's canonical learning surface; default `.harness/solutions/**`, or `docs/solutions/**` only when repo instructions declare it canonical |
| Auto memory scan | Optional secondary evidence only; never primary repo truth |
| Related Docs Finder | Overlap search across `.harness/solutions/**`, Project Brain surfaces, and legacy `docs/solutions/**` |
| High/moderate/low overlap | `overlap_decision: high_update_existing`, `moderate_create_and_flag_refresh`, `low_create_new`, or `blocked` |
| Project Brain follow-up | Integrated `project_brain_status` with explicit classification or blocker |
| Local Memory MCP sync | `local_memory_indexing_status`; indexing failure is reported separately from artifact success |
| Schema-driven compound-docs variant | `legacy_docs_solution_status` plus schema/frontmatter validation when the target repo still requires structured `docs/solutions/**` |

## Capture Depth

Default to `full` when the solved problem is non-trivial and context is
available. Full capture may gather helper-style evidence for context, root
cause, related docs, prevention strategy, category/path selection, and optional
session history, but helpers return text only. They do not write drafts or
intermediate solution files.

Use `compact_safe` only when the user explicitly asks for compact mode or the
session is constrained enough that full capture would add more cost than
retrieval value. Compact-safe still requires solved proof, root cause,
validation or blocker, overlap awareness, redaction, and one complete primary
artifact or a blocked status.

## Evidence Order

Prefer source, diff, validation, tracker, and repo instruction evidence.
Auto-memory, session summaries, pasted chat, and generated summaries are
supplementary context only. If supplementary memory contradicts verified repo
evidence, treat it as cautionary context and do not encode it as fact.

## Overlap Decisions

- `high_update_existing`: same problem, root cause, solution, or prevention
  rule. Update the existing artifact instead of creating a duplicate.
- `moderate_create_and_flag_refresh`: same area but a different angle. Create
  the new artifact only if it adds retrieval value, then flag a narrow refresh
  or consolidation follow-up.
- `low_create_new`: related but distinct. Create a new artifact when solved
  proof and prevention value exist.
- `blocked`: overlap cannot be assessed because canonical learning surfaces,
  permissions, or evidence are missing.

## Project Brain And Indexing

When Project Brain is active, route stable facts into the correct surface:
`.harness/knowledge/**`, `.harness/decisions/**`, `.harness/rules/**`, or
`.harness/memory/LEARNINGS.md`. If the classification is unclear, block rather
than guessing.

Report Local Memory or indexing separately. A learning artifact can be written
while indexing is `blocked`, but the final status must make that blocker
visible and must not imply Project Brain is complete.

Promotion guidance from the old compound lane still applies as policy, not
automatic mutation:

- first verified occurrence: knowledge candidate
- repeated confirmed occurrence: update existing knowledge and count evidence
- third confirmed occurrence: rule candidate, requiring explicit classification
- contradicted guidance: hypothesis or stale-note candidate, not active rule

## Schema-Driven docs/solutions

Use `docs/solutions/**` as the primary write target only when the target repo's
instructions declare that surface canonical. When it is canonical, preserve the
old compound-docs discipline:

- validate YAML/frontmatter expectations before writing
- preserve path-safe filenames and category semantics
- update high-overlap existing docs instead of creating duplicates
- report `legacy_docs_solution_status`
- block when schema expectations, canonical category, or write authority are
  unclear

In this repository, new HE solution captures default to `.harness/solutions/**`.
Legacy `docs/solutions/**` remains source evidence unless a repo-specific
instruction overrides that default.

## Removal Gate For he-compound

Before removing the obsolete `he-compound` package, prove:

- `he-reinforce` references this migration contract
- `contract.yaml` includes capture depth, overlap decision, legacy docs status,
  Project Brain status, and Local Memory indexing status
- `evals.yaml` contains cases for old compound full capture and schema-driven
  `docs/solutions` preservation
- command-surface handles and picker projection resolve `he-reinforce`, not
  `he-compound`
- lifecycle routing docs describe `he-compound` as removed/replaced, not as a
  compatibility skill
