---
source: https://docs.coderabbit.ai/overview/pull-request-review
---

# Pull Request Reviews

Within moments of opening a pull request, CodeRabbit analyzes your code with multiple AI models and provides actionable feedback that can be easy to miss in manual reviews.

## Automatic and incremental

CodeRabbit reviews new pull requests automatically and updates feedback as you push new commits.

- **New PRs**: Full analysis of changed files with detailed findings.
- **New commits**: Incremental analysis focused on newly introduced deltas.
- **Every update**: Fresh insights without repeating resolved comments.

Zero config to start: open a PR and review the results. You can then tune review instructions, focus areas, and style.

## Connected to your workflow

CodeRabbit links relevant issues from GitHub, Jira, or Linear to pull requests. It validates changes against issue intent and acceptance criteria so mismatches can be caught before merge.

## Beyond CI/CD checks

Linters and scanners are essential, but CodeRabbit also reasons about code behavior in context:

- Finds logic issues that static analyzers may miss
- Suggests design or architecture improvements using relevant repository context
- Flags potential performance bottlenecks
- Highlights maintainability concerns early

## Keep the conversation going

Every review comment can be continued as a conversation. Ask for clarification, alternatives, or concrete examples:

```text
@coderabbitai Suggest a better approach for this error handling
```

CodeRabbit can explain reasoning and adjust recommendations based on follow-up context.

## What's next

Pull request reviews are only one workflow surface. CodeRabbit can also run in IDE and CLI workflows.
