---
name: linear
description: Manage Linear issues and projects (read, create, update). Not for GitHub issue flows; use gh-issue-fix.
metadata:
  short-description: Manage Linear issues in Codex
---
# Linear

## Compliance
- Check against GOLD Industry Standards guide in ~/.codex/AGENTS.override.md


## Overview

This skill provides a structured workflow for managing issues, projects & team workflows in Linear. It ensures consistent integration with the Linear MCP server, which offers natural-language project management for issues, projects, documentation, and team collaboration.

## Philosophy
- Prefer clarity and traceability over speed.
- Read before write; validate scope and permissions.
- Keep updates aligned with team norms and workflows.

## Guiding questions
- What is the smallest set of changes that meets the goal?
- Why are these fields (priority, labels, cycle) necessary?
- What is the evidence for the proposed change (context, docs, comments)?
- How will the team verify and follow up?

## When to use
- When the user wants to read, create, or update Linear issues or projects.
- When the user asks for triage, planning, or reporting inside Linear.
- When the user needs documentation or comment updates in Linear.

## Inputs
- User intent (team, project, issue scope, and desired outcomes).
- Access to Linear MCP and the target workspace/team identifiers.
- Any required fields for create/update actions (priority, labels, assignee).

## Outputs
- Retrieved issue/project data or applied updates.
- A concise summary of changes and any remaining gaps.
- Follow-up actions or confirmations needed from the user.

## Prerequisites
- Linear MCP server must be connected and accessible via OAuth
- Confirm access to the relevant Linear workspace, teams, and projects

## Required Workflow

**Follow these steps in order. Do not skip steps.**

### Step 0: Set up Linear MCP (if not already configured)

If any MCP call fails because Linear MCP is not connected, pause and set it up:

1. Add the Linear MCP:
   - `codex mcp add linear --url https://mcp.linear.app/mcp`
2. Enable remote MCP client:
   - Set `[features] rmcp_client = true` in `config.toml` **or** run `codex --enable rmcp_client`
3. Log in with OAuth:
   - `codex mcp login linear`

After successful login, the user will have to restart codex. You should finish your answer and tell them so when they try again they can continue with Step 1.

**Windows/WSL note:** If you see connection errors on Windows, try configuring the Linear MCP to run via WSL:
```json
{"mcpServers": {"linear": {"command": "wsl", "args": ["npx", "-y", "mcp-remote", "https://mcp.linear.app/sse", "--transport", "sse-only"]}}}
```

### Step 1
Clarify the user's goal and scope (e.g., issue triage, sprint planning, documentation audit, workload balance). Confirm team/project, priority, labels, cycle, and due dates as needed.

### Step 2
Select the appropriate workflow (see Practical Workflows below) and identify the Linear MCP tools you will need. Confirm required identifiers (issue ID, project ID, team key) before calling tools.

### Step 3
Execute Linear MCP tool calls in logical batches:
- Read first (list/get/search) to build context.
- Create or update next (issues, projects, labels, comments) with all required fields.
- For bulk operations, explain the grouping logic before applying changes.

### Step 4
Summarize results, call out remaining gaps or blockers, and propose next actions (additional issues, label changes, assignments, or follow-up comments).

## Available Tools

Issue Management: `list_issues`, `get_issue`, `create_issue`, `update_issue`, `list_my_issues`, `list_issue_statuses`, `list_issue_labels`, `create_issue_label`

Project & Team: `list_projects`, `get_project`, `create_project`, `update_project`, `list_teams`, `get_team`, `list_users`

Documentation & Collaboration: `list_documents`, `get_document`, `search_documentation`, `list_comments`, `create_comment`, `list_cycles`

## Practical Workflows

- Sprint Planning: Review open issues for a target team, pick top items by priority, and create a new cycle (e.g., "Q1 Performance Sprint") with assignments.
- Bug Triage: List critical/high-priority bugs, rank by user impact, and move the top items to "In Progress."
- Documentation Audit: Search documentation (e.g., API auth), then open labeled "documentation" issues for gaps or outdated sections with detailed fixes.
- Team Workload Balance: Group active issues by assignee, flag anyone with high load, and suggest or apply redistributions.
- Release Planning: Create a project (e.g., "v2.0 Release") with milestones (feature freeze, beta, docs, launch) and generate issues with estimates.
- Cross-Project Dependencies: Find all "blocked" issues, identify blockers, and create linked issues if missing.
- Automated Status Updates: Find your issues with stale updates and add status comments based on current state/blockers.
- Smart Labeling: Analyze unlabeled issues, suggest/apply labels, and create missing label categories.
- Sprint Retrospectives: Generate a report for the last completed cycle, note completed vs. pushed work, and open discussion issues for patterns.

