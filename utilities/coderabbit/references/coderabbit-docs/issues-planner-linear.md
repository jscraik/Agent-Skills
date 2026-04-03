---
source: https://docs.coderabbit.ai/issues/planner/linear
---

# Planning on Linear

Generate comprehensive Coding Plans from your issues using Linear issue tracker.

## Prerequisites

Enable the Linear integration as explained in integrations documentation

## Initiating Planning

### Manual Planning

### Auto-Planning (Recommended)

Navigate to the **Planning** tab in the CodeRabbit web app to configure automatic planning rulesets.

A ruleset consists of conditions that, when met, automatically trigger plan generation. All conditions are optional—you can use any combination that fits your workflow:

| Condition | Description |
| --- | --- |
| **Issue Type** | Match specific issue types (e.g., Bug, Feature, Task) |
| **Labels** | Match issues with specific labels |
| **Assignee** | Match issues assigned to specific users |
| **Status** | Match issues in specific statuses (e.g., Ready, In Progress) |

You can create multiple rulesets with different combinations of conditions. A plan is triggered when any ruleset matches.

## Repository Resolution

Since Linear issues aren't tied to a specific repository, CodeRabbit needs to determine which repository to analyze when generating a plan.
CodeRabbit attempts to resolve the repository in this order:

## Viewing and Refining Plans

Once a Coding Plan is generated, view it in the CodeRabbit web app. Anyone in your organization can view and work with the plans.

### Chatting about Your Plan

Use the chat panel on the right side of the plan viewer in the CodeRabbit web app to:

- Ask questions about the plan or the codebase
- Request changes to specific tasks or phases
- Challenge design choices and provide additional context
- Get clarification on implementation details

### Re-planning

After providing feedback through chat:

1. Review your feedback in the chat history
2. Click the **Redo** button
3. CodeRabbit generates a new plan version incorporating your feedback

### Version History

Each re-plan creates a new version. Use the version selector at the top of the plan viewer to:

- View previous versions
- Compare what changed between versions
- Revert to an earlier version by marking it as active

### Handing off to a Coding Agent

Click the **Handoff** button at the bottom of the plan viewer to see your options:

#### Copy to Clipboard

Copy the agentic prompts to your clipboard, then paste them into your preferred coding agent (Claude Code, Cursor, GitHub Copilot, etc.).

#### IDE Extension

If you have the CodeRabbit IDE extension installed, the Coding Plan can be sent directly to your coding agent through the extension. The agentic prompts appear in your coding agent's input field, ready to execute.
If you don't have the extension installed, you'll be prompted to install it.
