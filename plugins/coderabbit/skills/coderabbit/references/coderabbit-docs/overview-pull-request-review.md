---
source: https://docs.coderabbit.ai/overview/pull-request-review
---

# Pull Request Reviews

Within moments of opening a pull request, CodeRabbit analyzes your code with multiple AI models and provides actionable feedback, catching issues that are easy to miss in manual reviews.

## Automatic and incremental

CodeRabbit reviews new pull requests automatically and updates its feedback as you push new commits -- focusing on what changed.

- **New PRs**: Full analysis of all changes with detailed findings
- **New commits**: Incremental reviews that track what's new since the last review
- **Every update**: Fresh insights without repeating resolved comments

Zero config to start: just open a PR and get the results! This documentation will guide you through review instructions, focus areas, and review style tuning to make the outcome even better.

## Connected to your workflow

CodeRabbit links relevant issues from GitHub, Jira, or Linear to your pull requests, ensuring nothing falls through the cracks. It validates changes against issue requirements and acceptance criteria, catching misalignments before merge.
No more hunting through issue trackers to understand what a PR should accomplish, context is right there when you need it.

## Beyond your CI/CD pipeline

While your linters catch style issues and security scanners flag known vulnerabilities, CodeRabbit understands context:

- Detects bugs that static analyzers miss
- Suggests architecture improvements based on your full repository
- Identifies performance bottlenecks in your logic
- Points out maintainability issues before they compound

Think of it as an experienced teammate who's always available for that first review. The same second!

## Keep the conversation going

Every review comment is the start of a conversation. Reply to ask for clarification, request code examples, or discuss alternatives:

```
@coderabbitai Suggest a better approach for this error handling
```

CodeRabbit has full repository context and can explain its reasoning, generate code, or adjust suggestions based on your feedback.

## What's next

Pull request reviews are just the beginning. CodeRabbit also works in your IDE and from the command line, bringing AI assistance directly into your development workflow.
