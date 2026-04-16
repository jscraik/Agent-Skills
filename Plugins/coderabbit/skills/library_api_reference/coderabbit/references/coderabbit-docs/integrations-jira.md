---
source: https://docs.coderabbit.ai/integrations/jira
---

# Jira Integration

Connect CodeRabbit to Jira to enrich pull request reviews with issue context, validate changes against acceptance criteria, create issues from review comments, and design Coding Plans.

## Overview

The Jira integration connects CodeRabbit to your Jira workspace, bringing issue context into every stage of development. Here's what the integration enables:

## Prerequisites

Before setting up the Jira integration, ensure you have:

- A **Jira Cloud** account (for Jira Data Center or self-hosted, see Jira Data Center below)
- Admin access to install apps on your Jira site
- A CodeRabbit Pro plan

## Install the Jira Cloud integration

The Jira Cloud integration uses a Forge app from the Atlassian Marketplace. Follow these steps to connect your Jira site to CodeRabbit:

## Jira Data Center (Self-Hosted)

For self-hosted Jira Data Center installations, a different setup process applies.

## Configure CodeRabbit for Jira

After connecting Jira, configure which Jira projects CodeRabbit should access by adding your project keys. The project key is the prefix that appears before issue numbers—for example, if your issue URL is `https://company.atlassian.net/browse/PROJ-123`, the project key is `PROJ`.

- YAML Configuration
- Web Interface

Add the `project_keys` setting under `knowledge_base.jira` in your `.coderabbit.yaml` file:

```
# yaml-language-server: $schema=https://coderabbit.ai/integrations/schema.v2.json
knowledge_base:
  jira:
    usage: "enabled"
    project_keys:
      - "PROJ"
      - "DEV"
      - "BACKEND"

chat:
  integrations:
    jira:
      usage: "enabled"
```

The `usage` setting controls when the integration is active:

- `auto` (default): Disabled for public repositories, enabled for private repositories
- `enabled`: Always enabled
- `disabled`: Always disabled

1. Navigate to your repository or organization settings in the CodeRabbit app
2. Go to **Configuration** → **Knowledge Base**
3. Under **Jira**, add your project keys
4. Save the configuration

## Example usage

### Linking Jira issues to pull requests

To have CodeRabbit validate requirements from a Jira issue, include the issue URL in your pull request description:

```
This PR implements the user authentication flow.

Closes https://company.atlassian.net/browse/PROJ-123
```

CodeRabbit will fetch the issue details and assess whether your code changes address the requirements specified in the issue. See the Linked issues guide for best practices on linking issues.

### Creating Jira issues from reviews

During a code review, you can ask CodeRabbit to create a Jira issue by mentioning `@coderabbitai` in a comment:

```
@coderabbitai create a Jira issue for this technical debt in the PROJ project
```

CodeRabbit will create a well-structured issue with relevant context from the code review discussion. See the Issue creation guide for more details.

## Requirement validation

Best practices for linking issues to pull requests

## Issue Planning

Generate Coding Plans from issues for coding agents

## Issue creation

Create issues directly from CodeRabbit reviews
