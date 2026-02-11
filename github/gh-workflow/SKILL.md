---
name: gh-workflow
description: "Consolidated GitHub lifecycle skill for agents and users: intake, issue fixing, PR prep, review comment handling, CI diagnosis, and server-side merge via gh. Use when requests involve GitHub issues/PRs/checks/merge operations."
---

# GH Workflow (Canonical)

## When to use

Use this as the single source of truth for GitHub task execution when a request involves:

- GitHub issue triage/fixing
- PR preparation or review comment handling
- CI failure diagnosis for PR checks
- Server-side merge with `gh pr merge`

## Philosophy

- One canonical workflow prevents drift across overlapping GH skills.
- Keep actions minimal, reversible, and evidence-backed.
- Prefer explicit state (`ready`, `blocked`, `in_progress`, `completed`, `failed`).
- Route non-GitHub Actions checks as links-only evidence.

## Variation guidance

- Adapt mode selection to user intent and available context.
- In `full_lifecycle`, skip already-completed stages and focus on the next blocker.
- Increase evidence detail for risky changes and merge operations.
- Keep routing deterministic while varying explanation depth for user vs agent consumers.

## Modes

Select one mode explicitly from user intent; default to `full_lifecycle` when multiple stages are requested.

- `intake`
- `issue_fix`
- `pr_prepare`
- `pr_review_comments`
- `ci_diagnose`
- `pr_merge_server`
- `full_lifecycle`

## Inputs

- Requested mode (or clear intent that maps to one mode)
- Repo path/slug when ambiguous
- PR number or URL for PR/comment/check/merge workflows (optional only when discoverable from current branch)
- Issue number for `issue_fix`

## Preconditions

1. `gh` exists and is authenticated (`gh auth status`).
2. Repository context is resolved (`gh repo view --json nameWithOwner`).
3. PR context is resolved when needed (`gh pr view --json number,url,headRefName,baseRefName,state`).
4. For merge mode, check state/branch protection status is known.

If any precondition fails, return `status=blocked` with remediation.

## Default behaviors

### Merge defaults (`pr_merge_server`)

- Primary command:
  - `gh pr merge <pr> --squash --delete-branch --auto`
- Fallback if auto-merge unsupported and checks already passing:
  - `gh pr merge <pr> --squash --delete-branch`
- If auto-merge unsupported and checks are not passing:
  - Block and return required next action.

### CI diagnosis scope (`ci_diagnose`)

- GitHub Actions: extract run/job evidence + failure snippets.
- Non-GitHub Actions checks: capture provider/check name + details URL only.

## Outputs

All substantive responses must align with `references/contract.yaml` (`schema_version: 1`) and include:

- `mode`, `repo`, `pr`, optional `issue`
- `status`
- `actions_taken[]`
- `evidence[]`
- `merge` object (for merge mode)
- `next_step`
- `risks[]`

Also provide a concise human-readable summary.

## Workflow

1. Resolve mode from request.
2. Run `intake` gates (auth/repo/pr discovery).
3. Execute mode-specific workflow:
   - `issue_fix`: inspect issue, implement minimal fix, run checks, summarize evidence.
   - `pr_prepare`: branch prep, stage intended files, commit, push, create draft PR.
   - `pr_review_comments`: list threads, apply scoped fixes, map each fix to evidence.
   - `ci_diagnose`: inspect failing checks, summarize first actionable failure.
   - `pr_merge_server`: apply merge defaults/fallback and report final merge status.
   - `full_lifecycle`: chain `intake -> issue_fix -> pr_prepare -> pr_review_comments -> ci_diagnose -> pr_merge_server`.
4. Return contract + human summary.

## Failure handling

- Missing auth -> `blocked` + `gh auth login` remediation.
- No current-branch PR and no PR provided -> `blocked` + request PR identifier.
- Merge requested with failing checks and no auto-merge path -> `blocked` + required checks to clear.
- External CI failure only -> `in_progress` or `blocked` with provider URL evidence.

## Validation

Fail fast: **stop at the first failed gate** and fix it before continuing.

- Keep frontmatter to `name` + `description`.
- Keep logic canonical here; aliases must route here.
- Keep evals realistic and route-safe (`references/evals.yaml`).

## Anti-patterns

- Duplicating logic in alias skills.
- Attempting deep non-GitHub-Actions provider scraping.
- Merging server-side without reporting final merge outcome.
- Expanding scope beyond requested mode(s).

## Security constraints

- Never reveal secrets/tokens/PII.
- Do not run destructive git operations outside explicit request.

## Bundled scripts

- `scripts/inspect_pr_checks.py`
- `scripts/fetch_comments.py`
- `scripts/github-pr.py`

## Example prompts

- "Fix issue #123, open a draft PR, then merge when checks pass."
- "Diagnose failing checks on PR 456 and summarize the first actionable failure."
- "Use gh to merge this PR to main server-side."
- "Address comments 2 and 4 on the current PR and show evidence."

## Remember

The agent is capable of extraordinary work in this domain. These guidelines unlock that potential—they don't constrain it.
Use judgment, adapt to context, and push boundaries when appropriate.

## References

- `references/contract.yaml`
- `references/evals.yaml`
- `references/migration.md`
