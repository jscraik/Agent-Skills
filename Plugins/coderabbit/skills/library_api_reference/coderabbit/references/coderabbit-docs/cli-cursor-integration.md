---
source: https://docs.coderabbit.ai/cli/cursor-integration
---

# Cursor Integration

Enable Cursor to run the CodeRabbit CLI as part of your development workflow. Let AI code, review, and fix issues autonomously without human intervention.

## Autonomous AI development workflows

CodeRabbit CLI + Cursor allows you to develop faster with code that gets reviewed for issues before it reaches the PR. Because Cursor executes CodeRabbit directly as part of its steps, code that gets made by Cursor can automatically be reviewed by CodeRabbit.

## Why integrate these tools

- **Expert issue detection**: CodeRabbit spots race conditions, memory leaks, and logic errors
- **AI-powered fixes**: Cursor implements fixes with full context from CodeRabbit's analysis
- **Context preservation**: `--prompt-only` mode gives Cursor succinct context about issues
- **Agentic development loop**: AI codes, runs reviews, applies fixes, and iterates

## Prerequisites

**Windows users**: The CodeRabbit CLI requires WSL to run on Windows.

1. **Install Cursor** and setup an account
2. **Install CodeRabbit CLI**:
   ```bash
   curl -fsSL https://cli.coderabbit.ai/install.sh | sh
   source ~/.zshrc
   ```
3. **Authenticate CodeRabbit**:
   ```bash
   coderabbit auth login
   ```
4. **Verify auth**:
   ```bash
   coderabbit auth status
   ```
5. **Test that Cursor can run CodeRabbit**
6. **Setup a Cursor Rule for CodeRabbit** (recommended)

### Cursor Rule example

```
# Running the CodeRabbit CLI

CodeRabbit is already installed in the terminal. Run it as a way to review your code.
Run the command: cr -h for details on commands available. In general, I want you to run
coderabbit with the `--prompt-only` flag. To review uncommitted changes run:
`coderabbit --prompt-only -t uncommitted`.

IMPORTANT: When running CodeRabbit to review code changes, don't run it more than 3 times
in a given set of changes.
```

## Integration workflow

### Example prompt

```
Please implement phase 7.3 of the planning doc and then run coderabbit --prompt-only -t uncommitted,
let it run as long as it needs and fix any issues.
```

## Optimization tips

- Use `--prompt-only` mode for efficiency
- CodeRabbit reads your `cursor.md` file for configuration (Pro plan feature)

## Troubleshooting

- Check authentication: `coderabbit auth status`
- Verify git status
- Specify base branch if not `main`
- Reviews may take 7 to 30+ minutes
