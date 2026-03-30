---
name: linear
description: "Manage Linear issues, projects, and docs through the Linear MCP workflow with consistent read/create/update operations. Use when a user asks to triage, create, update, or report on Linear work items."
metadata:
  skill-type: team_automation
---

# Linear

## Table of Contents
- [Scope and triggers](#scope-and-triggers)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Failure mode](#failure-mode)
- [Standards snapshot](#standards-snapshot-march-2026)
- [Required workflow](#required-workflow)
- [Available tools](#available-tools)
- [Practical workflows](#practical-workflows)
- [Troubleshooting](#troubleshooting)
- [Validation](#validation)
- [Anti-patterns to avoid](#anti-patterns-to-avoid)
- [Decision feedback protocol](#decision-feedback-protocol)

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
- When a durable summary of current Linear state is needed before any change is made.

## Required inputs
- User intent (team, project, issue scope, and desired outcomes).
- Access to Linear MCP and the target workspace/team identifiers.
- Any required fields for create/update actions (priority, labels, assignee).

## Deliverables
- Retrieved issue/project data or applied updates.
- A concise summary of changes and any remaining gaps.
- Follow-up actions or confirmations needed from the user.

## Failure mode
If the request is too ambiguous to safely write to Linear, stay read-only, summarize the missing decision, and ask for the smallest approval or identifier needed.

## Standards snapshot (March 2026)
- Read before write, and show the evidence that justifies any mutation.
- Treat bulk updates as high-risk operations: preview grouping logic and impact before applying changes.
- Prefer exact identifiers and explicit state transitions over fuzzy natural-language edits once mutation begins.
- Preserve auditability: the user should be able to see what changed, why, and what still needs follow-up.

## Constraints
- Redact secrets, tokens, credentials, and sensitive data by default.
- Avoid destructive or bulk updates without clear user direction.
- Keep write scope explicit before mutating Linear state.

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
- If the write plan changes after reading context, pause and restate the new write scope before mutating anything.

### Step 4
Summarize results, call out remaining gaps or blockers, and propose next actions (additional issues, label changes, assignments, or follow-up comments).

## Available Tools

Issue Management: `list_issues`, `get_issue`, `save_issue`, `list_issue_statuses`, `list_issue_labels`, `create_issue_label`

Project & Team: `list_projects`, `get_project`, `save_project`, `list_teams`, `get_team`, `list_users`

Documentation & Collaboration: `list_documents`, `get_document`, `create_document`, `update_document`, `search_documentation`, `list_comments`, `save_comment`, `list_cycles`

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

## Anti-patterns to avoid
- Bulk editing without a preview or user confirmation.
- Changing status/priority without rationale.
- Writing comments that duplicate existing context.
- Creating issues or project updates before checking whether an existing artifact already covers the need.
- Treating approximate issue names as safe stand-ins for exact identifiers once writes begin.

## Example prompts
- "Create a Linear issue for the login bug and assign it to me."
- "Summarize open P1 bugs for the client team."
- "Update the project timeline and add a status comment."

## Validation
- Confirm the final summary includes changed entities, unchanged blockers, and any user decisions still needed.
- For bulk edits, confirm the number of affected items matches the stated plan.
- Fail fast on auth, workspace, or identifier ambiguity before applying writes.

## References
- `references/contract.yaml`
- `references/evals.yaml`

<!-- skill-score-boost-v1 -->
## Philosophy and tradeoffs
- Use this skill when consistent decision-making matters more than one-off execution because project context should drive the approach.
- Principle and mindset: prioritize tradeoffs and constraints over rigid checklists; understand why each step exists.
- Ask this to keep outcomes robust: Why is this the right default, and what could change this outcome?
- How do we adapt if constraints shift?
- What evidence is needed before choosing one path over another?

## Anti-patterns and caveats
- Avoid applying this playbook generically without checking repository-specific context.
- **NEVER** skip required validation gates when behavior changes.
- **DO NOT** use this skill as a rigid replacement for engineering judgment.
- **DON'T** ignore warnings or assume one pattern fits all repos.
- Common pitfall: treating anti-patterns as optional.
- Incorrect assumptions here can lead to fragile guidance.
- Warning: wrong sequencing can create avoidable regressions.

## Variation and adaptation
- Vary the workflow by team size, risk, and deployment target.
- Use different strategies for small, medium, and large changes.
- Adapt recommendations to the specific environment and avoid repetitive templates.
- Avoid generic or cookie-cutter responses; craft context-specific alternatives.
- Keep outputs diverse and not repetitive.
- Converge on a custom path only after evidence review.
- Different constraints should produce different, non-generic recommendations.

## Empowering execution style
- Be capable of exploring multiple options and enabling the team to make safe decisions.
- Unlock confidence by explaining options and tradeoffs clearly.
- Feel free to be creative while staying rigorous and precise.
- Push boundaries with practical alternatives when simple recipes fail.
- Enable outcomes-oriented problem solving.

## Decision feedback protocol

## See Also

| Skill | When to use together |
|---|---|
| [[ce-plan]] | Convert Linear issues into sequenced implementation plans |
| [[gh-workflow]] | Link Linear issues to GitHub PRs during delivery |
| [[simple-tasks]] | Use for lightweight local task tracking between Linear syncs |
| [[alignment-checkpoint]] | Gate Linear issue creation behind intent alignment |
| [[compound-engineering-router]] | Route compound work captured as Linear issues |

**Topic map:** [[agent-ops]]

<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol (required):**
- If post-run feedback capture is enabled for this runtime, emit a non-blocking `post_run_feedback` event via `request_user_input` after result delivery.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 utilities/skill-builder/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->

## Gotchas
- None yet. Capture recurring failures here as symptom -> cause -> do instead -> check.
