# PR #192 Post-Push Triage: 5f20d84

Runtime source: live GitHub/gh queries against `jscraik/Agent-Skills` PR #192 after head `5f20d846e7837eb05bf123f6e87ee9a9bb406ff8`.

## Status

- PR: https://github.com/jscraik/Agent-Skills/pull/192
- Title: `feat(jsc-351): add Codex ABI conformance gates`
- State: open
- Draft: false
- Head: `codex/jsc-351-abi-conformance` at `5f20d846e7837eb05bf123f6e87ee9a9bb406ff8`
- Base: `main` at `4c78f981723875534c08466568bb533b28cd593d`
- GitHub mergeability: `MERGEABLE`
- GitHub merge state: `BLOCKED`
- Status rollup: `SUCCESS`
- Local checkout caveat: `/Users/jamiecraik/dev/agent-skills` is still on `codex/jsc-351-abi-conformance...origin/codex/jsc-351-abi-conformance [behind 15]` with a dirty worktree, so local files are stale relative to the pushed PR head.

## Findings

### P1: Merge is blocked by two current unresolved review threads

Evidence:

- Repository rules for `main` include pull-request rule `required_review_thread_resolution: true`, with `required_approving_review_count: 0`.
- GraphQL review thread query returned `reviewThreads.totalCount = 33`; 31 are resolved, 2 are unresolved and not outdated.
- Current unresolved thread 1:
  - URL: https://github.com/jscraik/Agent-Skills/pull/192#discussion_r3293517618
  - File: `Infrastructure/scripts/lifecycle-and-sync/command_surface.py:437`
  - Author: `chatgpt-codex-connector`
  - Commit: `5f20d846e7837eb05bf123f6e87ee9a9bb406ff8`
  - Summary: P1, "Validate rooted symlink targets before skipping handle checks"; the rooted-symlink fast path can skip generated handle checks without verifying required files such as `SKILL.md`, allowing broken runtime handles to pass with `checked_count = 0`.
- Current unresolved thread 2:
  - URL: https://github.com/jscraik/Agent-Skills/pull/192#discussion_r3293517621
  - File: `Infrastructure/scripts/lifecycle-and-sync/skill_discovery.py:267`
  - Author: `chatgpt-codex-connector`
  - Commit: `5f20d846e7837eb05bf123f6e87ee9a9bb406ff8`
  - Summary: P1, "Restrict default visibility to policy-approved system bridges"; current logic treats any system-owned bridge skill as default-visible when the name is in `SYSTEM_BRIDGE_SKILL_NAMES`, risking hidden bridge skills leaking into default picker/catalog behavior.

Impact:

These are current-head P1 review findings and the repo rules require conversation resolution. Merge is not safe until both are fixed or explicitly resolved with documented disposition.

Remediation:

Address the two P1 findings in a new commit on `codex/jsc-351-abi-conformance`, rerun the relevant focused tests/validators, push, and confirm both threads are resolved or outdated. Do not merge from the stale local checkout without first fetching/resetting or switching to a clean worktree for the PR head.

### P2: CI is green, but it no longer clears the merge block by itself

Evidence:

- `gh pr checks 192 --repo jscraik/Agent-Skills --json ...` reports all active checks passing after the refresh.
- `CodeQL`, `Semgrep OSS`, `Semgrep (SAST)`, `Trivy`, `Gitleaks`, `Socket`, `Snyk`, `Harness PR Pipeline` jobs, `CI Tests`, `skill-quality`, `docs-governance`, CircleCI `ci/circleci: pr-pipeline`, and `pr-template` are passing.
- `eval-baseline` is `SKIPPED`/neutral.
- GraphQL status check rollup for head `5f20d846e7837eb05bf123f6e87ee9a9bb406ff8` is `SUCCESS`.
- GitHub still reports `mergeStateStatus: BLOCKED`.

Impact:

CI is not the current blocker. Treating the PR as merge-ready because checks are green would miss the rule-required unresolved review conversations.

Remediation:

Keep checks as green proof, but use review-thread resolution as the closeout gate.

### P2: Branch/local drift creates stale-state risk for remediation

Evidence:

- Local `git status --short --branch` reports `## codex/jsc-351-abi-conformance...origin/codex/jsc-351-abi-conformance [behind 15]`.
- The local worktree has many modified and untracked files, including existing JSC-351 artifacts and unrelated-looking Harness Engineering/llm-wiki surfaces.
- Live PR head is `5f20d846e7837eb05bf123f6e87ee9a9bb406ff8`.

Impact:

Any local remediation from the current checkout risks being based on stale files and a dirty tree. This is especially risky because the two current blockers touch `Infrastructure/scripts/lifecycle-and-sync/command_surface.py` and `Infrastructure/scripts/lifecycle-and-sync/skill_discovery.py`, both already modified locally.

Remediation:

Before implementing the next remediation slice, fetch the branch and work from a clean current-head worktree, or explicitly reconcile the current dirty checkout before editing.

## Merge Safety

No-go. PR #192 is technically mergeable and status checks are green, but it is blocked by repo rules requiring review-thread resolution. The two unresolved P1 current-head threads must be addressed or explicitly resolved before merge.

## Next Steps

1. Fetch/update a clean worktree for `codex/jsc-351-abi-conformance` at `5f20d846e7837eb05bf123f6e87ee9a9bb406ff8`.
2. Fix `command_surface.py` so rooted symlink fast paths verify required target files before skipping generated handle checks.
3. Fix `skill_discovery.py` so default-visible system bridge exposure is limited to the policy-approved default surface.
4. Run focused tests for lifecycle command handles/default visibility plus the relevant repo wrapper validation.
5. Push the remediation commit and re-query review threads, checks, and `mergeStateStatus`.

WROTE: artifacts/reviews/jsc-351-pr192-triage-lane/post-push-5f20d84.md
