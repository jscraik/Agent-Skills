---
status: complete
priority: p2
issue_id: "009"
tags:
  - code-review
  - cli-contract
  - docs-plans
dependencies: []
---

# Inconsistent run_graph_op.sh flag contract in plan content

## Problem Statement
The plan defines conflicting CLI contracts for `run_graph_op.sh`: the **Inputs** table only lists `-h` and `--json`, but examples and test scenarios repeatedly use additional flags (`--dry-run`, `--max-nodes`, `--max-edges`, `--timeout-seconds`, `--min-size`, `--vault-root`). This mismatch makes the implementation contract ambiguous and increases drift risk between docs and script behavior.

## Findings
- **Gap:** The discrepancy appears across the contract section and test commands.
  - Inputs table lacks many flags: `docs/plans/2026-02-26-feat-arscontexta-graph-visual-communities-evolution-plan.md:259-264`.
  - Example invocations reference undeclared flags: `docs/plans/2026-02-26-feat-arscontexta-graph-visual-communities-evolution-plan.md:311-314`.
  - Test scenarios also rely on undeclared flags (`--max-nodes`, `--dry-run`): `docs/plans/2026-02-26-feat-arscontexta-graph-visual-communities-evolution-plan.md:679-683`.
- This affects both manual and machine integrations because downstream tooling cannot rely on one source of truth for argument validation.

## Proposed Solutions

### Option 1: Authoritative single-schema option parser
**Approach:** Define one canonical parser section in the plan listing all supported flags, default values, constraints, and precedence rules.

**Pros:**
- Eliminates ambiguity between sections.
- Makes `--json`, `--dry-run`, and operation passthrough flags testable.
- Simplifies downstream wrapper integration.

**Cons:**
- Requires updating multiple sections to remove inconsistent examples.

**Effort:** 1-2 hours

**Risk:** Low

### Option 2: Split contract into global vs operation-scoped flags table
**Approach:** Add two explicit tables: global flags (available for all operations) and per-operation flags (visual/communities/evolution).

**Pros:**
- Reduces parser complexity and confusion.
- Supports future extensibility without contract breakage.

**Cons:**
- Slightly more documentation and maintenance overhead.

**Effort:** 2-3 hours

**Risk:** Medium

### Option 3: Minimal compatibility-only quick fix
**Approach:** Keep contract as-is but add aliases for every sample flag as no-op placeholders, with warning output.

**Pros:**
- Minimal changes to existing pseudocode.

**Cons:**
- Masks true contract ambiguity and can hide validation defects.

**Effort:** 30-60 minutes

**Risk:** Medium-High

## Recommended Action

TBD (set during triage): adopt Option 1 or 2 and keep one authoritative flag contract source.

## Technical Details

**Affected sections/files:**
- `docs/plans/2026-02-26-feat-arscontexta-graph-visual-communities-evolution-plan.md` (run_graph_op.sh CLI Contract + Example/Test sections).

## Acceptance Criteria
- [ ] Plan includes one authoritative flag table for global and per-operation flags.
- [ ] Every example and test command references only declared flags.
- [ ] Invalid/unknown flags include explicit parse errors and stable `error.code`.

## Work Log

### 2026-02-26 - Initial Discovery

**By:** code review process

**Actions:**
- Compared contract table against command examples and test matrix.
- Found undeclared flags referenced across multiple sections.

**Learnings:**
- Multiple sources of truth are already present; a single schema table is needed before implementation.

## Notes
- Keep this as a required implementation prerequisite to avoid divergence between human/operator docs and automation tooling.
