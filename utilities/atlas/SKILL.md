---
name: atlas
description: macOS-only AppleScript control for the ChatGPT Atlas desktop app. Use only when the user explicitly asks to control Atlas tabs/bookmarks/history on macOS and the "ChatGPT Atlas" app is installed; do not trigger for general browser tasks or non-macOS environments.
metadata:
  skill-type: team_automation
---

# Atlas

## Table of Contents
- [Standards snapshot](#standards-snapshot)
- [When to use](#when-to-use)
- [When not to use](#when-not-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Philosophy](#philosophy)
- [Workflow](#workflow)
- [Verification](#verification)
- [Constraints](#constraints)
- [Anti-patterns](#anti-patterns)
- [Remember](#remember)

## Standards snapshot (March 2026)
- Atlas control is macOS-only and explicit-user-request only.
- Prefer the bundled CLI and inspectable local data paths over improvised AppleScript snippets.
- Treat local browser history and bookmarks as sensitive user data.

## When to use
- The user explicitly asks to control ChatGPT Atlas tabs or windows.
- The user wants to inspect Atlas bookmarks or history on macOS.
- The task needs Atlas-specific browser state rather than a general browser automation workflow.

## When not to use
- General browsing, scraping, or browser automation. Use a browser automation skill instead.
- Non-macOS environments.
- Requests that do not explicitly target ChatGPT Atlas.

## Required inputs
- The Atlas task: tabs, bookmarks, history, or app metadata.
- Confirmation that the environment is macOS with Atlas installed.
- Any search terms, limits, or URLs relevant to the task.

## Deliverables
- The requested Atlas command results or the safest next step to obtain them.
- Clear notes when permissions, install location, or local profile paths block the task.

## Philosophy
- Use stable, reproducible CLI commands.
- Minimize access to user browsing data to what the task actually needs.
- Prefer diagnosis over repeated AppleScript retries when Atlas permissions are missing.

## Workflow
1. Confirm the request is Atlas-specific and macOS-scoped.
2. Use the bundled `atlas_cli.py` rather than ad hoc AppleScript when possible.
3. Check app availability before attempting control actions.
4. For bookmarks or history, query local Atlas data with bounded scope and clear filters.
5. If permissions fail, stop and explain the exact macOS Automation permission the user needs to grant.

## Verification
- Confirm Atlas is installed in `/Applications` or `~/Applications`.
- Confirm commands target the intended Atlas app instance and data root.
- Confirm history or bookmark queries are bounded by search terms, limits, or time windows when possible.
- Confirm results do not expose more private browsing data than the user asked for.

## Validation
- Verify the request is explicitly Atlas-specific before using this skill.
- Verify the response points to the bundled `scripts/` helpers or skill `references/` docs when path or data-root issues arise.
- Reuse any shipped `assets/` or examples in the skill folder instead of inventing parallel command snippets.

## Constraints
- Do not use this skill for non-Atlas browsers.
- Treat local history, bookmarks, and profile metadata as sensitive.
- Never print secrets, tokens, or unrelated private browsing data.
- Avoid irreversible actions unless the user asked for them explicitly.

## Anti-patterns
- Using Atlas as a stand-in for generic browser automation.
- Dumping raw history or bookmarks without narrowing to the request.
- Repeating AppleScript attempts without checking install paths or permissions first.
- Assuming the beta and stable Atlas data roots are interchangeable without verifying freshness.

## Examples
- "List my ChatGPT Atlas tabs and focus the tab on chatgpt.com."
- "Search Atlas history for OpenAI docs from today only."

## See Also

| Skill | When to use together |
|---|---|
| [[openai-docs]] | Reference official ChatGPT documentation for Atlas features |
| [[agent-browser]] | Complement Atlas AppleScript control with browser automation |
| [[notebooklm]] | Cross-reference Atlas conversations with NotebookLM notebooks |

**Topic map:** [[mobile-native]]

## Remember
- This skill is a precise tool, not a general browser hammer.
- Atlas tasks should be explicit, bounded, and privacy-aware.
- When blocked, the best output is the exact permission or path issue and the next safe step.

## Gotchas
- None yet. Capture recurring failures here as symptom -> cause -> do instead -> check.

## Failure mode
- If Atlas is unavailable, unsupported on the current host, or the requested control surface cannot be confirmed, stop, name the limitation, and fall back to a non-Atlas workflow rather than guessing UI automation.
