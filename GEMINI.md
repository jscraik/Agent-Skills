# Gemini Context

For this Codex/Gemini/Claude repository, this file captures always-on context for AI tooling and run-time workflow reminders.

For repository-wide rules, use `AGENTS.md` as the source of truth.

## Testing Standards
- Run full test suite before committing (for example `npm test`, `pytest`, or the package-native equivalent used in that subproject).
- Ensure all tests pass after multi-file changes.
- Fix test isolation issues immediately by mocking async operations properly.

## Development Workflow
- Applies to Codex, Claude, and Gemini workstreams in this repo.

## Code Quality Checks
- Run TypeScript type check (`tsc --noEmit`) after code changes in TypeScript packages where applicable.
- Run linter before committing.
- Fix all TypeScript errors and lint issues before marking tasks complete.

## Git & PR Workflow
- Use this PR flow for cross-tool review handoffs.

## PR Workflow
- When working on PRs, check ALL review comments before marking complete.
- After fixing review comments, re-verify PR state on GitHub before reporting success.
- Handle merge conflicts directly on GitHub, not just locally.

## MCP & External Tools
- Keep MCP configuration explicit for both Codex and Claude automation.

## MCP Server Configuration
- Register MCP servers with `claude mcp add <name> -- <command>` and keep argument separation explicit.
- For 1Password integrations, use `[ -e ]` instead of `[ -f ]` so named-pipe checks work correctly.
