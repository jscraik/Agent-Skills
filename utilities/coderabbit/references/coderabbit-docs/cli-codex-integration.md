---
source: https://docs.coderabbit.ai/cli/codex-integration
---

# Codex Integration

Enable Codex to execute CodeRabbit directly in your development workflow. Let AI code, review, and fix issues autonomously without human intervention.

## Get continuous code review with Codex

Codex executes CodeRabbit directly as part of its development process. Ask Codex to implement a feature, run a code review, and fix any issues. CodeRabbit catches race conditions, memory leaks, and logic errors, then Codex applies the fixes with full context about the problems.

**Windows users:** Codex has experimental Windows support. For the best experience on Windows, use WSL (Windows Subsystem for Linux). See our WSL on Windows guide for setup instructions.

The integration creates a tight feedback loop: CodeRabbit analyzes your code changes and surfaces specific issues, then Codex applies the fixes based on CodeRabbit's context-rich feedback.

## Why integrate these tools

- **Expert issue detection**: CodeRabbit spots race conditions, memory leaks, and logic errors that generic linters miss
- **AI-powered fixes**: Codex implements fixes with full context from CodeRabbit's analysis
- **Context preservation**: CodeRabbit's `--prompt-only` mode gives Codex succinct context about issues
- **Continuous workflow**: Stay in development flow without switching between tools

## Prerequisites

1. **Install Codex**: Follow platform-specific instructions
2. **Install CodeRabbit CLI**:
   ```bash
   curl -fsSL https://cli.coderabbit.ai/install.sh | sh
   source ~/.zshrc
   ```
3. **Authenticate CodeRabbit within Codex**:
   - Request escalated permissions: `Please run: coderabbit auth login`
   - Grant network permissions when prompted
   - Get authentication link from Codex
   - Complete authentication in browser
   - Paste token back to Codex
4. **Verify setup**: `Run: coderabbit auth status`

### About Codex approval modes

- **Auto** (default): Can read files, make edits, and run commands. Requires approval for network access.
- **Read Only**: Chat and planning mode
- **Full Access**: Complete access without approval (use with caution)

## Integration workflow

### Basic workflow

1. **Request implementation + review**:
   ```
   Please implement phase 7.3 of the planning doc and then run coderabbit --prompt-only,
   let it run as long as it needs and fix any issues.
   ```
2. **Codex implements and runs CodeRabbit**
3. **CodeRabbit analysis and fix implementation**
4. **Automated issue resolution**

### Example: AI fitness tracker integration

1. Start the feature on a new branch
2. Tell Codex to implement and run CodeRabbit
3. CodeRabbit identifies issues (API error handling, memory leaks, race conditions, input validation)
4. Codex automatically applies fixes
5. Verification continues until all critical issues resolved

## Optimization tips

### Use prompt-only mode for efficiency

```bash
coderabbit --prompt-only
```

This mode provides:
- Succinct issue context
- Token-efficient formatting
- Specific file locations and line numbers
- Suggested fix approaches

### Configure CodeRabbit for Codex

CodeRabbit automatically reads your `agents.md` file. Add context there about code review standards and architectural preferences.

This is a Pro paid plan feature.

## Troubleshooting

### CodeRabbit not finding issues

1. Check authentication: `coderabbit auth login`
2. Verify git status
3. Review file types
4. Try different modes: `coderabbit --plain`

### Codex not applying fixes

1. Check authentication: `coderabbit auth status`
2. Use prompt-only mode
3. Provide explicit context
4. Check if review finished
5. Address timeout issues

### Managing review duration

Reviews may take 8 to 30+ minutes:

1. Review smaller changesets
2. Use `--type uncommitted` for only uncommitted changes
3. Configure base branch: `--base develop` or `--base main`
4. Work on focused feature branches
