---
status: complete
priority: p2
issue_id: "011"
tags:
  - code-review
  - portability
  - operations
dependencies: []
---

# Hardcoded absolute paths reduce portability of plan validation and implementation

## Problem Statement
The plan, examples, and validation commands assume `/Users/jamiecraik/...` absolute paths throughout, which makes the plan non-portable to other workspaces, CI agents, or containerized environments unless manually rewritten.

## Findings
- Absolute paths are used in execution contract, validation commands, and task list (e.g., `/Users/jamiecraik/dev/configs/...`, `/Users/jamiecraik/dev/agent-skills/...`) in multiple sections.
- This appears at least at: `docs/plans/...:254-257`, `377-403`, `405-451`, `520-531`, `659-687`.

## Proposed Solutions

### Option 1: Environment-rooted variables in plan and scripts
**Approach:** Replace absolute paths with configurable roots such as `REPO_ROOT`, `VAULT_ROOT`, `OPS_ROOT`.

**Pros:**
- Works in CI and alternate home directories.
- Easier to test across environments.

**Cons:**
- Requires default/fallback path docs.

**Effort:** 1-2 hours

**Risk:** Low

### Option 2: Keep absolute paths but define derivation from repo-relative path
**Approach:** Keep path examples local but include derivation command (`ROOT=$(git rev-parse --show-toplevel)`) and derive target paths.

**Pros:**
- Minimal text churn.

**Cons:**
- Still assumes git checkout layout.

**Effort:** 1 hour

**Risk:** Low-Medium

### Option 3: Defer path binding to runtime script config files
**Approach:** Move all paths to config (vault config/ops config) and pass into `run_graph_op.sh`.

**Pros:**
- Strong operational flexibility.

**Cons:**
- Requires additional config management.

**Effort:** 3-4 hours

**Risk:** Medium

## Recommended Action

TBD. Prefer Option 1 to support local and CI deterministically.

## Technical Details

**Affected content:**
- Multiple acceptance/gating lines and command examples in the same plan file.

## Acceptance Criteria
- [ ] No hardcoded user-home absolute paths remain in required commands.
- [ ] Path derivation is documented with defaults and override mechanism.
- [ ] CI/local commands can execute from non-interactive environments.

## Work Log

### 2026-02-26 - Initial Discovery

**By:** code review process

**Actions:**
- Scanned command and test snippets for absolute path usage.
- Identified multiple hardcoded environment-specific references.

**Learnings:**
- A single root variable would collapse this issue with minimal risk.

## Notes
- This is particularly important because `run_graph_op.sh` may execute in automation or worktree contexts.
