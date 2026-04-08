---
source: https://docs.coderabbit.ai/cli/codex-integration
---

# Codex Integration

Enable Codex to execute CodeRabbit in your development workflow so code generation, review, and fix loops can run continuously.

## Get continuous code review with Codex

Codex can run CodeRabbit as part of feature development: implement changes, run review, and apply fixes from findings.

**Windows users:** Codex has experimental Windows support. Prefer WSL for best results.

## Why integrate these tools

- **Issue detection**: CodeRabbit finds logic and security issues that basic linters can miss.
- **AI-assisted fixes**: Codex can apply fixes using CodeRabbit feedback context.
- **Context preservation**: `--prompt-only` mode gives concise issue context for Codex.
- **Continuous workflow**: Less context switching between tools.

## Prerequisites

1. **Install Codex** using platform-specific instructions.
2. **Install CodeRabbit CLI** (download, inspect, then run installer):

   ```bash
   curl -fsSL https://cli.coderabbit.ai/install.sh -o /tmp/coderabbit-install.sh
   sh /tmp/coderabbit-install.sh
   source ~/.zshrc
   ```

3. **Authenticate CodeRabbit from Codex**:
   - Request `coderabbit auth login`.
   - Grant network permissions when prompted.
   - Complete browser authentication flow.
4. **Verify setup**:

   ```bash
   coderabbit auth status
   ```

## About Codex approval modes

- **Auto** (default): Read/edit/commands allowed; network requires approval.
- **Read Only**: Planning/chat only.
- **Full Access**: No approval prompts (use with caution).

## Integration workflow

### Basic workflow

1. Request implementation and review.
2. Codex implements and runs CodeRabbit.
3. CodeRabbit returns findings.
4. Codex applies fixes and re-validates.

Example request:

```text
Please implement phase 7.3 of the planning doc and then run coderabbit --prompt-only,
let it run as long as needed, and fix any issues it reports.
```

## Optimization tips

### Use prompt-only mode for efficiency

```bash
coderabbit --prompt-only
```

This mode provides concise issue context, file/line locations, and suggested fix directions.

### Configure CodeRabbit for Codex

CodeRabbit reads your `AGENTS.md` guidance. Add review standards and architecture preferences there.

This is a Pro paid plan feature.

## Troubleshooting

### CodeRabbit not finding issues

1. Re-authenticate: `coderabbit auth login`
2. Verify git status and changed files
3. Confirm file types are supported
4. Try plain mode: `coderabbit --plain`

### Codex not applying fixes

1. Verify auth: `coderabbit auth status`
2. Use `--prompt-only`
3. Provide explicit task context
4. Ensure review run completed
5. Reduce changeset size if timeouts occur

### Managing review duration

Reviews can take 8 to 30+ minutes:

1. Keep changesets focused
2. Use `--type uncommitted` for local delta-only reviews
3. Set base branch explicitly (`--base develop` or `--base main`)
4. Work from feature branches
