---
source: https://docs.coderabbit.ai/knowledge-base
---

# Knowledge Base

CodeRabbit's knowledge base is the collection of context sources it draws on to make reviews smarter than a plain diff analysis. When CodeRabbit reviews a pull request, it combines several signals: what your team has taught it, the coding rules already in your repo, related code in linked repositories, external documentation fetched from the web, connected MCP servers, and issues or past PRs that provide business context.

This section documents each context source, how to configure it, and when you need to take action to enable it.

## Context sources

## Learnings

Adaptive AI memory. CodeRabbit learns your team's review preferences from natural-language chat and applies them automatically to future reviews.

## Code Guidelines

Auto-detected team rules. CodeRabbit reads coding standards from `.cursorrules`, `CLAUDE.md`, `.github/copilot-instructions.md`, and other AI agent configuration files — no manual import required.

## Multi-repo Analysis

Cross-repository context. Link related repositories so CodeRabbit can detect breaking changes, API mismatches, and dependency issues that cross repo boundaries.

## MCP Servers

External tool context via the Model Context Protocol. Connect MCP servers to give CodeRabbit access to internal APIs, databases, or documentation systems during reviews.

## Web Search

Up-to-date external documentation. CodeRabbit searches the web to gather context about libraries, APIs, and standards referenced in a pull request.

## Linked Issues

Issue tracker context. CodeRabbit reads linked GitHub, GitLab, Jira, and Linear issues to understand the intent behind a pull request and validate that the changes address them.

## What's on by default vs. what needs setup

| Context source | Status | Notes |
| --- | --- | --- |
| Learnings | **On by default** | Starts learning from your first `@coderabbitai` chat interaction |
| Code guidelines | **On by default** | Reads supported config files automatically; no setup required |
| Web search | **On by default** | Enabled unless explicitly disabled |
| Pull request context | **On by default** | Uses past PRs for context; scope configurable |
| GitHub / GitLab issues | **On by default (private repos)** | `auto` scope; enabled for private repos, isolated for public |
| Multi-repo analysis | **Needs setup** | Requires linking repositories in `.coderabbit.yaml` or the UI |
| MCP servers | **Needs setup** | Requires an MCP integration to be configured |
| Jira | **Needs setup** | Requires Jira integration and an active connection |
| Linear | **Needs setup** | Requires Linear integration and an active connection |

## Issue trackers and past pull requests

CodeRabbit can pull context from issue trackers and your PR history using four `knowledge_base` configuration fields:

- **`knowledge_base.issues`** — scope for GitHub and GitLab issues (`local`, `global`, or `auto`; default: `auto`)
- **`knowledge_base.jira`** — use Jira as a knowledge source (`auto`, `enabled`, or `disabled`; default: `auto`); supports `project_keys` to restrict to specific projects
- **`knowledge_base.linear`** — use Linear as a knowledge source (`auto`, `enabled`, or `disabled`; default: `auto`); supports `team_keys` to restrict to specific teams
- **`knowledge_base.pull_requests`** — scope for past PR context (`local`, `global`, or `auto`; default: `auto`)

For Jira and Linear, `auto` means the integration is active for private repositories and disabled for public ones. See PR validation and linked issues for how CodeRabbit uses this context during reviews. See the configuration reference for all available options.

## Global configuration

### Opt out of data retention

All context sources that learn from your repository — including learnings, issues, and PR context — require CodeRabbit to retain data about your organization's usage. To disable these features and remove any stored data, set `knowledge_base.opt_out` to `true`:

```
# yaml-language-server: $schema=https://coderabbit.ai/integrations/schema.v2.json
knowledge_base:
  opt_out: true
```

### Full configuration reference

For a complete list of `knowledge_base` options including scope values, file patterns, and integration keys, see the Knowledge base section of the configuration reference.
