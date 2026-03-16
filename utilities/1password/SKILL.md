---
name: 1password
description: Plan, validate, and use 1Password CLI setup for secret injection and auth. Use when tasks need 1Password CLI usage, secret references, op run/read/inject, or provisioning secrets via env vars/.env files and scripts.
---

# 1Password CLI

Use 1Password CLI safely for sign-in, secret references, env injection, and script-driven secret access without exposing secret material.

## Standards snapshot (March 2026)
- Follow current 1Password CLI docs for exact command behavior instead of guessing flags or install steps.
- Prefer secret references, `op run`, and `op inject` over copying secrets into files or shell history.
- Treat app sign-in state, shell session state, and tmux session state as explicit prerequisites.
- Keep automation and human flows separate: use service accounts or Environments for unattended use, not ad hoc interactive login hacks.

## When to use
- Setting up or validating 1Password CLI.
- Reading secrets through secret references.
- Injecting secrets into env files, templates, or scripts.
- Running commands with secrets via `op run`.

## When not to use
- Managing secrets by copying plaintext values into source-controlled files.
- Doing generic credential management with no 1Password CLI or secret-reference workflow.
- Running `op` directly in unstable shell contexts when tmux-backed sign-in is required.

## Required inputs
- The secret-loading goal: sign-in, read, run, inject, or environment provisioning.
- OS and shell context.
- Account or vault context when multiple accounts are present.
- Any target files, templates, scripts, or env workflows involved.

## Deliverables
- A safe 1Password CLI path for the requested flow.
- Exact prerequisites and verification steps.
- Relevant reference-file pointers for the chosen command family.
- If requested, a structured status report with a `schema_version` field.

## Philosophy
- Secrets should flow through references and runtime injection, not through copied plaintext.
- The safest working path is better than the shortest-looking command.
- Verification matters: if sign-in or secret resolution is not proven, the workflow is not ready.

## Constraints
- Redact secrets, tokens, secret references containing sensitive identifiers, and account details by default.
- Do not paste secret values into chat, logs, shell history, code, or committed files.
- Do not run `op` outside the required tmux session pattern when interactive sign-in stability matters.
- Prefer 1Password Environments or service accounts for automation rather than reusing human interactive auth.

## Workflow
1. Verify OS, shell, and CLI availability with `op --version`.
2. Confirm the desktop app integration or service-account path that fits the request.
3. Start a fresh tmux session for interactive `op` work when sign-in persistence matters.
4. Verify `op signin` and `op whoami` before attempting any secret read.
5. Choose the right command family:
   - `op run` for env-backed command execution
   - `op read` for a single secret
   - `op inject` for templates or config files
   - `op plugin run` for shell-plugin-assisted flows
6. Return the exact next steps and the reference file for that lane.

## tmux requirement
When interactive sign-in is required, use a fresh tmux-backed session and keep all `op` commands inside it. This avoids re-prompts and broken auth state across short-lived shells.

## Tooling and references
- Core references:
  - `references/get-started.md`
  - `references/cli-examples.md`
  - `references/cli-reference.md`
  - `references/secret-references.md`
  - `references/secrets-environment-variables.md`
  - `references/secrets-scripts.md`
  - `references/environment-variables.md`
  - `references/best-practices.md`
  - `references/commands-run.md`
  - `references/commands-read.md`
  - `references/commands-inject.md`
  - `references/commands-signin.md`
  - `references/commands-whoami.md`
  - `references/contract.yaml`
  - `references/evals.yaml`
- Use assets only when the task needs bundled 1Password support material from `assets/`.

## Validation
- Verify CLI availability.
- Verify sign-in state with `op whoami` before secret access.
- Verify the selected secret-loading pattern matches the requested outcome.
- Fail fast at the first missing auth, vault, or session prerequisite.

## Anti-patterns
- Running `op` commands in arbitrary short-lived shells after interactive sign-in.
- Writing resolved secrets to disk when `op run` or `op inject` would avoid it.
- Mixing human interactive auth with unattended automation requirements.
- Treating missing sign-in or account context as a minor warning.

## Examples
- Help me use `op run` with this `.env` template.
- Verify my 1Password CLI setup and tell me why `op whoami` fails.
- Show the safest way to inject secret references into this config file.

## See Also

| Skill | When to use together |
|---|---|
| [[security-best-practices]] | Apply secret management best practices alongside 1Password |
| [[create-auth]] | Inject credentials into authentication flows via 1Password |
| [[cloudflare-deploy]] | Inject secrets into Cloudflare deployments via op run |
| [[workers-mcp]] | Secure MCP server secrets with 1Password injection |
| [[bootstrap]] | Provision dev environment secrets via 1Password during bootstrap |

**Topic map:** [[security-ops]]

## Remember
If the workflow would expose a secret unnecessarily, it is the wrong workflow.
