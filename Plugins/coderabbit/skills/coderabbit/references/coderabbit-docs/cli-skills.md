---
source: https://docs.coderabbit.ai/cli/skills
---

# CodeRabbit Skills

## Overview

**Skills** are a standardized format for packaging AI agent capabilities as structured Markdown files (`SKILL.md`). Each skill describes a capability — its purpose, usage triggers, and the steps the agent should follow to execute it. This gives AI agents a consistent, discoverable, interoperable way to understand and invoke external tools without manual configuration. You can learn more about the open standard at agentskills.io.

CodeRabbit Skills are open-source, agent-installable capabilities built on this standard — browse and contribute at github.com/coderabbitai/skills. With these skills, any compatible agent can trigger a full review without explanations on how to run specific console commands.

Skills complement the existing agent integrations documented in the CLI section. You can use skills alongside manual CLI workflows or as a replacement when you want a more natural, language-driven interface.

## Prerequisites

Before installing skills, make sure the CodeRabbit CLI is installed and authenticated:

```bash
# Install the CodeRabbit CLI
curl -fsSL https://cli.coderabbit.ai/install.sh | sh

# Authenticate
coderabbit auth login
```

For full CLI setup instructions, see the CLI overview.

## Supported agents

First-class support includes Claude Code, Cursor, Codex, GitHub Copilot, and Gemini CLI, with 35+ agents supported in total. See the coderabbitai/skills repository for the complete list.

## Installing Skills

Install the CodeRabbit skills package using `npx`:

```bash
npx skills add coderabbitai/skills
```

### Installation options

Customize how skills are installed with these flags:

| Flag | Purpose |
| --- | --- |
| `-g, --global` | Install to user directory instead of the current project |
| `-a, --agent` | Target a specific agent (e.g., `-a claude-code`) |
| `-s, --skill` | Install a particular skill by name |
| `--all` | Install all skills to all agents without prompts |

### Installation commands

```bash
# Install for all detected agents in the current project
npx skills add coderabbitai/skills

# Install globally to your user directory
npx skills add coderabbitai/skills -g

# Install only for Claude Code
npx skills add coderabbitai/skills -a claude-code
```

Skills are installed as `SKILL.md` files into `~/.agents/skills` directory or into the agent's designated skills directory.

## Available Skills

### `code-review`

The `code-review` skill triggers a full CodeRabbit analysis of your current changes directly from a natural language request.

#### Triggering the skill

Activate the skill using natural language inside your AI agent:

- "Review my code"
- "Check for security issues"
- "What's wrong with my changes?"
- "Run a code review"
- "Review my PR"

The agent reads the installed `SKILL.md` file and automatically invokes the CodeRabbit CLI.

#### How it works

When triggered, the agent will:

1. Check that the CodeRabbit CLI is installed and authenticated
2. Run the review on your current changes
3. Present findings grouped by severity — **Critical**, **Warning**, and **Info**
4. Optionally fix issues and re-review until the output is clean

#### CLI flags used by the skill

The skill uses these CodeRabbit CLI flags internally:

| Flag | Description |
| --- | --- |
| `--prompt-only` | Agent-optimized output for agentic workflows |
| `--plain` | Detailed plain text output |
| `-t` | Review type (all, committed, uncommitted) |
| `--base` | Branch to compare against |
| `--base-commit` | Compare against a specific commit hash |

#### Autonomous workflow

Skills enable a fully autonomous review-fix loop:
Implement -> Review -> Fix Critical/Warning issues -> Re-review until clean
The agent continues iterating until no Critical or Warning issues remain, then provides a summary of everything that was fixed.

### `autofix`

The `autofix` skill fetches unresolved CodeRabbit review threads on your current branch's pull request and helps you apply fixes interactively or in batch.

#### Triggering the autofix skill

Activate the skill using natural language inside your AI agent:

- "Autofix CodeRabbit comments"
- "Fix CodeRabbit review issues"
- "Review and fix CodeRabbit feedback"

The agent reads the installed `SKILL.md` file, finds your open PR, and pulls unresolved CodeRabbit review threads.

#### How autofix works

When triggered, the agent will:

1. Check local branch status and warn about uncommitted or unpushed changes
2. Locate the open pull request for the current branch
3. Fetch unresolved review threads authored by CodeRabbit
4. Extract issue metadata and fix prompts from each thread
5. Let you choose either review-each-fix mode or auto-fix-all mode
6. Apply selected fixes and create one consolidated commit
7. Prompt the user if the commit should be pushed upstream

#### CLI commands used by the skill

The skill relies on GitHub CLI plus Git commands:

| Command | Purpose |
| --- | --- |
| `gh pr list --head $(git branch --show-current) --state open --json number,title` | Find the open PR for the current branch |
| `gh api graphql ... pullRequest.reviewThreads ...` | Fetch unresolved CodeRabbit review threads |
| `gh pr comment <pr-number> --body "<summary>"` | Post a run summary after fixes are applied |
| `git add ... && git commit -m "fix: apply CodeRabbit auto-fixes"` | Create one consolidated commit |

#### Fix modes

The skill supports two fix paths:

- **Review each issue**: See each proposed fix and approve, defer, or modify it.
- **Auto-fix all**: Apply all eligible fixes in batch, prioritized from highest severity first.

In both modes, the skill uses CodeRabbit's "Prompt for AI Agents" (the agent-ready fix instruction) guidance from each unresolved thread as the fix specification.

## Troubleshooting

### Verification commands

Use these commands to confirm your CLI setup is working before filing a skills-related issue:

```bash
# Check the installed CLI version
coderabbit --version

# Verify authentication status
coderabbit auth status
```

For detailed CLI troubleshooting, see the CLI overview.
