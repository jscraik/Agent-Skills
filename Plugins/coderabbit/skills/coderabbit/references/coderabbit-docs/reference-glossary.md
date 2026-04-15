---
source: https://docs.coderabbit.ai/reference/glossary
---

Definitions of CodeRabbit-specific terms and Git platform terminology used throughout the documentation.

## CodeRabbit terms

### Code Guidelines

Files in your repository that describe your team's coding standards, such as `.cursorrules`, `CLAUDE.md`, or `AGENTS.md`. CodeRabbit reads these files and applies them as review criteria.

### Finishing Touches

Automated actions in the PR for common cleanup tasks like generating docstrings and writing unit tests.

### Fortune

A random fun fact, tip, or trivia message displayed in the Walkthrough while CodeRabbit is still processing the review.

### High-Level Summary

An AI-generated summary of a PR's purpose and key changes, written for human reviewers.

### Incremental Review

When new commits are pushed to a PR that has already been reviewed, CodeRabbit can re-review focusing on just the new changes rather than starting from scratch.

### Knowledge Base

The collected context CodeRabbit draws on during reviews. This includes Learnings, issues, past PRs, Code Guidelines files, and integrations with Jira, Linear, and MCP servers.

### Learnings

When you respond to CodeRabbit's review comments, CodeRabbit remembers that preference and applies it to future reviews. These remembered preferences are called learnings.

### Path Filters

Glob patterns that control which files CodeRabbit includes in or excludes from a review.

### Path-based Instructions

Custom review rules that only apply to files matching a glob pattern.

### Pre-Merge Checks

Validation rules CodeRabbit evaluates before a PR is merged. Built-in checks include docstring coverage, PR title quality, PR description completeness, and linked issue assessment.

### Profile (Chill / Assertive)

Controls how much feedback CodeRabbit gives. **Chill** focuses on important issues. **Assertive** provides comprehensive feedback including style and best practices.

### Request Changes Workflow

A two-step automation: CodeRabbit submits a "Request changes" review when it finds issues, then automatically switches to "Approve" once all comments are resolved.

### Tone Instructions

A free-text field where you describe how CodeRabbit should communicate.

### Walkthrough

The main summary comment that CodeRabbit posts on every PR. Multi-section overview of everything that changed.

## Git platform terms

### Base Branch

The branch that a PR is merging changes into.

| GitHub | GitLab | Bitbucket | Azure DevOps |
| --- | --- | --- | --- |
| Base branch | Target branch | Destination branch | Target branch |

### Head / Source Branch

The branch that contains the new changes being proposed in the PR.

| GitHub | GitLab | Bitbucket | Azure DevOps |
| --- | --- | --- | --- |
| Head branch | Source branch | Source branch | Source branch |

### Status Check

| GitHub | GitLab | Bitbucket | Azure DevOps |
| --- | --- | --- | --- |
| Status checks | External status checks | Build status | PR status |

### Labels

| GitHub | GitLab | Bitbucket | Azure DevOps |
| --- | --- | --- | --- |
| Labels | Labels | Not supported natively | Labels |

## General terms

### Docstring

A documentation comment embedded directly in source code.

### Glob Pattern

A file-matching syntax using wildcards. `*` matches any filename, `**` matches any directory depth, `!` prefix excludes.

### MCP

Model Context Protocol -- an open standard for connecting AI tools to external data sources and services.

### Regex

Regular expressions -- a pattern-matching syntax more powerful than glob.

### Sequence Diagram

A standard UML diagram type that shows the order of interactions between components over time.
