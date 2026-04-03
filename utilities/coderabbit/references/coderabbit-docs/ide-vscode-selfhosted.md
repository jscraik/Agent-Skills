---
source: https://docs.coderabbit.ai/ide/vscode-selfhosted
---

# Use with self-hosted CodeRabbit

Connect the VSCode extension to your self-hosted CodeRabbit instance for on-premises code reviews with full data control.

Configure the CodeRabbit VSCode extension to work with your organization's self-hosted CodeRabbit instance. This setup gives you all the benefits of AI-powered code reviews while maintaining full control over your code and data.

## Prerequisites

Before connecting to your self-hosted instance, ensure:

- **Extension version**: CodeRabbit extension version `0.12.1` or higher installed in your editor
- **Clean setup**: Log out of the extension if you were previously connected to the managed service

## Connect your self-hosted instance

1. **Access self-hosted option** - Click on the "Self hosting CodeRabbit?" button, located below the "Use CodeRabbit for free" button.
2. **Configure instance URL** - Enter your self-hosted instance URL when prompted. Make sure the instance URL is reachable within your network and websocket connections are allowed.
3. **Select git provider and authenticate** - Select your git provider: GitLab, Self-Hosted GitLab, GitHub, or GitHub Enterprise. If using GitHub or GitHub Enterprise, enter your GitHub Personal Access Token when prompted.

You should now be connected to your self-hosted instance and ready to use the VSCode extension.

## Next steps

- Uninstall the VSCode extension
