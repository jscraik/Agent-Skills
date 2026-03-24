# Resolve PR Parallel Overlap Matrix

Use this matrix to keep `resolve-pr-parallel` focused on remediation of all unresolved PR review threads, not readiness review or general GitHub lifecycle work.

## Table of Contents
- [Boundary rule](#boundary-rule)
- [Matrix](#matrix)
- [Notes](#notes)

## Boundary rule
- Trigger `resolve-pr-parallel` when the user wants the remaining unresolved PR review threads handled as a batch, especially when parallel remediation is desired.
- If the user only wants to inspect readiness, triage comments, or handle a few selected comments manually, route to the narrower owner instead.

## Matrix

| Request shape | Primary outcome | Owner |
|---|---|---|
| "Resolve all remaining review comments on this PR." | Batch remediation and thread resolution | `resolve-pr-parallel` |
| "Clear every unresolved review thread on PR 482 and verify GitHub is clean." | End-to-end review-thread remediation | `resolve-pr-parallel` |
| "Is this PR ready to merge?" | Readiness and blocker audit | `check-pr` |
| "Handle review comments 2 and 4 only." | Selected-comment workflow | `gh-workflow` |
| "Prepare this branch as a PR and request review." | Broader GitHub lifecycle management | `gh-workflow` |
| "Why are the PR checks failing?" | CI diagnosis | `gh-fix-ci` |
| "How should this repo's CircleCI workflow gate PR remediation and deploys?" | CircleCI workflow design and policy | `circleci` |
| "Do a broad readiness review of this branch." | Package-level review | `ce-review` |
| "Find the engineering risks in this PR." | Technical critique, not remediation | `ce-technical-review` |

## Notes
- `resolve-pr-parallel` is a focused specialist, not the canonical GitHub umbrella skill.
- If the user already names a narrower owner like `check-pr` or `gh-workflow`, that narrower owner wins.
- Question-only threads still count as remediation work here, but only when the user wants the whole unresolved-thread set handled.
