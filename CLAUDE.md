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

When modifying shell scripts or configuration files, always use non-interactive command patterns. Avoid commands that require user input (like `op read` from 1Password) - they hang in CI/CD and headless environments.

## Code Quality

| Task | Command |
|------|---------|
| TypeScript check | `tsc --noEmit` |
| Lint | Run repo-native linter |

Fix all errors before marking complete.

## Testing

After fixing any code, always run the relevant test suite to verify the fix works before committing. If tests fail, debug and iterate rather than committing broken code.

Existing guidance:

- Run full test suite before committing
- Mock `process.exit` in CLI tests to prevent hangs
- Run full suite after auth/CLI/async changes

## Git Workflow

When working with git branches, prefer merge over rebase for complex histories (>50 commits). Always run `git status` and resolve conflicts systematically before proceeding with changes.
For git operations like cherry-picking or branch syncing, prefer direct file restoration (`git checkout source_branch -- path/to/file`) over complex cherry-pick workflows when only specific files are needed.

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

For YAML schema changes and configuration files, validate against the schema immediately after editing. Do not assume syntax is correct without verification.

## Code Review Fixes

When fixing CodeRabbit or automated review comments, batch related fixes by file type and verify each category (types, security, validation, linting) before moving to the next.

## Refactoring

When refactoring interfaces that affect multiple files, first update the interface/type definitions, then systematically update all consumers before running tests. Verify no 'conflated' concerns exist (e.g., subcommand vs. mode flags).

## Documentation

Always format markdown plan files cleanly before writing - avoid stray backticks, inconsistent heading levels, or mixed quote styles. Use `prettier --write` or equivalent for markdown files.

---

See [AGENTS.md](./AGENTS.md) for common rules and quick-start.
