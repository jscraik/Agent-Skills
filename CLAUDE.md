# Claude AI Governance

This repository contains governance rules for Claude Code and other AI assistants working in this codebase.

This file is **agent-tool specific**. For repository-wide rules, read `AGENTS.md` first.

---

# AI Assistance Governance (Model A)

This project follows **Model A** AI artifact governance: prompts and session logs are committed artifacts in the repository.

## When creating PRs with AI assistance

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

## Development Workflow
- Applies to Codex and Claude workflow execution in this repository.

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

## MCP & External Tools
- Keep MCP server setup explicit and tool-agnostic where possible.

## MCP Server Configuration
- Register MCP servers with `claude mcp add <name> -- <command>` and keep command arguments explicit.
- For 1Password integrations, use `[ -e ]` instead of `[ -f ]` to handle named pipes correctly.

## Command preflight helper
- Source `scripts/codex-preflight.sh` and run `preflight_repo` before command-heavy, destructive, or path-sensitive work.
- Validate required bins and target paths first so mistakes are prevented before edits.
