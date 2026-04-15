---
source: https://docs.coderabbit.ai/integrations/linear
---

# Linear Integration

Connect CodeRabbit to Linear to enrich pull request reviews with issue context, validate changes against acceptance criteria, create issues from review comments, and design Coding Plans.

## Overview

The Linear integration connects CodeRabbit to your Linear workspace, bringing issue context into every stage of development. Here's what the integration enables:

## Prerequisites

Before setting up the Linear integration, ensure you have:

- A Linear account with access to the workspace you want to connect
- A CodeRabbit Pro plan

## Install the Linear integration

The Linear integration uses OAuth authentication to securely connect your Linear workspace to CodeRabbit.

## Configure CodeRabbit for Linear

After connecting Linear, configure which Linear teams CodeRabbit should access by adding your team keys. The team key is a short team identifier—for example, if your issue URL is `https://linear.app/company/issue/DEV-123`, the team key is `DEV`.

- YAML Configuration
- Web Interface

Add the `team_keys` setting under `knowledge_base.linear` in your `.coderabbit.yaml` file:

```
# yaml-language-server: $schema=https://coderabbit.ai/integrations/schema.v2.json
knowledge_base:
  linear:
    usage: "enabled"
    team_keys:
      - "DEV"
      - "ENG"

chat:
  integrations:
    linear:
      usage: "enabled"
```

The `usage` setting controls when the integration is active:

- `auto` (default): Disabled for public repositories, enabled for private repositories
- `enabled`: Always enabled
- `disabled`: Always disabled

1. Navigate to your repository or organization settings in the CodeRabbit app
2. Go to **Configuration** → **Knowledge Base**
3. Under **Linear**, add your team keys
4. Save the configuration

## Example usage

### Linking Linear issues to pull requests

To have CodeRabbit validate requirements from a Linear issue, include the issue URL in your pull request description:

```
This PR implements the user authentication flow.

Closes https://linear.app/company/issue/DEV-123
```

CodeRabbit will fetch the issue details and assess whether your code changes address the requirements specified in the issue. See the Linked issues guide for best practices on linking issues.

### Creating Linear issues from reviews

During a code review, you can ask CodeRabbit to create a Linear issue by mentioning `@coderabbitai` in a comment:

```
@coderabbitai create a Linear issue for this bug in the DEV team
```

CodeRabbit will create a well-structured issue with relevant context from the code review discussion. See the Issue creation guide for more details.

## Requirement validation

Best practices for linking issues to pull requests

## Issue planning

Generate Coding Plans from issues for coding agents

## Issue creation

Create issues directly from CodeRabbit reviews
