# Git Triage — JSC-351 PU-006

STATUS: recovered_by_coordinator_after_subagent_artifact_failure

## Summary

The git triage lane found a delivery governance blocker: the repository has no PR delivery surface for the current JSC-351 work, while the checkout is still on `main` and contains a large mixed dirty tree. This means it is not safe to blindly commit or push the whole worktree as the JSC-351 slice.

## Runtime Evidence

- Repository root: `/Users/jamiecraik/dev/agent-skills`
- Current branch: `main`
- Upstream state: `main...origin/main [ahead 5]`
- Staged files: 0
- Dirty tree evidence from `git status --short --branch`: large mixed tracked and untracked change set, including JSC-351 implementation files, generated skillset surfaces, review artifacts, plan/spec artifacts, and unrelated-looking skill/plugin/content changes.
- GitHub context reported by the triage subagent: no current-branch PR and no open PRs in `jscraik/Agent-Skills`.

## Blocker Classification

- Severity: blocker
- Category: governance / delivery / stale-state prevention
- Blocker class: `mixed_worktree_on_main_without_pr_surface`
- Operational impact: continuing implementation without a branch/PR means CI, review state, mergeability, CodeRabbit/Codex comments, and Linear delivery truth cannot be monitored as required by the governed workflow.

## Findings

### BLOCKER: Delivery Surface Missing

Current validated slices have remained local while the user explicitly required commit-to-PR between slices and continuous subagent-managed triage.

Remediation:
- Stop opening new implementation slices.
- Create an isolation branch before any commit.
- Stage only explicitly classified JSC-351-owned paths.
- Run a staged-diff triage pass before committing.
- Push the branch and open a PR so GitHub, CI, review, CodeRabbit/Codex comments, and Linear state can be monitored.

### HIGH: Mixed Worktree Scope Risk

The dirty tree mixes runtime code, generated manifests, docs, review artifacts, and unrelated-looking skill/plugin/content changes.

Remediation:
- Do not run broad `git add .`.
- Use an explicit file list or patch staging.
- Keep unrelated files unstaged.
- Commit generated/projection outputs only when their source changes and provenance are clear.

## Recommended Safe Delivery Sequence

1. Create an isolation branch from the current HEAD:
   `git switch -c codex/jsc-351-abi-conformance`

2. Build a candidate JSC-351 staging list from the goal board, plan/spec, implementation notes, JSC-351 code/tests, schemas, and JSC-351 review artifacts.

3. Run staged-scope checks before commit:
   `git diff --cached --name-only`
   `git diff --cached --stat`
   `git diff --cached`

4. Commit only after staged scope is verified.

5. Push the branch and open a PR.

6. Start continuous PR triage: GitHub PR state, CI checks, review threads, CodeRabbit/Codex comments, stale branch detection, and Linear state.

## Artifact Provenance

The git-triage subagent returned the triage content in mailbox but did not write the requested file after one artifact-only recovery request. Per the review swarm contract, this file persists the coordinator-recovered triage result and records the subagent artifact failure instead of treating mailbox text as sufficient completion evidence.

WROTE: artifacts/reviews/jsc-351-pu006/git-triage.md
