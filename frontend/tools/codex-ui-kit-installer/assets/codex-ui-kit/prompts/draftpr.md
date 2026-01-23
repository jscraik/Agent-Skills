---
description: Prep a branch, commit, and open a draft PR
argument-hint: [FILES=<paths>] [PR_TITLE="<title>"]
---

Create a branch named `dev/<feature_name>` for this work.

If files are specified, stage them first: $FILES.

Commit the staged changes with a clear message.

Open a draft PR on the same branch.
- If `gh` (GitHub CLI) is available, use it (`gh pr create --draft ...`).
- If `gh` is not available, output:
  - the branch name
  - the commit hash
  - a ready-to-paste PR title and description

Use $PR_TITLE when supplied; otherwise write a concise summary yourself.
