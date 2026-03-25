Read when: you need the original upstream `greploop` loop semantics, comment trigger wording, or exact iteration flow from `greptileai/skills`.

# Upstream Greploop

Source:
- Repo: `https://github.com/greptileai/skills`
- Skill path: `greploop/SKILL.md`
- Ref: `main`
- Blob SHA: `e2e1a45e1f53118302184c22ecd6df4a32b0a811`

## Original routing

The upstream skill describes `greploop` as an iterative PR-improvement loop that:
- triggers Greptile review,
- fixes actionable comments,
- pushes changes,
- re-triggers review,
- repeats until a `5/5` confidence score with zero unresolved comments or until a max-iteration cap is hit.

## Preserved upstream loop outline

1. Identify the PR from input or current branch.
2. Trigger a fresh Greptile review with:
   - `git push`
   - `gh pr comment <PR_NUMBER> --body "@greptile review"`
   - `gh pr checks <PR_NUMBER> --watch`
3. Fetch the latest Greptile review and inline comments.
4. Parse:
   - confidence score,
   - unresolved comment count.
5. Stop when:
   - score is `5/5` and unresolved comments are zero, or
   - max iterations is reached.
6. For unresolved comments:
   - read context,
   - classify actionable versus informational,
   - fix actionable items,
   - resolve addressed review threads.
7. Commit and push, then repeat.

## Local adaptation

This repo preserves the upstream loop doctrine but tightens four things:

- approval gating:
  comment, commit, push, and thread-resolution actions stay behind explicit approval;
- bounded autonomy:
  the local wrapper emphasizes audit-only and propose-fixes lanes before mutation;
- deconfliction:
  `check-pr` owns one-shot readiness classification and `gh-workflow` owns broader GitHub lifecycle operations;
- safety:
  score chasing is not treated as sufficient reason to make speculative code changes.
