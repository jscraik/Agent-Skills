---
source: https://docs.coderabbit.ai/ide/vscode-config
---

# Configure the VS Code extension

Customize the CodeRabbit VS Code extension settings including AI agent integration, automatic review behavior, and self-hosted configurations.

Configure the CodeRabbit VS Code extension to match your workflow preferences. For more information about using the extension, see Review local changes.

These instructions are specific to VS Code. If you're using a VS Code-compatible editor like Cursor or Windsurf, the steps are similar but may require some adaptation.

## Find the settings screen

1. **Open CodeRabbit sidebar** - Open the CodeRabbit activity bar/sidebar.
2. **Click the settings icon** - In the sidebar, click the gear-shaped icon on the top right (beside the logout icon).

You can also search for **CodeRabbit: Settings** in the command palette to open the settings directly.

The settings screen contains the following configuration controls.

## Configure AI agent integration

The **Agent Type** setting lets you choose how the extension responds when using the **Fix with AI** feature during code reviews.

### Native integrations

- **Native** - Prompts the AI agent associated with your IDE to apply the suggested fix. Works with VS Code (using Copilot) and Cursor. For other IDEs, copies to clipboard.
- **Clipboard** - Copies prompt text describing the suggested fix to your clipboard for manual use with your preferred AI agent.

### Command-line tools

- **Claude Code** - Opens Terminal and uses the `claude` command-line program to apply fixes.
- **Codex CLI** - Opens Terminal and uses the `codex` command-line program to apply fixes.
- **OpenCode** - Opens Terminal and uses the `opencode` command-line program to apply fixes.

### VS Code extensions

- **Cline** - Opens the Cline sidebar and runs a task to apply the suggested fix.
- **Roo** - Opens the Roo sidebar and runs a task to apply the suggested fix.
- **Kilo Code** - Opens the Kilo Code sidebar and runs a task to apply the suggested fix.
- **Augment Code** - Opens the Augment Code sidebar with the prompt, allowing you to start the task manually.

For more information about the **Fix with AI** feature, see Request help from your AI coding agent.

## Configure automatic review behavior

The **Auto Review Mode** setting controls how the extension handles automatic code reviews after you make commits to your local Git repository.

- **Disabled** - The extension doesn't perform automatic code reviews.
- **Prompt** - After every commit, displays a dialog asking if you'd like to perform a code review.
- **Auto** - Always performs a review after every commit automatically.

For more information about this feature, see Automatically review local commits.

## Use with self-hosted CodeRabbit

This setting is only used when you're using a self-hosted instance of CodeRabbit. If you're using the CodeRabbit Cloud service, you don't need to configure this setting.

You will need to log in and log out of the extension after adding this value for the changes to take effect.

## What's next

- **Use the VS Code extension** - Learn how to review code changes and use AI features
- **Uninstall the VS Code extension** - Remove the CodeRabbit extension from your editor
