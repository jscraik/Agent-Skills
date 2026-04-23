# Security and Governance

## Table of Contents
- [Baselines](#baselines)
- [Repository practice](#repository-practice)
- [External integration preflight](#external-integration-preflight)
- [AI disclosure artifacts](#ai-disclosure-artifacts)

## Baselines
- See `~/.codex/instructions/standards.md`.
- See `~/.codex/instructions/rvcp-common.md`.

## Repository practice
- Repository-wide security and workflow rules in `AGENTS.md` take precedence.
- Use repository-specific AI handling from `AGENTS.md`.

## External integration preflight
- Run `codex mcp list` before MCP-dependent work.
- Verify authentication in this order:
  1. Confirm environment variables are expanded.
  2. Confirm 1Password session with `op account list`.
  3. Run a simple MCP/API connectivity check.
  4. Proceed with full operations.
- If auth fails, debug auth first before retrying commands.

## AI disclosure artifacts
- CODEX governance applies to PRs:
  - `Infrastructure/artifacts/ai/prompts/YYYY-MM-DD-<slug>.yaml`
  - `Infrastructure/artifacts/ai/sessions/YYYY-MM-DD-<slug>.json`