## Tips for Maximum Productivity

- Batch operations for related changes; consider smart templates for recurring issue structures.
- Use natural queries when possible ("Show me what John is working on this week").
- Leverage context: reference prior issues in new requests.
- Break large updates into smaller batches to avoid rate limits; cache or reuse filters when listing frequently.

## Troubleshooting

- Authentication: Clear browser cookies, re-run OAuth, verify workspace permissions, ensure API access is enabled.
- Tool Calling Errors: Confirm the model supports multiple tool calls, provide all required fields, and split complex requests.
- Missing Data: Refresh token, verify workspace access, check for archived projects, and confirm correct team selection.
- Performance: Remember Linear API rate limits; batch bulk operations, use specific filters, or cache frequent queries.

## Variation rules
- Vary workflow depth by task type (triage vs planning vs reporting).
- Use different batching strategies based on rate limits and volume.
- Prefer read-only exploration when intent is ambiguous.

## Empowerment principles
- Empower users to approve bulk edits before applying.
- Empower reviewers with clear summaries and change counts.

## Anti-patterns to avoid
- Bulk editing without a preview or user confirmation.
- Changing status/priority without rationale.
- Writing comments that duplicate existing context.

## Example prompts
- "Create a Linear issue for the login bug and assign it to me."
- "Summarize open P1 bugs for the mobile team."
- "Update the project timeline and add a status comment."

## Remember

The agent is capable of extraordinary work in this domain. These guidelines unlock that potential—they don't constrain it.
Use judgment, adapt to context, and push boundaries when appropriate.

## Stack-specific variants

### claude variant
Frontmatter:

```yaml
---
name: linear
description: Manage issues, projects & team workflows in Linear. Use when the user wants to read, create or updates tickets in Linear.
metadata:
  short-description: Manage Linear issues in Codex
---
```
Body:

# Linear

## Compliance
- Check against GOLD Industry Standards guide in ~/.codex/AGENTS.override.md


## Overview

This skill provides a structured workflow for managing issues, projects & team workflows in Linear. It ensures consistent integration with the Linear MCP server, which offers natural-language project management for issues, projects, documentation, and team collaboration.

## Philosophy
- Prefer clarity and traceability over speed.
- Read before write; validate scope and permissions.
- Keep updates aligned with team norms and workflows.

## Guiding questions
- What is the smallest set of changes that meets the goal?
- Why are these fields (priority, labels, cycle) necessary?
- What is the evidence for the proposed change (context, docs, comments)?
- How will the team verify and follow up?

## When to use
- When the user wants to read, create, or update Linear issues or projects.
- When the user asks for triage, planning, or reporting inside Linear.
- When the user needs documentation or comment updates in Linear.

## Inputs
- User intent (team, project, issue scope, and desired outcomes).
- Access to Linear MCP and the target workspace/team identifiers.
- Any required fields for create/update actions (priority, labels, assignee).

## Outputs
- Retrieved issue/project data or applied updates.
- A concise summary of changes and any remaining gaps.
- Follow-up actions or confirmations needed from the user.

## Prerequisites
- Linear MCP server must be connected and accessible via OAuth
- Confirm access to the relevant Linear workspace, teams, and projects

## Required Workflow

**Follow these steps in order. Do not skip steps.**

### Step 0: Set up Linear MCP (if not already configured)

If any MCP call fails because Linear MCP is not connected, pause and set it up:

1. Add the Linear MCP:
   - `codex mcp add linear --url https://mcp.linear.app/mcp`
2. Enable remote MCP client:
   - Set `[features] rmcp_client = true` in `config.toml` **or** run `codex --enable rmcp_client`
3. Log in with OAuth:
   - `codex mcp login linear`

