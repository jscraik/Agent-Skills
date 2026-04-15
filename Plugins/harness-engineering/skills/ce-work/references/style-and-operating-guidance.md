# Style and Operating Guidance

## Table of Contents
- [Purpose](#purpose)
- [Standards snapshot (April 2026)](#standards-snapshot-april-2026)
- [Execution philosophy](#execution-philosophy)
- [Depth variation model](#depth-variation-model)

## Purpose
This reference preserves high-value operating context for execution quality without bloating route-critical flow in `SKILL.md`.

## Standards snapshot (April 2026)
- Keep execution skills scoped to one reusable job with routing-first descriptions.
- Resolve lane, scope, and governing artifacts before code changes.
- Treat validation evidence as a completion requirement, not optional polish.
- Keep repo evidence and local conventions primary; use external docs only when behavior claims depend on current framework/library semantics.
- Preserve valuable context in references instead of deleting it during compaction.

## Execution philosophy
- Start fast, but not blind: restate the execution contract before coding.
- Plans reduce risk; execution proves them against reality.
- Prefer small verified slices over one large unchecked landing.
- Keep worktree and branch hygiene explicit for safe parallelism.
- Carry rollout and operational discipline through implementation, not only planning.

## Depth variation model
Adapt implementation strictness to context while preserving safety gates.

Codebase context:
- Greenfield: default stronger test-first posture.
- Legacy: characterization-first where behavior lock-in is needed before refactor.

Risk level:
- High risk: tighter slices, more explicit cross-boundary validation and rollback checks.
- Low risk: lighter pacing, but no skipping of required verification gates.

Familiarity:
- Familiar pattern: faster execution with standard gates.
- Unknown pattern/domain: increase evidence gathering and validation depth before marking complete.
