---
source: https://docs.coderabbit.ai/issues/planner
---

# Issue Planner

Turn issues into comprehensive Coding Plans ready for your favorite coding agent or IDE copilot. Works with Jira, Linear, GitHub, and GitLab.

CodeRabbit analyzes your issues, specifications, and project codebase to generate Coding Plans you can hand off to any coding agent or IDE copilot. Because CodeRabbit deeply understands your codebase through continuous analysis, each plan is tailored to your architecture and conventions, covering codebase research, step-by-step tasks, and agent-ready prompts.

## Supported Issue Trackers

CodeRabbit supports four issue trackers for plan generation. See the platform-specific guides for setup and configuration details.

## Planning

The recommended way to use issue planning is to **enable auto-planning** on your platform so that Coding Plans are generated automatically whenever issues match the conditions you configure. Refer to the platform-specific guides above to set up auto-planning.
To generate a plan on demand, comment `@coderabbitai plan` on any issue.

## Viewing and Refining Plans

How you view and refine Coding Plans depends on your platform:

### Plan Structure

Each Coding Plan contains the following sections:

| Section | Description |
| --- | --- |
| **Summary** | 2-3 sentence overview of the implementation approach |
| **Research** | Deep codebase analysis leveraging CodeRabbit's project knowledge, identifying relevant files, patterns, dependencies, and architectural decisions specific to the project |
| **Design Choices** | Decisions made during planning with rationale for each |
| **Phases** | Logical chunks of work that should be done together |
| **Tasks** | Individual tasks within each phase |
| **Agent Prompt** | Machine-readable instructions for coding agents (per phase and combined) |

### Chatting about Your Plan

Chat with CodeRabbit to ask questions, request changes to specific tasks or phases, challenge design choices, or get clarification on implementation details. CodeRabbit responds and updates the plan accordingly. See the platform-specific guides for details on how chatting works on your platform.

### Re-planning

Provide feedback and regenerate your plan to incorporate changes. See the platform-specific guides for details on the re-planning workflow.

### Handing off to a Coding Agent

Once you're satisfied with a Coding Plan, copy the agentic prompts and paste them into your preferred coding agent (Claude Code, Cursor, GitHub Copilot, etc.). Depending on the platform, you can also hand off directly through the CodeRabbit IDE extension or ask an agent with direct platform access (for example, GitHub or GitLab MCP) to fetch the issue and execute CodeRabbit's plan. See the platform-specific guides for handoff options.

## Frequently Asked Questions

### How long does plan generation take?

Plan generation typically takes between 5 and 10 minutes depending on the complexity of the issue and codebase.

### Can I regenerate a plan?

Yes. You can regenerate a plan on all supported platforms. See your platform's guide for specific instructions.

### Can multiple people work on the same plan?

Yes. Anyone in your organization can view plans, discuss them with CodeRabbit, and trigger re-plans.

### How is CodeRabbit different from using ChatGPT or coding agents for planning?

Any AI agent or LLM can write an implementation plan. The difference is in the quality and context behind that plan:

1. **Deeper codebase understanding** - When an AI agent generates a plan, it typically reviews only a handful of files. CodeRabbit's Coding Plans are grounded in deep codebase understanding through continuous code analysis and an extensive knowledge base.
2. **Access to issues and better context** - CodeRabbit works with issue trackers, surfacing relevant related issues, even when the assigned engineer isn't aware of them.
3. **Collaborative review** - CodeRabbit plans are available for review by other engineers and product owners. Team members can discuss, challenge design choices, and refine plans together before implementation begins.
4. **Accountability and history** - Every plan version is preserved. You can track what was planned, when it was planned, and why decisions were made.
