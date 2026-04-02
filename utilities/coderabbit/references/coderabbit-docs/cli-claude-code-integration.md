---
source: https://docs.coderabbit.ai/cli/claude-code-integration
---

# Claude Code Integration

AI-powered code review in Claude Code through the CodeRabbit plugin. Let AI code, review, and fix issues autonomously without human intervention.

## Autonomous AI development workflows

The CodeRabbit plugin for Claude Code creates autonomous AI development workflows. Claude Code can trigger CodeRabbit reviews directly through simple commands, enabling you to build features, run code reviews, and fix issues without manual intervention.

This integration makes AI coding more independent, with built-in quality gates that catch issues before they reach production.

CodeRabbit analyzes your code changes and surfaces specific issues, then Claude Code applies fixes based on CodeRabbit's context-rich feedback.

## Installation

Install the CodeRabbit plugin for Claude Code from the marketplace.

## Usage

### Running code reviews

Use the `/coderabbit:review` command to trigger a review:

The command will:

- Verify CLI installation and authentication
- Run the code review
- Present findings grouped by severity

### Review options

Customize your review with these options:

```
/coderabbit:review                    # Review all changes
/coderabbit:review committed          # Only committed changes
/coderabbit:review uncommitted        # Only uncommitted changes
/coderabbit:review --base main        # Compare against main branch
```

### Natural language interface

You can also trigger reviews using natural language:

- "Review my code"
- "Check for security issues"
- "What's wrong with my changes?"

Claude Code will automatically invoke the CodeRabbit plugin to perform the review.

## Integration workflow

### Use CodeRabbit as part of building new features

1. **Request implementation + review**: Ask Claude Code to implement a feature and run CodeRabbit
2. **CodeRabbit analysis**: CodeRabbit analyzes code changes and surfaces issues
3. **Claude Code fixes**: Claude Code applies fixes based on CodeRabbit feedback

### Example: API integration implementation

This example shows the workflow implementing a webhook handler for payment processing.

## Advanced usage

### Reviewing specific changes

```
/coderabbit:review uncommitted    # Only uncommitted changes
/coderabbit:review committed      # Only committed changes
```

### Comparing against different branches

```
/coderabbit:review --base develop
/coderabbit:review --base master
```

### Combining with natural language

```
Review my uncommitted changes for security issues
```

## Configuration

### Configure CodeRabbit for Claude Code

CodeRabbit automatically reads your `claude.md` file, so you can add context there on how code reviews should run, your coding standards, and architectural preferences.

## Troubleshooting

### Plugin not found

1. Verify marketplace access: `/plugin marketplace add coderabbitai/claude-plugin`
2. Check plugin installation
3. Reinstall if needed: `/plugin uninstall coderabbit` then `/plugin install coderabbit`

### CLI not authenticated

1. Check CLI authentication: `coderabbit auth status`
2. Re-authenticate: `coderabbit auth login`
3. Verify CLI installation in PATH

### CodeRabbit not finding issues

1. Check git status (CodeRabbit analyzes tracked changes)
2. Specify review scope with options
3. Specify base branch if not `main`
4. Review file types (CodeRabbit focuses on code files)

### Review taking too long

Reviews may take 7 to 30+ minutes:

1. Review smaller changesets
2. Use `/coderabbit:review uncommitted` for working directory changes only
3. Break large features into smaller, reviewable chunks
