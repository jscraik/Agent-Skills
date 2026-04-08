---
source: https://docs.coderabbit.ai/issues/enrichment
---

# Issue Enrichment

CodeRabbit automatically analyzes your issues to detect duplicates, find related issues and PRs, suggest assignees, and apply smart labels.

## Overview

CodeRabbit Issue Enrichment automatically analyzes your issues and provides contextual
insights to help you work more efficiently. When you create or edit an issue, CodeRabbit
posts a comment with:

- Duplicate Detection - Identifies if your issue already exists
- Similar Issues - Shows related issues that might have solutions or context
- Related Pull Requests - Finds PRs that addressed similar problems
- Suggested Assignees - Recommends team members based on expertise
- Smart Labeling - Automatically categorizes issues with appropriate labels

## Platform Support

Issue enrichment is currently available for **GitHub Issues** - Full enrichment support including duplicate detection, similar issues, related PRs, suggested assignees, and smart labeling.

## Getting Started

Issue enrichment is enabled by default on GitHub issues. CodeRabbit will automatically enrich new issues with contextual information.

### Disable Issue Enrichment

To turn off automatic enrichment, add this to your `.coderabbit.yaml` configuration file:

```
issue_enrichment:
  auto_enrich:
    enabled: false
```

## Features

### Duplicate Detection

CodeRabbit analyzes your issue against existing issues in your repository and knowledge
base to detect potential duplicates.

### Similar Issues

Discover related issues that might provide context, workarounds, or solutions.

### Related PRs

See PRs that addressed similar problems or touched related code.

### Suggested Assignees

Get smart recommendations for who should work on the issue based on past contributions
to related issues and PRs.

### Smart Auto-Labeling

Automatically apply appropriate labels to issues based on their content.

#### Configuration

```
issue_enrichment:
  labeling:
    auto_apply_labels: true
    labeling_instructions:
      - label: bug
        instructions: Issues reporting bugs, errors, crashes, incorrect behavior, or unexpected results.
      - label: enhancement
        instructions: Feature requests, improvements to existing functionality, performance optimizations.
      - label: documentation
        instructions: Documentation updates, additions, corrections, or clarifications needed.
```

## Frequently Asked Questions

### Can I customize what information is shown?

Currently, the enrichment format is standardized, but you can customize label categories with auto-labeling and configure auto-planning to choose which issues get plans.

### Does enrichment work for private repositories?

Yes! Issue enrichment works for both public and private repositories. Knowledge base and enrichment respect your repository access controls.

### How does CodeRabbit find related issues and PRs?

CodeRabbit uses semantic similarity search on your knowledge base by indexing issues and PRs based upon vectorized representations (which cannot be reversed into the original issues and PR's).

### Will enrichment update when I edit the issue?

Yes! When you edit an issue that already has enrichment, CodeRabbit will re-analyze the updated content, search for new related issues and PRs, update the enrichment comment, and trigger auto-planning if labels changed.
