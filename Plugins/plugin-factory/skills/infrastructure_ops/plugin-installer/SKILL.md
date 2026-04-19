---
name: plugin-installer
description: Install validated Codex plugins from trusted sources with quarantine validation, provenance, and rollback. Use when distribution and installation are the primary goals.
metadata:
  short-description: Install validated plugins with provenance and rollback safety
  skill-type: infrastructure_ops
---

# Plugin Installer

## Philosophy

- Install only with provenance and rollback evidence.

## When to Use

Use for downstream plugin installation and visibility recovery after build hardening.

Route elsewhere:
- plugin creation -> `[[plugin-creator]]`
- conversion/hardening -> `[[plugin-builder]]`

## Inputs

- source repo/url and plugin path
- destination root
- pinned ref and trust policy
- validation level (`strict|compat`)

## Outputs

Return: `schema_version`, `installed_plugin`, `install_path`, `validation`, `artifacts`, optional `blocked_by`.

## Workflow

Use the staged install protocol in `references/workflow.md`.

Required operational context is never removed; detailed guidance is relocated to references, not trimmed.

Read when:
- You need full install, provenance, and rollback flow details: [references/workflow.md](./references/workflow.md).

## Validation

```bash
bash Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family.sh
```

Fail fast: stop at first failed gate and report blocker text.

## Anti-Patterns

- installing from unpinned moving refs without explicit override
- promoting from quarantine before validation
- omitting provenance or rollback artifacts

## Constraints

- redact secrets and auth tokens in install logs
- do not skip trust policy checks by default
- allow network access only for explicit allowlisted source hosts: `https://github.com`, `https://api.github.com`, `https://raw.githubusercontent.com`

## References

- `references/workflow.md`
- `references/contract.yaml`
- `references/evals.yaml`
- `references/task-profile.json`
- `assets/`
