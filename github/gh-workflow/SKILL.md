---
name: gh-workflow
description: "Consolidated GitHub lifecycle skill for agents and users: intake, issue fixing, PR prep, review request/reception, review comment handling, CI diagnosis, and server-side merge via gh. Use when requests involve GitHub issues/PRs/checks/merge operations."
metadata:
  skill-type: ci_cd_deployment
---

# GH Workflow

Use the canonical GitHub workflow path for issue, PR, review, CI, and merge work driven by `gh`.

## Standards snapshot (March 2026)
- Keep GitHub operations evidence-backed and stateful: know the repo, branch, PR, and current git status before acting.
- Verify every git-changing operation immediately after it happens.
- Prefer one explicit mode at a time unless the user clearly wants the full lifecycle.
- Treat non-GitHub-Actions providers as link-only evidence unless a narrower skill owns them.
- Keep GitHub Actions workflows pinned to full commit SHAs for third-party actions and use least-privilege `permissions`.

## Philosophy
- GitHub state and local git state must agree before you call work complete.
- Prefer explicit operating modes over fuzzy all-in-one execution.
- Verification after mutation is part of the workflow, not an optional epilogue.

## When to use
- GitHub issue triage or issue-linked fixes.
- PR preparation, review requests, review intake, and review-comment handling.
- CI failure diagnosis for PR checks.
- Server-side merge flows through `gh pr merge`.

## Modes
- `intake`
- `issue_fix`
- `pr_prepare`
- `pr_request_review`
- `pr_receive_review`
- `pr_review_comments`
- `ci_diagnose`
- `pr_merge_server`
- `full_lifecycle`

## Required inputs
- Requested mode or clear user intent.
- Repo path or slug when ambiguous.
- PR number or URL for PR, comment, check, or merge work when it cannot be discovered.
- Issue number for `issue_fix`.

## Preconditions
1. `gh` is installed and authenticated.
2. Repository context resolves correctly.
3. Git state is clean or explicitly understood.
4. PR context is resolved when needed.
5. Mergeability and check state are known before merge operations.

## Deliverables
- A concise status summary with the current mode, repo, PR or issue context, and next step.
- Evidence for the action taken, especially after git operations.
- Clear blocked states with remediation.
- If requested, a structured status report aligned to `references/contract.yaml` with `schema_version: 1`.

## Constraints
- Redact secrets, tokens, credentials, and sensitive repository data by default.
- Do not run destructive git operations without explicit user approval.
- Do not guess command syntax when `gh help` or git inspection can verify it.

## Failure mode
- If auth, repo context, or PR context is missing, stop and return a blocked status with the exact remediation.
- If git state is dirty or conflicted in a way that changes the operation, stop and surface the actual state.
- If merge is requested while checks are failing and no safe auto-merge path exists, block instead of forcing progress.

## Workflow
1. Resolve the mode from user intent.
2. Run intake gates: auth, repo, git state, and PR discovery when relevant.
3. Execute the mode-specific workflow.
4. After any git-changing operation, run verification:
   - `git status`
   - `git log --oneline -5`
   - `git branch -vv`
5. Return the outcome, evidence, risks, and next step.

## Mode notes
- `issue_fix`: inspect the issue, make the minimal fix, and verify it.
- `pr_prepare`: stage intended files, commit, verify git state, push, and prepare the PR.
- `pr_request_review`: summarize change scope, risk, and readiness evidence before requesting review.
- `pr_receive_review`: classify feedback as accept, clarify, or push back with evidence.
- `pr_review_comments`: map fixes back to specific review items.
- `ci_diagnose`: inspect failing checks and surface the first actionable blocker.
- `pr_merge_server`: verify mergeability and checks, perform the merge, then verify the post-merge state.

## Tooling and references
- Use `gh help <command>` when command shape is uncertain.
- Prefer `--body-file` over inline multi-line PR bodies.
- Reference files:
  - `references/contract.yaml`
  - `references/evals.yaml`
  - `references/folded-legacy-modes-core60.md`
  - `references/migration.md`
  - `agents/openai.yaml`
- Use assets only when the task benefits from bundled GitHub workflow support material in `assets/`.

## Validation
- Verify auth, repo, and git preconditions before acting.
- Verify post-operation git state after any commit, push, merge, or rebase.
- Verify the reported status matches actual `gh` and git evidence.
- Fail fast at the first broken gate.

## Anti-patterns
- Guessing `gh` flags from memory when `gh help` can verify them.
- Reporting success after a git-changing operation without a post-op check.
- Attempting deep scraping of external CI providers from this workflow.
- Expanding scope beyond the requested lifecycle stage.

## GitHub Actions security baseline
- Pin actions to a full-length commit SHA.
- Apply least-privilege `permissions` for workflows and jobs.

## Examples
- Prepare this branch as a draft PR and show me the review summary.
- Check PR 123, classify the review feedback, and tell me what to fix next.
- Merge this PR server-side if the checks are ready and then verify the final state.

## Remember
GitHub workflow work is only complete when the repository state and the GitHub state agree.

## See Also

| Skill | When to use together |
|---|---|
| [[gh-fix-ci]] | Focused CI diagnosis mode — use when the only task is debugging a failing Actions check |
| [[verification-before-completion]] | Gate all merge claims with fresh `gh pr checks` and `git log` evidence |
| [[systematic-debugging]] | When PR CI failures reveal a code-level bug that needs root-cause investigation |
| [[release]] | After merging — use to cut the version tag and publish the release |
| [[check-pr]] | Pre-merge policy review: readiness view with check status and remediation priority |

**Topic map:** [[backend-platform]]

## Gotchas
- None yet. Capture recurring failures here as symptom -> cause -> do instead -> check.
