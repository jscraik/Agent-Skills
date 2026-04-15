---
source: https://docs.coderabbit.ai/cli/cli-with-self-hosted-CodeRabbit
---

# Use with self-hosted CodeRabbit

Configure the CodeRabbit CLI to work with your organization's self-hosted instance so reviews stay in your controlled environment.

## Prerequisites

Before connecting to your self-hosted instance:

### CLI version

Install CodeRabbit CLI version `0.3.5` or newer.

### Clean setup

If you previously used the managed service, log out first:

```bash
coderabbit auth logout
```

## Connect your self-hosted instance

### Install CLI

Download the installer script, inspect it, then run it:

```bash
curl -fsSL https://cli.coderabbit.ai/install.sh -o /tmp/coderabbit-install.sh
sh /tmp/coderabbit-install.sh
```

### Restart your shell

```bash
source ~/.zshrc
```

### Authenticate

```bash
coderabbit auth login --self-hosted
```

The CLI will guide you through subsequent prompts.

### Select your Git provider

Choose the provider in the interactive prompt.

### Enter your self-hosted CodeRabbit URL

Provide your self-hosted URL (for example, `https://your-self-hosted-coderabbit-url/`) and confirm validation.

### Complete sign-in with an access token

Follow the browser redirect, sign in to your Git provider, and paste the generated token back into the CLI prompt.
