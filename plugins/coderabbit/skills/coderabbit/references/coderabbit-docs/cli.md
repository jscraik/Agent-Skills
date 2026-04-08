---
source: https://docs.coderabbit.ai/cli
---

# Command-Line Review Tool

Get AI code reviews directly in your CLI before you commit. Catch race conditions, memory leaks, and security vulnerabilities without leaving your development environment.

This feature is currently in open beta.

## Key features

- **Review uncommitted changes**: Catch bugs before they reach your repository
- **Apply fixes in one step**: Fix simple issues instantly
- **Context-aware reviews**: Paid plans unlock reviews powered by your team's codebase history

## Getting started

### Install CLI

```bash
# Install script
curl -fsSL https://cli.coderabbit.ai/install.sh | sh
source ~/.zshrc

# Homebrew
brew install coderabbit
```

### Authenticate

```bash
cr auth login
```

### Review your code

```bash
cr              # Review in current repo
cr --base develop  # If main branch is not 'main'
cr --base master
```

**Git repository required**: The CLI must be run from within an initialized Git repository.

## Review modes

```bash
cr               # Interactive mode (default)
cr --plain       # Plain text mode - detailed feedback
cr --prompt-only # Prompt-only mode - minimal output for AI agents
```

## Working with review results

Example findings include:
- Race condition detected
- Memory leak potential
- Security vulnerability
- Logic error

### Browse and apply suggestions

In interactive mode, use arrow keys to navigate and press enter for details.

## AI agent integration

CodeRabbit detects problems, then your AI coding agent implements fixes.

### Example prompt for your AI agent

```
Please implement phase 7.3 of the planning doc and then run cr --prompt-only,
let it run as long as it needs (run it in the background) and fix any issues.
```

### Components of a good prompt

1. Run CodeRabbit CLI with `--prompt-only` flag
2. Run in the background (reviews can take 7-30+ minutes)
3. Evaluate and implement fixes
4. Verify with a second pass
5. Set loop limits

## Pricing and capabilities

| Plan | Reviews per hour |
|---|---|
| Free | 3 |
| OSS | 2 |
| Trial | 4 |
| Pro | 8 |
| Enterprise | 12 |

## CLI with Usage-based Add-on

Usage-based add-on uses a credit system ($0.25 per file reviewed). Steps:

1. Buy credits from Subscription and Billing dashboard
2. Create an Agentic API Key
3. Authenticate: `coderabbit auth login --api-key "cr-************"`
4. Run review: `coderabbit review --plain`

## Uninstall

```bash
# Install script
rm $(which coderabbit)

# Homebrew
brew remove coderabbit
```
