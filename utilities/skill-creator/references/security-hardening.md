# Security hardening for script-backed skills

This repo’s default assumption is that skill code runs in constrained environments:
- sandboxes / restricted filesystems
- no network (unless explicitly enabled)
- approval prompts for risky actions (depending on Codex configuration)

Use this doc to design safe scripts and predictable workflows.

## Rules (required)

### 1) No network assumptions

- Default behavior must work without internet access.
- If network access is required:
  - make it explicit in `SKILL.md` (Constraints + Validation)
  - gate it behind a flag (for example `--allow-network`)
  - fail fast with a clear error message if the flag is not set

### 2) Never echo secrets or environment variables

- Do **not** print environment variables or secret values.
- Avoid logging request headers, tokens, or `Authorization:` values.
- If you must log configuration, log only non-sensitive fields and redact the rest.

Practical guardrails:
- implement a `redact(text)` helper that replaces common secret patterns
- treat anything matching `*_KEY`, `*_TOKEN`, `*_SECRET`, `PASSWORD`, or `PRIVATE_KEY` as sensitive

### 3) Require explicit confirmation for destructive actions

Treat these as destructive:
- deleting files or directories
- overwriting outputs in place
- running commands that mutate remote state (push, publish, deploy)
- writing outside the current workspace

Recommended pattern:
- default to `--dry-run`
- require `--confirm` / `--force` for destructive paths
- print an exact “what will happen” summary before the action runs

## Codex approvals with `.rules`

Codex supports rule files to control which commands can run outside the sandbox and whether they require prompting.

See `references/destructive-commands.rules` for an example you can copy to:
- `~/.codex/rules/default.rules`

Notes:
- Codex loads `*.rules` at startup; restart Codex after edits.
- Use `decision = "prompt"` for risky commands and `decision = "forbidden"` for commands you never want run outside the sandbox by the agent.

## Testing security assumptions

Add at least one eval case in `references/evals.yaml` that verifies:
- secrets are not echoed
- the skill does not assume network
- destructive actions require explicit confirmation

Example acceptance ideas:
- `not_regex: (API_KEY|TOKEN|SECRET|PASSWORD)`
- `contains: --dry-run`
- `contains: --confirm`


## Codex sandbox + approval settings

For non-interactive runs (`codex exec`), prefer least privilege:

- Default: `--sandbox read-only`
- For edits: `--full-auto` or `--sandbox workspace-write`
- Avoid `--sandbox danger-full-access` unless you are inside an isolated runner.

In CI, set approvals explicitly to avoid hanging on prompts:
- `--ask-for-approval never`

Never use `--dangerously-bypass-approvals-and-sandbox` / `--yolo` unless you are inside an externally hardened, disposable environment.
