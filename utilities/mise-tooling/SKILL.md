---
name: mise-tooling
description: "Operate mise tool-version workflows with trust-aware config loading, local/global version pinning, and deterministic runtime execution. Use when a user needs mise commands or trust/activation troubleshooting."
metadata:
  skill-type: runbook
---

# Mise Tooling

Use this skill for `mise` version management, environment activation, trust prompts, and task-level tool pinning.

## When to use

- The user needs deterministic language/tool versions per project.
- The repo uses `mise.toml` or `.tool-versions` and commands are drifting.
- The user asks about trust prompts or shell activation behavior.
- The user needs per-task tool pinning.

## Non-triggers

- asdf-only workflows with no migration intent.
- package-manager release policy asks unrelated to runtime version pinning.

## Philosophy

- Pin versions explicitly; avoid floating runtime assumptions.
- Trust prompts are a security boundary, not a nuisance.
- Prefer reproducible execution (`mise exec`) when shell activation is ambiguous.

## Required inputs

- Current project path and config files (`mise.toml`, `.tool-versions`).
- Target scope (`local` vs `global`).
- Shell context requiring activation/export.

## Deliverables

- Exact `mise` commands for install/use/exec flow.
- Trust posture guidance for untrusted configs.
- Shell activation or one-shot execution recommendation.
- Validation checklist for active versions.
- Structured outputs should include `schema_version` when a schema-bound contract is requested.

## Rules

**Pin tools explicitly**:

```bash
mise use node@24
mise use --global node@24
```

**Use deterministic wrappers when shell activation is uncertain**:

```bash
mise exec -- node my-script.js
```

**Handle trust prompts deliberately**:

```bash
mise trust <path-to-mise.toml>
mise install
# mise <path> is not trusted. Trust it [y/n]?
```

**Enable shell exports when requested**:

```bash
eval "$(mise env -s bash)"
```

## Workflow

1. Inspect existing `mise.toml` or `.tool-versions` and requested scope.
2. Recommend/pin versions with `mise use` (`local` or `--global`).
3. Resolve trust state before install execution; use `mise trust <path-to-mise.toml>` (or `mise trust --all` for the current repo) only after explicit review of the config contents.
4. Choose `mise exec` for deterministic command execution or `mise env` for shell activation.
5. Validate selected tools and versions.

## Constraints

- Redact secrets, credentials, tokens, and sensitive data by default.
- Do not auto-trust unknown configuration files.
- Do not change global defaults without explicit user intent.

## Validation

- `mise ls`
- `mise current`
- `mise exec -- <tool> --version`
- `mise trust --show` to confirm trust state for active config files
- If trust blocks execution, stop and report the trust decision point.

## Failure mode

- If `mise` resolves the wrong binary, capture `mise current` plus the failing command path and stop before mutation.
- If trust is required, block on explicit trust decision instead of forcing `--all`.

## Gotchas

- Shells without activation can resolve the wrong binary path.
- Global pins can unexpectedly override local expectations.
- Trust prompts must be handled explicitly on new checkouts/worktrees.

## Anti-patterns

- Using unpinned latest versions in reproducible workflows.
- Auto-trusting external configuration without user intent.
- Assuming shell activation is present when it is not.

## Examples

- "Pin Node 24 and pnpm for this repository with mise, then show me how to verify which binaries are active in CI."
- "I ran `mise use node@24` but `node -v` still shows the old version. What exact fix path should I follow?"
- "This worktree says `.mise.toml` is untrusted. What is the safe next step?"

## References

- `references/contract.yaml`
- `references/evals.yaml`
- `references/context7-notes.md`

## See Also

| Skill | When to use together |
|---|---|
| [[fix-mise]] | Deep-dive broken trust, shim, or runtime-resolution states |
| [[pnpm-manager]] | Run workspace commands under the pinned runtime |
| [[npm-release]] | Ensure release commands execute on the intended Node toolchain |
