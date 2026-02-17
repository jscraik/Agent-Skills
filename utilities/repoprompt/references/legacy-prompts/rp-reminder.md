---
description: Reminder to use RepoPrompt MCP tools
repoprompt_managed: true
repoprompt_skills_version: 6
repoprompt_variant: mcp
---

# RepoPrompt Tools Reminder

Continue your current workflow using RepoPrompt MCP tools instead of built-in alternatives.

## Primary Tools

| Task | Use This | Not This |
|------|----------|----------|
| Find files/content | `file_search` | grep, find, Glob |
| Read files | `read_file` | cat, Read |
| Edit files | `apply_edits` | sed, Edit |
| Create/delete/move | `file_actions` | touch, rm, mv, Write |

## Quick Reference

```json
// Search (path or content)
{"tool":"file_search","args":{"pattern":"keyword","mode":"auto"}}

// Read file (or slice)
{"tool":"read_file","args":{"path":"Root/file.swift"}}
{"tool":"read_file","args":{"path":"Root/file.swift","start_line":50,"limit":30}}

// Edit (search/replace)
{"tool":"apply_edits","args":{"path":"Root/file.swift","search":"old","replace":"new"}}

// File operations
{"tool":"file_actions","args":{"action":"create","path":"Root/new.swift","content":"..."}}
{"tool":"file_actions","args":{"action":"delete","path":"/absolute/path.swift"}}
{"tool":"file_actions","args":{"action":"move","path":"Root/old.swift","new_path":"Root/new.swift"}}
```

## Context Management

```json
// Check selection
{"tool":"manage_selection","args":{"op":"get","view":"files"}}

// Add files for chat context
{"tool":"manage_selection","args":{"op":"add","paths":["Root/path/file.swift"]}}
```

Continue with your task using these tools.