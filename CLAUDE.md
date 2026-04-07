---
schema_version: 1
---

# Claude Code Governance

Agent-tool specific instructions for Claude Code.

For repository-wide rules, see [AGENTS.md](./AGENTS.md).

## Table of Contents

- [Claude-Only Instructions](#claude-only-instructions)
- [MCP Configuration](#mcp-configuration)
- [Shell Scripting](#shell-scripting)
- [Code Quality](#code-quality)
- [Testing](#testing)
- [Git Workflow](#git-workflow)
- [PR Workflow](#pr-workflow)
- [Error Handling](#error-handling)
- [Browser/Playwright](#browserplaywright)
- [Configuration Files](#configuration-files)
- [Code Review Fixes](#code-review-fixes)
- [Refactoring](#refactoring)
- [Documentation](#documentation)

## Claude-Only Instructions

### AI Assistance Governance (Model A)

This project follows **Model A** AI artifact governance: prompts and session logs are committed artifacts.

**When creating PRs with AI assistance:**

1. **Save artifacts** to `artifacts/ai/`:
   - Prompt: `artifacts/ai/prompts/YYYY-MM-DD-<slug>.yaml`
   - Session: `artifacts/ai/sessions/YYYY-MM-DD-<slug>.json`

2. **Commit both files** in the PR branch

3. **Reference paths** in PR body under "AI assistance" section

4. **Do NOT:**

   | Avoid | Do Instead |
   |-------|------------|
   | Embed prompt excerpts in PR body | Reference file paths only |
   | Link to external logs/pastebins | Commit artifacts to repo |
   | Skip artifacts when AI assisted | Create and commit both files |

5. **Abort** if artifacts cannot be created and committed.

See templates: `artifacts/ai/prompts/.template.yaml`

## MCP Configuration

Register MCP servers explicitly:
```bash
claude mcp add <name> -- <command>
```

For 1Password: use `[ -e ]` instead of `[ -f ]` for named pipes.

## Shell Scripting

For shared workflow guidance, see [AGENTS.md](./AGENTS.md). For shared shell-scripting guidance, see the canonical guidance in that file.

## Code Quality

| Task | Command |
|------|---------|
| TypeScript check | `tsc --noEmit` |
| Lint | Run repo-native linter |

Fix all errors before marking complete.

## Testing

For shared workflow guidance, see [AGENTS.md](./AGENTS.md). For shared testing guidance, see the canonical guidance in that file.

## Git Workflow

For shared git workflow guidance, see [AGENTS.md](./AGENTS.md), which points to the canonical workflow and safety guidance.
## PR Workflow

- Check **all** review comments before marking complete
- Re-verify PR state on GitHub after fixes
- Handle merge conflicts on GitHub (not just locally)
- Verify each thread: `gh pr view <PR> --comments`

## Error Handling

When encountering API errors or failures, suggest a concrete workaround that advances the user's goal.

## Browser/Playwright

When browser tooling cannot access local files directly, immediately start `python3 -m http.server` in the relevant directory.

## Configuration Files

For shared configuration-files guidance, see [AGENTS.md](./AGENTS.md). For YAML and configuration validation, use the canonical guidance there.

## Code Review Fixes

For shared review-comment fix guidance, see [AGENTS.md](./AGENTS.md).

## Refactoring

For shared refactoring guidance, see [AGENTS.md](./AGENTS.md). For interface-first refactoring and downstream updates, follow the canonical guidance there.

## Documentation

For shared documentation guidance, see [AGENTS.md](./AGENTS.md). For plan-file formatting conventions, use the canonical guidance there.

---

See [AGENTS.md](./AGENTS.md) for common rules and quick-start.
