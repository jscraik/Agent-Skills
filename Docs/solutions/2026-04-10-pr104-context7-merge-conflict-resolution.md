---
title: PR merge conflict resolution with isolated worktree and preserved hooks
asset_family: pull request conflict remediation
owner: Agent Skills Team
source_artifact: Skills/agent-ops/context7/SKILL.md
freshness_reviewed_on: 2026-10-10
last_updated: 2026-10-10
review_after_days: 90
---

# PR Merge Conflict Resolution With Isolated Worktree And Preserved Hooks

Reviewed against the current [Git workflow standards](/codestyle/13-git-workflow.md)
on 2026-10-10. The original incident used hook bypasses. That historical
behaviour is not an approved fallback under current policy; the resolution below
supersedes that advice. This review does not re-verify the historical hosted PR.

## Table of Contents

- [Problem](#problem)
- [Resolution](#resolution)
- [Evidence](#evidence)
- [Follow-up](#follow-up)

## Problem

A long-lived PR branch (`codex/context7-skill-wizard-pr-20260410`) became non-mergeable against its base (`feature/wiki-llm-reference`) while the primary local checkout had extensive unrelated modifications. Resolving conflicts in-place risked contaminating user-owned local changes and made rollback harder.

During reconciliation, repository hooks also blocked normal commit/push flow:

- commit-time validation failed due projection-integrity drift not caused by the conflict fix;
- pre-push diagnostics repeatedly terminated during `Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family.sh` (`Terminated: 15`), preventing normal push despite a clean conflict resolution.

## Resolution

Use this sequence when conflict resolution must be isolated from a dirty working tree:

1. Create a separate temporary worktree from the PR head branch.
2. Merge the base branch into that worktree and resolve only files with conflict markers.
3. Stage conflict files explicitly and verify all conflict markers are removed.
4. Run required validation and normal signed commit hooks. If a gate fails or is terminated, capture its exact diagnostic and determine whether the defect belongs to the conflict change or another surface.
5. Repair defects within the authorised scope. For an out-of-scope blocker, continue independent work and request the smallest scope extension needed. Do not bypass hooks, disable signing or claim that unrelated failures are clearance.
6. Once the normal gates permit delivery, push without force to the authorised PR branch. Re-check its hosted head, checks, review threads and mergeability; a clean local merge alone proves none of those lanes.

For the historical incident, the recorded conflict set was (these are historical paths, not current command targets):

- `product/docs/context7/SKILL.md`
- `product/docs/context7/Infrastructure/references/contract.yaml`
- `product/docs/context7/Infrastructure/references/evals.yaml`
- `Skills/uv-python-project-setup/Infrastructure/scripts/README.md`

The durable rule is: isolate merge-conflict work from unrelated local edits and preserve the normal delivery gates. Isolation does not create authority to bypass a failing gate.

## Evidence

- PR context and mergeability target:
  [PR #104](https://github.com/jscraik/Agent-Skills/pull/104)
- Base/head pair used during merge:
  - base: `feature/wiki-llm-reference`
  - head: `codex/context7-skill-wizard-pr-20260410`
- Conflict-resolution merge commit pushed to PR head:
  - `5179eedbb98a3f83fc816e00f41f27273372fe79`
- Verification outcome after push:
  - GitHub PR metadata reported `mergeable: true`.
- Historical commands recorded, not a current runbook:
  - `git worktree add ... /tmp/agent-skills-pr104 ...`
  - `git merge --no-edit origin/feature/wiki-llm-reference`
  - `rg -n "^(<<<<<<<|=======|>>>>>>>)" ...`
  - `git commit --no-verify ...`
  - `git push --no-verify origin HEAD:codex/context7-skill-wizard-pr-20260410`
- Hook failure signal captured during normal flow:
  - pre-push diagnostics failed with `make: *** [hooks-pre-push] Terminated: 15` while running `Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family.sh`.

## Follow-up

- Investigate why `Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family.sh` intermittently terminates under hook execution even with a clean tree.
- Keep conflict-only remediation commits narrowly scoped and avoid bundling repo-wide drift fixes in the same PR.
- Preserve the recorded incident evidence, but use the current hook-preserving sequence for new work. The historical mergeability observation is not current review or CI clearance.
