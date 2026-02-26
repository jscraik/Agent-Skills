---
status: complete
priority: p3
issue_id: "013"
tags:
  - code-review
  - validation
  - schema
dependencies: []
---

# Missing explicit JSON schema + fixture definitions for `run_graph_op.v1`

## Problem Statement
The contract defines a `run_graph_op.v1` shape but does not provide a concrete schema object (JSON Schema/YAML contract) for fields like `stage`, `errors`, `warnings`, and `planned_actions`, reducing confidence that machine consumers will parse outputs deterministically.

## Findings
- Output example is present but incomplete and non-normative:
  `docs/plans/...:269-289`.
- Plan also requests validation of schema/version but does not provide testable schema source file:
  `docs/plans/...:525`, `543`.

## Proposed Solutions

### Option 1: Add machine-readable schema file
**Approach:** Add `run_graph_op.v1.schema.json` in plan or scripts directory with strict required fields and enums.

**Pros:**
- Enables automated validation in CI.
- Prevents contract drift across implementations.

**Cons:**
- Extra artifact upkeep.

**Effort:** 1-2 hours

**Risk:** Low

### Option 2: Keep textual example and ad-hoc assertions
**Approach:** Use sample payload only plus manual reviewer checks.

**Pros:**
- Minimal effort.

**Cons:**
- Harder to automate and easier for regressions to slip through.

**Effort:** 30-60 minutes

**Risk:** Medium-High

### Option 3: Use in-script JSON schema comments only
**Approach:** Embed schema comments into script and validate with python on output generation.

**Pros:**
- Keeps contract close to runtime code.

**Cons:**
- Still requires explicit test harness and can become inconsistent with docs.

**Effort:** 2-3 hours

**Risk:** Medium

## Recommended Action

TBD: choose Option 1 and wire to validation gate.

## Technical Details

**Affected content:**
- Contract section + acceptance criteria + validation commands in the same plan file.

## Acceptance Criteria
- [ ] A versioned schema file exists for `run_graph_op.v1`.
- [ ] Machine-readable output validation is part of CI-style command set.
- [ ] Schema failures fail plan acceptance on deterministic fields.

## Work Log

### 2026-02-26 - Initial Discovery

**By:** code review process

**Actions:**
- Reviewed contract section and validation criteria.
- Confirmed no concrete machine schema definition is included.

**Learnings:**
- Without schema enforcement, contracts are interpreted inconsistently across integrations.

## Notes
- Include schema link from docs section to make this directly discoverable in plan reviews.
