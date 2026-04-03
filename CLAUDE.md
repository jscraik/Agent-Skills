# Claude AI Governance

This repository contains governance rules for Claude Code and other AI assistants working in this codebase.

This file is **agent-tool specific**. For repository-wide rules, read `AGENTS.md` first.

## Table of Contents
- [Error Handling Protocol](#error-handling-protocol)
- [Reporting & Insights](#reporting--insights)
- [Output Paths](#output-paths)
- [Communication](#communication)
- [Efficiency](#efficiency)
- [Browser/Playwright](#browserplaywright)
- [AI Assistance Governance (Model A)](#ai-assistance-governance-model-a)
- [Artifact Templates](#artifact-templates)
- [PR Template](#pr-template)
- [Testing Standards](#testing-standards)
- [Development Workflow](#development-workflow)
- [Code Quality Checks](#code-quality-checks)
- [Git & PR Workflow](#git--pr-workflow)
- [PR Workflow](#pr-workflow)
- [MCP & External Tools](#mcp--external-tools)
- [MCP Server Configuration](#mcp-server-configuration)
- [Shell Script Portability](#shell-script-portability)
- [TypeScript Configuration](#typescript-configuration)
- [Command preflight helper](#command-preflight-helper)

## Error Handling Protocol
- When encountering API errors, model access issues, or unexpected failures, do not just report the error; always suggest a concrete workaround or alternative approach that still advances the user's goal.

## Reporting & Insights
- For any report or insights generation task, check that required services and model access are available before starting.
- If they are unavailable, fall back to generating the report from local data using available tools such as Read, Bash, Glob, and Grep.

## Output Paths
- Before generating files, verify output directory paths against `package.json` (or package-local script config) so generated paths match configured output settings.
- Audit existing scripts and config files for hardcoded output paths; update generated destinations to match configured paths.

## Communication
- When the user explicitly states a root cause, confirm the direction and proceed with that diagnosis instead of proposing alternative fixes.

## Efficiency
- Before implementing multi-file edits or complex automation for a simple information request, pause and ask: `Would a direct answer or simple command suffice?`

## Browser/Playwright
- When browser tooling cannot access local files directly, immediately start `python3 -m http.server` in the relevant directory instead of iterating on brittle workarounds or abandoning the browser path.

---

## AI Assistance Governance (Model A)

This project follows **Model A** AI artifact governance: prompts and session logs are committed artifacts in the repository.

### When creating PRs with AI assistance

Claude must:

1. **Save artifacts to `artifacts/ai/` directory**:
   - Final prompt → `artifacts/ai/prompts/YYYY-MM-DD-<slug>.yaml`
   - Session summary → `artifacts/ai/sessions/YYYY-MM-DD-<slug>.json`

2. **Commit both files in the PR branch**:
   ```bash
   git add artifacts/ai/prompts/YYYY-MM-DD-<slug>.yaml artifacts/ai/sessions/YYYY-MM-DD-<slug>.json
   ```

3. **Reference exact paths in PR body**:
   - Under **AI assistance** section:
     - Prompt: `artifacts/ai/prompts/YYYY-MM-DD-<slug>.yaml`
     - Session: `artifacts/ai/sessions/YYYY-MM-DD-<slug>.json`
   - In **AI Session Log** details:
     - Log file: `artifacts/ai/sessions/YYYY-MM-DD-<slug>.json`
     - Prompt file: `artifacts/ai/prompts/YYYY-MM-DD-<slug>.yaml`

4. **Do NOT**:
   - Embed prompt/log excerpts in the PR body
   - Link to external logs or pastebins
   - Skip creating artifacts when AI assistance is acknowledged

5. **Abort** if artifacts cannot be created and committed.

## Artifact Templates

See `artifacts/ai/prompts/.template.yaml` and `artifacts/ai/sessions/.template.json` for required fields.

## PR Template

All PRs must use `.github/PULL_REQUEST_TEMPLATE.md` which includes required AI disclosure sections.

## Testing Standards
- For this repo, run full test suites in the relevant package before committing (`npm test`, `pytest`, or the package-native equivalent used for that folder).
- Ensure all tests pass after multi-file changes.
- Fix test isolation issues immediately (mock async operations properly).
- After modifying auth-related, CLI-related, or async code, always run the full test suite.
- For CLI tests that exercise `process.exit`, mock exit calls to avoid hanging tests.

## Development Workflow
- Applies to Codex and Claude workflow execution in this repository.
- If validation surfaces durable repo work rather than a one-off note, create or update a Linear issue in the `agent-skills` project instead of leaving the finding only in chat.

## Code Quality Checks
- Run TypeScript type check (`tsc --noEmit`) after code changes in TypeScript packages where applicable.
- Run linter before committing.
- Fix all TypeScript errors and lint issues before marking tasks complete.

## Git & PR Workflow
- For Codex/Claude review handoffs, apply the rules below.

## PR Workflow
- When working on PRs, check ALL review comments before marking complete.
- After fixing review comments, re-verify PR state on GitHub before reporting success.
- Handle merge conflicts directly on GitHub, not just locally.
- When resolving review feedback, run `gh pr view <PR_NUMBER> --comments` and inspect every comment/thread status before declaring completion.

## MCP & External Tools
- Keep MCP server setup explicit and tool-agnostic where possible.

## MCP Server Configuration
- Register MCP servers with `claude mcp add <name> -- <command>` and keep command arguments explicit.
- For 1Password integrations, use `[ -e ]` instead of `[ -f ]` to handle named pipes correctly.

## Shell Script Portability
- For file existence checks, prefer `[ -e "..." ]` over `[ -f "..." ]` to correctly handle named pipes and other special files.

## TypeScript Configuration
- TypeScript strict mode is enabled where applicable; guard property access with null/undefined checks before using values.
- Run `pnpm typecheck` after significant TypeScript changes (or use the repo-native command when using a different package manager).

## Command preflight helper
- Run `bash scripts/codex-preflight.sh --stack auto --mode required` before command-heavy, destructive, or path-sensitive work.
- Validate required bins and target paths first so mistakes are prevented before edits.
