---
source: https://docs.coderabbit.ai/plan/agent-handoff
---

# Agent Handoff

Copy agent-ready prompts from a Coding Plan and hand them off to your preferred coding agent or IDE.

Once you are satisfied with a Coding Plan, Agent Handoff lets you select specific phases and produce precise, context-rich prompts ready for any coding agent. The prompts include all the context an agent needs: file paths, implementation details, and design decisions. This lets you use faster, cheaper models for execution without sacrificing quality.

## How Agent Handoff works

1. **Open the plan detail view** -- In the CodeRabbit web app, navigate to the plan you want to hand off.

2. **Select phases** -- Choose the phases you want to hand off. You can select individual phases for focused work, or select all phases for a complete handoff.

3. **Click Agent Handoff** -- Open the Agent Handoff panel to see your output options.

4. **Choose an output method** -- Pick how you want to deliver the prompt to your coding agent:
   - **Copy to clipboard:** Paste the prompt into any agent (Claude Code, GitHub Copilot, Cursor, or any other).
   - **Send to IDE:** Push the prompt directly to Cursor, VS Code, or Windsurf through the CodeRabbit IDE extension.

## Supported agents and IDEs

Agent Handoff produces standard prompts that work with any coding agent. Additionally, the CodeRabbit IDE extension enables direct handoff to supported editors.

| Target | Method |
| --- | --- |
| **Cursor** | Direct via IDE extension or copy to clipboard |
| **VS Code** and extensions | Direct via IDE extension or copy to clipboard |
| **Windsurf** | Direct via IDE extension or copy to clipboard |
| **Claude Code** | Copy to clipboard |
| **GitHub Copilot** | Copy to clipboard |
| **Any clipboard agent** | Copy to clipboard |

For direct IDE handoff, install the CodeRabbit IDE extension first.

## Tips for effective handoff

- Some coding agents may perform better with focused, sequential instructions rather than everything at once. Consider **handing off one phase at a time** for complex plans.
- **Review the generated prompt before pasting.** The prompt is editable, so you can add clarifications or remove sections the agent doesn't need.
- **Match the model to the task.** Because the plan already contains precise instructions, you can often use faster or cheaper models for execution without losing quality.

## What's next

### CodeRabbit IDE extension

Install the extension to enable direct plan handoff to Cursor, VS Code, and Windsurf.

### CodeRabbit Plan for issue trackers

Turn issues from Jira, Linear, GitHub, or GitLab into structured Coding Plans ready for any coding agent.
