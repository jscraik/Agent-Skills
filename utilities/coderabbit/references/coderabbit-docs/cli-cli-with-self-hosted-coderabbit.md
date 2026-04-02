---
source: https://docs.coderabbit.ai/cli/cli-with-self-hosted-CodeRabbit
---

# Use with self-hosted CodeRabbit

Configure the CodeRabbit CLI to work with your organization's self-hosted CodeRabbit instance. This setup gives you all the benefits of AI-powered code reviews while maintaining full control over your code and data.

## Prerequisites

Before connecting to your self-hosted instance, ensure:

### CLI version

CodeRabbit CLI version 0.3.5 or higher installed

### Clean setup

Log out of the extension if you were previously connected to the managed service (`coderabbit auth logout`)

## Connect your self-hosted instance

### Install CLI

Download and install the CodeRabbit CLI to start reviewing code locally.

```
curl -fsSL https://cli.coderabbit.ai/install.sh | sh
```

### Restart your shell

After installation, restart your shell or reload your shell configuration.

```
# Restart your shell or run:
source ~/.zshrc
```

### Authenticate

Link your CodeRabbit account to enable personalized reviews based on your team's patterns.

```
coderabbit auth login --self-hosted
```

This is going to ask you for more details in the further steps.

### Select your Git provider

Select the Git provider from the list using arrow keys to connect the CLI with.

### Enter your self-hosted CodeRabbit url

Provide your self-hosted CodeRabbit's url: "your-self-hosted-coderabbit-url/". Verify the url validation.

### Complete the signin with an Access Token

Follow the browser redirect to sign in and copy the access token from your git provider back to your CLI.
