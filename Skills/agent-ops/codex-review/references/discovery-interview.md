# Codex Review Discovery Interview

Use this only when the review request is underspecified and interaction is available.
Ask one round at a time; do not dump the full plan.

## Request user input mini-templates

Round 1 target question:

What should this skill help you do?

What exact local diff, branch, PR, commit ref, or review artifact should Codex review?

Explain why this matters: wrong target selection can review an empty diff, stale patch, or the wrong commit.

## Copy-paste payload examples

Ambiguous target:

What exact local diff, branch, PR, commit ref, or review artifact should Codex review?

Ambiguous proof:

Which validation should run with the review: the helper's auto-detected check, a specific test command, or no tests?

Ambiguous permissions:

Should the helper use its normal default sandbox/approval mode, or should it request explicit full-access review mode with `--full-access` / `CODEX_REVIEW_YOLO=1`?

## Round 1: Target

What exact local diff, branch, PR, commit ref, or review artifact should Codex review?

Why this matters: target mode changes the helper path and prevents reviewing an empty diff, stale patch, or wrong commit.

## Round 2: Proof

Which validation should run with the review: the helper's auto-detected check, a specific test command, or no tests?

Why this matters: validation ownership must separate current-patch failures, pre-existing failures, unrelated dirty worktree issues, and environment/tooling failures.

## Round 3: Permission Boundary

Should the helper use its normal default sandbox/approval mode, or should it request explicit full-access review mode with `--full-access` / `CODEX_REVIEW_YOLO=1`?

Why this matters: full-access mode changes the side-effect class and should be reserved for a real sandbox blocker after approval.

## Round 4: Confirmation

Does this capture the review target, validation proof, and permission boundary well enough for me to proceed?

Anything to add or change before I run the review?
