---
source: https://docs.coderabbit.ai/cli/gemini-integration
---

# Gemini Integration

Enable Gemini to execute CodeRabbit directly in your development workflow. Let AI code, review, and fix issues autonomously without human intervention.

## Overview

Use CodeRabbit with Google's Gemini CLI in a full agentic loop. Code with Gemini, review the changes with CodeRabbit, and fix the issues with Gemini.

## Prerequisites

1. Install Gemini CLI
2. Install CodeRabbit CLI:
   ```bash
   curl -fsSL https://cli.coderabbit.ai/install.sh | sh
   source ~/.zshrc
   ```
3. Authenticate: `coderabbit auth login`
4. Verify: `coderabbit auth status`

## Use CodeRabbit as part of building new features

1. Request implementation + review from Gemini
2. Gemini implements and runs CodeRabbit
3. CodeRabbit analysis and fix implementation
4. Automated issue resolution

## Optimization tips

### Use prompt-only mode for efficiency

```bash
coderabbit --prompt-only
```

This mode:
- Provides succinct issue context
- Uses token-efficient formatting
- Includes specific file locations and line numbers
- Suggests fix approaches without overwhelming detail

### Configure CodeRabbit for Gemini

CodeRabbit automatically reads your `gemini.md` file. Add context on how code reviews should run, your coding standards, and architectural preferences. Note this feature is only available on the Pro paid plan.

## Troubleshooting

### CodeRabbit not finding issues

1. Check authentication status: `coderabbit auth status`
2. Verify git status
3. Consider review type: `--type uncommitted`, `--type committed`, `--type all`
4. Specify base branch: `--base develop` or `--base master`
5. Review file types (CodeRabbit focuses on code files)

### Managing review duration

Reviews may take 7 to 30+ minutes:

1. Ensure background execution
2. Review smaller changesets
3. Use `--type uncommitted` for only uncommitted changes
4. Work on focused feature branches
