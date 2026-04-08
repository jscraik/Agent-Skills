---
source: https://docs.coderabbit.ai/reference/review-commands
---

Complete reference of CodeRabbit commands for controlling code reviews, generating documentation, and managing pull requests.

All commands must be used with the `@coderabbitai` mention in PR comments or descriptions to trigger CodeRabbit's response.

## Review control commands

These commands control CodeRabbit's automatic review behavior for your pull request.

### Manual review triggers

**@coderabbitai review**

Description: Triggers an incremental review of new changes only
Usage: Post as a comment in your pull request
When to use:
- Automatic reviews are disabled
- You want to manually request a review of recent changes
- You've made updates and want focused feedback on new code

```
@coderabbitai review
```

**@coderabbitai full review**

Description: Performs a complete review of all files from scratch
Usage: Post as a comment in your pull request
When to use:
- You want fresh insights on the entire PR
- Previous reviews may have missed something
- You've made significant changes affecting the overall logic

```
@coderabbitai full review
```

### Review flow control

**@coderabbitai pause**

Description: Temporarily stops automatic reviews on the PR
Usage: Post as a comment in your pull request

```
@coderabbitai pause
```

**@coderabbitai resume**

Description: Restarts automatic reviews after a pause

```
@coderabbitai resume
```

**@coderabbitai ignore**

Description: Permanently disables automatic reviews for this PR
Usage: Add anywhere in the pull request description
Note: This command must be placed in the PR description, not in comments. To re-enable reviews, remove this text from the description.

```
@coderabbitai ignore
```

## Content generation commands

**@coderabbitai summary**

A placeholder in your PR description that gets replaced with CodeRabbit's high-level summary of the changes.

**@coderabbitai generate docstrings**

Generates docstrings for functions and classes in the PR. Must be enabled in configuration under `reviews.finishing_touches.docstrings.enabled`.

**@coderabbitai generate unit tests**

Generates unit tests for the code in the PR. Must be enabled in configuration under `reviews.finishing_touches.unit_tests.enabled`.

**@coderabbitai generate sequence diagram**

Creates a sequence diagram visualizing the PR's history and changes.

## Comment management

**@coderabbitai resolve**

Marks all CodeRabbit review comments as resolved. This will resolve ALL CodeRabbit comments.

## Information and configuration

**@coderabbitai configuration**

Displays current CodeRabbit configuration settings.

**@coderabbitai help**

Shows a quick reference guide of available commands.

## Command reference table

| Command | Type | Description | Location |
| --- | --- | --- | --- |
| `@coderabbitai review` | Review | Incremental review of new changes | PR comment |
| `@coderabbitai full review` | Review | Complete review from scratch | PR comment |
| `@coderabbitai pause` | Control | Temporarily stop reviews | PR comment |
| `@coderabbitai resume` | Control | Restart reviews after pause | PR comment |
| `@coderabbitai ignore` | Control | Permanently disable reviews | PR description |
| `@coderabbitai summary` | Content | Regenerate PR summary | PR comment |
| `@coderabbitai generate docstrings` | Content | Generate function documentation | PR comment |
| `@coderabbitai generate unit tests` | Content | Generate test cases | PR comment |
| `@coderabbitai generate sequence diagram` | Content | Create visual diagram | PR comment |
| `@coderabbitai resolve` | Management | Resolve all CR comments | PR comment |
| `@coderabbitai configuration` | Info | Show current settings | PR comment |
| `@coderabbitai help` | Info | Show command reference | PR comment |

## Related configuration

- **Automatic reviews**: `reviews.auto_review.enabled`
- **Docstring generation**: `reviews.finishing_touches.docstrings.enabled`
- **Unit test generation**: `reviews.finishing_touches.unit_tests.enabled`
- **High-level summaries**: `reviews.high_level_summary`
- **Sequence diagrams**: `reviews.sequence_diagrams`
