---
source: https://docs.coderabbit.ai/guides/code-review-overview
---

# Code Review Overview

Transform your code review process with CodeRabbit's AI-powered analysis that delivers comprehensive feedback within minutes of creating a pull request. Get detailed summaries, security insights, and improvement suggestions that help your team ship better code faster.

## What CodeRabbit does for your pull requests

CodeRabbit automatically analyzes every pull request with a multi-layered approach that combines the best of AI and industry-standard tools.

## How automatic reviews work

## Review types and severity levels

CodeRabbit categorizes its feedback into different types and severity levels to help you prioritize and address issues effectively.

### Review types

CodeRabbit provides three types of review feedback:

- **Potential issue** - Identifies potential bugs, security vulnerabilities, or problematic code patterns
- **Refactor suggestion** - Recommends code improvements for maintainability, performance, or best practices
- **Nitpick** - Suggests minor style or formatting improvements (only in Assertive mode)

### Severity levels

Each review comment is assigned a severity level to indicate its importance:

- **Critical** - Severe issues that could cause system failures, security breaches, or data loss
- **Major** - Significant problems that impact functionality or performance
- **Minor** - Issues that should be addressed but don't critically impact the system
- **Trivial** - Low-impact suggestions for code quality improvements
- **Info** - Informational comments or context without requiring action

### Review triggers and events

CodeRabbit automatically initiates reviews based on these repository activities:

**Full comprehensive review** when a new pull request is created:
- Complete analysis of all proposed changes
- Security and quality assessment
- Code style and best practices review

**Incremental review** when existing pull requests receive new commits:
- Focus on newly added changes
- Updates to previous recommendations
- Maintains conversation context

## Interactive code reviews with CodeRabbit

Once CodeRabbit reviews your pull request, you can engage in dynamic conversations and request specific actions by mentioning `@coderabbitai` in your comments.

### Smart conversation capabilities

Ask CodeRabbit questions about your code changes, architecture decisions, or implementation approaches. It has access to your entire repository for informed responses.

```
@coderabbitai Why did you suggest using a factory pattern here?
```

Manage CodeRabbit's review behavior for specific pull requests:

```
@coderabbitai pause
@coderabbitai resume
@coderabbitai resolve
```

Request CodeRabbit to generate documentation:

```
@coderabbitai generate docstrings
```

## Next steps

Ready to dive deeper into CodeRabbit's capabilities? Explore these essential features to maximize your code review experience.
