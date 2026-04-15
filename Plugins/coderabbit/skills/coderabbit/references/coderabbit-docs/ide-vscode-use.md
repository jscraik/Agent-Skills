---
source: https://docs.coderabbit.ai/ide/vscode-use
---

# Use the VSCode extension

Review code changes in your local Git repository using the CodeRabbit VSCode extension with automatic or manual review options.

Review code changes directly in VSCode using the CodeRabbit extension. Choose between automatic reviews after every commit or manual reviews for specific changes.

## Choose your workflow

### Automatic reviews

The simplest way to get code reviews. CodeRabbit automatically reviews all changes when you commit to your local Git repository.

### Manual reviews

Get precise control over what CodeRabbit reviews. Compare any branch against any other branch, review only committed changes, or focus on specific files.

## Working with review results

After any review completes, CodeRabbit adds actionable comments to your code. Each comment includes specific suggestions you can apply directly or use as guidance.

### Browse and apply suggestions

Review comments appear in the **Files** section of the CodeRabbit sidebar. Click any comment to see the detailed suggestion inline in your editor.

When CodeRabbit provides a specific code fix, click the **Apply suggested change** checkmark icon to apply it immediately.

### Use AI coding agents

For complex issues, click the **Fix with AI** star icon to send the problem to your preferred AI coding agent:

- **VSCode + Copilot**: Sends directly to Copilot
- **Command-line tools**: Claude Code, Codex CLI, OpenCode - opens terminal with respective command
- **VSCode extensions**: Cline, Roo, Kilo Code, Augment Code - integrates with extension sidebars
- **Clipboard fallback**: Copies prompt for use with any AI agent

Configure your preferred AI agent in extension settings.

### Comment management

- **Ignore**: Remove comment from editor view
- **Collapse**: Hide comment but keep indicator icon
- **Restore**: Click collapsed/ignored comments in sidebar to show again
