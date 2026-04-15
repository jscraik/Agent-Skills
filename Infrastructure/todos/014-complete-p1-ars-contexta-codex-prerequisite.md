---
status: complete
priority: p1
issue_id: "014"
tags:
  - code-review
  - setup
  - operations
dependencies: []
---

# Broken `ars-contexta-codex` prerequisite path blocks implementation start

## Problem Statement
The plan requires `product/domain/ars-contexta-codex/SKILL.md` and references `skills/ars-contexta-codex` as a symlink, but this target is missing/broken today. This prevents canonical execution of the plan’s `/graph` integration steps and invalidates prerequisite checks before rollout.

## Findings
- Implementation task references absolute/required path `product/domain/ars-contexta-codex/SKILL.md` as required prerequisite: `Docs/plans/2026-02-26-feat-arscontexta-graph-visual-communities-evolution-plan.md`.
- In repository state, `product/domain/ars-contexta-codex` does not exist, while `skills/ars-contexta-codex` is a broken symlink to that path.
- This is already listed as a dependency/risk, but still requires explicit remediation before the runbook/automation steps in the plan can be executed.

## Proposed Solutions

### Option 1: Restore/correct the symlink target
**Approach:** Recreate or repoint `product/domain/ars-contexta-codex` (or `skills/ars-contexta-codex`) to a real, tracked directory containing `SKILL.md` and any implementation guidance.

**Pros:**
- Fastest unblock path.
- Keeps existing implementation references intact.

**Cons:**
- Requires locating canonical source of truth for domain skill content.

**Effort:** Small

**Risk:** Medium

### Option 2: Update plan and tasks to target existing canonical path
**Approach:** Change prerequisite references to the actual valid directory currently available in repo.

**Pros:**
- Immediate review and execution consistency.
- No dangling-link risk.

**Cons:**
- Needs proof that all consumers accept new path.

**Effort:** Small-Medium

**Risk:** Medium

### Option 3: Add preflight guard and explicit failure mode if missing
**Approach:** Keep paths for now but add explicit guard in plan/automation that fails with actionable remediation and blocks downstream graph op tasks.

**Pros:**
- Avoids silent failure.

**Cons:**
- Still delays implementation until manual intervention.

**Effort:** Small

**Risk:** Medium

## Recommended Action

TBD in triage: choose Option 1 or Option 2, with explicit preflight verification before any implementation.

## Technical Details
- Affects: `Docs/plans/2026-02-26-feat-arscontexta-graph-visual-communities-evolution-plan.md` (Dependencies & Risks, Implementation Tasks).
- Repo check command evidence: `ls -ld product/domain/ars-contexta-codex skills/ars-contexta-codex`.

## Acceptance Criteria
- [ ] `product/domain/ars-contexta-codex/SKILL.md` is present and valid.
- [ ] `skills/ars-contexta-codex` resolves to an existing directory.
- [ ] No hard dependency blocker remains in implementation gate checks.

## Work Log

### 2026-02-26 - Initial Discovery

**By:** code review process

**Actions:**
- Confirmed symlink and path resolution state in repo.
- Captured that prerequisite blocker is real despite being documented.

**Learnings:**
- Plan dependency must be operationally fixed before task execution.

## Resources
- `Docs/plans/2026-02-26-feat-arscontexta-graph-visual-communities-evolution-plan.md`
- `product/domain/ars-contexta-codex` (planned)
- `skills/ars-contexta-codex`
