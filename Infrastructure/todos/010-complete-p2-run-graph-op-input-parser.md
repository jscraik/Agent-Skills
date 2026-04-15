---
status: complete
priority: p2
issue_id: "010"
tags:
  - code-review
  - execution-contract
  - bash
  - parser
dependencies: [009]
---

# run_graph_op.sh pseudocode references undefined helper functions

## Problem Statement
The pseudocode in the plan calls helper functions (`in_array`, `usage`, `emit_error`, `preflight`, `emit_plan`) without specifying their definitions or source-of-truth module, while acceptance guidance also expects strict error codes and JSON envelopes. This creates an unverified execution path and risk of runtime breakage if helper imports are omitted.

## Findings
- In `run_graph_op.sh` pseudocode, `in_array` / `usage` / `emit_error` / `preflight` / `emit_plan` are used but not defined or sourced:
  `Docs/plans/2026-02-26-feat-arscontexta-graph-visual-communities-evolution-plan.md:417-425`.
- The contract requires rich machine outputs, but no explicit requirement exists to source a shared library that guarantees this behavior before command dispatch.

## Proposed Solutions

### Option 1: Define one shared shell library contract
**Approach:** Add explicit `source "$SCRIPT_DIR/_graph_lib.sh"` requirement and document helper APIs (`in_array`, `emit_error`, `emit_json`, parser utilities).

**Pros:**
- Reusable and testable behavior across script + helper tests.
- Prevents undefined-function runtime failures.

**Cons:**
- Adds one file and import requirement to test/prod execution paths.

**Effort:** 2-4 hours

**Risk:** Medium

### Option 2: Inline minimal parser helpers
**Approach:** Replace helper calls with explicit inline shell functions within `run_graph_op.sh`.

**Pros:**
- No external sourcing assumptions.
- Faster to bootstrap initially.

**Cons:**
- Duplicates logic and increases coupling/maintenance burden.

**Effort:** 1-2 hours

**Risk:** Medium

### Option 3: Keep pseudocode only
**Approach:** Keep current plan text and leave implementation to future interpretation.

**Pros:**
- Minimal documentation edits.

**Cons:**
- High defect risk at implementation time and inconsistent behavior.

**Effort:** 30 min

**Risk:** High

## Recommended Action

TBD: prefer Option 1 with explicit helper contract and unit-invocable helper tests.

## Technical Details

**Affected content:**
- `Docs/plans/.../2026-02-26-feat-arscontexta-graph-visual-communities-evolution-plan.md` (Pseudocode section, Validation gates).

## Acceptance Criteria
- [ ] Script pseudocode explicitly identifies helper module imports.
- [ ] Every helper used in pseudocode is defined with signature and return contract.
- [ ] Invalid op parsing returns `E_USAGE`/`E_VALIDATION` consistently.

## Work Log

### 2026-02-26 - Initial Discovery

**By:** code review process

**Actions:**
- Audited pseudocode and contract sections.
- Confirmed helper calls appear without declared definitions.

**Learnings:**
- Plan needs one explicit dependency row for shared script library to close the gap.

## Notes
- Suggest adding a “helpers are required” bootstrap check before any execution branch.
