# GitHub Skill Consolidation Migration Note

Canonical GitHub skill: `gh-workflow`

## Effective date
- February 11, 2026

## Alias retirement status
The following deprecated aliases were retired and removed on **February 24, 2026**:

- `gh-actions-fix` -> `ci_diagnose`
- `gh-address-comments` -> `pr_review_comments`
- `gh-issue-fix` -> `issue_fix`
- `gh-pr-local` -> `pr_prepare` (or `intake` for discovery)
- `yeet` -> `pr_prepare`

## Historical sunset plan (superseded)
- May 12, 2026 (superseded by early retirement on February 24, 2026)

## Merge policy default
- Server-side merge via `gh pr merge`
- Default: `--squash --delete-branch --auto`
- Fallback: `--squash --delete-branch` when auto-merge unsupported and checks pass
- Block when checks fail and auto-merge is unavailable
