# GitHub Skill Consolidation Migration Note

Canonical GitHub skill: `gh-workflow`

## Effective date
- February 11, 2026

## Aliases (compatibility window)
The following skills are deprecated aliases that now route to `gh-workflow` modes:

- `gh-actions-fix` -> `ci_diagnose`
- `gh-address-comments` -> `pr_review_comments`
- `gh-issue-fix` -> `issue_fix`
- `gh-pr-local` -> `pr_prepare` (or `intake` for discovery)
- `yeet` -> `pr_prepare`

## Sunset review date
- May 12, 2026

## Merge policy default
- Server-side merge via `gh pr merge`
- Default: `--squash --delete-branch --auto`
- Fallback: `--squash --delete-branch` when auto-merge unsupported and checks pass
- Block when checks fail and auto-merge is unavailable
