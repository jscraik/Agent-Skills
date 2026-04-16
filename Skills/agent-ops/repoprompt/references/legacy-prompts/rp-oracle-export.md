---
description: Export context for oracle consultation using RepoPrompt MCP tools
repoprompt_managed: true
repoprompt_skills_version: 6
repoprompt_variant: mcp
---

# Oracle Export

Task: $ARGUMENTS

Export a comprehensive prompt with full context for consultation with an external oracle.

## How It Works

Describe the task or question you need the oracle to solve. The context_builder agent will:
1. Analyze your request and explore the codebase
2. Select the most relevant files within a token budget
3. Write a detailed prompt explaining the task and context

You don't need to specify which files to include—just describe what you need help with.

## Workflow

### 0. Workspace Verification (REQUIRED)

Before building context, confirm the target codebase is loaded:

```json
{"tool":"list_windows","args":{}}
```

**Check the output:**
- If your target root appears in a window → bind to that window with `select_window`
- If not → the codebase isn't loaded

**Bind to the correct window:**
```json
{"tool":"select_window","args":{"window_id":<window_id_with_your_root>}}
```

**If the root isn't loaded**, find and open the workspace:
```json
{"tool":"manage_workspaces","args":{"action":"list"}}
{"tool":"manage_workspaces","args":{"action":"switch","workspace":"<workspace_name>","open_in_new_window":true}}
```

### 1. Build Context

```json
{"tool":"context_builder","args":{
  "instructions":"<the task/question above>",
  "response_type":"clarify"
}}
```

Wait for context_builder to complete. It will explore the codebase and build optimal context.

### 2. Export Prompt

Confirm the export path with the user (default: `~/Downloads/oracle-prompt.md`), then export:

```json
{"tool":"prompt","args":{"op":"export","path":"<confirmed path>"}}
```

Report the export path and token count to the user.
