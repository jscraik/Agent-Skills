---
source: https://docs.coderabbit.ai/configuration/auto-review
---

# Automatic review controls

The `reviews.auto_review` settings group in `.coderabbit.yaml` file gives you fine-grained control over when CodeRabbit runs automatic reviews. By default, `enabled` is `true` and CodeRabbit reviews every PR automatically. You can disable reviews globally and re-enable them by keyword or label, apply them only to certain branches, skip draft PRs, pause after a set number of commits, and exclude PRs from specific authors.

## Scope (which PRs qualify)

Configure which pull requests CodeRabbit will review by specifying branch targets, draft status, labels, and keyword-based opt-in.

### `base_branches`

Specify which target branches should receive automatic reviews.

```yaml
reviews:
  auto_review:
    base_branches: []   # default — only the default branch
```

By default, CodeRabbit reviews PRs that target the repository's **default branch** (e.g. `main` or `master`). Use `base_branches` to add other branches.
Each entry is a **regex pattern**:

```yaml
reviews:
  auto_review:
    base_branches:
      - "develop"
      - "release/.*"
      - "hotfix/.*"
```

Use `".*"` to match all branches and review every PR regardless of target.

### `drafts`

Include draft PRs in automatic reviews.

```yaml
reviews:
  auto_review:
    drafts: false   # default
```

By default, CodeRabbit skips draft PRs. Set `drafts: true` to include them. This is useful for teams that use draft PRs as part of active development and want early feedback.

### `labels`

Control reviews using PR labels, including negative filters.

```yaml
reviews:
  auto_review:
    labels: []   # default — no label filter
```

The `labels` array controls which PRs are reviewed based on their labels. Labels prefixed with `!` are **negative** matches (exclusions).

| Configuration | Effect |
| --- | --- |
| `[]` (empty) | All PRs are reviewed (no label filter) |
| `["bug", "feature"]` | Only PRs with the `bug` or `feature` label |
| `["!wip"]` | All PRs **except** those labeled `wip` |
| `["bug", "!wip"]` | PRs labeled `bug` but **not** labeled `wip` |

**Example — opt-in via label with auto-review disabled:**

```yaml
reviews:
  auto_review:
    enabled: false
    labels: ["review-ready"]
```

Only PRs labeled `review-ready` will be reviewed.

### `description_keyword`

Opt-in by PR description when automatic reviews are disabled.

```yaml
reviews:
  auto_review:
    enabled: false
    description_keyword: "coderabbit:review"
```

When `enabled` is `false` and `description_keyword` is set to a non-empty string, CodeRabbit reviews any PR whose **description** contains that exact keyword string. PRs without the keyword are skipped.
Leave `description_keyword` empty (the default) to rely solely on label-based opt-in or manual `@coderabbitai review` commands.

---

## Exclusions

Configure rules to skip reviews completely for specific PRs based on title patterns or author. To skip specific **files** within a PR: lock files, generated code, or build artifacts - use `reviews.path_filters` instead.

### `ignore_title_keywords`

Skip reviews for PRs matching specific title keywords.

```yaml
reviews:
  auto_review:
    ignore_title_keywords:
      - "WIP"
      - "DO NOT MERGE"
      - "[skip review]"
```

If the PR title contains **any** of these strings (case-insensitive), the review is skipped silently. This is the lightest-weight way to signal that a PR is not ready for review.

### `ignore_usernames`

Skip reviews for PRs from specific authors (bots, service accounts).

```yaml
reviews:
  auto_review:
    ignore_usernames:
      - "dependabot[bot]"
      - "renovate[bot]"
      - "github-actions[bot]"
```

PRs authored by any username in this list are skipped silently — no review is posted. This is the recommended way to exclude automated bots, dependency update services, and service accounts.

**Username matching rules:**

- Exact match, **case-sensitive**
- No wildcard or regex support — each entry must be a full username
- Whitespace around entries is trimmed automatically
- Empty strings are ignored

**Common entries by platform:**

| Platform | Example usernames |
| --- | --- |
| GitHub | `dependabot[bot]`, `renovate[bot]`, `github-actions[bot]` |
| GitLab | `gitlab-ci-token`, `project_123_bot` |
| Azure DevOps | Service account display names |

Username skipping takes precedence over all other controls — if a PR author is in `ignore_usernames`, the review is skipped regardless of labels, `enabled`, or any other setting.
To force a review for a skipped author, comment `@coderabbitai review` on the PR.

---

## Incremental review

Configure how CodeRabbit handles updates and subsequent pushes to an existing PR.

### `auto_incremental_review`

Review updates on each new push (default enabled).

```yaml
reviews:
  auto_review:
    auto_incremental_review: true   # default
```

When `true` (the default), CodeRabbit re-reviews a PR after each new push, focusing on the **commits added since the last review**. This keeps feedback timely without re-analyzing unchanged code.
Set to `false` to review only when a PR is first opened. Subsequent pushes will be ignored until you trigger the review manually.

### `auto_pause_after_reviewed_commits`

Pause automatic reviews after reaching a commit threshold.

```yaml
reviews:
  auto_review:
    auto_pause_after_reviewed_commits: 5   # default
```

CodeRabbit automatically pauses incremental reviews after this many **reviewed** commits since the last pause. The counter resets each time the pause is lifted.
Set to `0` to disable the pause and always review, no matter how many commits accumulate.

| Value | Behavior |
| --- | --- |
| `0` | Never auto-pause — review every push |
| `5` | Pause after 5 reviewed commits (default) |
| `N` | Pause after N reviewed commits |

### Manual review commands

When automatic incremental reviews reach their limits, you can use manual commands to control the review process:

- `@coderabbitai review` — Request an incremental review of new changes on demand
- `@coderabbitai full review` — Re-initiate a complete review of all files from scratch
- `@coderabbitai pause` — Temporarily stop automatic reviews
- `@coderabbitai resume` — Restart automatic reviews after a pause

---

## Complete `auto_review` example

```yaml
reviews:
  auto_review:
    enabled: true
    auto_incremental_review: true
    auto_pause_after_reviewed_commits: 10
    drafts: false
    base_branches:
      - "develop"
      - "release/.*"
    ignore_title_keywords:
      - "WIP"
      - "[skip review]"
    labels:
      - "!do-not-review"
    ignore_usernames:
      - "dependabot[bot]"
      - "renovate[bot]"
      - "release-bot"
    description_keyword: ""
```

This configuration:

- Reviews all non-draft PRs automatically on each push
- Pauses after 10 reviewed commits
- Also reviews PRs targeting `develop` or any `release/*` branch
- Skips PRs titled with `WIP` or `[skip review]`
- Skips PRs labeled `do-not-review`
- Skips PRs from dependency bots and the release bot