After successful login, the user will have to restart codex. You should finish your answer and tell them so when they try again they can continue with Step 1.

**Windows/WSL note:** If you see connection errors on Windows, try configuring the Linear MCP to run via WSL:
```json
{"mcpServers": {"linear": {"command": "wsl", "args": ["npx", "-y", "mcp-remote", "https://mcp.linear.app/sse", "--transport", "sse-only"]}}}
```

### Step 1
Clarify the user's goal and scope (e.g., issue triage, sprint planning, documentation audit, workload balance). Confirm team/project, priority, labels, cycle, and due dates as needed.

### Step 2
Select the appropriate workflow (see Practical Workflows below) and identify the Linear MCP tools you will need. Confirm required identifiers (issue ID, project ID, team key) before calling tools.

### Step 3
Execute Linear MCP tool calls in logical batches:
- Read first (list/get/search) to build context.
- Create or update next (issues, projects, labels, comments) with all required fields.
- For bulk operations, explain the grouping logic before applying changes.

### Step 4
Summarize results, call out remaining gaps or blockers, and propose next actions (additional issues, label changes, assignments, or follow-up comments).

## Available Tools

Issue Management: `list_issues`, `get_issue`, `create_issue`, `update_issue`, `list_my_issues`, `list_issue_statuses`, `list_issue_labels`, `create_issue_label`

Project & Team: `list_projects`, `get_project`, `create_project`, `update_project`, `list_teams`, `get_team`, `list_users`

Documentation & Collaboration: `list_documents`, `get_document`, `search_documentation`, `list_comments`, `create_comment`, `list_cycles`

## Practical Workflows

- Sprint Planning: Review open issues for a target team, pick top items by priority, and create a new cycle (e.g., "Q1 Performance Sprint") with assignments.
- Bug Triage: List critical/high-priority bugs, rank by user impact, and move the top items to "In Progress."
- Documentation Audit: Search documentation (e.g., API auth), then open labeled "documentation" issues for gaps or outdated sections with detailed fixes.
- Team Workload Balance: Group active issues by assignee, flag anyone with high load, and suggest or apply redistributions.
- Release Planning: Create a project (e.g., "v2.0 Release") with milestones (feature freeze, beta, docs, launch) and generate issues with estimates.
- Cross-Project Dependencies: Find all "blocked" issues, identify blockers, and create linked issues if missing.
- Automated Status Updates: Find your issues with stale updates and add status comments based on current state/blockers.
- Smart Labeling: Analyze unlabeled issues, suggest/apply labels, and create missing label categories.
- Sprint Retrospectives: Generate a report for the last completed cycle, note completed vs. pushed work, and open discussion issues for patterns.

## Tips for Maximum Productivity

- Batch operations for related changes; consider smart templates for recurring issue structures.
- Use natural queries when possible ("Show me what John is working on this week").
- Leverage context: reference prior issues in new requests.
- Break large updates into smaller batches to avoid rate limits; cache or reuse filters when listing frequently.

## Troubleshooting

- Authentication: Clear browser cookies, re-run OAuth, verify workspace permissions, ensure API access is enabled.
- Tool Calling Errors: Confirm the model supports multiple tool calls, provide all required fields, and split complex requests.
- Missing Data: Refresh token, verify workspace access, check for archived projects, and confirm correct team selection.
- Performance: Remember Linear API rate limits; batch bulk operations, use specific filters, or cache frequent queries.

## Variation rules
- Vary workflow depth by task type (triage vs planning vs reporting).
- Use different batching strategies based on rate limits and volume.
- Prefer read-only exploration when intent is ambiguous.

## Empowerment principles
- Empower users to approve bulk edits before applying.
- Empower reviewers with clear summaries and change counts.

## Anti-patterns to avoid
- Bulk editing without a preview or user confirmation.
- Changing status/priority without rationale.
- Writing comments that duplicate existing context.

## Example prompts
- "Create a Linear issue for the login bug and assign it to me."
- "Summarize open P1 bugs for the mobile team."
- "Update the project timeline and add a status comment."

## Remember

The agent is capable of extraordinary work in this domain. These guidelines unlock that potential—they don't constrain it.
Use judgment, adapt to context, and push boundaries when appropriate.
