---
source: https://docs.coderabbit.ai/pr-reviews/walkthroughs
---

Every time CodeRabbit reviews a pull request, it posts a walkthrough comment — a structured overview of the changes that appears at the top of the PR comment thread, separate from inline code comments. The walkthrough is on by default and fully configurable.

## Overview

The walkthrough comment is made up of independent sections. Each section can be enabled or disabled separately to match your team's workflow.
By default the walkthrough is wrapped in a collapsible Markdown `<details>` block. Set `collapse_walkthrough` to `false` to keep it expanded.

```
reviews:
  collapse_walkthrough: false
```

## Walkthrough sections

### Changed files summary

A grouped summary of files changed in the PR. Related changes are consolidated into rows — for example, a PR that modifies one source file and 27 localization files produces two rows. Each row includes a plain-language description of what changed.
Enable/disable with `changed_files_summary` (default: `true`).

### Sequence diagrams

For PRs that affect component interactions — API calls, event flows, async workflows — CodeRabbit generates Mermaid sequence diagrams showing the updated flow. Diagrams are rendered inline in GitHub and GitLab.
Enable/disable with `sequence_diagrams` (default: `true`).

### Estimated review effort

A score from 1 (trivial) to 5 (very complex) estimating how much effort the PR requires to review thoroughly. The estimate considers the number of files changed, the nature of the changes, and logic complexity.
Enable/disable with `estimate_code_review_effort` (default: `true`).

Open and closed issues that are related to the PR changes, even if not explicitly linked. Useful for surfacing issues that may be affected by the change or provide useful context.
Enable/disable with `related_issues` (default: `true`).

### Linked issue assessment

When a PR references an issue via keywords like `Closes #123`, CodeRabbit reads the issue and checks whether the changes address it. It highlights gaps between what the issue requested and what the PR delivers.
See PR Validation using Linked Issues for guidance on writing effective issues and understanding how CodeRabbit evaluates Pull Requests against them.
Enable/disable with `assess_linked_issues` (default: `true`).

Merged and open PRs that touched the same areas of the codebase, helping reviewers understand the change history of a file or feature.
Enable/disable with `related_prs` (default: `true`).

### Suggested labels

Labels that describe the nature of the change, such as `bug`, `enhancement`, `frontend`, or `breaking-change`. When no `labeling_instructions` are configured, suggestions are inferred from labels used on similar past PRs.
Enable/disable with `suggested_labels` (default: `true`).

### Suggested reviewers

Reviewers suggested based on git history and code ownership. Suggestions are included in the walkthrough and can optionally be assigned automatically.
Enable/disable with `suggested_reviewers` (default: `true`).

### Review status messages

Brief status messages posted when a review is skipped or cannot proceed — for example when a PR is in draft, matches an ignored title keyword, or review was manually paused.
Enable/disable with `review_status` (default: `true`).

### Poem

A short poem at the end of the walkthrough, generated from the changeset. Can be disabled if you prefer a strictly professional output.
Enable/disable with `poem` (default: `true`).

## Fortune while you wait

While a review is in progress, CodeRabbit posts a fortune message as a placeholder in the walkthrough comment. The placeholder is replaced by the full walkthrough once the review completes.
Enable/disable with `in_progress_fortune` (default: `true`).

## Including the PR summary

By default the PR summary is written into the PR description. To move it into the walkthrough comment instead, set `high_level_summary_in_walkthrough` to `true`. The summary will appear at the top of the walkthrough, above the changed files table.

```
reviews:
  high_level_summary_in_walkthrough: true
```
