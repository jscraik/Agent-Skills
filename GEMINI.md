# Gemini Context

For this Codex/Gemini/Claude repository, this file captures always-on context for AI tooling and run-time workflow reminders.

For repository-wide rules, use `AGENTS.md` as the source of truth.

## Output Paths
- Before generating files, verify output directory paths match `package.json` output config and package scripts.
- Check scripts/configs for hardcoded output paths and align generated destinations to configured paths.

## Testing Standards
- Run full test suite before committing (for example `npm test`, `pytest`, or the package-native equivalent used in that subproject).
- Ensure all tests pass after multi-file changes.
- Fix test isolation issues immediately by mocking async operations properly.
- After modifying auth-related, CLI-related, or async code, always run the full test suite.
- For CLI tests that exercise `process.exit`, mock exit calls so tests do not hang.

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
- For each PR review, run `gh pr view <PR_NUMBER> --comments` and verify each comment thread before finishing.

## MCP & External Tools
- Keep MCP configuration explicit for both Codex and Claude automation.

## MCP Server Configuration
- Register MCP servers with `claude mcp add <name> -- <command>` and keep argument separation explicit.
- For 1Password integrations, use `[ -e ]` instead of `[ -f ]` so named-pipe checks work correctly.

## Shell Script Portability
- Prefer `[ -e "..." ]` over `[ -f "..." ]` for existence checks to support named pipes and special files.

## TypeScript Configuration
- TypeScript strict mode is enabled where applicable; ensure null/undefined checks are present before property access.
- Run `pnpm typecheck` after significant TypeScript changes (or use repo-native equivalent for the package).
