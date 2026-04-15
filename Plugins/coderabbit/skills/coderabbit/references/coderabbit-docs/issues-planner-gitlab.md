---
source: https://docs.coderabbit.ai/issues/planner/gitlab
---

# Planning on GitLab

Generate comprehensive Coding Plans from your issues on the GitLab issue tracker.

## Prerequisites

### Webhook Configuration

For Issue Planner to work, your GitLab webhook must include the **Issues events** trigger. If you recently installed CodeRabbit, this trigger is **automatically configured** for you. No additional setup is required.
If you installed CodeRabbit before Issue Planner was available, you need to manually add the "Issues events" trigger to your webhook:
Go to **Settings → Webhooks** in your GitLab project or group, edit the webhook pointing to `https://coderabbit.ai/gitlabHandler`, enable **Issues events** under Trigger, and save.

## Initiating Planning

### Manual Planning

### Auto-Planning (Recommended)

Automatically generate plans when specific labels are added to issues.

- Using configuration file
- Using the Web Interface

```
issue_enrichment:
  planning:
    enabled: true
    auto_planning:
      enabled: true
      labels:
        - "plan-me" # Auto-plan issues with this label
        - "feature" # Also auto-plan these
        - "!no-plan" # Never auto-plan issues with this label
```

To configure auto-planning labels in the CodeRabbit web app:

1. Navigate to **Configuration → Issue Enrichment → Auto-Planning**
2. Enable **Automatic Planning**
3. Add your desired labels in the labels field:
   - Enter labels that should trigger auto-planning (e.g., `plan-me`, `feature`)
   - Use the `!` prefix for exclusion labels (e.g., `!no-plan`)
4. Save your configuration

The web interface provides the same functionality as the YAML configuration, allowing you to manage auto-planning labels without committing configuration files to your repository.

### Label Matching Rules

| Configuration | Behavior |
| --- | --- |
| Inclusion only (e.g., `feature`) | Only plans issues with at least one matching label |
| Exclusion only (e.g., `!wip`) | Plans all issues except those with excluded labels |
| Mixed (e.g., `feature`, `!wip`) | Plans issues that have an inclusion label AND don't have any exclusion labels |

## Viewing and Refining Plans

Once a Coding Plan is generated, CodeRabbit posts the full plan as a comment on the issue.

### Chatting about Your Plan

Reply to the Coding Plan comment on the issue to:

- Ask questions about the plan or the codebase
- Request changes to specific tasks or phases
- Challenge design choices and provide additional context
- Get clarification on implementation details

For example:

```
Can you add more detail to Phase 2 about error handling?
```

### Re-planning

Once asked to make changes, CodeRabbit will respond to your comment and update the plan accordingly. You can also comment `@coderabbitai plan` again on the issue to regenerate the plan from scratch.

### Handing Off to a Coding Agent

Copy the agentic prompts from the Coding Plan comment on the issue, and paste them into your preferred coding agent (Claude Code, Cursor, GitHub Copilot, etc.).
Alternatively, if your coding agent can access GitLab directly (for example, through the GitLab MCP), you can simply ask it to `fetch the issue by its number and execute CodeRabbit's plan`.
