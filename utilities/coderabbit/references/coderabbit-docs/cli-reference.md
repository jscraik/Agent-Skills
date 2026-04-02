---
source: https://docs.coderabbit.ai/cli/reference
---

# CLI Command Reference

Complete reference for all CodeRabbit CLI commands and options.

## Commands

`cr` is the short alias for `coderabbit`. Both work identically.

| Command | Description |
|---|---|
| `cr` | Run code review (interactive mode by default) |
| `cr --plain` | Output detailed feedback in plain text format |
| `cr --prompt-only` | Show minimal output optimized for AI agents |
| `cr auth` | Authentication commands |
| `cr auth login` | Authenticate via OAuth, self-hosted (`--self-hosted`), or API key (`--api-key "<key>"`) |
| `cr auth logout` | Log out from CodeRabbit |
| `cr auth status` | Show current authentication status |
| `cr auth org` | Switch between organizations |
| `cr review` | AI-driven code reviews with interactive or plain text output |
| `cr update` | Check for and install the latest CLI version |

## Options

| Option | Description |
|---|---|
| `-t, --type <type>` | Review type: all, committed, uncommitted (default: "all") |
| `-c, --config <files...>` | Additional instructions for CodeRabbit AI (e.g., claude.md, coderabbit.yaml) |
| `--base <branch>` | Base branch for comparison |
| `--base-commit <commit>` | Base commit on current branch for comparison |
| `--api-key "<key>"` | Agentic API key for usage-based reviews |
| `--cwd <path>` | Working directory path (must contain an initialized Git repository) |
| `--no-color` | Disable colored output |
