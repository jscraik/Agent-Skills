# CE Work Anti-Patterns

## Table of Contents
- [Purpose](#purpose)
- [Detection and correction loop](#detection-and-correction-loop)
- [Anti-pattern catalog](#anti-pattern-catalog)

## Purpose
This reference captures execution-stage anti-patterns so `he-work` can detect and correct them consistently before handoff.

## Detection and correction loop
1. Detect from evidence.
2. Correct before marking task complete.
3. If not fully correctable in-turn, record a bounded blocker and safe next step.

## Anti-pattern catalog

### Raw spec execution without planning
Signals:
- multi-phase, migration-heavy, or cross-cutting raw spec executed directly.

Correction:
- route to `he-plan` first,
- resume implementation only after plan-level execution structure exists.

### Parallel work on overlapping files
Signals:
- delegated or parallel slices modify same file regions,
- merge conflicts or repeated regressions appear.

Correction:
- collapse to serial execution,
- re-slice by non-overlapping boundaries.

### No validation evidence
Signals:
- task marked complete without test/lint/type/integration evidence,
- handoff claims completion with no trace.

Correction:
- run required gates,
- attach evidence before completion.

### Contract drift ignored
Signals:
- implementation behavior diverges from plan/spec,
- artifact status/checklists no longer match shipped behavior.

Correction:
- pause coding,
- update governing artifact before continuing.

### Doer as checker
Signals:
- implementation and verification are treated as the same step,
- no independent risk lens for high-impact changes.

Correction:
- run dedicated verification specialists for risky slices,
- keep completion decision evidence-based.

### Shotgun debugging
Signals:
- many speculative edits land before first targeted verification,
- rollback path becomes unclear.

Correction:
- revert to tracer-bullet slices,
- validate after each minimal change.

### Horizontal slicing
Signals:
- work split by layer only, with no end-to-end behavior proof.

Correction:
- execute vertical behavior slices,
- require cross-boundary verification for each meaningful behavior.
