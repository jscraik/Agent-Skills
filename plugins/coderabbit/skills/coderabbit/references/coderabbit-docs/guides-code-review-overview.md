---
source: https://docs.coderabbit.ai/guides/code-review-overview
---

# Code Review Overview

Transform your code review process with CodeRabbit's AI-powered analysis that delivers feedback within minutes of opening a pull request. You get summaries, security insights, and improvement suggestions that help teams ship higher-quality code faster.

## What CodeRabbit does for pull requests

CodeRabbit automatically analyzes pull requests with a multi-layer approach that combines AI and industry-standard tooling.

## Review types and severity levels

CodeRabbit categorizes feedback so teams can prioritize issues.

### Review types

- **Potential issue**: Potential bugs, security vulnerabilities, or risky code patterns.
- **Refactor suggestion**: Improvements for maintainability, performance, or best practices.
- **Nitpick**: Minor style and formatting suggestions (Assertive mode).

### Severity levels

- **Critical**: Could cause outages, data loss, or severe security impact.
- **Major**: Significant functional or performance concerns.
- **Minor**: Important improvements with lower immediate impact.
- **Trivial**: Low-impact code-quality suggestions.
- **Info**: Informational context that may not require action.

## Review triggers

**Full review** on new pull requests:
- Complete analysis of proposed changes
- Security and quality assessment
- Style and best-practice checks

**Incremental review** on new commits to existing pull requests:
- Focus on newly introduced changes
- Update recommendations as the PR evolves
- Preserve ongoing context

## Interactive code reviews with `@coderabbitai`

After CodeRabbit posts feedback, you can ask follow-up questions and request actions directly in PR comments.

CodeRabbit can use the repository context available to the pull request when generating responses.

```text
@coderabbitai Why did you suggest using a factory pattern here?
```

```text
@coderabbitai pause
@coderabbitai resume
@coderabbitai resolve
```

```text
@coderabbitai generate docstrings
```

## Next steps

Explore related guides to tune review instructions, focus areas, and review style for your team.
