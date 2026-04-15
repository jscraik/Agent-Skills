---
source: https://docs.coderabbit.ai/overview/coderabbit-plan
---

# CodeRabbit Plan

Turn ideas, issues, PRDs, and designs into precise Coding Plans grounded in your codebase, then hand them off to any coding agent.

CodeRabbit Plan turns your ideas into detailed, project-aware Coding Plans you can review, refine, and hand off to any coding agent. Because every plan is grounded in deep codebase understanding and enriched by your project Knowledge Base, it references the right files, follows your established patterns, and produces agent-ready prompts, not generic outlines.

## 1. Create a plan

- Using web interface
- Using issue tracker

The fastest way to get started is the CodeRabbit web app. Go to app.coderabbit.ai/plan, describe what you want to build in a free-form text, select a repository, and click **Create plan**. The form also supports file attachments. See the Create a plan guide for the full step-by-step walkthrough.

You can generate Coding Plans directly from your issue tracker. Comment `@coderabbitai plan` on any issue, or enable auto-planning to generate plans automatically when issues match your rules.

### GitHub

### GitLab

### Jira

### Linear

### Codebase understanding

Analyzes your repository's architecture, patterns, and existing code so every plan fits naturally into how your project is built.

### Project context

Draws on related issues, design documents, and accumulated learnings to ground every plan in your project's broader context.

## 2. Refine

Chat with CodeRabbit to refine details, challenge design choices, or request changes. The conversation is collaborative: product owners and other team members can participate too, ensuring the plan reflects the team's knowledge.

- Web app
- Issue Trackers (GitHub & GitLab)

Review, tune, and adjust your Coding Plan in the CodeRabbit web app. Use the chat panel to iterate on the plan until it's ready.

![Coding Plan in the CodeRabbit web app](https://mintcdn.com/coderabbit/0_UNDuRPehZvImxS/assets/images/plan-editor.png?fit=max&auto=format&n=0_UNDuRPehZvImxS&q=85&s=675d1c116a50b922932579684cb300c3)

The full Coding Plan is posted as a comment directly on the issue. Reply to the plan comment to refine details, challenge design choices, or request changes.

![Coding Plan posted as a comment on a GitHub issue](https://mintcdn.com/coderabbit/0_UNDuRPehZvImxS/assets/images/planning-github-comment.png?fit=max&auto=format&n=0_UNDuRPehZvImxS&q=85&s=720c50d5d557a1e5bc8838b37d0645f9)

### Collaborative Planning

Plans are available for review by engineers and product owners. Team members discuss, challenge design choices, and refine plans together.

### Accountability and history

Every plan version is preserved. Track what was planned, when it was planned, and why decisions were made.

## 3. Handoff

Once the plan reflects the team's decisions, hand off the finalized prompts to your coding agent of choice. The agent receives precise, codebase-aware instructions it can act on immediately.

### Agent-ready prompts

Finalized plans are exported as structured, codebase-aware prompts that any coding agent can act on immediately -- no reinterpretation required.

### Any coding agent

Hand off to Claude Code, Codex, Cursor, Gemini, or any other coding agent. The prompt format is agent-agnostic.

## What's next

### CodeRabbit Plan documentation

Full documentation covering the web interface, plan structure, refinement, and Agent Handoff.

### Issue-based planning guides

Platform-specific guides for generating Coding Plans from GitHub, GitLab, Jira, and Linear issues.

### CodeRabbit architecture

The system behind every Coding Plan and review comment.
